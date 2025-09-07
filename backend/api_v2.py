"""
API principale EazzyCalculator
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from db_manager import DatabaseManager
import uvicorn

# Contexte de l'application pour gérer les connexions aux bases de données
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: créer le gestionnaire de base de données
    app.state.db = DatabaseManager()
    yield
    # Shutdown: fermer les connexions
    app.state.db.close_all()

# Créer l'application FastAPI
app = FastAPI(
    title="EazzyCalculator API V2",
    description="API améliorée pour l'analyse et la gestion des combinaisons de loterie",
    version="2.0.0",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route de base
@app.get("/")
async def root():
    """Route principale de l'API"""
    return {
        "message": "Bienvenue sur l'API EazzyCalculator V2",
        "version": "2.0.0",
        "status": "active"
    }

# Route de santé
@app.get("/health")
async def health_check():
    """Vérification de l'état de l'API et des connexions aux bases de données"""
    try:
        with DatabaseManager() as db:
            pg_tables = db.check_postgres_tables()
            sqlite_tables = db.check_sqlite_tables()
            
            return {
                "status": "healthy",
                "version": "2.0.0",
                "databases": {
                    "postgresql": {
                        "status": "connected",
                        "tables": pg_tables,
                        "tables_count": len(pg_tables)
                    },
                    "sqlite": {
                        "status": "connected",
                        "tables": sqlite_tables,
                        "tables_count": len(sqlite_tables)
                    }
                }
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur de connexion aux bases de données: {str(e)}"
        )

# Routes pour les combinaisons
@app.get("/combinations/chips")
async def get_chips():
    """Obtenir la liste des chips disponibles"""
    try:
        with DatabaseManager() as db:
            cursor = db.sqlite_conn.cursor()
            cursor.execute("SELECT DISTINCT chip FROM combinations ORDER BY chip")
            chips = [row[0] for row in cursor.fetchall()]
            return {"chips": chips, "total": len(chips)}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des chips: {str(e)}"
        )

@app.get("/combinations/chip/{chip_id}")
async def get_chip_combinations(chip_id: int):
    """Obtenir les combinaisons pour un chip spécifique"""
    try:
        with DatabaseManager() as db:
            cursor = db.sqlite_conn.cursor()
            cursor.execute("SELECT * FROM combinations WHERE chip = ?", (chip_id,))
            combinations = [dict(row) for row in cursor.fetchall()]
            return {
                "chip": chip_id,
                "combinations": combinations,
                "total": len(combinations)
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des combinaisons: {str(e)}"
        )

# Routes pour les analyses PostgreSQL
@app.get("/analysis/draws")
async def get_recent_draws(limit: int = 10):
    """Obtenir les tirages récents"""
    try:
        with DatabaseManager() as db:
            with db.pg_conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM lottery_draws 
                    ORDER BY draw_date DESC 
                    LIMIT %s
                """, (limit,))
                columns = [desc[0] for desc in cursor.description]
                draws = [dict(zip(columns, row)) for row in cursor.fetchall()]
                return {"draws": draws, "total": len(draws)}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des tirages: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run("api_v2:app", host="0.0.0.0", port=8000, reload=True)
