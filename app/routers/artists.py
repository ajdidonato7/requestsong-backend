from fastapi import APIRouter, HTTPException, status
from app.database import get_database
from app.models.artist import ArtistPublic

router = APIRouter(prefix="/api/artists", tags=["artists"])

@router.get("/{username}", response_model=ArtistPublic)
async def get_artist_profile(username: str):
    """Get public artist profile by username"""
    db = get_database()
    
    artist_data = db.artists.find_one({"username": username})
    if not artist_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found"
        )
    
    return ArtistPublic(
        username=artist_data["username"],
        display_name=artist_data["display_name"],
        bio=artist_data.get("bio"),
        is_active=artist_data["is_active"]
    )

@router.get("/{username}/exists")
async def check_artist_exists(username: str):
    """Check if an artist exists and is active"""
    db = get_database()
    
    artist_data = db.artists.find_one({"username": username, "is_active": True})
    return {"exists": artist_data is not None}