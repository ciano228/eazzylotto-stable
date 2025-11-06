from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pathlib import Path
import psycopg2
import uvicorn
import os

from katula_ui_data_service import KatulaUIDataService
from app.routes.katula_complete_routes import router as katula_complete_router
from app.routes.analytics import router as analytics_router

app = FastAPI(title="Katula Main API")

# Configuration CORS en premier
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pour le développement uniquement
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routeurs
app.include_router(katula_complete_router)
app.include_router(analytics_router)

# Ensuite, monter les fichiers statiques
frontend_dir = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir), html=True), name="static")

DB_CONFIG = {
    'host': 'localhost',
    'database': 'katooling_main_system',
    'user': 'postgres',
    'password': 'Katulaa_33',
    'port': 5432
}

katula_ui_service = KatulaUIDataService(DB_CONFIG)

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(frontend_dir, 'index.html'))

@app.get("/katula-dynamic")
async def serve_katula_dynamic():
    return FileResponse(os.path.join(frontend_dir, 'pages', 'katula', 'katula-dynamic.html'))

@app.get("/api/health")
async def health():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM table_de_katula")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return {"status": "healthy", "total_rows": count}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/katula/table/{universe}")
async def get_katula_table(universe: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT chip_id, univers, ligne, colonne, petique, chip, forme, denomination, granque_name, tome
            FROM table_de_katula 
            WHERE univers = %s 
            ORDER BY chip_id
        """, (universe,))
        
        results = cursor.fetchall()
        
        chips = {}
        for row in results:
            chip_id, univers, ligne, colonne, petique, chip, forme, denomination, granque_name, tome = row
            
            chips[chip_id] = {
                'chip_number': chip_id,
                'ligne': ligne,
                'colonne': colonne,
                'petique': petique,
                'forme': forme,
                'denomination': denomination,
                'granque_name': granque_name,
                'tome': tome,
                'formes': {forme: denomination} if forme else {}
            }
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "universe": universe,
            "chips": chips,
            "total_chips": len(chips)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/denomination/{universe}/{denomination}")
async def get_denomination(universe: str, denomination: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT num1, num2, alpha_ranking, univers, denomination
            FROM table_de_katula 
            WHERE univers = %s AND denomination = %s
        """, (universe, denomination))
        
        results = cursor.fetchall()
        
        details = []
        for row in results:
            num1, num2, alpha_ranking, univers, denom = row
            details.append({
                "num1": num1,
                "num2": num2,
                "alpha_ranking": alpha_ranking,
                "univers": univers,
                "denomination": denom
            })

        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "details": details
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/granque-tome/{universe}")
async def get_granque_tome(universe: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT granque_name 
            FROM table_de_katula 
            WHERE univers = %s AND granque_name IS NOT NULL
        """, (universe,))
        granques = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("""
            SELECT DISTINCT tome 
            FROM table_de_katula 
            WHERE univers = %s AND tome IS NOT NULL
        """, (universe,))
        tomes = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "granque_data": {g: [] for g in granques},
            "tome_data": {t: [] for t in tomes}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/katula/formes")
async def get_katula_formes():
    try:
        formes = katula_ui_service.get_formes()
        return {"formes": formes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/katula/ui-data/{universe}")
async def get_katula_ui_data(universe: str, request: Request):
    print(f"\n=== Requête reçue pour l'univers: {universe} ===")
    print(f"URL complète: {request.url}")
    print(f"En-têtes: {request.headers}")
    
    try:
        print(f"Appel de get_ui_data pour l'univers: {universe}")
        data = katula_ui_service.get_ui_data(universe)
        print(f"Données récupérées: {data}")
        
        if "error" in data:
            print(f"Erreur dans les données: {data['error']}")
            raise HTTPException(status_code=500, detail=data["error"])
            
        print(f"Réponse envoyée pour l'univers: {universe}")
        return data
        
    except HTTPException as he:
        print(f"HTTPException: {he.detail}")
        raise
    except Exception as e:
        error_msg = f"Erreur inattendue: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/api/debug/routes")
async def debug_routes():
    routes = []
    for route in app.routes:
        routes.append({"path": route.path, "name": route.name, "methods": route.methods if hasattr(route, "methods") else []})
    return {"routes": routes}

# Gestionnaire d'erreurs 404 pour le routage côté client
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: StarletteHTTPException):
    return FileResponse(os.path.join(str(frontend_dir), 'index.html'))

# Gestionnaire d'erreurs global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Une erreur interne est survenue."}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)