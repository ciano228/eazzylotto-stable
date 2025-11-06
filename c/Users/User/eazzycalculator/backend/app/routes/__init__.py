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

# Fin de l'initialisation des routes
logger.info("All routes initialized successfully")