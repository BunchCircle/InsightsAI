#!/bin/bash

# Build Next.js app
next build

# Export static files
next export -o out

# Ensure deployment directory exists
mkdir -p /app/insights-frontend/out

# Copy files to deployment directory
cp -r out/* /app/insights-frontend/out/
