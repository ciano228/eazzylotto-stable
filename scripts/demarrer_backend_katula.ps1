# Activation de l'environnement virtuel
if (Test-Path venv) {
    .\venv\Scripts\Activate.ps1
} else {
    python -m venv venv
    .\venv\Scripts\Activate.ps1
}

# Installation des dépendances
pip install -r requirements.txt

# Démarrage du backend avec les nouveaux services Katula
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8081
