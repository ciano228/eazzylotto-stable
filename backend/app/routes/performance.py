from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.database.connection import get_db
from app.services.performance_service import PerformanceService
from pydantic import BaseModel

router = APIRouter()

class PredictionCreate(BaseModel):
    universe: str
    trigger_numbers: List[int]
    predicted_numbers: List[Dict]
    predicted_pairs: List[str]
    predicted_attributes: Dict

@router.post("/record")
async def record_prediction(req: PredictionCreate, db: Session = Depends(get_db)):
    try:
        record = PerformanceService.record_prediction(
            db, req.universe, req.trigger_numbers, 
            req.predicted_numbers, req.predicted_pairs, req.predicted_attributes
        )
        return {"status": "success", "id": record.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluate")
async def evaluate_predictions(db: Session = Depends(get_db)):
    try:
        count = PerformanceService.evaluate_all_pending(db)
        return {"status": "success", "evaluated_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_stats(universe: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        # Trigger evaluation before getting stats to be up to date
        PerformanceService.evaluate_all_pending(db)
        stats = PerformanceService.get_stats(db, universe)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
