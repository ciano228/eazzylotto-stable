from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Combination(Base):
    __tablename__ = "combinations"
    
    id = Column(Integer, primary_key=True, index=True)
    chip = Column(Integer, nullable=False, index=True)
    colonne = Column(String(10), index=True)
    ligne = Column(String(10), index=True)
    forme = Column(String(50), index=True)
    denomination = Column(String(100))
    petique = Column(String(10), index=True)
    granque_name = Column(String(10), index=True)
    tome = Column(String(10), index=True)
    univers = Column(String(50), index=True)

    class Config:
        orm_mode = True
