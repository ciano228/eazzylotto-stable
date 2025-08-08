@echo off
echo ========================================
echo    EAZZYLOTTO - TEST APPLICATION
echo ========================================
echo.

echo [1/2] Demarrage du serveur frontend...
cd frontend
start "EazzyLotto Frontend" python -m http.server 8081
echo Frontend demarre sur http://localhost:8081
echo.

echo [2/2] Tentative de demarrage du backend...
cd ..\backend
start "EazzyLotto Backend" python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
echo Backend demarre sur http://localhost:8000
echo.

echo ========================================
echo    APPLICATION DEMARREE !
echo ========================================
echo.
echo Pages principales :
echo - Page d'accueil : http://localhost:8081/index.html
echo - Tour guide     : http://localhost:8081/katooling-tour.html
echo - Dashboard      : http://localhost:8081/dashboard.html
echo - Parametres     : http://localhost:8081/parametres.html
echo.
echo Appuyez sur une touche pour ouvrir l'application...
pause > nul

start http://localhost:8081/index.html