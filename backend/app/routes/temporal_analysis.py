"""
Route API pour l'analyse temporelle par drawer
Agrège les occurrences de drawers par position de chip sur les grilles Katula
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from collections import defaultdict

router = APIRouter()

@router.get("/temporal-drawer-data")
async def get_temporal_drawer_data(
    session_id: Optional[str] = Query(None, description="ID de la session à analyser (Int ou UUID)"),
    session_name: Optional[str] = Query(None, description="Nom de la session à analyser"),
    cycle: Optional[int] = Query(None, description="Numéro du cycle à analyser (1, 2...)"),
    universe: str = Query("mundo", description="Univers (fruity, mundo, etc.)"),
    date_start: Optional[str] = Query(None, description="Date de début (YYYY-MM-DD)"),
    date_end: Optional[str] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    marking_type: str = Query("drawer", description="Type de marquage (drawer, chip, denomination, etc.)")
):
    """
    Récupère les données temporelles agrégées par drawer pour les mini-grids Katula
    
    Retourne les occurrences par chip avec drawer_name et forme depuis la BD
    """
    try:
        from app.services.analysis_service import AnalysisService
        import psycopg2
        from app.database.connection import SessionLocal
        from app.models.session import WorkSession

        # Résoudre le nom de session en ID si nécessaire
        if not session_id and session_name:
            db_lookup = SessionLocal()
            try:
                # Recherche insensible à la casse et partielle si possible, ou exacte
                session = db_lookup.query(WorkSession).filter(WorkSession.name == session_name).first()
                if session:
                    session_id = session.id
                else:
                    # Essayer avec LIKE
                    session = db_lookup.query(WorkSession).filter(WorkSession.name.ilike(f"%{session_name}%")).first()
                    if session:
                        session_id = session.id
                    else:
                        raise HTTPException(status_code=404, detail=f"Session '{session_name}' non trouvée")
            finally:
                db_lookup.close()

        # Récupérer le journal statistique avec drawer_name
        db_params = {
            'host': 'localhost',
            'database': 'katooling_main_system',
            'user': 'postgres',
            'password': 'Katulaa_33',
            'port': 5432
        }
        
        # S'il y a un session_id, utiliser le service existant
        if session_id:
            from app.database.connection import SessionLocal
            db = SessionLocal()
            try:
                min_draw = None
                max_draw = None
                
                # Si cycle spécifié, calculer les bornes
                if cycle is not None:
                    session_info = db.query(WorkSession).filter(WorkSession.id == session_id).first()
                    if session_info and session_info.cycle_length:
                        cycle_len = session_info.cycle_length
                        min_draw = (cycle - 1) * cycle_len + 1
                        max_draw = cycle * cycle_len
                
                journal_result = AnalysisService.generate_statistical_journal(
                    db=db,
                    universe=universe,
                    session_id=session_id,
                    min_draw=min_draw,
                    max_draw=max_draw
                )
            finally:
                db.close()
        else:
            # Si pas de session_id, utiliser les dates
            from app.database.connection import SessionLocal
            db = SessionLocal()
            try:
                journal_result = AnalysisService.generate_statistical_journal(
                    db=db,
                    universe=universe,
                    start_date=date_start,
                    end_date=date_end
                )
            finally:
                db.close()
        
        journal_entries = journal_result.get("journal", [])
        
        # Agréger par drawer_name (drawers sont les entités principales)
        drawer_occurrences = {}  # drawer_name -> {chip, forme, count, details}
        
        for entry in journal_entries:
            # Ignorer les entrées N-D et N-H
            if entry.get("status") not in ["completed"]:
                continue
            
            chip_str = entry.get("chip")  # Ex: "chip1", "chip2"
            if not chip_str or chip_str in ["N-D", "N-H"]:
                continue
            
            # Extraire le numéro du chip (chip1 -> 1, chip15 -> 15)
            try:
                if isinstance(chip_str, str) and chip_str.startswith("chip"):
                    chip_number = int(chip_str.replace("chip", ""))
                else:
                    chip_number = int(chip_str)
            except (ValueError, AttributeError):
                continue
            
            # Récupérer l'attribut selon le marking_type
            if marking_type == "drawer":
                drawer_name = entry.get("drawer_name") or entry.get("drawer")
                forme = entry.get("forme")
                
                if not drawer_name:
                    continue
                
                # Agréger par drawer_name (ex: drawer1, drawer10, drawer100...)
                if drawer_name not in drawer_occurrences:
                    drawer_occurrences[drawer_name] = {
                        "drawer_name": drawer_name,
                        "chip_number": chip_number,  # Position sur la grille
                        "forme": forme,
                        "count": 0,
                        "attributes": [],
                        "details": []
                    }
                
                drawer_occurrences[drawer_name]["count"] += 1
                drawer_occurrences[drawer_name]["attributes"].append(drawer_name)
                drawer_occurrences[drawer_name]["details"].append({
                    "drawer_name": drawer_name,
                    "chip_number": chip_number,
                    "forme": forme,
                    "date": entry.get("date"),
                    "lottery_name": entry.get("lottery_name")
                })
                
            elif marking_type == "chip":
                # Mode chip classique - agréger par position chip
                if chip_number not in drawer_occurrences:
                    drawer_occurrences[chip_number] = {
                        "chip_number": chip_number,
                        "count": 0,
                        "attributes": [chip_number],
                        "details": []
                    }
                drawer_occurrences[chip_number]["count"] += 1
                drawer_occurrences[chip_number]["details"].append({
                    "chip": chip_number,
                    "date": entry.get("date")
                })
                
            elif marking_type == "denomination":
                denomination = entry.get("denomination")
                if not denomination or denomination in ["N-D", "N-H"]:
                    continue
                    
                # Pour denomination, on groupe aussi par chip
                if chip_number not in drawer_occurrences:
                    drawer_occurrences[chip_number] = {
                        "chip_number": chip_number,
                        "count": 0,
                        "attributes": [],
                        "details": []
                    }
                drawer_occurrences[chip_number]["count"] += 1
                drawer_occurrences[chip_number]["attributes"].append(denomination)
                drawer_occurrences[chip_number]["details"].append({
                    "denomination": denomination,
                    "chip": chip_number,
                    "date": entry.get("date")
                })
            
            elif marking_type == "forme":
                forme = entry.get("forme")
                if not forme or forme in ["N-D", "N-H"]:
                    continue
                    
                # Pour forme, on groupe par chip
                if chip_number not in drawer_occurrences:
                    drawer_occurrences[chip_number] = {
                        "chip_number": chip_number,
                        "forme": forme,
                        "count": 0,
                        "attributes": [],
                        "details": []
                    }
                drawer_occurrences[chip_number]["count"] += 1
                drawer_occurrences[chip_number]["attributes"].append(forme)
                drawer_occurrences[chip_number]["details"].append({
                    "forme": forme,
                    "chip": chip_number,
                    "date": entry.get("date")
                })
        
        
        # Compter le total de tirages analysés
        total_draws = len(set(entry.get("draw_id") for entry in journal_entries if entry.get("status") == "completed"))
        
        # Pour le mode drawer: regrouper les drawers par position chip
        if marking_type == "drawer":
            # Créer un mapping chip_number -> liste de drawers
            occurrences_by_chip = {}
            for drawer_name, drawer_data in drawer_occurrences.items():
                chip_pos = drawer_data["chip_number"]
                
                if chip_pos not in occurrences_by_chip:
                    occurrences_by_chip[chip_pos] = {
                        "count": 0,
                        "drawers": [],  # Liste des drawers à cette position
                        "attributes": [],
                        "details": []
                    }
                
                # Ajouter ce drawer à la position chip
                occurrences_by_chip[chip_pos]["count"] += drawer_data["count"]
                occurrences_by_chip[chip_pos]["drawers"].append({
                    "drawer_name": drawer_name,
                    "forme": drawer_data["forme"],
                    "count": drawer_data["count"]
                })
                occurrences_by_chip[chip_pos]["attributes"].extend(drawer_data["attributes"])
                occurrences_by_chip[chip_pos]["details"].extend(drawer_data["details"])
            
            return {
                "status": "success",
                "universe": universe,
                "marking_type": marking_type,
                "occurrences": occurrences_by_chip,  # Indexé par chip_number
                "drawer_details": drawer_occurrences,  # Détails par drawer_name
                "total_draws": total_draws,
                "total_entries": len(journal_entries),
                "session_id": session_id,
                "period_label": journal_entries[0].get("cycle_info") or (f"Période {journal_entries[0].get('period')}" if journal_entries[0].get('period') else None) if journal_entries else None,
                "date_range": {
                    "start": date_start,
                    "end": date_end
                }
            }
        else:
            # Pour les autres modes (chip, denomination, forme)
            return {
                "status": "success",
                "universe": universe,
                "marking_type": marking_type,
                "occurrences": drawer_occurrences,
                "total_draws": total_draws,
                "total_entries": len(journal_entries),
                "session_id": session_id,
                "period_label": journal_entries[0].get("cycle_info") or (f"Période {journal_entries[0].get('period')}" if journal_entries[0].get('period') else None) if journal_entries else None,
                "date_range": {
                    "start": date_start,
                    "end": date_end
                }
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur analyse temporelle: {str(e)}")
