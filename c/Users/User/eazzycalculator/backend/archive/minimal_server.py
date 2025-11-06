from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.services.katula_table_service import KatulaTableService
from sqlalchemy.orm import Session
from app.database.connection import get_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Katula API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/katula/table/{universe}")
async def get_katula_table(universe: str):
    """Retourne la structure de la table de Katula pour un univers"""
    return KatulaTableService.create_katula_table(universe)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
