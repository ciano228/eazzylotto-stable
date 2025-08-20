#!/usr/bin/env python3
"""
Initialisation de la base de données Katula
"""
import sqlite3
import os
import sys

def init_katula_database():
    """Initialise la BD avec les données Katula"""
    
    # Créer le dossier backend/data s'il n'existe pas
    data_dir = "backend/data"
    os.makedirs(data_dir, exist_ok=True)
    
    # Chemin vers la BD
    db_path = os.path.join(data_dir, "katula.db")
    
    print(f"[INIT] Création de la BD: {db_path}")
    
    # Connexion à la BD
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Vérifier si le fichier SQL existe
        sql_file = "create_katula_table.sql"
        if not os.path.exists(sql_file):
            print(f"[ERREUR] Fichier {sql_file} non trouvé")
            # Créer une table basique si le fichier n'existe pas
            create_basic_table(cursor)
        else:
            # Lire et exécuter le script SQL
            with open(sql_file, "r", encoding="utf-8") as f:
                sql_script = f.read()
            
            # Exécuter le script
            cursor.executescript(sql_script)
        
        conn.commit()
        
        # Vérifier les données
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"[OK] Tables créées: {[table[0] for table in tables]}")
        
        # Vérifier les données si la table combinations existe
        try:
            cursor.execute("SELECT COUNT(*) FROM combinations WHERE univers = 'mundo'")
            count = cursor.fetchone()[0]
            print(f"[OK] BD créée avec {count} entrées pour l'univers Mundo")
            
            # Afficher quelques exemples
            cursor.execute("SELECT chip, forme, denomination FROM combinations WHERE univers = 'mundo' LIMIT 5")
            examples = cursor.fetchall()
            
            print("[EXEMPLES]")
            for chip, forme, denom in examples:
                print(f"  Chip {chip} - {forme}: {denom}")
        except sqlite3.OperationalError:
            print("[INFO] Table combinations non trouvée, création d'une structure basique")
            create_basic_table(cursor)
            conn.commit()
        
        return True
        
    except Exception as e:
        print(f"[ERREUR] {e}")
        return False
        
    finally:
        conn.close()

def create_basic_table(cursor):
    """Crée une table basique si le fichier SQL n'existe pas"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS combinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chip TEXT NOT NULL,
            forme TEXT NOT NULL,
            denomination TEXT NOT NULL,
            univers TEXT NOT NULL DEFAULT 'mundo',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insérer quelques données de test
    test_data = [
        ('001', 'circle', 'Alpha', 'mundo'),
        ('002', 'square', 'Beta', 'mundo'),
        ('003', 'triangle', 'Gamma', 'mundo'),
        ('004', 'diamond', 'Delta', 'mundo'),
        ('005', 'star', 'Epsilon', 'mundo')
    ]
    
    cursor.executemany(
        "INSERT INTO combinations (chip, forme, denomination, univers) VALUES (?, ?, ?, ?)",
        test_data
    )
    print("[INFO] Données de test insérées")

if __name__ == "__main__":
    print("=== INITIALISATION BD KATULA ===")
    
    if init_katula_database():
        print("\n[SUCCESS] BD Katula initialisée")
        print("Les données réelles seront maintenant affichées dans katula-dynamic.html")
        print("\nPour tester:")
        print("1. python start_backend.py")
        print("2. python start_frontend.py")
        print("3. Ouvrir http://localhost:8081/katula-dynamic.html")
    else:
        print("\n[FAILED] Erreur lors de l'initialisation")
        sys.exit(1)