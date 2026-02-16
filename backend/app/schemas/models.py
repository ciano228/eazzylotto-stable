"""
Schémas Pydantic pour les modèles de données
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Schémas d'authentification
class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class User(UserBase):
    id: int
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: Optional[int] = None


class TokenData(BaseModel):
    user_id: Optional[int] = None


# Schémas de calcul
class CalcRequest(BaseModel):
    expr: str = Field(..., description="Expression mathématique à évaluer")


class CalcResponse(BaseModel):
    result: float
    expression: str


# Schémas Katula
class KatulaMatrixRequest(BaseModel):
    universe: str = "mundo"
    chip_number: Optional[int] = None


class KatulaAnalysisRequest(BaseModel):
    universe: str = "mundo"
    numbers: List[int]


class JournalEntryRequest(BaseModel):
    num1: int
    num2: int


class DrawValidationRequest(BaseModel):
    numbers: List[int]
    universe: str = "mundo"


# Schémas de session
class SessionCreate(BaseModel):
    name: str
    lottery_type: str
    description: Optional[str] = None


class SessionUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None


class DrawCreate(BaseModel):
    draw_number: int
    draw_date: str
    winning_numbers: List[int]
    lottery_name: str
    is_completed: bool = True


# Schémas d'analyse
class AnalysisRequest(BaseModel):
    session_id: int
    universe: str = "mundo"
    analysis_type: str = "full"


class PredictionRequest(BaseModel):
    universe: str = "mundo"
    historical_draws: List[List[int]]
    prediction_count: int = 5
