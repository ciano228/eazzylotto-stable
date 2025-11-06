"""
Script pour ajouter les icônes manquantes pour l'univers fruity
"""
import sqlite3
from typing import List, Dict

# Configuration des formes pour fruity
FRUITY_FORMES = {
    'carre': ['🍎', '🍐', '🍊', '🍋'],      # Fruits durs
    'triangle': ['🍇', '🍒', '🫐', '🍓'],    # Petits fruits
    'cercle': ['🍊', '🍎', '🍐', '🍋'],      # Fruits ronds
    'rectangle': ['🍌', '🥝', '🥑', '🥭']    # Fruits longs/ovales
}

def add_fruity_combinations():
    try:
        # Connexion à la base de données
        conn = sqlite3.connect('eazzylotto.db')
        cursor = conn.cursor()
        
        # Créer la table si elle n'existe pas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS combinations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chip INTEGER NOT NULL,
                forme TEXT NOT NULL,
                denomination TEXT NOT NULL,
                univers TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Supprimer les anciennes données fruity si elles existent
        cursor.execute("DELETE FROM combinations WHERE univers = 'fruity'")
        
        # Ajouter les nouvelles combinaisons
        for chip in range(1, 49):  # 48 chips
            for forme, denominations in FRUITY_FORMES.items():
                for denom in denominations:
                    cursor.execute("""
                        INSERT INTO combinations 
                        (chip, forme, denomination, univers)
                        VALUES (?, ?, ?, 'fruity')
                    """, (chip, forme, denom))
        
        conn.commit()
        print("[OK] Données fruity ajoutées avec succès")
        
        # Vérification
        cursor.execute("SELECT COUNT(*) FROM combinations WHERE univers = 'fruity'")
        count = cursor.fetchone()[0]
        print(f"[INFO] {count} combinaisons ajoutées pour l'univers fruity")
        
        # Afficher quelques exemples
        cursor.execute("""
            SELECT DISTINCT forme, GROUP_CONCAT(denomination) as denoms
            FROM combinations 
            WHERE univers = 'fruity'
            GROUP BY forme
            LIMIT 5
        """)
        examples = cursor.fetchall()
        print("\n[EXEMPLES]")
        for forme, denoms in examples:
            print(f"  {forme}: {denoms}")
            
    except Exception as e:
        print(f"[ERREUR] {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_fruity_combinations()
