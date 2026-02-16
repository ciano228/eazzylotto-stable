"""
Test du JournalService avec les vraies données PostgreSQL
"""
from app.database.connection import SessionLocal
from app.services.journal_service import JournalService

print("=" * 80)
print("TEST DU JOURNAL SERVICE AVEC POSTGRESQL")
print("=" * 80)

db = SessionLocal()

try:
    print("\n1. TEST: Récupération de la combinaison 34-38")
    print("-" * 80)
    
    entry = JournalService.generate_journal_entry(db, 34, 38)
    
    if "error" in entry:
        print(f"[ERREUR] {entry['error']}")
    else:
        print("[OK] Combinaison trouvée !\n")
        print(f"Combination      : {entry['combination']}")
        print(f"Num1             : {entry['num1']}")
        print(f"Num2             : {entry['num2']}")
        print(f"Univers          : {entry['univers']}")
        print(f"Forme            : {entry['forme']}")
        print(f"Granque          : {entry['granque']}")
        print(f"Petique          : {entry['petique']}")
        print(f"Tome             : {entry['tome']}")
        print(f"Denomination     : {entry['denomination']}")
        print(f"Engine           : {entry['engine']}")
        print(f"Beastie          : {entry['beastie']}")
        print(f"Chip             : {entry['chip']}")
        print(f"Ligne            : {entry['ligne']}")
        print(f"Colonne          : {entry['colonne']}")
        print(f"Alpha Ranking    : {entry['alpha_ranking']}")
    
    print("\n" + "=" * 80)
    print("2. TEST: Journal complet pour un tirage")
    print("-" * 80)
    
    numbers = [34, 38, 12, 45]
    print(f"\nNuméros du tirage: {numbers}\n")
    
    journal = JournalService.generate_full_journal(db, numbers)
    
    print(f"Total combinaisons : {journal['total_combinations']}")
    print(f"Entrées valides    : {journal['valid_entries']}")
    print(f"Erreurs            : {journal['errors']}")
    
    print(f"\nDistribution par univers:")
    for univers, entries in journal['by_universe'].items():
        print(f"  - {univers:15} : {len(entries)} combinaison(s)")
    
    print(f"\nPremières entrées du journal:")
    for i, entry in enumerate(journal['journal_entries'][:3], 1):
        print(f"\n  Entrée {i}:")
        print(f"    Combination : {entry['combination']}")
        print(f"    Univers     : {entry['univers']}")
        print(f"    Forme       : {entry['forme']}")
        print(f"    Granque     : {entry['granque']}")
        print(f"    Tome        : {entry['tome']}")
    
    print("\n" + "=" * 80)
    print("3. TEST: Validation d'univers")
    print("-" * 80)
    
    numbers = [34, 38]
    expected_universe = "mundo"
    
    print(f"\nNuméros          : {numbers}")
    print(f"Univers attendu  : {expected_universe}\n")
    
    validation = JournalService.validate_draw_universe(db, numbers, expected_universe)
    
    print(f"Valide           : {validation['is_valid']}")
    print(f"Total combinaisons : {validation['total_combinations']}")
    print(f"Combinaisons valides : {validation['valid_combinations']}")
    
    if validation['invalid_combinations']:
        print(f"\nCombinaisons invalides:")
        for invalid in validation['invalid_combinations']:
            print(f"  - {invalid['combination']}: attendu={invalid['expected_universe']}, réel={invalid['actual_universe']}")
    
    print("\n" + "=" * 80)
    print("TESTS TERMINES")
    print("=" * 80)
    
finally:
    db.close()
