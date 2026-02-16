#!/usr/bin/env python3
"""
Analyser la structure des tomes dans la BD
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import psycopg2
from dotenv import load_dotenv

def analyze_tome_structure():
    """Analyser la structure actuelle des tomes"""
    
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
        
        print("=== ANALYSE STRUCTURE TOMES ===")
        
        # 1. Vérifier la structure de la table combinations
        print("\n1. STRUCTURE TABLE COMBINATIONS:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'combinations' 
            AND column_name LIKE '%tome%'
            ORDER BY ordinal_position
        """)
        
        tome_columns = cursor.fetchall()
        for col_name, data_type, nullable in tome_columns:
            print(f"  - {col_name}: {data_type} (nullable: {nullable})")
        
        # 2. Vérifier l'existence de la table tomes
        print("\n2. TABLE TOMES:")
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'tomes'
            )
        """)
        
        tomes_table_exists = cursor.fetchone()[0]
        print(f"  Table 'tomes' existe: {tomes_table_exists}")
        
        if tomes_table_exists:
            # Structure de la table tomes
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'tomes'
                ORDER BY ordinal_position
            """)
            
            tomes_structure = cursor.fetchall()
            print("  Structure table tomes:")
            for col_name, data_type, nullable in tomes_structure:
                print(f"    - {col_name}: {data_type} (nullable: {nullable})")
            
            # Contenu de la table tomes
            cursor.execute("SELECT * FROM tomes ORDER BY tome_name")
            tomes_content = cursor.fetchall()
            print(f"  Contenu table tomes ({len(tomes_content)} entrées):")
            for row in tomes_content[:10]:  # Limiter à 10
                print(f"    {row}")
        
        # 3. Vérifier les contraintes
        print("\n3. CONTRAINTES:")
        cursor.execute("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints 
            WHERE table_name = 'combinations' 
            AND constraint_name LIKE '%tome%'
        """)
        
        constraints = cursor.fetchall()
        for constraint_name, constraint_type in constraints:
            print(f"  - {constraint_name}: {constraint_type}")
        
        # 4. Échantillon de données actuelles
        print("\n4. ECHANTILLON DONNEES ACTUELLES:")
        cursor.execute("""
            SELECT DISTINCT tome, COUNT(*) as count
            FROM combinations 
            WHERE tome IS NOT NULL
            GROUP BY tome
            ORDER BY tome
            LIMIT 10
        """)
        
        current_tomes = cursor.fetchall()
        print("  Valeurs tome actuelles:")
        for tome, count in current_tomes:
            print(f"    {tome}: {count} occurrences")
        
        cursor.close()
        conn.close()
        
        # 5. Recommandations
        print("\n5. RECOMMANDATIONS:")
        print("  PROBLEME IDENTIFIE:")
        print("    - Colonne 'tome' dans combinations (devrait être 'tome_id' ou référencer tomes.id)")
        print("    - Table 'tomes' existe mais pas de relation correcte")
        
        print("\n  SOLUTIONS POSSIBLES:")
        print("    A. Renommer colonne 'tome' -> 'tome_name' (garder les valeurs texte)")
        print("    B. Créer colonne 'tome_id' et faire référence à tomes.id")
        print("    C. Supprimer contrainte FK et garder tome comme texte libre")
        
        return tome_columns, tomes_table_exists, constraints, current_tomes
        
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None, None

def propose_solution():
    """Proposer une solution pour corriger la structure"""
    
    print("\n=== SOLUTION RECOMMANDEE ===")
    print("OPTION A: Garder tome comme texte libre (SIMPLE)")
    print("  1. Supprimer la contrainte FK tome -> tomes")
    print("  2. Garder la colonne 'tome' comme TEXT")
    print("  3. Permettre les valeurs calculées (tome1, tome2, etc.)")
    
    print("\nOPTION B: Relation correcte avec table tomes (PROPRE)")
    print("  1. Ajouter colonne tome_id INTEGER")
    print("  2. Créer FK tome_id -> tomes.id") 
    print("  3. Migrer les données existantes")
    print("  4. Supprimer ancienne colonne tome")
    
    print("\nQUELLE OPTION PREFEREZ-VOUS ?")

if __name__ == "__main__":
    analyze_tome_structure()
    propose_solution()