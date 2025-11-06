"""
Configuration for database connection.
"""
import os

DB_CONFIG = {
    'dbname': os.getenv('KATOOLING_DB_NAME', 'katooling_main_system'),
    'user': os.getenv('KATOOLING_DB_USER', 'postgres'),
    'password': os.getenv('KATOOLING_DB_PASSWORD', ''),  # Retrieve from environment
    'host': os.getenv('KATOOLING_DB_HOST', 'localhost'),
    'port': os.getenv('KATOOLING_DB_PORT', '5432')
}