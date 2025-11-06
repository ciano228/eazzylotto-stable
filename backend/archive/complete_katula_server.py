from fastapi import FastAPI, HTTPException, status, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import traceback
import uvicorn
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

# Import du service Katula mis à jour
from katula_complete_service import KatulaCompleteService as KCS

# Configuration de la base de données PostgreSQL
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "Katulaa_33")
POSTGRES_DB = os.getenv("POSTGRES_DB", "katooling_main_system")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class KatulaCompleteService:
    """Service pour interagir avec les données Katula dans la base de données"""
    
    # Utilisation de la configuration dynamique du service
    UNIVERSES = list(KCS().UNIVERSES.keys())
    
    # Valeurs par défaut (peuvent être surchargées par la configuration de l'univers)
    TOMES = ['tome1', 'tome2', 'tome3', 'tome4', 'tome5']

    def __init__(self):
        self.kcs = KCS()

    def get_available_universes(self):
        """Retourne la liste des univers disponibles"""
        return [{"name": name, "description": f"Univers {name}"} for name in self.UNIVERSES]

    def get_formes(self, universe: str):
        """Retourne les formes disponibles pour un univers donné"""
        if universe not in self.UNIVERSES:
            return []
        
        # Exemple de formes, à adapter selon vos besoins
        return [
            {"id": "carre", "name": "Carré", "color": "#3498db"},
            {"id": "cercle", "name": "Cercle", "color": "#e74c3c"},
            {"id": "triangle", "name": "Triangle", "color": "#2ecc71"},
            {"id": "rectangle", "name": "Rectangle", "color": "#f39c12"}
        ]

    def get_katula_table(self, universe: str):
        """Récupère les données de la table Katula pour un univers donné"""
        try:
            # Appel synchrone à la méthode de KCS
            return self.kcs.get_katula_table(universe)
        except Exception as e:
            print(f"Erreur lors de la récupération des données: {str(e)}")
            raise

    def get_granque_tome_data(self, universe: str):
        """Récupère les données granque/tome pour un univers donné"""
        # Exemple de données, à adapter selon vos besoins
        return {
            "granques": [
                {"id": 1, "name": "Granque 1", "description": "Description granque 1"},
                {"id": 2, "name": "Granque 2", "description": "Description granque 2"}
            ],
            "tomes": [
                {"id": 1, "name": "Tome 1", "description": "Description tome 1"},
                {"id": 2, "name": "Tome 2", "description": "Description tome 2"}
            ]
        }

# État des mises à jour
update_status = {
    'in_progress': False,
    'last_update': None,
    'last_error': None,
    'next_scheduled': None
}

def check_for_updates():
    """Vérifie les mises à jour disponibles"""
    try:
        # Exemple: git fetch pour vérifier les mises à jour
        result = subprocess.run(['git', 'fetch'], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        if result.returncode != 0:
            return False, "Erreur lors de la vérification des mises à jour"
        
        # Vérifier s'il y a des mises à jour
        result = subprocess.run(['git', 'status', '-uno'], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        return 'Your branch is behind' in result.stdout, None
    except Exception as e:
        return False, str(e)

def perform_update():
    """Effectue la mise à jour du système"""
    global update_status
    update_status['in_progress'] = True
    update_status['last_error'] = None
    
    try:
        # Sauvegarder les données actuelles
        backup_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backup')
        os.makedirs(backup_path, exist_ok=True)
        
        # Mettre à jour le code
        subprocess.run(['git', 'pull'], check=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        # Mettre à jour les dépendances si nécessaire
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      cwd=os.path.dirname(os.path.abspath(__file__)))
        
        update_status['last_update'] = datetime.now().isoformat()
        update_status['next_scheduled'] = (datetime.now() + timedelta(hours=24)).isoformat()
        return True, None
    except Exception as e:
        update_status['last_error'] = str(e)
        return False, str(e)
    finally:
        update_status['in_progress'] = False

def schedule_updates():
    """Planifie les vérifications de mises à jour"""
    while True:
        try:
            has_updates, error = check_for_updates()
            if error:
                print(f"Erreur lors de la vérification des mises à jour: {error}")
            elif has_updates:
                print("Mises à jour disponibles. Mise à jour en cours...")
                success, error = perform_update()
                if success:
                    print("Mise à jour terminée avec succès")
                    # Redémarrer l'application
                    os.execl(sys.executable, sys.executable, *sys.argv)
                else:
                    print(f"Échec de la mise à jour: {error}")
        except Exception as e:
            print(f"Erreur dans la planification des mises à jour: {e}")
        
        # Vérifier toutes les 24 heures
        time.sleep(24 * 60 * 60)

# Démarrer le thread de vérification des mises à jour
update_thread = threading.Thread(target=schedule_updates, daemon=True)
update_thread.start()

# Initialisation de l'application FastAPI
app = FastAPI(
    title="API Katula",
    description="API pour la gestion des données Katula",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation du service
service = KatulaCompleteService()

# Routes API
@app.get("/api/katula/universes", response_model=Dict[str, Any])
async def get_universes():
    """Retourne la liste des univers disponibles"""
    try:
        universes = service.get_available_universes()
        return {"status": "success", "universes": universes}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des univers: {str(e)}"
        )

@app.get("/api/katula/table/{universe}", response_model=Dict[str, Any])
async def get_katula_table(universe: str):
    """Récupère les données de la table Katula pour un univers donné"""
    try:
        table_data = service.get_katula_table(universe)
        if not table_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Aucune donnée trouvée pour l'univers {universe}"
            )
        return {"status": "success", "data": table_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des données: {str(e)}"
        )

@app.get("/api/katula/formes/{universe}", response_model=Dict[str, Any])
async def get_formes(universe: str):
    """Récupère les formes disponibles pour un univers donné"""
    try:
        formes = service.get_formes(universe)
        return {"status": "success", "formes": formes}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des formes: {str(e)}"
        )

