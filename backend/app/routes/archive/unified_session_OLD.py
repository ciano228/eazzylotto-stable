"""
Routes pour les sessions unifiées
Utilise UnifiedDBSessionService au lieu de SessionService
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import sys
import os

# Ajouter le chemin backend pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.unified_db_session_service_fixed import UnifiedDBSessionService

router = APIRouter()
unified_service = UnifiedDBSessionService()

class LotteryScheduleItem(BaseModel):
    name: str
    day_offset: int  # 0=lundi, 1=mardi, etc.

class SessionCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    lottery_type: str
    numbers_per_draw: int
    total_draws: int
    lottery_schedule: Optional[List[LotteryScheduleItem]] = []
    start_date: Optional[str] = None  # Format: "DD/MM/YYYY"
    number_range_min: int = 1
    number_range_max: int = 90
    cycle_length: Optional[int] = 7

@router.get("/session/sessions")
async def list_sessions():
    """Liste toutes les sessions de work_sessions"""
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
        
        cursor.close()
        conn.close()
        
        return {"sessions": sessions, "total": len(sessions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.post("/session")
async def create_session(session_data: SessionCreate):
    """Créer une nouvelle session dans unified_sessions"""
    try:
        # Convertir les données pour UnifiedDBSessionService
        schedule_for_db = []
        
        # Construire un planning de tirages basé sur lottery_schedule
        if session_data.lottery_schedule and session_data.start_date:
            start_date = datetime.strptime(session_data.start_date, "%d/%m/%Y")
            draw_num = 1
            
            # Générer les tirages sur plusieurs semaines
            total_draws = session_data.total_draws
            cycle_length = session_data.cycle_length or 7
            
            # Calculer combien de cycles complets
            num_cycles = (total_draws // len(session_data.lottery_schedule)) + 1
            
            for cycle in range(num_cycles):
                for lottery_item in session_data.lottery_schedule:
                    if draw_num > total_draws:
                        break
                    
                    # Calculer la date du tirage
                    days_offset = (cycle * 7) + lottery_item.day_offset
                    draw_date = start_date + timedelta(days=days_offset)
                    
                    schedule_for_db.append({
                        'draw_number': draw_num,
                        'lottery_name': lottery_item.name,
                        'draw_date': draw_date.strftime('%Y-%m-%d')
                    })
                    draw_num += 1
        
        # Créer la session
        session_id = unified_service.create_session({
            'name': session_data.name,
            'description': session_data.description or '',
            'lottery_type': session_data.lottery_type,
            'numbers_per_draw': session_data.numbers_per_draw,
            'number_range_min': session_data.number_range_min,
            'number_range_max': session_data.number_range_max,
            'total_draws': session_data.total_draws,
            'cycle_length': session_data.cycle_length or 7,
            'lottery_schedule': [{'name': item.name, 'day_offset': item.day_offset} for item in (session_data.lottery_schedule or [])],
            'start_date': start_date if session_data.start_date else None,
            'schedule': schedule_for_db
        })
        
        if not session_id:
            raise HTTPException(status_code=500, detail="Échec création session")
        
        return {
            "message": "Session créée avec succès",
            "session_id": session_id,
            "id": session_id,
            "name": session_data.name
        }
        
    except Exception as e:
        print(f"[ERROR] Erreur création session: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur création: {str(e)}")

@router.get("/sessions/{session_id}")
async def get_session(session_id: int):
    """Récupère les détails d'une session depuis work_sessions"""
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

