@echo off
REM Pioneer + OpenAI Chat - Start Script for Windows
REM This script starts both the backend and frontend servers

echo.
echo 🚀 Starting Pioneer + OpenAI Chat...
echo.

REM Check if .env exists
if not exist .env (
    echo ❌ Error: .env file not found!
    echo Please copy env.example to .env and add your API keys:
    echo   copy env.example .env
    echo   REM Then edit .env with your actual API keys
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
    echo ✓ Virtual environment created
    echo.
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update Python dependencies
echo 📦 Installing Python dependencies...
pip install -q -r requirements.txt
echo ✓ Python dependencies installed
echo.

REM Check if frontend dependencies are installed
if not exist frontend\node_modules (
    echo 📦 Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
    echo ✓ Frontend dependencies installed
    echo.
)

REM Start backend in new window
echo 🖥️  Starting backend server...
start "Pioneer Backend" cmd /k "venv\Scripts\activate.bat && python backend\main.py"
echo ✓ Backend started
echo.

REM Wait a moment for backend to start
timeout /t 2 /nobreak >nul

REM Start frontend in new window
echo 🎨 Starting frontend server...
start "Pioneer Frontend" cmd /k "cd frontend && npm run dev"
echo ✓ Frontend started
echo.

echo ✅ Application is running!
echo.
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo.
echo Close the terminal windows to stop the servers
echo.
pause

