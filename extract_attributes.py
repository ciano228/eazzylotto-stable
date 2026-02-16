
import os
import sys
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Chemins
BASE_DIR = os.path.abspath(os.getcwd())
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, "backend"))

from backend.app.services.pattern_recognition_service import PatternRecognitionService

def dump_columns():
    service = PatternRecognitionService()
    universe = "mundo"
    
    # Load map
    u_map = service._get_map(universe)
    
    # Get all keys from the first entry to see all attributes
    first_key = next(iter(u_map))
    all_attributes = list(u_map[first_key][0].keys())
    
    result = {
        "universe": universe,
        "mapping_size": len(u_map),
        "attribute_columns": all_attributes,
        "sample_pair": f"{first_key[0]}-{first_key[1]}",
        "sample_data": u_map[first_key][0]
    }
    
    with open('katooling_attributes.json', 'w') as f:
        json.dump(result, f, indent=4)
    
    print(f"Extraction terminée : {len(all_attributes)} attributs trouvés.")

if __name__ == "__main__":
    dump_columns()
