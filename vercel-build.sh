#!/bin/bash

# Make script exit on first error
set -e

# Create backend directories
mkdir -p .vercel/backend

# Copy backend files
cp -r backend/* .vercel/backend/
cp requirements-vercel.txt .vercel/backend/requirements.txt

# Copy model files
mkdir -p .vercel/backend/models
cp backend/best.pt .vercel/backend/models/
cp backend/pick_best.pt .vercel/backend/models/

# Create temporary uploads directory
mkdir -p /tmp/uploads

echo "Build script completed successfully"
