@echo off
chcp 65001 >nul
cls

echo ================================================================
echo 🚀 EAZZYCALCULATOR - DÉMARRAGE RAPIDE
echo ================================================================
echo.

echo 📋 Vérification de l'installation...
echo.

python verifier_installation.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Problèmes détectés. Veuillez les corriger avant de continuer.
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo ✅ Installation validée!
echo ================================================================
echo.
echo 🚀 Démarrage du serveur...
echo.
echo 📍 URLs d'accès:
echo    - API: http://localhost:8000
echo    - Documentation: http://localhost:8000/api/docs
echo    - Frontend: http://localhost:8000/
echo.
echo ⚠️  Appuyez sur Ctrl+C pour arrêter le serveur
echo.
echo ================================================================
echo.

python start_backend.py

pause
