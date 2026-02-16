"""
Service utilisant la structure existante complète
Exploite directement les 143 tables et relations existantes
"""
import os
import psycopg2
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class ExistingStructureService:
    
    @staticmethod
    def get_db_connection():
        """Connexion à la vraie base PostgreSQL"""
        DATABASE_URL = os.getenv("DATABASE_URL")
        parts = DATABASE_URL.replace("postgresql://", "").split("@")
        user_pass = parts[0].split(":")
        host_db = parts[1].split("/")
        host_port = host_db[0].split(":")
        
        return psycopg2.connect(
            host=host_port[0],
            port=host_port[1] if len(host_port) > 1 else "5432",
            database=host_db[1],
            user=user_pass[0],
            password=user_pass[1]
        )
    
    @staticmethod
    def get_complete_katula_data(universe: str) -> Dict[str, Any]:
        """Utilise la vraie table_de_katula + combinations + toutes les relations"""
        try:
            conn = ExistingStructureService.get_db_connection()
            cursor = conn.cursor()
            
            # Requête complète utilisant toutes les relations existantes
            cursor.execute("""
                SELECT 
                    tk.chip_id,
                    tk.univers,
                    tk.ligne,
                    tk.colonne,
                    tk.petique,
                    tk.chip,
                    tk.forme,
                    tk.denomination as katula_denomination,
                    c.combination_id,
                    c.num1,
                    c.num2,
                    c.alpha_ranking,
                    c.denomination as combo_denomination,
                    c.granque_name,
                    c.tome,
                    c.engine,
                    c.beastie,
                    c.quartier,
                    c.region,
                    c.gentillee
                FROM table_de_katula tk
                LEFT JOIN combinations c ON (
                    tk.univers = c.univers 
                    AND tk.forme = c.forme 
                    AND tk.denomination = c.denomination
                )
                WHERE tk.univers = %s
                ORDER BY tk.ligne, tk.colonne, c.combination_id
            """, (universe,))
            
            results = cursor.fetchall()
            
            # Organiser les données par position (ligne, colonne)
            positions_data = {}
            
            for row in results:
                (chip_id, univers, ligne, colonne, petique, chip, forme, katula_denom,
                 combo_id, num1, num2, alpha_ranking, combo_denom, granque, tome,
                 engine, beastie, quartier, region, gentillee) = row
                
                position_key = f"{ligne}-{colonne}"
                
                if position_key not in positions_data:
                    positions_data[position_key] = {
                        "chip_id": chip_id,
                        "ligne": ligne,
                        "colonne": colonne,
                        "petique": petique,
                        "chip_name": chip,
                        "formes_data": {},
                        "combinations": [],
                        "granques": set(),
                        "tomes": set(),
                        "engines": set(),
                        "beasties": set()
                    }
                
                # Ajouter les données de forme
                if forme and katula_denom:
                    if forme not in positions_data[position_key]["formes_data"]:
                        positions_data[position_key]["formes_data"][forme] = []
                    
                    positions_data[position_key]["formes_data"][forme].append({
                        "denomination": katula_denom,
                        "source": "table_de_katula"
                    })
                
                # Ajouter les combinaisons liées
                if combo_id:
                    positions_data[position_key]["combinations"].append({
                        "combination_id": combo_id,
                        "numbers": f"{num1}-{num2}",
                        "alpha_ranking": alpha_ranking,
                        "denomination": combo_denom
                    })
                    
                    # Collecter les métadonnées
                    if granque: positions_data[position_key]["granques"].add(granque)
                    if tome: positions_data[position_key]["tomes"].add(tome)
                    if engine: positions_data[position_key]["engines"].add(engine)
                    if beastie: positions_data[position_key]["beasties"].add(beastie)
            
            # Convertir les sets en listes
            for pos_data in positions_data.values():
                pos_data["granques"] = list(pos_data["granques"])
                pos_data["tomes"] = list(pos_data["tomes"])
                pos_data["engines"] = list(pos_data["engines"])
                pos_data["beasties"] = list(pos_data["beasties"])
            
            # Créer la matrice 8x6
            matrix = []
            chip_positions = {}
            
            for row in range(8):
                matrix_row = []
                for col in range(6):
                    ligne_key = f"L{row+1}"
                    colonne_key = f"C{col+1}"
                    position_key = f"{ligne_key}-{colonne_key}"
                    chip_number = row * 6 + col + 1
                    
                    if position_key in positions_data:
                        pos_data = positions_data[position_key]
                        
                        cell_data = {
                            "chip_number": chip_number,
                            "position": f"{row+1}-{col+1}",
                            "chip_name": pos_data["chip_name"],
                            "petique": pos_data["petique"],
                            "formes_data": pos_data["formes_data"],
                            "combinations_count": len(pos_data["combinations"]),
                            "metadata": {
                                "granques": pos_data["granques"],
                                "tomes": pos_data["tomes"],
                                "engines": pos_data["engines"],
                                "beasties": pos_data["beasties"]
                            }
                        }
                        
                        matrix_row.append(cell_data)
                        chip_positions[f"chip_{chip_number}"] = {
                            **cell_data,
                            "row": row + 1,
                            "column": col + 1,
                            "full_combinations": pos_data["combinations"]
                        }
                    else:
                        # Position vide
                        cell_data = {
                            "chip_number": chip_number,
                            "position": f"{row+1}-{col+1}",
                            "chip_name": f"chip{chip_number}",
                            "petique": "unknown",
                            "formes_data": {},
                            "combinations_count": 0,
                            "metadata": {"granques": [], "tomes": [], "engines": [], "beasties": []}
                        }
                        matrix_row.append(cell_data)
                
                matrix.append(matrix_row)
            
            # Statistiques globales
            total_combinations = sum(len(pos["combinations"]) for pos in positions_data.values())
            all_granques = set()
            all_tomes = set()
            all_engines = set()
            all_beasties = set()
            
            for pos_data in positions_data.values():
                all_granques.update(pos_data["granques"])
                all_tomes.update(pos_data["tomes"])
                all_engines.update(pos_data["engines"])
                all_beasties.update(pos_data["beasties"])
            
            cursor.close()
            conn.close()
            
            return {
                "universe": universe,
                "matrix": matrix,
                "chip_positions": chip_positions,
                "statistics": {
                    "total_katula_entries": len(results),
                    "unique_positions": len(positions_data),
                    "total_combinations": total_combinations,
                    "granques_count": len(all_granques),
                    "tomes_count": len(all_tomes),
                    "engines_count": len(all_engines),
                    "beasties_count": len(all_beasties),
                    "all_granques": list(all_granques),
                    "all_tomes": list(all_tomes),
                    "all_engines": list(all_engines),
                    "all_beasties": list(all_beasties)
                },
                "last_updated": datetime.now().isoformat(),
                "total_chips": len(chip_positions),
                "status": "active",
                "data_source": "existing_complete_structure"
            }
            
        except Exception as e:
            print(f"Erreur structure existante: {e}")
            return {"error": str(e), "data_source": "error"}
    
    @staticmethod
    def get_real_sessions_with_draws() -> Dict[str, Any]:
        """Récupère les vraies sessions avec leurs tirages"""
        try:
            conn = ExistingStructureService.get_db_connection()
            cursor = conn.cursor()
            
            # Sessions avec leurs tirages
            cursor.execute("""
                SELECT 
                    ws.id,
                    ws.name,
                    ws.description,
                    ws.lottery_type,
                    ws.numbers_per_draw,
                    ws.total_draws,
                    ws.current_draw,
                    ws.is_active,
                    ws.created_at,
                    COUNT(sd.id) as actual_draws
                FROM work_sessions ws
                LEFT JOIN session_draws sd ON ws.id = sd.session_id
                GROUP BY ws.id, ws.name, ws.description, ws.lottery_type, 
                         ws.numbers_per_draw, ws.total_draws, ws.current_draw, 
                         ws.is_active, ws.created_at
                ORDER BY ws.created_at DESC
            """)
            
            sessions_data = cursor.fetchall()
            sessions = []
            
            for session in sessions_data:
                sessions.append({
                    "id": session[0],
                    "name": session[1] or f"Session {session[0]}",
                    "description": session[2],
                    "lottery_type": session[3] or "unknown",
                    "numbers_per_draw": session[4] or 5,
                    "total_draws": session[5] or 0,
                    "current_draw": session[6] or 0,
                    "is_active": session[7] if session[7] is not None else False,
                    "created_at": session[8].isoformat() if session[8] else None,
                    "actual_draws": session[9],
                    "progress_percentage": round((session[9] / max(session[5], 1)) * 100, 1) if session[5] else 0
                })
            
            cursor.close()
            conn.close()
            
            return {
                "value": sessions,
                "total": len(sessions),
                "data_source": "existing_complete_structure"
            }
            
        except Exception as e:
            return {"error": str(e), "value": [], "total": 0}
    
    @staticmethod
    def get_granque_tome_complete(universe: str) -> Dict[str, Any]:
        """Récupère les vraies données granque/tome depuis combinations"""
        try:
            conn = ExistingStructureService.get_db_connection()
            cursor = conn.cursor()
            
            # Granques depuis combinations
            cursor.execute("""
                SELECT DISTINCT granque_name, denomination, chip_id
                FROM combinations 
                WHERE univers = %s AND granque_name IS NOT NULL
                ORDER BY granque_name, denomination
            """, (universe,))
            granque_results = cursor.fetchall()
            
            # Tomes depuis combinations
            cursor.execute("""
                SELECT DISTINCT tome, denomination, chip_id
                FROM combinations 
                WHERE univers = %s AND tome IS NOT NULL
                ORDER BY tome, denomination
            """, (universe,))
            tome_results = cursor.fetchall()
            
            # Organiser granques
            granque_data = {}
            for granque_name, denomination, chip_id in granque_results:
                if granque_name not in granque_data:
                    granque_data[granque_name] = []
                granque_data[granque_name].append({
                    "denomination": denomination,
                    "chip": chip_id
                })
            
            # Organiser tomes
            tome_data = {}
            for tome, denomination, chip_id in tome_results:
                if tome not in tome_data:
                    tome_data[tome] = []
                tome_data[tome].append({
                    "denomination": denomination,
                    "chip": chip_id
                })
            
            cursor.close()
            conn.close()
            
            return {
                "universe": universe,
                "granque_data": granque_data,
                "tome_data": tome_data,
                "statistics": {
                    "total_granques": len(granque_data),
                    "total_tomes": len(tome_data),
                    "granque_entries": len(granque_results),
                    "tome_entries": len(tome_results)
                },
                "data_source": "existing_complete_structure"
            }
            
        except Exception as e:
            return {"error": str(e), "data_source": "error"}

    @staticmethod
    def get_real_session_draws(session_id: int) -> Dict[str, Any]:
        """Récupère les tirages d'une session réelle, en comblant les manquants."""
        try:
            conn = ExistingStructureService.get_db_connection()
            cursor = conn.cursor()

            # 1. Récupérer les détails de la session
            cursor.execute("SELECT total_draws, lottery_type FROM work_sessions WHERE id = %s", (session_id,))
            session_details = cursor.fetchone()
            if not session_details:
                return {"error": "Session not found", "value": []}
            
            total_draws, lottery_type = session_details

            # 2. Récupérer les tirages existants
            cursor.execute("""
                SELECT id, draw_number, lottery_name, draw_date, winning_numbers, is_completed, is_no_draw
                FROM session_draws 
                WHERE session_id = %s
            """, (session_id,))
            
            existing_draws_data = cursor.fetchall()
            existing_draws = {row[1]: row for row in existing_draws_data}

            # 3. Construire la liste complète des tirages
            all_draws = []
            for draw_num in range(1, total_draws + 1):
                if draw_num in existing_draws:
                    draw_data = existing_draws[draw_num]
                    all_draws.append({
                        "id": draw_data[0],
                        "draw_number": draw_data[1],
                        "lottery_name": draw_data[2],
                        "draw_date": draw_data[3].strftime("%d/%m/%Y") if draw_data[3] else "N/A",
                        "winning_numbers": draw_data[4] or [],
                        "is_completed": draw_data[5],
                        "is_no_draw": draw_data[6] or False,
                        "status": "completed" # ou un autre statut basé sur la logique métier
                    })
                else:
                    # Créer un tirage manquant (no draw)
                    all_draws.append({
                        "id": f"missing_{session_id}_{draw_num}", # ID synthétique
                        "draw_number": draw_num,
                        "lottery_name": f"{lottery_type} - Tirage {draw_num}",
                        "draw_date": "N/A",
                        "winning_numbers": [],
                        "is_completed": False,
                        "is_no_draw": True,
                        "status": "no_draw"
                    })

            cursor.close()
            conn.close()
            
            return {
                "value": all_draws,
                "total": len(all_draws),
                "data_source": "existing_complete_structure_with_gaps"
            }

        except Exception as e:
            return {"error": str(e), "value": [], "total": 0}