# Script de démarrage EazzyLotto
Write-Host "🎯 Démarrage EazzyLotto.com..." -ForegroundColor Green

# Démarrer le backend en arrière-plan
Write-Host "🔧 Démarrage du backend (port 8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

# Attendre 3 secondes
Start-Sleep -Seconds 3

# Démarrer le frontend
Write-Host "🌐 Démarrage du frontend (port 8081)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; python server.py"

# Attendre 2 secondes
Start-Sleep -Seconds 2

# Ouvrir le navigateur
Write-Host "🚀 Ouverture du navigateur..." -ForegroundColor Green
Start-Process "http://localhost:8081/index.html"

Write-Host "✅ EazzyLotto démarré avec succès !" -ForegroundColor Green
Write-Host "📱 Page de connexion : http://localhost:8081/index.html" -ForegroundColor Cyan
Write-Host "📊 Dashboard : http://localhost:8081/dashboard.html" -ForegroundColor Cyan
Write-Host "🔧 API Docs : http://localhost:8000/docs" -ForegroundColor Cyan