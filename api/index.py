from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.routers import auth, artists, requests

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    connect_to_mongo()
    yield
    # Shutdown
    close_mongo_connection()

app = FastAPI(
    title="Requestr API",
    description="Live musician song request application",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS - Specific to your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://requestsong-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add manual CORS headers for your specific frontend
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    # Handle preflight OPTIONS requests immediately
    if request.method == "OPTIONS":
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "https://requestsong-frontend.vercel.app",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "86400",
            }
        )
    
    # Process the request
    try:
        response = await call_next(request)
    except Exception as e:
        # Even for errors, add CORS headers
        response = Response(
            status_code=500,
            content={"detail": "Internal server error"},
            headers={
                "Access-Control-Allow-Origin": "https://requestsong-frontend.vercel.app",
                "Access-Control-Allow-Credentials": "true",
            }
        )
    
    # Add CORS headers to all responses
    response.headers["Access-Control-Allow-Origin"] = "https://requestsong-frontend.vercel.app"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(artists.router, prefix="/api")
app.include_router(requests.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to Requestr API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Export for Vercel
handler = app