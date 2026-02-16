# Script PowerShell de démarrage EazzyCalculator
# Encodage UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Clear-Host

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "🚀 EAZZYCALCULATOR - DÉMARRAGE RAPIDE" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Vérification de l'installation..." -ForegroundColor Yellow
Write-Host ""

# Exécuter le script de vérification
python verifier_installation.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Problèmes détectés. Veuillez les corriger avant de continuer." -ForegroundColor Red
    Write-Host ""
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "✅ Installation validée!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Démarrage du serveur..." -ForegroundColor Yellow
Write-Host ""
Write-Host "📍 URLs d'accès:" -ForegroundColor Cyan
Write-Host "   - API: http://localhost:8000" -ForegroundColor White
Write-Host "   - Documentation: http://localhost:8000/api/docs" -ForegroundColor White
Write-Host "   - Frontend: http://localhost:8000/" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Appuyez sur Ctrl+C pour arrêter le serveur" -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Démarrer le serveur
python start_backend.py

Read-Host "Appuyez sur Entrée pour quitter"
