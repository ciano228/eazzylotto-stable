"""
Script de préparation de la Version 1 d'EazzyLotto
"""
import os
import shutil
from pathlib import Path

# Pages principales à inclure
MAIN_PAGES = [
    'index.html',  # Page d'accueil
    'dashboard.html',  # Tableau de bord principal
    'katula-dynamic.html',  # Table de Katula dynamique
    'katula-multi-universe.html',  # Multi-univers
    'pattern-viewer.html',  # Visualiseur de patterns
    'advanced-journal.html',  # Journal avancé
    'results-history.html',  # Historique des résultats
    'prediction-panel.html',  # Panneau de prédiction
    'login.html',  # Page de connexion
    'signup.html',  # Page d'inscription
]

# Dossiers à copier intégralement
FOLDERS_TO_COPY = [
    'assets',
    'static',
    'templates'
]

def create_structure():
    """Crée la structure de base pour la version 1"""
    root = Path('eazzylotto-v1')
    
    # Créer les dossiers principaux
    for dir_name in ['frontend', 'backend', 'data']:
        (root / dir_name).mkdir(parents=True, exist_ok=True)

def copy_frontend_files():
    """Copie les fichiers frontend nécessaires"""
    source = Path('frontend')
    dest = Path('eazzylotto-v1/frontend')
    
    # Copier les pages principales
    for page in MAIN_PAGES:
        if (source / page).exists():
            shutil.copy2(source / page, dest / page)
            print(f"✓ Copié {page}")
    
    # Copier les dossiers de ressources
    for folder in FOLDERS_TO_COPY:
        if (source / folder).exists():
            shutil.copytree(
                source / folder,
                dest / folder,
                dirs_exist_ok=True
            )
            print(f"✓ Copié dossier {folder}")

def copy_backend_files():
    """Copie les fichiers backend nécessaires"""
    source = Path('backend')
    dest = Path('eazzylotto-v1/backend')
    
    # Fichiers backend essentiels
    backend_files = [
        'main.py',
        'init_db.py',
        'requirements.txt',
        '.env.example'
    ]
    
    # Copier les fichiers backend
    for file in backend_files:
        if (source / file).exists():
            shutil.copy2(source / file, dest / file)
            print(f"✓ Copié {file}")
    
    # Copier le dossier app avec sa structure
    if (source / 'app').exists():
        shutil.copytree(
            source / 'app',
            dest / 'app',
            dirs_exist_ok=True
        )
        print("✓ Copié dossier app")

def create_example_env():
    """Crée un fichier .env.example avec les configurations nécessaires"""
    env_content = """# Configuration EazzyLotto Version 1
DATABASE_URL=sqlite:///./data/eazzylotto.db
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
DEBUG=True
"""
    
    with open('eazzylotto-v1/.env.example', 'w') as f:
        f.write(env_content)
    print("✓ Créé .env.example")

def main():
    """Fonction principale"""
    try:
        print("🚀 Préparation de EazzyLotto Version 1...")
        
        # Créer la structure
        create_structure()
        
        # Copier les fichiers
        copy_frontend_files()
        copy_backend_files()
        
        # Créer le fichier .env exemple
        create_example_env()
        
        print("\n✨ Version 1 préparée avec succès!")
        print("\nPour démarrer l'application:")
        print("1. cd eazzylotto-v1")
        print("2. cp .env.example .env  (et configurez les variables)")
        print("3. ./start.bat (Windows) ou ./start.ps1 (PowerShell)")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        raise

if __name__ == "__main__":
    main()
