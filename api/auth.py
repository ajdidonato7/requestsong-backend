from datetime import timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
import json
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_database
from app.models.artist import Artist, ArtistCreate, ArtistPublic, Token
from app.auth import (
    authenticate_artist,
    create_access_token,
    get_password_hash,
    get_current_active_artist
)
from app.config import settings

def handler(request):
    """Vercel serverless function handler for auth endpoints"""
    
    # CORS headers for all responses
    cors_headers = {
        'Access-Control-Allow-Origin': 'https://requestsong-frontend.vercel.app',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Credentials': 'true',
        'Content-Type': 'application/json'
    }
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': ''
        }
    
    # Handle POST /login
    if request.method == 'POST' and request.path.endswith('/login'):
        try:
            # Parse form data
            body = request.body
            if isinstance(body, str):
                import urllib.parse
                parsed = urllib.parse.parse_qs(body)
                username = parsed.get('username', [''])[0]
                password = parsed.get('password', [''])[0]
            else:
                # Handle JSON body
                data = json.loads(body)
                username = data.get('username', '')
                password = data.get('password', '')
            
            # Authenticate
            import asyncio
            artist = asyncio.run(authenticate_artist(username, password))
            
            if not artist:
                return {
                    'statusCode': 401,
                    'headers': cors_headers,
                    'body': json.dumps({
                        'detail': 'Incorrect username or password'
                    })
                }
            
            # Create token
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": artist.username}, expires_delta=access_token_expires
            )
            
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({
                    'access_token': access_token,
                    'token_type': 'bearer'
                })
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': cors_headers,
                'body': json.dumps({
                    'detail': f'Internal server error: {str(e)}'
                })
            }
    
    # Default response
    return {
        'statusCode': 404,
        'headers': cors_headers,
        'body': json.dumps({
            'detail': 'Not found'
        })
    }