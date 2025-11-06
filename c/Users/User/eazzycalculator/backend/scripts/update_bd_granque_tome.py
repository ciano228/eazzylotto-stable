#!/usr/bin/env python3
"""
Ajouter les colonnes granque_name et tome à la BD existante
"""
import sqlite3
import os

def update_database():
    db_path = "backend/data/katula.db"
    
    if not os.path.exists(db_path):
        print(f"[ERREUR] BD non trouvée: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Ajouter les colonnes
        cursor.execute("ALTER TABLE combinations ADD COLUMN granque_name TEXT")
        cursor.execute("ALTER TABLE combinations ADD COLUMN tome TEXT")
        
        # Mettre à jour avec des données d'exemple
        updates = [
            ("Q1", "tome1", 1), ("Q1", "tome1", 2), ("Q2", "tome2", 3),
            ("Q1", "tome1", 4), ("Q2", "tome2", 5), ("Q3", "tome3", 6),
            ("Q4", "tome4", 7), ("Q1", "tome1", 8)
        ]
        
        for granque, tome, chip in updates:
            cursor.execute(
                "UPDATE combinations SET granque_name = ?, tome = ? WHERE chip = ?",
                (granque, tome, chip)
            )
        
        conn.commit()
        print("[OK] Colonnes ajoutées et données mises à jour")
        
        # Vérifier
        cursor.execute("SELECT chip, granque_name, tome FROM combinations WHERE granque_name IS NOT NULL LIMIT 5")
        results = cursor.fetchall()
        for row in results:
            print(f"  Chip {row[0]}: {row[1]}, {row[2]}")
            
    except Exception as e:
        print(f"[ERREUR] {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_database()