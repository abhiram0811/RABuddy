#!/bin/bash

echo "🚀 RABuddy Backend Deployment Helper"
echo "===================================="

echo ""
echo "✅ Code changes made:"
echo "1. ✅ Fixed CORS origins in config.py"
echo "2. ✅ Added specific Vercel domain to CORS whitelist"
echo "3. ✅ Added query_id field to API responses"
echo "4. ✅ Added OPTIONS method support for CORS preflight"
echo "5. ✅ Fixed fallback routes in app.py"

echo ""
echo "📝 To deploy these changes:"
echo "1. If using git deployment:"
echo "   git add ."
echo "   git commit -m \"Fix CORS and API response format\""
echo "   git push origin main"

echo ""
echo "2. If using manual deployment:"
echo "   - Upload the updated backend/ directory to your Render service"
echo "   - Or trigger a manual deploy in Render dashboard"

echo ""
echo "🔍 Current backend status:"
curl -s -o /dev/null -w "Health check: %{http_code}\n" https://rabuddy-backend.onrender.com/health

echo ""
echo "🧪 Test after deployment:"
echo "bash test_backend_connectivity.sh"

echo ""
echo "🌐 Your frontend should connect to:"
echo "https://rabuddy-backend.onrender.com/api"
