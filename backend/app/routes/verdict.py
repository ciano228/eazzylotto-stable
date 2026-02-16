from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database.connection import get_db
from app.services.verdict_engine_service import VerdictEngineService
from app.models.performance import PredictionRecord
from pydantic import BaseModel

router = APIRouter()

class VerdictRequest(BaseModel):
    numbers: List[int]
    universe: str = "mundo"

class FeedbackRequest(BaseModel):
    prediction_id: int
    actual_numbers: List[int]

@router.post("/analyze")
async def get_ai_verdict(req: VerdictRequest, db: Session = Depends(get_db)):
    """
    Unified AI endpoint that provides a final verdict by fusing multiple analysis models.
    """
    try:
        verdict = VerdictEngineService.get_unified_verdict(db, req.numbers, req.universe)
        return verdict
    except Exception as e:
        import traceback
        print(f"Error in Verdict Engine: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Intelligence Engine Error: {str(e)}")

@router.post("/feedback")
async def submit_prediction_feedback(req: FeedbackRequest, db: Session = Depends(get_db)):
    """
    Submit real results for a previous prediction to evaluate performance and improve models.
    """
    try:
        record = db.query(PredictionRecord).filter(PredictionRecord.id == req.prediction_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Prediction record not found")
        
        # 1. Update actual numbers
        record.actual_numbers = req.actual_numbers
        record.is_evaluated = True
        
        # 2. Simple Hit Calculation (How many predicted numbers are in the actual draw?)
        predicted_data = record.predicted_numbers # List of [number, weight]
        if predicted_data and isinstance(predicted_data, list):
            # If stored as list of tuples/lists [num, weight]
            p_nums = [n[0] if isinstance(n, (list, tuple)) else n for n in predicted_data]
            actual_set = set(req.actual_numbers)
            hits = [n for n in p_nums if n in actual_set]
            
            # Score: percentage of hits relative to top 5 most probable
            record.hit_score_numbers = len(hits) / 5.0
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Feedback recorded",
            "hits_detected": len(hits) if 'hits' in locals() else 0,
            "hit_score": record.hit_score_numbers
        }
    except Exception as e:
        print(f"Error in Feedback Submission: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
