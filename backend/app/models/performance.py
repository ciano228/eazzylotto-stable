from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.database.connection import Base

class PredictionRecord(Base):
    __tablename__ = "prediction_records"
    
    id = Column(Integer, primary_key=True, index=True)
    universe = Column(String, nullable=False, index=True)
    
    # Context of the prediction
    trigger_numbers = Column(JSON, nullable=False) # The numbers used to generate prediction
    prediction_date = Column(DateTime, server_default=func.now())
    
    # The actual predictions made at T time
    predicted_numbers = Column(JSON) # e.g. [{"number": 24, "frequency": 45.5}, ...]
    predicted_pairs = Column(JSON)   # e.g. ["24-67", "12-89"]
    predicted_attributes = Column(JSON) # e.g. {"Engine": "E5", "Tome": "T8"}
    
    # Result tracking
    actual_numbers = Column(JSON)    # Filled after draw
    draw_date = Column(DateTime)     # Date of the actual draw that followed
    is_evaluated = Column(Boolean, default=False)
    
    # Performance Scores (0.0 to 1.0)
    hit_score_numbers = Column(Float, default=0.0)
    hit_score_attributes = Column(Float, default=0.0)
    
    # Metadata
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
