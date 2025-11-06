@echo off
echo 🚀 Démarrage d'EazzyCalculator...
echo.
echo 📁 Dossier de travail: %CD%
echo 👤 Utilisateur Git: ciano228
echo 📧 Email: brightmc33@gmail.com
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python n'est pas installé ou pas dans le PATH
    echo 💡 Installez Python depuis https://python.org
    pause
    exit /b 1
)

echo ✅ Python détecté
echo.

REM Créer le dossier data s'il n'existe pas
if not exist "backend\data" (
    echo 📁 Création du dossier backend\data...
    mkdir backend\data
)

REM Démarrer le serveur intégré
echo 🌐 Démarrage du serveur intégré...
echo 🔗 Interface: http://localhost:8000/katula-dynamic.html
echo 📊 API: http://localhost:8000/docs
echo.
echo 💡 Appuyez sur Ctrl+C pour arrêter le serveur
echo.

python integrated_server.py

pause