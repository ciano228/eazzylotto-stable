@echo off
echo 🎯 Démarrage EazzyLotto.com...

echo 🔧 Démarrage du backend (port 8000)...
start "EazzyLotto Backend" cmd /k "cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo 🌐 Démarrage du frontend (port 8081)...
start "EazzyLotto Frontend" cmd /k "cd frontend && python server.py"

timeout /t 2 /nobreak >nul

echo 🚀 Ouverture du navigateur...
start http://localhost:8081/index.html

echo ✅ EazzyLotto démarré avec succès !
echo 📱 Page de connexion : http://localhost:8081/index.html
echo 📊 Dashboard : http://localhost:8081/dashboard.html  
echo 🔧 API Docs : http://localhost:8000/docs

pause