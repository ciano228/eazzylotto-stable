"""
Katooling Orchestration Service
Unifie l'analyse temporelle et le split pour le suivi des attributs.
"""

from typing import Dict, Any, List
from .temporal_analysis_service import TemporalAnalysisService
from split_strategy_service import SplitStrategyService
import os

class KatoolingService:
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.split_service = SplitStrategyService(db_config)
        self.temporal_service = TemporalAnalysisService()

    def get_tracking_opportunities(self, db, universe: str, tables_config: List[Dict]):
        """
        Identifie les meilleures opportunités de tracking basées sur l'analyse temporelle.
        """
        analysis = self.temporal_service.analyze_temporal_patterns(
            db, universe, tables_config
        )
        # On pourrait ici filtrer les patterns par confiance ou type
        return analysis

    def prepare_split_refinement(self, universe: str, session_id: int, 
                               attribute_type: str, attribute_value: str, 
                               lookback_days: int = 180):
        """
        Prépare le split pour un attribut choisi afin de raffiner l'investissement.
        """
        return self.split_service.perform_split(
            universe, session_id, attribute_type, attribute_value, lookback_days
        )

# Factory function for FastAPI
def get_katooling_service():
    db_config = {
        'dbname': os.getenv('DB_NAME', 'katooling_main_system'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'Katulaa_33'),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432')
    }
    return KatoolingService(db_config)
