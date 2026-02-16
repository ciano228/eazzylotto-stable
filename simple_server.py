"""
Serveur simple pour katula-dynamic.html
"""
import http.server
import socketserver
import threading
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import uvicorn
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

# Configuration de la base de données
def get_db_connection():
    """Crée une connexion à la base de données PostgreSQL."""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME', 'katooling_main_system'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'Katulaa_33'),
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432')
        )
        return conn
    except Exception as e:
        logger.error(f"Erreur de connexion à la base de données: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de connexion à la base de données: {e}")

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import des services katooling
try:
    from backend.add_katooling_routes import add_katooling_routes
    KATOOLING_AVAILABLE = True
except ImportError:
    KATOOLING_AVAILABLE = False
    print("Services katooling non disponibles")

# Serveur API FastAPI
api_app = FastAPI()
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from fastapi import Request
from fastapi.responses import JSONResponse

# Service unifié basé sur unified_sessions / unified_draws
from backend.unified_db_session_service import UnifiedDBSessionService

unified_db_session_service = UnifiedDBSessionService()

# Intégration des routes Analytics pour Katula (Support Temporal Analysis)
try:
    # Ajustement des imports selon le path
    try:
        from backend.app.routes.chip_structure import router as chip_structure_router
        from backend.app.routes.temporal_analysis import router as temporal_analysis_router
    except ImportError:
        # Fallback si backend est la racine
        from app.routes.chip_structure import router as chip_structure_router
        from app.routes.temporal_analysis import router as temporal_analysis_router
    
    api_app.include_router(chip_structure_router, prefix="/api/analytics", tags=["analytics"])
    api_app.include_router(temporal_analysis_router, prefix="/api/analytics", tags=["analytics"])
    print("✅ Routes Analytics Katula ajoutées sur /api/analytics")
except Exception as e:
    print(f"⚠️ Erreur ajout routes Analytics: {e}")

@api_app.post("/api/kiro/chat")
async def kiro_chat(request: Request):
    data = await request.json()
    message = data.get("message", "")

    generated_response = f"Réponse à: {message}"
    model_used = "katula-gpt"

    return JSONResponse(
        content={
            "status": "success",
            "model": model_used,
            "type": "text",
            "streaming": True,
            "response": generated_response,
            "tokens": len(generated_response.split())
        },
        media_type="application/json; charset=utf-8"
    )

@api_app.get("/api/universe/{universe}/formes")
async def get_universe_formes(universe: str):
    try:
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        
        config = service.get_universe_config(universe)
        return {
            "status": "success",
            "universe": universe,
            "formes": config.forms,
            "total_formes": len(config.forms),
            "type": config.type.value,
            "description": config.description
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}


@api_app.get("/api/katula/tomes/{univers}")
async def get_universe_tomes(univers: str):
    """Récupérer la liste des chips par tome pour un univers donné.

    Structure retournée :
    {
        "univers": "mundo",
        "tomes": {
            "tome 1": [1, 2, ...],
            "tome 2": [...]
        }
    }
    """
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT chip, tome
                FROM combinations
                WHERE univers = %s
                  AND tome IS NOT NULL
                ORDER BY tome, chip
                """,
                (univers,)
            )

            rows = cur.fetchall()

        tomes_map = {}
        for row in rows:
            tome_val = row.get("tome")
            chip_val = row.get("chip")
            if tome_val is None or chip_val is None:
                continue
            # Normaliser la clé de tome en chaîne
            tome_key = str(tome_val)
            tomes_map.setdefault(tome_key, []).append(int(chip_val))

        return {
            "status": "success",
            "univers": univers,
            "tomes": tomes_map
        }

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des tomes pour {univers}: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur récupération tomes: {e}")


@api_app.get("/api/draws/real/{univers}")
async def get_real_draws(univers: str, date_start: str, date_end: str):
    """Retourner les tirages réels pour un univers donné sur une plage de dates.

    Les données proviennent de la table unified_draws.
    La structure retournée est du type :
    {
        "status": "success",
        "univers": "mundo",
        "date_start": "YYYY-MM-DD",
        "date_end": "YYYY-MM-DD",
        "draws": [
            {
                "draw_number": ..., 
                "lottery_name": ..., 
                "draw_date": "YYYY-MM-DD",
                "winning_numbers": "..."
            },
            ...
        ]
    }
    """
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT 
                    draw_number,
                    lottery_name,
                    draw_date,
                    winning_numbers
                FROM unified_draws
                WHERE univers = %s
                  AND draw_date BETWEEN %s AND %s
                ORDER BY draw_date, draw_number
                """,
                (univers, date_start, date_end)
            )

            rows = cur.fetchall()

        return {
            "status": "success",
            "univers": univers,
            "date_start": date_start,
            "date_end": date_end,
            "draws": rows,
        }

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des tirages pour {univers}: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur récupération tirages: {e}")


