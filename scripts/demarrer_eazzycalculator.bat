@echo off
title EazzyCalculator - Demarrage Systeme
color 0A

echo.
echo ========================================
echo    EAZZYCALCULATOR - SYSTEME UNIFIE
echo ========================================
echo.

echo [1/3] Demarrage du Backend API...
echo      Port: 8000
echo      API: FastAPI avec 5 univers complets
echo.
start "EazzyCalculator Backend" cmd /k "cd /d %~dp0backend && python main.py"

echo Attente du demarrage du backend...
timeout /t 5 /nobreak > nul

echo [2/3] Demarrage du Frontend...
echo      Port: 8080
echo      Structure: Unifiee et organisee
echo.
start "EazzyCalculator Frontend" cmd /k "cd /d %~dp0app && python -m http.server 8080"

echo Attente du demarrage du frontend...
timeout /t 3 /nobreak > nul

echo [3/3] Ouverture du navigateur...
echo      URL: http://localhost:8080
echo.
start http://localhost:8080

echo.
echo ========================================
echo         SYSTEME DEMARRE AVEC SUCCES
echo ========================================
echo.
echo  Backend API:     http://localhost:8000
echo  Frontend App:    http://localhost:8080
echo  Test Colonnes:   http://localhost:8080/test-nouvelles-colonnes.html
echo  Dashboard:       http://localhost:8080/pages/dashboard/dashboard.html
echo.
echo  Fonctionnalites disponibles:
echo  - 5 univers complets (Mundo, Fruity, Trigga, Roaster, Sunshine)
echo  - Nouvelles colonnes (granque-name, tome)
echo  - Sessions fonctionnelles
echo  - Structure unifiee et organisee
echo.
echo Appuyez sur une touche pour fermer cette fenetre...
pause > nul