from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Test server is working!"}

@app.get("/health")
async def health():
    return {"status": "OK"}

if __name__ == "__main__":
    print("🚀 Démarrage du serveur de test...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 