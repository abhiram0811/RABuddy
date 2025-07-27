# RABuddy Deployment Guide

## Current Status
- ✅ Backend deployed on Render: https://rabuddy-backend.onrender.com
- ✅ Frontend deployed on Vercel: https://rabuddy.abhiranmultani.com
- ✅ Local development environment configured

## Issues Fixed
1. **Vercel API URL**: Updated to point to Render backend instead of ngrok
2. **Port consistency**: Standardized to use port 5000 for backend
3. **Environment variables**: Properly configured for both local and production

## Deployment Steps

### Backend (Render)
Your backend is correctly configured and should be working. The logs show it's running.

### Frontend (Vercel)
The frontend needs to be redeployed with the updated configuration.

1. **Push your changes to Git:**
   ```bash
   git add .
   git commit -m "Fix API URL configuration for production deployment"
   git push
   ```

2. **Vercel will automatically redeploy** when you push to your main branch.

## Local Development

### Quick Start
Run the automated script:
```bash
./start_dev.bat
```

### Manual Start
1. **Backend (Terminal 1):**
   ```bash
   cd backend
   python src/app.py
   ```

2. **Frontend (Terminal 2):**
   ```bash
   cd frontend
   npm run dev
   ```

## URLs
- **Local Backend**: http://localhost:5000
- **Local Frontend**: http://localhost:3000
- **Production Backend**: https://rabuddy-backend.onrender.com
- **Production Frontend**: https://rabuddy.abhiranmultani.com

## Testing the Deployment

### Test Backend
Visit: https://rabuddy-backend.onrender.com/health
Should return: `{"status": "healthy", "service": "RABuddy Backend"}`

### Test API
Visit: https://rabuddy-backend.onrender.com/api/test
Should return: `{"message": "API is working", "status": "success"}`

## Environment Variables

### Render (Backend)
Make sure these are set in your Render dashboard:
- `GEMINI_API_KEY`: Your Google AI API key
- `FLASK_ENV`: production
- `ENVIRONMENT`: production

### Vercel (Frontend)
The environment variable is set in `vercel.json`:
- `NEXT_PUBLIC_API_URL`: https://rabuddy-backend.onrender.com/api

## Troubleshooting

### If Vercel frontend shows blank page:
1. Check the browser console for errors
2. Ensure Vercel build completed successfully
3. Verify the API URL is correct in the network tab

### If backend is not responding:
1. Check Render logs for errors
2. Ensure all environment variables are set
3. Test the health endpoint

### Common Issues:
- **CORS errors**: Already configured to allow all origins
- **Build failures**: Check Node.js version compatibility
- **API timeout**: Render free tier may have cold starts
