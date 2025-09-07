from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

users = {"admin": {"email": "admin@test.com", "password": "admin"}}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "auth_available": True}

@app.post("/api/auth/register")
async def register(user: UserCreate):
    users[user.username] = {"email": user.email, "password": user.password}
    return {"access_token": f"token_{user.username}", "token_type": "bearer", "user_id": 1}

@app.post("/api/auth/login")
async def login(user: UserLogin):
    if user.username not in users or users[user.username]["password"] != user.password:
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    return {"access_token": f"token_{user.username}", "token_type": "bearer", "user_id": 1}

@app.get("/api/auth/me")
async def get_me(authorization: str = Header(None)):
    return {"id": 1, "username": "test", "email": "test@example.com"}

@app.get("/api/sessions")
async def get_sessions(authorization: str = Header(None)):
    return [
        {"id": 1, "name": "Session Test 1", "date": "2024-01-15", "draws": [1, 5, 12, 23, 34], "status": "active"},
        {"id": 2, "name": "Session Test 2", "date": "2024-01-14", "draws": [3, 8, 15, 27, 41], "status": "completed"}
    ]

@app.get("/api/analytics")
async def get_analytics(authorization: str = Header(None)):
    return {
        "stats": {"totalSessions": 45, "totalDraws": 1250, "winRate": 12.5, "avgAccuracy": 78.3},
        "trends": [{"date": "2024-01-01", "sessions": 5, "accuracy": 75}],
        "frequency": [{"number": 1, "frequency": 25}]
    }

@app.get("/api/ml/predictions")
async def get_predictions(authorization: str = Header(None)):
    return {
        "predictions": [
            {"id": 1, "numbers": [7, 14, 21, 28, 35], "confidence": 85, "model": "LSTM", "date": "2024-01-15", "status": "pending"}
        ],
        "accuracy": 82.5
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)