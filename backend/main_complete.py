from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import json
import random

# Modèles Pydantic pour les requêtes
class CombinationRequest(BaseModel):
    numbers: List[int]
    universe: Optional[str] = None

class AnalysisRequest(BaseModel):
    universe: str
    start_date: str
    end_date: str
    marking_type: Optional[str] = "combination"

class PredictionRequest(BaseModel):
    input_numbers: List[int]
    prediction_horizon: int = 5

class DrawRequest(BaseModel):
    numbers: List[int]
    date: str
    draw_type: str = "standard"

# Modèles de réponse
class CombinationResponse(BaseModel):
    combination: str
    universe: str
    marking_types: Dict[str, Any]
    confidence: float

class AnalysisResponse(BaseModel):
    universe: str
    period: Dict[str, str]
    patterns: List[Dict[str, Any]]
    statistics: Dict[str, Any]

class PredictionResponse(BaseModel):
    predictions: List[Dict[str, Any]]
    confidence_scores: List[float]
    methodology: str

class DrawResponse(BaseModel):
    id: int
    numbers: List[int]
    date: str
    draw_type: str
    created_at: str

app = FastAPI(
    title="EazzyCalculator API",
    description="API complète pour l'analyse et la prédiction des numéros de loterie",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Données simulées pour les tests
MOCK_COMBINATIONS = [
    {"numbers": [1, 15, 23, 45, 67], "universe": "Mundo", "confidence": 0.85},
    {"numbers": [3, 12, 28, 41, 59], "universe": "Fruity", "confidence": 0.72},
    {"numbers": [7, 19, 34, 52, 78], "universe": "Trigga", "confidence": 0.91},
    {"numbers": [2, 11, 25, 38, 61], "universe": "Roaster", "confidence": 0.68},
    {"numbers": [9, 16, 31, 47, 73], "universe": "Sunshine", "confidence": 0.79}
]

MOCK_DRAWS = [
    {"id": 1, "numbers": [1, 15, 23, 45, 67], "date": "2025-08-01", "draw_type": "standard"},
    {"id": 2, "numbers": [3, 12, 28, 41, 59], "date": "2025-08-02", "draw_type": "standard"},
    {"id": 3, "numbers": [7, 19, 34, 52, 78], "date": "2025-08-03", "draw_type": "standard"}
]

# Routes principales
@app.get("/")
async def root():
    return {"message": "EazzyCalculator API is running", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "OK", "timestamp": datetime.now().isoformat()}

# Routes pour les combinaisons
@app.post("/api/combinations/classify", response_model=CombinationResponse)
async def classify_combination(request: CombinationRequest):
    """Classifie une combinaison dans un univers"""
    if len(request.numbers) != 5:
        raise HTTPException(status_code=400, detail="Une combinaison doit contenir exactement 5 numéros")
    
    # Logique de classification simulée
    sum_numbers = sum(request.numbers)
    if sum_numbers < 100:
        universe = "Mundo"
    elif sum_numbers < 150:
        universe = "Fruity"
    elif sum_numbers < 200:
        universe = "Trigga"
    elif sum_numbers < 250:
        universe = "Roaster"
    else:
        universe = "Sunshine"
    
    confidence = random.uniform(0.6, 0.95)
    
    return CombinationResponse(
        combination=" ".join(map(str, request.numbers)),
        universe=universe,
        marking_types={
            "chip": random.choice(["A", "B", "C"]),
            "combination": random.choice(["X", "Y", "Z"]),
            "denomination": random.randint(1, 10)
        },
        confidence=confidence
    )

@app.get("/api/combinations/search")
async def search_combinations(q: str = "", universe: str = "", limit: int = 10):
    """Recherche des combinaisons"""
    results = []
    for combo in MOCK_COMBINATIONS:
        if (not q or q in " ".join(map(str, combo["numbers"]))) and \
           (not universe or combo["universe"] == universe):
            results.append(combo)
            if len(results) >= limit:
                break
    
    return {"combinations": results, "total": len(results)}

# Routes pour l'analyse temporelle
@app.post("/api/analysis/temporal", response_model=AnalysisResponse)
async def temporal_analysis(request: AnalysisRequest):
    """Analyse temporelle des données"""
    # Simulation d'analyse temporelle
    patterns = [
        {"type": "recurrence", "description": "Numéros récurrents détectés", "confidence": 0.85},
        {"type": "cycle", "description": "Cycle de 7 jours identifié", "confidence": 0.72},
        {"type": "sequence", "description": "Séquence arithmétique trouvée", "confidence": 0.68}
    ]
    
    statistics = {
        "total_draws": random.randint(50, 200),
        "most_frequent": [7, 15, 23, 41, 67],
        "least_frequent": [2, 11, 19, 37, 73],
        "average_sum": random.randint(120, 180)
    }
    
    return AnalysisResponse(
        universe=request.universe,
        period={"start": request.start_date, "end": request.end_date},
        patterns=patterns,
        statistics=statistics
    )

@app.get("/api/analysis/patterns/{universe}")
async def get_patterns(universe: str):
    """Récupère les patterns pour un univers donné"""
    patterns = {
        "Mundo": ["Pattern A", "Pattern B"],
        "Fruity": ["Pattern C", "Pattern D"],
        "Trigga": ["Pattern E", "Pattern F"],
        "Roaster": ["Pattern G", "Pattern H"],
        "Sunshine": ["Pattern I", "Pattern J"]
    }
    
    return {"universe": universe, "patterns": patterns.get(universe, [])}

# Routes pour les prédictions IA
@app.post("/api/predictions/generate", response_model=PredictionResponse)
async def generate_predictions(request: PredictionRequest):
    """Génère des prédictions IA"""
    predictions = []
    confidence_scores = []
    
    for i in range(request.prediction_horizon):
        # Simulation de prédictions
        pred_numbers = sorted(random.sample(range(1, 91), 5))
        confidence = random.uniform(0.6, 0.95)
        
        predictions.append({
            "draw_number": i + 1,
            "numbers": pred_numbers,
            "universe": random.choice(["Mundo", "Fruity", "Trigga", "Roaster", "Sunshine"]),
            "date": (datetime.now() + timedelta(days=i+1)).strftime("%Y-%m-%d")
        })
        confidence_scores.append(confidence)
    
    return PredictionResponse(
        predictions=predictions,
        confidence_scores=confidence_scores,
        methodology="LSTM Neural Network + Temporal Analysis"
    )

@app.get("/api/predictions/history")
async def get_prediction_history(limit: int = 10):
    """Historique des prédictions"""
    history = []
    for i in range(limit):
        history.append({
            "id": i + 1,
            "date": (datetime.now() - timedelta(days=i+1)).strftime("%Y-%m-%d"),
            "predicted": sorted(random.sample(range(1, 91), 5)),
            "actual": sorted(random.sample(range(1, 91), 5)),
            "accuracy": random.uniform(0.2, 0.8)
        })
    
    return {"history": history}

# Routes pour les tirages
@app.post("/api/draws/create", response_model=DrawResponse)
async def create_draw(request: DrawRequest):
    """Crée un nouveau tirage"""
    if len(request.numbers) != 5:
        raise HTTPException(status_code=400, detail="Un tirage doit contenir exactement 5 numéros")
    
    new_draw = {
        "id": len(MOCK_DRAWS) + 1,
        "numbers": request.numbers,
        "date": request.date,
        "draw_type": request.draw_type,
        "created_at": datetime.now().isoformat()
    }
    
    MOCK_DRAWS.append(new_draw)
    return DrawResponse(**new_draw)

@app.get("/api/draws/list")
async def list_draws(limit: int = 10, draw_type: str = ""):
    """Liste des tirages"""
    draws = MOCK_DRAWS
    if draw_type:
        draws = [d for d in draws if d["draw_type"] == draw_type]
    
    return {"draws": draws[:limit], "total": len(draws)}

@app.get("/api/draws/{draw_id}")
async def get_draw(draw_id: int):
    """Récupère un tirage spécifique"""
    for draw in MOCK_DRAWS:
        if draw["id"] == draw_id:
            return draw
    raise HTTPException(status_code=404, detail="Tirage non trouvé")

# Routes pour les résultats gagnants
@app.get("/api/results/winners")
async def get_winning_results(limit: int = 10):
    """Résultats gagnants"""
    winners = []
    for i in range(limit):
        winners.append({
            "id": i + 1,
            "date": (datetime.now() - timedelta(days=i*3)).strftime("%Y-%m-%d"),
            "numbers": sorted(random.sample(range(1, 91), 5)),
            "prize_amount": random.randint(1000, 100000),
            "winners_count": random.randint(1, 50)
        })
    
    return {"winners": winners}

@app.get("/api/results/statistics")
async def get_results_statistics():
    """Statistiques des résultats"""
    return {
        "total_draws": len(MOCK_DRAWS),
        "total_prizes": random.randint(100000, 1000000),
        "average_prize": random.randint(5000, 25000),
        "most_common_numbers": [7, 15, 23, 41, 67],
        "least_common_numbers": [2, 11, 19, 37, 73]
    }

# Routes pour le workflow KATOOLING
@app.post("/api/katooling/execute")
async def execute_katooling_workflow(request: PredictionRequest):
    """Exécute le workflow KATOOLING complet"""
    # Simulation du workflow en 5 étapes
    steps = {
        "step1_data_collection": {
            "status": "completed",
            "data_points": random.randint(100, 500),
            "quality_score": random.uniform(0.8, 0.95)
        },
        "step2_classification": {
            "status": "completed",
            "universes_analyzed": ["Mundo", "Fruity", "Trigga", "Roaster", "Sunshine"],
            "combinations_classified": random.randint(50, 200)
        },
        "step3_temporal_analysis": {
            "status": "completed",
            "patterns_detected": random.randint(5, 15),
            "cycles_identified": random.randint(2, 8)
        },
        "step4_ai_predictions": {
            "status": "completed",
            "predictions_generated": request.prediction_horizon,
            "average_confidence": random.uniform(0.7, 0.9)
        },
        "step5_validation": {
            "status": "completed",
            "validation_score": random.uniform(0.75, 0.95),
            "recommendations": ["Utiliser les prédictions avec confiance élevée", "Surveiller les patterns temporels"]
        }
    }
    
    return {
        "workflow_version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "input_numbers": request.input_numbers,
        "steps": steps,
        "summary": {
            "overall_confidence": random.uniform(0.8, 0.95),
            "recommended_action": "Proceed with predictions",
            "risk_level": "Low"
        }
    }

@app.get("/api/katooling/status")
async def get_katooling_status():
    """Statut du service KATOOLING"""
    return {
        "service": "KATOOLING Workflow",
        "status": "operational",
        "version": "1.0.0",
        "last_update": datetime.now().isoformat(),
        "endpoints_available": [
            "/api/katooling/execute",
            "/api/katooling/status"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 