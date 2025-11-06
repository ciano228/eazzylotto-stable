#!/usr/bin/env python3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/analytics/katula/table/{universe}")
async def get_katula_table(universe: str):
    return {"status": "success", "universe": universe, "chips": {}}

@app.get("/api/analytics/katula/formes/{universe}")
async def get_katula_formes(universe: str):
    formes = {
        "mundo": ["carre", "triangle", "cercle", "rectangle"],
        "fruity": ["carre", "triangle", "cercle", "rectangle", "losange"],
        "trigga": ["triangle", "losange", "etoile"],
        "roaster": ["cercle", "carre", "rectangle"],
        "sunshine": ["etoile", "cercle", "triangle"]
    }
    return {"formes": formes.get(universe.lower(), ["carre", "triangle", "cercle", "rectangle"])}

@app.get("/api/analytics/katula/chip/{universe}/{chip_number}")
async def get_katula_chip(universe: str, chip_number: int):
    return {
        "chip_number": chip_number,
        "universe": universe,
        "formes_data": {
            "carre": [{"denomination": f"A{chip_number}"}],
            "triangle": [{"denomination": f"B{chip_number}"}],
            "cercle": [{"denomination": f"C{chip_number}"}],
            "rectangle": [{"denomination": f"D{chip_number}"}]
        }
    }

@app.get("/api/analytics/granque-tome/{universe}")
async def get_granque_tome(universe: str):
    return {
        "granque_data": {"Q1": [], "Q2": [], "Q3": [], "Q4": []},
        "tome_data": {"tome1": [], "tome2": [], "tome3": []},
        "denomination_mapping": {}
    }

@app.get("/api/analytics/denomination/{universe}/{denomination}")
async def get_denomination(universe: str, denomination: str):
    return {
        "denomination": denomination,
        "universe": universe,
        "total_occurrences": 1,
        "details": [{"num1": 1, "num2": 2, "alpha_ranking": "a"}]
    }

if __name__ == "__main__":
    print("[KATULA] Serveur simple port 8082")
    print("[API] http://localhost:8082")
    uvicorn.run(app, host="0.0.0.0", port=8082)