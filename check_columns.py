#!/usr/bin/env python3
import sqlite3
import os

db_path = "backend/data/katula.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== STRUCTURE TABLE ===")
    cursor.execute("PRAGMA table_info(combinations)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"Colonne: {col[1]} (type: {col[2]})")
    
    print("\n=== EXEMPLE DONNÉES ===")
    cursor.execute("SELECT * FROM combinations LIMIT 1")
    sample = cursor.fetchone()
    if sample:
        print("Exemple ligne:", sample)
    
    conn.close()
else:
    print("Database not found!")