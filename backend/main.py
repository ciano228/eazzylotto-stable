from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
import os
from pathlib import Path
from dotenv import load_dotenv

# Importer nos modules d'authentification
try:
    from database import get_db, init_db
    from models import User, LotteryDraw, UserSession
    from auth import verify_password, get_password_hash, create_access_token, verify_token
    AUTH_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Modules d'authentification non disponibles: {e}")
    AUTH_AVAILABLE = False

# Charger les variables d'environnement
load_dotenv()

# Créer l'application FastAPI
app = FastAPI(
    title="EazzyCalculator API",
    description="API pour l'analyse et la prédiction des numéros de loterie avec authentification",
    version="2.0.0"
)

# Configuration de sécurité
security = HTTPBearer() if AUTH_AVAILABLE else None

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
    return {
        "status": "healthy", 
        "message": "Backend EazzyLotto opérationnel",
        "auth_available": AUTH_AVAILABLE,
        "version": "2.0.0"
    }

# Routes d'authentification (si disponibles)
if AUTH_AVAILABLE:
    from pydantic import BaseModel
    from typing import Optional
    from datetime import datetime
    
    class UserCreate(BaseModel):
        username: str
        email: str
        password: str
    
    class UserLogin(BaseModel):
        username: str
        password: str
    
    class Token(BaseModel):
        access_token: str
        token_type: str
        user_id: int
    
    @app.post("/api/auth/register", response_model=Token)
    async def register(user: UserCreate, db: Session = Depends(get_db)):
        # Vérifier si l'utilisateur existe
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
    
    @app.post("/api/auth/login", response_model=Token)
    async def login(user: UserLogin, db: Session = Depends(get_db)):
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
    
    # Middleware d'authentification
    async def get_current_user(token: str = Depends(security), db: Session = Depends(get_db)):
        try:
            # Extraire le token du header Authorization
            if hasattr(token, 'credentials'):
                token_str = token.credentials
            else:
                token_str = token
            
            user_id = verify_token(token_str)
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
            return user
        except Exception as e:
            raise HTTPException(status_code=401, detail="Token invalide")
    
    print("[OK] Routes d'authentification configurées")
else:
    print("[WARNING] Authentification désactivée - modules manquants")

# Initialiser la base de données
if AUTH_AVAILABLE:
    try:
        init_db()
        print("[OK] Base de données d'authentification initialisée")
    except Exception as e:
        print(f"[WARNING] Erreur init base de données auth: {e}")

# Essayer d'importer et monter les routes avec gestion d'erreurs
try:
    from app.database.connection import engine, Base
    # Créer les tables
    Base.metadata.create_all(bind=engine)
    print("[OK] Base de données principale initialisée")
except Exception as e:
    print(f"[WARNING] Erreur base de données principale: {e}")

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

# Routes supplémentaires pour le dashboard React
if AUTH_AVAILABLE:
    @app.get("/api/auth/me")
    async def get_current_user_info(current_user: User = Depends(get_current_user)):
        return {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email
        }
    
    @app.get("/api/sessions")
    async def get_sessions(current_user: User = Depends(get_current_user)):
        # Retourner des données de test pour l'instant
        return [
            {
                "id": 1,
                "name": "Session Test 1",
                "date": "2024-01-15",
                "draws": [1, 5, 12, 23, 34],
                "status": "active"
            },
            {
                "id": 2,
                "name": "Session Test 2",
                "date": "2024-01-14",
                "draws": [3, 8, 15, 27, 41],
                "status": "completed"
            }
        ]
    
    @app.get("/api/analytics")
    async def get_analytics(current_user: User = Depends(get_current_user)):
        return {
            "stats": {
                "totalSessions": 45,
                "totalDraws": 1250,
                "winRate": 12.5,
                "avgAccuracy": 78.3
            },
            "trends": [
                {"date": "2024-01-01", "sessions": 5, "accuracy": 75},
                {"date": "2024-01-02", "sessions": 8, "accuracy": 82},
                {"date": "2024-01-03", "sessions": 6, "accuracy": 78},
                {"date": "2024-01-04", "sessions": 12, "accuracy": 85},
                {"date": "2024-01-05", "sessions": 9, "accuracy": 80}
            ],
            "frequency": [
                {"number": 1, "frequency": 25},
                {"number": 5, "frequency": 32},
                {"number": 12, "frequency": 28},
                {"number": 23, "frequency": 35},
                {"number": 34, "frequency": 22}
            ]
        }
    
    @app.get("/api/ml/predictions")
    async def get_ml_predictions(current_user: User = Depends(get_current_user)):
        return {
            "predictions": [
                {
                    "id": 1,
                    "numbers": [7, 14, 21, 28, 35],
                    "confidence": 85,
                    "model": "LSTM",
                    "date": "2024-01-15",
                    "status": "pending"
                },
                {
                    "id": 2,
                    "numbers": [3, 12, 19, 26, 42],
                    "confidence": 78,
                    "model": "Random Forest",
                    "date": "2024-01-14",
                    "status": "verified"
                }
            ],
            "accuracy": 82.5
        }
    
    @app.post("/api/ml/generate")
    async def generate_ml_prediction(current_user: User = Depends(get_current_user)):
        import random
        return {
            "id": random.randint(100, 999),
            "numbers": sorted(random.sample(range(1, 50), 5)),
            "confidence": random.randint(70, 95),
            "model": "LSTM",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "status": "pending"
        }

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
