#!/usr/bin/env python3

import sys
sys.path.append('.')
from app.database.connection import get_db
from app.models.combination import Combination
from sqlalchemy import text

def calculate_tome_for_chip(db, chip_number, universe):
    """
    Calcule le tome pour un chip selon la formule :
    sigma = somme des occurrences sur le chip + somme des Q des dénominations distinctes
    
    Règles tome :
    1 <= sigma < 20 : tome1
    20 <= sigma < 30 : tome2  
    30 <= sigma < 40 : tome3
    40 <= sigma < 50 : tome4
    50 <= sigma < 60 : tome5
    etc...
    """
    
    # Récupérer toutes les combinaisons du chip
    combinations = db.query(Combination).filter(
        Combination.chip == f'chip{chip_number}',
        Combination.univers == universe
    ).all()
    
    if not combinations:
        return None, 0, []
    
    # Compter les occurrences totales
    total_occurrences = len(combinations)
    
    # Récupérer les dénominations distinctes et leurs granques
    denominations_granques = {}
    for combo in combinations:
        if combo.denomination not in denominations_granques:
            # Extraire le numéro du granque (ex: "Q1" -> 1, "Q2" -> 2)
            granque_value = 0
            if combo.granque_name:
                try:
                    granque_value = int(combo.granque_name.replace('Q', '').replace('q', ''))
                except:
                    granque_value = 0
            denominations_granques[combo.denomination] = granque_value
    
    # Calculer sigma
    sum_granques = sum(denominations_granques.values())
    sigma = total_occurrences + sum_granques
    
    # Déterminer le tome selon les règles
    if 1 <= sigma < 20:
        tome = "tome1"
    elif 20 <= sigma < 30:
        tome = "tome2"
    elif 30 <= sigma < 40:
        tome = "tome3"
    elif 40 <= sigma < 50:
        tome = "tome4"
    elif 50 <= sigma < 60:
        tome = "tome5"
    elif 60 <= sigma < 70:
        tome = "tome6"
    elif 70 <= sigma < 80:
        tome = "tome7"
    else:
        tome = f"tome{(sigma // 10) + 1}"
    
    return tome, sigma, list(denominations_granques.keys())

def verify_and_fix_tomes():
    db = next(get_db())
    
    universes = ['trigga', 'roaster', 'sunshine']
    
    for universe in universes:
        print(f"\n{'='*50}")
        print(f"VÉRIFICATION UNIVERS: {universe.upper()}")
        print(f"{'='*50}")
        
        corrections_needed = []
        
        for chip_number in range(1, 49):  # Chips 1-48
            calculated_tome, sigma, denominations = calculate_tome_for_chip(db, chip_number, universe)
            
            if calculated_tome is None:
                continue
            
            # Récupérer le tome actuel dans la BD
            current_combinations = db.query(Combination).filter(
                Combination.chip == f'chip{chip_number}',
                Combination.univers == universe
            ).first()
            
            current_tome = current_combinations.tome if current_combinations else None
            
            print(f"\nChip {chip_number}:")
            print(f"  Occurrences: {len(denominations)}")
            print(f"  Dénominations: {', '.join(denominations[:3])}{'...' if len(denominations) > 3 else ''}")
            print(f"  Sigma calculé: {sigma}")
            print(f"  Tome calculé: {calculated_tome}")
            print(f"  Tome actuel BD: {current_tome}")
            
            if current_tome != calculated_tome:
                print(f"  ❌ CORRECTION NÉCESSAIRE: {current_tome} -> {calculated_tome}")
                corrections_needed.append({
                    'chip': chip_number,
                    'universe': universe,
                    'old_tome': current_tome,
                    'new_tome': calculated_tome,
                    'sigma': sigma
                })
            else:
                print(f"  ✅ CORRECT")
        
        # Appliquer les corrections
        if corrections_needed:
            print(f"\n🔧 APPLICATION DES CORRECTIONS POUR {universe.upper()}:")
            
            for correction in corrections_needed:
                try:
                    # Mettre à jour toutes les combinaisons du chip
                    db.execute(
                        text("""
                        UPDATE combinations 
                        SET tome = :new_tome 
                        WHERE chip = :chip_name AND univers = :universe
                        """),
                        {
                            'new_tome': correction['new_tome'],
                            'chip_name': f"chip{correction['chip']}",
                            'universe': correction['universe']
                        }
                    )
                    
                    print(f"  ✅ Chip {correction['chip']}: {correction['old_tome']} -> {correction['new_tome']} (σ={correction['sigma']})")
                    
                except Exception as e:
                    print(f"  ❌ Erreur chip {correction['chip']}: {e}")
            
            # Valider les changements
            db.commit()
            print(f"✅ {len(corrections_needed)} corrections appliquées pour {universe}")
        else:
            print(f"✅ Aucune correction nécessaire pour {universe}")

def test_tome_calculation():
    """Test de la fonction de calcul de tome"""
    db = next(get_db())
    
    print("🧪 TEST DE CALCUL DE TOME")
    print("="*30)
    
    # Tester quelques chips
    test_cases = [
        ('trigga', 1),
        ('roaster', 15),
        ('sunshine', 30)
    ]
    
    for universe, chip_num in test_cases:
        tome, sigma, denominations = calculate_tome_for_chip(db, chip_num, universe)
        print(f"\n{universe} - Chip {chip_num}:")
        print(f"  Sigma: {sigma}")
        print(f"  Tome calculé: {tome}")
        print(f"  Dénominations: {len(denominations)}")

if __name__ == "__main__":
    print("🔍 VÉRIFICATION ET CORRECTION DES TOMES")
    print("Formule: sigma = occurrences + somme(granques des dénominations distinctes)")
    print("Règles: 1-19→tome1, 20-29→tome2, 30-39→tome3, etc.")
    
    # Test d'abord
    test_tome_calculation()
    
    # Puis vérification et correction
    verify_and_fix_tomes()
    
    print("\n🎉 VÉRIFICATION TERMINÉE")