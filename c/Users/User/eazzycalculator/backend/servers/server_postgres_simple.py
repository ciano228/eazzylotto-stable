from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from collections import defaultdict
import uvicorn
import psycopg2
import psycopg2.extras
from contextlib import contextmanager

# Local DB config (points to the real PostgreSQL database)
DB_CONFIG = {
    'host': 'localhost',
    'database': 'katooling_main_system',
    'user': 'postgres',
    'password': 'Katulaa_33',
    'port': 5432
}

# Liste des univers autorisés
VALID_UNIVERSES = ['mundo', 'fruity', 'trigga', 'roaster', 'sunshine']


@contextmanager
def get_db_cursor():
    """Context manager yielding a RealDictCursor and closing the connection after use."""
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

app = FastAPI(
    title="Katula PostgreSQL API",
    description="API pour accéder aux données Katula via PostgreSQL",
    version="1.0.0"
)

# Configuration pour le CORS - autoriser toutes les origines
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les origines
    allow_credentials=True,
    allow_methods=["*"],  # Autorise toutes les méthodes
    allow_headers=["*"],  # Autorise tous les headers
)

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

@app.get("/api/health", description="Vérifier l'état de l'API et de la base de données")
async def health():
    """
    Vérifier l'état de santé de l'API et retourner la liste des tables disponibles.
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [record['table_name'] for record in cursor]
            return {"status": "healthy", "tables": tables}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/katula/table", description="Récupérer les données de la table Katula")
async def get_katula_table():
    """
    Récupérer les 1000 dernières entrées de la table Katula.
    """
    try:
        with get_db_cursor() as cursor:
            # Récupération des données de la table
            cursor.execute("""
                SELECT * FROM table_de_katula 
                ORDER BY id DESC 
                LIMIT 1000
            """)
            data = cursor.fetchall()
            
            return {
                "status": "success",
                "data": [dict(row) for row in data]
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving Katula table data: {str(e)}"
        )

@app.get("/api/katula/data", description="Récupérer les données de la table Katula")
async def get_katula_data():
    """
    Récupérer toutes les données de la table Katula avec une limite de 1000 enregistrements.
    """
    try:
        with get_db_cursor() as cursor:
            query = """
            SELECT * FROM table_de_katula 
            ORDER BY id DESC 
            LIMIT 1000
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            return {"status": "success", "data": results}
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving Katula data: {str(e)}"
        )

@app.get("/api/quintuple-shots/{universe}", description="Récupérer tous les quintuple-shots d'un univers")
async def get_quintuple_shots(universe: str):
    """
    Récupérer tous les quintuple-shots d'un univers avec leurs fréquences.
    """
    universe = validate_universe(universe)
    try:
        with get_db_cursor() as cursor:
            query = """
            SELECT DISTINCT grandeTome, COUNT(*) as frequency
            FROM table_de_katula
            WHERE univers = %s AND grandeTome IS NOT NULL AND grandeTome != ''
            GROUP BY grandeTome ORDER BY frequency DESC
            """

            cursor.execute(query, (universe,))
            results = cursor.fetchall()

            shots_data = [
                {'shot': record['grandeTome'], 'frequency': record['frequency']}
                for record in results
            ]

            return {
                'universe': universe,
                'shots': [s['shot'] for s in shots_data],
                'shots_with_frequency': shots_data
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving quintuple-shots data: {str(e)}"
        )

@app.get("/api/katula/formes/{universe}", description="Récupérer les formes d'un univers")
@app.get("/api/formes/{universe}")  # Alias pour la compatibilité
async def get_universe_formes(universe: str):
    """
    Récupérer les formes distinctes et leurs fréquences dans un univers.
    """
    universe = validate_universe(universe)
    try:
        with get_db_cursor() as cursor:
            query = """
            SELECT DISTINCT forme, COUNT(*) as frequency
            FROM table_de_katula
            WHERE univers = %s AND forme IS NOT NULL AND forme != ''
            GROUP BY forme
            ORDER BY frequency DESC
            """

            cursor.execute(query, (universe,))
            results = cursor.fetchall()

            formes_data = [
                {"forme": record['forme'], "frequency": record['frequency']} 
                for record in results
            ]

            return {
                "status": "success",
                "universe": universe,
                "formes": formes_data
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving formes from universe {universe}: {str(e)}"
        )

@app.get("/api/katula/table/{universe}", description="Récupérer les données d'une table d'univers")
async def get_universe_table(universe: str):
    """
    Récupérer la structure et les données d'une table d'univers.
    """
    universe = validate_universe(universe)
    try:
        with get_db_cursor() as cursor:
            # Récupérer les colonnes de la table_de_katula (schéma canonique)
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'table_de_katula'
                ORDER BY ordinal_position
            """)
            columns = [record['column_name'] for record in cursor.fetchall()]

            # Récupérer les données pour cet univers
            query = """
            SELECT * FROM table_de_katula
            WHERE univers = %s
            ORDER BY chip_id DESC
            LIMIT 1000
            """

            cursor.execute(query, (universe,))
            results = cursor.fetchall()

            return {
                "status": "success",
                "universe": universe,
                "columns": columns,
                "data": [dict(row) for row in results]
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving data from universe {universe}: {str(e)}"
        )

@app.get("/api/formes/real/{universe}", description="Récupérer toutes les formes d'un univers")
async def get_formes(universe: str):
    """
    Récupérer toutes les formes d'un univers avec leurs fréquences, classées en formes simples et composites.
    """
    universe = validate_universe(universe)
    try:
        with get_db_cursor() as cursor:
            query = """
            SELECT DISTINCT forme, COUNT(*) as frequency
            FROM table_de_katula
            WHERE univers = %s AND forme IS NOT NULL AND forme != ''
            GROUP BY forme ORDER BY frequency DESC
            """

            cursor.execute(query, (universe,))
            results = cursor.fetchall()

            formes_data = []
            simples = []
            composites = []

            for record in results:
                forme = record['forme']
                frequency = record['frequency']
                formes_data.append({'forme': forme, 'frequency': frequency})

                if '-' in (forme or ''):
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
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving formes data: {str(e)}"
        )

@app.get("/api/formes/real/{universe}/chip/{chip_number}", description="Récupérer les formes pour un chip spécifique")
async def get_chip_formes(universe: str, chip_number: str):
    """
    Récupérer toutes les formes et leurs dénominations pour un chip spécifique dans un univers donné.
    """
    try:
        universe = validate_universe(universe)
        with get_db_cursor() as cursor:
            # chip_number is expected to be a label like 'chip1' or 'chip12'
            chip_label = str(chip_number)
            query = """
            SELECT forme, denomination, COUNT(*) as frequency
            FROM table_de_katula
            WHERE univers = %s AND chip = %s AND forme IS NOT NULL AND forme != ''
            GROUP BY forme, denomination ORDER BY frequency DESC
            """

            cursor.execute(query, (universe, chip_label))
            results = cursor.fetchall()

            formes_data = defaultdict(list)
            for record in results:
                formes_data[record['forme']].append({
                    'denomination': record.get('denomination'),
                    'frequency': record.get('frequency', 0)
                })

            return {
                'universe': universe,
                'chip': chip_label,
                'formes_data': dict(formes_data),
                'total_items': sum(len(items) for items in formes_data.values())
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chip formes: {str(e)}")

if __name__ == "__main__":
    print("Serveur PostgreSQL demarré sur http://localhost:8081")
    uvicorn.run(app, host="0.0.0.0", port=8081)