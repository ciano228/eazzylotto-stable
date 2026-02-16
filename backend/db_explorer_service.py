"""
Service d'exploration de la base de données PostgreSQL
Identifie les tables existantes et leur structure
"""

import psycopg2
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

class DatabaseExplorerService:
    def __init__(self):
        # Utiliser la même config que KatulaCompleteService
        try:
            from katula_complete_service import KatulaCompleteService
            katula_service = KatulaCompleteService()
            self.db_config = katula_service.db_config
        except:
            load_dotenv()
            self.db_config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'database': os.getenv('DB_NAME', 'katooling_main_system'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', 'postgres')
            }
    
    def explore_database_structure(self) -> Dict[str, Any]:
        """Explore la structure complète de la base de données"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Lister toutes les tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            
            result = {
                'database': self.db_config['database'],
                'total_tables': len(tables),
                'tables': tables,
                'session_related_tables': [],
                'draw_related_tables': [],
                'other_tables': []
            }
            
            # Classifier les tables
            for table in tables:
                if 'session' in table.lower():
                    result['session_related_tables'].append(table)
                elif any(word in table.lower() for word in ['draw', 'tirage', 'result', 'lottery', 'loto']):
                    result['draw_related_tables'].append(table)
                else:
                    result['other_tables'].append(table)
            
            cursor.close()
            conn.close()
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_table_structure(self, table_name: str) -> Dict[str, Any]:
        """Récupère la structure d'une table spécifique"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Structure de la table
            cursor.execute("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))
            
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    'name': row[0],
                    'type': row[1],
                    'nullable': row[2] == 'YES',
                    'default': row[3],
                    'max_length': row[4]
                })
            
            # Contraintes et clés
            cursor.execute("""
                SELECT 
                    tc.constraint_name,
                    tc.constraint_type,
                    kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu 
                    ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_name = %s
            """, (table_name,))
            
            constraints = []
            for row in cursor.fetchall():
                constraints.append({
                    'name': row[0],
                    'type': row[1],
                    'column': row[2]
                })
            
            # Compter les enregistrements
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            record_count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            return {
                'table_name': table_name,
                'columns': columns,
                'constraints': constraints,
                'record_count': record_count
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def search_session_data(self) -> Dict[str, Any]:
        """Recherche des données de sessions existantes"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            result = {
                'sessions_found': False,
                'session_tables': [],
                'potential_session_data': []
            }
            
            # Chercher des tables contenant "session"
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND LOWER(table_name) LIKE '%session%'
            """)
            
            session_tables = [row[0] for row in cursor.fetchall()]
            result['session_tables'] = session_tables
            
            if session_tables:
                result['sessions_found'] = True
                
                # Explorer chaque table de session
                for table in session_tables:
                    try:
                        cursor.execute(f"SELECT * FROM {table} LIMIT 5")
                        sample_data = cursor.fetchall()
                        
                        # Récupérer les noms de colonnes
                        cursor.execute("""
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name = %s
                            ORDER BY ordinal_position
                        """, (table,))
                        
                        columns = [row[0] for row in cursor.fetchall()]
                        
                        result['potential_session_data'].append({
                            'table': table,
                            'columns': columns,
                            'sample_data': sample_data[:3]  # Limiter à 3 exemples
                        })
                        
                    except Exception as table_error:
                        result['potential_session_data'].append({
                            'table': table,
                            'error': str(table_error)
                        })
            
            cursor.close()
            conn.close()
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def search_draw_data(self) -> Dict[str, Any]:
        """Recherche des données de tirages existantes"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            result = {
                'draws_found': False,
                'draw_tables': [],
                'potential_draw_data': []
            }
            
            # Chercher des tables contenant des mots-clés de tirages
            keywords = ['draw', 'tirage', 'result', 'lottery', 'loto', 'numero', 'number']
            
            for keyword in keywords:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND LOWER(table_name) LIKE %s
                """, (f'%{keyword}%',))
                
                tables = [row[0] for row in cursor.fetchall()]
                result['draw_tables'].extend(tables)
            
            # Supprimer les doublons
            result['draw_tables'] = list(set(result['draw_tables']))
            
            if result['draw_tables']:
                result['draws_found'] = True
                
                # Explorer chaque table de tirage
                for table in result['draw_tables']:
                    try:
                        cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                        sample_data = cursor.fetchall()
                        
                        cursor.execute("""
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name = %s
                            ORDER BY ordinal_position
                        """, (table,))
                        
                        columns = [row[0] for row in cursor.fetchall()]
                        
                        result['potential_draw_data'].append({
                            'table': table,
                            'columns': columns,
                            'sample_data': sample_data
                        })
                        
                    except Exception as table_error:
                        result['potential_draw_data'].append({
                            'table': table,
                            'error': str(table_error)
                        })
            
            cursor.close()
            conn.close()
            
            return result
            
        except Exception as e:
            return {"error": str(e)}