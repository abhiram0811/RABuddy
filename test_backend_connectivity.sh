#!/bin/bash

echo "🔍 Testing RABuddy Backend..."
echo "================================"

# Test 1: Check if backend is responding
echo "1. Testing basic connectivity..."
echo "URL: https://rabuddy-backend.onrender.com/health"
curl -s -o /dev/null -w "Status: %{http_code}\n" https://rabuddy-backend.onrender.com/health

echo ""
echo "2. Testing API status..."
echo "URL: https://rabuddy-backend.onrender.com/api/status"
curl -s -o /dev/null -w "Status: %{http_code}\n" https://rabuddy-backend.onrender.com/api/status

echo ""
echo "3. Testing API test endpoint..."
echo "URL: https://rabuddy-backend.onrender.com/api/test"
curl -s -o /dev/null -w "Status: %{http_code}\n" https://rabuddy-backend.onrender.com/api/test

echo ""
echo "4. Testing CORS preflight..."
echo "URL: https://rabuddy-backend.onrender.com/api/query"
curl -s -X OPTIONS \
  -H "Origin: https://rabuddy-5ncawvp74-abhiram-reddy-mulintis-projects.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -o /dev/null -w "Status: %{http_code}\n" \
  https://rabuddy-backend.onrender.com/api/query

echo ""
echo "5. Testing actual query..."
curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Origin: https://rabuddy-5ncawvp74-abhiram-reddy-mulintis-projects.vercel.app" \
  -d '{"question": "Test question"}' \
  -o /dev/null -w "Status: %{http_code}\n" \
  https://rabuddy-backend.onrender.com/api/query

echo ""
echo "🏁 Test complete!"