@app.get("/api/katula/granque-tome/{universe}", response_model=Dict[str, Any])
async def get_granque_tome(universe: str):
    """Récupère les données granque/tome pour un univers donné"""
    try:
        data = service.get_granque_tome_data(universe)
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des données granque/tome: {str(e)}"
        )

# Redirection de l'ancien endpoint vers le nouveau
@app.get("/granque-tome/{universe}")
async def legacy_granque_tome(universe: str):
    """Ancien endpoint maintenu pour la rétrocompatibilité"""
    return await get_granque_tome(universe)

# Ajoutez cette route pour la racine de l'API
@app.get("/")
async def root():
    return {
        "message": "Bienvenue sur l'API Katula",
        "documentation": "/docs",
        "endpoints": {
            "universes": "/api/katula/universes",
            "table": "/api/katula/table/{universe}",
            "formes": "/api/katula/formes/{universe}",
            "granque_tome": "/api/katula/granque-tome/{universe}"
        }
    }

# Ajoutez cette route pour la racine de l'API
@app.get("/api")
async def api_root():
    return await root()

# Endpoints pour la gestion des mises à jour
@app.get("/api/update/check", tags=["Mises à jour"])
async def check_update():
    """Vérifie si des mises à jour sont disponibles"""
    has_updates, error = check_for_updates()
    return {
        "update_available": has_updates,
        "last_checked": datetime.now().isoformat(),
        "error": error
    }

@app.post("/api/update/apply", tags=["Mises à jour"])
async def apply_update():
    """Applique les mises à jour disponibles"""
    if update_status['in_progress']:
        raise HTTPException(status_code=400, detail="Une mise à jour est déjà en cours")
    
    success, error = perform_update()
    if success:
        return {"status": "success", "message": "Mise à jour appliquée avec succès"}
    else:
        raise HTTPException(status_code=500, detail=f"Échec de la mise à jour: {error}")

@app.get("/api/update/status", tags=["Mises à jour"])
async def get_update_status():
    """Récupère l'état actuel des mises à jour"""
    return {
        "in_progress": update_status['in_progress'],
        "last_update": update_status['last_update'],
        "last_error": update_status['last_error'],
        "next_scheduled": update_status['next_scheduled']
    }
from fastapi import Request
from fastapi.responses import JSONResponse

@app.post("/api/kiro/chat")
async def kiro_chat(request: Request):
    data = await request.json()
    message = data.get("message", "")

    return JSONResponse(
        content={
            "status": "success",
            "model": "katula-gpt",             # ✅ requis par Kiro
            "type": "text",                    # ✅ aide Kiro à interpréter le format
            "streaming": True,                 # ✅ indique que la réponse est streamable
            "response": f"Réponse à: {message}",
            "tokens": len(message.split())
        },
        media_type="application/json; charset=utf-8"
    )
if __name__ == "__main__":
    # Vérifier les mises à jour au démarrage
    has_updates, _ = check_for_updates()
    if has_updates:
        print("Mises à jour disponibles. Utilisez l'API pour les appliquer.")
    
    uvicorn.run(
        "complete_katula_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )