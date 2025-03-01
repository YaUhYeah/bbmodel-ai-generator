#!/bin/bash

# Start the backend server
echo "Starting backend server..."
cd /workspace/bbmodel-ai-generator/backend
python run.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 2

# Start the frontend server
echo "Starting frontend server..."
cd /workspace/bbmodel-ai-generator/frontend
npm start &
FRONTEND_PID=$!

# Function to handle script termination
function cleanup {
  echo "Stopping servers..."
  kill $BACKEND_PID
  kill $FRONTEND_PID
  exit
}

# Trap SIGINT (Ctrl+C) and call cleanup
trap cleanup SIGINT

# Keep script running
echo "Servers are running. Press Ctrl+C to stop."
wait