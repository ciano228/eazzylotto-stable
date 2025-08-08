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
        SessionService.create_session_draws_with_schedule(db, session.id, total_draws, lottery_schedule, start_date)
        
        return session
    
    @staticmethod
    def create_session_draws_with_schedule(
        db: Session, 
        session_id: int, 
        total_draws: int, 
        lottery_schedule: List[Dict], 
        start_date: datetime
    ):
        """Créer les tirages avec planning cyclique"""
        from datetime import timedelta
        
        draws = []
        cycle_length = len(lottery_schedule)
        
        for i in range(total_draws):
            cycle_position = i % cycle_length
            lottery_info = lottery_schedule[cycle_position]
            
            # Calculer la date du tirage
            days_from_start = (i // cycle_length) * 7 + lottery_info['day_offset']
            draw_date = start_date + timedelta(days=days_from_start)
            
            draw = SessionDraw(
                session_id=session_id,
                draw_number=i + 1,
                cycle_position=cycle_position,
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
        
        return {
            "session_id": session.id,
            "session_name": session.name,
            "current_draw": session.current_draw,
            "total_draws": session.total_draws,
            "completed_draws": completed_draws,
            "progress_percentage": round((completed_draws / session.total_draws) * 100, 1),
            "numbers_per_draw": session.numbers_per_draw,
            "number_range": f"{session.number_range_min}-{session.number_range_max}"
        }