from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Créer l'application FastAPI
app = FastAPI(
    title="EazzyCalculator API",
    description="API pour l'analyse et la prédiction des numéros de loterie",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permet toutes les origines pour le développement
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes de base d'abord
@app.get("/")
async def root():
    return {"message": "EazzyCalculator API is running"}

@app.get("/api")
async def api_root():
    return {"message": "EazzyCalculator API is running"}

@app.get("/api/health")
async def health_check():
    """Endpoint de vérification de santé"""
    return {"status": "healthy", "message": "Backend EazzyLotto opérationnel"}

# Essayer d'importer et monter les routes avec gestion d'erreurs
try:
    from app.database.connection import engine, Base
    # Créer les tables
    Base.metadata.create_all(bind=engine)
    print("[OK] Base de données initialisée")
except Exception as e:
    print(f"[WARNING] Erreur base de données: {e}")

# Importer les routers avec gestion d'erreurs
routers_loaded = 0
try:
    from app.routes.session import router as session_router
    app.include_router(session_router, prefix="/api/session", tags=["session"])
    print("[OK] Session router monté")
    routers_loaded += 1
except Exception as e:
    print(f"[ERROR] Session router: {e}")

try:
    from app.routes.analytics import router as analytics_router
    app.include_router(analytics_router)
    print("[OK] Analytics router monté")
    routers_loaded += 1
except Exception as e:
    print(f"[ERROR] Analytics router: {e}")

try:
    from app.routes.lottery import router as lottery_router
    app.include_router(lottery_router, prefix="/api/lottery", tags=["lottery"])
    print("[OK] Lottery router monté")
    routers_loaded += 1
except Exception as e:
    print(f"[ERROR] Lottery router: {e}")

try:
    from app.routes.analysis import router as analysis_router
    app.include_router(analysis_router, prefix="/api/analysis", tags=["analysis"])
    print("[OK] Analysis router monté")
    routers_loaded += 1
except Exception as e:
    print(f"[ERROR] Analysis router: {e}")

try:
    from app.routes.katooling_workflow import router as katooling_workflow_router
    app.include_router(katooling_workflow_router, prefix="/api/katooling", tags=["katooling"])
    print("[OK] Katooling router monté")
    routers_loaded += 1
except Exception as e:
    print(f"[ERROR] Katooling router: {e}")

print(f"[INFO] {routers_loaded}/5 routers chargés avec succès")

# Routes de test supplémentaires
@app.get("/api/test")
async def test_endpoint():
    return {"status": "test", "message": "Endpoint de test fonctionnel"}

@app.get("/api/session/test")
async def test_session():
    return {"status": "session_test", "sessions": []}

@app.get("/api/analytics/test")
async def test_analytics():
    return {"status": "analytics_test", "data": {}}

# Chemins absolus vers les dossiers frontend
current_dir = Path(__file__).parent
frontend_dir = current_dir.parent / "frontend"
assets_dir = frontend_dir / "assets"

# Servir les fichiers statiques du frontend (APRÈS les routes API)
app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
