from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.utils.safe_eval import SafeEvaluator
from app.database.connection import get_db
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/calculate",
    tags=["calculator"]
)

class CalcRequest(BaseModel):
    expr: str

@router.post("/", response_model=Dict[str, Any])
async def calculate(request: CalcRequest, db: Session = Depends(get_db)):
    """
    Calcule le résultat d'une expression mathématique simple.
    """
    expr = request.expr.strip()
    if not expr:
        raise HTTPException(status_code=400, detail="L'expression est vide")
        
    try:
        evaluator = SafeEvaluator()
        result = evaluator.evaluate(expr)
        return {
            "expr": expr,
            "result": result,
            "status": "success"
        }
    except ValueError as e:
        logger.debug("Erreur de calcul: %s", e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Erreur inattendue lors de l'évaluation")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne d'évaluation"
        )
