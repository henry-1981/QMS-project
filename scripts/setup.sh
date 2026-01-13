#!/bin/bash

set -e

echo "QMS Agent System - Development Environment Setup"
echo "=================================================="

echo "Step 1: Installing system dependencies..."
sudo apt update
sudo apt install -y python3.12-venv postgresql postgresql-contrib python3-pip

echo "Step 2: Creating Python virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate

echo "Step 3: Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Step 4: Setting up PostgreSQL..."
sudo -u postgres createdb qms_db 2>/dev/null || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER qms_user WITH PASSWORD 'qms_password';" 2>/dev/null || echo "User already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE qms_db TO qms_user;"

echo "Step 5: Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Please edit .env file with your API keys"
fi

echo "Step 6: Initializing database..."
alembic upgrade head

echo "Setup completed!"
echo "To start the server:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload"
