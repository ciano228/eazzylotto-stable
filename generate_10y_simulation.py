"""
10-Year Simulation Generator
Génère une session de simulation avec 10 ans de tirages hebdomadaires
"""

import psycopg2
from datetime import datetime, timedelta
import random
import json

class SimulationGenerator:
    def __init__(self, db_config):
        self.db_config = db_config
        
    def get_universe_numbers(self, universe='mundo'):
        """Récupère tous les numéros valides pour l'univers"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT DISTINCT chip
            FROM combinations
            WHERE univers = %s
        """, (universe,))
        
        numbers = []
        for (chip,) in cur.fetchall():
            # Extract number from chip (chip1 -> 1)
            if chip and chip.startswith('chip'):
                try:
                    num = int(chip.replace('chip', ''))
                    numbers.append(num)
                except:
                    pass
        
        conn.close()
        return sorted(numbers)
    
    def generate_draw(self, numbers_pool, draw_size=5):
        """Génère un tirage aléatoire"""
        return sorted(random.sample(numbers_pool, draw_size))
    
    def create_simulation_session(self, universe='mundo', years=10, draws_per_week=1):
        """
        Crée une session de simulation
        
        Args:
            universe: L'univers (mundo, fruity, etc.)
            years: Nombre d'années à simuler
            draws_per_week: Nombre de tirages par semaine
        """
        print(f"\n{'='*60}")
        print(f"SIMULATION 10 ANS - Univers: {universe}")
        print(f"{'='*60}\n")
        
        # Calculer le nombre total de tirages
        weeks = years * 52
        total_draws = weeks * draws_per_week
        
        print(f"Configuration:")
        print(f"  - Années: {years}")
        print(f"  - Semaines: {weeks}")
        print(f"  - Tirages par semaine: {draws_per_week}")
        print(f"  - Total tirages: {total_draws}")
        
        # Récupérer les numéros disponibles
        numbers_pool = self.get_universe_numbers(universe)
        print(f"  - Numéros disponibles: {len(numbers_pool)} (1-{max(numbers_pool)})")
        
        # Créer la session
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()
        
        # Insérer la session
        print(f"\nCréation de la session...")
        cur.execute("""
            INSERT INTO work_sessions (
                name, description, lottery_type,
                numbers_per_draw, number_range_min, number_range_max,
                total_draws, cycle_length, start_date, is_active
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            f'Simulation_{years}Y_{universe}',
            f'Session de simulation sur {years} ans pour découverte de patterns',
            'simulated_weekly',
            5,  # 5 numéros par tirage
            min(numbers_pool),
            max(numbers_pool),
            total_draws,
            7,  # Cycle hebdomadaire
            datetime.now().date(),
            False  # Pas active
        ))
        
        session_id = cur.fetchone()[0]
        print(f"  Session créée: ID = {session_id}")
        
        # Générer les tirages
        print(f"\nGénération des tirages...")
        start_date = datetime.now() - timedelta(days=years*365)
        
        for week in range(weeks):
            if (week + 1) % 52 == 0:
                print(f"  Année {(week+1)//52} / {years} complétée...")
            
            for draw_idx in range(draws_per_week):
                draw_number = week * draws_per_week + draw_idx + 1
                draw_date = start_date + timedelta(days=week*7 + draw_idx)
                
                # Générer le tirage
                winning_numbers = self.generate_draw(numbers_pool, draw_size=5)
                
                # Insérer dans la BD
                cur.execute("""
                    INSERT INTO session_draws (
                        session_id, draw_number, lottery_name, draw_date,
                        winning_numbers, is_completed, cycle_position
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    session_id,
                    draw_number,
                    f'{universe}_weekly',
                    draw_date.date(),
                    json.dumps(winning_numbers),
                    True,
                    (draw_number - 1) % 7 + 1
                ))
        
        conn.commit()
        conn.close()
        
        print(f"\n{'='*60}")
        print(f"SIMULATION TERMINÉE")
        print(f"{'='*60}")
        print(f"Session ID: {session_id}")
        print(f"Tirages générés: {total_draws}")
        print(f"Periode: {start_date.date()} -> {datetime.now().date()}")
        print(f"{'='*60}\n")
        
        return session_id


def main():
    """Point d'entrée principal"""
    db_config = {
        'dbname': 'katooling_main_system',
        'user': 'postgres',
        'password': 'Katulaa_33',
        'host': 'localhost',
        'port': '5432'
    }
    
    generator = SimulationGenerator(db_config)
    
    # Générer simulation 10 ans
    session_id = generator.create_simulation_session(
        universe='mundo',
        years=10,
        draws_per_week=1  # 1 tirage par semaine (style loto hebdo)
    )
    
    print(f"\n✅ Session de simulation créée avec succès!")
    print(f"Pour analyser les patterns, lancez:")
    print(f"  python discover_patterns.py --session-id {session_id}")
    

if __name__ == "__main__":
    main()
