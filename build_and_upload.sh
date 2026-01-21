#!/usr/bin/env bash
set -e

echo "Building cli-commons for PyPI..."
echo ""

if ! python -c "import build, twine" 2>/dev/null; then
    echo "Installing build tools..."
    pip install --quiet build twine
fi

echo "Cleaning old builds..."
rm -rf build dist *.egg-info

echo "Building package..."
python -m build

echo ""
echo "Build complete!"
ls -lh dist/

echo ""
echo "Checking package..."
twine check dist/*

echo ""
echo "Next: twine upload dist/*"
