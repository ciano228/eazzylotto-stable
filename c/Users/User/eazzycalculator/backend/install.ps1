# Créer l'environnement virtuel s'il n'existe pas
if (-not (Test-Path "venv")) {
    Write-Host "Création de l'environnement virtuel..."
    python -m venv venv
}

# Activer l'environnement virtuel
Write-Host "Activation de l'environnement virtuel..."
.\venv\Scripts\Activate.ps1

# Installer les dépendances
Write-Host "Installation des dépendances..."
pip install -r requirements.txt

Write-Host "Installation terminée. Vous pouvez maintenant lancer le serveur avec:"
Write-Host "uvicorn main:app --reload --port 8000"
