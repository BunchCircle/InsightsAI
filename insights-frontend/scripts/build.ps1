# Build the Next.js application
npm run build

# Create the output directory if it doesn't exist
New-Item -ItemType Directory -Force -Path out

# Copy necessary files
if (Test-Path ".next/static") {
    Copy-Item -Path ".next/static" -Destination "out/static" -Recurse -Force
}
if (Test-Path ".next/server") {
    Copy-Item -Path ".next/server" -Destination "out/server" -Recurse -Force
}
if (Test-Path ".next/standalone") {
    Get-ChildItem -Path ".next/standalone/*" | Copy-Item -Destination "out/" -Recurse -Force
}

# Run the copy-build script
node scripts/copy-build.js
