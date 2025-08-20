param(
    [switch]$NoBrowser
)

Write-Host "🎯 EazzyLotto - Lanceur Automatique" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Yellow

# Fonction pour démarrer le backend
function Start-Backend {
    Write-Host "🔧 Démarrage du backend..." -ForegroundColor Cyan
    
    try {
        # Vérifier si le dossier backend existe
        if (Test-Path "backend") {
            Set-Location "backend"
            
            # Chercher le fichier main
            $mainFile = "main"
            if (Test-Path "main_fixed.py") { $mainFile = "main_fixed" }
            elseif (Test-Path "app.py") { $mainFile = "app" }
            
            Write-Host "📁 Utilisation de $mainFile.py" -ForegroundColor Yellow
            
            # Démarrer uvicorn en arrière-plan
            $backendJob = Start-Job -ScriptBlock {
                param($mainFile)
                python -m uvicorn "$($mainFile):app" --reload --host 0.0.0.0 --port 8000
            } -ArgumentList $mainFile
            
            Set-Location ".."
            Start-Sleep 3
            
            Write-Host "✅ Backend démarré sur http://localhost:8000" -ForegroundColor Green
            return $backendJob
        } else {
            Write-Host "❌ Dossier backend introuvable" -ForegroundColor Red
            return $null
        }
    }
    catch {
        Write-Host "❌ Erreur backend: $($_.Exception.Message)" -ForegroundColor Red
        Set-Location ".."
        return $null
    }
}

# Fonction pour démarrer le frontend
function Start-Frontend {
    Write-Host "🌐 Démarrage du frontend..." -ForegroundColor Cyan
    
    try {
        # Vérifier si le dossier frontend existe, sinon utiliser le dossier racine
        $frontendPath = if (Test-Path "frontend") { "frontend" } else { "." }
        
        Set-Location $frontendPath
        
        # Démarrer le serveur HTTP
        $frontendJob = Start-Job -ScriptBlock {
            python -m http.server 8081
        }
        
        if ($frontendPath -ne ".") { Set-Location ".." }
        Start-Sleep 2
        
        Write-Host "✅ Frontend démarré sur http://localhost:8081" -ForegroundColor Green
        return $frontendJob
    }
    catch {
        Write-Host "❌ Erreur frontend: $($_.Exception.Message)" -ForegroundColor Red
        if ($frontendPath -ne ".") { Set-Location ".." }
        return $null
    }
}

# Fonction pour ouvrir le navigateur
function Open-Browser {
    if (-not $NoBrowser) {
        Write-Host "🌐 Ouverture du navigateur..." -ForegroundColor Cyan
        Start-Sleep 2
        
        $urls = @(
            "http://localhost:8081/launching-page.html",
            "http://localhost:8081/index.html",
            "http://localhost:8081"
        )
        
        foreach ($url in $urls) {
            try {
                Start-Process $url
                Write-Host "✅ Navigateur ouvert: $url" -ForegroundColor Green
                break
            }
            catch {
                Write-Host "⚠️ Tentative suivante..." -ForegroundColor Yellow
            }
        }
    }
}

# Fonction pour afficher le statut
function Show-Status {
    Write-Host ""
    Write-Host "🎉 EAZZYLOTTO DÉMARRÉ AVEC SUCCÈS !" -ForegroundColor Green
    Write-Host "=" * 50 -ForegroundColor Yellow
    Write-Host "📱 URLs de l'application:" -ForegroundColor Cyan
    Write-Host "   🏠 Accueil: http://localhost:8081/launching-page.html" -ForegroundColor White
    Write-Host "   📊 Dashboard: http://localhost:8081/dashboard.html" -ForegroundColor White
    Write-Host "   🎯 Smart Input: http://localhost:8081/smart-input.html" -ForegroundColor White
    Write-Host "   🔧 API Docs: http://localhost:8000/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Serveurs actifs:" -ForegroundColor Cyan
    Write-Host "   ⚙️ Backend API: http://localhost:8000" -ForegroundColor White
    Write-Host "   🌐 Frontend: http://localhost:8081" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Appuyez sur Ctrl+C pour arrêter l'application" -ForegroundColor Yellow
    Write-Host "=" * 50 -ForegroundColor Yellow
}

# Script principal
try {
    Write-Host "🚀 Démarrage de EazzyLotto..." -ForegroundColor Green
    
    # Démarrer le backend
    $backendJob = Start-Backend
    
    # Démarrer le frontend
    $frontendJob = Start-Frontend
    
    # Ouvrir le navigateur
    Open-Browser
    
    # Afficher le statut
    Show-Status
    
    # Garder le script en vie
    Write-Host "Appuyez sur une touche pour arrêter l'application..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
catch {
    Write-Host "❌ Erreur critique: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    # Nettoyer les jobs
    Write-Host "🛑 Arrêt de l'application..." -ForegroundColor Yellow
    
    if ($backendJob) {
        Stop-Job $backendJob -ErrorAction SilentlyContinue
        Remove-Job $backendJob -ErrorAction SilentlyContinue
        Write-Host "✅ Backend arrêté" -ForegroundColor Green
    }
    
    if ($frontendJob) {
        Stop-Job $frontendJob -ErrorAction SilentlyContinue
        Remove-Job $frontendJob -ErrorAction SilentlyContinue
        Write-Host "✅ Frontend arrêté" -ForegroundColor Green
    }
    
    Write-Host "👋 Au revoir !" -ForegroundColor Green
}@echo off
REM File: /c/Users/User/eazzycalculator/quick_launch.bat
title EazzyLotto Quick Launch
color 0A

echo 🎯 EazzyLotto - Lancement Rapide
echo.

echo Demarrage backend...
cd backend 2>nul || echo Backend folder not found
start "Backend" cmd /k "python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 || python -m uvicorn main_fixed:app --reload --host 0.0.0.0 --port 8000"

echo Demarrage frontend...
cd .. 2>nul
start "Frontend" cmd /k "python -m http.server 8081"

echo Attente 5 secondes...
timeout /t 5 /nobreak >nul

echo Ouverture navigateur...
start http://localhost:8081/launching-page.html

echo.
echo ✅ EazzyLotto lance !
echo 📱 http://localhost:8081/launching-page.html
echo 🔧 http://localhost:8000/docs
echo.
pause