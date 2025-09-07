@echo off
echo ========================================
echo    DEMARRAGE SIMPLE DES SERVEURS
echo ========================================
echo.

echo 1. Demarrage du Backend...
cd backend
start "Backend" cmd /k "python main_complete.py"
cd ..

echo 2. Demarrage du Frontend...
cd frontend
start "Frontend" cmd /k "python server.py"
cd ..

echo.
echo ========================================
echo    SERVEURS DEMARRES
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:8081
echo Dashboard: http://localhost:8081/dashboard.html
echo.
echo Appuyez sur une touche pour fermer...
pause > nul 