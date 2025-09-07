@echo off
echo === DEMARRAGE DU BACKEND EAZZYLOTTO ===
echo.

REM Activation de l'environnement virtuel
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Impossible d'activer l'environnement virtuel
    pause
    exit /b 1
)
echo [OK] Environnement virtuel active
echo.

REM Installation/Mise à jour des dépendances
pip install fastapi uvicorn sqlalchemy databases python-multipart
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Impossible d'installer les dependances
    pause
    exit /b 1
)
echo [OK] Dependances installees
echo.

REM Démarrage du serveur FastAPI
echo [INFO] Demarrage du serveur FastAPI sur le port 8081...
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8081

pause