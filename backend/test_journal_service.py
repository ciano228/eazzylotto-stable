"""
Script de test pour le JournalService
Vérifie que les données récupérées sont correctes depuis la BD
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.services.journal_service import JournalService
from app.services.combination_service import CombinationService

# Configuration de la base de données
DATABASE_URL = "sqlite:///./data/katula.db"

# Créer l'engine et la session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_single_combination():
    """Test d'une seule combinaison"""
    print("\n" + "="*60)
    print("TEST 1: Vérification d'une combinaison unique")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Test avec 34-38 qui devrait être dans 'roaster' selon l'utilisateur
        num1, num2 = 34, 38
        
        print(f"\nTest de la combinaison {num1}-{num2}")
        print("-" * 40)
        
        # Méthode 1: Via CombinationService
        combo_info = CombinationService.get_combination_info(db, num1, num2)
        
        if combo_info:
            print("\n✓ Données trouvées dans la BD:")
            print(f"  Univers: {combo_info['univers']}")
            print(f"  Forme: {combo_info['forme']}")
            print(f"  Granque: {combo_info['granque']}")
            print(f"  Petique: {combo_info['petique']}")
            print(f"  Tome: {combo_info['tome']}")
            print(f"  Denomination: {combo_info['denomination']}")
        else:
            print(f"\n✗ Combinaison {num1}-{num2} non trouvée dans la BD")
        
        # Méthode 2: Via JournalService
        print("\n" + "-" * 40)
        print("Via JournalService:")
        entry = JournalService.generate_journal_entry(db, num1, num2)
        
        if "error" not in entry:
            print(f"\n✓ Entrée de journal générée:")
            print(f"  Combination: {entry['combination']}")
            print(f"  Num1: {entry['num1']}")
            print(f"  Forme: {entry['forme']}")
            print(f"  Granque: {entry['granque']}")
            print(f"  Petique: {entry['petique']}")
            print(f"  Tome: {entry['tome']}")
        else:
            print(f"\n✗ Erreur: {entry['error']}")
        
    finally:
        db.close()


def test_full_draw():
    """Test d'un tirage complet"""
    print("\n" + "="*60)
    print("TEST 2: Journal complet d'un tirage")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Exemple de tirage
        numbers = [34, 38, 12, 45]
        
        print(f"\nNuméros du tirage: {numbers}")
        print("-" * 40)
        
        journal = JournalService.generate_full_journal(db, numbers)
        
        print(f"\n✓ Journal généré:")
        print(f"  Total combinaisons: {journal['total_combinations']}")
        print(f"  Entrées valides: {journal['valid_entries']}")
        print(f"  Erreurs: {journal['errors']}")
        
        print(f"\n  Distribution par univers:")
        for univers, entries in journal['by_universe'].items():
            print(f"    - {univers}: {len(entries)} combinaison(s)")
        
        print(f"\n  Première entrée du journal:")
        if journal['journal_entries']:
            first_entry = journal['journal_entries'][0]
            print(f"    Combination: {first_entry['combination']}")
            print(f"    Num1: {first_entry['num1']}")
            print(f"    Forme: {first_entry['forme']}")
            print(f"    Granque: {first_entry['granque']}")
            print(f"    Petique: {first_entry['petique']}")
            print(f"    Tome: {first_entry['tome']}")
        
        # Afficher toutes les entrées
        print(f"\n  Toutes les entrées:")
        for i, entry in enumerate(journal['journal_entries'], 1):
            print(f"\n    Entrée {i}:")
            print(f"      Combination: {entry['combination']}")
            print(f"      Num1: {entry['num1']}")
            print(f"      Univers: {entry['univers']}")
            print(f"      Forme: {entry['forme']}")
            print(f"      Granque: {entry['granque']}")
            print(f"      Petique: {entry['petique']}")
            print(f"      Tome: {entry['tome']}")
        
    finally:
        db.close()


def test_universe_validation():
    """Test de validation d'univers"""
    print("\n" + "="*60)
    print("TEST 3: Validation d'univers")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Test avec des numéros qui devraient être dans 'mundo'
        numbers = [1, 2, 3, 4]
        expected_universe = "mundo"
        
        print(f"\nNuméros: {numbers}")
        print(f"Univers attendu: {expected_universe}")
        print("-" * 40)
        
        validation = JournalService.validate_draw_universe(db, numbers, expected_universe)
        
        print(f"\n✓ Résultat de la validation:")
        print(f"  Valide: {validation['is_valid']}")
        print(f"  Total combinaisons: {validation['total_combinations']}")
        print(f"  Combinaisons valides: {validation['valid_combinations']}")
        
        if validation['invalid_combinations']:
            print(f"\n  ✗ Combinaisons invalides:")
            for invalid in validation['invalid_combinations']:
                print(f"    - {invalid['combination']}: attendu={invalid['expected_universe']}, réel={invalid['actual_universe']}")
        
        print(f"\n  Distribution par univers:")
        for univers, data in validation['universe_distribution'].items():
            print(f"    - {univers}: {data['count']} combinaison(s)")
        
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTS DU SERVICE JOURNAL")
    print("="*60)
    
    test_single_combination()
    test_full_draw()
    test_universe_validation()
    
    print("\n" + "="*60)
    print("TESTS TERMINÉS")
    print("="*60 + "\n")
