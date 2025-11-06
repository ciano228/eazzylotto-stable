@app.get("/api/inspect-db")
async def inspect_db():
    KatulaCompleteService.inspect_database_structure()
    return {"status": "Inspection terminée, vérifiez les logs du serveur"}