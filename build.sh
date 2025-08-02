#!/bin/bash

# Build frontend
cd insights-frontend
npm install
npm run build

# Create the out directory in the root
mkdir -p ../out

# Copy the build files to the root out directory
cp -r out/* ../out/

# Go back to root
cd ..

# Install Python dependencies
pip install -r requirements.txt
