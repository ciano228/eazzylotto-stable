@echo off
echo ========================================
echo    EAZZYLOTTO - TESTS FINAUX
echo ========================================
echo.

echo [1/4] Verification de la structure...
if not exist "backend\main.py" (
    echo ERREUR: Backend non trouve
    pause
    exit /b 1
)
if not exist "frontend\index.html" (
    echo ERREUR: Frontend non trouve
    pause
    exit /b 1
)
echo ✓ Structure OK

echo.
echo [2/4] Demarrage du backend...
cd backend
start "Backend Server" cmd /k "python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ✓ Backend demarre sur http://localhost:8000

echo.
echo [3/4] Demarrage du frontend...
cd ..\frontend
start "Frontend Server" cmd /k "python -m http.server 3000"
echo ✓ Frontend demarre sur http://localhost:3000

echo.
echo [4/4] Ouverture des pages de test...
timeout /t 3 /nobreak >nul
start http://localhost:8000/docs
start http://localhost:3000/index.html

echo.
echo ========================================
echo    TESTS A EFFECTUER:
echo ========================================
echo 1. API Documentation: http://localhost:8000/docs
echo 2. Login Page: http://localhost:3000/index.html
echo 3. Creer un compte et se connecter
echo 4. Tester le dashboard et la navigation
echo 5. Tester les fonctionnalites metier
echo.
echo Appuyez sur une touche pour continuer...
pause >nul