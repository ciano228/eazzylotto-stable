from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import uvicorn

app = FastAPI(title="Simple Katula API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_CONFIG = {
    'host': 'localhost',
    'database': 'katooling_main_system',
    'user': 'postgres',
    'password': 'Katulaa_33',
    'port': 5432
}

@app.get("/api/health")
async def health():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM table_de_katula")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return {"status": "healthy", "total_rows": count}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/katula/matrix/{universe}")
async def get_katula_matrix(universe: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Requête simple
        cursor.execute("""
            SELECT chip_id, univers, ligne, colonne, petique, chip, forme, denomination, granque_name, tome
            FROM table_de_katula 
            WHERE univers = %s 
            ORDER BY chip_id
            LIMIT 48
        """, (universe,))
        
        results = cursor.fetchall()
        
        # Organiser en matrice 8x6
        matrix = {}
        chips = {}
        
        for row in results:
            chip_id, univers, ligne, colonne, petique, chip, forme, denomination, granque_name, tome = row
            
            chips[chip_id] = {
                'chip_number': chip_id,
                'ligne': ligne,
                'colonne': colonne,
                'petique': petique,
                'forme': forme,
                'denomination': denomination,
                'granque_name': granque_name,
                'tome': tome,
                'formes': {forme: denomination} if forme else {}
            }
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "universe": universe,
            "chips": chips,
            "total_chips": len(chips)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)