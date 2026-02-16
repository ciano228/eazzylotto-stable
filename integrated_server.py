#!/usr/bin/env python3
"""
Serveur intégré pour EazzyCalculatoravec backend FastAPI
Version unifiée bas ée sur simple_server.py
"""
import http.server
import socketserver
import threading
import time
from datetime import date, datetime
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import uvicorn
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import logging
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
import socket
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from backend.session_statistics_engine import SessionStatisticsEngine
from backend.unified_db_session_service import UnifiedDBSessionService
from backend.win_tracker_service import WinTrackerService
from backend.split_strategy_service import SplitStrategyService

# Ajouter le dossier backend au path pour les imports relatifs dans les modules app.*
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))


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


def safe_execute(cursor, sql, params=None):
    """Execute SQL, but if it fails due to missing 'univers' column, retry with 'universe'.
    Returns cursor after successful execution.
    """
    try:
        if params is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, params)
        return cursor
    except Exception as e:
        msg = str(e).lower()
        # handle common column name mismatch between 'univers' and 'universe'
        if 'column "univers" does not exist' in msg or 'column \"univers\" does not exist' in msg:
            try:
                alt_sql = sql.replace('univers', 'universe')
                if params is None:
                    cursor.execute(alt_sql)
                else:
                    cursor.execute(alt_sql, params)
                return cursor
            except Exception:
                pass
        # re-raise original error if we cannot recover
        raise

