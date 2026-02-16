from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Combination(Base):
    __tablename__ = "combinations"
    
    id = Column("combination_id", Integer, primary_key=True, index=True)
    chip = Column(String(10), nullable=False, index=True)
    colonne = Column(String(10), index=True)
    ligne = Column(String(10), index=True)
    forme = Column(String(50), index=True)
    denomination = Column(String(100))
    petique = Column(String(50), index=True)
    granque_name = Column(String(10), index=True)
    tome = Column(String(100), index=True)
    univers = Column(String(50), index=True)
    drawer = Column(Integer, index=True)
    drawer_name = Column(String(255), index=True)

    class Config:
        orm_mode = True
