#!/usr/bin/env python3
"""
Script pour créer les tables d'analyse statistique
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import get_db
from sqlalchemy import text

def create_analytics_tables():
    """Créer les tables pour l'analyse statistique"""
    
    try:
        db = next(get_db())
        
        print("=== CRÉATION DES TABLES D'ANALYSE ===")
        
        # Table pour l'historique des écarts
        print("Création de la table attribute_gaps...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS attribute_gaps (
                id SERIAL PRIMARY KEY,
                attribute_type VARCHAR(50) NOT NULL,
                attribute_value VARCHAR(100) NOT NULL,
                universe VARCHAR(20) NOT NULL,
                last_appearance_draw_id INTEGER,
                current_gap INTEGER DEFAULT 0,
                average_gap DECIMAL(10,2) DEFAULT 0,
                max_gap INTEGER DEFAULT 0,
                min_gap INTEGER DEFAULT 0,
                total_appearances INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(attribute_type, attribute_value, universe)
            )
        """))
        
        # Table pour les fréquences temporelles
        print("Création de la table frequency_analysis...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS frequency_analysis (
                id SERIAL PRIMARY KEY,
                attribute_type VARCHAR(50) NOT NULL,
                attribute_value VARCHAR(100) NOT NULL,
                universe VARCHAR(20) NOT NULL,
                period_5 INTEGER DEFAULT 0,
                period_10 INTEGER DEFAULT 0,
                period_20 INTEGER DEFAULT 0,
                period_50 INTEGER DEFAULT 0,
                trend VARCHAR(20) DEFAULT 'stable',
                heat_score DECIMAL(5,2) DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(attribute_type, attribute_value, universe)
            )
        """))
        
        # Table pour les associations/corrélations
        print("Création de la table attribute_correlations...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS attribute_correlations (
                id SERIAL PRIMARY KEY,
                attribute1_type VARCHAR(50) NOT NULL,
                attribute1_value VARCHAR(100) NOT NULL,
                attribute2_type VARCHAR(50) NOT NULL,
                attribute2_value VARCHAR(100) NOT NULL,
                universe VARCHAR(20) NOT NULL,
                co_occurrence_count INTEGER DEFAULT 0,
                correlation_strength DECIMAL(5,2) DEFAULT 0,
                confidence_level DECIMAL(5,2) DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(attribute1_type, attribute1_value, attribute2_type, attribute2_value, universe)
            )
        """))
        
        # Index pour optimiser les performances
        print("Création des index...")
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_gaps_universe ON attribute_gaps(universe)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_gaps_type ON attribute_gaps(attribute_type)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_freq_universe ON frequency_analysis(universe)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_freq_heat ON frequency_analysis(heat_score DESC)"))
        
        db.commit()
        print("✅ Tables d'analyse créées avec succès!")
        
        # Vérifier les tables créées
        print("\n=== VÉRIFICATION DES TABLES ===")
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('attribute_gaps', 'frequency_analysis', 'attribute_correlations')
            ORDER BY table_name
        """))
        
        tables = [row[0] for row in result]
        print(f"Tables créées: {tables}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    create_analytics_tables()