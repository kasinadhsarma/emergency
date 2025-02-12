#!/bin/bash

# Start backend server
echo "Installing Python dependencies..."
cd backend
python3 -m pip install -r requirements.txt

echo "Starting backend server..."
python3 -m uvicorn app:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend server
cd ..
echo "Installing frontend dependencies..."
npm install

echo "Starting frontend server..."
npm run dev &
FRONTEND_PID=$!

# Handle script termination
trap 'kill $BACKEND_PID $FRONTEND_PID' EXIT

# Wait for both processes
wait
