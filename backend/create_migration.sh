#!/bin/bash

cd ~/qms-agent-system/backend
source venv/bin/activate

echo "Creating initial database migration..."
alembic revision --autogenerate -m "Initial migration: all QMS tables"

echo "Migration created successfully!"
echo "To apply migration, run: alembic upgrade head"
