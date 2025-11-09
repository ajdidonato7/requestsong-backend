#!/usr/bin/env python3
"""
Test script for Spotify API integration
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.services.spotify import spotify_service
    print("✅ Successfully imported Spotify service")
    
    # Test search functionality
    print("\n🔍 Testing Spotify search...")
    
    # Test with a popular song
    test_query = "Bohemian Rhapsody Queen"
    print(f"Searching for: '{test_query}'")
    
    try:
        results = spotify_service.search_tracks(test_query, limit=5)
        print(f"✅ Search successful! Found {len(results)} tracks")
        
        if results:
            print("\n📋 First result:")
            first_track = results[0]
            print(f"  - Title: {first_track['name']}")
            print(f"  - Artist: {first_track['artist']}")
            print(f"  - Album: {first_track['album']}")
            print(f"  - Spotify ID: {first_track['id']}")
            print(f"  - Has preview: {'Yes' if first_track['preview_url'] else 'No'}")
            print(f"  - Has album art: {'Yes' if first_track['album_image'] else 'No'}")
            
            # Test getting specific track details
            print(f"\n🎵 Testing track details for ID: {first_track['id']}")
            track_details = spotify_service.get_track(first_track['id'])
            if track_details:
                print("✅ Track details retrieved successfully")
                print(f"  - Duration: {track_details['duration_ms']}ms")
                print(f"  - Popularity: {track_details['popularity']}")
            else:
                print("❌ Failed to get track details")
        
    except Exception as e:
        print(f"❌ Search failed: {str(e)}")
        
except ImportError as e:
    print(f"❌ Failed to import Spotify service: {str(e)}")
    print("Make sure all dependencies are installed and environment variables are set")
    
except Exception as e:
    print(f"❌ Unexpected error: {str(e)}")

print("\n" + "="*50)
print("Test completed!")
print("="*50)