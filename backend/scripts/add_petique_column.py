#!/usr/bin/env python3
"""
Ajouter la colonne petique à la BD
"""
import sqlite3
import os

def add_petique_column():
    db_path = "backend/data/katula.db"
    
    if not os.path.exists(db_path):
        print(f"[ERREUR] BD non trouvée: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Ajouter la colonne petique
        cursor.execute("ALTER TABLE combinations ADD COLUMN petique TEXT")
        
        # Mettre à jour avec des données d'exemple basées sur les chips
        # q1: chips 1-12, q2: chips 13-24, q3: chips 25-36, q4: chips 37-48
        updates = [
            ("q1", 1), ("q1", 2), ("q2", 3), ("q1", 4), ("q2", 5), 
            ("q3", 6), ("q4", 7), ("q1", 8)
        ]
        
        for petique, chip in updates:
            cursor.execute(
                "UPDATE combinations SET petique = ? WHERE chip = ?",
                (petique, chip)
            )
        
        conn.commit()
        print("[OK] Colonne petique ajoutée")
        
        # Vérifier
        cursor.execute("SELECT chip, granque_name, petique, tome FROM combinations WHERE petique IS NOT NULL LIMIT 5")
        results = cursor.fetchall()
        for row in results:
            print(f"  Chip {row[0]}: Granque={row[1]}, Petique={row[2]}, Tome={row[3]}")
            
    except Exception as e:
        print(f"[ERREUR] {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_petique_column()