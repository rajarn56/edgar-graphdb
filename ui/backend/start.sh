#!/bin/bash
# Start script for FastAPI backend

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch venv/.installed
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Please create one with Neo4j credentials."
    echo "Example:"
    echo "  NEO4J_URI=bolt://localhost:7687"
    echo "  NEO4J_USER=neo4j"
    echo "  NEO4J_PASSWORD=your_password"
fi

# Start server
echo "Starting FastAPI backend on http://localhost:8000"
uvicorn app:app --reload --port 8000

