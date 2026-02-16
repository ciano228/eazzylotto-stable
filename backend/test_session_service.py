"""
Service de Session de Test pour l'Analyse Temporelle Géométrique
Génère des sessions de loto avec périodicité 7 jours
"""

import psycopg2
from typing import Dict, List, Any
from datetime import datetime, timedelta
import random
import json

class TestSessionService:
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.use_db = bool(db_config and db_config.get('host'))
    
    def create_test_session(self, session_name: str = "session_test_001", 
                          periods: int = 6) -> Dict[str, Any]:
        """Crée une session de test avec 7 lotos par semaine"""
        
        loto_names = [
            "loto_lundi", "loto_mardi", "loto_mercredi", "loto_jeudi",
            "loto_vendredi", "loto_samedi", "loto_dimanche"
        ]
        
        session_data = {
            "session_name": session_name,
            "periods": periods,
            "loto_names": loto_names,
            "draws": []
        }
        
        # Générer les tirages pour chaque période
        start_date = datetime.now() - timedelta(days=periods * 7)
        
        for period in range(periods):
            period_start = start_date + timedelta(days=period * 7)
            
            for day, loto_name in enumerate(loto_names):
                draw_date = period_start + timedelta(days=day)
                numbers = self._generate_draw_numbers()
                
                draw = {
                    "id": f"{session_name}_P{period+1}_{loto_name}",
                    "session": session_name,
                    "period": period + 1,
                    "loto_name": loto_name,
                    "date": draw_date.strftime('%Y-%m-%d'),
                    "day_of_week": day + 1,
                    "numbers": numbers
                }
                
                session_data["draws"].append(draw)
        
        return session_data
    
    def _generate_draw_numbers(self) -> List[int]:
        """Génère 5 numéros entre 1 et 90"""
        numbers = []
        while len(numbers) < 5:
            num = random.randint(1, 90)
            if num not in numbers:
                numbers.append(num)
        return sorted(numbers)
    
    def save_session_to_db(self, session_data: Dict[str, Any]) -> bool:
        """Sauvegarde la session (mode simulation sans BD)"""
        if not self.use_db:
            print(f"Session {session_data['session_name']} sauvegardée en mémoire")
            return True
            
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Créer la table si elle n'existe pas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_sessions (
                    id SERIAL PRIMARY KEY,
                    session_name VARCHAR(100) NOT NULL,
                    draw_id VARCHAR(200) NOT NULL,
                    period INTEGER NOT NULL,
                    loto_name VARCHAR(50) NOT NULL,
                    draw_date DATE NOT NULL,
                    day_of_week INTEGER NOT NULL,
                    numbers INTEGER[] NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Supprimer les données existantes pour cette session
            cursor.execute("DELETE FROM test_sessions WHERE session_name = %s", 
                         (session_data["session_name"],))
            
            # Insérer les nouveaux tirages
            for draw in session_data["draws"]:
                cursor.execute("""
                    INSERT INTO test_sessions 
                    (session_name, draw_id, period, loto_name, draw_date, day_of_week, numbers)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    draw["session"],
                    draw["id"],
                    draw["period"],
                    draw["loto_name"],
                    draw["date"],
                    draw["day_of_week"],
                    draw["numbers"]
                ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Erreur sauvegarde session: {e}")
            return False
    
    def get_session_draws(self, session_name: str) -> List[Dict[str, Any]]:
        """Récupère les tirages d'une session (mode simulation)"""
        if not self.use_db:
            # Mode simulation - recréer la session
            session_data = self.create_test_session(session_name, 6)
            return session_data['draws']
            
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT draw_id, period, loto_name, draw_date, day_of_week, numbers
                FROM test_sessions 
                WHERE session_name = %s
                ORDER BY period, day_of_week
            """, (session_name,))
            
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            draws = []
            for result in results:
                draws.append({
                    "id": result[0],
                    "period": result[1],
                    "loto_name": result[2],
                    "date": result[3].strftime('%Y-%m-%d'),
                    "day_of_week": result[4],
                    "numbers": result[5]
                })
            
            return draws
            
        except Exception as e:
            print(f"Erreur récupération session: {e}")
            return []
    
    def analyze_session_patterns(self, session_name: str, universe: str = "mundo") -> Dict[str, Any]:
        """Analyse les patterns d'une session de test"""
        from temporal_geometric_service import TemporalGeometricService
        
        # Récupérer les tirages
        draws = self.get_session_draws(session_name)
        
        if not draws:
            return {"error": "Session non trouvée"}
        
        # Convertir au format attendu par le service temporel
        formatted_draws = []
        for draw in draws:
            formatted_draws.append({
                "id": draw["id"],
                "date": draw["date"],
                "numbers": draw["numbers"],
                "universe": universe,
                "loto_name": draw["loto_name"],
                "period": draw["period"]
            })
        
        # Analyser avec le service temporel géométrique
        temporal_service = TemporalGeometricService(self.db_config)
        
        period_config = {
            'period_type': 'weekly',
            'analyze_by_period': True,
            'session_name': session_name
        }
        
        analysis = temporal_service.analyze_temporal_patterns(
            universe, formatted_draws, period_config
        )
        
        # Ajouter des statistiques spécifiques à la session
        session_stats = self._calculate_session_stats(draws)
        analysis['session_stats'] = session_stats
        
        return analysis
    
    def _calculate_session_stats(self, draws: List[Dict]) -> Dict[str, Any]:
        """Calcule les statistiques de la session"""
        stats = {
            "total_draws": len(draws),
            "periods": len(set(draw["period"] for draw in draws)),
            "loto_frequency": {},
            "number_frequency": {},
            "day_patterns": {}
        }
        
        # Fréquence par loto
        for draw in draws:
            loto = draw["loto_name"]
            stats["loto_frequency"][loto] = stats["loto_frequency"].get(loto, 0) + 1
        
        # Fréquence des numéros
        for draw in draws:
            for num in draw["numbers"]:
                stats["number_frequency"][num] = stats["number_frequency"].get(num, 0) + 1
        
        # Patterns par jour
        for draw in draws:
            day = draw["day_of_week"]
            if day not in stats["day_patterns"]:
                stats["day_patterns"][day] = {"count": 0, "numbers": []}
            stats["day_patterns"][day]["count"] += 1
            stats["day_patterns"][day]["numbers"].extend(draw["numbers"])
        
        return stats