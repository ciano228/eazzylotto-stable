"""
Test du JournalServiceV2 avec PostgreSQL
"""
from app.services.journal_service_v2 import JournalServiceV2

print("=" * 80)
print("TEST DU JOURNAL SERVICE V2 AVEC POSTGRESQL")
print("=" * 80)

print("\n1. TEST: Recuperation de la combinaison 34-38")
print("-" * 80)

entry = JournalServiceV2.generate_journal_entry(34, 38)

if "error" in entry:
    print(f"[ERREUR] {entry['error']}")
else:
    print("[OK] Combinaison trouvee !\n")
    print(f"Combination      : {entry.get('num1')}-{entry.get('num2')}")
    print(f"Univers          : {entry.get('univers')}")
    print(f"Forme            : {entry.get('forme')}")
    print(f"Granque          : {entry.get('granque_name')}")
    print(f"Petique          : {entry.get('petique')}")
    print(f"Tome             : {entry.get('tome')}")
    print(f"Denomination     : {entry.get('denomination')}")
    print(f"Engine           : {entry.get('engine')}")
    print(f"Beastie          : {entry.get('beastie')}")
    print(f"Chip             : {entry.get('chip')}")
    print(f"Ligne            : {entry.get('ligne')}")
    print(f"Colonne          : {entry.get('colonne')}")
    print(f"Alpha Ranking    : {entry.get('alpha_ranking')}")
    print(f"Quartier         : {entry.get('quartier')}")
    print(f"Region           : {entry.get('region')}")
    print(f"Gentillee        : {entry.get('gentillee')}")

print("\n" + "=" * 80)
print("2. TEST: Journal complet pour un tirage")
print("-" * 80)

numbers = [34, 38, 12, 45]
print(f"\nNumeros du tirage: {numbers}\n")

journal = JournalServiceV2.generate_full_journal(numbers)

print(f"Total combinaisons : {journal['total_combinations']}")
print(f"Entrees valides    : {journal['valid_entries']}")
print(f"Erreurs            : {journal['errors']}")

print(f"\nDistribution par univers:")
for univers, entries in journal['by_universe'].items():
    print(f"  - {univers:15} : {len(entries)} combinaison(s)")

print(f"\nPremieres entrees du journal:")
for i, entry in enumerate(journal['journal_entries'][:3], 1):
    print(f"\n  Entree {i}:")
    print(f"    Combination : {entry.get('num1')}-{entry.get('num2')}")
    print(f"    Univers     : {entry.get('univers')}")
    print(f"    Forme       : {entry.get('forme')}")
    print(f"    Granque     : {entry.get('granque_name')}")
    print(f"    Tome        : {entry.get('tome')}")

print("\n" + "=" * 80)
print("3. TEST: Validation d'univers")
print("-" * 80)

numbers = [34, 38]
expected_universe = "mundo"

print(f"\nNumeros          : {numbers}")
print(f"Univers attendu  : {expected_universe}\n")

validation = JournalServiceV2.validate_draw_universe(numbers, expected_universe)

print(f"Valide           : {validation['is_valid']}")
print(f"Total combinaisons : {validation['total_combinations']}")
print(f"Combinaisons valides : {validation['valid_combinations']}")

if validation['invalid_combinations']:
    print(f"\nCombinaisons invalides:")
    for invalid in validation['invalid_combinations']:
        print(f"  - {invalid['combination']}: attendu={invalid['expected_universe']}, reel={invalid['actual_universe']}")

print("\n" + "=" * 80)
print("TESTS TERMINES - TOUTES LES DONNEES PROVIENNENT DE POSTGRESQL")
print("=" * 80)
