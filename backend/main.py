"""
Module principal de l'API EazzyCalculator.
Fournit l'API FastAPI avec authentification, calculs sécurisés et analytics.

Fonctionnalités principales :
- Authentification JWT
- Calculs mathématiques sécurisés
- Analytics et prédictions
- Support frontend intégré
"""

# Imports standards
from datetime import datetime
from pathlib import Path
import logging
import uvicorn

# Imports FastAPI
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

# Imports locaux
from app.database.connection import engine, Base, get_db
from app.models.user import User
from app.schemas.models import CalcRequest, Token, UserCreate, UserLogin, User as UserSchema
from app.core.auth import (
    get_current_user, create_access_token,
    verify_token, get_password_hash, verify_password
)
from app.core.config import Settings
from app.utils.calculator import evaluate_expression

# Configuration du logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Charger la configuration
settings = Settings()

# Créer l'application FastAPI
app = FastAPI(
    title="EazzyCalculator API",
    description="API sécurisée pour les calculs et prédictions",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Constantes de l'application
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    *settings.CORS_ORIGINS
]

# Configuration des routers
AVAILABLE_ROUTERS = [
    ("app.routes.lottery", "/api/lottery", ["lottery"]),
    ("app.routes.analysis", "/api/analysis", ["analysis"]),
    ("app.routes.analytics", "/api/analytics", ["analytics"]),
    ("app.routes.katula", "/api/katula", ["katula"]),
    ("app.routes.katooling_workflow", "/api/katooling", ["katooling"]),
    ("app.routes.pattern_recognition", "/api/patterns", ["patterns"]),
    ("app.routes.unified_session", "/api/unified", ["sessions"]),
    ("app.routes.journal", "/api/journal", ["journal"]),
    ("app.routes.performance", "/api/performance", ["performance"]),
    ("app.routes.verdict", "/api/verdict", ["verdict"]),
    ("app.routes.chat", "/api/chat", ["chat"])
]

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fonctions utilitaires
def check_database_connection() -> bool:
    """Vérifie la connexion à la base de données"""
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
    except Exception:
        logger.warning("Impossible de se connecter à la base de données")
        return False

def configure_static_files():
    """Configure les fichiers statiques et le frontend"""
    # Fichiers statiques de base
    static_dir = Path("static")
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory="static"), name="static")
        logger.info("Dossier static monté")
    
    # Frontend et assets
    frontend_dir = Path(__file__).parent.parent / "frontend"
    assets_dir = frontend_dir / "assets"
    
    if frontend_dir.exists():
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
            logger.info("Dossier assets monté")
        app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
        logger.info("Frontend monté")
    else:
        logger.warning("Dossier frontend non trouvé")

def setup_routers():
    """Configure et monte les routers de l'application"""
    mounted_count = 0
    
    for path, prefix, tags in AVAILABLE_ROUTERS:
        try:
            module = __import__(path, fromlist=["router"])
            app.include_router(
                module.router,
                prefix=prefix,
                tags=tags
            )
            logger.info(f"Router monté : {path}")
            mounted_count += 1
        except ImportError as e:
            logger.warning(f"Module non trouvé : {path}")
        except Exception as e:
            logger.error(f"Erreur de chargement du router {path} : {e}")
    
    logger.info(f"{mounted_count}/{len(AVAILABLE_ROUTERS)} routers montés avec succès")

def init_app():
    """Initialise l'application FastAPI"""
    try:
        setup_routers()
        configure_static_files()
        logger.info("Application initialisée avec succès")
    except Exception as e:
        logger.error(f"Erreur d'initialisation : {e}")
        raise

# Configuration initiale
# configure_static_files() # Removed to prevent shadowing API routes

# Routes de base
@app.get("/", response_class=HTMLResponse, tags=["root"])
async def root():
    """Page d'accueil avec documentation HTML"""
    return """
    <html>
        <head>
            <title>EazzyCalculator - API Documentation</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    max-width: 800px; 
                    margin: 2em auto; 
                    padding: 0 1em;
                    line-height: 1.6;
                }
                h1 { 
                    color: #2c3e50; 
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 0.5em;
                }
                .links { 
                    margin-top: 2em;
                    background: #f8f9fa;
                    padding: 1em;
                    border-radius: 5px;
                }
                .links a { 
                    color: #3498db; 
                    text-decoration: none;
                    font-weight: bold;
                }
                .links a:hover { 
                    text-decoration: underline; 
                }
                .description {
                    color: #666;
                    font-style: italic;
                }
            </style>
        </head>
        <body>
            <h1>EazzyCalculator - API Documentation</h1>
            <p>Bienvenue sur l'API EazzyCalculator. Cette API sécurisée permet d'effectuer des calculs et des analyses mathématiques.</p>
            <div class="links">
                <p><a href="/api/docs">Documentation API (Swagger UI)</a> <span class="description">- Interface interactive complète</span></p>
                <p><a href="/api/redoc">Documentation alternative (ReDoc)</a> <span class="description">- Format alternatif plus lisible</span></p>
            </div>
        </body>
    </html>
    """

@app.get("/api/health", tags=["health"])
async def health_check():
    """Endpoint de vérification de santé de l'API"""
    try:
        db_status = "connected" if engine.connect() else "disconnected"
    except:
        db_status = "error"
    
    return {
        "status": "healthy",
        "version": f"{settings.PROJECT_NAME} v2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
        "environment": settings.ENVIRONMENT
    }

@app.post("/api/calculate", tags=["calculator"])
async def calculate(request: CalcRequest, current_user: User = Depends(get_current_user)):
    """
    Effectue un calcul mathématique sécurisé
    
    - Supporte les opérations : +, -, *, /, ** (puissance)
    - Les expressions sont validées pour la sécurité
    - Requiert une authentification
    """
    try:
        result = evaluate_expression(request.expr)
        return {"result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors du calcul: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne lors du calcul")

# Routes d'authentification
@app.post("/api/auth/register", response_model=Token, tags=["auth"])
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Enregistre un nouvel utilisateur"""
    # Vérifier si l'utilisateur existe déjà
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")

    # Créer nouvel utilisateur
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Créer token
    access_token = create_access_token(data={"sub": str(db_user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": db_user.id
    }

@app.post("/api/auth/login", response_model=Token, tags=["auth"])
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """Connecte un utilisateur existant"""
    # Vérifier utilisateur
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Nom d'utilisateur ou mot de passe incorrect")

    # Mettre à jour dernière connexion
    db_user.last_login = datetime.utcnow()
    db.commit()

    # Créer token
    access_token = create_access_token(data={"sub": str(db_user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": db_user.id
    }

@app.get("/api/auth/me", response_model=UserSchema, tags=["auth"])
async def get_user_info(current_user: User = Depends(get_current_user)):
    """Récupère les informations de l'utilisateur connecté"""
    return current_user



# Événements de l'application
@app.on_event("startup")
async def startup_event():
    """Événement de démarrage de l'application"""
    try:
        # Initialiser l'application
        init_app()
        
        # Créer les tables
        Base.metadata.create_all(bind=engine)
        logger.info("Tables de base de données créées avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation : {e}")
        raise

if __name__ == "__main__":
    host = settings.HOST or "0.0.0.0"
    port = settings.PORT or 8000
    
    logger.info(f"Démarrage du serveur sur {host}:{port}")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )


# Fin du fichier
