#!/usr/bin/env python3
"""
Script pour diagnostiquer les données des combinaisons
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import get_db
from app.models.combination import Combination

def debug_combinations():
    """Examiner les données des combinaisons"""
    
    try:
        # Obtenir une session de base de données
        db = next(get_db())
        
        print("=== DIAGNOSTIC DES COMBINAISONS ===")
        
        # Examiner quelques combinaisons pour voir le format des données
        combinations = db.query(Combination).limit(10).all()
        
        print(f"Nombre de combinaisons trouvées: {len(combinations)}")
        print()
        
        for i, combo in enumerate(combinations, 1):
            print(f"Combinaison {i}: {combo.combination}")
            print(f"  Univers: '{combo.univers}'")
            print(f"  Forme: '{combo.forme}'")
            print(f"  Engine: '{combo.engine}'")
            print(f"  Beastie: '{combo.beastie}'")
            print(f"  Tome: '{combo.tome}'")
            print(f"  Denomination: '{combo.denomination}'")
            print(f"  Alpha Ranking: '{combo.alpha_ranking}'")
            print("---")
        
        # Vérifier s'il y a des données mélangées
        print("\n=== ANALYSE DES DONNÉES MÉLANGÉES ===")
        
        # Chercher des combinaisons où les données semblent mélangées
        mixed_data = db.query(Combination).filter(
            Combination.forme.ilike('%car%') |
            Combination.forme.ilike('%lion%') |
            Combination.forme.ilike('%tiger%') |
            Combination.engine.ilike('%carre%') |
            Combination.engine.ilike('%triangle%')
        ).limit(5).all()
        
        if mixed_data:
            print("Données potentiellement mélangées trouvées:")
            for combo in mixed_data:
                print(f"  {combo.combination}: forme='{combo.forme}', engine='{combo.engine}', beastie='{combo.beastie}'")
        else:
            print("Aucune donnée mélangée détectée dans l'échantillon.")
        
        # Statistiques par univers
        print("\n=== STATISTIQUES PAR UNIVERS ===")
        universes = db.query(Combination.univers).distinct().all()
        for (universe,) in universes:
            count = db.query(Combination).filter(Combination.univers == universe).count()
            print(f"  {universe}: {count} combinaisons")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    return True

if __name__ == "__main__":
    debug_combinations()