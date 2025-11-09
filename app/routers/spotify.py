from typing import List, Dict
from fastapi import APIRouter, HTTPException, status, Query
from app.services.spotify import spotify_service

router = APIRouter(prefix="/spotify", tags=["spotify"])

@router.get("/search", response_model=List[Dict])
async def search_tracks(
    q: str = Query(..., description="Search query for tracks"),
    limit: int = Query(20, ge=1, le=50, description="Number of results to return (1-50)")
):
    """
    Search for tracks on Spotify
    
    Args:
        q: Search query string
        limit: Maximum number of results to return (default: 20, max: 50)
        
    Returns:
        List of track objects with simplified structure
    """
    if not q or len(q.strip()) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty"
        )
    
    try:
        tracks = spotify_service.search_tracks(q.strip(), limit)
        return tracks
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during search: {str(e)}"
        )

@router.get("/track/{track_id}", response_model=Dict)
async def get_track(track_id: str):
    """
    Get detailed information about a specific Spotify track
    
    Args:
        track_id: Spotify track ID
        
    Returns:
        Track object with detailed information
    """
    if not track_id or len(track_id.strip()) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Track ID cannot be empty"
        )
    
    try:
        track = spotify_service.get_track(track_id.strip())
        if not track:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Track not found"
            )
        return track
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error getting track: {str(e)}"
        )