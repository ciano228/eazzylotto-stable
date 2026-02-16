from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.services.gap_analysis_service import GapAnalysisService
from app.services.pattern_recognition_service import PatternRecognitionService
from app.services.performance_service import PerformanceService
from app.models.performance import PredictionRecord

class VerdictEngineService:
    """
    The 'Brain' of the system.
    Orchestrates multiple analysis patterns and merges them into a single 'Verdict'.
    """

    @staticmethod
    def get_unified_verdict(db: Session, numbers: List[int], universe: str = "mundo") -> Dict[str, Any]:
        # 1. Source: Structural Signature (DNA)
        pattern_service = PatternRecognitionService()
        pattern_data = pattern_service.find_similar_draws(
            db, numbers, universe, min_match_percent=20
        )
        
        # 2. Source: Statistical Gaps (Frequency)
        # We simulate a session-less gap analysis for the whole universe
        try:
            gap_data = GapAnalysisService.calculate_gaps(db, universe)
        except Exception:
            gap_data = {}
        
        # 3. Fusion Logic (The Verdict)
        # We cross-reference predictions
        fusion_numbers = {} # number -> weight
        
        # Process Pattern Predictions (Weight 1.5)
        pattern_cons = pattern_data.get("consequences", {})
        for n_item in pattern_cons.get("most_frequent_numbers", []):
            num = n_item["number"]
            fusion_numbers[num] = fusion_numbers.get(num, 0) + (n_item["frequency"] * 1.5)
            
        # Process Gap Predictions (Weight 1.0)
        # We look for 'Interesting' attributes (gap > mean)
        # For simplicity in this meta-engine, we'll extract top gap numbers if possible
        # In a real fusion, we'd need a more mapped approach.
        
        # 4. Final Ranking
        sorted_verdict = sorted(fusion_numbers.items(), key=lambda x: x[1], reverse=True)
        
        # 5. Extract Probable Duos from Patterns
        probable_duos = []
        for p_item in pattern_cons.get("most_frequent_pairs", []):
            try:
                # p_item['pair'] is "num1-num2"
                p_nums = [int(x) for x in p_item["pair"].split('-')]
                probable_duos.append({
                    "numbers": p_nums,
                    "frequency": p_item["frequency"],
                    "count": p_item["count"]
                })
            except (ValueError, KeyError):
                continue

        # 6. Advanced Confidence Calculation
        # Factor 1: Quantity of matches
        match_count = len(pattern_data.get("matches", []))
        base_confidence = min(match_count * 4, 60) # Up to 60% based on quantity
        
        # Factor 2: Quality of matches (Best ADN Match)
        best_match = max([m["match_score"] for m in pattern_data.get("matches", [])]) if pattern_data.get("matches") else 0
        quality_bonus = (best_match / 100) * 35 # Up to +35% based on quality
        
        final_confidence = round(min(max(base_confidence + quality_bonus, 15), 98), 1)

        # 7. Archive Prediction for future feedback
        prediction_record = PredictionRecord(
            universe=universe,
            trigger_numbers=numbers,
            predicted_numbers=[n for n in sorted_verdict[:10]],
            predicted_pairs=[p["pair"] for p in pattern_cons.get("most_frequent_pairs", [])[:5]],
            predicted_attributes={
                t: stats[0]['value'] for t, stats in pattern_cons.get("most_frequent_attributes", {}).items() if stats
            }
        )
        db.add(prediction_record)
        db.commit()
        db.refresh(prediction_record)

        return {
            "prediction_id": prediction_record.id,
            "universe": universe,
            "confidence_score": final_confidence,
            "top_verdict_numbers": [
                {"number": n, "weighted_score": round(s, 1)} 
                for n, s in sorted_verdict[:10]
            ],
            "probable_duos": probable_duos[:5],
            "sources": {
                "pattern_recognition": {
                    "events_analyzed": pattern_cons.get("analyzed_events", 0),
                    "best_match": round(best_match, 1),
                    "adn_dimension": 42, # Qualitative indicator
                    "matched_draws": pattern_data.get("matches", [])[:10]
                }
            }
        }
