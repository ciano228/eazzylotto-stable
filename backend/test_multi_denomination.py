#!/usr/bin/env python3

import sys
sys.path.append('.')
from app.database.connection import get_db
from app.services.combination_service import CombinationService

def test_multi_denomination():
    db = next(get_db())
    
    print('=== TEST DÉNOMINATION MULTIPLE: star 3/star 7 ===')
    results = CombinationService.get_combinations_by_denomination(db, 'star 3/star 7', 'fruity')
    
    for r in results:
        print(f'Dénomination: {r["denomination"]} | Combinaison: {r["combination"]} | Position: {r["alpha_ranking"]}')
    
    print(f'\nTotal: {len(results)} combinaisons trouvées')
    
    print('\n=== TEST DÉNOMINATION SIMPLE: star 3 ===')
    results_simple = CombinationService.get_combinations_by_denomination(db, 'star 3', 'fruity')
    
    for r in results_simple:
        print(f'Dénomination: {r["denomination"]} | Combinaison: {r["combination"]} | Position: {r["alpha_ranking"]}')
    
    print(f'\nTotal: {len(results_simple)} combinaisons trouvées')

if __name__ == "__main__":
    test_multi_denomination()