@api_app.get("/api/draws/sessions")
async def list_sessions():
    """Lister les sessions de tirages enregistrées dans unified_sessions.

    Structure retournée :
    {
        "status": "success",
        "sessions": [
            {
                "session_uuid": "...",
                "name": "...",
                "univers": "mundo",
                "total_draws": 120,
                "created_at": "YYYY-MM-DD ..."
            },
            ...
        ]
    }
    """
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT 
                    session_uuid,
                    name,
                    univers,
                    total_draws,
                    created_at
                FROM unified_sessions
                ORDER BY created_at DESC
                """
            )

            rows = cur.fetchall()

        return {
            "status": "success",
            "sessions": rows,
        }

    except Exception as e:
        logger.error(f"Erreur lors du listing des sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur récupération sessions: {e}")


# === UNIFIED SESSION ENDPOINTS (utilisés par smart-input & analyses) ===

@api_app.post("/api/unified/session")
async def create_unified_session(payload: dict):
    """Créer une nouvelle session dans unified_sessions.

    Le payload provient de smart-input.html et ressemble à :
    {
        "name": "Session Janvier 2025",
        "description": "...",
        "lottery_type": "Loto Français",
        "numbers_per_draw": 6,
        "total_draws": 21,
        "number_range": "1-90",
        "start_date": "2025-01-01",
        "schedule": [ { "day": 0, "name": "Loto Lundi", "id": "..." }, ... ]
    }
    Pour l'instant on enregistre surtout les métadonnées de session dans unified_sessions.
    Les tirages détaillés pourront être alimentés ensuite via ETL ou endpoints dédiés.
    """
    try:
        # Tolérance : accepter plusieurs variantes de nom, ou générer un nom par défaut
        raw_name = payload.get("name") or payload.get("session_name") or payload.get("session")
        if raw_name is None or str(raw_name).strip().lower() in ("", "undefined", "null"):
            from datetime import datetime
            name = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        else:
            name = str(raw_name).strip()

        description = payload.get("description") or ""
        lottery_type = payload.get("lottery_type") or "standard"
        numbers_per_draw = int(payload.get("numbers_per_draw") or 5)
        total_draws = int(payload.get("total_draws") or 0)

        # Plage de numéros au format "min-max"
        number_range = payload.get("number_range") or "1-90"
        try:
            range_min_str, range_max_str = str(number_range).split("-")
            number_range_min = int(range_min_str)
            number_range_max = int(range_max_str)
        except Exception:
            number_range_min, number_range_max = 1, 90

        # Construire un planning de tirages à partir du planning hebdo optionnel
        raw_schedule = payload.get("schedule") or []
        schedule = []
        if isinstance(raw_schedule, list) and raw_schedule:
            # Ordonner par jour puis par nom pour avoir un ordre stable
            try:
                sorted_items = sorted(
                    raw_schedule,
                    key=lambda x: (int(x.get("day", 0)), str(x.get("name", "")))
                )
            except Exception:
                sorted_items = raw_schedule

            draw_number = 1
            for item in sorted_items:
                lottery_name = item.get("name") or f"Tirage {draw_number}"
                schedule.append({
                    "draw_number": draw_number,
                    "lottery_name": lottery_name,
                })
                draw_number += 1

            # S'assurer que total_draws est cohérent avec le planning
            if draw_number - 1 > 0:
                total_draws = max(total_draws, draw_number - 1)

        # Préparer les données pour le service unifié basé BD
        session_data = {
            "name": name,
            "description": description,
            "lottery_type": lottery_type,
            "numbers_per_draw": numbers_per_draw,
            "number_range_min": number_range_min,
            "number_range_max": number_range_max,
            "total_draws": total_draws,
            "schedule": schedule,
        }

        # Utiliser le service unifié pour créer la session ET ses tirages vides
        session_uuid = unified_db_session_service.create_session(session_data)

        if not session_uuid:
            raise HTTPException(status_code=500, detail="Impossible de créer la session unifiée")

        return {"status": "success", "session_id": session_uuid}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur création session unifiée: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur création session unifiée: {e}")


@api_app.get("/api/unified/session/sessions")
async def unified_list_sessions():
    """Lister les sessions unifiées (wrapper sur UnifiedDBSessionService)."""
    try:
        sessions = unified_db_session_service.list_all_sessions()
        return {"status": "success", "sessions": sessions}
    except Exception as e:
        logger.error(f"Erreur unified_list_sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur récupération sessions unifiées: {e}")


@api_app.get("/api/unified/session/sessions/active")
async def unified_get_active_session():
    """Récupérer la session active dans unified_sessions.

    On considère la première ligne avec is_active = true, sinon la plus récente.
    """
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Chercher une session active
            cur.execute(
                """
                SELECT session_uuid, name, description, total_draws,
                       numbers_per_draw, number_range_min, number_range_max,
                       created_at, is_active
                FROM unified_sessions
                WHERE is_active = TRUE
                ORDER BY created_at DESC
                LIMIT 1
                """
            )
            row = cur.fetchone()

            # Si aucune active, prendre la plus récente
            if not row:
                cur.execute(
                    """
                    SELECT session_uuid, name, description, total_draws,
                           numbers_per_draw, number_range_min, number_range_max,
                           created_at, is_active
                    FROM unified_sessions
                    ORDER BY created_at DESC
                    LIMIT 1
                    """
                )
                row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Aucune session unifiée trouvée")

        session_data = {
            "id": row["session_uuid"],
            "name": row["name"],
            "description": row["description"],
            "lottery_type": row["name"],  # compatibilité minimale
            "numbers_per_draw": row["numbers_per_draw"],
            "number_range_min": row["number_range_min"],
            "number_range_max": row["number_range_max"],
            "total_draws": row["total_draws"],
            "current_draw": 1,
            "is_active": row["is_active"],
        }

        return {"session": session_data}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur unified_get_active_session: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur récupération session active unifiée: {e}")


@api_app.post("/api/unified/session/sessions/{session_uuid}/activate")
async def unified_activate_session(session_uuid: str):
    """Activer une session unifiée (is_active = true)."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Désactiver toutes les sessions
            cur.execute("UPDATE unified_sessions SET is_active = FALSE")
            # Activer la session cible
            cur.execute(
                "UPDATE unified_sessions SET is_active = TRUE WHERE session_uuid = %s",
                (session_uuid,),
            )
            if cur.rowcount == 0:
                conn.rollback()
                raise HTTPException(status_code=404, detail="Session unifiée non trouvée")

        conn.commit()
        return {"status": "success", "session_id": session_uuid}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur unified_activate_session: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur activation session unifiée: {e}")


