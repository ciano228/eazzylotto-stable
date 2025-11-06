"""
API principale EazzyCalculator V2.

Cette API fournit une interface améliorée pour l'analyse et la gestion 
des combinaisons de loterie, avec un support pour plusieurs bases de données.
"""
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from app.api.db import init_db_connection, check_database_health
from app.api.combinations import router as combinations_router

# Créer l'application FastAPI
app = FastAPI(
    title="EazzyCalculator API V2",
    description="API améliorée pour l'analyse et la gestion des combinaisons de loterie",
    version="2.0.0",
    lifespan=init_db_connection
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routers
app.include_router(combinations_router)
from app.api.analysis import router as analysis_router
app.include_router(analysis_router)

# Route de base
@app.get("/", tags=["root"])
async def root() -> Dict[str, str]:
    """Route principale de l'API"""
    return {
        "message": "Bienvenue sur l'API EazzyCalculator V2",
        "version": "2.0.0",
        "status": "active"
    }

# Route de santé
@app.get("/health", tags=["health"])
async def health_check() -> Dict[str, Any]:
    """Vérification de l'état de l'API et des connexions aux bases de données"""
    health_status = await check_database_health()
    health_status["version"] = "2.0.0"
    
    if health_status["status"] != "healthy":
        raise HTTPException(
            status_code=500,
            detail=health_status["error"]
        )
    
    return health_status

if __name__ == "__main__":
    uvicorn.run(
        "api_v2:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )
