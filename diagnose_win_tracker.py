#!/usr/bin/env python3
"""
Script de diagnostic Win-Tracker
Analyse pourquoi aucune opportunité n'est trouvée
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME', 'katooling_main_system'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'Katulaa_33'),
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432')
    )

def diagnose_session(session_name='sim_2024_mon-sun_weekly', universe='mundo'):
    print(f"\n{'='*80}")
    print(f"DIAGNOSTIC WIN-TRACKER: {session_name} / {universe}")
    print(f"{'='*80}\n")
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # 1. Vérifier la session
    print("1. VÉRIFICATION SESSION")
    cur.execute("SELECT * FROM work_sessions WHERE name = %s", (session_name,))
    session = cur.fetchone()
    if not session:
        print(f"   [X] Session '{session_name}' introuvable!")
        return
    
    session_id = session['id']
    print(f"   [OK] Session trouvee: ID={session_id}, Type={session['lottery_type']}")
    
    # 2. Compter les tirages
    print("\n2. TIRAGES DISPONIBLES")
    cur.execute("""
        SELECT COUNT(*) as total,
               COUNT(CASE WHEN is_completed THEN 1 END) as completed,
               MIN(draw_date) as first_date,
               MAX(draw_date) as last_date
        FROM session_draws 
        WHERE session_id = %s
    """, (session_id,))
    draws_info = cur.fetchone()
    print(f"   Total tirages: {draws_info['total']}")
    print(f"   Tirages complétés: {draws_info['completed']}")
    print(f"   Periode: {draws_info['first_date']} -> {draws_info['last_date']}")
    
    if draws_info['completed'] == 0:
        print("   [X] Aucun tirage complete!")
        return
    
    # 3. Vérifier les combinaisons dans l'univers
    print(f"\n3. COMBINAISONS DANS L'UNIVERS '{universe}'")
    cur.execute("""
        SELECT COUNT(*) as total,
               COUNT(DISTINCT chip) as chips,
               COUNT(DISTINCT petique) as petiques,
               COUNT(DISTINCT granque_name) as granques,
               COUNT(DISTINCT tome) as tomes,
               COUNT(DISTINCT forme) as formes
        FROM combinations 
        WHERE univers = %s
    """, (universe,))
    combos = cur.fetchone()
    print(f"   Total combinaisons: {combos['total']}")
    print(f"   Chips: {combos['chips']}, Pétiques: {combos['petiques']}")
    print(f"   Granques: {combos['granques']}, Tomes: {combos['tomes']}, Formes: {combos['formes']}")
    
    if combos['total'] == 0:
        print(f"   [X] Aucune combinaison dans l'univers '{universe}'!")
        return
    
    # 4. Analyser une zone exemple (petique q1)
    print("\n4. ANALYSE ZONE EXEMPLE: petique=q1")
    cur.execute("""
        SELECT COUNT(DISTINCT combination) as count
        FROM combinations 
        WHERE univers = %s AND petique = 'q1'
    """, (universe,))
    zone_count = cur.fetchone()['count']
    print(f"   Combinaisons dans q1: {zone_count}")
    
    investment_cost = zone_count * 1
    potential_gain = 200
    net_profit = potential_gain - investment_cost
    roi = (net_profit / investment_cost * 100) if investment_cost > 0 else 0
    
    print(f"   Coût investissement: {investment_cost} unités")
    print(f"   Gain potentiel: {potential_gain} unités")
    print(f"   Profit net: {net_profit} unités")
    print(f"   ROI: {roi:.2f}%")
    
    # 5. Tester l'estimation de probabilité
    print("\n5. ESTIMATION PROBABILITÉ (200 derniers tirages)")
    try:
        cur.execute("""
            SELECT COUNT(*) as count
            FROM session_draws
            WHERE winning_numbers IS NOT NULL 
              AND jsonb_array_length(winning_numbers::jsonb) > 0
              AND is_completed = TRUE
            ORDER BY draw_date DESC
            LIMIT 200
        """)
        available_draws = cur.fetchone()['count']
        print(f"   Tirages disponibles pour analyse: {available_draws}")
        
        if available_draws < 10:
            print(f"   [!] Trop peu de tirages pour estimation fiable!")
        
        # Simuler le calcul de probabilité
        from win_tracker_service import WinTrackerService
        service = WinTrackerService()
        prob = service._estimate_zone_probability(universe, 'petique', 'q1', lookback=200)
        print(f"   Probabilité estimée: {prob:.6f} ({prob*100:.4f}%)")
        
        expected_return = prob * potential_gain
        expected_profit = expected_return - investment_cost
        expected_roi = (expected_profit / investment_cost * 100) if investment_cost > 0 else 0
        
        print(f"   Espérance de retour: {expected_return:.2f} unités")
        print(f"   Espérance de profit: {expected_profit:.2f} unités")
        print(f"   ROI espéré: {expected_roi:.2f}%")
        
        # 6. Vérifier la recommandation
        print("\n6. LOGIQUE DE RECOMMANDATION")
        risk_level = 'LOW' if investment_cost <= 150 else ('MEDIUM' if investment_cost <= 180 else 'HIGH')
        print(f"   Niveau de risque: {risk_level}")
        
        # Critères pour BUY
        if expected_profit > 0 and expected_roi > 5:
            if risk_level == 'LOW':
                recommendation = 'BUY'
            elif risk_level == 'MEDIUM':
                recommendation = 'BUY' if expected_roi > 10 else 'HOLD'
            else:
                recommendation = 'BUY' if expected_roi > 20 else 'AVOID'
        elif expected_profit > 0:
            recommendation = 'HOLD'
        else:
            recommendation = 'AVOID'
        
        print(f"   Recommandation: {recommendation}")
        
        if recommendation != 'BUY':
            print(f"\n   [X] RAISON: Zone non recommandee BUY")
            print(f"      - Espérance profit: {expected_profit:.2f} (doit être > 0)")
            print(f"      - ROI espéré: {expected_roi:.2f}% (seuil: {5 if risk_level=='LOW' else (10 if risk_level=='MEDIUM' else 20)}%)")
        else:
            print(f"   [OK] Zone recommandee BUY!")
        
    except Exception as e:
        print(f"   [X] Erreur estimation: {e}")
        import traceback
        traceback.print_exc()
    
    # 7. Tester toutes les zones
    print("\n7. ANALYSE TOUTES LES ZONES")
    try:
        from win_tracker_service import WinTrackerService
        service = WinTrackerService()
        opportunities = service.get_best_opportunities(universe, limit=10)
        
        print(f"   Opportunités BUY trouvées: {len(opportunities)}")
        
        if opportunities:
            print("\n   TOP OPPORTUNITÉS:")
            for i, opp in enumerate(opportunities[:5], 1):
                print(f"   {i}. {opp.zone_type}={opp.zone_value}")
                print(f"      ROI: {opp.expected_roi:.2f}%, Profit: {opp.expected_profit:.2f}, Coût: {opp.investment_cost}")
        else:
            print("\n   [X] AUCUNE OPPORTUNITE TROUVEE")
            print("\n   CAUSES POSSIBLES:")
            print("   1. Probabilités trop faibles (< seuils ROI)")
            print("   2. Coûts d'investissement trop élevés")
            print("   3. Pas assez de tirages historiques")
            print("   4. Données de tirages mal formatées")
            
    except Exception as e:
        print(f"   [X] Erreur analyse: {e}")
        import traceback
        traceback.print_exc()
    
    conn.close()
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    session = sys.argv[1] if len(sys.argv) > 1 else 'sim_2024_mon-sun_weekly'
    universe = sys.argv[2] if len(sys.argv) > 2 else 'mundo'
    diagnose_session(session, universe)
