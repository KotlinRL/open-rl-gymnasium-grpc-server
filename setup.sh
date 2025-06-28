#!/bin/bash

set -e

# Step 1: Navigate to the correct directory
cd "$(dirname "${BASH_SOURCE[0]}")"
PROJECT_ROOT=$(pwd)

# Step 2: Set up virtual environment
echo "Setting up a Python virtual environment..."
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate
echo "Virtual Environment Activated!"

# Step 3: Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 4: Generate gRPC stubs
PROTO_SRC="$PROJECT_ROOT/protos"
echo "Generating gRPC stubs for server and tests..."
python -m grpc_tools.protoc \
    -I"$PROTO_SRC" \
    --python_out=./src \
    --grpc_python_out=./src \
    "$PROTO_SRC"/*.proto

echo "gRPC stubs generated successfully!"

# Step 5. Run unit tests
deactivate
echo "Setup process completed successfully!"