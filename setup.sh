#!/bin/bash
set -e

echo "=== System Compilation Pipeline Starting ==="

# 1. Clear out any broken previous staging setups
rm -rf build
mkdir build
cd build

# 2. Configure project and build optimized release binaries
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build . --config Release -j$(nproc 2>/dev/null || echo 2)

# 3. Copy compiled shared library module to root folder for Python visibility
cp spatial_math_py*.so .. 2>/dev/null || true

echo "=== System Compilation Finished Successfully ==="
