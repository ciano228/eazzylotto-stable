# Routes package
"""
Package initialization for routes
"""
from fastapi import APIRouter
import importlib
import logging

# Créer le logger
logger = logging.getLogger(__name__)

# Créer le router API principal
api_router = APIRouter()

# Router de test toujours disponible
try:
    from .test import router as test_router
    api_router.include_router(test_router, prefix="/test", tags=["test"])
    logger.info("Test router mounted successfully")
except Exception as e:
    logger.error(f"Error mounting test router: {e}")

# Liste des routers à importer
ROUTER_CONFIGS = [
    {"module": "katula_matrix", "prefix": "/katula-matrix", "tag": "katula-matrix"},
    {"module": "universe_info", "prefix": "/universe", "tag": "universe"},
    {"module": "analysis", "prefix": "/analysis", "tag": "analysis"},
    {"module": "analytics", "prefix": "/analytics", "tag": "analytics"},
    {"module": "combinations", "prefix": "/combinations", "tag": "combinations"},
    {"module": "session", "prefix": "/session", "tag": "session"},
    {"module": "lottery", "prefix": "/lottery", "tag": "lottery"},
    {"module": "katooling_workflow", "prefix": "/katooling", "tag": "katooling"},
    {"module": "katula", "prefix": "/katula", "tag": "katula"}
]

# Importer et monter chaque router dynamiquement
for config in ROUTER_CONFIGS:
    try:
        module = importlib.import_module(f".{config['module']}", package="app.routes")
        router = getattr(module, "router")
        api_router.include_router(router, prefix=config["prefix"], tags=[config["tag"]])
        logger.info(f"Router {config['module']} mounted successfully at {config['prefix']}")
    except Exception as e:
        logger.error(f"Error mounting {config['module']} router: {e}")

# Créer le router API principal
api_router = APIRouter()

# Monter tous les routers
api_router.include_router(katula_matrix_router, prefix="/katula-matrix", tags=["katula-matrix"])
api_router.include_router(universe_info_router, prefix="/universe", tags=["universe"])
api_router.include_router(analysis_router, prefix="/analysis", tags=["analysis"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
api_router.include_router(combinations_router, prefix="/combinations", tags=["combinations"])
api_router.include_router(session_router, prefix="/session", tags=["session"])
api_router.include_router(lottery_router, prefix="/lottery", tags=["lottery"])
api_router.include_router(katooling_router, prefix="/katooling", tags=["katooling"])
api_router.include_router(katula_router, prefix="/katula", tags=["katula"])