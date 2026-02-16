
@api_app.get("/stats/advanced/{session_id}")
async def get_advanced_session_stats(session_id: str, universe: Optional[str] = Query(None)):
    """
    Récupère les statistiques avancées pour une session donnée.
    Calcule Count, Fréquence, Dernière Sortie, et Écart (Due) pour tous les attributs.
    """
    try:
        # 1. Récupérer les tirages de la session
        session_draws = session_service.get_session_draws(session_id)
        
        if not session_draws:
             return {"status": "warning", "message": "Aucun tirage trouvé pour cette session", "stats": {}}

        # 2. Déterminer l'univers
        # Soit passé en paramètre, soit déduit de la session (si dispo), soit 'mundo' par défaut
        target_universe = universe or "mundo"
        # Idéalement, la session devrait stocker l'univers. On regarde si le premier tirage a l'info.
        if not universe and session_draws and 'universe' in session_draws[0]:
            target_universe = session_draws[0]['universe']

        # 3. Calculer les stats
        stats = stats_engine.calculate_stats(session_draws, target_universe)
        
        return {
            "status": "success",
            "session_id": session_id,
            "universe": target_universe,
            "total_draws": len(session_draws),
            "stats": stats
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur calcul statistiques: {str(e)}")
