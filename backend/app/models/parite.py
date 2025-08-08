from sqlalchemy import Column, Integer, String
from app.database.connection import Base

class Parite(Base):
    __tablename__ = "parite"
    
    parite_id = Column(Integer, primary_key=True, index=True)
    parite = Column(String)
    description = Column(String)