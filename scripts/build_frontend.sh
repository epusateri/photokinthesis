#!/bin/bash
# Build script for Photokinthesis React frontend

set -e

echo "Building React frontend..."

# Navigate to frontend directory
cd "$(dirname "$0")/../frontend"

# Install dependencies
echo "Installing npm dependencies..."
npm install

# Build for production
echo "Building production bundle..."
npm run build

# Copy built files to Flask static directory
echo "Copying built files to Flask static directory..."
rm -rf ../src/photokinthesis/web/static/*
cp -r dist/* ../src/photokinthesis/web/static/

echo ""
echo "✓ Frontend build complete!"
echo "  Built files copied to src/photokinthesis/web/static/"
echo ""
echo "You can now run the server:"
echo "  photokinthesis serve --collection-xmp-dir ./collections --collection-image-dir ./images"
