"""
Serveur alternatif pour katula-dynamic.html avec ports fixes différents
"""
import http.server
import socketserver
import threading
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Serveur API FastAPI
api_app = FastAPI()
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@api_app.get("/api/universe/{universe}/formes")
async def get_universe_formes(universe: str):
    try:
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        
        config = service.get_universe_config(universe)
        return {
            "status": "success",
            "universe": universe,
            "formes": config.forms,
            "total_formes": len(config.forms),
            "type": config.type.value,
            "description": config.description
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/formes/real/{universe}/chip/{chip_id}")
async def get_chip_formes(universe: str, chip_id: str):
    try:
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        
        chip_number = int(chip_id.replace('chip', '')) if chip_id.startswith('chip') else int(chip_id)
        result = service.get_chip_compartments(universe, chip_number)
        
        if 'error' in result:
            return {"status": "error", "error": result['error']}
        
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

@api_app.get("/api/filter-options/{universe}")
async def get_filter_options(universe: str):
    try:
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        return service.get_filter_options(universe)
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/granques/{universe}")
async def get_granques(universe: str):
    try:
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        options = service.get_filter_options(universe)
        return {
            "status": "success",
            "granques": options.get('filter_options', {}).get('granques', []),
            "universe": universe
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/tomes/{universe}")
async def get_tomes(universe: str):
    try:
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        options = service.get_filter_options(universe)
        return {
            "status": "success",
            "tomes": options.get('filter_options', {}).get('tomes', []),
            "universe": universe
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.post("/api/filter/{universe}")
async def apply_filters(universe: str, filters: dict):
    try:
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        return service.apply_filters(universe, filters)
    except Exception as e:
        return {"status": "error", "error": str(e)}

def start_api_server():
    import uvicorn
    uvicorn.run(api_app, host="0.0.0.0", port=8877, log_level="error")

def start_file_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 9977), handler) as httpd:
        print("✅ Serveur Web: http://localhost:9977/frontend/katula-dynamic.html")
        httpd.serve_forever()

if __name__ == "__main__":
    print("=== SERVEUR KATULA ALTERNATIF ===")
    print("🚀 API: http://localhost:8877")
    print("🌐 PAGE: http://localhost:9977/frontend/katula-dynamic.html")
    print("📡 ENDPOINTS: http://localhost:8877/docs")
    
    # Démarrer l'API en arrière-plan
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    
    time.sleep(2)  # Attendre que l'API démarre
    print("✅ API démarrée sur port 8877")
    
    # Démarrer le serveur de fichiers
    start_file_server()