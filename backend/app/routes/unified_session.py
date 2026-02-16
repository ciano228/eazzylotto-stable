"""
Routes pour les sessions unifiées - Version corrigée
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

from app.database.connection import get_db
from app.services.journal_service_v2 import JournalServiceV2 as JournalService

router = APIRouter()

class LotteryScheduleItem(BaseModel):
    name: str
    day_offset: int

class SessionCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    lottery_type: str
    numbers_per_draw: int
    total_draws: int
    lottery_schedule: Optional[List[LotteryScheduleItem]] = []
    start_date: Optional[str] = None
    number_range_min: int = 1
    number_range_max: int = 90

class DrawResult(BaseModel):
    numbers: List[int]
    draw_date: str
    lottery_name: str
    is_no_draw: Optional[bool] = False
    no_draw_reason: Optional[str] = None

@router.post("/session")
async def create_session(session_data: SessionCreate):
    """Créer une nouvelle session directement en base"""
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host='localhost', database='katooling_main_system',
            user='postgres', password='Katulaa_33', port=5432
        )
        cursor = conn.cursor()
        
        # Convertir le planning en JSON
        schedule_json = json.dumps([{'name': item.name, 'day_offset': item.day_offset} for item in (session_data.lottery_schedule or [])])
        
        # Convertir la date
        start_date = None
        if session_data.start_date:
            start_date = datetime.strptime(session_data.start_date, "%d/%m/%Y").date()
        
        # Insérer la session
        cursor.execute("""
            INSERT INTO work_sessions (
                name, description, lottery_type, numbers_per_draw, total_draws,
                number_range_min, number_range_max, lottery_schedule, start_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (
            session_data.name,
            session_data.description or '',
            session_data.lottery_type,
            session_data.numbers_per_draw,
            session_data.total_draws,
            session_data.number_range_min,
            session_data.number_range_max,
            schedule_json,
            start_date
        ))
        
        session_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

        # Trigger fix_session_mapping to update session mapping
        try:
            import sys
            import os
            # Ensure backend directory is in path to import fix_session_mapping
            backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            if backend_dir not in sys.path:
                sys.path.append(backend_dir)
            
            from fix_session_mapping import fix_session_mapping
            print("Triggering fix_session_mapping after session creation...")
            fix_session_mapping()
        except Exception as e:
            print(f"Warning: Failed to run fix_session_mapping: {e}")
        
        return {
            "message": "Session créée avec succès",
            "session_id": session_id,
            "id": session_id,
            "name": session_data.name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création: {str(e)}")

@router.post("/sessions/{session_id}/draws/{draw_number}")
async def save_draw_result(session_id: int, draw_number: int, draw_data: DrawResult):
    """Sauvegarde le résultat d'un tirage directement en base"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host='localhost', database='katooling_main_system',
            user='postgres', password='Katulaa_33', port=5432
        )
        cursor = conn.cursor()
        
        # Supprimer l'ancien tirage s'il existe
        cursor.execute("""
            DELETE FROM session_draws 
            WHERE session_id = %s AND draw_number = %s
        """, (session_id, draw_number))
        
        # Insérer le nouveau tirage
        import json
        cursor.execute("""
            INSERT INTO session_draws (
                session_id, draw_number, lottery_name, draw_date,
                winning_numbers, is_completed, is_no_draw
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            session_id, draw_number, draw_data.lottery_name, draw_data.draw_date,
            json.dumps(draw_data.numbers), len(draw_data.numbers) > 0, draw_data.is_no_draw
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Tirage sauvegardé avec succès", "draw_number": draw_number}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.delete("/sessions/{session_id}/draws/{draw_number}")
async def delete_draw_result(session_id: int, draw_number: int):
    """Supprime le résultat d'un tirage spécifié"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host='localhost', database='katooling_main_system',
            user='postgres', password='Katulaa_33', port=5432
        )
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM session_draws 
            WHERE session_id = %s AND draw_number = %s
        """, (session_id, draw_number))
        
        conn.commit()
        
        # Check if anything was deleted
        deleted_count = cursor.rowcount
        
        cursor.close()
        conn.close()
        
        if deleted_count == 0:
             return {"status": "not_found", "message": "Aucun tirage trouvé avec ce numéro"}
             
        return {"status": "success", "message": "Tirage supprimé avec succès"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur suppression: {str(e)}")

@router.get("/session/sessions")
async def list_sessions():
    """Liste toutes les sessions"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host='localhost', database='katooling_main_system',
            user='postgres', password='Katulaa_33', port=5432
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM work_sessions ORDER BY id DESC")
        columns = [desc[0] for desc in cursor.description]
        sessions = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Ajouter l'alias 'universe' pour compatibilité frontend
        for s in sessions:
            if 'lottery_type' in s:
                s['universe'] = s['lottery_type']
        
        cursor.close()
        conn.close()
        
        return {"status": "success", "sessions": sessions, "value": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.get("/sessions/{session_id}")
async def get_session(session_id: int):
    """Récupère les détails d'une session"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host='localhost', database='katooling_main_system',
            user='postgres', password='Katulaa_33', port=5432
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM work_sessions WHERE id = %s", (session_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        columns = [desc[0] for desc in cursor.description]
        session = dict(zip(columns, row))
        
        cursor.close()
        conn.close()
        
        return {"session": session}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.get("/sessions/{session_id}/draws")
async def get_session_draws(
    session_id: int, 
    limit: Optional[int] = Query(None, description="Nombre maximum de tirages à retourner"),
    offset: Optional[int] = Query(0, description="Nombre de tirages à sauter")
):
    """Récupère les tirages d'une session avec pagination optionnelle"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host='localhost', database='katooling_main_system',
            user='postgres', password='Katulaa_33', port=5432
        )
        cursor = conn.cursor()
        
        query = "SELECT * FROM session_draws WHERE session_id = %s ORDER BY draw_number"
        params = [session_id]
        
        if limit is not None:
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
        cursor.execute(query, params)
        
        columns = [desc[0] for desc in cursor.description]
        draws = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return draws
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.post("/sessions/{session_id}/activate")
async def activate_session(session_id: int):
    """Active une session dans work_sessions"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host='localhost', database='katooling_main_system',
            user='postgres', password='Katulaa_33', port=5432
        )
        cursor = conn.cursor()
        
        # Désactiver toutes les autres sessions
        cursor.execute("UPDATE work_sessions SET is_active = false")
        
        # Activer la session demandée
        cursor.execute("UPDATE work_sessions SET is_active = true WHERE id = %s", (session_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Session activée", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.get("/session/sessions/active")
async def get_active_session():
    """Récupère la session active depuis work_sessions"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host='localhost', database='katooling_main_system',
            user='postgres', password='Katulaa_33', port=5432
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM work_sessions WHERE is_active = true ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Aucune session active")
        
        columns = [desc[0] for desc in cursor.description]
        session = dict(zip(columns, row))
        
        cursor.close()
        conn.close()
        
        return {"session": session}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.post("/katula/analyze-session")
async def analyze_session_with_katula(analysis_data: dict):
    """Analyse une session avec la méthode Katula complète"""
    try:
        session_id = analysis_data.get('session_id')
        draws = analysis_data.get('draws', [])
        # Prioriser la clé 'universe' ou 'univers'
        universe = analysis_data.get('universe') or analysis_data.get('univers') or 'mundo'
        
        if not draws:
            return {"error": "Aucun tirage à analyser"}
        
        # Récupérer le cycle_length de la session
        import psycopg2
        conn = psycopg2.connect(
            host='localhost', database='katooling_main_system',
            user='postgres', password='Katulaa_33', port=5432
        )
        cursor = conn.cursor()
        cursor.execute("SELECT cycle_length FROM work_sessions WHERE id = %s", (session_id,))
        result = cursor.fetchone()
        cycle_length = result[0] if result and result[0] else 7
        cursor.close()
        conn.close()
        print(f"✅ Using session cycle_length for periods: {cycle_length}")
        
        db_conn = JournalService._get_connection()
        try:
            # OPTIMISATION: Batch load existing cache
            session_draw_ids = [int(d.get('id')) for d in draws if d.get('id')]
            cache_map = {}
            if session_draw_ids:
                temp_cursor = db_conn.cursor()
                try:
                    # Utiliser ANY(ARRAY[%s]) ou passer un tuple pour ANY(%s)
                    temp_cursor.execute("""
                        SELECT session_draw_id, analysis_results 
                        FROM session_draw_analyses 
                        WHERE session_draw_id = ANY(%s) AND universe = %s
                    """, (session_draw_ids, universe))
                    rows = temp_cursor.fetchall()
                    print(f"🔍 Cache check: found {len(rows)} entries for {len(session_draw_ids)} draws")
                    for row in rows:
                        # row[1] est déjà le JSON parsé grâce à psycopg2 s'il détecte le type JSON
                        if isinstance(row[1], str):
                            cache_map[row[0]] = json.loads(row[1])
                        else:
                            cache_map[row[0]] = row[1]
                except Exception as cache_err:
                    print(f"⚠️ Cache read error: {cache_err}")
                finally:
                    temp_cursor.close()

            # Analyser chaque tirage avec JournalService
            analyzed_draws = []
            new_analyzed_count = 0
            for draw in draws:
                draw_id = draw.get('id')
                
                # Vérifier si on a déjà ce tirage en cache
                if draw_id and int(draw_id) in cache_map:
                    cached_data = cache_map[int(draw_id)]
                    # Recalculer la période (car elle dépend du cycle actuel)
                    try:
                        p_val = (int(draw.get('draw_number')) - 1) // cycle_length + 1
                        cached_data['period'] = p_val
                        if 'katula_analysis' in cached_data and 'journal_entries' in cached_data['katula_analysis']:
                            for e in cached_data['katula_analysis']['journal_entries']:
                                e['period'] = p_val
                    except:
                        pass
                    
                    analyzed_draws.append(cached_data)
                    continue

                # Cas spécial: No Draw
                if draw.get('is_no_draw'):
                    p_val = None
                    if draw.get('draw_number'):
                        try:
                            p_val = (int(draw.get('draw_number')) - 1) // cycle_length + 1
                        except:
                            pass
                    
                    analyzed_entry = {
                        'draw_number': draw.get('draw_number'),
                        'draw_date': draw.get('draw_date'),
                        'lottery_name': draw.get('lottery_name'),
                        'period': p_val,
                        'winning_numbers': [],
                        'katula_analysis': {
                            'universe': universe,
                            'journal_entries': [{
                                'status': 'no_draw',
                                'date': draw.get('draw_date'),
                                'combination': 'NO-DRAW',
                                'univers': universe,
                                'period': p_val
                            }]
                        }
                    }
                    analyzed_draws.append(analyzed_entry)
                    continue

                if not draw.get('winning_numbers'):
                    continue
                    
                # Utiliser le service de journal complet
                journal_data = JournalService.generate_full_journal(draw['winning_numbers'], conn=db_conn)
                
                all_entries = journal_data.get("journal_entries", [])
                universe_entries = [e for e in all_entries if e.get("univers") == universe and e.get("status") == "normal"]
                
                if universe_entries:
                    journal_entries = universe_entries
                else:
                    journal_entries = [{
                        "status": "no_hold",
                        "univers": universe,
                        "combination_str": "NO-HOLD",
                        "date": draw.get('draw_date'),
                        "winning_numbers": draw.get('winning_numbers')
                    }]
                
                p_val = None
                if draw.get('draw_number'):
                    try:
                        p_val = (int(draw.get('draw_number')) - 1) // cycle_length + 1
                    except:
                        pass

                for e in journal_entries:
                    e['period'] = p_val

                analyzed_entry = {
                    'draw_number': draw.get('draw_number'),
                    'draw_date': draw.get('draw_date'),
                    'lottery_name': draw.get('lottery_name'),
                    'period': p_val,
                    'winning_numbers': draw['winning_numbers'],
                    'katula_analysis': {
                        'universe': universe,
                        'journal_entries': journal_entries
                    }
                }
                
                analyzed_draws.append(analyzed_entry)
                new_analyzed_count += 1
                
                # SAUVEGARDE EN CACHE
                if draw_id:
                    save_cursor = db_conn.cursor()
                    try:
                        save_cursor.execute("""
                            INSERT INTO session_draw_analyses (session_draw_id, universe, analysis_results)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (session_draw_id, universe) DO UPDATE 
                            SET analysis_results = EXCLUDED.analysis_results
                        """, (int(draw_id), universe, json.dumps(analyzed_entry, default=str)))
                        db_conn.commit()
                    except Exception as save_err:
                        # print(f"⚠️ Cache save error: {save_err}")
                        db_conn.rollback()
                    finally:
                        save_cursor.close()
            
            if new_analyzed_count > 0:
                print(f"🆕 Analyzed {new_analyzed_count} new draws and updated cache.")
            
            return {
                "status": "success",
                "session_id": session_id,
                "universe": universe,
                "univers": universe,
                "total_draws": len(analyzed_draws),
                "analyzed_draws": analyzed_draws
            }
        finally:
            db_conn.close()


            
    except Exception as e:
        import traceback
        print(f"ERROR in analyze_session_with_katula: {str(e)}")
        traceback.print_exc()
        return {"error": f"Erreur analyse Katula: {str(e)}"}



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

@router.get("/sessions/{session_id}/latest-period")
async def get_latest_period(session_id: int):
    """Récupère la période la plus récente d'une session avec dates auto-remplies"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host='localhost', database='katooling_main_system',
            user='postgres', password='Katulaa_33', port=5432
        )
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT MIN(draw_date) as start_date, MAX(draw_date) as end_date, COUNT(*) as total_draws
            FROM session_draws
            WHERE session_id = %s AND draw_date IS NOT NULL
        """, (session_id,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not result or not result[0]:
            return {
                "status": "no_data",
                "start_date": None,
                "end_date": None,
                "total_draws": 0,
                "universe": "mundo"
            }
        
        start_date, end_date, total_draws = result
        
        return {
            "status": "success",
            "start_date": start_date.strftime("%Y-%m-%d") if start_date else None,
            "end_date": end_date.strftime("%Y-%m-%d") if end_date else None,
            "total_draws": total_draws,
            "universe": "mundo"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.post("/db/clear-all")
async def clear_all_data(
    confirm: Optional[str] = Query(default=None)
):
    """Vider toutes les sessions et tirages"""
    try:
        if confirm != "yes-delete-all":
            raise HTTPException(
                status_code=400,
                detail="Confirmation requise. Utilisez ?confirm=yes-delete-all"
            )
        import psycopg2
        conn = psycopg2.connect(
            host='localhost', database='katooling_main_system',
            user='postgres', password='Katulaa_33', port=5432
        )
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM session_draws")
        cursor.execute("DELETE FROM work_sessions")
        cursor.execute("ALTER SEQUENCE work_sessions_id_seq RESTART WITH 1")
        cursor.execute("ALTER SEQUENCE session_draws_id_seq RESTART WITH 1")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"success": True, "message": "Toutes les données supprimées"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}