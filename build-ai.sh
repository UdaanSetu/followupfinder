#!/bin/bash
echo "🏗️ Building the FollowUpFinder AI Docker image..."
# Build the image using the Dockerfile in the ai/ directory
docker build -t followupfinder-ai:latest -f ai/Dockerfile ai/
echo "📤 Importing image directly into the Kubernetes cluster engine..."
k3d image import followupfinder-ai:latest -c followupfinder
echo "✅ Build complete! You will now see it in Docker Desktop."

