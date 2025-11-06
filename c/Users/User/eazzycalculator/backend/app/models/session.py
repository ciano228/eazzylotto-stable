from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base

class WorkSession(Base):
    __tablename__ = "work_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Nom de la session (ex: "Session Janvier 2025")
    description = Column(String)  # Description optionnelle
    lottery_type = Column(String, nullable=False)  # Type de loto (ex: "Loto Français")
    numbers_per_draw = Column(Integer, nullable=False)  # Nombre de numéros par tirage
    number_range_min = Column(Integer, default=1)  # Plage minimum
    number_range_max = Column(Integer, default=90)  # Plage maximum
    total_draws = Column(Integer, nullable=False)  # Nombre total de tirages dans la session
    current_draw = Column(Integer, default=1)  # Tirage actuel
    cycle_length = Column(Integer, default=7)  # Longueur du cycle (ex: 7 jours)
    lottery_schedule = Column(JSON)  # Planning des lotos dans le cycle
    start_date = Column(DateTime, nullable=False)  # Date de début de la session
    is_active = Column(Boolean, default=True)  # Session active ou non
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relation avec les tirages
    draws = relationship("SessionDraw", back_populates="session")

class SessionDraw(Base):
    __tablename__ = "session_draws"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("work_sessions.id"), nullable=False)
    draw_number = Column(Integer, nullable=False)  # Numéro du tirage dans la session (1, 2, 3...)
    cycle_position = Column(Integer, nullable=False)  # Position dans le cycle (0-6 pour une semaine)
    lottery_name = Column(String, nullable=False)  # Nom spécifique du tirage
    draw_date = Column(DateTime, nullable=False)
    winning_numbers = Column(JSON)  # Liste des numéros gagnants
    is_completed = Column(Boolean, default=False)  # Tirage complété ou non
    is_no_draw = Column(Boolean, default=False)  # Indique si c'est un No Draw
    created_at = Column(DateTime, server_default=func.now())
    
    # Relations
    session = relationship("WorkSession", back_populates="draws")