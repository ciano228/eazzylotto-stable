#!/usr/bin/env python3
"""
Test direct de l'endpoint backend
"""
import sqlite3
import os

def test_endpoint_logic():
    """Tester la logique de l'endpoint directement"""
    
    print("=== TEST ENDPOINT LOGIC ===\n")
    
    db_path = "backend/data/katula.db"
    universe = "mundo"
    chip_number = 1
    
    if not os.path.exists(db_path):
        print(f"[ERREUR] BD non trouvée: {db_path}")
        return
    
    print(f"[TEST] Univers: {universe}, Chip: {chip_number}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Formes pour mundo
    formes = ["carre", "triangle", "cercle", "rectangle"]
    
    formes_data = {}
    
    for forme in formes:
        print(f"\n[FORME] {forme}")
        
        # Requête exacte comme dans le backend
        cursor.execute(
            "SELECT DISTINCT denomination FROM combinations WHERE univers = ? AND forme = ? AND chip = ?",
            (universe.lower(), forme.lower(), chip_number)
        )
        query_result = cursor.fetchall()
        
        print(f"  Requête: univers='{universe.lower()}', forme='{forme.lower()}', chip={chip_number}")
        print(f"  Résultat: {query_result}")
        
        items = []
        for row in query_result:
            items.append({
                "denomination": row[0],
                "object_name": row[0],
                "forme": forme,
                "chip": chip_number,
                "universe": universe
            })
        
        formes_data[forme] = items
        print(f"  Items: {len(items)}")
    
    conn.close()
    
    print(f"\n[RÉSULTAT FINAL]")
    for forme, items in formes_data.items():
        if items:
            print(f"  {forme}: {[item['denomination'] for item in items]}")
        else:
            print(f"  {forme}: VIDE")
    
    # Vérifier les données brutes dans la BD
    print(f"\n[DONNÉES BRUTES BD]")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT univers, forme, chip, denomination FROM combinations LIMIT 10")
    rows = cursor.fetchall()
    for row in rows:
        print(f"  {row}")
    conn.close()

if __name__ == "__main__":
    test_endpoint_logic()