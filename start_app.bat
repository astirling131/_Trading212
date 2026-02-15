@echo off
echo ==========================================
echo   Trading Data Scraper - Startup Script
echo ==========================================

echo.
echo [1/2] Starting FastAPI Backend...
start "Trading212 Backend" cmd /k "uvicorn api:app --reload"

echo.
echo [2/2] Starting React Frontend...
cd frontend
start "Trading212 Frontend" cmd /k "npm run dev"

echo.
echo ==========================================
echo   App launched!
echo   Backend: http://127.0.0.1:8000
echo   Frontend: http://localhost:5173
echo ==========================================
pause
