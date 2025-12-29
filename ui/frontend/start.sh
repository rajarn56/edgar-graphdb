#!/bin/bash
# Start script for React frontend

cd "$(dirname "$0")"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start development server
echo "Starting React frontend on http://localhost:5173"
npm run dev

