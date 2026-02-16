"""
Serveur API pour le Service Katula Corrigé
Expose les endpoints pour katula-dynamic.html
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

app = FastAPI(title="Katula Corrected API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/katula/table/{universe}")
async def get_katula_table(universe: str):
    """Endpoint pour récupérer la table Katula complète"""
    try:
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        result = service.get_katula_table(universe)
        
        if 'error' in result:
            return {"status": "error", "error": result['error']}
        
        return {"status": "success", "data": result}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/api/formes/{universe}")
async def get_universe_formes(universe: str):
    """Endpoint pour récupérer les formes d'un univers"""
    try:
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        config = service.get_universe_config(universe)
        
        return {
            "status": "success",
            "universe": universe,
            "formes": config.forms,
            "type": config.type.value,
            "description": config.description
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/api/formes/real/{universe}/chip/{chip_id}")
async def get_chip_formes(universe: str, chip_id: str):
    """Endpoint compatible avec katula-dynamic.js"""
    try:
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        
        # Extraire le numéro du chip
        chip_number = int(chip_id.replace('chip', '')) if chip_id.startswith('chip') else int(chip_id)
        
        result = service.get_chip_compartments(universe, chip_number)
        
        if 'error' in result:
            return {"status": "error", "error": result['error']}
        
        # Formater pour katula-dynamic.js
        formes_data = {}
        for compartment in result.get('compartments', []):
            forme = compartment['forme']
            if forme and compartment['denomination']:
                if forme not in formes_data:
                    formes_data[forme] = []
                
                # Séparer les dénominations multiples
                denominations = compartment['denomination'].split('/')
                for denom in denominations:
                    formes_data[forme].append({
                        "denomination": denom.strip(),
                        "frequency": 1
                    })
        
        return {
            "status": "success",
            "formes_data": formes_data,
            "total_items": len(result.get('compartments', []))
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("Demarrage serveur API Katula corrige...")
    print("API: http://localhost:8008/")
    print("Endpoint table: http://localhost:8008/api/katula/table/mundo")
    print("Endpoint chip: http://localhost:8008/api/formes/real/mundo/chip/chip1")
    
    uvicorn.run("katula_corrected_server:app", host="0.0.0.0", port=8008, reload=True)