from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from datetime import datetime, timedelta
import statistics

class GapAnalysisService:
    
    @staticmethod
    def calculate_gaps(db: Session, universe: str = "mundo", session_id: int = None) -> Dict[str, Any]:
        """Calcule les écarts pour tous les attributs d'un univers, optionnellement filtré par session"""
        
        results = {}
        
        if session_id:
            # Pour l'analyse par session, on génère les combinaisons à partir des session_draws
            print(f"📊 Analyse des écarts pour session {session_id}...")
            
            # Récupérer les numéros gagnants de la session
            session_query = """
                SELECT winning_numbers, draw_date, id
                FROM session_draws 
                WHERE session_id = :session_id 
                AND winning_numbers IS NOT NULL 
                AND array_length(winning_numbers, 1) >= 2
                ORDER BY draw_date DESC
                LIMIT 100
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
                            # Ajouter position basée sur l'ordre chronologique inverse
                            combo_with_position = {
                                "forme": combo_info.get("forme"),
                                "engine": combo_info.get("engine"), 
                                "beastie": combo_info.get("beastie"),
                                "tome": combo_info.get("tome"),
                                "chip": combo_info.get("chip"),
                                "parite": combo_info.get("parite"),
                                "unidos": combo_info.get("unidos"),
                                "position": len(all_session_combinations)
                            }
                            all_session_combinations.append(combo_with_position)
            
            # Analyser chaque type d'attribut
            attribute_types = ['forme', 'engine', 'beastie', 'tome', 'chip', 'parite', 'unidos']
            
            for attr_type in attribute_types:
                print(f"  Analyse des écarts pour {attr_type} (Session {session_id})...")
                
                # Extraire les données pour cet attribut
                attr_data = []
                for combo in all_session_combinations:
                    if combo.get(attr_type):
                        attr_data.append((combo[attr_type], 0, combo["position"]))
                
                if attr_data:
                    attribute_gaps = GapAnalysisService._analyze_attribute_gaps(attr_data, attr_type)
                    results[attr_type] = attribute_gaps
                    # Mettre à jour la table avec l'info de session
                    GapAnalysisService._update_gaps_table(db, attr_type, attribute_gaps, f"{universe}_session_{session_id}")
        
        else:
            # Analyse globale (code existant)
            direct_attributes = ['forme', 'engine', 'beastie', 'tome', 'chip']
            
            for attr_type in direct_attributes:
                print(f"📊 Analyse des écarts pour {attr_type} (Global)...")
                
                query = f"""
                    SELECT 
                        c.{attr_type} as attribute_value,
                        c.combination_id,
                        ROW_NUMBER() OVER (ORDER BY c.combination_id DESC) as position
                    FROM combinations c 
                    WHERE c.univers = :universe 
                    AND c.{attr_type} IS NOT NULL
                    ORDER BY c.combination_id DESC
                    LIMIT 1000
                """
                
                result = db.execute(text(query), {"universe": universe})
                data = result.fetchall()
                
                if data:
                    attribute_gaps = GapAnalysisService._analyze_attribute_gaps(data, attr_type)
                    results[attr_type] = attribute_gaps
                    GapAnalysisService._update_gaps_table(db, attr_type, attribute_gaps, universe)
            
            # Analyser parite avec jointure
            print("📊 Analyse des écarts pour parite (Global)...")
            parite_query = """
                SELECT 
                    p.parite as attribute_value,
                    c.combination_id,
                    ROW_NUMBER() OVER (ORDER BY c.combination_id DESC) as position
                FROM combinations c 
                LEFT JOIN parite p ON c.parite_id = p.parite_id
                WHERE c.univers = :universe 
                AND p.parite IS NOT NULL
                ORDER BY c.combination_id DESC
                LIMIT 1000
            """
            
            result = db.execute(text(parite_query), {"universe": universe})
            data = result.fetchall()
            
            if data:
                attribute_gaps = GapAnalysisService._analyze_attribute_gaps(data, 'parite')
                results['parite'] = attribute_gaps
                GapAnalysisService._update_gaps_table(db, 'parite', attribute_gaps, universe)
            
            # Analyser unidos avec jointure
            print("📊 Analyse des écarts pour unidos (Global)...")
            unidos_query = """
                SELECT 
                    u.unidos as attribute_value,
                    c.combination_id,
                    ROW_NUMBER() OVER (ORDER BY c.combination_id DESC) as position
                FROM combinations c 
                LEFT JOIN unidos u ON c.unidos_id = u.unidos_id
                WHERE c.univers = :universe 
                AND u.unidos IS NOT NULL
                ORDER BY c.combination_id DESC
                LIMIT 1000
            """
            
            result = db.execute(text(unidos_query), {"universe": universe})
            data = result.fetchall()
            
            if data:
                attribute_gaps = GapAnalysisService._analyze_attribute_gaps(data, 'unidos')
                results['unidos'] = attribute_gaps
                GapAnalysisService._update_gaps_table(db, 'unidos', attribute_gaps, universe)
        
        return results
    
    @staticmethod
    def _analyze_attribute_gaps(data: List, attr_type: str) -> Dict[str, Dict]:
        """Analyse les écarts pour un type d'attribut donné"""
        
        # Grouper par valeur d'attribut
        value_positions = {}
        for row in data:
            value = row[0]  # attribute_value
            position = row[2]  # position
            
            if value not in value_positions:
                value_positions[value] = []
            value_positions[value].append(position)
        
        gaps_analysis = {}
        
        for value, positions in value_positions.items():
            if len(positions) < 2:
                # Pas assez de données pour calculer les écarts
                gaps_analysis[value] = {
                    "current_gap": positions[0] if positions else 0,
                    "average_gap": 0,
                    "max_gap": 0,
                    "min_gap": 0,
                    "total_appearances": len(positions),
                    "gaps_list": [],
                    "regularity_score": 0
                }
                continue
            
            # Calculer les écarts entre apparitions
            # Les positions sont ordonnées DESC, donc on inverse pour avoir les vrais écarts
            gaps = []
            for i in range(len(positions) - 1):
                gap = abs(positions[i] - positions[i + 1])
                gaps.append(gap)
            
            # Statistiques des écarts
            current_gap = positions[0]  # Écart depuis la dernière apparition
            average_gap = statistics.mean(gaps) if gaps else 0
            max_gap = max(gaps) if gaps else 0
            min_gap = min(gaps) if gaps else 0
            
            # Score de régularité (plus c'est proche de 1, plus c'est régulier)
            if gaps and len(gaps) > 1:
                std_dev = statistics.stdev(gaps)
                regularity_score = max(0, 1 - (std_dev / average_gap)) if average_gap > 0 else 0
            else:
                regularity_score = 0
            
            gaps_analysis[value] = {
                "current_gap": current_gap,
                "average_gap": round(average_gap, 2),
                "max_gap": max_gap,
                "min_gap": min_gap,
                "total_appearances": len(positions),
                "gaps_list": gaps[:10],  # Garder seulement les 10 derniers écarts
                "regularity_score": round(regularity_score, 3)
            }
        
        return gaps_analysis
    
    @staticmethod
    def _update_gaps_table(db: Session, attr_type: str, gaps_data: Dict, universe: str):
        """Met à jour la table attribute_gaps avec les nouvelles données"""
        
        for value, stats in gaps_data.items():
            # Vérifier si l'enregistrement existe
            existing = db.execute(text("""
                SELECT id FROM attribute_gaps 
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
                    UPDATE attribute_gaps SET
                        current_gap = :current_gap,
                        average_gap = :average_gap,
                        max_gap = :max_gap,
                        min_gap = :min_gap,
                        total_appearances = :total_appearances,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                """), {
                    "current_gap": stats["current_gap"],
                    "average_gap": stats["average_gap"],
                    "max_gap": stats["max_gap"],
                    "min_gap": stats["min_gap"],
                    "total_appearances": stats["total_appearances"],
                    "id": existing[0]
                })
            else:
                # Insérer nouveau
                db.execute(text("""
                    INSERT INTO attribute_gaps 
                    (attribute_type, attribute_value, universe, current_gap, 
                     average_gap, max_gap, min_gap, total_appearances)
                    VALUES (:attr_type, :value, :universe, :current_gap, 
                            :average_gap, :max_gap, :min_gap, :total_appearances)
                """), {
                    "attr_type": attr_type,
                    "value": str(value),
                    "universe": universe,
                    "current_gap": stats["current_gap"],
                    "average_gap": stats["average_gap"],
                    "max_gap": stats["max_gap"],
                    "min_gap": stats["min_gap"],
                    "total_appearances": stats["total_appearances"]
                })
        
        db.commit()
    
    @staticmethod
    def get_overdue_attributes(db: Session, universe: str = "mundo", threshold_multiplier: float = 1.5) -> Dict[str, List]:
        """Récupère les attributs en retard (écart actuel > moyenne * seuil)"""
        
        result = db.execute(text("""
            SELECT 
                attribute_type,
                attribute_value,
                current_gap,
                average_gap,
                (current_gap::float / NULLIF(average_gap, 0)) as delay_ratio,
                total_appearances
            FROM attribute_gaps 
            WHERE universe = :universe 
            AND average_gap > 0
            AND current_gap > (average_gap * :threshold)
            ORDER BY delay_ratio DESC
        """), {
            "universe": universe,
            "threshold": threshold_multiplier
        })
        
        overdue = {}
        for row in result:
            attr_type = row[0]
            if attr_type not in overdue:
                overdue[attr_type] = []
            
            overdue[attr_type].append({
                "value": row[1],
                "current_gap": row[2],
                "average_gap": float(row[3]),
                "delay_ratio": float(row[4]),
                "total_appearances": row[5]
            })
        
        return overdue
    
    @staticmethod
    def get_hot_attributes(db: Session, universe: str = "mundo", threshold_multiplier: float = 0.8) -> Dict[str, List]:
        """Récupère les attributs 'chauds' (écart actuel proche de la moyenne)"""
        
        result = db.execute(text("""
            SELECT 
                attribute_type,
                attribute_value,
                current_gap,
                average_gap,
                (current_gap::float / NULLIF(average_gap, 0)) as heat_ratio,
                total_appearances
            FROM attribute_gaps 
            WHERE universe = :universe 
            AND average_gap > 0
            AND current_gap >= (average_gap * :threshold)
            AND current_gap <= (average_gap * 1.2)
            ORDER BY heat_ratio DESC
        """), {
            "universe": universe,
            "threshold": threshold_multiplier
        })
        
        hot = {}
        for row in result:
            attr_type = row[0]
            if attr_type not in hot:
                hot[attr_type] = []
            
            hot[attr_type].append({
                "value": row[1],
                "current_gap": row[2],
                "average_gap": float(row[3]),
                "heat_ratio": float(row[4]),
                "total_appearances": row[5]
            })
        
        return hot
    
    @staticmethod
    def get_gaps_summary(db: Session, universe: str = "mundo") -> Dict[str, Any]:
        """Résumé général des écarts pour un univers"""
        
        result = db.execute(text("""
            SELECT 
                attribute_type,
                COUNT(*) as total_values,
                AVG(current_gap) as avg_current_gap,
                AVG(average_gap) as avg_historical_gap,
                MAX(current_gap) as max_current_gap,
                MIN(current_gap) as min_current_gap
            FROM attribute_gaps 
            WHERE universe = :universe
            GROUP BY attribute_type
            ORDER BY attribute_type
        """), {"universe": universe})
        
        summary = {}
        for row in result:
            summary[row[0]] = {
                "total_values": row[1],
                "avg_current_gap": round(float(row[2]), 2),
                "avg_historical_gap": round(float(row[3]), 2),
                "max_current_gap": row[4],
                "min_current_gap": row[5]
            }
        
        return summary