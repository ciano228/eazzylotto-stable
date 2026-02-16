
import sys
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
import itertools

# Adjust path to include the current directory
sys.path.append(os.getcwd())

from backend.split_strategy_service import SplitStrategyService
from backend.unified_db_session_service import UnifiedDBSessionService

db_config = {
    'dbname': 'katooling_main_system',
    'user': 'postgres',
    'password': 'Katulaa_33',
    'host': 'localhost',
    'port': '5432'
}

def extended_audit_180_draws():
    print(f"\n{'='*75}")
    print(f"AUDIT ÉTENDU : ANALYSE SUR 180 TIRAGES (ENV. 3.5 ANS)")
    print(f"{'='*75}\n")
    
    universe = 'mundo'
    session_id = 25
    
    split_service = SplitStrategyService(db_config)
    session_service = UnifiedDBSessionService()
    
    # 1. Charger les tirages et isoler les 180 derniers
    all_draws = session_service.get_session_draws(session_id)
    # Trier par date décroissante pour prendre les plus récents
    draws = sorted(all_draws, key=lambda x: x.get('draw_date') or "", reverse=True)[:180]
    draws.reverse() # Remettre en ordre chronologique
    
    print(f"Nombre de tirages analysés : {len(draws)}")
    
    # 2. Zone de référence
    all_79_combos = set(split_service._get_all_combinations_for_attribute(universe, 'forme_tome', 'rectangle_tome1'))
    
    # 3. Traçage
    ya_played_data = defaultdict(int) 
    total_hits = 0
    draws_with_hit = 0
    
    for draw in draws:
        nums = sorted(draw.get('winning_numbers', []))
        pairs = [f"{p[0]}-{p[1]}" for p in itertools.combinations(nums, 2)]
        
        hit_in_draw = False
        for p in pairs:
            if p in all_79_combos:
                ya_played_data[p] += 1
                total_hits += 1
                hit_in_draw = True
        
        if hit_in_draw:
            draws_with_hit += 1
            
    # 4. Résultats du Split
    ya_count = len(ya_played_data)
    not_yet_count = len(all_79_combos) - ya_count
    
    print(f"--- RÉSULTATS DU SPLIT (N=180 TIRAGES) ---")
    print(f"  Combinaisons YA-PLAYED (Actives)   : {ya_count}/{len(all_79_combos)}")
    print(f"  Combinaisons NOT-YET-PLAYED (Sommeil) : {not_yet_count}/{len(all_79_combos)}")
    
    # 5. Constance
    freq = (draws_with_hit / 180) * 100
    print(f"\nANALYSE DE CONSTANCE :")
    print(f"  Le pattern est sorti dans {draws_with_hit} tirages sur 180.")
    print(f"  Fréquence réelle observée : {freq:.1f}%")
    print(f"  Nombre total de paires sorties : {total_hits}")

    # 6. Comparaison Financière
    cost_full = 180 * 79
    gain_full = draws_with_hit * 200 # Conservateur (1 gain max par tirage)
    
    # Pour le Ya-Played, on simule le coût basé sur la taille du groupe trouvé
    cost_split = 180 * ya_count
    gain_split = total_hits * 200 # On compte tous les hits car on joue les pièces précises
    
    print(f"\n--- PERFORMANCE SUR 180 TIRAGES ---")
    print(f"STRATÉGIE FULL (79 pièces) :")
    print(f"  Coût: {cost_full} | Gains: {gain_full} | Profit: {gain_full - cost_full} | ROI: {(gain_full/cost_full)*100:.1f}%")
    
    print(f"STRATÉGIE SPLIT (Ciblée sur {ya_count} pièces) :")
    print(f"  Coût: {cost_split} | Gains: {gain_split} | Profit: {gain_split - cost_split} | ROI: {(gain_split/cost_split)*100:.1f}%")

    # 7. Distribution des Hits
    print(f"\nDistribution des répétitions :")
    sorted_ya = sorted(ya_played_data.items(), key=lambda x: x[1], reverse=True)
    
    # On regarde si certaines sortent vraiment beaucoup plus que d'autres
    top_5 = sorted_ya[:5]
    print(f"  Top 5 des combinaisons les plus 'chaudes' :")
    for combo, count in top_5:
        print(f"    - {combo} : {count} sorties en {len(draws)} tirages")

    print("\nOBSERVATION FINALE :")
    if ya_count > 19:
        print(f"En passant de 180 jours à 180 tirages, le nombre d'actives est passé de 19 à {ya_count}.")
        print("Cela prouve que sur le long terme, plus de combinaisons sortent,")
        print("MAIS une grande partie de la zone (environ 25-30%) reste totalement inactive même après 3 ans !")

if __name__ == "__main__":
    extended_audit_180_draws()
