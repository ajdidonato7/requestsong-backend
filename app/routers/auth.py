from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from app.database import get_database
from app.models.artist import Artist, ArtistCreate, ArtistPublic, Token
from app.auth import (
    authenticate_artist,
    create_access_token,
    get_password_hash,
    get_current_active_artist
)
from app.config import settings

def add_cors_headers(response: Response):
    """Add CORS headers to response"""
    response.headers["Access-Control-Allow-Origin"] = "https://requestsong-frontend.vercel.app"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=ArtistPublic)
async def register_artist(artist_data: ArtistCreate, response: Response):
    """Register a new artist"""
    # Add CORS headers
    add_cors_headers(response)
    
    db = get_database()
    
    # Check if username already exists
    if db.artists.find_one({"username": artist_data.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if db.artists.find_one({"email": artist_data.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new artist
    hashed_password = get_password_hash(artist_data.password)
    artist = Artist(
        username=artist_data.username,
        display_name=artist_data.display_name,
        email=artist_data.email,
        password_hash=hashed_password,
        bio=artist_data.bio
    )
    
    # Insert into database
    result = db.artists.insert_one(artist.model_dump(by_alias=True))
    
    if result.inserted_id:
        return ArtistPublic(
            username=artist.username,
            display_name=artist.display_name,
            bio=artist.bio,
            is_active=artist.is_active
        )
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to create artist"
    )

@router.post("/login", response_model=Token)
async def login_artist(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    """Login artist and return access token"""
    # Add CORS headers
    add_cors_headers(response)
    
    artist = await authenticate_artist(form_data.username, form_data.password)
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": artist.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=ArtistPublic)
async def read_current_artist(current_artist: Artist = Depends(get_current_active_artist)):
    """Get current authenticated artist"""
    return ArtistPublic(
        username=current_artist.username,
        display_name=current_artist.display_name,
        bio=current_artist.bio,
        is_active=current_artist.is_active
    )
