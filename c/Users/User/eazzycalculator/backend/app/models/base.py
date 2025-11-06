"""
Models de l'application
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base

class KatulaTable(Base):
    """Table de Katula - représentation géométrique des combinaisons"""
    __tablename__ = "katula_tables"

    id = Column(Integer, primary_key=True, index=True)
    universe = Column(String, index=True)
    structure = Column(String)  # JSON string de la structure
    created_at = Column(DateTime)
