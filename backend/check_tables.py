#!/usr/bin/env python3
"""
Script pour vérifier l'existence des tables parite et unidos
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import get_db
from sqlalchemy import text

def check_tables():
    """Vérifier l'existence des tables parite et unidos"""
    
    try:
        # Obtenir une session de base de données
        db = next(get_db())
        
        print("=== VÉRIFICATION DES TABLES ===")
        
        # Lister toutes les tables
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        
        tables = [row[0] for row in result]
        print(f"Tables disponibles: {tables}")
        
        # Vérifier spécifiquement parite et unidos
        parite_exists = 'parite' in tables
        unidos_exists = 'unidos' in tables
        
        print(f"\nTable 'parite' existe: {parite_exists}")
        print(f"Table 'unidos' existe: {unidos_exists}")
        
        if parite_exists:
            print("\n=== STRUCTURE TABLE PARITE ===")
            result = db.execute(text("SELECT * FROM parite LIMIT 5"))
            rows = result.fetchall()
            if rows:
                print("Colonnes:", result.keys())
                for row in rows:
                    print(f"  {dict(row)}")
            else:
                print("Table parite vide")
        
        if unidos_exists:
            print("\n=== STRUCTURE TABLE UNIDOS ===")
            result = db.execute(text("SELECT * FROM unidos LIMIT 5"))
            rows = result.fetchall()
            if rows:
                print("Colonnes:", result.keys())
                for row in rows:
                    print(f"  {dict(row)}")
            else:
                print("Table unidos vide")
        
        # Vérifier les valeurs dans combinations
        print("\n=== ÉCHANTILLON PARITE_ID ET UNIDOS_ID ===")
        result = db.execute(text("""
            SELECT combination, parite_id, unidos_id 
            FROM combinations 
            WHERE parite_id IS NOT NULL AND unidos_id IS NOT NULL
            LIMIT 10
        """))
        
        for row in result:
            print(f"  {row[0]}: parite_id={row[1]}, unidos_id={row[2]}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    check_tables()