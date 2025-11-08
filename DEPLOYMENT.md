# Backend Deployment Guide

This guide will help you deploy the Requestr FastAPI backend to either Fly.io or Render.

## Option 1: Fly.io Deployment

## Prerequisites

1. Install the Fly CLI: https://fly.io/docs/getting-started/installing-flyctl/
2. Create a Fly.io account: https://fly.io/app/sign-up
3. Set up a MongoDB Atlas cluster (free tier available): https://www.mongodb.com/atlas

## Setup Steps

### 1. Login to Fly.io
```bash
flyctl auth login
```

### 2. Navigate to backend directory
```bash
cd backend
```

### 3. Initialize the app (if not already done)
```bash
flyctl apps create requestr-backend
```

### 4. Set up MongoDB Atlas
1. Create a MongoDB Atlas cluster
2. Create a database user
3. Get your connection string (it should look like: `mongodb+srv://username:password@cluster.mongodb.net/requestr?retryWrites=true&w=majority`)

### 5. Set environment variables
```bash
# Set your MongoDB Atlas connection string
flyctl secrets set MONGODB_URL="mongodb+srv://username:password@cluster.mongodb.net/requestr?retryWrites=true&w=majority"

# Set a strong secret key for JWT tokens
flyctl secrets set SECRET_KEY="your-super-secret-key-change-this-to-something-very-long-and-random"

# Set environment to production
flyctl secrets set ENVIRONMENT="production"
```

### 6. Deploy the backend
```bash
flyctl deploy
```

### 7. Get your backend URL
```bash
flyctl status
```
Your backend will be available at: `https://requestr-backend.fly.dev`

## API Endpoints

All API endpoints are prefixed with `/api`:

- `GET /` - Welcome message
- `GET /health` - Health check
- `POST /api/auth/register` - Artist registration
- `POST /api/auth/login` - Artist login
- `GET /api/auth/me` - Get current user
- `GET /api/artists/{username}` - Get artist profile
- `POST /api/requests` - Create song request
- `GET /api/requests/{username}` - Get requests for artist
- `PUT /api/requests/{id}` - Update request
- `DELETE /api/requests/{id}` - Delete request

## Configuration Details

### Environment Variables
- `MONGODB_URL`: Your MongoDB Atlas connection string
- `SECRET_KEY`: A secure secret key for JWT token signing
- `ENVIRONMENT`: Set to "production" for production deployment
- `DATABASE_NAME`: Database name (defaults to "requestr")
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (defaults to 30)

### CORS Configuration
The backend is configured to allow requests from:
- `http://localhost:3000` (local development)
- `https://requestsong-frontend.vercel.app` (your specific frontend)
- Additional domains can be added in `backend/app/main.py`

**Important**: After updating CORS settings, redeploy your backend for changes to take effect.

### Scaling
The app is configured with:
- 1 CPU core
- 256MB RAM
- Auto-scaling enabled (scales to 0 when not in use)

To scale up:
```bash
flyctl scale memory 512  # Increase memory to 512MB
flyctl scale count 2     # Run 2 instances
```

### Monitoring
- Health checks are configured at `/health`
- View logs: `flyctl logs`
- Monitor status: `flyctl status`

## Troubleshooting

### Common Issues
1. **Database connection errors**: Verify your MongoDB Atlas connection string and IP whitelist
2. **CORS errors**:
   - Ensure your frontend domain is explicitly listed in `backend/app/main.py`
   - Redeploy backend after adding new domains
   - Check that the frontend URL matches exactly (including https://)
3. **Build failures**: Check that all dependencies are properly specified in requirements.txt

### Useful Commands
```bash
flyctl logs                    # View application logs
flyctl ssh console            # SSH into the running container
flyctl status                 # Check app status
flyctl secrets list          # List environment variables
flyctl deploy --no-cache     # Deploy without using cache
```

## Custom Domain (Optional)
To use a custom domain:
```bash
flyctl certs create api.yourdomain.com