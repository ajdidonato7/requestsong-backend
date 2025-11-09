import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from typing import List, Dict, Optional
from fastapi import HTTPException, status

class SpotifyService:
    def __init__(self):
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            raise ValueError("Spotify credentials not found in environment variables")
        
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    def search_tracks(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Search for tracks on Spotify
        
        Args:
            query: Search query string
            limit: Maximum number of results to return (default: 20, max: 50)
            
        Returns:
            List of track dictionaries with simplified structure
        """
        try:
            # Limit the search to a reasonable number
            limit = min(limit, 50)
            
            results = self.sp.search(q=query, type='track', limit=limit)
            tracks = results['tracks']['items']
            
            simplified_tracks = []
            for track in tracks:
                # Get the first artist name (primary artist)
                artist_name = track['artists'][0]['name'] if track['artists'] else 'Unknown Artist'
                
                # Get all artist names for display
                all_artists = ', '.join([artist['name'] for artist in track['artists']])
                
                # Get album art (use the smallest available image)
                album_image = None
                if track['album']['images']:
                    # Sort by size and get the smallest image
                    images = sorted(track['album']['images'], key=lambda x: x['width'])
                    album_image = images[0]['url']
                
                simplified_track = {
                    'id': track['id'],
                    'name': track['name'],
                    'artist': artist_name,
                    'all_artists': all_artists,
                    'album': track['album']['name'],
                    'album_image': album_image,
                    'preview_url': track['preview_url'],
                    'external_url': track['external_urls']['spotify'],
                    'duration_ms': track['duration_ms'],
                    'popularity': track['popularity']
                }
                simplified_tracks.append(simplified_track)
            
            return simplified_tracks
            
        except spotipy.exceptions.SpotifyException as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Spotify API error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error searching tracks: {str(e)}"
            )
    
    def get_track(self, track_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific track
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            Track dictionary with detailed information or None if not found
        """
        try:
            track = self.sp.track(track_id)
            
            if not track:
                return None
            
            # Get the first artist name (primary artist)
            artist_name = track['artists'][0]['name'] if track['artists'] else 'Unknown Artist'
            
            # Get all artist names for display
            all_artists = ', '.join([artist['name'] for artist in track['artists']])
            
            # Get album art (use the medium size if available)
            album_image = None
            if track['album']['images']:
                # Try to get medium size image, fallback to first available
                for image in track['album']['images']:
                    if image['width'] >= 300:
                        album_image = image['url']
                        break
                if not album_image:
                    album_image = track['album']['images'][0]['url']
            
            return {
                'id': track['id'],
                'name': track['name'],
                'artist': artist_name,
                'all_artists': all_artists,
                'album': track['album']['name'],
                'album_image': album_image,
                'preview_url': track['preview_url'],
                'external_url': track['external_urls']['spotify'],
                'duration_ms': track['duration_ms'],
                'popularity': track['popularity'],
                'release_date': track['album']['release_date']
            }
            
        except spotipy.exceptions.SpotifyException as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Spotify API error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting track: {str(e)}"
            )

# Global instance
spotify_service = SpotifyService()