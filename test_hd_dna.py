
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.abspath(os.getcwd())
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, "backend"))

from backend.app.services.pattern_recognition_service import PatternRecognitionService

def test_high_range():
    print("--- Test Signature Haute Dimension (Numéros > 48) ---")
    service = PatternRecognitionService()
    
    # Numéros hors-chips (49, 55, 66, 77, 88)
    test_nums = [49, 55, 66, 77, 88]
    universe = "mundo"
    
    u_map = service._get_map(universe)
    sig = service.generate_draw_signature(test_nums, universe)
    
    print(f"Numéros testés: {test_nums}")
    print(f"Nombre de paires analysées: {len(sig)}")
    
    # Vérifier la richesse d'une paire
    if sig and sig[0]:
        found_attrs = [k for k, v in sig[0].items() if v != "---"]
        print(f"Paire 1 DNA Density: {len(found_attrs)} attributs trouvés sur 42 possibles.")
        print(f"Attributs détectés: {found_attrs}")
        
        if 'chip' in sig[0] and sig[0]['chip'] == "---":
            print("✅ Confirmation: 'chip' est bien indéfini pour ces numéros (normal).")
        
        if len(found_attrs) > 5:
            print("✅ SUCCÈS: L'IA exploite bien les autres colonnes (parité, région, etc.) même sans jeton (chip)!")
    else:
        print("❌ ERREUR: Aucune donnée ADN trouvée pour ces numéros.")

if __name__ == "__main__":
    test_high_range()
