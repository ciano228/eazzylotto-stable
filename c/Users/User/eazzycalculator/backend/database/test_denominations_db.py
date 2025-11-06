#!/usr/bin/env python3

import sys
sys.path.append('.')
from app.database.connection import get_db
from app.models.combination import Combination

def test_denominations():
    db = next(get_db())
    
    print('=== VRAIES DÉNOMINATIONS CHIP 44 FRUITY ===')
    results = db.query(Combination.denomination).filter(
        Combination.chip == 'chip44',
        Combination.univers == 'fruity'
    ).distinct().all()
    
    print("Dénominations trouvées:")
    for r in results:
        print(f'- "{r.denomination}"')
    
    print('\n=== TEST API AVEC VRAIES DÉNOMINATIONS ===')
    from app.services.combination_service import CombinationService
    
    for r in results:
        denomination = r.denomination
        print(f'\n🔍 Test: "{denomination}"')
        
        combinations = CombinationService.get_combinations_by_denomination(
            db, denomination, 'fruity'
        )
        
        print(f"Résultats: {len(combinations)} combinaisons")
        for combo in combinations[:2]:  # Limiter à 2
            print(f"  - {combo['combination']} | Position: {combo['alpha_ranking']}")

if __name__ == "__main__":
    test_denominations()