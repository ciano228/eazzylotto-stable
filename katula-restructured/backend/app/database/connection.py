import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from typing import Iterator, Any
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseConnectionError(Exception):
    """Exception levée pour les erreurs de connexion à la base de données."""
    pass

@contextmanager
def get_db_cursor() -> Iterator[psycopg2.extras.RealDictCursor]:
    """
    Contexte manager pour obtenir un curseur de base de données.
    
    Returns:
        psycopg2.extras.RealDictCursor: Un curseur configuré pour retourner des dictionnaires
        
    Raises:
        DatabaseConnectionError: Si la connexion à la base de données échoue
    """
    conn = None
    try:
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            port=settings.DB_PORT,
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Erreur lors de l'exécution de la requête: {str(e)}")
            raise
    except psycopg2.Error as e:
        error_msg = f"Erreur de connexion à la base de données: {str(e)}"
        logger.error(error_msg)
        raise DatabaseConnectionError(error_msg) from e
    finally:
        if conn:
            try:
                cursor.close()
            except Exception as e:
                logger.warning(f"Erreur lors de la fermeture du curseur: {str(e)}")
            try:
                conn.close()
            except Exception as e:
                logger.warning(f"Erreur lors de la fermeture de la connexion: {str(e)}")

def execute_query(query: str, params: tuple = None, fetch: bool = True) -> list[dict[str, Any]]:
    """
    Exécute une requête SQL et retourne les résultats.
    
    Args:
        query: La requête SQL à exécuter
        params: Les paramètres à utiliser avec la requête
        fetch: Si True, retourne les résultats de la requête
        
    Returns:
        list[dict]: Une liste de dictionnaires représentant les lignes de résultats
    """
    with get_db_cursor() as cursor:
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall() if fetch else None
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de la requête: {str(e)}")
            raise

def execute_single_query(query: str, params: tuple = None) -> dict[str, Any]:
    """
    Exécute une requête SQL et retourne un seul résultat.
    
    Args:
        query: La requête SQL à exécuter
        params: Les paramètres à utiliser avec la requête
        
    Returns:
        dict: Un dictionnaire représentant la première ligne de résultats
    """
    with get_db_cursor() as cursor:
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone() or {}
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de la requête: {str(e)}")
            raise
