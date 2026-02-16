from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.database.connection import get_db
from app.services.pattern_recognition_service import PatternRecognitionService

router = APIRouter()

class DrawAnalysisRequest(BaseModel):
    numbers: List[int]
    universe: str = "mundo"
    threshold: int = 50

class DrawAnalysisResponse(BaseModel):
    target_numbers: List[int]
    universe: str
    total_matches: int
    matches: List[dict]
    consequences: dict

@router.post("/analyze-draw")
async def analyze_draw_pattern(
    request: DrawAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Analyzes a draw's structural pattern (signature) and finds historical matches
    to predict future consequences.
    """
    try:
        service = PatternRecognitionService()
        result = service.find_similar_draws(
            db, 
            request.numbers, 
            request.universe, 
            request.threshold
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
            
        # Return with matched_draws and simplified keys for frontend consistency
        matched_draws = []
        for m in result.get("matches", []):
            m_copy = m.copy()
            m_copy["numbers"] = m.get("draw_numbers") # Legacy key support
            m_copy["date"] = m.get("draw_date")       # Legacy key support
            matched_draws.append(m_copy)

        return {
            "target_numbers": result["target_numbers"],
            "universe": result["universe"],
            "total_matches": result["total_matches"],
            "matches": matched_draws,
            "matched_draws": matched_draws,
            "consequences": result["consequences"]
        }
        
    except Exception as e:
        print(f"Error in analyze_draw_pattern: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analyze")
async def analyze_draw_get(
    numbers: str = Query(..., description="Comma separated numbers"),
    universe: str = "mundo",
    threshold: int = 20,
    db: Session = Depends(get_db)
):
    """
    GET version for easy frontend integration, using a unique path to avoid 405 conflicts.
    """
    try:
        nums_list = [int(n.strip()) for n in numbers.split(',') if n.strip().isdigit()]
        service = PatternRecognitionService()
        result = service.find_similar_draws(db, nums_list, universe, threshold)
        
        matched_draws = []
        for m in result.get("matches", []):
            m_copy = m.copy()
            m_copy["numbers"] = m.get("draw_numbers")
            m_copy["date"] = m.get("draw_date")
            matched_draws.append(m_copy)

        return {
            "target_numbers": nums_list,
            "universe": universe,
            "total_matches": result.get("total_matches", 0),
            "matches": matched_draws,
            "matched_draws": matched_draws,
            "consequences": result.get("consequences", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signature")
async def get_draw_signature(
    numbers: str = Query(..., description="Comma separated numbers, e.g. 70,89,54,25,34"),
    universe: str = "mundo"
):
    """
    Returns the raw signature (attribute list) for a given set of numbers.
    """
    try:
        nums_list = [int(n.strip()) for n in numbers.split(',') if n.strip().isdigit()]
        if len(nums_list) < 2:
            raise HTTPException(status_code=400, detail="At least 2 numbers required")
            
        service = PatternRecognitionService()
        signature = service.generate_draw_signature(nums_list, universe)
        
        return {
            "numbers": nums_list,
            "universe": universe,
            "signature": signature
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analyze-session")
async def analyze_session(
    session_id: Optional[int] = Query(None, description="ID of the session"),
    numbers: Optional[str] = Query(None, description="Comma separated numbers (fallback)"),
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    universe: str = "mundo",
    db: Session = Depends(get_db)
):
    """
    Analyzes either a session evolution OR a specific draw if 'numbers' is provided (legacy fallback).
    """
    try:
        service = PatternRecognitionService()
        
        # Fallback for cached frontend calling this with numbers instead of session_id
        if numbers and not session_id:
            nums_list = [int(n.strip()) for n in numbers.split(',') if n.strip().isdigit()]
            result = service.find_similar_draws(db, nums_list, universe, 20)
            
            matched_draws = []
            for m in result.get("matches", []):
                m_copy = m.copy()
                m_copy["numbers"] = m.get("draw_numbers")
                m_copy["date"] = m.get("draw_date")
                matched_draws.append(m_copy)

            return {
                "target_numbers": nums_list,
                "universe": universe,
                "total_matches": result.get("total_matches", 0),
                "matched_draws": matched_draws,
                "consequences": result.get("consequences", {})
            }

        if not session_id:
            raise HTTPException(status_code=400, detail="session_id or numbers required")

        result = service.analyze_session_evolution(
            db,
            session_id,
            start_date,
            end_date,
            universe
        )
        return result
    except Exception as e:
        print(f"Error in analyze_session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
