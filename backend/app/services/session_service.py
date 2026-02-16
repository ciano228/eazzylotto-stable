








from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.session import WorkSession, SessionDraw

class SessionService:
    
    @staticmethod
    def create_work_session(
        db: Session,
        name: str,
        lottery_type: str,
        numbers_per_draw: int,
        total_draws: int,
        lottery_schedule: List[Dict],
        start_date: datetime,
        number_range_min: int = 1,
        number_range_max: int = 90,
        description: str = None,
        cycle_length: int = 7
    ) -> WorkSession:
        """Créer une nouvelle session de travail"""
        
        # Désactiver les autres sessions actives
        db.query(WorkSession).filter(WorkSession.is_active == True).update({"is_active": False})
        
        session = WorkSession(
            name=name,
            description=description,
            lottery_type=lottery_type,
            numbers_per_draw=numbers_per_draw,
            number_range_min=number_range_min,
            number_range_max=number_range_max,
            total_draws=total_draws,
            current_draw=1,
            cycle_length=cycle_length,  # Utiliser le paramètre fourni
            lottery_schedule=lottery_schedule,
            start_date=start_date,
            is_active=True
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # Créer les tirages vides pour la session avec le planning cyclique
        SessionService.create_session_draws_with_schedule(db, session.id, total_draws, lottery_schedule, start_date, cycle_length)
        
        return session
    
    @staticmethod
    def create_session_draws_with_schedule(
        db: Session, 
        session_id: int, 
        total_draws: int, 
        lottery_schedule: List[Dict], 
        start_date: datetime,
        cycle_length: int = 7
    ):
        """Créer les tirages avec planning cyclique - Ordonnanceur Calendaire"""
        from datetime import timedelta
        
        # 1. Trier le planning par jour de la semaine (6=Dimanche devient -1 pour être premier)
        def sort_key(item):
            offset = item['day_offset']
            return -1 if offset == 6 else offset
            
        sorted_schedule = sorted(lottery_schedule, key=sort_key)
        schedule_count = len(sorted_schedule)
        
        # 2. Ancrer la start_date sur le début de sa semaine (Dimanche précédent ou actuel)
        # weekday() en Python: 0=Lun, 6=Dim. Si 6, offset=0. Si 0, offset=1.
        # Pour recaler sur le Dimanche : days_to_subtract = (start_date.weekday() + 1) % 7
        # anchor_date = start_date - timedelta(days=days_to_subtract)
        
        draws = []
        for i in range(total_draws):
            idx0 = i
            period_index = idx0 // cycle_length
            period_position = idx0 % cycle_length
            
            # Index dans le planning (Cycle Snapping)
            schedule_index = period_position % schedule_count
            lottery_info = sorted_schedule[schedule_index]
            
            # Calculer la date absolue basée sur la semaine de début
            weeks_per_period = cycle_length // 7
            weeks_internal = period_position // schedule_count
            
            total_weeks = (period_index * weeks_per_period) + weeks_internal
            
            # Utiliser la logique de jour de la semaine pour caler sur le bon jour réel
            # On veut que si start_date est un Dimanche et loto est Dimanche, offset est 0.
            # jours_offset_reel: distance entre le loto et le début de sa propre semaine
            # lottery_info['day_offset'] est 0=Lun ... 6=Dim.
            # On le transforme pour que 6(Dim)=0, 0(Lun)=1, 1(Mar)=2...
            day_mapped = (lottery_info['day_offset'] + 1) % 7
            
            draw_date = (start_date - timedelta(days=(start_date.weekday() + 1) % 7)) + \
                        timedelta(weeks=total_weeks, days=day_mapped)
            
            # Sécurité: Si la date calculée est avant la start_date réelle de la session au tirage #1,
            # on la décale d'une semaine (pour respecter l'intention de l'utilisateur de commencer À PARTIR de start_date)
            # if i == 0 and draw_date < start_date:
            #    # Cependant, si l'utilisateur dit Commencer le 08-06 (Dimanche) et le planning commence par Dimanche,
            #    # draw_date sera 08-06. C'est parfait.
            
            draw = SessionDraw(
                session_id=session_id,
                draw_number=idx0 + 1,
                cycle_position=schedule_index,
                lottery_name=lottery_info['name'],
                draw_date=draw_date,
                winning_numbers=[],
                is_completed=False
            )
            draws.append(draw)
        
        db.add_all(draws)
        db.commit()
    
    @staticmethod
    def create_session_draws(db: Session, session_id: int, total_draws: int, lottery_type: str):
        """Créer les tirages vides pour une session (méthode legacy)"""
        draws = []
        for i in range(1, total_draws + 1):
            draw = SessionDraw(
                session_id=session_id,
                draw_number=i,
                cycle_position=0,  # Position par défaut
                lottery_name=f"{lottery_type} - Tirage {i}",
                draw_date=datetime.now(),  # Date par défaut, sera mise à jour lors de la saisie
                winning_numbers=[],
                is_completed=False
            )
            draws.append(draw)
        
        db.add_all(draws)
        db.commit()
    
    @staticmethod
    def get_active_session(db: Session) -> Optional[WorkSession]:
        """Récupérer la session active"""
        return db.query(WorkSession).filter(WorkSession.is_active == True).first()
    
    @staticmethod
    def get_all_sessions(db: Session) -> List[WorkSession]:
        """Récupérer toutes les sessions disponibles"""
        return db.query(WorkSession).order_by(WorkSession.created_at.desc()).all()
    
    @staticmethod
    def activate_session(db: Session, session_id: int) -> WorkSession:
        """Activer une session spécifique"""
        # Désactiver toutes les sessions
        db.query(WorkSession).update({"is_active": False})
        
        # Activer la session demandée
        session = db.query(WorkSession).filter(WorkSession.id == session_id).first()
        if session:
            session.is_active = True
            db.commit()
            db.refresh(session)
        
        return session
    
    @staticmethod
    def get_session_draws(db: Session, session_id: int) -> List[SessionDraw]:
        """Récupérer tous les tirages d'une session"""
        return db.query(SessionDraw).filter(
            SessionDraw.session_id == session_id
        ).order_by(SessionDraw.draw_number).all()
    
    @staticmethod
    def get_current_draw(db: Session, session_id: int) -> Optional[SessionDraw]:
        """Récupérer le tirage actuel d'une session"""
        session = db.query(WorkSession).filter(WorkSession.id == session_id).first()
        if not session:
            return None
            
        return db.query(SessionDraw).filter(
            SessionDraw.session_id == session_id,
            SessionDraw.draw_number == session.current_draw
        ).first()
    
    @staticmethod
    def save_draw_numbers(
        db: Session, 
        session_id: int, 
        draw_number: int, 
        numbers: List[int],
        draw_date: datetime = None,
        is_no_draw: bool = False
    ) -> SessionDraw:
        """Sauvegarder les numéros d'un tirage, supporte le mode No Draw"""
        draw = db.query(SessionDraw).filter(
            SessionDraw.session_id == session_id,
            SessionDraw.draw_number == draw_number
        ).first()
        if not draw:
            raise ValueError(f"Tirage {draw_number} non trouvé dans la session {session_id}")
        draw.winning_numbers = numbers if numbers else []
        draw.is_completed = True
        draw.is_no_draw = is_no_draw
        if draw_date:
            draw.draw_date = draw_date
        db.commit()
        db.refresh(draw)
        # Mettre à jour le tirage actuel de la session
        session = db.query(WorkSession).filter(WorkSession.id == session_id).first()
        if session and draw_number == session.current_draw and draw_number < session.total_draws:
            session.current_draw = draw_number + 1
            db.commit()
        return draw
    
    @staticmethod
    def get_session_progress(db: Session, session_id: int) -> Dict[str, Any]:
        """Obtenir le progrès d'une session"""
        session = db.query(WorkSession).filter(WorkSession.id == session_id).first()
        if not session:
            return {}
        
        completed_draws = db.query(SessionDraw).filter(
            SessionDraw.session_id == session_id,
            SessionDraw.is_completed == True
        ).count()
        
        last_draw = db.query(SessionDraw).filter(
            SessionDraw.session_id == session_id
        ).order_by(SessionDraw.draw_date.desc()).first()
        
        return {
            "session_id": session.id,
            "session_name": session.name,
            "current_draw": session.current_draw,
            "total_draws": session.total_draws,
            "completed_draws": completed_draws,
            "progress_percentage": round((completed_draws / session.total_draws) * 100, 1),
            "numbers_per_draw": session.numbers_per_draw,
            "number_range": f"{session.number_range_min}-{session.number_range_max}",
            "start_date": session.start_date.isoformat() if session.start_date else None,
            "end_date": last_draw.draw_date.isoformat() if last_draw and last_draw.draw_date else None
        }
    
    @staticmethod
    def sync_session_schedule(db: Session, session_id: int) -> Dict[str, Any]:
        """Synchronize session draws with expected schedule, creating missing placeholders"""
        from datetime import timedelta
        
        session = db.query(WorkSession).filter(WorkSession.id == session_id).first()
        if not session:
            return {"error": "Session not found", "created": 0, "existing": 0}
        
        # Get existing draws mapping
        existing_draws = db.query(SessionDraw).filter(
            SessionDraw.session_id == session_id
        ).all()
        existing_draw_map = {draw.draw_number: draw for draw in existing_draws}
        
        # 1. Trier le planning par jour de la semaine (6=Dimanche devient -1 pour être premier)
        lottery_schedule = session.lottery_schedule or []
        if not lottery_schedule:
            return {"message": "No schedule defined", "created": 0, "existing": len(existing_draws)}

        def sort_key(item):
            offset = item.get('day_offset', 0)
            return -1 if offset == 6 else offset
            
        sorted_schedule = sorted(lottery_schedule, key=sort_key)
        schedule_count = len(sorted_schedule)
        
        cycle_length = session.cycle_length or 7
        total_draws = session.total_draws
        created_count = 0
        updated_count = 0
        
        new_draws = []
        # Date d'ancrage (Dimanche de la semaine de début)
        anchor_sun = session.start_date - timedelta(days=(session.start_date.weekday() + 1) % 7)

        for i in range(1, total_draws + 1):
            idx0 = i - 1
            # Position relative dans la période
            period_position = idx0 % cycle_length
            # Index dans le planning (Cycle Snapping)
            schedule_index = period_position % schedule_count
            lottery_info = sorted_schedule[schedule_index]
            
            # Calculer la date absolue
            weeks_per_period = cycle_length // 7
            weeks_internal = period_position // schedule_count
            total_weeks = ((idx0 // cycle_length) * weeks_per_period) + weeks_internal
            
            day_mapped = (lottery_info['day_offset'] + 1) % 7
            draw_date = anchor_sun + timedelta(weeks=total_weeks, days=day_mapped)
            
            if i in existing_draw_map:
                # RÉPARATION: Si placeholder non complété, on réaligne la date et le nom
                draw = existing_draw_map[i]
                if not draw.is_completed:
                    if draw.draw_date != draw_date or draw.lottery_name != lottery_info['name']:
                        draw.draw_date = draw_date
                        draw.lottery_name = lottery_info['name']
                        draw.cycle_position = schedule_index
                        updated_count += 1
                continue
            
            # Create placeholder draw
            new_draw = SessionDraw(
                session_id=session_id,
                draw_number=i,
                cycle_position=schedule_index,
                lottery_name=lottery_info['name'],
                draw_date=draw_date,
                winning_numbers=[],
                is_completed=False,
                is_no_draw=False
            )
            new_draws.append(new_draw)
            created_count += 1
            
        if new_draws:
            db.add_all(new_draws)
        
        db.commit()
        
        return {
            "message": f"Schedule synchronized for session '{session.name}'",
            "created": created_count,
            "updated": updated_count,
            "existing": len(existing_draws),
            "total": len(existing_draws) + created_count
        }
