from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Combination(Base):
    __tablename__ = "combinations"

    combination_id = Column(Integer, primary_key=True, index=True)
    chip = Column(Integer, index=True)
    chip_id = Column(Integer)
    colonne = Column(String(10), index=True)
    ligne = Column(String(10), index=True)
    forme = Column(String(50), index=True)
    denomination = Column(String(100), index=True)
    petique = Column(String(10), index=True)
    granque_name = Column(String(10), index=True)
    tome = Column(String(10), index=True)
    univers = Column(String(50), index=True)
    num1 = Column(Integer)
    num2 = Column(Integer)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    subscription_type = Column(String(50), default="free")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime)
