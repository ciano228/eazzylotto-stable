"""
Split Strategy Service
Gère la division temporelle des zones (déjà jouées vs pas encore jouées)
"""

import psycopg2
import psycopg2.extras
from typing import Dict, List, Any, Set
from datetime import datetime, timedelta
import itertools

class SplitStrategyService:
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config


    def _get_all_combinations_for_attribute(self, universe: str, 
                                          attribute_type: str, 
                                          attribute_value: str) -> List[str]:
        """Récupère toutes les paires distinctes pour un attribut donné."""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()
        
        # Gérer les attributs synthétiques (ex: forme_tome)
        # On considère comme synthétique tout type contenant un underscore
        if '_' in attribute_type:
            # Format composite type="forme_tome" value="rectangle_tome1"
            types = attribute_type.split('_')
            # Les valeurs sont aussi séparées par des underscores dans le moteur synthétique
            values = attribute_value.split('_')
            
            if len(types) != len(values):
                # Fallback ou erreur si mismatch
                return []
                
            conditions = []
            params = [universe]
            for t, v in zip(types, values):
                # Mapping special names
                col = t
                if t == 'granque': col = 'granque_name'
                conditions.append(f"{col} = %s")
                params.append(v)
            
            where_clause = " AND ".join(conditions)
            query = f"SELECT * FROM combinations WHERE univers = %s AND {where_clause}"
        else:
            # Format simple
            col = attribute_type
            val = attribute_value
            
            if attribute_type == 'granque': 
                col = 'granque_name'
            elif attribute_type == 'chip':
                # S'assurer que la valeur a le préfixe 'chip' si nécessaire
                if not str(val).startswith('chip'):
                    val = f"chip{val}"
                    
            query = f"SELECT * FROM combinations WHERE univers = %s AND {col} = %s"
            params = [universe, val]
            
        try:
            cur.execute(query, params)
            # Fetch all columns to return a rich object
            colnames = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            
            combinations_data = []
            for row in rows:
                combinations_data.append(dict(zip(colnames, row)))
                
            return combinations_data
        except Exception as e:
            print(f"Error fetching combinations: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    def perform_split(self, universe: str, session_id: int, 
                    attribute_type: str, attribute_value: str, 
                    lookback_days: int = 180) -> Dict[str, Any]:
        """
        Divise les combinaisons d'un attribut en deux groupes: 
        'ya-played' (apparu récemment) et 'not-yet-played'.
        Le lookback est calculé par rapport au dernier tirage de la session.
        """
        # 1. Identifier toutes les combinaisons possibles pour cet attribut
        all_combos = self._get_all_combinations_for_attribute(universe, attribute_type, attribute_value)
        if not all_combos:
            display_val = attribute_value
            if attribute_type == 'chip' and not str(display_val).startswith('chip'):
                display_val = f"chip{display_val}"
            return {"status": "error", "message": f"Aucune combinaison trouvée pour {attribute_type} {display_val}"}

        # 2. Récupérer les métadonnées de la session et les combinaisons jouées avec dates
        session_info = self._get_session_metadata(session_id)
        played_data = self._get_played_combinations_relative(session_id, lookback_days)
        played_combos_map = played_data['combinations_map'] # combo string -> list of dates
        
        # 3. Effectuer le split
        ya_played = []
        not_yet_played = []
        
        for combo_dict in all_combos:
            raw_combo_str = combo_dict.get('combination')
            if raw_combo_str in played_combos_map:
                # Ajouter stats d'apparition
                dates = played_combos_map[raw_combo_str]
                combo_dict['apparition_count'] = len(dates)
                combo_dict['apparition_dates'] = [d.isoformat() for d in sorted(dates, reverse=True)]
                ya_played.append(combo_dict)
            else:
                combo_dict['apparition_count'] = 0
                combo_dict['apparition_dates'] = []
                not_yet_played.append(combo_dict)
                
        return {
            "status": "success",
            "attribute": f"{attribute_type}:{attribute_value}",
            "universe": universe,
            "session_name": session_info.get('name', f"Session #{session_id}"),
            "period_days": lookback_days,
            "analysis_bounds": {
                "start": played_data['start_date'],
                "end": played_data['end_date'],
                "draw_count": played_data['draw_count']
            },
            "total_count": len(all_combos),
            "ya_played": {
                "count": len(ya_played),
                "combinations": ya_played,
                "profit_potential": 200 - len(ya_played)
            },
            "not_yet_played": {
                "count": len(not_yet_played),
                "combinations": not_yet_played,
                "profit_potential": 200 - len(not_yet_played)
            }
        }

    def _get_session_metadata(self, session_id: int) -> Dict[str, Any]:
        """Récupère le nom et les infos de base de la session."""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("SELECT name, lottery_type FROM work_sessions WHERE id = %s", (session_id,))
            row = cur.fetchone()
            return dict(row) if row else {}
        finally:
            cur.close()
            conn.close()

    def _get_played_combinations_relative(self, session_id: int, lookback_days: int) -> Dict[str, Any]:
        """Récupère les combinaisons jouées sur une période relative au dernier tirage, avec dates."""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()
        
        try:
            # Trouver la date du dernier tirage de la session
            cur.execute("""
                SELECT MAX(draw_date) 
                FROM session_draws 
                WHERE session_id = %s AND is_completed = TRUE
            """, (session_id,))
            max_date = cur.fetchone()[0]
            
            if not max_date:
                return {"combinations_map": {}, "start_date": None, "end_date": None, "draw_count": 0}
            
            cutoff_date = max_date - timedelta(days=lookback_days)
            
            query = """
                SELECT winning_numbers, draw_date
                FROM session_draws 
                WHERE session_id = %s 
                  AND draw_date >= %s
                  AND draw_date <= %s
                  AND is_completed = TRUE
                ORDER BY draw_date DESC
            """
            
            cur.execute(query, (session_id, cutoff_date, max_date))
            rows = cur.fetchall()
            
            combinations_map = {} # combo_str -> list of dates
            draw_dates = set()
            
            for winning_numbers, draw_date in rows:
                if not winning_numbers: continue
                draw_dates.add(draw_date)
                
                # S'assurer que winning_numbers est une liste
                if isinstance(winning_numbers, str):
                    import json
                    winning_numbers = json.loads(winning_numbers)
                
                if len(winning_numbers) < 2: continue
                
                # Générer toutes les paires (p1-p2)
                for p in itertools.combinations(sorted(winning_numbers), 2):
                    combo_str = f"{p[0]}-{p[1]}"
                    if combo_str not in combinations_map:
                        combinations_map[combo_str] = []
                    combinations_map[combo_str].append(draw_date)
                    
            return {
                "combinations_map": combinations_map,
                "start_date": cutoff_date.isoformat() if cutoff_date else None,
                "end_date": max_date.isoformat() if max_date else None,
                "draw_count": len(draw_dates)
            }
        except Exception as e:
            print(f"Error fetching played combinations: {e}")
            return {"combinations_map": {}, "start_date": None, "end_date": None, "draw_count": 0}
        finally:
            cur.close()
            conn.close()
