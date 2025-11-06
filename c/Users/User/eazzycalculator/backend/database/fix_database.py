#!/usr/bin/env python3
"""
Correction de la base de données - Ajout des colonnes manquantes
"""

import psycopg2
import os
from dotenv import load_dotenv

def fix_database():
    """Ajouter les colonnes manquantes"""
    
    load_dotenv()
    db_url = os.getenv('DATABASE_URL')
    
    # Extraire les paramètres de connexion
    db_url = db_url.replace('postgresql://', '')
    user_pass, host_db = db_url.split('@')
    user, password = user_pass.split(':')
    host_port, database = host_db.split('/')
    host, port = host_port.split(':') if ':' in host_port else (host_port, '5432')
    
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        cursor = conn.cursor()
        
        # Vérifier si la colonne is_no_draw existe
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'session_draws' AND column_name = 'is_no_draw'
        """)
        
        if not cursor.fetchone():
            print("Ajout de la colonne is_no_draw...")
            cursor.execute("""
                ALTER TABLE session_draws 
                ADD COLUMN is_no_draw BOOLEAN DEFAULT FALSE
            """)
            print("Colonne is_no_draw ajoutée")
        else:
            print("Colonne is_no_draw existe déjà")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Base de données corrigée!")
        return True
        
    except Exception as e:
        print(f"Erreur: {e}")
        return False

if __name__ == "__main__":
    fix_database()