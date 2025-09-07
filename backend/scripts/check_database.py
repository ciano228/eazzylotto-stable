#!/usr/bin/env python3
import sqlite3
import os

db_path = "backend/data/katula.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== CHIPS DISPONIBLES ===")
    cursor.execute("SELECT DISTINCT chip FROM combinations ORDER BY chip")
    chips = cursor.fetchall()
    print(f"Chips: {[chip[0] for chip in chips]}")
    print(f"Total chips: {len(chips)}")
    
    print("\n=== CHIP 48 DATA ===")
    cursor.execute("SELECT * FROM combinations WHERE chip = 48")
    chip48_data = cursor.fetchall()
    print(f"Chip 48 entries: {len(chip48_data)}")
    for row in chip48_data:
        print(row)
    
    conn.close()
else:
    print("Database not found!")