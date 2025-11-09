from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from bson import ObjectId
from app.database import get_database
from app.models.request import Request, RequestCreate, RequestUpdate, RequestPublic, RequestReorder
from app.models.artist import Artist
from app.auth import get_current_active_artist

router = APIRouter(prefix="/requests", tags=["requests"])

@router.post("/", response_model=RequestPublic)
async def create_request(request_data: RequestCreate):
    """Create a new song request"""
    db = get_database()
    
    # Check if artist exists and is active
    artist = db.artists.find_one({"username": request_data.artist_username, "is_active": True})
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found or inactive"
        )
    
    # Get the next queue position for this artist
    last_request = db.requests.find_one(
        {"artist_username": request_data.artist_username, "status": "pending"},
        sort=[("queue_position", -1)]
    )
    next_position = (last_request["queue_position"] + 1) if last_request else 1
    
    # Create the request
    request = Request(
        artist_username=request_data.artist_username,
        song_title=request_data.song_title,
        song_artist=request_data.song_artist,
        requester_name=request_data.requester_name,
        message=request_data.message,
        tip_amount=request_data.tip_amount,
        queue_position=next_position,
        spotify_track_id=request_data.spotify_track_id,
        spotify_track_url=request_data.spotify_track_url,
        album_image_url=request_data.album_image_url,
        preview_url=request_data.preview_url
    )
    
    # Insert into database
    result = db.requests.insert_one(request.dict(by_alias=True))
    
    if result.inserted_id:
        return RequestPublic(
            id=str(result.inserted_id),
            song_title=request.song_title,
            song_artist=request.song_artist,
            requester_name=request.requester_name,
            message=request.message,
            tip_amount=request.tip_amount,
            status=request.status,
            queue_position=request.queue_position,
            created_at=request.created_at,
            spotify_track_id=request.spotify_track_id,
            spotify_track_url=request.spotify_track_url,
            album_image_url=request.album_image_url,
            preview_url=request.preview_url
        )
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to create request"
    )

@router.get("/{artist_username}", response_model=List[RequestPublic])
async def get_artist_requests(artist_username: str, status_filter: str = "pending"):
    """Get all requests for an artist (public view)"""
    db = get_database()
    
    # Check if artist exists
    artist = db.artists.find_one({"username": artist_username})
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found"
        )
    
    # Build query filter
    query = {"artist_username": artist_username}
    if status_filter != "all":
        query["status"] = status_filter
    
    # Get requests sorted by queue position
    requests_cursor = db.requests.find(query).sort("queue_position", 1)
    requests = []
    
    for request_data in requests_cursor:
        requests.append(RequestPublic(
            id=str(request_data["_id"]),
            song_title=request_data["song_title"],
            song_artist=request_data["song_artist"],
            requester_name=request_data["requester_name"],
            message=request_data.get("message"),
            tip_amount=request_data.get("tip_amount"),
            status=request_data["status"],
            queue_position=request_data["queue_position"],
            created_at=request_data["created_at"],
            spotify_track_id=request_data.get("spotify_track_id"),
            spotify_track_url=request_data.get("spotify_track_url"),
            album_image_url=request_data.get("album_image_url"),
            preview_url=request_data.get("preview_url")
        ))
    
    return requests

@router.put("/{request_id}", response_model=RequestPublic)
async def update_request(
    request_id: str,
    request_update: RequestUpdate,
    current_artist: Artist = Depends(get_current_active_artist)
):
    """Update a request (artist only)"""
    db = get_database()
    
    # Validate ObjectId
    if not ObjectId.is_valid(request_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request ID"
        )
    
    # Find the request
    request_data = db.requests.find_one({"_id": ObjectId(request_id)})
    if not request_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    # Check if current artist owns this request
    if request_data["artist_username"] != current_artist.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this request"
        )
    
    # Prepare update data
    update_data = {"updated_at": datetime.utcnow()}
    if request_update.status is not None:
        update_data["status"] = request_update.status
    if request_update.queue_position is not None:
        update_data["queue_position"] = request_update.queue_position
    
    # Update the request
    result = db.requests.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update request"
        )
    
    # Return updated request
    updated_request = db.requests.find_one({"_id": ObjectId(request_id)})
    return RequestPublic(
        id=str(updated_request["_id"]),
        song_title=updated_request["song_title"],
        song_artist=updated_request["song_artist"],
        requester_name=updated_request["requester_name"],
        message=updated_request.get("message"),
        tip_amount=updated_request.get("tip_amount"),
        status=updated_request["status"],
        queue_position=updated_request["queue_position"],
        created_at=updated_request["created_at"],
        spotify_track_id=updated_request.get("spotify_track_id"),
        spotify_track_url=updated_request.get("spotify_track_url"),
        album_image_url=updated_request.get("album_image_url"),
        preview_url=updated_request.get("preview_url")
    )

@router.delete("/{request_id}")
async def delete_request(
    request_id: str,
    current_artist: Artist = Depends(get_current_active_artist)
):
    """Delete/reject a request (artist only)"""
    db = get_database()
    
    # Validate ObjectId
    if not ObjectId.is_valid(request_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request ID"
        )
    
    # Find the request
    request_data = db.requests.find_one({"_id": ObjectId(request_id)})
    if not request_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    # Check if current artist owns this request
    if request_data["artist_username"] != current_artist.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this request"
        )
    
    # Delete the request
    result = db.requests.delete_one({"_id": ObjectId(request_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete request"
        )
    
    # Reorder remaining requests to fill the gap
    await _reorder_queue_after_deletion(
        db, current_artist.username, request_data["queue_position"]
    )
    
    return {"message": "Request deleted successfully"}

@router.put("/reorder", response_model=List[RequestPublic])
async def reorder_requests(
    reorder_data: List[RequestReorder],
    current_artist: Artist = Depends(get_current_active_artist)
):
    """Reorder multiple requests in the queue (artist only)"""
    db = get_database()
    
    # Validate all request IDs and ownership
    for item in reorder_data:
        if not ObjectId.is_valid(item.request_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid request ID: {item.request_id}"
            )
        
        request_data = db.requests.find_one({"_id": ObjectId(item.request_id)})
        if not request_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Request not found: {item.request_id}"
            )
        
        if request_data["artist_username"] != current_artist.username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to reorder these requests"
            )
    
    # Update queue positions
    for item in reorder_data:
        db.requests.update_one(
            {"_id": ObjectId(item.request_id)},
            {"$set": {"queue_position": item.new_position, "updated_at": datetime.utcnow()}}
        )
    
    # Return updated queue
    return await get_artist_requests(current_artist.username, "pending")

async def _reorder_queue_after_deletion(db, artist_username: str, deleted_position: int):
    """Helper function to reorder queue after a request is deleted"""
    # Move all requests with higher positions down by 1
    db.requests.update_many(
        {
            "artist_username": artist_username,
            "queue_position": {"$gt": deleted_position},
            "status": "pending"
        },
        {"$inc": {"queue_position": -1}}
    )