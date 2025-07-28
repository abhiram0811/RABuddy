# 🔑 GEMINI API Setup Instructions for Render

## Step 1: Get Your GEMINI API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key (starts with `AIza...`)

## Step 2: Add GEMINI API Key to Render
1. Go to your [Render Dashboard](https://dashboard.render.com/)
2. Click on your `rabuddy-backend` service
3. Go to "Environment" tab
4. Find the `GEMINI_API_KEY` variable
5. Paste your API key value: `AIzaSyCwukPFpzRp_OvgSaTeStb0yxCIMU7_KDg`
6. Click "Save Changes"

## Step 3: Trigger Manual Deploy
1. Go to "Manual Deploy" tab
2. Click "Deploy latest commit"
3. Wait for deployment to complete

## Step 4: Test the Deployment
```bash
# Test if the new deployment is working
curl https://rabuddy-backend.onrender.com/api/test

# Should return:
# {"message":"RABuddy Production API test successful",...}

# Test a query
curl -X POST -H "Content-Type: application/json" \
  -d '{"question": "What are the guest policies?"}' \
  https://rabuddy-backend.onrender.com/api/query
```

## Step 5: Debug if Needed
```bash
# Check environment variables
curl https://rabuddy-backend.onrender.com/debug/env
```

## 🎯 Expected Result
After setting up GEMINI API key:
- ✅ `/api/test` returns "RABuddy Production API test successful"
- ✅ `/api/query` returns actual RAG responses with PDF sources
- ✅ Your Vercel frontend works with real data

## 🔧 Your Current API Key
Your GEMINI API key from .env file: `AIzaSyCwukPFpzRp_OvgSaTeStb0yxCIMU7_KDg`
Copy this value into Render environment variables.
