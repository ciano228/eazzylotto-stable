"""
Configuration du système Katula
"""
import os
from typing import Dict, Any

# Configuration de la base de données
DB_CONFIG: Dict[str, Any] = {
    'host': os.getenv('KATULA_DB_HOST', 'localhost'),
    'database': os.getenv('KATULA_DB_NAME', 'katooling_main_system'),
    'user': os.getenv('KATULA_DB_USER', 'postgres'),
    'password': os.getenv('KATULA_DB_PASSWORD', 'Katulaa_33'),
    'port': int(os.getenv('KATULA_DB_PORT', '5432'))
}

# Configuration des environnements
ENV = os.getenv('KATULA_ENV', 'development')

# Autres configurations potentielles
DEBUG = ENV == 'development'