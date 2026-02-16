#!/usr/bin/env python3
"""
Migration pour centraliser toutes les sessions dans unified_sessions
et supprimer work_sessions
"""

import psycopg2
import json
from datetime import datetime

def migrate_to_unified_only():
    """Migrer vers unified_sessions uniquement"""
    
    db_config = {
        'host': 'localhost',
        'database': 'katooling_main_system',
        'user': 'postgres',
        'password': 'Katulaa_33',
        'port': 5432
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        print("=== MIGRATION VERS UNIFIED_SESSIONS UNIQUEMENT ===\n")
        
        # 1. Vérifier les données manquantes dans unified_sessions
        print("1. VERIFICATION DES DONNEES MANQUANTES:")
        
        cursor.execute("""
            SELECT w.id, w.name, w.created_at, w.total_draws
            FROM work_sessions w
            LEFT JOIN unified_sessions u ON w.name = u.name
            WHERE u.name IS NULL
        """)
        missing_sessions = cursor.fetchall()
        
        if missing_sessions:
            print(f"   Sessions manquantes dans unified_sessions: {len(missing_sessions)}")
            for session in missing_sessions:
                print(f"     - {session[1]} (ID {session[0]})")
        else:
            print("   Toutes les sessions work_sessions existent dans unified_sessions")
        
        # 2. Synchroniser les données les plus récentes
        print("\n2. SYNCHRONISATION DES DONNEES:")
        
        cursor.execute("""
            SELECT w.id, w.name, w.created_at, w.total_draws, w.current_draw, w.is_active,
                   u.id as u_id, u.created_at as u_created_at
            FROM work_sessions w
            JOIN unified_sessions u ON w.name = u.name
            WHERE w.created_at > u.created_at OR w.total_draws != u.total_draws
        """)
        outdated_sessions = cursor.fetchall()
        
        if outdated_sessions:
            print(f"   Sessions à synchroniser: {len(outdated_sessions)}")
            for session in outdated_sessions:
                print(f"     - {session[1]}: work({session[3]} tirages) > unified({session[6]} tirages)")
                
                # Mettre à jour unified_sessions avec les données de work_sessions
                cursor.execute("""
                    UPDATE unified_sessions 
                    SET total_draws = %s, current_draw = %s, is_active = %s, updated_at = %s
                    WHERE name = %s
                """, (session[3], session[4], session[5], session[2], session[1]))
        
        # 3. Migrer les tirages de session_draws vers unified_draws
        print("\n3. MIGRATION DES TIRAGES:")
        
        cursor.execute("""
            SELECT COUNT(*) FROM session_draws sd
            JOIN work_sessions ws ON sd.session_id = ws.id
            LEFT JOIN unified_draws ud ON ud.session_uuid = (
                SELECT session_uuid FROM unified_sessions WHERE name = ws.name
            ) AND ud.draw_number = sd.draw_number
            WHERE ud.id IS NULL
        """)
        missing_draws = cursor.fetchone()[0]
        
        if missing_draws > 0:
            print(f"   Tirages à migrer: {missing_draws}")
            
            # Migrer les tirages manquants
            cursor.execute("""
                INSERT INTO unified_draws (session_uuid, draw_number, lottery_name, draw_date, winning_numbers, is_completed, metadata)
                SELECT 
                    us.session_uuid,
                    sd.draw_number,
                    sd.lottery_name,
                    sd.draw_date,
                    sd.winning_numbers,
                    sd.is_completed,
                    json_build_object(
                        'cycle_position', sd.cycle_position,
                        'is_no_draw', sd.is_no_draw,
                        'migrated_from', 'session_draws'
                    )
                FROM session_draws sd
                JOIN work_sessions ws ON sd.session_id = ws.id
                JOIN unified_sessions us ON us.name = ws.name
                LEFT JOIN unified_draws ud ON ud.session_uuid = us.session_uuid AND ud.draw_number = sd.draw_number
                WHERE ud.id IS NULL
            """)
            migrated_draws = cursor.rowcount
            print(f"   Tirages migrés: {migrated_draws}")
        
        # 4. Vérifier l'intégrité après migration
        print("\n4. VERIFICATION DE L'INTEGRITE:")
        
        cursor.execute("SELECT COUNT(*) FROM unified_sessions")
        unified_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM unified_draws")
        unified_draws_count = cursor.fetchone()[0]
        
        print(f"   unified_sessions: {unified_count} sessions")
        print(f"   unified_draws: {unified_draws_count} tirages")
        
        # 5. Créer une sauvegarde des tables work_*
        print("\n5. CREATION DE SAUVEGARDE:")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_sessions_backup AS 
            SELECT *, NOW() as backup_date FROM work_sessions
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_draws_backup AS 
            SELECT *, NOW() as backup_date FROM session_draws
        """)
        
        print("   Sauvegarde créée: work_sessions_backup, session_draws_backup")
        
        conn.commit()
        
        # 6. Plan de suppression (à exécuter manuellement)
        print("\n6. PLAN DE SUPPRESSION (à exécuter manuellement):")
        print("   -- Supprimer les tables work_* après vérification")
        print("   -- DROP TABLE session_draws;")
        print("   -- DROP TABLE work_sessions;")
        
        cursor.close()
        conn.close()
        
        print("\n=== MIGRATION TERMINEE ===")
        print("unified_sessions est maintenant la table principale")
        print("unified_draws contient tous les tirages")
        
        return True
        
    except Exception as e:
        print(f"Erreur: {e}")
        return False

if __name__ == "__main__":
    success = migrate_to_unified_only()
    if success:
        print("\nMIGRATION REUSSIE!")
    else:
        print("\nMIGRATION ECHOUEE!")