@router.post("/sessions/{session_id}/activate")
async def activate_session(session_id: int):
    """Active une session"""
    try:
        success = unified_service.activate_session(session_id)
        if not success:
            raise HTTPException(status_code=500, detail="Échec activation")
        return {"message": "Session activée", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.get("/session/sessions/active")
async def get_active_session():
    """Récupère la session active"""
    try:
        sessions = unified_service.list_all_sessions()
        active = [s for s in sessions if s.get('is_active')]
        if not active:
            raise HTTPException(status_code=404, detail="Aucune session active")
        return active[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.get("/sessions/{session_id}/draws")
async def get_session_draws(session_id: int):
    """Récupère les tirages d'une session depuis session_draws"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host='localhost', database='katooling_main_system',
            user='postgres', password='Katulaa_33', port=5432
        )
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM session_draws 
            WHERE session_id = %s 
            ORDER BY draw_number
        """, (session_id,))
        
        columns = [desc[0] for desc in cursor.description]
        draws = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return draws
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
class DrawResult(BaseModel):
    numbers: List[int]
    draw_date: str
    lottery_name: str
    is_no_draw: Optional[bool] = False
    no_draw_reason: Optional[str] = None

@router.post("/sessions/{session_id}/draws/{draw_number}")
async def save_draw_result(session_id: int, draw_number: int, draw_data: DrawResult):
    """Sauvegarde le résultat d'un tirage"""
    try:
        success = unified_service.save_draw_result(session_id, draw_number, {
            'numbers': draw_data.numbers,
            'draw_date': draw_data.draw_date,
            'lottery_name': draw_data.lottery_name,
            'is_no_draw': draw_data.is_no_draw,
            'no_draw_reason': draw_data.no_draw_reason
        })
        
        if success:
            return {"message": "Tirage sauvegardé avec succès", "draw_number": draw_number}
        else:
            raise HTTPException(status_code=500, detail="Échec de la sauvegarde")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.delete("/sessions/{session_id}/draws/{draw_number}")
async def delete_draw_result(session_id: int, draw_number: int):
    """Supprime un tirage"""
    try:
        success = unified_service.delete_draw(session_id, draw_number)
        if success:
            return {"message": "Tirage supprimé avec succès"}
        else:
            raise HTTPException(status_code=404, detail="Tirage non trouvé")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.get("/sessions/{session_id}/test-db")
async def test_database_connection(session_id: int):
    """Test de connexion à la base de données pour une session"""
    try:
        draws = unified_service.get_session_draws(session_id)
        return {
            "status": "success",
            "message": "Connexion BD réussie",
            "draws_count": len(draws),
            "draws": draws
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BD: {str(e)}")

@router.post("/sessions/{session_id}/direct-save")
async def direct_save_draw(session_id: int, draw_data: dict):
    """Sauvegarde directe en base de données"""
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
        
        draw_number = draw_data.get('draw_number')
        numbers = draw_data.get('numbers', [])
        lottery_name = draw_data.get('lottery_name', '')
        draw_date = draw_data.get('draw_date')
        is_completed = len(numbers) > 0
        
        print(f'SAUVEGARDE DIRECTE: Session {session_id}, Draw {draw_number}')
        print(f'Numbers: {numbers}, Completed: {is_completed}')
        
        # Créer la table si elle n'existe pas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_draws (
                id SERIAL PRIMARY KEY,
                session_id INTEGER,
                draw_number INTEGER,
                lottery_name VARCHAR(255),
                draw_date DATE,
                winning_numbers INTEGER[],
                is_completed BOOLEAN DEFAULT FALSE,
                is_no_draw BOOLEAN DEFAULT FALSE,
                no_draw_reason TEXT,
                cycle_position INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Supprimer et recréer
        cursor.execute("""
            DELETE FROM session_draws 
            WHERE session_id = %s AND draw_number = %s
        """, (session_id, draw_number))
        
        cursor.execute("""
            INSERT INTO session_draws (
                session_id, draw_number, lottery_name, draw_date,
                winning_numbers, is_completed, cycle_position
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            session_id, draw_number, lottery_name, draw_date,
            numbers, is_completed, draw_number
        ))
        
        conn.commit()
        
        # Vérification
        cursor.execute("""
            SELECT winning_numbers, is_completed 
            FROM session_draws 
            WHERE session_id = %s AND draw_number = %s
        """, (session_id, draw_number))
        
        result = cursor.fetchone()
        print(f'Vérification: {result}')
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": "Sauvegarde directe réussie",
            "verification": result
        }
        
    except Exception as e:
        print(f'ERREUR sauvegarde directe: {e}')
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

@router.post("/session/simple")
async def create_simple_session(data: dict):
    try:
        import psycopg2
        conn = psycopg2.connect(
            host='localhost', database='katooling_main_system',
            user='postgres', password='Katulaa_33', port=5432
        )
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_sessions (
                id SERIAL PRIMARY KEY, name VARCHAR(255), description TEXT,
                total_draws INTEGER, numbers_per_draw INTEGER,
                number_range_min INTEGER, number_range_max INTEGER,
                is_active BOOLEAN DEFAULT TRUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            INSERT INTO work_sessions (name, description, total_draws, numbers_per_draw, number_range_min, number_range_max, lottery_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (data.get('name', 'Test'), data.get('description', ''), data.get('total_draws', 3),
               data.get('numbers_per_draw', 5), data.get('number_range_min', 1), data.get('number_range_max', 90), data.get('lottery_type', '5/90')))
        
        session_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"success": True, "session_id": session_id, "message": "Session créée"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/db/explore")
async def explore_database():
    """Explorer la base de données pour voir les sessions et tirages existants"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host='localhost', database='katooling_main_system',
            user='postgres', password='Katulaa_33', port=5432
        )
        cursor = conn.cursor()
        
        # Lister toutes les tables
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        result = {"tables": tables}
        
        # Explorer work_sessions si elle existe
        if 'work_sessions' in tables:
            cursor.execute("SELECT * FROM work_sessions ORDER BY id DESC LIMIT 10")
            columns = [desc[0] for desc in cursor.description]
            sessions = [dict(zip(columns, row)) for row in cursor.fetchall()]
            result["work_sessions"] = sessions
        
        # Explorer session_draws si elle existe
        if 'session_draws' in tables:
            cursor.execute("""
                SELECT sd.*, ws.name as session_name 
                FROM session_draws sd 
                LEFT JOIN work_sessions ws ON sd.session_id = ws.id 
                ORDER BY sd.session_id, sd.draw_number LIMIT 20
            """)
            columns = [desc[0] for desc in cursor.description]
            draws = [dict(zip(columns, row)) for row in cursor.fetchall()]
            result["session_draws"] = draws
        
        cursor.close()
        conn.close()
        
        return result
        
    except Exception as e:
        return {"error": str(e)}

@router.post("/db/clear-all")
async def clear_all_data():
    """Vider toutes les sessions et tirages"""
    try:
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