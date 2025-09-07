import sqlite3

def check_fruity_formes():
    try:
        conn = sqlite3.connect('eazzylotto.db')
        cursor = conn.cursor()
        
        # Vérifier les formes distinctes pour fruity
        cursor.execute("""
            SELECT DISTINCT forme
            FROM combinations 
            WHERE univers = 'fruity'
            ORDER BY forme
        """)
        formes = cursor.fetchall()
        
        print("\nFormes distinctes pour l'univers 'fruity':")
        for forme in formes:
            # Compter les occurrences de chaque forme
            cursor.execute("""
                SELECT COUNT(*) 
                FROM combinations 
                WHERE univers = 'fruity' AND forme = ?
            """, (forme[0],))
            count = cursor.fetchone()[0]
            print(f"- {forme[0]}: {count} occurrences")
            
            # Afficher quelques exemples pour chaque forme
            cursor.execute("""
                SELECT chip, denomination 
                FROM combinations 
                WHERE univers = 'fruity' AND forme = ? 
                LIMIT 3
            """, (forme[0],))
            examples = cursor.fetchall()
            print("  Exemples:")
            for chip, denom in examples:
                print(f"    Chip {chip}: {denom}")
            print()
            
    except Exception as e:
        print(f"Erreur: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_fruity_formes()
