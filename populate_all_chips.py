#!/usr/bin/env python3
import sqlite3
import os

db_path = "backend/data/katula.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Générer des données pour tous les chips 1-48
    formes = ["carre", "triangle", "cercle", "rectangle"]
    granques = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"]
    petiques = ["q1", "q2", "q3", "q4"]
    tomes = ["tome1", "tome2", "tome3", "tome4"]
    alphas = ["a", "b", "c", "d"]
    
    print("Ajout des données pour chips 9-48...")
    
    for chip in range(9, 49):  # Chips 9 à 48
        for i, forme in enumerate(formes):
            denomination = f"D{chip}{forme[0].upper()}{i+1}"
            num1 = (chip * 2 + i) % 90 + 1
            num2 = (chip * 3 + i * 2) % 90 + 1
            alpha = alphas[i % 4]
            granque = granques[(chip + i) % 6]
            petique = petiques[i % 4]
            tome = tomes[i % 4]
            
            cursor.execute("""
                INSERT INTO combinations 
                (univers, forme, chip, denomination, num1, num2, alpha_ranking, granque_name, petique, tome)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ("mundo", forme, chip, denomination, num1, num2, alpha, granque, petique, tome))
    
    conn.commit()
    
    # Vérifier le résultat
    cursor.execute("SELECT COUNT(*) FROM combinations")
    total = cursor.fetchone()[0]
    print(f"Total entrées: {total}")
    
    cursor.execute("SELECT DISTINCT chip FROM combinations ORDER BY chip")
    chips = cursor.fetchall()
    print(f"Chips disponibles: {len(chips)} (1-{chips[-1][0]})")
    
    conn.close()
    print("Base de données mise à jour avec succès!")
else:
    print("Database not found!")