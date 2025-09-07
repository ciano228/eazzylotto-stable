"""
Script de déploiement production pour EazzyCalculator
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionDeployment:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.backend_dir = self.root_dir / 'backend'
        self.frontend_dir = self.root_dir / 'frontend'
        self.venv_dir = self.root_dir / 'venv'

    def check_environment(self):
        """Vérifie l'environnement de production"""
        logger.info("Vérification de l'environnement...")
        
        # Vérifier Python
        if sys.version_info < (3, 8):
            raise RuntimeError("Python 3.8 ou supérieur requis")
        
        # Vérifier les variables d'environnement
        required_vars = ['DATABASE_URL', 'SECRET_KEY', 'ENVIRONMENT']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise RuntimeError(f"Variables d'environnement manquantes: {missing_vars}")

    def setup_database(self):
        """Configure la base de données de production"""
        logger.info("Configuration de la base de données...")
        try:
            subprocess.run([
                sys.executable,
                str(self.backend_dir / 'init_db.py')
            ], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Erreur configuration base de données: {e}")
            raise

    def start_backend(self):
        """Démarre le serveur backend"""
        logger.info("Démarrage du backend...")
        try:
            cmd = [
                sys.executable, '-m', 'uvicorn',
                'main:app',
                '--host', '0.0.0.0',
                '--port', '8000',
                '--workers', '4',
                '--log-level', 'info'
            ]
            subprocess.Popen(cmd, cwd=str(self.backend_dir))
            logger.info("Backend démarré avec succès")
        except Exception as e:
            logger.error(f"Erreur démarrage backend: {e}")
            raise

    def start_frontend(self):
        """Démarre le serveur frontend"""
        logger.info("Démarrage du frontend...")
        try:
            cmd = [
                sys.executable, '-m', 'http.server',
                '--bind', '0.0.0.0',
                '8080'
            ]
            subprocess.Popen(cmd, cwd=str(self.frontend_dir))
            logger.info("Frontend démarré avec succès")
        except Exception as e:
            logger.error(f"Erreur démarrage frontend: {e}")
            raise

    def run(self):
        """Exécute le déploiement complet"""
        try:
            logger.info("Démarrage du déploiement production...")
            self.check_environment()
            self.setup_database()
            self.start_backend()
            self.start_frontend()
            logger.info("Déploiement terminé avec succès")
            logger.info("Application accessible sur:")
            logger.info("- Frontend: http://localhost:8080")
            logger.info("- Backend API: http://localhost:8000")
            logger.info("- Documentation API: http://localhost:8000/docs")
        except Exception as e:
            logger.error(f"Erreur lors du déploiement: {e}")
            sys.exit(1)

if __name__ == "__main__":
    deployment = ProductionDeployment()
    deployment.run()
