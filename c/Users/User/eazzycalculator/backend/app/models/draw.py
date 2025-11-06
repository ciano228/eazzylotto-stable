from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.database.connection import Base

class Draw(Base):
    __tablename__ = "draws"
    
    id = Column(Integer, primary_key=True, index=True)
    lottery_name = Column(String, nullable=False)
    draw_date = Column(DateTime, nullable=False)
    winning_numbers = Column(JSON)  # Liste des numéros gagnants
    number_range_min = Column(Integer, default=1)  # Range minimum (ex: 1)
    number_range_max = Column(Integer, default=90)  # Range maximum (ex: 90)
    created_at = Column(DateTime, server_default=func.now())
    
class DrawAnalysis(Base):
    __tablename__ = "draw_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    draw_id = Column(Integer, nullable=False)
    universe = Column(String)  # Univers analysé
    total_combinations = Column(Integer)  # Nombre total de combinaisons
    analysis_results = Column(JSON)  # Résultats détaillés de l'analyse
    created_at = Column(DateTime, server_default=func.now())