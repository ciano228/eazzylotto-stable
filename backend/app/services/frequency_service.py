from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from collections import Counter
import statistics
from datetime import datetime

class FrequencyService:
    
    @staticmethod
    def calculate_frequencies(db: Session, universe: str = "mundo", periods: List[int] = [5, 10, 20, 50], session_id: int = None) -> Dict[str, Any]:
        """Calcule les fréquences sur différentes périodes, optionnellement filtré par session"""
        
        session_info = f" (Session {session_id})" if session_id else " (Global)"
        print(f"📊 Calcul des fréquences pour {universe}{session_info}...")
        
        # Types d'attributs à analyser
        attribute_types = ['forme', 'engine', 'beastie', 'tome']
        frequencies = {}
        
        if session_id:
            # Pour l'analyse par session, générer les combinaisons à partir des session_draws
            print(f"  Génération des combinaisons pour session {session_id}...")
            
            # Récupérer les numéros gagnants de la session
            session_query = """
                SELECT winning_numbers, draw_date, id
                FROM session_draws 
                WHERE session_id = :session_id 
                AND winning_numbers IS NOT NULL 
                AND array_length(winning_numbers, 1) >= 2
                ORDER BY draw_date DESC
                LIMIT 50
            """
            
            session_result = db.execute(text(session_query), {"session_id": session_id})
            session_data = session_result.fetchall()
            
            if not session_data:
                return {}
            
            # Générer toutes les combinaisons pour cette session
            from app.services.combination_service import CombinationService
            all_session_combinations = []
            
            for i, row in enumerate(session_data):
                winning_numbers = row[0]
                if winning_numbers and len(winning_numbers) >= 2:
                    combinations_list = CombinationService.generate_combinations(winning_numbers)
                    for combo in combinations_list:
                        combo_info = CombinationService.get_combination_info(db, combo[0], combo[1])
                        if combo_info and combo_info.get("univers") == universe:
                            combo_with_position = {
                                "forme": combo_info.get("forme"),
                                "engine": combo_info.get("engine"), 
                                "beastie": combo_info.get("beastie"),
                                "tome": combo_info.get("tome"),
                                "position": len(all_session_combinations)
                            }
                            all_session_combinations.append(combo_with_position)
            
            # Analyser chaque type d'attribut
            for attr_type in attribute_types:
                print(f"  Analyse des fréquences pour {attr_type} (Session {session_id})...")
                
                # Extraire les données pour cet attribut
                attr_data = []
                for combo in all_session_combinations:
                    if combo.get(attr_type):
                        attr_data.append((combo[attr_type], 0, combo["position"]))
                
                if len(attr_data) >= max(periods):
                    # Calculer les fréquences pour chaque période
                    attr_frequencies = FrequencyService._calculate_period_frequencies(attr_data, periods)
                    
                    if attr_frequencies:
                        frequencies[attr_type] = attr_frequencies
                        # Mettre à jour la table frequency_analysis avec info de session
                        FrequencyService._update_frequency_table(db, attr_type, attr_frequencies, f"{universe}_session_{session_id}")
        
        else:
            # Analyse globale (code existant)
            for attr_type in attribute_types:
                print(f"  Analyse des fréquences pour {attr_type} (Global)...")
                
                query = f"""
                    SELECT 
                        c.{attr_type} as attribute_value,
                        c.combination_id,
                        ROW_NUMBER() OVER (ORDER BY c.combination_id DESC) as position
                    FROM combinations c 
                    WHERE c.univers = :universe 
                    AND c.{attr_type} IS NOT NULL
                    ORDER BY c.combination_id DESC
                    LIMIT 200
                """
                
                result = db.execute(text(query), {"universe": universe})
                data = result.fetchall()
                
                if len(data) < max(periods):
                    continue
                
                # Calculer les fréquences pour chaque période
                attr_frequencies = FrequencyService._calculate_period_frequencies(data, periods)
                
                if attr_frequencies:
                    frequencies[attr_type] = attr_frequencies
                    # Mettre à jour la table frequency_analysis
                    FrequencyService._update_frequency_table(db, attr_type, attr_frequencies, universe)
        
        return frequencies
    
    @staticmethod
    def _calculate_period_frequencies(data: List, periods: List[int]) -> Dict[str, Dict]:
        """Calcule les fréquences pour différentes périodes"""
        
        # Extraire les valeurs d'attributs
        values = [row[0] for row in data]
        
        # Grouper par valeur d'attribut
        value_frequencies = {}
        
        # Obtenir toutes les valeurs uniques
        unique_values = set(values)
        
        for value in unique_values:
            value_frequencies[value] = {
                "periods": {},
                "trend": "stable",
                "heat_score": 0
            }
            
            # Calculer la fréquence pour chaque période
            for period in periods:
                if period <= len(values):
                    recent_values = values[:period]
                    frequency = recent_values.count(value)
                    rate = frequency / period
                    
                    value_frequencies[value]["periods"][f"period_{period}"] = {
                        "count": frequency,
                        "rate": round(rate, 3)
                    }
            
            # Calculer la tendance (comparaison période courte vs longue)
            if len(periods) >= 2:
                short_period = min(periods)
                long_period = max(periods)
                
                if f"period_{short_period}" in value_frequencies[value]["periods"] and f"period_{long_period}" in value_frequencies[value]["periods"]:
                    short_rate = value_frequencies[value]["periods"][f"period_{short_period}"]["rate"]
                    long_rate = value_frequencies[value]["periods"][f"period_{long_period}"]["rate"]
                    
                    if short_rate > long_rate * 1.2:
                        value_frequencies[value]["trend"] = "increasing"
                    elif short_rate < long_rate * 0.8:
                        value_frequencies[value]["trend"] = "decreasing"
                    else:
                        value_frequencies[value]["trend"] = "stable"
            
            # Calculer le heat score (basé sur la fréquence récente vs moyenne)
            if f"period_{periods[0]}" in value_frequencies[value]["periods"]:
                recent_rate = value_frequencies[value]["periods"][f"period_{periods[0]}"]["rate"]
                overall_rate = values.count(value) / len(values)
                
                if overall_rate > 0:
                    heat_score = min(100, (recent_rate / overall_rate) * 50)
                    value_frequencies[value]["heat_score"] = round(heat_score, 2)
        
        return value_frequencies
    
    @staticmethod
    def _update_frequency_table(db: Session, attr_type: str, frequencies: Dict, universe: str):
        """Met à jour la table frequency_analysis"""
        
        for value, stats in frequencies.items():
            # Extraire les valeurs des périodes
            period_5 = stats["periods"].get("period_5", {}).get("count", 0)
            period_10 = stats["periods"].get("period_10", {}).get("count", 0)
            period_20 = stats["periods"].get("period_20", {}).get("count", 0)
            period_50 = stats["periods"].get("period_50", {}).get("count", 0)
            
            # Vérifier si l'enregistrement existe
            existing = db.execute(text("""
                SELECT id FROM frequency_analysis 
                WHERE attribute_type = :attr_type 
                AND attribute_value = :value 
                AND universe = :universe
            """), {
                "attr_type": attr_type,
                "value": str(value),
                "universe": universe
            }).fetchone()
            
            if existing:
                # Mettre à jour
                db.execute(text("""
                    UPDATE frequency_analysis SET
                        period_5 = :period_5,
                        period_10 = :period_10,
                        period_20 = :period_20,
                        period_50 = :period_50,
                        trend = :trend,
                        heat_score = :heat_score,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                """), {
                    "period_5": period_5,
                    "period_10": period_10,
                    "period_20": period_20,
                    "period_50": period_50,
                    "trend": stats["trend"],
                    "heat_score": stats["heat_score"],
                    "id": existing[0]
                })
            else:
                # Insérer nouveau
                db.execute(text("""
                    INSERT INTO frequency_analysis 
                    (attribute_type, attribute_value, universe, period_5, 
                     period_10, period_20, period_50, trend, heat_score)
                    VALUES (:attr_type, :value, :universe, :period_5, 
                            :period_10, :period_20, :period_50, :trend, :heat_score)
                """), {
                    "attr_type": attr_type,
                    "value": str(value),
                    "universe": universe,
                    "period_5": period_5,
                    "period_10": period_10,
                    "period_20": period_20,
                    "period_50": period_50,
                    "trend": stats["trend"],
                    "heat_score": stats["heat_score"]
                })
        
        db.commit()
    
    @staticmethod
    def get_trending_attributes(db: Session, universe: str = "mundo", trend_type: str = "increasing") -> Dict[str, List]:
        """Récupère les attributs avec une tendance spécifique"""
        
        result = db.execute(text("""
            SELECT 
                attribute_type,
                attribute_value,
                period_5,
                period_10,
                period_20,
                heat_score,
                trend
            FROM frequency_analysis 
            WHERE universe = :universe 
            AND trend = :trend_type
            ORDER BY heat_score DESC
        """), {
            "universe": universe,
            "trend_type": trend_type
        })
        
        trending = {}
        for row in result:
            attr_type = row[0]
            if attr_type not in trending:
                trending[attr_type] = []
            
            trending[attr_type].append({
                "value": row[1],
                "period_5": row[2],
                "period_10": row[3],
                "period_20": row[4],
                "heat_score": float(row[5]),
                "trend": row[6]
            })
        
        return trending
    
    @staticmethod
    def get_frequency_summary(db: Session, universe: str = "mundo") -> Dict[str, Any]:
        """Résumé des fréquences pour un univers"""
        
        result = db.execute(text("""
            SELECT 
                attribute_type,
                COUNT(*) as total_values,
                AVG(heat_score) as avg_heat_score,
                MAX(heat_score) as max_heat_score,
                COUNT(CASE WHEN trend = 'increasing' THEN 1 END) as increasing_count,
                COUNT(CASE WHEN trend = 'decreasing' THEN 1 END) as decreasing_count,
                COUNT(CASE WHEN trend = 'stable' THEN 1 END) as stable_count
            FROM frequency_analysis 
            WHERE universe = :universe
            GROUP BY attribute_type
            ORDER BY attribute_type
        """), {"universe": universe})
        
        summary = {}
        for row in result:
            summary[row[0]] = {
                "total_values": row[1],
                "avg_heat_score": round(float(row[2]), 2),
                "max_heat_score": float(row[3]),
                "increasing_count": row[4],
                "decreasing_count": row[5],
                "stable_count": row[6]
            }
        
        return summary
    
    @staticmethod
    def predict_next_likely(db: Session, universe: str = "mundo", top_n: int = 5) -> Dict[str, List]:
        """Prédit les attributs les plus susceptibles de sortir prochainement"""
        
        # Combiner les données d'écarts et de fréquences pour une prédiction
        result = db.execute(text("""
            SELECT 
                f.attribute_type,
                f.attribute_value,
                f.heat_score,
                f.trend,
                f.period_5,
                g.current_gap,
                g.average_gap,
                (g.current_gap::float / NULLIF(g.average_gap, 0)) as gap_ratio
            FROM frequency_analysis f
            LEFT JOIN attribute_gaps g ON (
                f.attribute_type = g.attribute_type 
                AND f.attribute_value = g.attribute_value 
                AND f.universe = g.universe
            )
            WHERE f.universe = :universe
            AND f.heat_score > 0
            ORDER BY f.heat_score DESC, gap_ratio DESC
        """), {"universe": universe})
        
        predictions = {}
        
        for row in result:
            attr_type = row[0]
            if attr_type not in predictions:
                predictions[attr_type] = []
            
            # Calculer un score de prédiction combiné
            heat_score = float(row[2]) if row[2] else 0
            gap_ratio = float(row[7]) if row[7] else 1
            
            # Score combiné (heat_score + bonus pour écart élevé)
            combined_score = heat_score + (gap_ratio * 10)
            
            predictions[attr_type].append({
                "value": row[1],
                "heat_score": heat_score,
                "trend": row[3],
                "recent_frequency": row[4],
                "current_gap": row[5],
                "gap_ratio": gap_ratio,
                "prediction_score": round(combined_score, 2)
            })
        
        # Garder seulement le top N pour chaque type
        for attr_type in predictions:
            predictions[attr_type] = sorted(
                predictions[attr_type], 
                key=lambda x: x['prediction_score'], 
                reverse=True
            )[:top_n]
        
        return predictions