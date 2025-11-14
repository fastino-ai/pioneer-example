#!/bin/bash

# Pioneer + OpenAI Chat - Start Script
# This script starts both the backend and frontend servers

echo "🚀 Starting Pioneer + OpenAI Chat..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy env.example to .env and add your API keys:"
    echo "  cp env.example .env"
    echo "  # Then edit .env with your actual API keys"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update Python dependencies
echo "📦 Installing Python dependencies..."
pip install -q -r requirements.txt
echo "✓ Python dependencies installed"
echo ""

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo "✓ Frontend dependencies installed"
    echo ""
fi

# Start backend in background
echo "🖥️  Starting backend server..."
python backend/main.py &
BACKEND_PID=$!
echo "✓ Backend started (PID: $BACKEND_PID)"
echo ""

# Wait a moment for backend to start
sleep 2

# Start frontend in background
echo "🎨 Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..
echo "✓ Frontend started (PID: $FRONTEND_PID)"
echo ""

echo "✅ Application is running!"
echo ""
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    # Kill any remaining processes on the ports
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    lsof -ti:3000 | xargs kill -9 2>/dev/null
    echo "✓ Servers stopped"
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup INT TERM

# Wait for processes
wait

