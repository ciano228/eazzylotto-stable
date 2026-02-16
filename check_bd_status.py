#!/usr/bin/env python3
"""
Vérifier le statut définitif des mises à jour dans la BD
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import psycopg2
from dotenv import load_dotenv

def check_bd_status():
    """Vérifier l'état actuel de la BD"""
    
    load_dotenv()
    
    db_config = {
        'host': os.getenv('KATULA_DB_HOST', 'localhost'),
        'database': os.getenv('KATULA_DB_NAME', 'katooling_main_system'),
        'user': os.getenv('KATULA_DB_USER', 'postgres'),
        'password': os.getenv('KATULA_DB_PASSWORD', 'Katulaa_33'),
        'port': int(os.getenv('KATULA_DB_PORT', '5432'))
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        print("=== STATUT DEFINITIF BD ===")
        
        # 1. Vérifier la contrainte tome
        cursor.execute("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'combinations' 
            AND constraint_type = 'FOREIGN KEY'
            AND constraint_name LIKE '%tome%'
        """)
        
        fk_constraints = cursor.fetchall()
        print(f"Contraintes FK tome: {len(fk_constraints)} (devrait être 0)")
        
        # 2. Compter les tomes mis à jour
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT tome) as nb_tomes,
                COUNT(DISTINCT chip) as nb_chips_avec_tome,
                COUNT(*) as nb_total_records
            FROM combinations 
            WHERE tome IS NOT NULL
        """)
        
        stats = cursor.fetchone()
        nb_tomes, nb_chips, nb_records = stats
        
        print(f"Tomes distincts: {nb_tomes}")
        print(f"Chips avec tome: {nb_chips}")
        print(f"Records avec tome: {nb_records}")
        
        # 3. Distribution des tomes
        cursor.execute("""
            SELECT tome, COUNT(DISTINCT chip) as nb_chips
            FROM combinations 
            WHERE tome IS NOT NULL
            GROUP BY tome
            ORDER BY 
                CAST(SUBSTRING(tome FROM 'tome([0-9]+)') AS INTEGER)
        """)
        
        tome_distribution = cursor.fetchall()
        print(f"\nDistribution des tomes:")
        for tome, nb_chips in tome_distribution:
            print(f"  {tome}: {nb_chips} chips")
        
        # 4. Vérifier les tomes élevés
        cursor.execute("""
            SELECT univers, chip, tome
            FROM (
                SELECT DISTINCT univers, chip, tome
                FROM combinations 
                WHERE tome IN ('tome11', 'tome12', 'tome14')
            ) t
            ORDER BY tome, univers, chip
        """)
        
        high_tomes = cursor.fetchall()
        print(f"\nTomes élevés (11,12,14):")
        for univers, chip, tome in high_tomes:
            print(f"  {tome}: {univers} {chip}")
        
        # 5. Vérifier la persistance (transaction commitée)
        cursor.execute("""
            SELECT pg_is_in_recovery(), 
                   current_timestamp,
                   (SELECT COUNT(*) FROM combinations WHERE tome = 'tome14') as tome14_count
        """)
        
        recovery, timestamp, tome14_count = cursor.fetchone()
        print(f"\nPersistance BD:")
        print(f"  En recovery: {recovery}")
        print(f"  Timestamp: {timestamp}")
        print(f"  Tome14 count: {tome14_count}")
        
        cursor.close()
        conn.close()
        
        # 6. Résumé du statut
        print(f"\n=== RESUME STATUT ===")
        if len(fk_constraints) == 0:
            print("OK Contrainte FK tome supprimée définitivement")
        else:
            print("ATTENTION Contrainte FK encore présente")
            
        if nb_tomes >= 10:
            print("OK Tomes calculés et persistés")
        else:
            print("ATTENTION Peu de tomes trouvés")
            
        if tome14_count > 0:
            print("OK Tomes élevés (tome14) présents")
        else:
            print("INFO Pas de tome14 trouvé")
        
        return True
        
    except Exception as e:
        print(f"Erreur: {e}")
        return False

if __name__ == "__main__":
    check_bd_status()