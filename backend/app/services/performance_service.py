from sqlalchemy.orm import Session
from sqlalchemy import text, func
from app.models.performance import PredictionRecord
from datetime import datetime
from typing import List, Dict, Any

class PerformanceService:
    @staticmethod
    def record_prediction(db: Session, universe: str, trigger_numbers: List[int], 
                          predicted_numbers: List[Dict], predicted_pairs: List[str], 
                          predicted_attributes: Dict) -> PredictionRecord:
        """Enregistre une nouvelle prédiction pour suivi ultérieur"""
        record = PredictionRecord(
            universe=universe,
            trigger_numbers=trigger_numbers,
            predicted_numbers=predicted_numbers,
            predicted_pairs=predicted_pairs,
            predicted_attributes=predicted_attributes
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def evaluate_all_pending(db: Session):
        """Recherche les tirages réels qui ont suivi les prédictions et calcule les scores"""
        pending = db.query(PredictionRecord).filter(PredictionRecord.is_evaluated == False).all()
        evaluated_count = 0
        
        for record in pending:
            # Chercher le tirage juste après la date de prédiction
            # Note: prediction_date est au format datetime
            query = text("""
                SELECT winning_numbers, draw_date 
                FROM session_draws 
                WHERE draw_date > :p_date 
                ORDER BY draw_date ASC 
                LIMIT 1
            """)
            res = db.execute(query, {'p_date': record.prediction_date}).fetchone()
            
            if res:
                actual_nums = res.winning_numbers
                record.actual_numbers = actual_nums
                record.draw_date = res.draw_date
                
                # Calcul des scores
                # 1. Score Numéros (Combien de numéros prédits sont dans le tirage réel)
                pred_nums_only = [p['number'] for p in (record.predicted_numbers or [])[:5]]
                hits = [n for n in actual_nums if n in pred_nums_only]
                record.hit_score_numbers = len(hits) / len(actual_nums) if actual_nums else 0
                
                # 2. Score Attributs (TODO: Analyse plus fine de l'ADN)
                # Pour l'instant on marque comme évalué
                record.is_evaluated = True
                evaluated_count += 1
        
        db.commit()
        return evaluated_count

    @staticmethod
    def get_stats(db: Session, universe: str = None) -> Dict[str, Any]:
        """Récupère les statistiques globales de performance"""
        query = db.query(PredictionRecord).filter(PredictionRecord.is_evaluated == True)
        if universe:
            query = query.filter(PredictionRecord.universe == universe)
        
        records = query.order_by(PredictionRecord.draw_date.desc()).all()
        
        if not records:
            return {"status": "No data yet"}
            
        avg_hit_rate = sum(r.hit_score_numbers for r in records) / len(records)
        
        # Evolution (last 10)
        evolution = [
            {"date": r.draw_date.isoformat(), "score": round(r.hit_score_numbers * 100, 1)} 
            for r in records[:10]
        ][::-1]
        
        return {
            "total_evaluated": len(records),
            "global_accuracy": round(avg_hit_rate * 100, 2),
            "evolution": evolution,
            "last_predictions": [
                {
                    "date": r.prediction_date.isoformat(),
                    "universe": r.universe,
                    "score": round(r.hit_score_numbers * 100, 1),
                    "trigger": r.trigger_numbers,
                    "actual": r.actual_numbers
                } for r in records[:5]
            ]
        }
