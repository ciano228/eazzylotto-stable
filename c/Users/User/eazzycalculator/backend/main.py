from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import uvicorn

app = FastAPI(title="Katula Main API")

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
        
        cursor.execute("""
            SELECT chip_id, univers, ligne, colonne, petique, chip, forme, denomination, granque_name, tome
            FROM table_de_katula 
            WHERE univers = %s 
            ORDER BY chip_id
        """, (universe,))
        
        results = cursor.fetchall()
        
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

@app.get("/api/denomination/{universe}/{denomination}")
async def get_denomination(universe: str, denomination: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT num1, num2, alpha_ranking, univers, denomination
            FROM table_de_katula 
            WHERE univers = %s AND denomination = %s
        """, (universe, denomination))
        
        results = cursor.fetchall()
        
        details = []
        for row in results:
            num1, num2, alpha_ranking, univers, denom = row
            details.append({
                "num1": num1,
                "num2": num2,
                "alpha_ranking": alpha_ranking,
                "univers": univers,
                "denomination": denom
            })

        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "details": details
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/granque-tome/{universe}")
async def get_granque_tome(universe: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT granque_name 
            FROM table_de_katula 
            WHERE univers = %s AND granque_name IS NOT NULL
        """, (universe,))
        granques = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("""
            SELECT DISTINCT tome 
            FROM table_de_katula 
            WHERE univers = %s AND tome IS NOT NULL
        """, (universe,))
        tomes = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "granque_data": {g: [] for g in granques},
            "tome_data": {t: [] for t in tomes}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)