#!/usr/bin/env python3
"""
Script pour examiner la structure de la base de données
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import get_db
from app.models.combination import Combination
from sqlalchemy import inspect

def debug_db_structure():
    """Examiner la structure de la base de données"""
    
    try:
        # Obtenir une session de base de données
        db = next(get_db())
        
        print("=== STRUCTURE DE LA TABLE COMBINATIONS ===")
        
        # Utiliser l'inspecteur SQLAlchemy pour voir toutes les colonnes
        inspector = inspect(db.bind)
        columns = inspector.get_columns('combinations')
        
        print(f"Nombre de colonnes: {len(columns)}")
        print()
        
        for column in columns:
            print(f"- {column['name']}: {column['type']} {'(nullable)' if column['nullable'] else '(not null)'}")
        
        print("\n=== ÉCHANTILLON DE DONNÉES PARITE/UNIDOS ===")
        
        # Examiner quelques combinaisons pour voir les valeurs de parite_id et unidos_id
        combinations = db.query(Combination).limit(10).all()
        
        for combo in combinations:
            print(f"Combinaison {combo.combination}:")
            print(f"  parite_id: {combo.parite_id}")
            print(f"  unidos_id: {combo.unidos_id}")
            print("---")
        
        # Vérifier s'il y a des valeurs distinctes pour parite_id et unidos_id
        print("\n=== VALEURS DISTINCTES ===")
        
        parite_values = db.query(Combination.parite_id).distinct().all()
        unidos_values = db.query(Combination.unidos_id).distinct().all()
        
        print(f"Valeurs distinctes parite_id: {[v[0] for v in parite_values]}")
        print(f"Valeurs distinctes unidos_id: {[v[0] for v in unidos_values]}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    return True

if __name__ == "__main__":
    debug_db_structure()