#!/usr/bin/env python3
"""
Test de connexion à la vraie BD existante
"""
import sqlite3
import os

def test_real_database():
    """Tester la connexion à la vraie BD"""
    
    # Chemins possibles pour la BD
    possible_paths = [
        "katooling_main_system.db",
        "backend/data/katula.db", 
        "katula.db",
        "main.db",
        "database.db"
    ]
    
    print("=== TEST CONNEXION BD RÉELLE ===\n")
    
    for db_path in possible_paths:
        if os.path.exists(db_path):
            print(f"[TROUVÉ] {db_path}")
            
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Lister les tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                print(f"  Tables: {[t[0] for t in tables]}")
                
                # Chercher une table avec des combinaisons
                for table_name in [t[0] for t in tables]:
                    if 'combination' in table_name.lower() or 'katula' in table_name.lower():
                        print(f"  [TABLE CANDIDATE] {table_name}")
                        
                        # Voir la structure
                        cursor.execute(f"PRAGMA table_info({table_name})")
                        columns = cursor.fetchall()
                        print(f"    Colonnes: {[c[1] for c in columns]}")
                        
                        # Voir quelques données
                        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                        rows = cursor.fetchall()
                        if rows:
                            print(f"    Exemple: {rows[0]}")
                
                conn.close()
                print()
                
            except Exception as e:
                print(f"  [ERREUR] {e}")
                print()
        else:
            print(f"[ABSENT] {db_path}")
    
    print("\n=== RECOMMANDATION ===")
    print("1. Identifier la vraie BD avec les données Katula")
    print("2. Vérifier les noms exacts des colonnes (case sensitive)")
    print("3. Adapter les requêtes SQL en conséquence")

if __name__ == "__main__":
    test_real_database()