# Serveur API FastAPI
api_app = FastAPI()
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration dictionary
db_config = {
    'dbname': os.getenv('DB_NAME', 'katooling_main_system'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'Katulaa_33'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

# Services for statistics
stats_engine = SessionStatisticsEngine(db_config)
session_service = UnifiedDBSessionService()
win_tracker_service = WinTrackerService()
split_strategy_service = SplitStrategyService(db_config)
# Monter le répertoire frontend pour servir les fichiers statiques
try:
    frontend_path = Path(__file__).parent / "frontend"
    if frontend_path.exists():
        api_app.mount("/frontend", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
        logger.info(f"Frontend mounted at /frontend from {frontend_path}")
    else:
        logger.warning(f"Frontend directory not found at {frontend_path}")
except Exception as e:
    logger.error(f"Error mounting frontend: {e}")

# Register lightweight redirects from root paths to canonical /frontend/* URLs
try:
    redirect_pages = [
        'win-tracker.html',
        'katula-dynamic.html',
        'katula-temporal-analysis.html',
        'smart-input.html',
        'index.html',
        'katooling-tracker.html'
    ]

    for page in redirect_pages:
        frontend_path_for_page = f'/frontend/{page}'
        route_path = f'/{page}'

        def make_redirect(target):
            async def redirect_handler():
                return RedirectResponse(url=target)
            return redirect_handler

        api_app.add_api_route(route_path, make_redirect(frontend_path_for_page), methods=['GET'])
        logger.info(f"Registered redirect {route_path} -> {frontend_path_for_page}")

    # root '/' -> /frontend/katula-dynamic.html (canonical)
    api_app.add_api_route('/', make_redirect('/frontend/katula-dynamic.html'), methods=['GET'])
    logger.info("Registered root '/' redirect to /frontend/katula-dynamic.html")
except Exception as e:
    logger.error(f"Error registering redirect root pages: {e}")

# === ROUTES API (au niveau module comme dans simple_server.py) ===

# Importer et monter les routeurs additionnels
try:
    from app.routes import (
        analytics, 
        katooling_workflow, 
        combinations, 
        unified_session,
        session,
        temporal_analysis,
        verdict,
        performance,
        lottery,
        pattern_recognition,
        structural_weights
    )
    
    # Monter les routeurs
    api_app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
    api_app.include_router(katooling_workflow.router, prefix="/katooling", tags=["katooling"])
    api_app.include_router(combinations.router)
    api_app.include_router(unified_session.router, prefix="/unified", tags=["session"])
    api_app.include_router(session.router, prefix="/session", tags=["session_v1"])
    api_app.include_router(temporal_analysis.router, prefix="/analytics", tags=["temporal"])
    api_app.include_router(verdict.router, prefix="/verdict", tags=["verdict"])
    api_app.include_router(performance.router, prefix="/performance", tags=["performance"])
    api_app.include_router(lottery.router, prefix="/lottery", tags=["lottery"])
    api_app.include_router(pattern_recognition.router, prefix="/patterns", tags=["patterns"])
    api_app.include_router(structural_weights.router, prefix="/structural-weights", tags=["structural_weights"])
    
    # Chatbot Router
    from app.routes import chat
    api_app.include_router(chat.router, prefix="/chat", tags=["chat"])
    
    print("SUCCESS: Tous les routeurs charges avec succes (analytics, katooling, combinations, unified_session, session, temporal_analysis, verdict, performance, lottery, pattern_recognition, structural_weights)")
except ImportError as e:
    print(f"ERROR: Erreur lors du chargement des routeurs: {e}")
    import traceback
    traceback.print_exc()

# Routes Journal V2 directement dans integrated_server
from pydantic import BaseModel
from typing import List

class DrawInput(BaseModel):
    numbers: List[int]
    universe: str = None

@api_app.post("/journal/generate")
async def generate_journal_endpoint(draw: DrawInput):
    """Génère le journal statistique pour un tirage"""
    try:
        from backend.app.services.journal_service_v2 import JournalServiceV2
        
        if len(draw.numbers) < 2:
            return {"success": False, "error": "Au moins 2 numéros requis"}
        
        journal = JournalServiceV2.generate_full_journal(draw.numbers)
        return {"success": True, "data": journal}
    except Exception as e:
        return {"success": False, "error": str(e)}

@api_app.post("/journal/validate-universe")
async def validate_universe_endpoint(draw: DrawInput):
    """Valide que toutes les combinaisons appartiennent à l'univers spécifié"""
    try:
        from backend.app.services.journal_service_v2 import JournalServiceV2
        
        if not draw.universe:
            return {"success": False, "error": "Univers requis pour la validation"}
        
        if len(draw.numbers) < 2:
            return {"success": False, "error": "Au moins 2 numéros requis"}
        
        validation = JournalServiceV2.validate_draw_universe(draw.numbers, draw.universe)
        return {"success": True, "data": validation}
    except Exception as e:
        return {"success": False, "error": str(e)}

@api_app.get("/journal/combination/{num1}/{num2}")
async def get_combination_endpoint(num1: int, num2: int):
    """Récupère l'entrée de journal pour une combinaison spécifique"""
    try:
        from backend.app.services.journal_service_v2 import JournalServiceV2
        
        entry = JournalServiceV2.generate_journal_entry(num1, num2)
        
        if "error" in entry:
            return {"success": False, "error": entry["error"]}
        
        return {"success": True, "data": entry}
    except Exception as e:
        return {"success": False, "error": str(e)}

@api_app.get("/journal/mappings")
async def get_mappings():
    """Récupère les mappings parite et unidos depuis la BD"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        parite_map = {1: 'Pair-Pair', 2: 'Pair-Impair', 3: 'Impair-Pair', 4: 'Impair-Impair'}
        unidos_map = {1: 'U1-Bas-Bas', 2: 'U2-Bas-Haut', 3: 'U3-Haut-Bas', 4: 'U4-Haut-Haut'}
        
        try:
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'parite' AND table_schema = 'public'
                ORDER BY ordinal_position
            """)
            parite_cols = [row['column_name'] for row in cursor.fetchall()]
            
            if len(parite_cols) >= 2:
                col1, col2 = parite_cols[0], parite_cols[1]
                cursor.execute(f"SELECT {col1}, {col2} FROM parite ORDER BY {col1}")
                parite_rows = cursor.fetchall()
                parite_map = {row[col1]: row[col2] for row in parite_rows}
        except Exception as e:
            logger.error(f"Parite fallback: {e}")
            conn.rollback()
        
        try:
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'unidos' AND table_schema = 'public'
                ORDER BY ordinal_position
            """)
            unidos_cols = [row['column_name'] for row in cursor.fetchall()]
            
            if len(unidos_cols) >= 2:
                col1, col2 = unidos_cols[0], unidos_cols[1]
                cursor.execute(f"SELECT {col1}, {col2} FROM unidos ORDER BY {col1}")
                unidos_rows = cursor.fetchall()
                unidos_map = {row[col1]: row[col2] for row in unidos_rows}
        except Exception as e:
            logger.error(f"Unidos fallback: {e}")
            conn.rollback()
        
        conn.close()
        
        return {
            "success": True, 
            "parite": parite_map, 
            "unidos": unidos_map
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

print("Routes journal V2 ajoutées directement dans integrated_server")


# Endpoint: staking strategy based on statistical journal
@api_app.post("/api/win-tracker/staking/{universe}")
async def staking_strategy_endpoint(universe: str, payload: Dict[str, Any]):
        """Génère une stratégie de mises multi-tirages pour les caractères récurrents.

        Expects JSON body:
            {
                "period_draws": [[...], [...], ...],
                "char_type": "tome",
                "multiplier": 10,
                "max_rounds": 4,
                "starting_stake": 1,
                "reward_per_win": 200,
                "top_n": 10
            }
        """
        try:
                from statistical_journal_service import StatisticalJournalService

                period_draws = payload.get('period_draws', []) if isinstance(payload, dict) else []
                char_type = payload.get('char_type', 'tome') if isinstance(payload, dict) else 'tome'
                multiplier = int(payload.get('multiplier', 10)) if isinstance(payload, dict) else 10
                max_rounds = int(payload.get('max_rounds', 4)) if isinstance(payload, dict) else 4
                starting_stake = int(payload.get('starting_stake', 1)) if isinstance(payload, dict) else 1
                reward_per_win = int(payload.get('reward_per_win', 200)) if isinstance(payload, dict) else 200
                top_n = int(payload.get('top_n', 10)) if isinstance(payload, dict) else 10

                svc = StatisticalJournalService(db_config={})
                result = svc.generate_staking_strategy(
                        universe,
                        period_draws,
                        char_type=char_type,
                        multiplier=multiplier,
                        max_rounds=max_rounds,
                        starting_stake=starting_stake,
                        reward_per_win=reward_per_win,
                        top_n=top_n
                )

                return JSONResponse(content=result)
        except Exception as e:
                logger.error(f"Erreur staking_strategy_endpoint: {e}")
                return JSONResponse(content={"status": "error", "error": str(e)})

# Routes journal V2 ajoutées ci-dessus

@api_app.post("/kiro/chat")
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

@api_app.get("/draws/real/{univers}")
async def get_real_draws(
    univers: str,
    date_start: str,
    date_end: str,
    session_id: int | None = Query(None),
    session_name: str | None = Query(None)
):
    """Retourner les tirages réels (table session_draws) sur une plage de dates.

    Note: le paramètre de chemin {univers} est conservé pour compat frontend.
    Les univers Katula proviennent du journal stats (combinations) et ne servent
    pas à filtrer les tirages.
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if session_id is not None:
                safe_execute(
                    cur,
                    """
                    SELECT 
                        sd.draw_number,
                        sd.lottery_name,
                        sd.draw_date,
                        sd.winning_numbers,
                        sd.is_completed,
                        sd.is_no_draw,
                        sd.no_draw_reason
                    FROM session_draws sd
                    WHERE sd.session_id = %s
                      AND sd.draw_date BETWEEN %s AND %s
                    ORDER BY sd.draw_date, sd.draw_number
                    """,
                    (session_id, date_start, date_end)
                )
            elif session_name:
                safe_execute(
                    cur,
                    """
                    SELECT 
                        sd.draw_number,
                        sd.lottery_name,
                        sd.draw_date,
                        sd.winning_numbers,
                        sd.is_completed,
                        sd.is_no_draw,
                        sd.no_draw_reason
                    FROM session_draws sd
                    JOIN work_sessions ws ON ws.id = sd.session_id
                    WHERE LOWER(ws.name) = LOWER(%s)
                      AND sd.draw_date BETWEEN %s AND %s
                    ORDER BY sd.draw_date, sd.draw_number
                    """,
                    (session_name, date_start, date_end)
                )
            else:
                safe_execute(
                    cur,
                    """
                    SELECT id
                    FROM work_sessions
                    WHERE is_active = true
                    ORDER BY id DESC
                    LIMIT 1
                    """,
                    ()
                )
                active = cur.fetchone() or {}
                active_id = active.get('id')
                if not active_id:
                    return {
                        "status": "success",
                        "univers": univers,
                        "date_start": date_start,
                        "date_end": date_end,
                        "draws": []
                    }

                safe_execute(
                    cur,
                    """
                    SELECT 
                        sd.draw_number,
                        sd.lottery_name,
                        sd.draw_date,
                        sd.winning_numbers,
                        sd.is_completed,
                        sd.is_no_draw,
                        sd.no_draw_reason
                    FROM session_draws sd
                    WHERE sd.session_id = %s
                      AND sd.draw_date BETWEEN %s AND %s
                    ORDER BY sd.draw_date, sd.draw_number
                    """,
                    (active_id, date_start, date_end)
                )

            rows = cur.fetchall()

        return {
            "status": "success",
            "univers": univers,
            "date_start": date_start,
            "date_end": date_end,
            "draws": rows
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des tirages (session_draws) pour {univers}: {e}")
        if conn:
            conn.rollback()
        return {"status": "error", "error": str(e)}
    finally:
        if conn:
            conn.close()


@api_app.get('/api/models')
async def get_models():
    """Return available models and whether they are enabled for clients.

    Reads `project_config.json` if present; otherwise returns a default set.
    """
    try:
        import json
        cfg_path = os.path.join(os.path.dirname(__file__), 'project_config.json')
        if not os.path.exists(cfg_path):
            # fallback minimal response
            return JSONResponse(content={"available": ["claude-haiku-4.5"], "enabled_for_all_clients": True})

        with open(cfg_path, 'r', encoding='utf-8') as f:
            cfg = json.load(f)

        models = cfg.get('models', {"available": ["claude-haiku-4.5"], "enabled_for_all_clients": True})
        return JSONResponse(content={"status": "success", "models": models})
    except Exception as e:
        logger.error(f"Error reading models config: {e}")
        return JSONResponse(content={"status": "error", "error": str(e)})


@api_app.post('/api/kiro/claude-simulate')
async def claude_simulate(request: Request):
    """Simulate a Claude Haiku 4.5 response for testing purposes.

    Accepts JSON: { "message": "...", "model": "claude-haiku-4.5" }
    Returns a structured JSON mimicking a real model response.
    """
    try:
        data = await request.json()
    except Exception:
        data = {}

    message = (data.get('message') or '').strip()
    model = data.get('model', 'claude-haiku-4.5')

    def _make_haiku(seed_text: str):
        # Simple deterministic 3-line haiku-like generator using words from input
        words = [w for w in seed_text.replace('\n', ' ').split() if w]
        if not words:
            return "Quiet code morning\nsmall functions awaken\nlog files hum softly"
        a = words[0][:6]
        b = words[len(words)//2][:8] if len(words) > 1 else words[0][:8]
        c = words[-1][:6]
        return f"{a} dawns\n{b} in the grid\n{c} returns"

    if not message:
        response_text = "Hello — this is a simulated Claude Haiku 4.5 endpoint. Provide a message to get a styled reply."
    else:
        # If model looks like haiku, return a short poetic reply plus a helpful paragraph
        haiku = _make_haiku(message)
        # Short summary / helpful answer emulation
        summary = f"Simulated answer to: {message[:200]}" if len(message) > 0 else ""
        response_text = f"{haiku}\n\n{summary}\n\n(--- simulated by {model})"

    # approximate token count
    token_est = max(1, len(response_text.split()) // 1)

    result = {
        'status': 'success',
        'model': model,
        'type': 'text',
        'streaming': False,
        'response': response_text,
        'tokens': token_est,
        'metadata': {
            'simulated': True,
            'style': 'haiku-brief-answer'
        }
    }

    return JSONResponse(content=result)


@api_app.post('/api/kiro/claude')
async def claude_forward(request: Request):
    """Forward requests to Anthropic Claude (real) when API key is provided.

    Accepts JSON: { "message": "...", "model": "claude-haiku-4.5", "api_key": "optional" }
    If `api_key` is provided in the request body it will be used for this call only.
    Otherwise the server looks for the `ANTHROPIC_API_KEY` environment variable.
    """
    try:
        data = await request.json()
    except Exception:
        data = {}

    message = (data.get('message') or '').strip()
    model = data.get('model', 'claude-haiku-4.5')
    provided_key = data.get('api_key')

    api_key = provided_key or os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        return JSONResponse(content={"status": "error", "error": "No Anthropic API key provided (set ANTHROPIC_API_KEY or include 'api_key' in request)"}, status_code=400)

    # Build prompt in Claude-friendly style
    prompt = f"Human: {message}\n\nAssistant:"

    # Prepare request to Anthropic (best-effort compatibility)
    anthropic_url = os.getenv('ANTHROPIC_API_URL', 'https://api.anthropic.com/v1/complete')
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key
    }

    payload = {
        'model': model,
        'prompt': prompt,
        'max_tokens_to_sample': int(data.get('max_tokens', 512)),
        'temperature': float(data.get('temperature', 0.2))
    }

    try:
        import requests
        resp = requests.post(anthropic_url, json=payload, headers=headers, timeout=15)
        try:
            j = resp.json()
        except Exception:
            j = {'raw_text': resp.text}

        return JSONResponse(content={
            'status': 'success' if resp.status_code == 200 else 'error',
            'http_status': resp.status_code,
            'model': model,
            'result': j
        }, status_code=200)
    except Exception as e:
        logger.error(f"Error forwarding to Anthropic: {e}")
        return JSONResponse(content={"status": "error", "error": str(e)}, status_code=500)


@api_app.post('/api/kiro/forward')
async def multi_provider_forward(request: Request):
        """Forward requests to a selected provider: 'anthropic', 'openai', 'mistral', 'deepseek', 'groq', 'ollama'.

        Request JSON:
            { "provider": "openai", "api_key": "...", "message": "...", "model": "..." }

        If `api_key` is missing it will look for environment variables:
            ANTHROPIC_API_KEY, OPENAI_API_KEY, MISTRAL_API_KEY, DEEPSEEK_API_KEY, GROQ_API_KEY

        Ollama requires no API key (runs locally at http://localhost:11434).
        """
        try:
                data = await request.json()
        except Exception:
                data = {}

        provider = (data.get('provider') or '').lower()
        message = data.get('message', '')
        model = data.get('model')
        provided_key = data.get('api_key')

        # Resolve API key
        env_keys = {
            'anthropic': os.getenv('ANTHROPIC_API_KEY'),
            'openai': os.getenv('OPENAI_API_KEY'),
            'mistral': os.getenv('MISTRAL_API_KEY'),
            'deepseek': os.getenv('DEEPSEEK_API_KEY'),
            'groq': os.getenv('GROQ_API_KEY'),
            'ollama': None
        }

        api_key = provided_key or env_keys.get(provider)
        # Ollama runs locally and doesn't require an API key
        if provider != 'ollama' and not api_key:
            return JSONResponse(content={"status": "error", "error": f"No API key provided for provider {provider}"}, status_code=400)

        # Provider-specific handling
        try:
            from backend.app.services.llm_provider_service import LLMProviderService
            llm_service = LLMProviderService()
            
            # Extract kwargs for provider
            kwargs = {
                'api_key': api_key,
                'max_tokens': int(data.get('max_tokens', 512)),
                'temperature': float(data.get('temperature', 0.7))
            }
            
            result = llm_service.generate_text(provider, model, message, **kwargs)
            
            if result.get('status') == 'error':
                 return JSONResponse(content=result, status_code=500)
            
            return JSONResponse(content=result)

        except ImportError:
             return JSONResponse(content={'status':'error','error':'LLMProviderService not found'}, status_code=500)
        except Exception as e:
            logger.error(f"Error forwarding to provider {provider}: {e}")
            return JSONResponse(content={'status':'error','error': str(e)}, status_code=500)

class PredictionRequest(BaseModel):
    input_numbers: List[int]
    prediction_horizon: Optional[int] = 5

@api_app.post("/predictions/generate")
async def generate_predictions(request: PredictionRequest):
    """Générer des prédictions (Mock ou appel service)"""
    try:
        # Simulation de prédiction
        import random
        predictions = []
        for i in range(request.prediction_horizon):
            pred_nums = sorted(random.sample(range(1, 91), 5))
            predictions.append({
                "date": f"2025-{(i+1):02d}-01",
                "predicted": pred_nums,
                "actual": [],
                "accuracy": round(random.uniform(0.6, 0.95), 2)
            })
            
        return {
            "status": "success",
            "predictions": predictions,
            "model": "LSTM-Mock"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

class DrawCreateRequest(BaseModel):
    numbers: List[int]
    date: str
    draw_type: str

@api_app.post("/draws/create")
async def create_draw(request: DrawCreateRequest):
    """Créer un nouveau tirage (Mock)"""
    return {
        "status": "success",
        "id": "new_draw_123",
        "message": "Tirage créé avec succès"
    }


@api_app.get("/universe/{universe}/formes")
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

@api_app.get("/formes/real/{universe}/chip/{chip_id}")
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
            print(f"Erreur DB pour chip {chip_id}: {db_error}")
            return {"status": "error", "error": str(db_error)}
            
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/formes/real/{universe}/all")
async def get_all_chips_formes(universe: str):
    """Récupérer les données de tous les chips en une seule requête avec dénominations complètes"""
    try:
        from backend.katula_complete_service import KatulaCompleteService
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        service = KatulaCompleteService()
        
        # Récupérer les données complètes chip par chip pour préserver les dénominations multiples
        all_chips_data = {}
        for chip_num in range(1, 49):  # 48 chips
            chip_result = service.get_chip_compartments(universe, chip_num)
            
            if 'error' not in chip_result and chip_result.get('compartments'):
                chip_key = f"chip{chip_num}"
                formes_data = {}
                
                for compartment in chip_result.get('compartments', []):
                    forme = compartment['forme']
                    denomination = compartment['denomination']
                    
                    if forme and denomination and denomination != "---":
                        # Préserver la dénomination COMPLÈTE avec tous les slashes
                        if forme not in formes_data:
                            formes_data[forme] = []
                        
                        formes_data[forme].append({
                            "denomination": denomination,  # Dénomination complète non tronquée
                            "frequency": 1,
                            "multiple": '/' in denomination
                        })
                
                if formes_data:
                    all_chips_data[chip_key] = {
                        "chip_number": chip_num,
                        "formes_data": formes_data
                    }
        
        return {
            "status": "success",
            "universe": universe,
            "chips": all_chips_data,
            "total_chips": len(all_chips_data)
        }
        
    except Exception as e:
        print(f"Erreur lors de la récupération globale: {e}")
        return {"status": "error", "error": str(e)}



@api_app.get("/filter-options/{universe}")
async def get_filter_options(universe: str):
    try:
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        return service.get_filter_options(universe)
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/granques/{universe}")
async def get_granques(universe: str):
    try:
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        
        import psycopg2
        conn = psycopg2.connect(**service.db_config)
        cursor = conn.cursor()
        
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

@api_app.get("/tomes/{universe}")
async def get_tomes(universe: str):
    try:
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        
        import psycopg2
        conn = psycopg2.connect(**service.db_config)
        cursor = conn.cursor()
        
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

@api_app.get("/katula/tomes/{univers}")
async def get_universe_tomes(univers: str):
    """Récupérer la liste des chips par tome pour un univers donné."""
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


# ----------------------------
# Win-Tracker POC Endpoints
# ----------------------------


@api_app.get("/win-tracker/opportunities/{universe}")
async def win_tracker_opportunities(universe: str, limit: int = 10, session_id: int | None = Query(None)):
    """Retourne les meilleures opportunités Win-Tracker pour un univers."""
    try:
        from win_tracker_service import WinTrackerService
        svc = WinTrackerService()
        if session_id:
            ops = svc.get_best_opportunities_for_session(universe, session_id, limit=limit)
        else:
            ops = svc.get_best_opportunities(universe, limit=limit)
        return JSONResponse(content={
            'status': 'success',
            'universe': universe,
            'session_id': session_id,
            'opportunities': [o.__dict__ for o in ops]
        })
    except Exception as e:
        logger.error(f"win_tracker_opportunities error for {universe}: {e}")
        return JSONResponse(content={'status': 'error', 'error': str(e)})


@api_app.get("/win-tracker/statistics/{universe}")
async def win_tracker_statistics(universe: str, session_id: int | None = Query(None)):
    """Retourne des statistiques agrégées Win-Tracker pour un univers."""
    try:
        from win_tracker_service import WinTrackerService
        svc = WinTrackerService()
        if session_id:
            stats = svc.get_zone_statistics_for_session(universe, session_id)
        else:
            stats = svc.get_zone_statistics(universe)
        return JSONResponse(content={'status': 'success', 'statistics': stats})
    except Exception as e:
        logger.error(f"win_tracker_statistics error for {universe}: {e}")
        return JSONResponse(content={'status': 'error', 'error': str(e)})


@api_app.get("/win-tracker/portfolio/{universe}/{budget}")
async def win_tracker_portfolio(universe: str, budget: int, session_id: int | None = Query(None)):
    """Calcule une stratégie de portefeuille pour un budget donné."""
    try:
        from win_tracker_service import WinTrackerService
        svc = WinTrackerService()
        if session_id:
            strategy = svc.calculate_portfolio_strategy_for_session(universe, session_id, budget)
        else:
            strategy = svc.calculate_portfolio_strategy(universe, budget)
        return JSONResponse(content={'status': 'success', 'strategy': strategy})
    except Exception as e:
        logger.error(f"win_tracker_portfolio error for {universe} budget {budget}: {e}")
        return JSONResponse(content={'status': 'error', 'error': str(e)})



@api_app.get("/analytics/chip-drawers-structure")
async def get_chip_drawers_structure(universe: str):
    """Retourne la structure des drawers par chip pour un univers donné.
    Essaie d'abord la table `drawers`, puis reconstitue depuis `combinations` si nécessaire.
    (Route legacy: universe en query string)
    """
    return await _get_chip_drawers_structure_for_universe(universe)


@api_app.get("/analytics/chip-drawers-structure/{universe}")
async def get_chip_drawers_structure_by_universe(universe: str):
    """Route attendue par le frontend: universe dans le path."""
    return await _get_chip_drawers_structure_for_universe(universe)


async def _get_chip_drawers_structure_for_universe(universe: str):
    def _chip_key_from_value(chip_value, fallback_text: str | None = None) -> str | None:
        if chip_value is None and not fallback_text:
            return None
        if isinstance(chip_value, (int, float)):
            try:
                return f"chip{int(chip_value)}"
            except Exception:
                return None
        if isinstance(chip_value, str):
            raw = chip_value.strip()
            import re
            m = re.search(r"^(?:chip)?\s*(\d+)$", raw, flags=re.IGNORECASE)
            if m:
                return f"chip{int(m.group(1))}"
            m2 = re.search(r"chip\s*(\d+)", raw, flags=re.IGNORECASE)
            if m2:
                return f"chip{int(m2.group(1))}"
        if fallback_text:
            import re
            m = re.search(r"drawer_(\d+)", fallback_text)
            if m:
                return f"chip{int(m.group(1))}"
        return None

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Première tentative: lire la table 'drawers' si disponible
            try:
                safe_execute(
                    cur,
                    """
                    SELECT chip, drawer, drawer_name, forme, denomination
                    FROM drawers
                    WHERE univers = %s
                    ORDER BY chip
                    """,
                    (universe,),
                )
                rows = cur.fetchall()

                if rows:
                    chip_structure = {}
                    for row in rows:
                        chip_key = _chip_key_from_value(
                            row.get('chip'),
                            (row.get('drawer_name') or row.get('drawer') or '')
                        )
                        if not chip_key:
                            continue

                        chip_structure.setdefault(chip_key, []).append({
                            'drawer_name': row.get('drawer_name') or row.get('drawer'),
                            'drawer': row.get('drawer'),
                            'forme': row.get('forme'),
                            'denomination': row.get('denomination')
                        })

                    total_chips = len(chip_structure)
                    total_drawers = sum(len(v) for v in chip_structure.values())
                    stats = {
                        'total_chips': total_chips,
                        'total_drawers': total_drawers,
                        'avg_drawers_per_chip': (total_drawers / total_chips) if total_chips else 0
                    }

                    return JSONResponse(content={
                        'status': 'success',
                        'universe': universe,
                        'chip_structure': chip_structure,
                        'statistics': stats
                    })
            except Exception as e:
                # La table drawers peut ne pas exister ou contenir d'autres schémas; fallback ci-dessous
                logger.warning(f"Fallback to 'combinations' for chip-drawers-structure. Reason: {e}")
                conn.rollback()

            # Fallback: reconstituer depuis combinations (formes / denominations)
            safe_execute(
                cur,
                """
                SELECT chip, forme, denomination
                FROM combinations
                WHERE univers = %s
                ORDER BY chip
                """,
                (universe,),
            )
            rows = cur.fetchall()

            chips_map = {}
            for row in rows:
                chip_key = _chip_key_from_value(row.get('chip'))
                forme = row.get('forme') or 'unknown'
                denom = row.get('denomination')
                if not chip_key:
                    continue
                chips_map.setdefault(chip_key, {})
                chips_map[chip_key].setdefault(forme, set())
                if denom:
                    chips_map[chip_key][forme].add(denom)

            chip_structure = {}
            for chip_key, formes in chips_map.items():
                drawers = []
                for forme, denoms in formes.items():
                    if not denoms:
                        drawers.append({
                            'drawer_name': f"drawer_{chip_key.replace('chip','')}_{forme}",
                            'drawer': f"drawer_{chip_key.replace('chip','')}_{forme}",
                            'forme': forme,
                            'denomination': None
                        })
                    else:
                        idx = 1
                        for denom in denoms:
                            drawers.append({
                                'drawer_name': f"drawer_{chip_key.replace('chip','')}_{forme}_{idx}",
                                'drawer': f"drawer_{chip_key.replace('chip','')}_{forme}_{idx}",
                                'forme': forme,
                                'denomination': denom
                            })
                            idx += 1
                chip_structure[chip_key] = drawers

            total_chips = len(chip_structure)
            total_drawers = sum(len(v) for v in chip_structure.values())
            stats = {
                'total_chips': total_chips,
                'total_drawers': total_drawers,
                'avg_drawers_per_chip': (total_drawers / total_chips) if total_chips else 0
            }

            return JSONResponse(content={
                'status': 'success',
                'universe': universe,
                'chip_structure': chip_structure,
                'statistics': stats
            })

    except Exception as e:
        logger.error(f"Erreur chip-drawers-structure for {universe}: {e}")
        if conn:
            conn.rollback()
        return JSONResponse(content={'status': 'error', 'universe': universe, 'error': str(e)})
    finally:
        if conn:
            conn.close()


# @api_app.get("/analytics/temporal-periods/{universe}")
async def get_temporal_periods(
    universe: str,
    session_id: int | None = Query(None),
    session_name: str | None = Query(None)
):
    """Retourne les bornes de dates disponibles pour un univers.

    Champs principaux (utilisés côté frontend):
    - available (bool)
    - earliest_date (YYYY-MM-DD)
    - latest_date (YYYY-MM-DD)
    - total_days
    - total_records
    """
    def _fallback_periods_from_sessions(conn_local):
        # Session source: work_sessions/session_draws (utilisé par /api/unified/...)
        with conn_local.cursor(cursor_factory=RealDictCursor) as cur:
            if session_id is not None:
                cur.execute(
                    """
                    SELECT MIN(sd.draw_date) AS earliest_date,
                           MAX(sd.draw_date) AS latest_date,
                           COUNT(*)          AS total_records
                    FROM session_draws sd
                    WHERE sd.session_id = %s
                      AND sd.draw_date IS NOT NULL
                      AND sd.is_completed = true
                    """,
                    (session_id,),
                )
                return cur.fetchone() or {}

            if session_name:
                cur.execute(
                    """
                    SELECT MIN(sd.draw_date) AS earliest_date,
                           MAX(sd.draw_date) AS latest_date,
                           COUNT(*)          AS total_records
                    FROM session_draws sd
                    JOIN work_sessions ws ON ws.id = sd.session_id
                    WHERE LOWER(ws.name) = LOWER(%s)
                      AND sd.draw_date IS NOT NULL
                      AND sd.is_completed = true
                    """,
                    (session_name,),
                )
                return cur.fetchone() or {}

            # Si une session est active, l'utiliser implicitement
            try:
                cur.execute(
                    """
                    SELECT id, name, lottery_type
                    FROM work_sessions
                    WHERE is_active = true
                    ORDER BY id DESC
                    LIMIT 1
                    """
                )
                active = cur.fetchone() or {}
                active_id = active.get('id')
                if active_id:
                    cur.execute(
                        """
                        SELECT MIN(sd.draw_date) AS earliest_date,
                               MAX(sd.draw_date) AS latest_date,
                               COUNT(*)          AS total_records
                        FROM session_draws sd
                        WHERE sd.session_id = %s
                          AND sd.draw_date IS NOT NULL
                          AND sd.is_completed = true
                        """,
                        (active_id,),
                    )
                    row_active = cur.fetchone() or {}
                    if (row_active.get('total_records') or 0) > 0:
                        return row_active
            except Exception as e:
                logger.warning(f"temporal-periods: active session fallback failed for {universe}: {e}")
            with conn_local.cursor(cursor_factory=RealDictCursor) as cur2:
                cur2.execute(
                    """
                    SELECT MIN(sd.draw_date) AS earliest_date,
                           MAX(sd.draw_date) AS latest_date,
                           COUNT(*)          AS total_records
                    FROM session_draws sd
                    WHERE sd.draw_date IS NOT NULL
                      AND sd.is_completed = true
                    """
                )
                return cur2.fetchone() or {}

    conn = None
    try:
        conn = get_db_connection()
        try:
            row = _fallback_periods_from_sessions(conn)
        except Exception as e:
            logger.warning(f"Fallback temporal-periods via sessions failed for {universe}: {e}")
            row = {}

        if not (row.get('total_records') or 0):
            try:
                row = _fallback_periods_from_sessions(conn)
            except Exception:
                row = {}

        earliest = row.get('earliest_date')
        latest = row.get('latest_date')
        total_records = int(row.get('total_records') or 0)

        def _to_date_str(value):
            if value is None:
                return None
            if isinstance(value, datetime):
                return value.date().isoformat()
            if isinstance(value, date):
                return value.isoformat()
            if isinstance(value, str):
                # yyyy-mm-dd or yyyy-mm-ddTHH:MM...
                try:
                    return datetime.fromisoformat(value).date().isoformat()
                except Exception:
                    return value
            return str(value)

        earliest_str = _to_date_str(earliest)
        latest_str = _to_date_str(latest)

        if earliest_str and latest_str:
            try:
                d0 = datetime.fromisoformat(earliest_str).date()
                d1 = datetime.fromisoformat(latest_str).date()
                total_days = (d1 - d0).days + 1
            except Exception:
                total_days = None
        else:
            total_days = None

        available = bool(total_records and earliest_str and latest_str)

        # Réponse stable (pas de 404) même si l'univers n'a pas de données.
        return {
            'status': 'success',
            'universe': universe,
            'available': available,
            'earliest_date': earliest_str,
            'latest_date': latest_str,
            'total_days': total_days,
            'total_records': total_records,
            # alias compat
            'start_date': earliest_str,
            'end_date': latest_str,
        }

    except Exception as e:
        logger.error(f"Erreur temporal-periods for {universe}: {e}")
        if conn:
            conn.rollback()
        return {
            'status': 'error',
            'universe': universe,
            'available': False,
            'earliest_date': None,
            'latest_date': None,
            'total_days': None,
            'total_records': 0,
            'error': str(e)
        }
    finally:
        if conn:
            conn.close()


# Désactivé: utiliser le endpoint dans analytics.py qui use AnalysisService pour cohérence
# @api_app.get("/analytics/temporal-data/{univers}")
async def get_temporal_data(
    univers: str,
    date_start: str,
    date_end: str,
    marking_type: str = 'drawer',
    session_id: int | None = Query(None),
    session_name: str | None = Query(None)
):
    """Retourne les occurrences agrégées par chip pour une plage de dates.
    Fournit pour chaque chip: count, attributes (drawer ids) et details (drawer, forme, chip, draw_date).
    """
    try:
        conn = get_db_connection()
        from backend.app.services.journal_service_v2 import JournalServiceV2
        from backend.app.services.combination_service import CombinationService

        def _fetch_draw_rows():
            # Important: un tirage peut appartenir à plusieurs univers selon ses combinaisons.
            # Donc on ne filtre JAMAIS les tirages par univers ici. L'univers sert uniquement
            # au filtrage après lookup des combinaisons dans le journal.

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if session_id is not None:
                    cur.execute(
                        """
                        SELECT sd.draw_number,
                               sd.draw_date,
                               sd.winning_numbers
                        FROM session_draws sd
                        WHERE sd.session_id = %s
                          AND sd.is_completed = true
                          AND sd.draw_date BETWEEN %s AND %s
                        ORDER BY sd.draw_date, sd.draw_number
                        """,
                        (session_id, date_start, date_end)
                    )
                    return cur.fetchall()

                if session_name:
                    cur.execute(
                        """
                        SELECT sd.draw_number,
                               sd.draw_date,
                               sd.winning_numbers
                        FROM session_draws sd
                        JOIN work_sessions ws ON ws.id = sd.session_id
                        WHERE LOWER(ws.name) = LOWER(%s)
                          AND sd.is_completed = true
                          AND sd.draw_date BETWEEN %s AND %s
                        ORDER BY sd.draw_date, sd.draw_number
                        """,
                        (session_name, date_start, date_end)
                    )
                    return cur.fetchall()

                # Fallback: session active (sans condition sur l'univers)
                cur.execute(
                    """
                    SELECT id
                    FROM work_sessions
                    WHERE is_active = true
                    ORDER BY id DESC
                    LIMIT 1
                    """
                )
                active = cur.fetchone() or {}
                active_id = active.get('id')
                if not active_id:
                    return []

                cur.execute(
                    """
                    SELECT sd.draw_number,
                           sd.draw_date,
                           sd.winning_numbers
                    FROM session_draws sd
                    WHERE sd.session_id = %s
                      AND sd.is_completed = true
                      AND sd.draw_date BETWEEN %s AND %s
                    ORDER BY sd.draw_date, sd.draw_number
                    """,
                    (active_id, date_start, date_end)
                )
                return cur.fetchall()

        rows = _fetch_draw_rows()

        def _normalize_numbers(wn):
            numbers_local: list[int] = []
            if isinstance(wn, (list, tuple)):
                for x in wn:
                    try:
                        numbers_local.append(int(x))
                    except Exception:
                        continue
            elif isinstance(wn, str):
                import re
                numbers_local = [int(x) for x in re.findall(r"\d+", wn)]
            return numbers_local

        target_universe = (univers or '').strip().lower()
        combo_cache: dict[tuple[int, int], dict] = {}

        occurrences: dict[str, dict] = {}
        drawers_data: dict[str, dict] = {}
        total_draws = 0
        matched_entries = 0

        for draw in rows:
            wn = draw.get('winning_numbers')
            draw_date = draw.get('draw_date')
            numbers = _normalize_numbers(wn)
            if len(numbers) < 2:
                continue

            total_draws += 1

            combos = CombinationService.generate_combinations(numbers)
            for num1, num2 in combos:
                a = int(num1)
                b = int(num2)
                if a > b:
                    a, b = b, a

                cache_key = (a, b)
                if cache_key in combo_cache:
                    entry = combo_cache[cache_key]
                else:
                    entry = JournalServiceV2.generate_journal_entry(a, b)
                    combo_cache[cache_key] = entry

                if not entry or entry.get('error'):
                    continue

                entry_universe = (entry.get('univers') or '').strip().lower()
                if entry_universe != target_universe:
                    continue

                matched_entries += 1

                chip_str = entry.get('chip')
                chip_num = None
                if isinstance(chip_str, str) and chip_str.startswith('chip'):
                    try:
                        chip_num = int(chip_str.replace('chip', ''))
                    except Exception:
                        chip_num = None
                elif isinstance(chip_str, int):
                    chip_num = chip_str

                if not chip_num:
                    continue

                # Pour compat UI: key de chip en string
                chip_key = str(chip_num)

                if marking_type == 'drawer':
                    drawer_id = entry.get('drawer') or entry.get('drawer_name')
                    if not drawer_id:
                        drawer_id = f"drawer-chip{chip_num}-{entry.get('forme') or 'N/A'}"

                    if drawer_id not in drawers_data:
                        drawers_data[drawer_id] = {
                            'count': 0,
                            'attributes': [],
                            'details': [],
                            'drawer_name': entry.get('drawer_name') or drawer_id,
                            'forme': entry.get('forme'),
                            'denomination': entry.get('denomination')
                        }

                    drawers_data[drawer_id]['count'] += 1
                    if chip_num not in drawers_data[drawer_id]['attributes']:
                        drawers_data[drawer_id]['attributes'].append(chip_num)

                    drawers_data[drawer_id]['details'].append({
                        'attribute': drawer_id,
                        'type': marking_type,
                        'drawer': drawer_id,
                        'drawer_name': entry.get('drawer_name') or drawer_id,
                        'forme': entry.get('forme'),
                        'denomination': entry.get('denomination'),
                        'chip': chip_num,
                        'draw_date': str(draw_date),
                        'num1': a,
                        'num2': b
                    })
                    continue

                if chip_key not in occurrences:
                    occurrences[chip_key] = {
                        'count': 0,
                        'attributes': [],
                        'details': []
                    }

                occurrences[chip_key]['count'] += 1

                if marking_type == 'chip':
                    attribute_value = chip_num
                elif marking_type == 'combination':
                    attribute_value = f"{a}-{b}"
                elif marking_type == 'denomination':
                    attribute_value = entry.get('denomination')
                elif marking_type == 'forme':
                    attribute_value = entry.get('forme')
                elif marking_type == 'tome':
                    attribute_value = entry.get('tome')
                elif marking_type == 'granque':
                    attribute_value = entry.get('granque_name')
                else:
                    attribute_value = entry.get(marking_type)

                if attribute_value and attribute_value not in occurrences[chip_key]['attributes']:
                    occurrences[chip_key]['attributes'].append(attribute_value)

                occurrences[chip_key]['details'].append({
                    'attribute': attribute_value,
                    'type': marking_type,
                    'chip': chip_num,
                    'draw_date': str(draw_date),
                    'num1': a,
                    'num2': b,
                    'drawer': entry.get('drawer'),
                    'drawer_name': entry.get('drawer_name'),
                    'forme': entry.get('forme'),
                    'denomination': entry.get('denomination')
                })

        if marking_type == 'drawer':
            return JSONResponse(content={
                'status': 'success',
                'data': {
                    'drawers': drawers_data, # Return as 'drawers'
                    'total_draws': total_draws,
                    'total_entries': matched_entries,
                    'period_info': {'date_start': date_start, 'date_end': date_end, 'universe': univers, 'marking_type': marking_type}
                }
            })
        else:
            return JSONResponse(content={
                'status': 'success',
                'data': {
                    'occurrences': occurrences,
                    'total_draws': total_draws,
                    'total_entries': matched_entries,
                    'period_info': {'date_start': date_start, 'date_end': date_end, 'universe': univers, 'marking_type': marking_type}
                }
            })

    except Exception as e:
        logger.error(f"Erreur temporal-data pour {univers}: {e}")
        if conn:
            conn.rollback()
        return JSONResponse(content={'status': 'error', 'error': str(e)})
    finally:
        if conn:
            conn.close()


@api_app.post("/temporal-analysis/{univers}")
async def temporal_analysis(univers: str, request_data: dict):
    """Endpoint simple d'analyse temporelle: agrège /temporal-data pour chaque table
    et renvoie des 'patterns' basiques (drawers les plus récurrents).
    """
    try:
        tables_config = request_data.get('tables_config', [])
        marking_type = request_data.get('marking_type', 'drawer')

        aggregated = {}
        patterns = []

        # Pour chaque configuration de table, appeler la logique interne pour récupérer les occurrences
        for cfg in tables_config:
            date_start = cfg.get('dateStart') or cfg.get('date_start')
            date_end = cfg.get('dateEnd') or cfg.get('date_end')

            # Réutiliser la logique de temporal-data en interne
            resp = await get_temporal_data(univers, date_start, date_end, marking_type)
            # resp est une Response/JSONResponse; extraire le contenu
            if isinstance(resp, JSONResponse):
                content = resp.body.decode('utf-8') if hasattr(resp, 'body') else None
                import json
                try:
                    parsed = json.loads(content) if content else {}
                except Exception:
                    parsed = {}
            else:
                parsed = resp

            data = parsed.get('data') if isinstance(parsed, dict) else (parsed or {}).get('data', {})

            for chip_key, info in (data.get('occurrences') or {}).items():
                for attr in info.get('attributes', []):
                    aggregated.setdefault(attr, 0)
                    aggregated[attr] += info.get('count', 1)

        # Construire des patterns simples: drawers triés par occurrences
        for drawer_id, count in sorted(aggregated.items(), key=lambda x: x[1], reverse=True):
            patterns.append({
                'id': drawer_id,
                'type': 'drawer',
                'count': count,
                'confidence': min(1, count / max(1, len(tables_config)))
            })

        return JSONResponse(content={'status': 'success', 'patterns': patterns})

    except Exception as e:
        logger.error(f"Erreur temporal-analysis pour {univers}: {e}")
        import traceback
        return JSONResponse(content={'status': 'error', 'error': str(e), 'traceback': traceback.format_exc()})

@api_app.get("/stats/advanced/{session_id}")
async def get_advanced_session_stats(session_id: str, universe: Optional[str] = Query(None)):
    """
    Récupère les statistiques avancées pour une session donnée.
    Calcule Count, Fréquence, Dernière Sortie, et Écart (Due) pour tous les attributs.
    """
    try:
        # 1. Récupérer les tirages de la session
        try:
             s_id_int = int(session_id)
        except ValueError:
             return JSONResponse(content={"status": "error", "message": "Invalid session ID format"}, status_code=400)
             
        session_draws = session_service.get_session_draws(s_id_int)

        if not session_draws:
             return {"status": "warning", "message": "Aucun tirage trouvé pour cette session", "stats": {}}

        # 2. Déterminer l'univers
        target_universe = universe or "mundo"
        # Essayer de trouver l'univers dans le premier tirage via lottery_name ou autre si besoin, 
        # mais ici on utilise le default.

        # 3. Calculer les stats
        stats = stats_engine.calculate_stats(session_draws, target_universe)
        
        return {
            "status": "success",
            "session_id": session_id,
            "universe": target_universe,
            "total_draws": len(session_draws),
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Erreur calcul statistiques avancées: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur calcul statistiques: {str(e)}")

@api_app.get("/stats/correlations/{session_id}")
def get_session_correlations(session_id: int):
    """
    Retourne les corrélations (Règles d'association) pour une session donnée.
    """
    try:
        # 1. Fetch draws
        draws = session_service.get_session_draws(session_id)
        if not draws:
             return JSONResponse(status_code=404, content={'error': 'Session not found or no draws'})
             
        # Convert objects to dicts
        draws_data = []
        for d in draws:
             # Draws are already dicts from unified_db_session_service
             draws_data.append({
                 'draw_number': d.get('draw_number'),
                 'winning_numbers': d.get('winning_numbers'),
                 'draw_date': d.get('draw_date'),
                 'lottery_name': d.get('lottery_name')
             })
        
        # 2. Run Correlation Analysis
        from backend.app.services.correlation_service import CorrelationService
        
        import os
        db_config = {
            'dbname': os.getenv('DB_NAME', 'katooling_main_system'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'Katulaa_33'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432')
        }
        
        correlation_service = CorrelationService(db_config)
        results = correlation_service.analyze_correlations(draws_data, 'mundo')
        
        return JSONResponse(content={'correlations': results})

    except Exception as e:
        logger.error(f"Error calculating correlations: {e}")
        return JSONResponse(status_code=500, content={'error': str(e)})

@api_app.get("/predict/next/{attribute}")
def predict_next_attribute(attribute: str, universe: str = 'mundo'):
    """
    Prédit la prochaine valeur pour un attribut donné (ex: 'engine', 'forme').
    Utilise le modèle LSTM entraîné sur l'historique réel.
    """
    try:
        from backend.app.ml.models.lstm_predictor import LSTMPredictor
        import os
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # DB Connection
        db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()

        try:
            predictor = LSTMPredictor(attribute_type=attribute, universe=universe)
            
            # Predict
            result = predictor.predict_next(session)
            return JSONResponse(content=result)
            
        finally:
            session.close()

    except Exception as e:
        logger.error(f"Error predicting {attribute}: {e}")
        return JSONResponse(status_code=500, content={'error': str(e)})

# === WIN-TRACKER ENDPOINTS ===

@api_app.get("/win-tracker/opportunities/{universe}")
def get_win_tracker_opportunities(universe: str, session_id: Optional[int] = None, limit: int = 5):
    """
    Retourne les meilleures opportunités d'investissement.
    Si session_id est fourni, analyse uniquement cette session.
    Sinon, analyse tous les tirages disponibles.
    """
    try:
        if session_id:
            opportunities = win_tracker_service.get_best_opportunities_for_session(universe, session_id, limit)
        else:
            opportunities = win_tracker_service.get_best_opportunities(universe, limit)
        
        return JSONResponse(content={
            'status': 'success',
            'universe': universe,
            'session_id': session_id,
            'opportunities': [opp.__dict__ for opp in opportunities]
        })
    except Exception as e:
        logger.error(f"Error getting win-tracker opportunities: {e}")
        return JSONResponse(status_code=500, content={'error': str(e)})

@api_app.get("/win-tracker/split-analysis/{universe}/{zone_type}/{zone_value}")
def get_split_analysis(universe: str, zone_type: str, zone_value: str, session_id: int, lookback_days: int = 180):
    """
    Analyse Split d'une zone (simple ou synthétique).
    Divise les combinaisons en 'ya-played' et 'not-yet-played'.
    """
    try:
        result = split_strategy_service.perform_split(
            universe, session_id, zone_type, zone_value, lookback_days
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in split analysis: {e}")
        return JSONResponse(status_code=500, content={'error': str(e)})

@api_app.get("/win-tracker/analyze/{universe}/{zone_type}/{zone_value}")
def analyze_win_tracker_zone(universe: str, zone_type: str, zone_value: str, session_id: Optional[int] = None):
    """
    Analyse une zone spécifique (ex: petique q1, granque Q3, etc.).
    Si session_id est fourni, analyse uniquement cette session.
    """
    try:
        if session_id:
            analysis = win_tracker_service.analyze_zone_for_session(universe, zone_type, zone_value, session_id)
        else:
            analysis = win_tracker_service.analyze_zone(universe, zone_type, zone_value)
        
        if not analysis:
            return JSONResponse(status_code=404, content={'error': 'Zone analysis failed'})
        
        return JSONResponse(content={
            'status': 'success',
            'universe': universe,
            'session_id': session_id,
            'analysis': analysis.__dict__
        })
    except Exception as e:
        logger.error(f"Error analyzing zone: {e}")
        return JSONResponse(status_code=500, content={'error': str(e)})

@api_app.get("/win-tracker/portfolio/{universe}")
def calculate_win_tracker_portfolio(universe: str, budget: int = 500, session_id: Optional[int] = None):
    """
    Calcule une stratégie de portefeuille optimale avec le budget donné.
    Si session_id est fourni, analyse uniquement cette session.
    """
    try:
        if session_id:
            portfolio = win_tracker_service.calculate_portfolio_strategy_for_session(universe, session_id, budget)
        else:
            portfolio = win_tracker_service.calculate_portfolio_strategy(universe, budget)
        
        return JSONResponse(content={
            'status': 'success',
            'portfolio': portfolio
        })
    except Exception as e:
        logger.error(f"Error calculating portfolio: {e}")
        return JSONResponse(status_code=500, content={'error': str(e)})

@api_app.get("/win-tracker/statistics/{universe}")
def get_win_tracker_statistics(universe: str, session_id: Optional[int] = None):
    """
    Retourne les statistiques générales des zones.
    Si session_id est fourni, analyse uniquement cette session.
    """
    try:
        if session_id:
            stats = win_tracker_service.get_zone_statistics_for_session(universe, session_id)
        else:
            stats = win_tracker_service.get_zone_statistics(universe)
        
        return JSONResponse(content={
            'status': 'success',
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return JSONResponse(status_code=500, content={'error': str(e)})



@api_app.get("/denomination/{universe}/{denomination}")
async def get_denomination_details(universe: str, denomination: str):
    try:
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        
        # Décoder l'URL et nettoyer la dénomination
        import urllib.parse
        clean_denomination = urllib.parse.unquote(denomination)
        
        print(f"[DEBUG] Recherche dénomination: '{clean_denomination}' dans {universe}")
        
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

@api_app.post("/filter/{universe}")
async def apply_filters(universe: str, filters: dict):
    try:
        from backend.katula_complete_service import KatulaCompleteService
        service = KatulaCompleteService()
        return service.apply_filters(universe, filters)
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.post("/katula/analyze-session")
async def analyze_session_with_katula(analysis_data: dict):
    """Analyse session avec VRAIES données PostgreSQL filtrées par univers"""
    try:
        from backend.app.services.journal_service_v2 import JournalServiceV2
        from itertools import combinations as combos_func
        
        session_id = analysis_data.get('session_id')
        draws = analysis_data.get('draws', [])
        # Prioriser la clé française 'univers' si fournie, sinon accepter 'universe'
        # Prioriser la clé française 'univers' si fournie, sinon accepter 'universe'
        universe = analysis_data.get('univers') or analysis_data.get('universe') or 'mundo'
        
        print(f"\n=== ANALYSE KATULA ===")
        print(f"[DEBUG] analysis_data keys: {list(analysis_data.keys())}")
        print(f"[DEBUG] universe RAW (fr) value: '{analysis_data.get('univers')}'")
        print(f"[DEBUG] universe RAW (en) value: '{analysis_data.get('universe')}'")
        print(f"[DEBUG] universe FINAL value (prioritized): '{universe}'")
        print(f"Session: {session_id}, Universe: {universe}, Draws: {len(draws)}")
        
        if not draws:
            return {"error": "Aucun tirage à analyser"}
        
        analyzed_draws = []
        for draw in draws:
            if not draw.get('winning_numbers'):
                continue
            
            print(f"\nTirage {draw.get('draw_date')}: {draw['winning_numbers']}")
            
            journal_entries = []
            combos = list(combos_func(draw['winning_numbers'], 2))
            
            for n1, n2 in combos:
                # REGLE METIER: num1 < num2 dans la BD
                num1, num2 = (n1, n2) if n1 < n2 else (n2, n1)
                entry = JournalServiceV2.generate_journal_entry(num1, num2)
                
                # Ignorer les combinaisons qui n'existent pas ou pas dans le bon univers
                if "error" in entry:
                    print(f"  {num1}-{num2}: SKIP (pas dans BD)")
                    continue
                    
                if entry.get('univers') != universe:
                    print(f"  {num1}-{num2}: SKIP (univers={entry.get('univers')} != {universe})")
                    continue
                
                print(f"  {num1}-{num2}: OK (univers={entry.get('univers')})")
                
                # Utiliser UNIQUEMENT les vraies données PostgreSQL
                journal_entries.append({
                    'combination': [num1, num2],
                    'combination_str': entry.get('combination', f"{num1}-{num2}"),  # Colonne 'combination' de la BD
                    'denomination': entry.get('denomination', 'N/A'),  # Colonne 'denomination' de la BD
                    'drawer': entry.get('drawer'),  # Colonne 'drawer' de la BD
                    'drawer_name': entry.get('drawer_name'),
                    'num1_analysis': {
                        'number': num1,
                        'chip': entry.get('chip'),
                        'forme': entry.get('forme'),
                        'denomination': entry.get('denomination'),
                        'drawer': entry.get('drawer'),
                        'drawer_name': entry.get('drawer_name'),
                        'petique': entry.get('petique'),
                        'tome': entry.get('tome'),
                        'granque_name': entry.get('granque_name'),
                        'position': {
                            'ligne': entry.get('ligne'),
                            'colonne': entry.get('colonne')
                        },
                        'alpha_ranking': entry.get('alpha_ranking'),
                        'engine': entry.get('engine'),
                        'beastie': entry.get('beastie')
                    },
                    'num2_analysis': {
                        'number': num2,
                        'chip': entry.get('chip'),
                        'forme': entry.get('forme'),
                        'denomination': entry.get('denomination'),
                        'drawer': entry.get('drawer'),
                        'drawer_name': entry.get('drawer_name'),
                        'petique': entry.get('petique'),
                        'tome': entry.get('tome'),
                        'granque_name': entry.get('granque_name'),
                        'position': {
                            'ligne': entry.get('ligne'),
                            'colonne': entry.get('colonne')
                        },
                        'alpha_ranking': entry.get('alpha_ranking'),
                        'engine': entry.get('engine'),
                        'beastie': entry.get('beastie')
                    },
                    'univers': entry.get('univers'),
                    'parite_id': entry.get('parite_id'),
                    'unidos_id': entry.get('unidos_id'),
                    'quartier': entry.get('quartier'),
                    'region': entry.get('region'),
                    'gentile': entry.get('gentile')
                })
            
            print(f"  Total: {len(journal_entries)} combinaisons pour {universe}")
            
            # Si AUCUNE combinaison trouvée pour ce tirage -> NO-HOLD
            if len(journal_entries) == 0:
                print(f"  => NO-HOLD: Aucune combinaison dans {universe}")
                journal_entries.append({
                    'combination': [],
                    'combination_str': 'NO-HOLD',
                    'denomination': 'NO-HOLD',
                    'status': 'no_hold',
                    'num1_analysis': {},
                    'num2_analysis': {},
                    'univers': 'no_hold'
                })
            
            analyzed_draws.append({
                'draw_number': draw.get('draw_number'),
                'draw_date': draw.get('draw_date'),
                'lottery_name': draw.get('lottery_name'),
                'winning_numbers': draw['winning_numbers'],
                'katula_analysis': {
                    'total_combinations': len(journal_entries),
                    'journal_entries': journal_entries,
                    'universe': universe
                }
            })
        
        print(f"\n=== RESULTAT: {len(analyzed_draws)} tirages analysés ===")
        
        return {
            "status": "success",
            "session_id": session_id,
            # Fournir les deux clés pour compatibilité
            "universe": universe,
            "univers": universe,
            "total_draws": len(analyzed_draws),
            "analyzed_draws": analyzed_draws
        }
        
    except Exception as e:
        import traceback
        print(f"\n=== ERREUR ===")
        print(traceback.format_exc())
        return {"error": f"Erreur analyse Katula: {str(e)}", "traceback": traceback.format_exc()}
    
@api_app.post("/katula/analyze-session-old")
async def analyze_session_with_katula_old(analysis_data: dict):
    """Analyse une session avec la méthode Katula en utilisant la table combinations"""
    try:
        session_id = analysis_data.get('session_id')
        draws = analysis_data.get('draws', [])
        # Prioriser la clé française 'univers' si fournie, sinon accepter 'universe'
        universe = analysis_data.get('univers') or analysis_data.get('universe') or 'mundo'
        
        if not draws:
            return {"error": "Aucun tirage à analyser"}
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        analyzed_draws = []
        for draw in draws:
            if not draw.get('winning_numbers'):
                continue
                
            katula_analysis = analyze_numbers_with_katula_db(
                draw['winning_numbers'], 
                universe,
                cursor
            )
            
            analyzed_draws.append({
                'draw_number': draw.get('draw_number'),
                'draw_date': draw.get('draw_date'),
                'lottery_name': draw.get('lottery_name'),
                'winning_numbers': draw['winning_numbers'],
                'katula_analysis': katula_analysis
            })
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "session_id": session_id,
            "universe": universe,
            "univers": universe,
            "total_draws": len(analyzed_draws),
            "analyzed_draws": analyzed_draws
        }
        
    except Exception as e:
        import traceback
        return {"error": f"Erreur analyse Katula: {str(e)}", "traceback": traceback.format_exc()}

def analyze_numbers_with_katula_db(numbers, universe, cursor):
    """Analyse des numéros avec la méthode Katula en utilisant la table combinations"""
    from itertools import combinations as combos_func
    
    combos = list(combos_func(numbers, 2))
    
    journal_entries = []
    for combo in combos:
        num1, num2 = combo
        
        num1_data = get_katula_data_for_number(num1, universe, cursor)
        num2_data = get_katula_data_for_number(num2, universe, cursor)
        
        journal_entries.append({
            'combination': [num1, num2],
            'denomination': f"{num1}-{num2}",
            'num1_analysis': num1_data,
            'num2_analysis': num2_data
        })
    
    character_analysis = {
        'formes': {},
        'granques': {},
        'petiques': {},
        'tomes': {}
    }
    
    for entry in journal_entries:
        for num_key in ['num1_analysis', 'num2_analysis']:
            analysis = entry[num_key]
            
            forme = analysis.get('forme', 'N/A')
            character_analysis['formes'][forme] = character_analysis['formes'].get(forme, 0) + 1
            
            granque = analysis.get('granque_name', 'N/A')
            character_analysis['granques'][granque] = character_analysis['granques'].get(granque, 0) + 1
            
            petique = analysis.get('petique', 'N/A')
            character_analysis['petiques'][petique] = character_analysis['petiques'].get(petique, 0) + 1
            
            tome = analysis.get('tome', 'N/A')
            character_analysis['tomes'][tome] = character_analysis['tomes'].get(tome, 0) + 1
    
    return {
        'total_combinations': len(combos),
        'journal_entries': journal_entries,
        'character_analysis': character_analysis
    }

def get_katula_data_for_number(number, universe, cursor):
    """Récupère TOUTES les données Katula pour un numéro depuis la table combinations"""
    try:
        chip_num = number if number <= 48 else number % 48 or 48
        chip_id = f"chip{chip_num}"
        
        # Récupérer TOUTES les lignes pour ce chip (une par forme/dénomination)
        cursor.execute("""
            SELECT forme, denomination, petique, tome, granque_name, ligne, colonne, alpha_ranking
            FROM combinations
            WHERE univers = %s AND chip = %s
            ORDER BY forme, denomination
        """, (universe, chip_id))
        
        results = cursor.fetchall()
        
        if results:
            # Retourner toutes les combinaisons possibles pour ce numéro
            all_combinations = []
            for result in results:
                all_combinations.append({
                    'forme': result[0],
                    'denomination': result[1],
                    'petique': result[2],
                    'tome': result[3],
                    'granque_name': result[4],
                    'ligne': result[5],
                    'colonne': result[6],
                    'alpha_ranking': result[7] if len(result) > 7 else None
                })
            
            # Utiliser la première comme défaut
            first = results[0]
            return {
                'number': number,
                'chip': chip_id,
                'chip_number': chip_num,
                'forme': first[0],
                'denomination': first[1],
                'petique': first[2],
                'tome': first[3],
                'granque_name': first[4],
                'position': {
                    'ligne': first[5],
                    'colonne': first[6],
                    'coordinates': f"{first[5]}{first[6]}"
                },
                'alpha_ranking': first[7] if len(first) > 7 else None,
                'all_combinations': all_combinations  # Toutes les combinaisons possibles
            }
        else:
            return {
                'number': number,
                'chip': chip_id,
                'chip_number': chip_num,
                'forme': 'N/A',
                'denomination': f"num_{number}",
                'petique': 'N/A',
                'tome': 'N/A',
                'granque_name': 'N/A',
                'position': {'ligne': 0, 'colonne': 0, 'coordinates': '00'},
                'all_combinations': []
            }
    except Exception as e:
        return {'number': number, 'error': str(e)}

def get_forme_for_number(num, universe):
    """Détermine la forme selon le numéro et l'univers"""
    formes_base = ['carre', 'triangle', 'cercle', 'rectangle']
    return formes_base[num % 4]

def get_engine_for_number(num):
    """Détermine l'engine selon le numéro"""
    engines = ['car', 'train', 'bus', 'truck', 'bike', 'plane', 'boat', 'rocket']
    return engines[num % len(engines)]

def get_beastie_for_number(num):
    """Détermine le beastie selon le numéro"""
    beasties = ['lion', 'tiger', 'cow', 'horse', 'pig', 'sheep', 'dog', 'cat']
    return beasties[num % len(beasties)]

@api_app.get("/stats/{universe}/{filter_type}/{filter_value}")
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
            
            # Calculer le nombre de tiroirs uniques (paires chip+forme) avec dénomination non vide
            unique_drawers_set = set()
            for item in details:
                # Ne compter que les tiroirs avec une vraie dénomination (pas "---" ou vide)
                if item["denomination"] and item["denomination"] != "---":
                    unique_drawers_set.add((item["chip"], item["forme"]))
            total_drawers = len(unique_drawers_set)
            
            filtered_chips = list(set([item["chip"] for item in details]))
            granque_details = details if filter_type == "granque" else []
            forme_details = details if filter_type == "forme" else []
        else:
            # Pour les autres filtres, récupérer toutes les paires chip+forme
            cursor.execute(f"""
                SELECT chip, forme
                FROM combinations
                WHERE univers = %s AND {where_clause}
            """, params)
            
            drawer_data = cursor.fetchall()
            # Compter les paires uniques
            unique_drawers_set = set()
            for row in drawer_data:
                unique_drawers_set.add((row[0], row[1]))
            total_drawers = len(unique_drawers_set)
            
            # Récupérer seulement les chips
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
                "total_drawers": total_drawers,
                "effs": "N/A",
                "zed": "N/A"
            },
            "filtered_chips": filtered_chips,
            "granque_details": granque_details if filter_type == "granque" else [],
            "forme_details": forme_details if filter_type == "forme" else []
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@api_app.get("/analytics/katula/matrix/test")
async def get_katula_matrix_test():
    """Endpoint de test qui retourne une matrice 8x6 statique et valide."""
    matrix_grid = [[None for _ in range(6)] for _ in range(8)]
    matrix_grid[0][0] = {
        "chip_number": 1,
        "compartments": [
            {"forme": "carre", "denomination": "TestDenom-1A"},
            {"forme": "triangle", "denomination": "TestDenom-1B"}
        ]
    }
    matrix_grid[2][2] = {
        "chip_number": 15,
        "compartments": [
            {"forme": "cercle", "denomination": "TestDenom-15"}
        ]
    }
    return {
        "status": "success",
        "matrix": matrix_grid
    }

# === FONCTIONS SERVEUR ===

def find_free_port(start_port):
    """Trouve un port libre à partir du port de départ"""
    port = start_port
    max_attempts = 20
    for _ in range(max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            port += 1
    return None

def start_combined_server(port):
    """Démarre le serveur combiné API + fichiers statiques"""
    try:
        base_dir = Path(__file__).parent.absolute()
        frontend_dir = base_dir / "frontend"
        
        os.chdir(base_dir)
        
        if not frontend_dir.exists():
            print(f"[ERREUR] Dossier frontend introuvable: {frontend_dir}")
            return
        
        app = FastAPI()
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Monter l'API avec le préfixe /api
        app.mount("/api", api_app)
        
        # Monter le répertoire frontend
        app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
        
        print("\n=== SERVEUR EAZZYCALCULATOR ===\n")
        print(f"Répertoire de travail: {os.getcwd()}")
        print(f"Dossier frontend: {frontend_dir}")
        print(f"\nURLs d'accès:")
        print(f"- Interface: http://localhost:{port}/")
        print(f"- Katula Dynamic: http://localhost:{port}/katula-dynamic.html")
        print(f"- Smart Input: http://localhost:{port}/smart-input.html")
        print(f"- API: http://localhost:{port}/api")
        print(f"- API Katula: http://localhost:{port}/api/formes/real/mundo/chip/chip1")
        
        def open_browser():
            time.sleep(2)
            import webbrowser
            webbrowser.open(f"http://localhost:{port}/katula-dynamic.html")
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        print("\nDémarrage du serveur... (Ctrl+C pour arrêter)")
        print("\nRoutes API disponibles:")
        for route in api_app.routes:
            try:
                methods = getattr(route, 'methods', None)
                method = list(methods)[0] if methods else 'GET'
                path = getattr(route, 'path', None) or getattr(route, 'name', str(route))
                print(f"   - {method} /api{path}")
            except Exception:
                # Fallback for mount or unexpected route objects
                path = getattr(route, 'path', None) or str(route)
                print(f"   - GET /api{path}")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\nArrêt du serveur...")
    except Exception as e:
        print(f"\n[ERREUR] {e}")
        import traceback
        traceback.print_exc()


@api_app.get("/stats/advanced/{session_id}")
async def get_advanced_session_stats(session_id: str, universe: Optional[str] = Query(None)):
    """
    Récupère les statistiques avancées pour une session donnée.
    Calcule Count, Fréquence, Dernière Sortie, et Écart (Due) pour tous les attributs.
    """
    try:
        # 1. Récupérer les tirages de la session
        session_draws = session_service.get_session_draws(session_id)
        
        if not session_draws:
             return {"status": "warning", "message": "Aucun tirage trouvé pour cette session", "stats": {}}

        # 2. Déterminer l'univers
        # Soit passé en paramètre, soit déduit de la session (si dispo), soit 'mundo' par défaut
        target_universe = universe or "mundo"
        # Idéalement, la session devrait stocker l'univers. On regarde si le premier tirage a l'info.
        if not universe and session_draws and 'universe' in session_draws[0]:
            target_universe = session_draws[0]['universe']

        # 3. Calculer les stats
        stats = stats_engine.calculate_stats(session_draws, target_universe)
        
        return {
            "status": "success",
            "session_id": session_id,
            "universe": target_universe,
            "total_draws": len(session_draws),
            "stats": stats
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur calcul statistiques: {str(e)}")

# Point d'entrée
if __name__ == "__main__":
    print("=== DEMARRAGE DU SERVEUR EAZZYCALCULATOR ===")
    
    # Port 8881 pour le serveur intégré (backend + frontend)
    port = 8881
    
    # Démarrer le serveur
    start_combined_server(port)
