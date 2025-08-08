from typing import List, Dict, Any
from collections import Counter
from sqlalchemy.orm import Session
from app.models.draw import Draw, DrawAnalysis
from app.services.combination_service import CombinationService

class AnalysisService:
    
    @staticmethod
    def analyze_draw(db: Session, draw_id: int, selected_universe: str = None) -> Dict[str, Any]:
        """Analyse un tirage spécifique"""
        draw = db.query(Draw).filter(Draw.id == draw_id).first()
        if not draw:
            return {"error": "Tirage non trouvé"}
        
        # Générer les combinaisons
        combinations = CombinationService.generate_combinations(draw.winning_numbers)
        
        # Classifier par univers
        classified = CombinationService.classify_combinations_by_universe(db, combinations)
        
        # Si un univers spécifique est sélectionné
        if selected_universe and selected_universe in classified:
            return {
                "draw_info": {
                    "lottery_name": draw.lottery_name,
                    "draw_date": draw.draw_date.strftime("%d/%m/%Y"),
                    "winning_numbers": draw.winning_numbers
                },
                "universe": selected_universe,
                "combinations": classified[selected_universe],
                "total_combinations": len(classified[selected_universe])
            }
        
        # Retourner tous les univers
        return {
            "draw_info": {
                "lottery_name": draw.lottery_name,
                "draw_date": draw.draw_date.strftime("%d/%m/%Y"),
                "winning_numbers": draw.winning_numbers
            },
            "universes": classified,
            "total_combinations": len(combinations)
        }
    
    @staticmethod
    def generate_statistical_journal(
        db: Session, 
        universe: str = "mundo", 
        start_date: str = None, 
        end_date: str = None,
        period_start: int = None,
        period_end: int = None,
        periodicity: int = 1,
        session_id: int = None
    ) -> Dict[str, Any]:
        """Génère le journal statistique avec périodicité et filtres avancés"""
        from datetime import datetime
        
        # Construction de la requête de base - prioriser les sessions cycliques
        if session_id:
            # Utiliser les données de session cyclique
            from app.models.session import SessionDraw
            session_draws = db.query(SessionDraw).filter(
                SessionDraw.session_id == session_id,
                SessionDraw.is_completed == True
            ).order_by(SessionDraw.draw_date.desc()).all()
            
            # Convertir en format Draw pour compatibilité
            draws = []
            for session_draw in session_draws:
                # Créer un objet Draw-like pour la compatibilité
                draw_obj = type('Draw', (), {
                    'id': session_draw.id,
                    'lottery_name': session_draw.lottery_name,
                    'draw_date': session_draw.draw_date,
                    'winning_numbers': session_draw.winning_numbers,
                    'cycle_position': session_draw.cycle_position,
                    'draw_number': session_draw.draw_number
                })()
                draws.append(draw_obj)
        else:
            # Utiliser l'ancien système
            query = db.query(Draw).order_by(Draw.draw_date.desc())
            
            # Filtrage par dates si spécifié
            if start_date and end_date:
                start_dt = datetime.strptime(start_date, "%d/%m/%Y")
                end_dt = datetime.strptime(end_date, "%d/%m/%Y")
                query = query.filter(Draw.draw_date >= start_dt, Draw.draw_date <= end_dt)
            
            draws = query.all()
        
        # Filtrage par périodes si spécifié
        if period_start is not None and period_end is not None:
            total_draws = len(draws)
            start_idx = max(0, total_draws - period_end * periodicity)
            end_idx = max(0, total_draws - (period_start - 1) * periodicity)
            draws = draws[start_idx:end_idx]
        
        # Groupement par périodes avec gestion complète des sessions cycliques
        journal_entries = []
        
        if session_id:
            # Pour les sessions cycliques, traiter TOUTES les dates prévues
            from app.models.session import WorkSession, SessionDraw
            session = db.query(WorkSession).filter(WorkSession.id == session_id).first()
            
            if session:
                # Récupérer TOUS les tirages prévus (complétés ou non)
                all_session_draws = db.query(SessionDraw).filter(
                    SessionDraw.session_id == session_id
                ).order_by(SessionDraw.draw_date.desc()).all()
                
                for i, session_draw in enumerate(all_session_draws):
                    period_number = ((session_draw.draw_number - 1) // periodicity) + 1
                    cycle_info = f"Cycle {session_draw.cycle_position + 1}"
                    
                    if session_draw.is_completed and session_draw.winning_numbers:
                        # Tirage complété - traiter normalement
                        combinations = CombinationService.generate_combinations(session_draw.winning_numbers)
                        classified = CombinationService.classify_combinations_by_universe(db, combinations)
                        
                        if universe and universe in classified and len(classified[universe]) > 0:
                            # Il y a des combinaisons dans cet univers
                            for combo in classified[universe]:
                                entry = {
                                    "draw_id": session_draw.id,
                                    "period": period_number,
                                    "cycle_info": cycle_info,
                                    "date": session_draw.draw_date.strftime("%d/%m/%Y"),
                                    "lottery_name": session_draw.lottery_name,
                                    "winning_numbers": session_draw.winning_numbers,
                                    "combination": combo["combination"],
                                    "denomination": combo.get("denomination"),
                                    "alpha_ranking": combo.get("alpha_ranking"),
                                    "granque": combo.get("granque"),
                                    "petique": combo.get("petique"),
                                    "ligne": combo.get("ligne"),
                                    "colonne": combo.get("colonne"),
                                    "parite": combo.get("parite"),
                                    "unidos": combo.get("unidos"),
                                    "chip": combo.get("chip"),
                                    "univers": combo["univers"],
                                    "forme": combo["forme"],
                                    "engine": combo["engine"],
                                    "beastie": combo["beastie"],
                                    "tome": combo["tome"],
                                    "is_period_start": i % periodicity == 0,
                                    "is_cycle_data": True,
                                    "status": "completed"
                                }
                                journal_entries.append(entry)
                        else:
                            # Tirage complété mais pas de combinaison dans cet univers
                            entry = {
                                "draw_id": session_draw.id,
                                "period": period_number,
                                "cycle_info": cycle_info,
                                "date": session_draw.draw_date.strftime("%d/%m/%Y"),
                                "lottery_name": session_draw.lottery_name,
                                "winning_numbers": session_draw.winning_numbers,
                                "combination": "N-H",
                                "denomination": "N-H",
                                "alpha_ranking": "N-H",
                                "granque": "N-H",
                                "petique": "N-H",
                                "ligne": "N-H",
                                "colonne": "N-H",
                                "parite": "N-H",
                                "unidos": "N-H",
                                "chip": "N-H",
                                "univers": universe,
                                "forme": "N-H",
                                "engine": "N-H",
                                "beastie": "N-H",
                                "tome": "N-H",
                                "is_period_start": i % periodicity == 0,
                                "is_cycle_data": True,
                                "status": "no_hold"
                            }
                            journal_entries.append(entry)
                    else:
                        # Tirage non complété (pas encore eu lieu ou jour férié)
                        entry = {
                            "draw_id": session_draw.id,
                            "period": period_number,
                            "cycle_info": cycle_info,
                            "date": session_draw.draw_date.strftime("%d/%m/%Y"),
                            "lottery_name": session_draw.lottery_name,
                            "winning_numbers": [],
                            "combination": "N-D",
                            "denomination": "N-D",
                            "alpha_ranking": "N-D",
                            "granque": "N-D",
                            "petique": "N-D",
                            "ligne": "N-D",
                            "colonne": "N-D",
                            "parite": "N-D",
                            "unidos": "N-D",
                            "chip": "N-D",
                            "univers": universe,
                            "forme": "N-D",
                            "engine": "N-D",
                            "beastie": "N-D",
                            "tome": "N-D",
                            "is_period_start": i % periodicity == 0,
                            "is_cycle_data": True,
                            "status": "no_draw"
                        }
                        journal_entries.append(entry)
        else:
            # Pour les données classiques (ancien système)
            for i, draw in enumerate(draws):
                period_number = (i // periodicity) + 1
                
                combinations = CombinationService.generate_combinations(draw.winning_numbers)
                classified = CombinationService.classify_combinations_by_universe(db, combinations)
                
                # Filtrer par univers (par défaut mundo)
                if universe and universe in classified:
                    for combo in classified[universe]:
                        entry = {
                            "draw_id": draw.id,
                            "period": period_number,
                            "cycle_info": None,
                            "date": draw.draw_date.strftime("%d/%m/%Y"),
                            "lottery_name": draw.lottery_name,
                            "winning_numbers": draw.winning_numbers,
                            "combination": combo["combination"],
                            "denomination": combo.get("denomination"),
                            "alpha_ranking": combo.get("alpha_ranking"),
                            "granque": combo.get("granque"),
                            "petique": combo.get("petique"),
                            "ligne": combo.get("ligne"),
                            "colonne": combo.get("colonne"),
                            "parite": combo.get("parite"),
                            "unidos": combo.get("unidos"),
                            "chip": combo.get("chip"),
                            "univers": combo["univers"],
                            "forme": combo["forme"],
                            "engine": combo["engine"],
                            "beastie": combo["beastie"],
                            "tome": combo["tome"],
                            "is_period_start": i % periodicity == 0,
                            "is_cycle_data": False,
                            "status": "completed"
                        }
                        journal_entries.append(entry)
        
        # Calcul des fréquences par période
        period_frequencies = AnalysisService.calculate_period_frequencies(journal_entries, periodicity)
        
        return {
            "journal": journal_entries,
            "period_frequencies": period_frequencies,
            "total_periods": len(set(entry["period"] for entry in journal_entries)),
            "periodicity": periodicity,
            "universe_filter": universe
        }
    
    @staticmethod
    def calculate_period_frequencies(journal_entries: List[Dict], periodicity: int) -> Dict[str, Dict]:
        """Calcule les fréquences d'attributs par période"""
        from collections import defaultdict, Counter
        
        period_data = defaultdict(lambda: {
            "forme": Counter(),
            "engine": Counter(),
            "beastie": Counter(),
            "tome": Counter()
        })
        
        # Grouper par période
        for entry in journal_entries:
            period = entry["period"]
            for attr in ["forme", "engine", "beastie", "tome"]:
                if entry.get(attr):
                    period_data[period][attr][entry[attr]] += 1
        
        # Calculer les pourcentages
        frequencies = {}
        for period, data in period_data.items():
            frequencies[period] = {}
            total_entries = len([e for e in journal_entries if e["period"] == period])
            
            for attr, counter in data.items():
                frequencies[period][attr] = {}
                for value, count in counter.items():
                    frequencies[period][attr][value] = {
                        "count": count,
                        "percentage": round((count / total_entries) * 100, 1) if total_entries > 0 else 0
                    }
        
        return frequencies
    
    @staticmethod
    def calculate_frequencies(journal: List[Dict]) -> Dict[str, Dict]:
        """Calcule les fréquences d'apparition des attributs"""
        frequencies = {
            "univers": Counter(),
            "forme": Counter(),
            "engine": Counter(),
            "beastie": Counter(),
            "tome": Counter()
        }
        
        for entry in journal:
            for attr in frequencies.keys():
                if entry.get(attr):
                    frequencies[attr][entry[attr]] += 1
        
        # Convertir en pourcentages
        total_entries = len(journal)
        for attr in frequencies:
            for key in frequencies[attr]:
                count = frequencies[attr][key]
                frequencies[attr][key] = {
                    "count": count,
                    "percentage": round((count / total_entries) * 100, 2)
                }
        
        return dict(frequencies)