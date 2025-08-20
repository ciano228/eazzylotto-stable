from sqlalchemy import Column, Integer, String, Boolean, DateTime, DECIMAL, ARRAY, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

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

class LotteryDraw(Base):
    __tablename__ = "lottery_draws"
    
    id = Column(Integer, primary_key=True, index=True)
    draw_date = Column(DateTime, nullable=False)
    numbers = Column(ARRAY(Integer), nullable=False)
    bonus_number = Column(Integer)
    lottery_type = Column(String(50), default="loto")
    jackpot_amount = Column(DECIMAL(15,2))
    winners_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    session_name = Column(String(255), nullable=False)
    universe_type = Column(String(50), nullable=False)
    period_start = Column(Integer, nullable=False)
    period_end = Column(Integer, nullable=False)
    analyzed_combinations = Column(JSON)
    predictions = Column(JSON)
    confidence_score = Column(DECIMAL(5,2))
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())