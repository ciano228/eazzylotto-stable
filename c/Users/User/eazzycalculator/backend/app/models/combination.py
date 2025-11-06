from sqlalchemy import Column, Integer, String
from app.database.connection import Base

class Combination(Base):
    __tablename__ = "combinations"
    
    # Clés primaires et identifiants
    combination_id = Column(Integer, primary_key=True, index=True)
    denomination_row_number = Column(Integer)
    row_number = Column(Integer)
    
    # Numéros de base
    num1 = Column(Integer)
    num2 = Column(Integer)
    combination = Column(String)
    
    # IDs de référence
    parite_id = Column(Integer)
    unidos_id = Column(Integer)
    forme_id = Column(Integer)
    univers_id = Column(Integer)
    denomination_id = Column(Integer)
    chip_id = Column(Integer)
    
    # Positions et cellules
    cell_num1 = Column(Integer)
    cell_num2 = Column(Integer)
    col_num1 = Column(String)
    col_num2 = Column(String)
    
    # Attributs principaux pour l'analyse
    univers = Column(String)  # mundo, fruity, trigga, roaster, sunshine
    forme = Column(String)
    engine = Column(String)
    beastie = Column(String)
    tome = Column(String)
    
    # Autres attributs
    granque_name = Column(String)
    denomination = Column(String)
    alpha_ranking = Column(String)
    base_name = Column(String)
    quartier = Column(String)
    region = Column(String)
    gentillee = Column(String)
    chip = Column(String)
    ligne = Column(String)
    colonne = Column(String)
    petique = Column(String)
    
    # Positions détaillées
    position_num1 = Column(String)
    position_num2 = Column(String)
    lot_num1 = Column(String)
    lot_num2 = Column(String)
    ash_num1 = Column(String)
    ash_num2 = Column(String)
    room_num1 = Column(String)
    room_num2 = Column(String)