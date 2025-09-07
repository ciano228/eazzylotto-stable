from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

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

app = FastAPI(title="Katula API", version="1.0.0")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
