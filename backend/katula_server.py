from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.katula_table_service import KatulaTableService

app = FastAPI(title="Katula API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Katula API Running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/katula/table/{universe}")
def get_katula_table(universe: str):
    """
    Retourne la structure de base de la Table de Katula pour un univers donné
    """
    try:
        table = KatulaTableService.create_katula_table(universe)
        return table
    except Exception as e:
        return {"error": str(e)}
