#!/bin/bash

set -e

echo "Installing ChromaDB dependencies..."

echo "Step 1: Installing build tools..."
sudo apt update
sudo apt install -y build-essential python3-dev

echo "Step 2: Activating virtual environment..."
cd ~/qms-agent-system/backend
source venv/bin/activate

echo "Step 3: Installing ChromaDB..."
pip install chromadb==0.4.22

echo "ChromaDB installation completed!"
echo "You can now use the full RAG functionality."
