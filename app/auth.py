from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from app.database import get_database
from app.models.artist import Artist, TokenData

# Password hashing - using argon2 instead of bcrypt for better compatibility
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_artist_by_username(username: str) -> Optional[Artist]:
    """Get artist by username from database"""
    db = get_database()
    artist_data = db.artists.find_one({"username": username})
    if artist_data:
        # Convert ObjectId to string for Pydantic compatibility
        artist_data["_id"] = str(artist_data["_id"])
        return Artist(**artist_data)
    return None

async def authenticate_artist(username: str, password: str) -> Optional[Artist]:
    """Authenticate an artist with username and password"""
    artist = await get_artist_by_username(username)
    if not artist:
        return None
    if not verify_password(password, artist.password_hash):
        return None
    return artist

async def get_current_artist(token: str = Depends(oauth2_scheme)) -> Artist:
    """Get current authenticated artist from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    artist = await get_artist_by_username(username=token_data.username)
    if artist is None:
        raise credentials_exception
    return artist

async def get_current_active_artist(current_artist: Artist = Depends(get_current_artist)) -> Artist:
    """Get current active artist (not disabled)"""
    if not current_artist.is_active:
        raise HTTPException(status_code=400, detail="Inactive artist")
    return current_artist