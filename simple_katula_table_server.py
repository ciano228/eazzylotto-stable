"""
Serveur Simple pour Table de Katula
Test rapide des services de table Katula
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Ajouter le chemin backend au PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

app = FastAPI(
    title="Table de Katula - Test Simple",
    description="API de test pour la table de Katula",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Page d'accueil"""
    return {
        "message": "Table de Katula - Serveur de Test",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "test_structure": "/test-structure",
            "test_postgres": "/test-postgres"
        }
    }

@app.get("/health")
async def health():
    """Vérification de santé"""
    return {"status": "healthy", "service": "katula-table-simple"}

@app.get("/test-structure")
async def test_structure():
    """Test de la structure de base"""
    try:
        # Structure de base 8x6
        matrix = []
        chip_counter = 1
        
        for row in range(1, 9):  # 8 lignes
            matrix_row = []
            for col in range(1, 7):  # 6 colonnes
                matrix_row.append({
                    "chip_number": chip_counter,
                    "position": f"R{row}C{col}",
                    "row": row,
                    "column": col
                })
                chip_counter += 1
            matrix.append(matrix_row)
        
        return {
            "success": True,
            "dimensions": {"rows": 8, "columns": 6, "total_chips": 48},
            "matrix": matrix
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/test-postgres")
async def test_postgres():
    """Test de connexion PostgreSQL"""
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host='localhost',
            database='katooling_main_system',
            user='postgres',
            password='Katulaa_33',
            port=5432
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cursor.fetchall()
        
        conn.close()
        
        return {
            "success": True,
            "database": "katooling_main_system",
            "tables": [table[0] for table in tables]
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/test-universe/{universe}")
async def test_universe_data(universe: str):
    """Test des données d'un univers"""
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host='localhost',
            database='katooling_main_system',
            user='postgres',
            password='Katulaa_33',
            port=5432
        )
        
        cursor = conn.cursor()
        
        # Vérifier si la table existe
        cursor.execute(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = '{universe}'
            )
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            conn.close()
            return {"error": f"Table '{universe}' n'existe pas"}
        
        # Récupérer quelques données
        cursor.execute(f"SELECT chip, forme, denomination, COUNT(*) as count FROM {universe} GROUP BY chip, forme, denomination LIMIT 10")
        sample_data = cursor.fetchall()
        
        conn.close()
        
        return {
            "success": True,
            "universe": universe,
            "table_exists": table_exists,
            "sample_data": [
                {
                    "chip": row[0],
                    "forme": row[1],
                    "denomination": row[2],
                    "count": row[3]
                } for row in sample_data
            ]
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("Demarrage du serveur simple Table de Katula...")
    print("API: http://localhost:8004/")
    print("Health: http://localhost:8004/health")
    print("Test Structure: http://localhost:8004/test-structure")
    print("Test PostgreSQL: http://localhost:8004/test-postgres")
    
    uvicorn.run(
        "simple_katula_table_server:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )