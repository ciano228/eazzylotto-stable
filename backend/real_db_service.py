"""
Service de Base de Données Réelle pour les Tests
Sauvegarde et exploitation des tirages de test en temps réel
"""

import psycopg2
from typing import Dict, List, Any
from datetime import datetime
import json

class RealDBService:
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.use_db = bool(db_config and db_config.get('host'))
    
    def save_test_session_to_db(self, session_data: Dict[str, Any]) -> bool:
        """Sauvegarde la session de test en BD réelle"""
        if not self.use_db:
            print("Mode simulation - BD non disponible")
            return False
            
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Créer les tables si elles n'existent pas
            self._create_tables(cursor)
            
            # Sauvegarder la session
            session_id = self._save_session_header(cursor, session_data)
            
            # Sauvegarder les tirages
            for draw in session_data['draws']:
                self._save_draw(cursor, session_id, draw)
                
                # Sauvegarder les combinaisons géométriques
                self._save_geometric_combinations(cursor, draw)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✅ Session {session_data['session_name']} sauvegardée en BD")
            return True
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde BD: {e}")
            return False
    
    def _create_tables(self, cursor):
        """Crée les tables nécessaires"""
        
        # Table des sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_sessions_real (
                id SERIAL PRIMARY KEY,
                session_name VARCHAR(100) UNIQUE NOT NULL,
                periods INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSONB
            )
        """)
        
        # Table des tirages
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_draws_real (
                id SERIAL PRIMARY KEY,
                session_id INTEGER REFERENCES test_sessions_real(id),
                draw_id VARCHAR(200) NOT NULL,
                period INTEGER NOT NULL,
                loto_name VARCHAR(50) NOT NULL,
                draw_date DATE NOT NULL,
                day_of_week INTEGER NOT NULL,
                numbers INTEGER[] NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des combinaisons géométriques
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS geometric_combinations_real (
                id SERIAL PRIMARY KEY,
                draw_id VARCHAR(200) NOT NULL,
                combination_numbers INTEGER[] NOT NULL,
                geometric_position VARCHAR(10) NOT NULL,
                ligne INTEGER NOT NULL,
                colonne INTEGER NOT NULL,
                quadrant VARCHAR(20) NOT NULL,
                zone VARCHAR(30) NOT NULL,
                tome VARCHAR(20) NOT NULL,
                granque VARCHAR(20) NOT NULL,
                forme VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Index pour les performances
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_draws_session 
            ON test_draws_real(session_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_combinations_draw 
            ON geometric_combinations_real(draw_id)
        """)
    
    def _save_session_header(self, cursor, session_data: Dict) -> int:
        """Sauvegarde l'en-tête de session"""
        cursor.execute("""
            INSERT INTO test_sessions_real (session_name, periods, metadata)
            VALUES (%s, %s, %s)
            ON CONFLICT (session_name) 
            DO UPDATE SET periods = EXCLUDED.periods, metadata = EXCLUDED.metadata
            RETURNING id
        """, (
            session_data['session_name'],
            session_data['periods'],
            json.dumps({
                'loto_names': session_data['loto_names'],
                'total_draws': len(session_data['draws'])
            })
        ))
        
        return cursor.fetchone()[0]
    
    def _save_draw(self, cursor, session_id: int, draw: Dict):
        """Sauvegarde un tirage"""
        cursor.execute("""
            INSERT INTO test_draws_real 
            (session_id, draw_id, period, loto_name, draw_date, day_of_week, numbers)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            session_id,
            draw['id'],
            draw['period'],
            draw['loto_name'],
            draw['date'],
            draw['day_of_week'],
            draw['numbers']
        ))
    
    def _save_geometric_combinations(self, cursor, draw: Dict):
        """Sauvegarde les combinaisons géométriques d'un tirage"""
        from itertools import combinations
        
        # Générer toutes les combinaisons 2 à 2
        combos = list(combinations(draw['numbers'], 2))
        
        for combo in combos:
            num1, num2 = combo
            
            # Calculer la position géométrique
            ligne = (num1 % 8) + 1
            colonne = (num2 % 6) + 1
            
            # Calculer les attributs
            quadrant = self._get_quadrant(ligne, colonne)
            zone = self._get_zone(ligne, colonne)
            tome = f"tome{((num1 + num2) % 4) + 1}"
            granque = f"Q{((num1 + num2) % 6) + 1}"
            forme = ['carre', 'triangle', 'cercle', 'rectangle'][num1 % 4]
            
            cursor.execute("""
                INSERT INTO geometric_combinations_real 
                (draw_id, combination_numbers, geometric_position, ligne, colonne, 
                 quadrant, zone, tome, granque, forme)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                draw['id'],
                [num1, num2],
                f"{ligne}{colonne}",
                ligne,
                colonne,
                quadrant,
                zone,
                tome,
                granque,
                forme
            ))
    
    def get_real_analysis_data(self, session_name: str, marking_type: str) -> Dict[str, Any]:
        """Récupère les données d'analyse depuis la BD réelle"""
        if not self.use_db:
            return {"error": "BD non disponible"}
            
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Récupérer les données selon le type de marquage
            if marking_type == 'tome':
                return self._get_tome_analysis(cursor, session_name)
            elif marking_type == 'forme':
                return self._get_forme_analysis(cursor, session_name)
            elif marking_type == 'quadrant':
                return self._get_quadrant_analysis(cursor, session_name)
            elif marking_type == 'zone':
                return self._get_zone_analysis(cursor, session_name)
            else:
                return self._get_position_analysis(cursor, session_name)
                
        except Exception as e:
            return {"error": str(e)}
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    def _get_tome_analysis(self, cursor, session_name: str) -> Dict[str, Any]:
        """Analyse des tomes depuis la BD"""
        cursor.execute("""
            SELECT gc.tome, COUNT(*) as frequency,
                   ARRAY_AGG(DISTINCT gc.geometric_position) as positions,
                   ARRAY_AGG(DISTINCT gc.quadrant) as quadrants
            FROM geometric_combinations_real gc
            JOIN test_draws_real td ON gc.draw_id = td.draw_id
            JOIN test_sessions_real ts ON td.session_id = ts.id
            WHERE ts.session_name = %s
            GROUP BY gc.tome
            ORDER BY frequency DESC
        """, (session_name,))
        
        results = cursor.fetchall()
        
        tome_stats = {}
        total_combinations = sum(row[1] for row in results)
        
        for tome, frequency, positions, quadrants in results:
            tome_stats[tome] = {
                'count': frequency,
                'frequency_percent': (frequency / total_combinations) * 100,
                'unique_positions': len(positions),
                'positions': positions,
                'quadrants': quadrants,
                'geometric_representation': {
                    'quadrant_distribution': dict(zip(*np.unique(quadrants, return_counts=True))) if quadrants else {},
                    'total_positions': len(positions)
                }
            }
        
        return {
            'analysis_type': 'tome',
            'session_name': session_name,
            'total_combinations': total_combinations,
            'tome_stats': tome_stats,
            'ranking': [(tome, stats) for tome, stats in sorted(tome_stats.items(), key=lambda x: x[1]['count'], reverse=True)]
        }
    
    def _get_forme_analysis(self, cursor, session_name: str) -> Dict[str, Any]:
        """Analyse des formes depuis la BD"""
        cursor.execute("""
            SELECT gc.forme, COUNT(*) as frequency,
                   ARRAY_AGG(DISTINCT gc.geometric_position) as positions
            FROM geometric_combinations_real gc
            JOIN test_draws_real td ON gc.draw_id = td.draw_id
            JOIN test_sessions_real ts ON td.session_id = ts.id
            WHERE ts.session_name = %s
            GROUP BY gc.forme
            ORDER BY frequency DESC
        """, (session_name,))
        
        results = cursor.fetchall()
        
        forme_stats = {}
        total_combinations = sum(row[1] for row in results)
        
        for forme, frequency, positions in results:
            forme_stats[forme] = {
                'count': frequency,
                'frequency_percent': (frequency / total_combinations) * 100,
                'unique_positions': len(positions),
                'positions': positions
            }
        
        return {
            'analysis_type': 'forme',
            'session_name': session_name,
            'total_combinations': total_combinations,
            'forme_stats': forme_stats,
            'ranking': [(forme, stats) for forme, stats in sorted(forme_stats.items(), key=lambda x: x[1]['count'], reverse=True)]
        }
    
    def _get_quadrant_analysis(self, cursor, session_name: str) -> Dict[str, Any]:
        """Analyse des quadrants depuis la BD"""
        cursor.execute("""
            SELECT gc.quadrant, COUNT(*) as frequency,
                   ARRAY_AGG(DISTINCT gc.geometric_position) as positions
            FROM geometric_combinations_real gc
            JOIN test_draws_real td ON gc.draw_id = td.draw_id
            JOIN test_sessions_real ts ON td.session_id = ts.id
            WHERE ts.session_name = %s
            GROUP BY gc.quadrant
            ORDER BY frequency DESC
        """, (session_name,))
        
        results = cursor.fetchall()
        
        quadrant_stats = {}
        total_combinations = sum(row[1] for row in results)
        
        for quadrant, frequency, positions in results:
            quadrant_stats[quadrant] = {
                'count': frequency,
                'frequency_percent': (frequency / total_combinations) * 100,
                'unique_positions': len(positions),
                'positions': positions
            }
        
        return {
            'analysis_type': 'quadrant',
            'session_name': session_name,
            'total_combinations': total_combinations,
            'quadrant_stats': quadrant_stats,
            'ranking': [(quadrant, stats) for quadrant, stats in sorted(quadrant_stats.items(), key=lambda x: x[1]['count'], reverse=True)]
        }
    
    def _get_zone_analysis(self, cursor, session_name: str) -> Dict[str, Any]:
        """Analyse des zones depuis la BD"""
        cursor.execute("""
            SELECT gc.zone, COUNT(*) as frequency,
                   ARRAY_AGG(DISTINCT gc.geometric_position) as positions
            FROM geometric_combinations_real gc
            JOIN test_draws_real td ON gc.draw_id = td.draw_id
            JOIN test_sessions_real ts ON td.session_id = ts.id
            WHERE ts.session_name = %s
            GROUP BY gc.zone
            ORDER BY frequency DESC
        """, (session_name,))
        
        results = cursor.fetchall()
        
        zone_stats = {}
        total_combinations = sum(row[1] for row in results)
        
        for zone, frequency, positions in results:
            zone_stats[zone] = {
                'count': frequency,
                'frequency_percent': (frequency / total_combinations) * 100,
                'unique_positions': len(positions),
                'positions': positions
            }
        
        return {
            'analysis_type': 'zone',
            'session_name': session_name,
            'total_combinations': total_combinations,
            'zone_stats': zone_stats,
            'ranking': [(zone, stats) for zone, stats in sorted(zone_stats.items(), key=lambda x: x[1]['count'], reverse=True)]
        }
    
    def _get_position_analysis(self, cursor, session_name: str) -> Dict[str, Any]:
        """Analyse des positions géométriques depuis la BD"""
        cursor.execute("""
            SELECT gc.geometric_position, COUNT(*) as frequency,
                   gc.ligne, gc.colonne, gc.quadrant, gc.zone
            FROM geometric_combinations_real gc
            JOIN test_draws_real td ON gc.draw_id = td.draw_id
            JOIN test_sessions_real ts ON td.session_id = ts.id
            WHERE ts.session_name = %s
            GROUP BY gc.geometric_position, gc.ligne, gc.colonne, gc.quadrant, gc.zone
            ORDER BY frequency DESC
        """, (session_name,))
        
        results = cursor.fetchall()
        
        position_stats = {}
        total_combinations = sum(row[1] for row in results)
        
        for position, frequency, ligne, colonne, quadrant, zone in results:
            position_stats[position] = {
                'count': frequency,
                'frequency_percent': (frequency / total_combinations) * 100,
                'ligne': ligne,
                'colonne': colonne,
                'quadrant': quadrant,
                'zone': zone
            }
        
        return {
            'analysis_type': 'position',
            'session_name': session_name,
            'total_combinations': total_combinations,
            'position_stats': position_stats,
            'ranking': [(pos, stats) for pos, stats in sorted(position_stats.items(), key=lambda x: x[1]['count'], reverse=True)]
        }
    
    def _get_quadrant(self, ligne: int, colonne: int) -> str:
        """Détermine le quadrant"""
        if ligne <= 4 and colonne <= 3:
            return "Q1"
        elif ligne <= 4 and colonne > 3:
            return "Q2"
        elif ligne > 4 and colonne <= 3:
            return "Q3"
        else:
            return "Q4"
    
    def _get_zone(self, ligne: int, colonne: int) -> str:
        """Détermine la zone géométrique"""
        if ligne <= 3:
            v_zone = "top"
        elif ligne <= 6:
            v_zone = "middle"
        else:
            v_zone = "bottom"
        
        if colonne <= 2:
            h_zone = "left"
        elif colonne <= 4:
            h_zone = "center"
        else:
            h_zone = "right"
        
        return f"{v_zone}_{h_zone}"