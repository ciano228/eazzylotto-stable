from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Modèles d'authentification
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
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int

# Modèles de calcul
class CalcRequest(BaseModel):
    expr: str

class CalcResponse(BaseModel):
    expr: str
    result: float
    status: str

# Modèles de session
class SessionBase(BaseModel):
    name: str
    status: str = "active"

class SessionCreate(SessionBase):
    draws: List[int]

class Session(SessionBase):
    id: int
    date: datetime
    draws: List[int]

    class Config:
        from_attributes = True

# Modèles de prédiction
class Prediction(BaseModel):
    id: int
    numbers: List[int]
    confidence: float
    model: str
    date: str
    status: str

# Modèles d'analyse
class AnalyticsTrend(BaseModel):
    date: str
    sessions: int
    accuracy: float

class FrequencyData(BaseModel):
    number: int
    frequency: int

class AnalyticsResponse(BaseModel):
    stats: dict
    trends: List[AnalyticsTrend]
    frequency: List[FrequencyData]
