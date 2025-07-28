#!/bin/bash

echo "🚀 TESTING NUCLEAR DEPLOYMENT"
echo "=============================="
echo ""

echo "Waiting 30 seconds for deployment to complete..."
sleep 30

echo ""
echo "Testing /api/test endpoint..."
response=$(curl -s https://rabuddy-backend.onrender.com/api/test)
echo "Response: $response"

if [[ $response == *"NUCLEAR"* ]]; then
    echo ""
    echo "🎉🎉🎉 SUCCESS! NUCLEAR DEPLOYMENT WORKED! 🎉🎉🎉"
    echo ""
    echo "Now testing a query..."
    curl -s -X POST -H "Content-Type: application/json" \
      -d '{"question": "Test question"}' \
      https://rabuddy-backend.onrender.com/api/query | jq .
else
    echo ""
    echo "❌ Still not working. Checking debug info..."
    curl -s https://rabuddy-backend.onrender.com/debug/env | jq .
fi
