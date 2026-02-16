"""
Test d'intégration simple
Serveur pour tester katula-dynamic.html avec les vraies données
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir les fichiers statiques
app.mount("/", StaticFiles(directory=".", html=True), name="static")

@app.get("/api/formes/real/{universe}/chip/{chip_id}")
async def get_chip_formes(universe: str, chip_id: str):
    """Endpoint pour les données de chip"""
    try:
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        
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

@app.get("/api")
async def root():
    return {"message": "Test Integration", "page": "/frontend/pages/katula/katula-dynamic.html"}

if __name__ == "__main__":
    import uvicorn
    print("Test integration - katula-dynamic.html")
    print("Page: http://localhost:8008/frontend/pages/katula/katula-dynamic.html")
    uvicorn.run("test_integration:app", host="0.0.0.0", port=8008, reload=True)