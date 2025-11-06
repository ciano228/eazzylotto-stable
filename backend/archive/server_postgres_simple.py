from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import psycopg2
from collections import defaultdict
import uvicorn
from pathlib import Path

app = FastAPI(title="Katula PostgreSQL API")

# Configuration pour le CORS - autoriser toutes les origines
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les origines
    allow_credentials=True,
    allow_methods=["*"],  # Autorise toutes les méthodes
    allow_headers=["*"],  # Autorise tous les headers
)

DB_CONFIG = {
    'host': 'localhost',
    'database': 'katooling_main_system',
    'user': 'postgres',
    'password': 'Katulaa_33',
    'port': 5432
}

# Liste des univers autorisés
VALID_UNIVERSES = ['mundo', 'fruity', 'trigga', 'roaster', 'sunshine']

def validate_universe(universe: str):
    """Valide le nom de l'univers"""
    if universe not in VALID_UNIVERSES:
        raise HTTPException(
            status_code=400,
            detail=f"Univers invalide. Les univers valides sont : {', '.join(VALID_UNIVERSES)}"
        )
    return universe

async def check_table_exists(cursor, table_name: str):
    """Vérifie si une table existe"""
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = %s
        );
    """, (table_name,))
    exists = cursor.fetchone()[0]
    if not exists:
        raise HTTPException(
            status_code=404,
            detail=f"La table {table_name} n'existe pas dans la base de données"
        )

@app.get("/api/health")
async def health():
    try:
        # Test de connexion à la base de données
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Liste toutes les tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        tables = [table[0] for table in cursor.fetchall()]
        
        return {"status": "healthy", "tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/katula/table")
async def get_katula_table():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Récupération des données de la table
        cursor.execute("""
            SELECT * FROM table_de_katula 
            ORDER BY id DESC 
            LIMIT 1000
        """)
        
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        data = [dict(zip(columns, row)) for row in results]
        
        cursor.close()
        conn.close()
        
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
        conn.close()
        return {
            "status": "ok", 
            "message": "PostgreSQL API", 
            "connected": True,
            "tables": tables
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "connected": False
        }

@app.get("/api/katula/data")
async def get_katula_data():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        query = """
        SELECT * FROM table_de_katula 
        ORDER BY id DESC 
        LIMIT 1000
        """
        
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        
        data = [dict(zip(columns, row)) for row in results]
        cursor.close()
        conn.close()
        
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/katula/enhanced/{universe}")
async def get_enhanced_universe(universe: str):
    universe = validate_universe(universe)
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Récupérer les données de base
        query = f"""
        SELECT * FROM {universe}
        ORDER BY id DESC 
        LIMIT 1000
        """
        
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        
        # Calculer les statistiques
        stats_query = f"""
        SELECT 
            COUNT(*) as total_entries,
            COUNT(DISTINCT forme) as unique_formes,
            COUNT(DISTINCT chip) as unique_chips
        FROM {universe}
        """
        
        cursor.execute(stats_query)
        stats = dict(zip(['total_entries', 'unique_formes', 'unique_chips'], cursor.fetchone()))
        
        data = [dict(zip(columns, row)) for row in results]
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "universe": universe,
            "data": data,
            "universe_stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/katula/formes/{universe}")
@app.get("/api/formes/{universe}")  # Alias pour la compatibilité
async def get_universe_formes(universe: str):
    universe = validate_universe(universe)
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        query = f"""
        SELECT DISTINCT forme, COUNT(*) as frequency
        FROM {universe}
        WHERE forme IS NOT NULL AND forme != ''
        GROUP BY forme
        ORDER BY frequency DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        formes_data = [{"forme": forme, "frequency": freq} for forme, freq in results]
        
        return {
            "status": "success",
            "universe": universe,
            "formes": formes_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/katula/table/{universe}")
async def get_universe_table(universe: str):
    universe = validate_universe(universe)
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Récupérer les colonnes de la table
        cursor.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{universe}'
            ORDER BY ordinal_position
        """)
        columns = [row[0] for row in cursor.fetchall()]
        
        # Récupérer les données
        query = f"""
        SELECT * FROM {universe}
        ORDER BY id DESC
        LIMIT 1000
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Convertir en liste de dictionnaires
        data = [dict(zip(columns, row)) for row in results]
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "universe": universe,
            "columns": columns,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/formes/real/{universe}")
async def get_formes(universe: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        query = f"""
        SELECT DISTINCT forme, COUNT(*) as frequency
        FROM {universe} 
        WHERE forme IS NOT NULL AND forme != ''
        GROUP BY forme ORDER BY frequency DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        formes_data = []
        simples = []
        composites = []
        
        for forme, frequency in results:
            formes_data.append({'forme': forme, 'frequency': frequency})
            if '-' in forme:
                composites.append(forme)
            else:
                simples.append(forme)
        
        return {
            'universe': universe,
            'formes': [f['forme'] for f in formes_data],
            'formes_with_frequency': formes_data,
            'simples': simples,
            'composites': composites
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/formes/real/{universe}/chip/{chip_number}")
async def get_chip_formes(universe: str, chip_number: int):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        query = f"""
        SELECT forme, denomination, COUNT(*) as frequency
        FROM {universe} 
        WHERE chip = %s AND forme IS NOT NULL AND forme != ''
        GROUP BY forme, denomination ORDER BY frequency DESC
        """
        
        cursor.execute(query, (str(chip_number),))
        results = cursor.fetchall()
        conn.close()
        
        formes_data = defaultdict(list)
        for forme, denomination, frequency in results:
            formes_data[forme].append({
                'denomination': denomination,
                'frequency': frequency
            })
        
        return {
            'universe': universe,
            'chip': chip_number,
            'formes_data': dict(formes_data),
            'total_items': sum(len(items) for items in formes_data.values())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
from fastapi import Request
from fastapi.responses import JSONResponse

@app.post("/api/kiro/chat")
async def kiro_chat(request: Request):
    data = await request.json()
    message = data.get("message", "")

    generated_response = f"Réponse à: {message}"
    model_used = "katula-gpt"  # ✅ adapte au nom de ton agent

    return JSONResponse(
        content={
            "status": "success",           # ✅ requis par Kiro
            "model": model_used,           # ✅ requis
            "type": "text",                # ✅ pour affichage correct
            "streaming": True,             # ✅ active le mode streaming
            "response": generated_response,
            "tokens": len(generated_response.split())
        },
        media_type="application/json; charset=utf-8"  # ✅ encodage explicite
    )

# Servir les fichiers statiques du frontend (à la fin pour ne pas interférer avec les routes API)
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")

if __name__ == "__main__":
    print("Serveur PostgreSQL demarré sur http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)