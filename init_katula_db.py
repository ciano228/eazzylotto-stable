#!/usr/bin/env python3
"""
Initialisation de la base de données Katula
"""
import sqlite3
import os

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
        # Lire et exécuter le script SQL
        with open("create_katula_table.sql", "r", encoding="utf-8") as f:
            sql_script = f.read()
        
        # Exécuter le script
        cursor.executescript(sql_script)
        conn.commit()
        
        # Vérifier les données
        cursor.execute("SELECT COUNT(*) FROM combinations WHERE univers = 'mundo'")
        count = cursor.fetchone()[0]
        
        print(f"[OK] BD créée avec {count} entrées pour l'univers Mundo")
        
        # Afficher quelques exemples
        cursor.execute("SELECT chip, forme, denomination FROM combinations WHERE univers = 'mundo' LIMIT 5")
        examples = cursor.fetchall()
        
        print("[EXEMPLES]")
        for chip, forme, denom in examples:
            print(f"  Chip {chip} - {forme}: {denom}")
        
        return True
        
    except Exception as e:
        print(f"[ERREUR] {e}")
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== INITIALISATION BD KATULA ===")
    
    if init_katula_database():
        print("\n[SUCCESS] BD Katula initialisée")
        print("Les données réelles seront maintenant affichées dans katula-dynamic.html")
    else:
        print("\n[FAILED] Erreur lors de l'initialisation")