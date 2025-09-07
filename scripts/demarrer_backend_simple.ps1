# Script PowerShell pour démarrer le backend
Write-Host "=== DEMARRAGE DU BACKEND EAZZYLOTTO ===" -ForegroundColor Cyan
Write-Host

# Activer l'environnement virtuel
try {
    & .\venv\Scripts\Activate.ps1
    Write-Host "[OK] Environnement virtuel activé" -ForegroundColor Green
} catch {
    Write-Host "[ERREUR] Impossible d'activer l'environnement virtuel: $_" -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

Write-Host

# Démarrer le serveur FastAPI
Write-Host "[INFO] Démarrage du serveur FastAPI..." -ForegroundColor Yellow
python backend\main.py

Read-Host "Appuyez sur Entrée pour quitter"
