"""
Validation script to extract and verify real Katula data from the database.
This script queries each universe separately to get the actual data structure.
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from typing import Dict, List, Any
from datetime import datetime

class KatulaValidator:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'database': 'katooling_main_system',
            'user': 'postgres',
            'password': 'Katulaa_33',
            'port': 5432
        }
        self.conn = None
        self.cur = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
            print("✅ Connected to database successfully")
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            raise
            
    def get_universes(self) -> List[str]:
        """Get list of all actual universes in the database"""
        self.cur.execute("""
            SELECT DISTINCT univers 
            FROM table_de_katula 
            WHERE univers IS NOT NULL 
            ORDER BY univers;
        """)
        return [row['univers'] for row in self.cur.fetchall()]
        
    def analyze_universe(self, universe: str) -> Dict[str, Any]:
        """Analyze complete structure of a specific universe"""
        print(f"\n📊 Analyzing universe: {universe.upper()}")
        
        # Get all formes (shapes) for this universe
        self.cur.execute("""
            SELECT DISTINCT forme 
            FROM table_de_katula 
            WHERE univers = %s AND forme IS NOT NULL 
            ORDER BY forme;
        """, (universe,))
        formes = [row['forme'] for row in self.cur.fetchall()]
        print(f"Found {len(formes)} unique formes: {formes}")
        
        # Get all petiques
        self.cur.execute("""
            SELECT DISTINCT petique 
            FROM table_de_katula 
            WHERE univers = %s AND petique IS NOT NULL 
            ORDER BY petique;
        """, (universe,))
        petiques = [row['petique'] for row in self.cur.fetchall()]
        print(f"Found {len(petiques)} unique petiques: {petiques}")
        
        # Get all unique denominations
        self.cur.execute("""
            SELECT DISTINCT denomination 
            FROM table_de_katula 
            WHERE univers = %s AND denomination IS NOT NULL 
            ORDER BY denomination;
        """, (universe,))
        denominations = [row['denomination'] for row in self.cur.fetchall()]
        print(f"Found {len(denominations)} unique denominations")
        
        # Get chip statistics
        self.cur.execute("""
            SELECT COUNT(DISTINCT chip) as chip_count 
            FROM table_de_katula 
            WHERE univers = %s;
        """, (universe,))
        chip_count = self.cur.fetchone()['chip_count']
        print(f"Total unique chips: {chip_count}")
        
        # Get detailed chip structures
        self.cur.execute("""
            WITH chip_stats AS (
                WITH ordered_formes AS (
                    SELECT DISTINCT forme,
                        CASE forme 
                            WHEN 'carre' THEN 1
                            WHEN 'triangle' THEN 2
                            WHEN 'cercle' THEN 3
                            WHEN 'rectangle' THEN 4
                            WHEN 'carre-triangle' THEN 5
                            WHEN 'carre-cercle' THEN 6
                            WHEN 'carre-rectangle' THEN 7
                            WHEN 'triangle-carre' THEN 8
                            WHEN 'triangle-cercle' THEN 9
                            WHEN 'triangle-rectangle' THEN 10
                            WHEN 'cercle-carre' THEN 11
                            WHEN 'cercle-triangle' THEN 12
                            WHEN 'cercle-rectangle' THEN 13
                            WHEN 'rectangle-carre' THEN 14
                            WHEN 'rectangle-triangle' THEN 15
                            WHEN 'rectangle-cercle' THEN 16
                            ELSE 99
                        END as forme_order
                    FROM table_de_katula 
                    WHERE univers = %(universe)s
                )
                SELECT 
                    chip,
                    COUNT(*) as compartment_count,
                    array_agg(DISTINCT t.forme ORDER BY of.forme_order) as formes,
                    array_agg(DISTINCT petique ORDER BY petique) as petiques,
                    array_agg(DISTINCT ligne ORDER BY ligne) as lignes,
                    array_agg(DISTINCT colonne ORDER BY colonne) as colonnes
                FROM table_de_katula t
                JOIN ordered_formes of ON t.forme = of.forme
                WHERE t.univers = %(universe)s
                GROUP BY chip
                ORDER BY CASE 
                    WHEN chip ~ '^[0-9]+$' THEN (chip::integer)
                    ELSE 999999  -- Put non-numeric chips at the end
                END
            )
            SELECT * FROM chip_stats;
        """, (universe,))
        
        chips = {}
        for row in self.cur.fetchall():
            chip_id = row['chip']
            chips[chip_id] = {
                'compartments': row['compartment_count'],
                'formes': row['formes'],
                'petiques': row['petiques'],
                'lignes': row['lignes'],
                'colonnes': row['colonnes']
            }
            
            # Get detailed compartment data for this chip
            self.cur.execute("""
                SELECT 
                    ligne, colonne, forme, petique, denomination
                FROM table_de_katula
                WHERE univers = %s AND chip = %s
                ORDER BY ligne, colonne;
            """, (universe, chip_id))
            
            chips[chip_id]['compartments_data'] = [dict(row) for row in self.cur.fetchall()]
            
        return {
            'universe': universe,
            'total_chips': chip_count,
            'available_formes': formes,
            'available_petiques': petiques,
            'denomination_count': len(denominations),
            'chips': chips
        }
        
    def validate_all_universes(self):
        """Validate and extract data for all universes"""
        try:
            self.connect()
            universes = self.get_universes()
            print(f"Found {len(universes)} universes: {universes}")
            
            validation_data = {}
            for universe in universes:
                validation_data[universe] = self.analyze_universe(universe)
                
            # Save validation results
            output_file = 'katula_validated_structure.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'validation_date': datetime.now().isoformat(),
                    'universes': validation_data
                }, f, indent=2, ensure_ascii=False)
                
            print(f"\n✅ Validation complete. Results saved to {output_file}")
            
        except Exception as e:
            print(f"❌ Validation error: {e}")
            raise
        finally:
            if self.cur:
                self.cur.close()
            if self.conn:
                self.conn.close()
            
if __name__ == "__main__":
    validator = KatulaValidator()
    validator.validate_all_universes()