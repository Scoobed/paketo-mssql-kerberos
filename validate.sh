#!/bin/bash

echo "Validating Paketo MSSQL Kerberos Buildpack"
echo "==========================================="
echo ""

ERRORS=0

# Check required files
echo "Checking required files..."
FILES=("buildpack.toml" "package.toml" "bin/detect" "bin/build")
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (missing)"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "Checking file permissions..."
SCRIPTS=("bin/detect" "bin/build")
for script in "${SCRIPTS[@]}"; do
    if [ -x "$script" ]; then
        echo "  ✓ $script (executable)"
    else
        echo "  ✗ $script (not executable)"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "Validating buildpack.toml..."
if grep -q "id = \"scoobed/mssql-kerberos\"" buildpack.toml; then
    echo "  ✓ Buildpack ID found"
else
    echo "  ✗ Buildpack ID not found"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "api = \"0.7\"" buildpack.toml; then
    echo "  ✓ Buildpack API version found"
else
    echo "  ✗ Buildpack API version not found"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "Testing detect script..."
cd examples/python
if ../../bin/detect . /tmp 2>/dev/null; then
    echo "  ✓ Detect script runs (found pyodbc)"
else
    echo "  ⚠ Detect script didn't detect (expected if no pyodbc in requirements.txt)"
fi
cd ../..

echo ""
echo "Checking example applications..."
if [ -f "examples/python/requirements.txt" ]; then
    echo "  ✓ Python example found"
    if grep -q "pyodbc" examples/python/requirements.txt; then
        echo "  ✓ Python example has pyodbc"
    fi
fi

if [ -f "examples/nodejs/package.json" ]; then
    echo "  ✓ Node.js example found"
fi

echo ""
echo "Checking Kubernetes manifests..."
if [ -f "examples/kubernetes/deployment.yaml" ]; then
    echo "  ✓ Kubernetes deployment example found"
fi

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "================================================"
    echo "✓ Validation passed! Buildpack structure is OK"
    echo "================================================"
    echo ""
    echo "Next steps:"
    echo "1. Install Docker to build images with this buildpack"
    echo "2. Run: ./build.sh --test"
    echo ""
    echo "Or use directly with pack:"
    echo "  pack build myapp \\"
    echo "    --buildpack $PWD \\"
    echo "    --buildpack gcr.io/paketo-buildpacks/python \\"
    echo "    --builder paketobuildpacks/builder-jammy-base"
    exit 0
else
    echo "================================================"
    echo "✗ Validation failed with $ERRORS error(s)"
    echo "================================================"
    exit 1
fi
