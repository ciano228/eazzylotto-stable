from sqlalchemy import Column, Integer, String
from app.database.connection import Base

class Chip(Base):
    __tablename__ = "chips"
    
    chip_id = Column(Integer, primary_key=True)
    chip_name = Column(String)
    description = Column(String)
    univers = Column(String)
    ligne = Column(String)
    colonne = Column(String)
    denomination = Column(String)
    univers_id = Column(Integer)
    petique = Column(String)