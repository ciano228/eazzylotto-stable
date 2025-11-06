from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
import random

class KatulaTableService:
    """
    Service pour la gestion de la Table de Katula - Matrice géométrique 8x6
    """
    MATRIX_ROWS = 8
    MATRIX_COLS = 6
    TOTAL_CHIPS = 48
    
    @staticmethod
    def create_katula_table(universe: str = "mundo") -> Dict[str, Any]:
        """Crée la structure de base de la Table de Katula"""
        table = {
            "universe": universe,
            "name": f"table_de_katula_{universe}",
            "dimensions": {
                "rows": KatulaTableService.MATRIX_ROWS,
                "columns": KatulaTableService.MATRIX_COLS,
                "total_chips": KatulaTableService.TOTAL_CHIPS
            },
            "matrix": [],
            "chip_positions": {},
            "geometric_attributes": {}
        }
        
        # Créer la matrice 8x6
        chip_counter = 1
        for row in range(1, KatulaTableService.MATRIX_ROWS + 1):
            matrix_row = []
            for col in range(1, KatulaTableService.MATRIX_COLS + 1):
                chip_id = f"chip{chip_counter}"
                cell = {
                    "chip_id": chip_id,
                    "chip_number": chip_counter,
                    "row": row,
                    "column": col,
                    "position": f"R{row}C{col}"
                }
                matrix_row.append(cell)
                table["chip_positions"][chip_id] = cell
                chip_counter += 1
            table["matrix"].append(matrix_row)
        
        return table

# Données de démonstration pour les formes et les chips
FORME_TYPES = ['carre', 'triangle', 'cercle', 'rectangle']

def generate_chip_data(chip_number: int, universe: str) -> dict:
    """Génère des données de démonstration pour un chip"""
    return {
        "chip_id": f"chip{chip_number}",
        "chip_number": chip_number,
        "universe": universe,
        "formes_data": {
            forme: [
                {
                    "denomination": f"{forme.capitalize()} {chip_number}-{i+1}",
                    "valeur": (chip_number + i) % 20 + 1,
                    "position": f"L{((chip_number-1) // 6) + 1}C{((chip_number-1) % 6) + 1}",
                    "couleur": "#" + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)])
                } for i in range(2)  # 2 items par forme pour la démo
            ] for forme in FORME_TYPES
        }
    }

def generate_granque_tome_data(universe: str) -> dict:
    """Génère des données de démonstration pour les granques et tomes"""
    return {
        "granque_data": {
            "Q1": [
                {"denomination": f"Granque Q1-{i+1}", "chip": i+1, "valeur": (i % 10) + 1}
                for i in range(1, 13)  # 12 chips par granque
            ],
            "Q2": [
                {"denomination": f"Granque Q2-{i+1}", "chip": i+13, "valeur": ((i+12) % 10) + 1}
                for i in range(1, 13)
            ],
            "Q3": [
                {"denomination": f"Granque Q3-{i+1}", "chip": i+25, "valeur": ((i+24) % 10) + 1}
                for i in range(1, 13)
            ],
            "Q4": [
                {"denomination": f"Granque Q4-{i+1}", "chip": i+37, "valeur": ((i+36) % 10) + 1}
                for i in range(1, 13)
            ]
        },
        "tome_data": {
            "T1": [
                {"denomination": f"Tome T1-{i+1}", "chip": (i*4) % 48 + 1, "valeur": (i % 10) + 1}
                for i in range(12)  # 12 entrées par tome
            ],
            "T2": [
                {"denomination": f"Tome T2-{i+1}", "chip": (i*4 + 1) % 48 + 1, "valeur": ((i+1) % 10) + 1}
                for i in range(12)
            ],
            "T3": [
                {"denomination": f"Tome T3-{i+1}", "chip": (i*4 + 2) % 48 + 1, "valeur": ((i+2) % 10) + 1}
                for i in range(12)
            ],
            "T4": [
                {"denomination": f"Tome T4-{i+1}", "chip": (i*4 + 3) % 48 + 1, "valeur": ((i+3) % 10) + 1}
                for i in range(12)
            ]
        },
        "denomination_mapping": {
            f"{forme}-{i+1}": {
                "type": forme,
                "valeur": (i % 10) + 1,
                "couleur": "#" + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)])
            }
            for forme in FORME_TYPES
            for i in range(12)  # 12 dénominations par forme
        }
    }

app = FastAPI(title="Katula API", version="1.0.0")

# Configuration CORS
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

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.get("/health")
def health_check_legacy():
    return {"status": "healthy"}

@app.get("/api/katula/table/{universe}")
def get_katula_table(universe: str):
    try:
        table = KatulaTableService.create_katula_table(universe)
        return table
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/katula/formes/{universe}")
async def get_formes(universe: str):
    try:
        return {
            "formes": FORME_TYPES,
            "universe": universe,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/katula/chip/{universe}/{chip_number}")
async def get_chip_data(universe: str, chip_number: int):
    try:
        if chip_number < 1 or chip_number > 48:
            raise HTTPException(status_code=400, detail="Le numéro de chip doit être entre 1 et 48")
        
        chip_data = generate_chip_data(chip_number, universe)
        return {
            **chip_data,
            "status": "success"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/granque-tome/{universe}")
async def get_granque_tome(universe: str):
    try:
        granque_tome_data = generate_granque_tome_data(universe)
        return {
            **granque_tome_data,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
