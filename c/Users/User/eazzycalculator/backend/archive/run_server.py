import uvicorn

if __name__ == "__main__":
    print("Démarrage du serveur Katula...")
    uvicorn.run("standalone_katula:app", host="0.0.0.0", port=8000, reload=True)
