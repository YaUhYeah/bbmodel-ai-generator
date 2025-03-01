#!/bin/bash

# Exit on error
set -e

echo "Installing backend dependencies..."
cd /workspace/bbmodel-ai-generator/backend
pip install -r requirements.txt

echo "Installing frontend dependencies..."
cd /workspace/bbmodel-ai-generator/frontend
npm install

echo "Dependencies installed successfully!"