@api_app.get("/api/unified/session/{session_uuid}/draws")
async def unified_get_session_draws(session_uuid: str):
    """Récupérer tous les tirages d'une session unifiée depuis unified_draws."""
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT 
                    draw_number,
                    lottery_name,
                    draw_date,
                    winning_numbers,
                    is_completed,
                    cycle_position
                FROM unified_draws
                WHERE session_uuid = %s
                ORDER BY draw_number
                """,
                (session_uuid,),
            )
            rows = cur.fetchall()

        # Adapter au format attendu par displayResultsHistory (id utilisé comme draw_id)
        draws = []
        for row in rows:
            draws.append(
                {
                    "id": row["draw_number"],
                    "draw_number": row["draw_number"],
                    "lottery_name": row["lottery_name"],
                    "draw_date": row["draw_date"].strftime("%Y-%m-%d") if row["draw_date"] else None,
                    "winning_numbers": row["winning_numbers"] or [],
                    "is_completed": row["is_completed"],
                    "cycle_position": row["cycle_position"],
                }
            )

        return {"status": "success", "draws": draws}

    except Exception as e:
        logger.error(f"Erreur unified_get_session_draws: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur récupération tirages unifiés: {e}")


@api_app.get("/api/unified/session/{session_uuid}/draws/{draw_id}")
async def unified_get_draw_detail(session_uuid: str, draw_id: int):
    """Récupérer le détail d'un tirage (draw_id ~= draw_number)."""
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT 
                    draw_number,
                    lottery_name,
                    draw_date,
                    winning_numbers,
                    is_completed
                FROM unified_draws
                WHERE session_uuid = %s AND draw_number = %s
                """,
                (session_uuid, draw_id),
            )
            row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Tirage unifié non trouvé")

        return {
            "id": row["draw_number"],
            "draw_number": row["draw_number"],
            "lottery_name": row["lottery_name"],
            "draw_date": row["draw_date"].strftime("%Y-%m-%d") if row["draw_date"] else None,
            "winning_numbers": row["winning_numbers"] or [],
            "is_completed": row["is_completed"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur unified_get_draw_detail: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur récupération tirage unifié: {e}")


@api_app.put("/api/unified/session/{session_uuid}/draws/{draw_id}")
async def unified_update_draw(session_uuid: str, draw_id: int, payload: dict):
    """Mettre à jour les numéros / la date d'un tirage unifié.

    Utilisé par smart-input.html lors de l'édition d'un tirage existant.
    draw_id est mappé sur draw_number dans unified_draws.
    """
    try:
        numbers = payload.get("numbers") or []
        draw_date_raw = payload.get("draw_date")

        from datetime import datetime
        draw_date = None
        if draw_date_raw:
            # Accepter YYYY-MM-DD ou JJ/MM/AAAA
            try:
                draw_date = datetime.strptime(draw_date_raw, "%Y-%m-%d").date()
            except ValueError:
                try:
                    draw_date = datetime.strptime(draw_date_raw, "%d/%m/%Y").date()
                except ValueError:
                    draw_date = None

        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE unified_draws
                SET winning_numbers = %s,
                    is_completed = TRUE,
                    draw_date = COALESCE(%s, draw_date)
                WHERE session_uuid = %s AND draw_number = %s
                """,
                (numbers, draw_date, session_uuid, draw_id),
            )

            if cur.rowcount == 0:
                conn.rollback()
                raise HTTPException(status_code=404, detail="Tirage unifié non trouvé")

        conn.commit()
        return {"status": "success", "draw_id": draw_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur unified_update_draw: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur mise à jour tirage unifié: {e}")


@api_app.post("/api/unified/session/{session_uuid}/draws/{draw_number}/results")
async def unified_save_draw_results(session_uuid: str, draw_number: int, payload: dict):
    """Créer ou mettre à jour les résultats d'un tirage unifié.

    Comportement proche de SessionService.save_draw_numbers, mais sur unified_draws.
    - Si un enregistrement existe pour (session_uuid, draw_number), on met à jour winning_numbers,
      draw_date (optionnelle) et is_completed = TRUE.
    - Sinon, on insère une nouvelle ligne minimale dans unified_draws.
    """
    try:
        numbers = payload.get("numbers") or []
        draw_date_raw = payload.get("draw_date")

        from datetime import datetime, date

        draw_date: date | None = None
        if draw_date_raw:
            # Accepter YYYY-MM-DD ou JJ/MM/AAAA
            try:
                draw_date = datetime.strptime(draw_date_raw, "%Y-%m-%d").date()
            except ValueError:
                try:
                    draw_date = datetime.strptime(draw_date_raw, "%d/%m/%Y").date()
                except ValueError:
                    draw_date = None

        conn = get_db_connection()
        with conn.cursor() as cur:
            # Vérifier si le tirage existe déjà
            cur.execute(
                """
                SELECT 1 FROM unified_draws
                WHERE session_uuid = %s AND draw_number = %s
                """,
                (session_uuid, draw_number),
            )
            exists = cur.fetchone() is not None

            if exists:
                # Mise à jour
                cur.execute(
                    """
                    UPDATE unified_draws
                    SET winning_numbers = %s,
                        is_completed = TRUE,
                        draw_date = COALESCE(%s, draw_date)
                    WHERE session_uuid = %s AND draw_number = %s
                    """,
                    (numbers, draw_date, session_uuid, draw_number),
                )
            else:
                # Insertion minimale
                lottery_name = payload.get("lottery_name") or f"Tirage {draw_number}"
                cur.execute(
                    """
                    INSERT INTO unified_draws
                        (session_uuid, draw_number, lottery_name, draw_date,
                         winning_numbers, is_completed, cycle_position)
                    VALUES (%s, %s, %s, %s, %s, TRUE, %s)
                    """,
                    (
                        session_uuid,
                        draw_number,
                        lottery_name,
                        draw_date or datetime.utcnow().date(),
                        numbers,
                        0,
                    ),
                )

        conn.commit()
        return {
            "status": "success",
            "session_uuid": session_uuid,
            "draw_number": draw_number,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur unified_save_draw_results: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur sauvegarde tirage unifié: {e}")

@api_app.get("/api/formes/real/{universe}/chip/{chip_id}")
async def get_chip_formes(universe: str, chip_id: str):
    try:
        # Essayer d'abord la vraie BD
        from backend.katula_complete_service import KatulaCompleteService
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        try:
            service = KatulaCompleteService()
            chip_number = int(chip_id.replace('chip', '')) if chip_id.startswith('chip') else int(chip_id)
            result = service.get_chip_compartments(universe, chip_number)
            
            if 'error' not in result and result.get('compartments'):
                formes_data = {}
                for compartment in result.get('compartments', []):
                    forme = compartment['forme']
                    denomination = compartment['denomination']
                    
                    if forme and denomination and denomination != "---":
                        # Gérer les dénominations multiples séparées par '/'
                        formes_data[forme] = [{
                            "denomination": denomination,  # Garder la dénomination complète
                            "frequency": 1,
                            "multiple": '/' in denomination
                        }]
                
                return {
                    "status": "success",
                    "formes_data": formes_data,
                    "total_items": len(result.get('compartments', [])),
                    "source": "database"
                }
        except Exception as db_error:
            print(f"Erreur BD complète: {db_error}")
            import traceback
            traceback.print_exc()
        
        # Fallback sur données de test si BD indisponible
        import random
        random.seed(int(chip_id.replace('chip', '')) if chip_id.startswith('chip') else 1)  # Seed fixe pour consistance
        
        denominations = ["table", "forest", "shoes", "gold", "house", "river", "mountain", "bike", "door", "window", "fire", "rainbow", "flower", "book", "bottle", "umbrella", "hotel", "canoe", "rope", "drum", "mango", "blade", "bed", "spoon", "car", "tree", "phone", "star", "moon", "sun", "cloud", "rain", "snow", "wind", "earth", "water", "air", "light", "dark", "red", "blue", "green", "yellow", "black", "white", "silver", "copper", "iron"]
        formes = ["carre", "triangle", "cercle", "rectangle"]
        
        chip_data = {}
        selected_formes = random.sample(formes, random.randint(2, 4))
        for forme in selected_formes:
            denom = random.choice(denominations) + str(random.randint(1, 9))
            chip_data[forme] = [{"denomination": denom, "frequency": 1}]
        
        return {
            "status": "success",
            "formes_data": chip_data,
            "total_items": len(chip_data),
            "source": "test_data"
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/filter-options/{universe}")
async def get_filter_options(universe: str):
    try:
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        return service.get_filter_options(universe)
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/granques/{universe}")
async def get_granques(universe: str):
    try:
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        
        import psycopg2
        conn = psycopg2.connect(**service.db_config)
        cursor = conn.cursor()
        
        # Récupérer toutes les granques distinctes pour cet univers
        cursor.execute("""
            SELECT granque_name, COUNT(*) as count
            FROM combinations
            WHERE univers = %s AND granque_name IS NOT NULL AND granque_name != ''
            GROUP BY granque_name
            ORDER BY granque_name
        """, (universe,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        granques_list = [row[0] for row in results]
        granques_with_count = [{
            "name": row[0],
            "count": row[1]
        } for row in results]
        
        return {
            "status": "success",
            "granques": granques_with_count,
            "granques_list": granques_list,
            "universe": universe,
            "total_granques": len(granques_with_count)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/tomes/{universe}")
async def get_tomes(universe: str):
    try:
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        
        import psycopg2
        conn = psycopg2.connect(**service.db_config)
        cursor = conn.cursor()
        
        # Récupérer tous les tomes distincts pour cet univers
        cursor.execute("""
            SELECT tome, COUNT(*) as count
            FROM combinations
            WHERE univers = %s AND tome IS NOT NULL AND tome != ''
            GROUP BY tome
            ORDER BY tome
        """, (universe,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        tomes_list = [row[0] for row in results]
        tomes_with_count = [{
            "name": row[0],
            "count": row[1]
        } for row in results]
        
        return {
            "status": "success",
            "tomes": tomes_with_count,
            "tomes_list": tomes_list,
            "universe": universe,
            "total_tomes": len(tomes_with_count)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.post("/api/filter/{universe}")
async def apply_filters(universe: str, filters: dict):
    try:
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        return service.apply_filters(universe, filters)
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/stats/{universe}/{filter_type}/{filter_value}")
async def get_filter_stats(universe: str, filter_type: str, filter_value: str):
    try:
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        
        import urllib.parse
        clean_value = urllib.parse.unquote(filter_value)
        
        import psycopg2
        conn = psycopg2.connect(**service.db_config)
        cursor = conn.cursor()
        
        # Construire la requête selon le type de filtre
        if filter_type == "chip":
            where_clause = "chip = %s"
            params = (universe, clean_value)
        elif filter_type == "ligne":
            ligne_num = int(clean_value)
            start_chip = (ligne_num - 1) * 6 + 1
            end_chip = ligne_num * 6
            chip_list = [f"chip{i}" for i in range(start_chip, end_chip + 1)]
            placeholders = ','.join(['%s'] * len(chip_list))
            where_clause = f"chip IN ({placeholders})"
            params = (universe, *chip_list)
        elif filter_type == "colonne":
            col_num = int(clean_value)
            chip_list = [f"chip{col_num + i*6}" for i in range(8)]
            placeholders = ','.join(['%s'] * len(chip_list))
            where_clause = f"chip IN ({placeholders})"
            params = (universe, *chip_list)
        elif filter_type == "quadrant":
            quadrant_chips = {
                'q1': [1,2,3,7,8,9,13,14,15,19,20,21],
                'q2': [4,5,6,10,11,12,16,17,18,22,23,24],
                'q3': [25,26,27,31,32,33,37,38,39,43,44,45],
                'q4': [28,29,30,34,35,36,40,41,42,46,47,48]
            }
            chip_nums = quadrant_chips.get(clean_value, [])
            chip_list = [f"chip{i}" for i in chip_nums]
            placeholders = ','.join(['%s'] * len(chip_list))
            where_clause = f"chip IN ({placeholders})"
            params = (universe, *chip_list)
        elif filter_type == "tome":
            where_clause = "tome = %s"
            params = (universe, clean_value)
        elif filter_type == "granque":
            where_clause = "granque_name = %s"
            params = (universe, clean_value)
        elif filter_type == "forme":
            where_clause = "forme = %s"
            params = (universe, clean_value)
        else:
            return {"status": "error", "error": f"Type de filtre non supporté: {filter_type}"}
        
        # Statistiques
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total_combinations,
                COUNT(DISTINCT chip) as total_chips,
                COUNT(DISTINCT denomination) as total_denominations
            FROM combinations
            WHERE univers = %s AND {where_clause}
        """, params)
        
        stats = cursor.fetchone()
        
        # Pour les granques et formes, récupérer les dénominations spécifiques
        if filter_type in ["granque", "forme"]:
            cursor.execute(f"""
                SELECT chip, forme, denomination
                FROM combinations
                WHERE univers = %s AND {where_clause}
            """, params)
            
            details = [{
                "chip": row[0],
                "forme": row[1],
                "denomination": row[2]
            } for row in cursor.fetchall()]
            
            filtered_chips = list(set([item["chip"] for item in details]))
            granque_details = details if filter_type == "granque" else []
            forme_details = details if filter_type == "forme" else []
        else:
            # Pour les autres filtres, récupérer seulement les chips
            cursor.execute(f"""
                SELECT DISTINCT chip
                FROM combinations
                WHERE univers = %s AND {where_clause}
            """, params)
            
            filtered_chips = [row[0] for row in cursor.fetchall()]
            granque_details = []
            forme_details = []
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "filter_type": filter_type,
            "filter_value": clean_value,
            "stats": {
                "total_combinations": stats[0],
                "total_chips": stats[1],
                "total_denominations": stats[2],
                "effs": "N/A",
                "zed": "N/A"
            },
            "filtered_chips": filtered_chips,
            "granque_details": granque_details if filter_type == "granque" else [],
            "forme_details": forme_details if filter_type == "forme" else []
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/denomination/{universe}/{denomination}")
async def get_denomination_details(universe: str, denomination: str):
    try:
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        
        # Décoder l'URL et nettoyer la dénomination
        import urllib.parse
        clean_denomination = urllib.parse.unquote(denomination)
        
        print(f"[DEBUG] Recherche dénomination: '{clean_denomination}' dans {universe}")
        print(f"[DEBUG] Granques disponibles: Q1-Q6, Tomes disponibles: tome1-tome3")
        
        import psycopg2
        conn = psycopg2.connect(**service.db_config)
        cursor = conn.cursor()
        
        # Vérifier si la colonne combination existe
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'combinations' AND column_name = 'combination'
        """)
        has_combination_column = cursor.fetchone() is not None
        
        # Récupérer toutes les combinations pour cette dénomination
        if has_combination_column:
            cursor.execute("""
                SELECT 
                    chip, forme, petique, tome, granque_name,
                    alpha_ranking, combination
                FROM combinations
                WHERE univers = %s AND denomination = %s
                ORDER BY alpha_ranking ASC
            """, (universe, clean_denomination))
        else:
            cursor.execute("""
                SELECT 
                    chip, forme, petique, tome, granque_name,
                    alpha_ranking
                FROM combinations
                WHERE univers = %s AND denomination = %s
                ORDER BY alpha_ranking ASC
            """, (universe, clean_denomination))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        combinations = []
        for row in results:
            combo_data = {
                "chip": row[0],
                "forme": row[1], 
                "petique": row[2],
                "tome": row[3],
                "granque_name": row[4],
                "alpha_ranking": row[5]
            }
            
            if has_combination_column and len(row) > 6:
                combo_data["combination"] = row[6]
            else:
                # Générer une combinaison basée sur alpha_ranking
                alpha = row[5]
                if alpha and len(alpha) >= 2:
                    # Convertir les lettres en nombres (a=1, b=2, etc.)
                    nums = [str(ord(c.lower()) - ord('a') + 1) for c in alpha[:2]]
                    combo_data["combination"] = "-".join(nums)
                else:
                    combo_data["combination"] = "--"
            
            combinations.append(combo_data)
        
        return {
            "status": "success",
            "universe": universe,
            "denomination": clean_denomination,
            "combinations": combinations,
            "total_combinations": len(combinations)
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/debug/chip/{chip_id}")
async def debug_chip(chip_id: str):
    try:
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        
        chip_number = int(chip_id.replace('chip', '')) if chip_id.startswith('chip') else int(chip_id)
        result = service.get_chip_compartments('mundo', chip_number)
        
        return {
            "chip_number": chip_number,
            "raw_result": result,
            "has_error": 'error' in result,
            "has_compartments": bool(result.get('compartments'))
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

# === WIN-TRACKER ENDPOINTS ===

@api_app.get("/api/win-tracker/analyze/{universe}/{zone_type}/{zone_value}")
async def analyze_zone(universe: str, zone_type: str, zone_value: str):
    """Analyse une zone spécifique pour la prédiction"""
    try:
        from backend.win_tracker_service import WinTrackerService
        service = WinTrackerService()
        
        analysis = service.analyze_zone(universe, zone_type, zone_value)
        if analysis:
            return {
                "status": "success",
                "analysis": analysis.__dict__
            }
        else:
            return {"status": "error", "error": "Impossible d'analyser la zone"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/win-tracker/opportunities/{universe}")
async def get_best_opportunities(universe: str, limit: int = 5):
    """Retourne les meilleures opportunités d'investissement"""
    try:
        from backend.win_tracker_service import WinTrackerService
        service = WinTrackerService()
        
        opportunities = service.get_best_opportunities(universe, limit)
        return {
            "status": "success",
            "universe": universe,
            "opportunities": [opp.__dict__ for opp in opportunities],
            "total_found": len(opportunities)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/win-tracker/portfolio/{universe}/{budget}")
async def calculate_portfolio(universe: str, budget: int):
    """Calcule une stratégie de portefeuille optimale"""
    try:
        from backend.win_tracker_service import WinTrackerService
        service = WinTrackerService()
        
        strategy = service.calculate_portfolio_strategy(universe, budget)
        return {
            "status": "success",
            "strategy": strategy
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/win-tracker/statistics/{universe}")
async def get_zone_statistics(universe: str):
    """Statistiques générales des zones"""
    try:
        from backend.win_tracker_service import WinTrackerService
        service = WinTrackerService()
        
        stats = service.get_zone_statistics(universe)
        return {
            "status": "success",
            "statistics": stats
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/win-tracker/all-zones/{universe}")
async def get_all_zones_analysis(universe: str):
    """Analyse complète de toutes les zones"""
    try:
        from backend.win_tracker_service import WinTrackerService
        service = WinTrackerService()
        
        analyses = service.get_all_zones_analysis(universe)
        return {
            "status": "success",
            "universe": universe,
            "zones": [analysis.__dict__ for analysis in analyses],
            "total_zones": len(analyses)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

# === ZONES SYNTHÉTIQUES ENDPOINTS ===

@api_app.get("/api/synthetic-zones/create/{universe}")
async def create_synthetic_zones(universe: str):
    """Crée des zones synthétiques pour un univers"""
    try:
        from backend.synthetic_zones_service import SyntheticZonesService
        service = SyntheticZonesService()
        
        zones = service.create_synthetic_zones(universe)
        return {
            "status": "success",
            "universe": universe,
            "synthetic_zones": [zone.__dict__ for zone in zones],
            "total_created": len(zones)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/synthetic-zones/jokers/{universe}")
async def get_joker_zones(universe: str, max_cost: int = 50):
    """Trouve les zones joker - petites, fréquentes et très rentables"""
    try:
        from backend.synthetic_zones_service import SyntheticZonesService
        service = SyntheticZonesService()
        
        jokers = service.get_joker_zones(universe, max_cost)
        return {
            "status": "success",
            "universe": universe,
            "joker_zones": [joker.__dict__ for joker in jokers],
            "total_jokers": len(jokers),
            "max_cost_filter": max_cost
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/synthetic-zones/patterns/{universe}")
async def analyze_patterns(universe: str, days_back: int = 90):
    """Analyse les patterns historiques"""
    try:
        from backend.synthetic_zones_service import SyntheticZonesService
        service = SyntheticZonesService()
        
        patterns = service.analyze_historical_patterns(universe, days_back)
        return {
            "status": "success",
            "universe": universe,
            "patterns": [pattern.__dict__ for pattern in patterns],
            "analysis_period_days": days_back,
            "total_patterns": len(patterns)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/synthetic-zones/best-strategy/{universe}/{budget}")
async def get_best_synthetic_strategy(universe: str, budget: int):
    """Stratégie optimale avec zones synthétiques"""
    try:
        from backend.synthetic_zones_service import SyntheticZonesService
        service = SyntheticZonesService()
        
        # Créer les zones synthétiques
        synthetic_zones = service.create_synthetic_zones(universe)
        
        # Sélectionner les meilleures dans le budget
        selected_zones = []
        total_cost = 0
        total_expected_profit = 0
        
        # Trier par ROI décroissant
        sorted_zones = sorted(synthetic_zones, key=lambda z: z.expected_roi, reverse=True)
        
        for zone in sorted_zones:
            if total_cost + zone.investment_cost <= budget:
                selected_zones.append(zone)
                total_cost += zone.investment_cost
                total_expected_profit += (zone.expected_roi / 100) * zone.investment_cost
        
        return {
            "status": "success",
            "universe": universe,
            "budget": budget,
            "strategy": {
                "selected_zones": [zone.__dict__ for zone in selected_zones],
                "total_investment": total_cost,
                "expected_profit": total_expected_profit,
                "budget_utilization": (total_cost / budget * 100) if budget > 0 else 0,
                "average_roi": sum(z.expected_roi for z in selected_zones) / len(selected_zones) if selected_zones else 0,
                "zones_count": len(selected_zones)
            }
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

# === ENDPOINTS ANALYSE TEMPORELLE GÉOMÉTRIQUE ===

@api_app.post("/api/analytics/temporal-analysis/{universe}")
async def analyze_temporal_patterns(universe: str, request: dict):
    """Analyser les patterns temporels géométriques"""
    try:
        from backend.temporal_geometric_service import TemporalGeometricService
        service = TemporalGeometricService({})
        
        # Récupérer les tirages simulés ou réels
        draw_results = request.get('draw_results', [])
        
        # Si pas de tirages fournis, générer des données simulées
        if not draw_results:
            draw_results = service._generate_simulated_draws_for_period(
                "2024-01-01", "2024-12-31", universe
            )
        
        period_config = {
            'period_type': request.get('period_type', 'monthly'),
            'analyze_by_period': True,
            'tables_config': request.get('tables_config', [])
        }
        
        analysis = service.analyze_temporal_patterns(
            universe, draw_results, period_config
        )
        
        return {
            'status': 'success',
            'universe': universe,
            'analysis': analysis,
            'patterns': analysis.get('recurring_patterns', []),
            'temporal_patterns': analysis.get('temporal_patterns', []),
            'hot_zones': analysis.get('hot_zones', []),
            'predictions': analysis.get('predictions', [])
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/analytics/temporal-data/{universe}")
async def get_temporal_data(universe: str, date_start: str, date_end: str, 
                           marking_type: str = 'chip'):
    """Récupérer les données temporelles pour une période"""
    try:
        from backend.temporal_geometric_service import TemporalGeometricService
        service = TemporalGeometricService({})
        
        data = service.get_temporal_data_for_period(
            universe, date_start, date_end, marking_type
        )
        return data
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.post("/api/analytics/geometric-mapping/{universe}")
async def create_geometric_mapping(universe: str, request: dict):
    """Créer un mapping géométrique pour un tirage"""
    try:
        from backend.temporal_geometric_service import TemporalGeometricService
        service = TemporalGeometricService({})
        
        numbers = request.get('numbers', [])
        date = request.get('date', '2024-01-01')
        
        if not numbers or len(numbers) < 2:
            return {"status": "error", "error": "Au moins 2 numéros requis"}
        
        # Générer les combinaisons 2 à 2
        combinations = service._generate_combinations_from_draw(numbers)
        
        # Mapper à la géométrie
        geometric_mapping = service._map_combinations_to_geometry(
            universe, combinations, date
        )
        
        return {
            'status': 'success',
            'universe': universe,
            'input_numbers': numbers,
            'combinations_count': len(combinations),
            'geometric_positions': geometric_mapping,
            'summary': {
                'total_positions': len(geometric_mapping),
                'quadrants': list(set(pos['quadrant'] for pos in geometric_mapping)),
                'zones': list(set(pos['zone'] for pos in geometric_mapping))
            }
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/analytics/temporal-periods/{universe}")
async def get_temporal_periods(universe: str):
    """Obtenir les périodes disponibles pour l'analyse temporelle"""
    try:
        from datetime import datetime, timedelta
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)  # 1 an de données
        
        return {
            'universe': universe,
            'available': True,
            'earliest_date': start_date.strftime('%Y-%m-%d'),
            'latest_date': end_date.strftime('%Y-%m-%d'),
            'total_days': 365,
            'total_records': 120,  # Simulé
            'periods': {
                'monthly': 12,
                'quarterly': 4,
                'yearly': 1
            },
            'recommended_analysis': 'monthly'
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

# === ENDPOINTS SESSION DE TEST ===

@api_app.post("/api/test-session/create")
async def create_test_session(request: dict):
    """Créer une session de test avec lotos hebdomadaires"""
    try:
        from backend.unified_session_service import unified_session_service
        
        session_name = request.get('session_name', 'session_test_001')
        
        # Initialiser ou récupérer la session
        session_data = unified_session_service.initialize_session_test_001()
        
        # Sauvegarder aussi dans le cache global pour compatibilité
        global test_sessions_cache
        if 'test_sessions_cache' not in globals():
            test_sessions_cache = {}
        test_sessions_cache[session_name] = session_data
        
        return {
            'status': 'success',
            'session': session_data,
            'total_draws': len(session_data['draws'])
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/test-session/{session_name}/analyze/{universe}")
async def analyze_test_session(session_name: str, universe: str):
    """Analyser une session de test avec l'approche géométrique"""
    try:
        from backend.temporal_geometric_service import TemporalGeometricService
        from backend.unified_session_service import unified_session_service
        
        # Récupérer la session depuis le service unifié
        session_data = unified_session_service.get_session_for_temporal_analysis(session_name)
        
        if not session_data:
            return {"status": "error", "error": "Session non trouvée"}
        
        # Analyser avec le service temporel géométrique
        service = TemporalGeometricService({})
        
        period_config = {
            'period_type': 'weekly',
            'analyze_by_period': True,
            'session_name': session_name
        }
        
        analysis = service.analyze_temporal_patterns(
            universe, session_data['draws'], period_config
        )
        
        # Mettre à jour le cache global pour compatibilité
        global test_sessions_cache
        if 'test_sessions_cache' not in globals():
            test_sessions_cache = {}
        test_sessions_cache[session_name] = session_data
        
        return {
            'status': 'success',
            'session_name': session_name,
            'universe': universe,
            'analysis': analysis,
            'session_info': {
                'total_draws': len(session_data['draws']),
                'periods': session_data['periods'],
                'loto_names': session_data['loto_names']
            }
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/test-session/{session_name}")
async def get_test_session(session_name: str):
    """Récupérer une session de test"""
    try:
        from backend.unified_session_service import unified_session_service
        
        session_data = unified_session_service.get_session_for_temporal_analysis(session_name)
        
        # Mettre à jour le cache global pour compatibilité
        global test_sessions_cache
        if 'test_sessions_cache' not in globals():
            test_sessions_cache = {}
        test_sessions_cache[session_name] = session_data
        
        return {
            'status': 'success',
            'session': session_data
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.post("/api/character-analysis/{universe}")
async def analyze_by_character(universe: str, request: dict):
    """Analyse par caractère (tome, forme, chip, etc.)"""
    try:
        from backend.character_analysis_service import CharacterAnalysisService
        service = CharacterAnalysisService({})
        
        session_name = request.get('session_name', 'session_test_001')
        marking_type = request.get('marking_type', 'tome')
        
        # Récupérer la session
        global test_sessions_cache
        if 'test_sessions_cache' not in globals() or session_name not in test_sessions_cache:
            return {"status": "error", "error": "Session non trouvée"}
        
        session_data = test_sessions_cache[session_name]
        
        # Analyser selon le caractère
        analysis = service.analyze_by_character(universe, session_data, marking_type)
        
        return {
            'status': 'success',
            'universe': universe,
            'session_name': session_name,
            'marking_type': marking_type,
            'analysis': analysis
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.post("/api/save-session-to-db")
async def save_session_to_real_db(request: dict):
    """Sauvegarder la session de test en BD réelle"""
    try:
        from backend.real_db_service import RealDBService
        
        # Configuration BD (remplacer par vos vraies valeurs)
        db_config = {
            'host': 'localhost',
            'database': 'katooling_main_system',
            'user': 'postgres',
            'password': 'your_password'  # À configurer
        }
        
        service = RealDBService(db_config)
        
        session_name = request.get('session_name', 'session_test_001')
        
        # Récupérer la session
        global test_sessions_cache
        if 'test_sessions_cache' not in globals() or session_name not in test_sessions_cache:
            return {"status": "error", "error": "Session non trouvée"}
        
        session_data = test_sessions_cache[session_name]
        
        # Sauvegarder en BD
        success = service.save_test_session_to_db(session_data)
        
        if success:
            return {
                'status': 'success',
                'message': f'Session {session_name} sauvegardée en BD',
                'session_name': session_name
            }
        else:
            return {
                'status': 'error',
                'error': 'Erreur lors de la sauvegarde en BD'
            }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/real-analysis/{session_name}/{universe}/{marking_type}")
async def get_real_analysis(session_name: str, universe: str, marking_type: str):
    """Analyse depuis la BD réelle"""
    try:
        from backend.real_db_service import RealDBService
        
        # Configuration BD
        db_config = {
            'host': 'localhost',
            'database': 'katooling_main_system',
            'user': 'postgres',
            'password': 'your_password'  # À configurer
        }
        
        service = RealDBService(db_config)
        
        # Récupérer l'analyse depuis la BD
        analysis = service.get_real_analysis_data(session_name, marking_type)
        
        return {
            'status': 'success',
            'session_name': session_name,
            'universe': universe,
            'marking_type': marking_type,
            'analysis': analysis,
            'source': 'real_database'
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.post("/api/statistical-journal/{universe}")
async def generate_statistical_journal(universe: str, request: dict):
    """Générer le journal statistique pour un tirage"""
    try:
        from backend.statistical_journal_service import StatisticalJournalService
        service = StatisticalJournalService({})
        
        numbers = request.get('numbers', [])
        if not numbers or len(numbers) < 2:
            return {"status": "error", "error": "Au moins 2 numéros requis"}
        
        journal = service.generate_journal(universe, numbers)
        
        return {
            'status': 'success',
            'universe': universe,
            'journal': journal
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.post("/api/period-comparison/{universe}")
async def generate_period_comparison(universe: str, request: dict):
    """Générer la comparaison de période (7 tirages)"""
    try:
        from backend.statistical_journal_service import StatisticalJournalService
        service = StatisticalJournalService({})
        
        period_draws = request.get('period_draws', [])
        if not period_draws or len(period_draws) != 7:
            return {"status": "error", "error": "7 tirages requis pour une période"}
        
        comparison = service.generate_period_comparison(universe, period_draws)
        
        return {
            'status': 'success',
            'universe': universe,
            'comparison': comparison
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/katula-zones/{universe}/{marking_type}")
async def get_katula_marking_zones(universe: str, marking_type: str):
    """Obtenir les zones de marquage Katula selon le caractère"""
    try:
        # Récupérer la session active
        global test_sessions_cache
        if 'test_sessions_cache' not in globals() or 'session_test_001' not in test_sessions_cache:
            return {"status": "error", "error": "Aucune session active"}
        
        session_data = test_sessions_cache['session_test_001']
        
        # Générer les zones de marquage pour tous les tirages
        from backend.statistical_journal_service import StatisticalJournalService
        service = StatisticalJournalService({})
        
        all_zones = {}
        
        for draw in session_data['draws']:
            journal = service.generate_journal(universe, draw['numbers'])
            
            # Extraire les zones pour le type de marquage demandé
            if marking_type in journal['marking_zones']:
                for char_value, zone_data in journal['marking_zones'][marking_type].items():
                    if char_value not in all_zones:
                        all_zones[char_value] = {
                            'chips_to_mark': set(),
                            'total_count': 0,
                            'appearances': 0
                        }
                    
                    all_zones[char_value]['chips_to_mark'].update(zone_data['chips_to_mark'])
                    all_zones[char_value]['total_count'] += zone_data['count']
                    all_zones[char_value]['appearances'] += 1
        
        # Convertir les sets en listes
        for char_value in all_zones:
            all_zones[char_value]['chips_to_mark'] = list(all_zones[char_value]['chips_to_mark'])
        
        return {
            'status': 'success',
            'universe': universe,
            'marking_type': marking_type,
            'zones': all_zones,
            'total_draws': len(session_data['draws'])
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

# === ENDPOINTS GESTION SESSIONS BD ===

@api_app.get("/api/sessions")
async def get_all_sessions():
    """Récupérer toutes les sessions disponibles depuis la base de données"""
    try:
        from backend.unified_db_session_service import UnifiedDBSessionService
        
        db_service = UnifiedDBSessionService()
        sessions = db_service.list_all_sessions()
        
        # Formater la réponse pour correspondre au format attendu par le frontend
        formatted_sessions = []
        for session in sessions:
            formatted_sessions.append({
                'name': session['session_name'],
                'total_draws': session.get('total_draws', 0),
                'completed_draws': session.get('completed_draws', 0),
                'progress_percentage': (session.get('completed_draws', 0) / session.get('total_draws', 1)) * 100 if session.get('total_draws', 0) > 0 else 0,
                'created_at': session.get('created_at'),
                'metadata': session.get('metadata', {}),
                'is_active': session.get('is_active', False),
                'description': session.get('description', '')
            })
        
        return {
            'status': 'success',
            'sessions': formatted_sessions
        }
        
    except Exception as e:
        import traceback
        return {
            "status": "error", 
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@api_app.get("/api/sessions/{session_name}")
async def get_session_details(session_name: str):
    """Récupérer les détails d'une session depuis la base de données"""
    try:
        from backend.unified_db_session_service import UnifiedDBSessionService
        
        db_service = UnifiedDBSessionService()
        
        # Récupérer les détails de base de la session
        sessions = db_service.list_all_sessions()
        session = next((s for s in sessions if s['session_name'] == session_name), None)
        
        if not session:
            return {"status": "error", "error": f"Session {session_name} non trouvée"}
        
        # Récupérer les tirages de la session
        draws = db_service.get_session_draws(session['session_id'])
        
        # Formater la réponse pour correspondre au format attendu par le frontend
        formatted_draws = []
        for draw in draws:
            formatted_draws.append({
                'draw_number': draw.get('draw_number'),
                'draw_date': draw.get('draw_date'),
                'numbers': draw.get('winning_numbers', []),  # winning_numbers from DB -> numbers for frontend
                'is_completed': draw.get('is_completed', True),
                'lottery_name': draw.get('lottery_name', ''),
                'cycle_position': draw.get('cycle_position', 0)
            })
        
        # Créer l'objet de session formaté
        formatted_session = {
            'name': session['session_name'],
            'session_name': session['session_name'],
            'description': session.get('description', ''),
            'total_draws': session.get('total_draws', 0),
            'completed_draws': len([d for d in formatted_draws if d.get('is_completed', False)]),
            'progress_percentage': (len([d for d in formatted_draws if d.get('is_completed', False)]) / session.get('total_draws', 1)) * 100 if session.get('total_draws', 0) > 0 else 0,
            'created_at': session.get('created_at'),
            'metadata': session.get('metadata', {}),
            'is_active': session.get('is_active', False),
            'draws': formatted_draws,
            'current_draw': session.get('current_draw', 1)
        }
        
        return {
            'status': 'success',
            'session': formatted_session
        }
        
    except Exception as e:
        import traceback
        return {
            "status": "error", 
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@api_app.get("/api/sessions/{session_name}/draws")
async def get_session_draws(session_name: str):
    """Récupérer les tirages d'une session"""
    try:
        from backend.unified_session_service import unified_session_service
        
        session_details = unified_session_service.get_session_for_smart_input(session_name)
        
        return {
            'status': 'success',
            'draws': session_details['draws']
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/sessions/{session_name}/progress")
async def get_session_progress(session_name: str):
    """Récupérer le progrès d'une session"""
    try:
        from backend.unified_session_service import unified_session_service
        
        progress = unified_session_service.get_session_progress(session_name)
        
        return {
            'status': 'success',
            'progress': progress
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/sessions/{session_name}/current-draw")
async def get_current_draw(session_name: str):
    """Récupérer le tirage courant d'une session"""
    try:
        from backend.unified_session_service import unified_session_service
        
        current_draw = unified_session_service.get_current_draw(session_name)
        
        if current_draw:
            return {
                'status': 'success',
                'draw': current_draw
            }
        else:
            return {"status": "error", "error": "Aucun tirage courant"}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.post("/api/sessions/{session_name}/save-draw")
async def save_draw_result(session_name: str, request: dict):
    """Sauvegarder le résultat d'un tirage"""
    try:
        from backend.unified_session_service import unified_session_service
        
        draw_data = {
            'draw_id': request.get('draw_id'),
            'numbers': request.get('numbers', []),
            'draw_date': request.get('draw_date')
        }
        
        success = unified_session_service.save_draw(session_name, draw_data)
        
        if success:
            return {
                'status': 'success',
                'message': 'Tirage sauvegardé avec succès'
            }
        else:
            return {"status": "error", "error": "Erreur lors de la sauvegarde"}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

# === ENDPOINTS EXPLORATION BD ===

@api_app.get("/api/db/explore")
async def explore_database():
    """Explorer la structure de la base de données"""
    try:
        from backend.db_explorer_service import DatabaseExplorerService
        service = DatabaseExplorerService()
        
        structure = service.explore_database_structure()
        return {
            'status': 'success',
            'database_structure': structure
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/db/table/{table_name}")
async def get_table_structure(table_name: str):
    """Récupérer la structure d'une table"""
    try:
        from backend.db_explorer_service import DatabaseExplorerService
        service = DatabaseExplorerService()
        
        structure = service.get_table_structure(table_name)
        return {
            'status': 'success',
            'table_structure': structure
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/db/search-sessions")
async def search_existing_sessions():
    """Rechercher des sessions existantes dans la BD"""
    try:
        from backend.db_explorer_service import DatabaseExplorerService
        service = DatabaseExplorerService()
        
        sessions = service.search_session_data()
        return {
            'status': 'success',
            'session_search': sessions
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/db/search-draws")
async def search_existing_draws():
    """Rechercher des tirages existants dans la BD"""
    try:
        from backend.db_explorer_service import DatabaseExplorerService
        service = DatabaseExplorerService()
        
        draws = service.search_draw_data()
        return {
            'status': 'success',
            'draw_search': draws
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

# === ENDPOINTS MIGRATION ===

@api_app.post("/api/migration/migrate-session/{session_id}")
async def migrate_session(session_id: str):
    """Migre une session vers PostgreSQL"""
    try:
        from backend.migration_service import MigrationService
        from backend.unified_session_service import unified_session_service
        
        migration_service = MigrationService()
        session_data = unified_session_service.get_session(session_id)
        
        if not session_data:
            return {"status": "error", "error": "Session non trouvée"}
        
        success = migration_service.migrate_session_to_postgres(session_id, session_data)
        return {"status": "success" if success else "error", "session_id": session_id}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.post("/api/migration/migrate-all")
async def migrate_all_sessions():
    """Migre toutes les sessions vers PostgreSQL"""
    try:
        from backend.migration_service import MigrationService
        from backend.unified_session_service import unified_session_service
        
        migration_service = MigrationService()
        results = migration_service.migrate_all_memory_sessions(unified_session_service)
        return {"status": "success", "migration_results": results}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/postgres/sessions")
async def get_postgres_sessions():
    """Liste des sessions PostgreSQL"""
    try:
        from backend.postgres_session_service import PostgresSessionService
        service = PostgresSessionService()
        return {"status": "success", "sessions": service.list_sessions()}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/postgres/session/{session_id}")
async def get_postgres_session(session_id: str):
    """Récupère une session PostgreSQL"""
    try:
        from backend.postgres_session_service import PostgresSessionService
        service = PostgresSessionService()
        
        session_data = service.get_session(session_id)
        if not session_data:
            return {"status": "error", "error": "Session non trouvée"}
        
        return {"status": "success", "session": session_data}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.post("/api/postgres/session/{session_id}/draw")
async def add_draw_postgres(session_id: str, draw_data: dict):
    """Ajoute un tirage à PostgreSQL"""
    try:
        from backend.postgres_session_service import PostgresSessionService
        service = PostgresSessionService()
        
        success = service.add_draw(session_id, draw_data)
        return {"status": "success" if success else "error"}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/postgres/session/{session_id}/stats")
async def get_postgres_session_stats(session_id: str):
    """Statistiques session PostgreSQL"""
    try:
        from backend.postgres_session_service import PostgresSessionService
        service = PostgresSessionService()
        
        stats = service.get_session_stats(session_id)
        return {"status": "success", "stats": stats}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

# === ENDPOINTS TABLE UNIFIEE ===

@api_app.get("/api/unified/sessions")
async def get_unified_sessions():
    """Liste toutes les sessions de la table unifiée"""
    try:
        from backend.unified_db_session_service import UnifiedDBSessionService
        service = UnifiedDBSessionService()
        
        sessions = service.list_all_sessions()
        return {"status": "success", "sessions": sessions}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/unified/session/{session_uuid}")
async def get_unified_session(session_uuid: str):
    """Récupère une session de la table unifiée"""
    try:
        from backend.unified_db_session_service import UnifiedDBSessionService
        service = UnifiedDBSessionService()
        
        session = service.get_session(session_uuid)
        if not session:
            return {"status": "error", "error": "Session non trouvée"}
        
        return {"status": "success", "session": session}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.post("/api/unified/session")
async def create_unified_session(request: dict):
    """Crée une nouvelle session dans la table unifiée"""
    try:
        from backend.unified_db_session_service import UnifiedDBSessionService
        service = UnifiedDBSessionService()
        
        session_uuid = service.create_session(request)
        if not session_uuid:
            return {"status": "error", "error": "Erreur création session"}
        
        return {"status": "success", "session_uuid": session_uuid}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.post("/api/unified/session/{session_uuid}/draw")
async def add_unified_draw(session_uuid: str, draw_data: dict):
    """Ajoute un tirage à une session unifiée"""
    try:
        from backend.unified_db_session_service import UnifiedDBSessionService
        service = UnifiedDBSessionService()
        
        success = service.add_draw(session_uuid, draw_data)
        return {"status": "success" if success else "error"}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.put("/api/unified/session/{session_uuid}/draw/{draw_number}")
async def update_unified_draw(session_uuid: str, draw_number: int, draw_data: dict):
    """Met à jour un tirage existant"""
    try:
        from backend.unified_db_session_service import UnifiedDBSessionService
        service = UnifiedDBSessionService()
        
        success = service.update_draw_results(session_uuid, draw_number, draw_data.get('numbers', []))
        return {"status": "success" if success else "error"}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.post("/api/unified/session/{session_uuid}/activate")
async def activate_unified_session(session_uuid: str):
    """Active une session unifiée"""
    try:
        from backend.unified_db_session_service import UnifiedDBSessionService
        service = UnifiedDBSessionService()
        
        success = service.activate_session(session_uuid)
        return {"status": "success" if success else "error"}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/api/unified/session/{session_uuid}/stats")
async def get_unified_session_stats(session_uuid: str):
    """Statistiques session unifiée"""
    try:
        from backend.unified_db_session_service import UnifiedDBSessionService
        service = UnifiedDBSessionService()
        
        stats = service.get_session_stats(session_uuid)
        return {"status": "success", "stats": stats}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

def find_free_port(start_port):
    """Trouve un port libre à partir du port de départ"""
    import socket
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def start_api_server(port):
    import uvicorn
    uvicorn.run(api_app, host="0.0.0.0", port=port, log_level="error")

def start_combined_server(port):
    import uvicorn
    from fastapi.staticfiles import StaticFiles
    
    # Servir les fichiers statiques
    api_app.mount("/", StaticFiles(directory=".", html=True), name="static")
    
    print(f"Serveur combine: http://localhost:{port}/frontend/katula-dynamic.html")
    print(f"API disponible: http://localhost:{port}/api/")
    print(f"Analyse Temporelle Geometrique activee")
    print(f"Endpoints disponibles:")
    print(f"   - POST /api/analytics/temporal-analysis/{{universe}}")
    print(f"   - GET /api/analytics/temporal-data/{{universe}}")
    print(f"   - POST /api/analytics/geometric-mapping/{{universe}}")
    print(f"   - GET /api/analytics/temporal-periods/{{universe}}")
    print(f"Sessions de test:")
    print(f"   - POST /api/test-session/create")
    print(f"   - GET /api/test-session/{{session_name}}/analyze/{{universe}}")
    print(f"   - GET /api/test-session/{{session_name}}")
    print(f"Analyse par caractere:")
    print(f"   - POST /api/character-analysis/{{universe}}")
    print(f"   - POST /api/save-session-to-db")
    print(f"   - GET /api/real-analysis/{{session}}/{{universe}}/{{marking_type}}")
    print(f"Journal statistique:")
    print(f"   - POST /api/statistical-journal/{{universe}}")
    print(f"   - POST /api/period-comparison/{{universe}}")
    print(f"   - GET /api/katula-zones/{{universe}}/{{marking_type}}")
    print(f"Gestion sessions BD:")
    print(f"   - GET /api/sessions")
    print(f"   - GET /api/sessions/{{session_name}}")
    print(f"   - GET /api/sessions/{{session_name}}/progress")
    print(f"   - GET /api/sessions/{{session_name}}/current-draw")
    print(f"   - POST /api/sessions/{{session_name}}/save-draw")
    print(f"Migration PostgreSQL:")
    print(f"   - POST /api/migration/migrate-session/{{session_id}}")
    print(f"   - POST /api/migration/migrate-all")
    print(f"   - GET /api/postgres/sessions")
    print(f"   - GET /api/postgres/session/{{session_id}}")
    print(f"   - POST /api/postgres/session/{{session_id}}/draw")
    print(f"   - GET /api/postgres/session/{{session_id}}/stats")
    
    # Ajouter les routes katooling si disponibles
    if KATOOLING_AVAILABLE:
        try:
            add_katooling_routes(api_app)
            print(f"Routes katooling_main_system:")
            print(f"   - GET /api/katooling/sessions")
            print(f"   - GET /api/katooling/sessions/{{session_id}}")
            print(f"   - GET /api/katooling/algeria")
            print(f"   - GET /api/katooling/session-mapping")
        except Exception as e:
            print(f"Erreur chargement routes katooling: {e}")
  

    uvicorn.run(api_app, host="0.0.0.0", port=port, log_level="error")

if __name__ == "__main__":
    print("=== SERVEUR UNIQUE EAZZYCALCULATOR ===")

    # Trouver un port libre
    port = find_free_port(8881)

    if not port:
        print("❌ Impossible de trouver un port libre")
        exit(1)

    # Servir les fichiers statiques
    from fastapi.staticfiles import StaticFiles
    api_app.mount("/", StaticFiles(directory=".", html=True), name="static")

    print(f"Serveur combine: http://localhost:{port}/frontend/katula-dynamic.html")
    print(f"API disponible: http://localhost:{port}/api/")
    print(f"Analyse Temporelle Geometrique activee")

    # Ajouter les routes katooling si disponibles
    if KATOOLING_AVAILABLE:
        try:
            add_katooling_routes(api_app)
            print(f"Routes katooling_main_system:")
            print(f"   - GET /api/katooling/sessions")
            print(f"   - GET /api/katooling/sessions/{{session_id}}")
            print(f"   - GET /api/katooling/algeria")
            print(f"   - GET /api/katooling/session-mapping")
        except Exception as e:
            print(f"Erreur chargement routes katooling: {e}")

    # Afficher dynamiquement toutes les routes
    print("Routes enregistrées dans api_app:")
    for route in api_app.routes:
        if route.path.startswith("/api"):
            print(f"   - {route.methods} {route.path}")

    # Démarrer le serveur
    import uvicorn
    uvicorn.run(api_app, host="0.0.0.0", port=port, log_level="error")

