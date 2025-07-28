#!/bin/bash
# Test the newly deployed Render backend

echo "🧪 Testing RABuddy Backend on Render..."
echo "=================================="

# Test health endpoint
echo "1. Testing health endpoint..."
curl -s -w "\nStatus: %{http_code}\n" https://rabuddy-backend.onrender.com/health

echo -e "\n2. Testing API test endpoint..."
curl -s -w "\nStatus: %{http_code}\n" https://rabuddy-backend.onrender.com/api/test

echo -e "\n3. Testing query endpoint with sample question..."
curl -s -w "\nStatus: %{http_code}\n" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the guest policies?"}' \
  https://rabuddy-backend.onrender.com/api/query

echo -e "\n✅ Test completed!"
