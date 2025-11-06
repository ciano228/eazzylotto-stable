from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.katula import router as katula_router

app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes de base
@app.get("/")
async def root():
    return {"message": "Katula API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Monter les routes Katula
app.include_router(katula_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
