# RABuddy Public Access Setup Guide

## Option 1: Localhost to Custom Domain Mapping

### Quick Setup (Recommended)

**Prerequisites:**
1. RABuddy running locally (backend on 5001, frontend on 3003)
2. ngrok installed and authenticated

#### Step 1: Download and Setup ngrok
1. Go to [ngrok.com](https://ngrok.com) and create a free account
2. Download ngrok for Windows
3. Extract to a folder (e.g., `C:\tools\ngrok\`)
4. Add to your Windows PATH or note the location
5. Get your auth token from [dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)
6. Run: `ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE`

#### Step 2: Use the Automated Script
```bash
# Simply run this script - it does everything!
start_rabuddy_public.bat
```

This script will:
- ✅ Start RABuddy backend (public version)
- ✅ Start RABuddy frontend  
- ✅ Create ngrok tunnels for both services
- ✅ Display setup instructions

#### Step 3: Configure Frontend API URL
1. Copy the **backend** ngrok URL (HTTPS, port 5001)
2. Run: `update_public_urls.bat`
3. Enter your backend URL when prompted
4. Restart the frontend

#### Step 4: Test and Share
1. Run: `test_public_access.bat` to verify everything works
2. Share your **frontend** ngrok URL with anyone!

### Manual Setup (if you prefer control)

#### Step 1: Start RABuddy locally
```bash
# Start backend (public version)
cd backend
python public_app.py

# Start frontend (in new terminal)
cd frontend  
npm run dev
```

#### Step 2: Create ngrok tunnels
```bash
# Terminal 1 - Backend tunnel
ngrok http 5001

# Terminal 2 - Frontend tunnel
ngrok http 3003
```

#### Step 3: Update environment
```bash
# Edit frontend/.env.local
NEXT_PUBLIC_API_URL=https://YOUR-BACKEND-NGROK-URL.ngrok.io/api
```

#### Step 4: Restart frontend
```bash
cd frontend
npm run dev
```

### Alternative: Using Cloudflare Tunnel (Custom Domain)

#### Step 1: Install Cloudflare Tunnel
```bash
# Download from: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/
```

#### Step 2: Setup custom domain
```bash
# Login to Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create rabuddy

# Route domain
cloudflared tunnel route dns rabuddy yourapp.yourdomain.com
cloudflared tunnel route dns rabuddy api.yourdomain.com
```

#### Step 3: Configure tunnel
Create `~/.cloudflared/config.yml`:
```yaml
tunnel: rabuddy
credentials-file: /path/to/credentials.json

ingress:
  - hostname: api.yourdomain.com
    service: http://localhost:5001
  - hostname: yourapp.yourdomain.com  
    service: http://localhost:3003
  - service: http_status:404
```

#### Step 4: Run tunnel
```bash
cloudflared tunnel run rabuddy
```

### Alternative: Using LocalTunnel (No Account)

#### Step 1: Install
```bash
npm install -g localtunnel
```

#### Step 2: Create tunnels
```bash
# Backend (use consistent subdomain)
lt --port 5001 --subdomain rabuddy-api

# Frontend (use consistent subdomain)  
lt --port 3003 --subdomain rabuddy-app
```

URLs will be:
- Backend: `https://rabuddy-api.loca.lt`
- Frontend: `https://rabuddy-app.loca.lt`

## Security Considerations

### Public Access Backend Features
- ✅ Enhanced CORS configuration
- ✅ Origin tracking for analytics
- ✅ Request logging for monitoring
- ✅ Public access indicators
- ✅ Rate limiting ready (can be added)

### Recommended Settings
```bash
# Backend environment (.env)
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://yourdomain.com,https://anotherdomain.com

# For production, consider:
RATE_LIMIT_ENABLED=true
MAX_REQUESTS_PER_MINUTE=60
REQUIRE_API_KEY=false  # Set to true for restricted access
```

## Sharing Your RABuddy

Once set up, anyone can access your RABuddy by:

1. **Frontend URL**: `https://abc123.ngrok.io` (or your custom domain)
2. **Mobile-friendly**: Works on phones, tablets, computers
3. **No installation**: Just open the URL in any browser
4. **Real-time**: All features work exactly like local version

### Example URLs
```
Frontend (share this): https://rabuddy-frontend.ngrok.io
Backend (for API):     https://rabuddy-backend.ngrok.io
Health check:          https://rabuddy-backend.ngrok.io/health
```

## Troubleshooting

### Common Issues

#### 1. ngrok tunnel not working
```bash
# Check if ngrok is authenticated
ngrok config check

# Restart tunnel with verbose logging
ngrok http 5001 --log stdout
```

#### 2. CORS errors in browser
- Ensure you updated the frontend `.env.local`
- Use HTTPS URLs from ngrok (not HTTP)
- Clear browser cache

#### 3. API not responding
```bash
# Test backend directly
curl https://your-backend-url.ngrok.io/health

# Check logs in backend terminal
```

#### 4. Frontend can't reach backend
- Verify API URL in `.env.local` is correct
- Ensure it ends with `/api`
- Restart frontend after changing environment

### Monitoring

#### Check public access status
```bash
# Backend health
curl https://your-backend-url.ngrok.io/health

# Test query
curl -X POST https://your-backend-url.ngrok.io/api/test \
  -H "Content-Type: application/json"

# Full query test
curl -X POST https://your-backend-url.ngrok.io/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}'
```

#### Monitor usage
- Check backend logs for request origins
- Monitor ngrok dashboard for traffic stats
- Use `public_app.py` logs for detailed tracking

## Next Steps

After Option 1 is working:
- ✅ Test with friends/colleagues
- ✅ Monitor performance and usage
- ✅ Consider moving to Option 2 (hosted deployment)
- ✅ Add custom domain with Cloudflare Tunnel
- ✅ Implement usage analytics
