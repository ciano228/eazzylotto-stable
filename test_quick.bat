@echo off
echo ========================================
echo    TEST RAPIDE EAZZYLOTTO
echo ========================================
echo.

echo [1/3] Demarrage backend...
cd backend
start "Backend" python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
timeout /t 3 /nobreak > nul

echo [2/3] Demarrage frontend...
cd ..\frontend
start "Frontend" python -m http.server 8081
timeout /t 2 /nobreak > nul

echo [3/3] Ouverture des pages de test...
timeout /t 2 /nobreak > nul
start http://localhost:8081/smart-input.html
start http://localhost:8081/advanced-journal.html

echo.
echo ========================================
echo    TESTS A EFFECTUER :
echo ========================================
echo.
echo 1. Dans smart-input.html :
echo    - Verifier que les sessions se chargent
echo    - Cliquer sur "Journal Statistique"
echo.
echo 2. Dans advanced-journal.html :
echo    - Verifier que la session active est selectionnee
echo    - Cliquer sur "Charger le Journal"
echo.
echo Appuyez sur une touche pour fermer...
pause > nul