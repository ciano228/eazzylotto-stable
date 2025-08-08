# Script PowerShell pour démarrer les serveurs EazzyCalculator
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DEMARRAGE DES SERVEURS EAZZYCALCULATOR" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier que nous sommes dans le bon répertoire
$currentDir = Get-Location
Write-Host "Répertoire actuel: $currentDir" -ForegroundColor Yellow

# Démarrer le Backend
Write-Host "1. Démarrage du Backend (Port 8000)..." -ForegroundColor Green
$backendPath = Join-Path $currentDir "backend"
if (Test-Path $backendPath) {
    Write-Host "   Dossier backend trouvé: $backendPath" -ForegroundColor Green
    $mainCompletePath = Join-Path $backendPath "main_complete.py"
    if (Test-Path $mainCompletePath) {
        Write-Host "   Fichier main_complete.py trouvé" -ForegroundColor Green
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; python main_complete.py" -WindowStyle Normal
        Write-Host "   Backend démarré dans une nouvelle fenêtre" -ForegroundColor Green
    } else {
        Write-Host "   ERREUR: main_complete.py non trouvé dans $backendPath" -ForegroundColor Red
    }
} else {
    Write-Host "   ERREUR: Dossier backend non trouvé" -ForegroundColor Red
}

Write-Host ""

# Démarrer le Frontend
Write-Host "2. Démarrage du Frontend (Port 8081)..." -ForegroundColor Green
$frontendPath = Join-Path $currentDir "frontend"
if (Test-Path $frontendPath) {
    Write-Host "   Dossier frontend trouvé: $frontendPath" -ForegroundColor Green
    $serverPath = Join-Path $frontendPath "server.py"
    if (Test-Path $serverPath) {
        Write-Host "   Fichier server.py trouvé" -ForegroundColor Green
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; python server.py" -WindowStyle Normal
        Write-Host "   Frontend démarré dans une nouvelle fenêtre" -ForegroundColor Green
    } else {
        Write-Host "   ERREUR: server.py non trouvé dans $frontendPath" -ForegroundColor Red
    }
} else {
    Write-Host "   ERREUR: Dossier frontend non trouvé" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    SERVEURS EN COURS DE DEMARRAGE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Frontend:    http://localhost:8081" -ForegroundColor Yellow
Write-Host "Dashboard:   http://localhost:8081/dashboard.html" -ForegroundColor Yellow
Write-Host ""
Write-Host "Attendez quelques secondes que les serveurs démarrent..." -ForegroundColor Green
Write-Host "Appuyez sur une touche pour fermer cette fenêtre..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 