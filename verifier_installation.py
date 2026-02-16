"""
Script de vérification de l'installation EazzyCalculator
Vérifie que tous les composants sont correctement installés
"""
import sys
import os
from pathlib import Path

def check_python_version():
    """Vérifie la version de Python"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print("✅ Python version OK:", f"{version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print("❌ Python version insuffisante:", f"{version.major}.{version.minor}.{version.micro}")
        print("   Version requise: 3.9+")
        return False

def check_dependencies():
    """Vérifie les dépendances Python"""
    required = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'psycopg2',
        'pydantic',
        'python-jose',
        'passlib',
        'python-dotenv'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MANQUANT")
            missing.append(package)
    
    return len(missing) == 0, missing

def check_files():
    """Vérifie la présence des fichiers essentiels"""
    base_dir = Path(__file__).parent
    
    essential_files = [
        "backend/main.py",
        "backend/requirements.txt",
        "backend/.env",
        "backend/app/__init__.py",
        "backend/app/core/config.py",
        "backend/app/core/auth.py",
        "backend/app/database/connection.py",
        "backend/app/models/user.py",
        "backend/app/schemas/models.py",
        "backend/app/services/journal_service_v2.py",
        "backend/app/services/katula_matrix_service.py",
        "backend/app/utils/calculator.py",
        "integrated_server.py",
        "start_backend.py"
    ]
    
    missing = []
    for file_path in essential_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MANQUANT")
            missing.append(file_path)
    
    return len(missing) == 0, missing

def check_database():
    """Vérifie la connexion à la base de données"""
    try:
        import psycopg2
        from dotenv import load_dotenv
        
        # Charger les variables d'environnement
        env_path = Path(__file__).parent / "backend" / ".env"
        load_dotenv(env_path)
        
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME', 'katooling_main_system'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'Katulaa_33'),
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432')
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        print("✅ Connexion PostgreSQL OK")
        print(f"   Version: {version[0].split(',')[0]}")
        return True
        
    except Exception as e:
        print("❌ Connexion PostgreSQL ÉCHEC")
        print(f"   Erreur: {str(e)}")
        return False

def check_env_variables():
    """Vérifie les variables d'environnement"""
    from dotenv import load_dotenv
    
    env_path = Path(__file__).parent / "backend" / ".env"
    load_dotenv(env_path)
    
    required_vars = [
        'DATABASE_URL',
        'DB_NAME',
        'DB_USER',
        'DB_PASSWORD',
        'SECRET_KEY'
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Masquer les mots de passe
            if 'PASSWORD' in var or 'SECRET' in var:
                display_value = '*' * 8
            else:
                display_value = value[:30] + '...' if len(value) > 30 else value
            print(f"✅ {var} = {display_value}")
        else:
            print(f"❌ {var} - NON DÉFINI")
            missing.append(var)
    
    return len(missing) == 0, missing

def main():
    """Fonction principale de vérification"""
    print("=" * 70)
    print("🔍 VÉRIFICATION DE L'INSTALLATION EAZZYCALCULATOR")
    print("=" * 70)
    print()
    
    all_ok = True
    
    # 1. Version Python
    print("📌 1. Version Python")
    print("-" * 70)
    if not check_python_version():
        all_ok = False
    print()
    
    # 2. Dépendances
    print("📌 2. Dépendances Python")
    print("-" * 70)
    deps_ok, missing_deps = check_dependencies()
    if not deps_ok:
        all_ok = False
        print()
        print("⚠️  Pour installer les dépendances manquantes:")
        print("   cd backend")
        print("   pip install -r requirements.txt")
    print()
    
    # 3. Fichiers essentiels
    print("📌 3. Fichiers essentiels")
    print("-" * 70)
    files_ok, missing_files = check_files()
    if not files_ok:
        all_ok = False
    print()
    
    # 4. Variables d'environnement
    print("📌 4. Variables d'environnement")
    print("-" * 70)
    env_ok, missing_env = check_env_variables()
    if not env_ok:
        all_ok = False
    print()
    
    # 5. Base de données
    print("📌 5. Connexion base de données")
    print("-" * 70)
    if not check_database():
        all_ok = False
    print()
    
    # Résumé
    print("=" * 70)
    if all_ok:
        print("✅ INSTALLATION COMPLÈTE ET FONCTIONNELLE")
        print()
        print("🚀 Pour démarrer le serveur:")
        print("   python start_backend.py")
        print()
        print("   ou")
        print()
        print("   python integrated_server.py")
    else:
        print("❌ INSTALLATION INCOMPLÈTE")
        print()
        print("⚠️  Veuillez corriger les problèmes ci-dessus avant de démarrer.")
    print("=" * 70)
    
    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
