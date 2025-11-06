#!/usr/bin/env python3

import sys
sys.path.append('.')
from app.database.connection import get_db
from app.services.combination_service import CombinationService

def debug_service():
    db = next(get_db())
    
    print('=== DEBUG SERVICE COMBINATION ===')
    
    test_cases = ["star 3", "bed 1", "nonexistent"]
    
    for denomination in test_cases:
        print(f'\n🔍 Test service: "{denomination}" dans fruity')
        
        try:
            combinations = CombinationService.get_combinations_by_denomination(
                db, denomination, 'fruity'
            )
            
            print(f"Type retourné: {type(combinations)}")
            print(f"Longueur: {len(combinations)}")
            
            if combinations:
                print("Première combinaison:")
                print(f"  {combinations[0]}")
            else:
                print("Liste vide retournée")
                
        except Exception as e:
            print(f"Exception levée: {e}")

if __name__ == "__main__":
    debug_service()