@echo off
echo ========================================
echo    DEMARRAGE DES SERVEURS EAZZYCALCULATOR
echo ========================================
echo.

echo 1. Demarrage du Backend (Port 8000)...
cd backend
start "Backend API" cmd /k "python main_complete.py"
cd ..

echo 2. Demarrage du Frontend (Port 8081)...
cd frontend
start "Frontend Server" cmd /k "python server.py"
cd ..

echo.
echo ========================================
echo    SERVEURS EN COURS DE DEMARRAGE
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo Frontend:    http://localhost:8081
echo Dashboard:   http://localhost:8081/dashboard.html
echo.
echo Appuyez sur une touche pour fermer cette fenetre...
pause > nul 