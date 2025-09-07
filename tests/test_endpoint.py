#!/usr/bin/env python3
import sqlite3
import os

# Test direct de la requête BD
db_path = "backend/data/katula.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== TEST GRANQUE ===")
    cursor.execute(
        "SELECT DISTINCT granque_name, denomination, chip FROM combinations WHERE univers = ? AND granque_name IS NOT NULL",
        ("mundo",)
    )
    granque_results = cursor.fetchall()
    print(f"Granque results: {len(granque_results)} entrées")
    for i, row in enumerate(granque_results[:5]):
        print(f"  {i+1}: {row}")
    
    print("\n=== TEST TOME ===")
    cursor.execute(
        "SELECT DISTINCT tome, denomination, chip FROM combinations WHERE univers = ? AND tome IS NOT NULL",
        ("mundo",)
    )
    tome_results = cursor.fetchall()
    print(f"Tome results: {len(tome_results)} entrées")
    for i, row in enumerate(tome_results[:5]):
        print(f"  {i+1}: {row}")
    
    print("\n=== TEST PETIQUE ===")
    cursor.execute(
        "SELECT DISTINCT petique, denomination, chip FROM combinations WHERE univers = ? AND petique IS NOT NULL",
        ("mundo",)
    )
    petique_results = cursor.fetchall()
    print(f"Petique results: {len(petique_results)} entrées")
    for i, row in enumerate(petique_results[:5]):
        print(f"  {i+1}: {row}")
    
    conn.close()
else:
    print("Database not found!")