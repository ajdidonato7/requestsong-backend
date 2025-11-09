from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from bson import ObjectId
from .artist import PyObjectId

class RequestStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    REJECTED = "rejected"

class Request(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    artist_username: str = Field(..., min_length=3, max_length=30)
    song_title: str = Field(..., min_length=1, max_length=200)
    song_artist: str = Field(..., min_length=1, max_length=200)
    requester_name: str = Field(..., min_length=1, max_length=100)
    message: Optional[str] = Field(None, max_length=500)
    tip_amount: Optional[float] = Field(None, ge=0)
    status: RequestStatus = RequestStatus.PENDING
    queue_position: int = Field(..., ge=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # Spotify integration fields
    spotify_track_id: Optional[str] = Field(None, description="Spotify track ID")
    spotify_track_url: Optional[str] = Field(None, description="Spotify track URL")
    album_image_url: Optional[str] = Field(None, description="Album cover image URL")
    preview_url: Optional[str] = Field(None, description="30-second preview URL")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class RequestCreate(BaseModel):
    artist_username: str = Field(..., min_length=3, max_length=30)
    song_title: str = Field(..., min_length=1, max_length=200)
    song_artist: str = Field(..., min_length=1, max_length=200)
    requester_name: str = Field(..., min_length=1, max_length=100)
    message: Optional[str] = Field(None, max_length=500)
    tip_amount: Optional[float] = Field(None, ge=0)
    # Spotify integration fields
    spotify_track_id: Optional[str] = Field(None, description="Spotify track ID")
    spotify_track_url: Optional[str] = Field(None, description="Spotify track URL")
    album_image_url: Optional[str] = Field(None, description="Album cover image URL")
    preview_url: Optional[str] = Field(None, description="30-second preview URL")

class RequestUpdate(BaseModel):
    status: Optional[RequestStatus] = None
    queue_position: Optional[int] = Field(None, ge=1)

class RequestReorder(BaseModel):
    request_id: str
    new_position: int = Field(..., ge=1)

class RequestPublic(BaseModel):
    id: str
    song_title: str
    song_artist: str
    requester_name: str
    message: Optional[str] = None
    tip_amount: Optional[float] = None
    status: RequestStatus
    queue_position: int
    created_at: datetime
    # Spotify integration fields
    spotify_track_id: Optional[str] = None
    spotify_track_url: Optional[str] = None
    album_image_url: Optional[str] = None
    preview_url: Optional[str] = None

    class Config:
        json_encoders = {ObjectId: str}