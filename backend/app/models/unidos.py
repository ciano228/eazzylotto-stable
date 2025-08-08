from sqlalchemy import Column, Integer, String
from app.database.connection import Base

class Unidos(Base):
    __tablename__ = "unidos"
    
    unidos_id = Column(Integer, primary_key=True, index=True)
    unidos = Column(String)
    description = Column(String)