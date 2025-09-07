# Activer l'environnement virtuel Python
$env:PYTHONPATH = "."
if (Test-Path "venv\Scripts\Activate.ps1") {
    . .\venv\Scripts\Activate.ps1
} else {
    Write-Host "❌ Environnement virtuel non trouvé!" -ForegroundColor Red
    exit 1
}

# Démarrer l'application
Write-Host "🚀 Démarrage d'EazzyCalculator..." -ForegroundColor Cyan
python scripts/start_app.py
