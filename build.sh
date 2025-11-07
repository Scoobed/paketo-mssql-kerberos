#!/bin/bash
set -e

echo "Building Paketo MSSQL Kerberos Buildpack"
echo "=========================================="

# Check if pack is installed
if ! command -v pack &> /dev/null; then
    echo "Error: pack CLI is not installed"
    echo "Install it from: https://buildpacks.io/docs/tools/pack/"
    exit 1
fi

# Package the buildpack
echo ""
echo "Step 1: Packaging buildpack..."
pack buildpack package scoobed/mssql-kerberos:latest \
    --config package.toml

echo ""
echo "✓ Buildpack packaged successfully"

# Optional: Test with example app
if [ "$1" == "--test" ]; then
    echo ""
    echo "Step 2: Testing with Python example..."
    # cd examples/python
    cd ../samples/python/pipenv
    
    pack build mssql-test-app \
        --buildpack scoobed/mssql-kerberos:latest \
        --buildpack paketobuildpacks/python:latest \
        --builder paketobuildpacks/builder-jammy-base \
        --env BP_ENABLE_MSSQL_ODBC=true
    
    echo ""
    echo "✓ Test build complete"
    echo ""
    echo "Run the test app with:"
    echo "  docker run -p 8080:8080 mssql-test-app"
fi

echo ""
echo "Build complete!"
echo ""
echo "Usage:"
echo "  pack build myapp \\"
echo "    --buildpack scoobed/mssql-kerberos:latest \\"
echo "    --buildpack gcr.io/paketo-buildpacks/python \\"
echo "    --builder paketobuildpacks/builder-jammy-base"
