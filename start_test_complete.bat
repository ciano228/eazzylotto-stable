@echo off
echo ========================================
echo    EAZZYLOTTO - DEMARRAGE COMPLET
echo ========================================
echo.

echo [1/4] Verification de la base de donnees...
cd backend
python fix_database.py
echo.

echo [2/4] Generation des donnees de test...
python generate_test_data.py
echo.

echo [3/4] Demarrage du serveur backend...
start "EazzyLotto Backend" python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
timeout /t 3 /nobreak > nul
echo Backend demarre sur http://localhost:8000
echo.

echo [4/4] Demarrage du serveur frontend...
cd ..\frontend
start "EazzyLotto Frontend" python -m http.server 8081
timeout /t 2 /nobreak > nul
echo Frontend demarre sur http://localhost:8081
echo.

echo ========================================
echo    APPLICATION PRETE !
echo ========================================
echo.
echo Pages de test principales :
echo - Dashboard        : http://localhost:8081/dashboard.html
echo - Test Sessions    : http://localhost:8081/test-sessions-data.html
echo - Tour Guide       : http://localhost:8081/katooling-tour.html
echo - Journal Stats    : http://localhost:8081/advanced-journal.html
echo - Analyse Temp     : http://localhost:8081/katula-temporal-analysis.html
echo - Predictions IA   : http://localhost:8081/lstm-neural-network.html
echo - Patterns         : http://localhost:8081/pattern-viewer.html
echo - Multi-Univers    : http://localhost:8081/katula-multi-universe.html
echo.
echo API Backend        : http://localhost:8000/docs
echo.

echo Ouverture automatique du dashboard...
timeout /t 3 /nobreak > nul
start http://localhost:8081/dashboard.html

echo.
echo Appuyez sur une touche pour fermer...
pause > nul