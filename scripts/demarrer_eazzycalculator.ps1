# Script de démarrage automatique pour EazzyCalculator
$ErrorActionPreference = "Stop"

function Write-Step {
    param($Message)
    Write-Host "`n=== $Message ===" -ForegroundColor Cyan
}

# Définir les chemins
$rootPath = $PSScriptRoot
$backendPath = Join-Path $rootPath "backend"
$dbPath = Join-Path $backendPath "database"
$venvPath = Join-Path $rootPath "venv"

# 1. Création de la structure des dossiers
Write-Step "Création de la structure des dossiers"
$folders = @(
    $backendPath,
    $dbPath,
    (Join-Path $backendPath "app"),
    (Join-Path $backendPath "app/routes"),
    (Join-Path $backendPath "app/models"),
    (Join-Path $backendPath "app/database")
)

foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "Dossier créé: $folder" -ForegroundColor Green
    }
}

# 2. Création/Activation de l'environnement virtuel
Write-Step "Configuration de l'environnement virtuel"
if (-not (Test-Path $venvPath)) {
    python -m venv $venvPath
    Write-Host "Environnement virtuel créé" -ForegroundColor Green
}

# Activation de l'environnement virtuel
& $venvPath\Scripts\Activate.ps1

# 3. Installation des dépendances
Write-Step "Installation des dépendances"
$requirements = @"
fastapi==0.68.1
uvicorn==0.15.0
sqlalchemy==1.4.23
databases[sqlite]==0.5.3
python-multipart==0.0.5
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
"@

$requirementsPath = Join-Path $rootPath "requirements.txt"
$requirements | Out-File $requirementsPath -Encoding utf8
pip install -r $requirementsPath

# 4. Configuration de la base de données
Write-Step "Configuration de la base de données"
$dbConfig = @"
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///eazzylotto.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"@

$dbConfigPath = Join-Path $backendPath "app/database/connection.py"
$dbConfig | Out-File $dbConfigPath -Encoding utf8

# 5. Création du fichier init_db.py
$initDb = @"
from app.database.connection import engine
from app.models.base import Base

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Initialisation de la base de données...")
    init_db()
    print("Base de données initialisée !")
"@

$initDbPath = Join-Path $backendPath "init_db.py"
$initDb | Out-File $initDbPath -Encoding utf8

# 6. Initialisation de la base de données
Write-Step "Initialisation de la base de données"
python $initDbPath

# 7. Démarrage du serveur
Write-Step "Démarrage du serveur"
Write-Host "Démarrage du serveur sur le port 8081..."
Set-Location $backendPath
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8081
