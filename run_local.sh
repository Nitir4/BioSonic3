#!/bin/bash

# BioSonic Local Development Runner
# ────────────────────────────────

# Function to kill background processes on exit
cleanup() {
    echo ""
    echo "Stopping BioSonic services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Trap SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

echo "🚀 Setting up BioSonic Local Development Environment..."

# 1. Setup Python Virtual Environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# 2. Install Backend Requirements
echo "📥 Installing backend requirements..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# 3. Install Frontend Dependencies
echo "📥 Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "🚀 Starting BioSonic services..."

# 4. Start Backend
echo "Starting Backend (FastAPI) on http://localhost:8080..."
cd backend
# We use --reload for development
uvicorn api:app --host 0.0.0.0 --port 8080 --reload &
BACKEND_PID=$!
cd ..

# 5. Start Frontend
echo "Starting Frontend (Vite) on http://localhost:5173..."
cd frontend
# Point frontend to the local backend port
export VITE_API_URL="http://localhost:8080"
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ Both services are running!"
echo "   - Frontend: http://localhost:5173"
echo "   - Backend:  http://localhost:8080"
echo "Press Ctrl+C to stop both."

# Wait for background processes to finish
wait
