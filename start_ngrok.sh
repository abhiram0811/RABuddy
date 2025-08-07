#!/bin/bash

echo "🌐 Starting ngrok tunnels for RABuddy"

# Kill any existing ngrok processes
pkill -f ngrok

# Start ngrok with the configuration file
echo "🚀 Starting ngrok tunnels..."
ngrok start --all --config ngrok.yml
