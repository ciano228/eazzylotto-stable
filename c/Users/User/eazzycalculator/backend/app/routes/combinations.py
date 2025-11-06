"""
Routes pour la gestion des combinaisons avec les nouvelles colonnes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
from app.database.connection import get_db

router = APIRouter(prefix="/api/combinations", tags=["combinations"])

@router.get("/universe/{universe}")
async def get_combinations_by_universe(
    universe: str,
    db: Session = Depends(get_db),
    limit: int = Query(50, description="Nombre de combinaisons à récupérer"),
    offset: int = Query(0, description="Décalage pour la pagination")
):
    """Récupérer les combinaisons d'un univers avec toutes les colonnes"""
    
    try:
        # Vérifier que l'univers existe
        valid_universes = ['mundo', 'fruity', 'trigga', 'roaster', 'sunshine']
        if universe not in valid_universes:
            raise HTTPException(
                status_code=400, 
                detail=f"Univers invalide. Univers disponibles: {valid_universes}"
            )
        
        # Requête pour récupérer les combinaisons avec les nouvelles colonnes
        query = """
            SELECT 
                c.combination_id,
                c.num1,
                c.num2,
                c.combination,
                c.univers,
                c.forme,
                c.engine,
                c.beastie,
                c.tome,
                c.granque_name,
                c.denomination,
                c.chip,
                c.ligne,
                c.colonne,
                c.petique,
                t.ligne as table_ligne,
                t.colonne as table_colonne,
                t.forme as table_forme,
                t.denomination as table_denomination,
                t.tome as table_tome,
                t.granque_name as table_granque_name
            FROM combinations c
            LEFT JOIN table_de_katula t ON c.univers = t.univers 
                AND (c.chip = t.chip OR c.ligne = t.ligne AND c.colonne = t.colonne)
            WHERE c.univers = :universe
            ORDER BY c.combination_id DESC
            LIMIT :limit OFFSET :offset
        """
        
        result = db.execute(text(query), {
            "universe": universe,
            "limit": limit,
            "offset": offset
        })
        
        combinations = []
        for row in result.fetchall():
            combination = {
                "combination_id": row.combination_id,
                "numbers": {
                    "num1": row.num1,
                    "num2": row.num2,
                    "combination": row.combination
                },
                "universe": row.univers,
                "attributes": {
                    "forme": row.forme or row.table_forme,
                    "engine": row.engine,
                    "beastie": row.beastie,
                    "tome": row.tome or row.table_tome,
                    "granque_name": row.granque_name or row.table_granque_name,
                    "denomination": row.denomination or row.table_denomination
                },
                "position": {
                    "chip": row.chip,
                    "ligne": row.ligne or row.table_ligne,
                    "colonne": row.colonne or row.table_colonne,
                    "petique": row.petique
                },
                "table_data": {
                    "ligne": row.table_ligne,
                    "colonne": row.table_colonne,
                    "forme": row.table_forme,
                    "denomination": row.table_denomination,
                    "tome": row.table_tome,
                    "granque_name": row.table_granque_name
                }
            }
            combinations.append(combination)
        
        # Compter le total pour la pagination
        count_query = "SELECT COUNT(*) FROM combinations WHERE univers = :universe"
        total_result = db.execute(text(count_query), {"universe": universe})
        total_count = total_result.scalar()
        
        return {
            "universe": universe,
            "combinations": combinations,
            "pagination": {
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total_count
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")

@router.get("/table-data/{universe}")
async def get_table_data_by_universe(
    universe: str,
    db: Session = Depends(get_db)
):
    """Récupérer les données de table_de_katula pour un univers"""
    
    try:
        valid_universes = ['mundo', 'fruity', 'trigga', 'roaster', 'sunshine']
        if universe not in valid_universes:
            raise HTTPException(
                status_code=400, 
                detail=f"Univers invalide. Univers disponibles: {valid_universes}"
            )
        
        query = """
            SELECT 
                chip_id,
                univers,
                ligne,
                colonne,
                petique,
                chip,
                forme,
                denomination,
                tome,
                granque_name
            FROM table_de_katula
            WHERE univers = :universe
            ORDER BY chip_id
        """
        
        result = db.execute(text(query), {"universe": universe})
        
        table_data = []
        for row in result.fetchall():
            entry = {
                "chip_id": row.chip_id,
                "univers": row.univers,
                "position": {
                    "ligne": row.ligne,
                    "colonne": row.colonne,
                    "petique": row.petique,
                    "chip": row.chip
                },
                "attributes": {
                    "forme": row.forme,
                    "denomination": row.denomination,
                    "tome": row.tome,
                    "granque_name": row.granque_name
                }
            }
            table_data.append(entry)
        
        return {
            "universe": universe,
            "table_data": table_data,
            "total_entries": len(table_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")

@router.get("/search")
async def search_combinations(
    db: Session = Depends(get_db),
    universe: Optional[str] = Query(None, description="Filtrer par univers"),
    granque_name: Optional[str] = Query(None, description="Filtrer par granque-name"),
    tome: Optional[str] = Query(None, description="Filtrer par tome"),
    forme: Optional[str] = Query(None, description="Filtrer par forme"),
    limit: int = Query(20, description="Nombre de résultats")
):
    """Rechercher des combinaisons avec les nouveaux critères"""
    
    try:
        # Construire la requête dynamiquement
        where_conditions = []
        params = {"limit": limit}
        
        if universe:
            where_conditions.append("c.univers = :universe")
            params["universe"] = universe
            
        if granque_name:
            where_conditions.append("(c.granque_name ILIKE :granque_name OR t.granque_name ILIKE :granque_name)")
            params["granque_name"] = f"%{granque_name}%"
            
        if tome:
            where_conditions.append("(c.tome ILIKE :tome OR t.tome ILIKE :tome)")
            params["tome"] = f"%{tome}%"
            
        if forme:
            where_conditions.append("(c.forme ILIKE :forme OR t.forme ILIKE :forme)")
            params["forme"] = f"%{forme}%"
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        query = f"""
            SELECT DISTINCT
                c.combination_id,
                c.num1,
                c.num2,
                c.univers,
                c.granque_name,
                c.tome,
                c.forme,
                c.denomination,
                c.chip,
                t.granque_name as table_granque_name,
                t.tome as table_tome,
                t.forme as table_forme
            FROM combinations c
            LEFT JOIN table_de_katula t ON c.univers = t.univers
            WHERE {where_clause}
            ORDER BY c.combination_id DESC
            LIMIT :limit
        """
        
        result = db.execute(text(query), params)
        
        search_results = []
        for row in result.fetchall():
            result_item = {
                "combination_id": row.combination_id,
                "numbers": f"{row.num1}-{row.num2}",
                "universe": row.univers,
                "granque_name": row.granque_name or row.table_granque_name,
                "tome": row.tome or row.table_tome,
                "forme": row.forme or row.table_forme,
                "denomination": row.denomination,
                "chip": row.chip
            }
            search_results.append(result_item)
        
        return {
            "search_criteria": {
                "universe": universe,
                "granque_name": granque_name,
                "tome": tome,
                "forme": forme
            },
            "results": search_results,
            "total_found": len(search_results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la recherche: {str(e)}")

@router.get("/stats/{universe}")
async def get_universe_stats(
    universe: str,
    db: Session = Depends(get_db)
):
    """Obtenir les statistiques d'un univers avec les nouvelles colonnes"""
    
    try:
        valid_universes = ['mundo', 'fruity', 'trigga', 'roaster', 'sunshine']
        if universe not in valid_universes:
            raise HTTPException(
                status_code=400, 
                detail=f"Univers invalide. Univers disponibles: {valid_universes}"
            )
        
        # Statistiques générales
        stats_query = """
            SELECT 
                COUNT(*) as total_combinations,
                COUNT(DISTINCT granque_name) as unique_granque_names,
                COUNT(DISTINCT tome) as unique_tomes,
                COUNT(DISTINCT forme) as unique_formes
            FROM table_de_katula
            WHERE univers = :universe
        """
        
        stats_result = db.execute(text(stats_query), {"universe": universe})
        stats = stats_result.fetchone()
        
        # Distribution par tome
        tome_query = """
            SELECT tome, COUNT(*) as count
            FROM table_de_katula
            WHERE univers = :universe AND tome IS NOT NULL
            GROUP BY tome
            ORDER BY count DESC
        """
        
        tome_result = db.execute(text(tome_query), {"universe": universe})
        tome_distribution = {row.tome: row.count for row in tome_result.fetchall()}
        
        # Distribution par forme
        forme_query = """
            SELECT forme, COUNT(*) as count
            FROM table_de_katula
            WHERE univers = :universe AND forme IS NOT NULL
            GROUP BY forme
            ORDER BY count DESC
        """
        
        forme_result = db.execute(text(forme_query), {"universe": universe})
        forme_distribution = {row.forme: row.count for row in forme_result.fetchall()}
        
        return {
            "universe": universe,
            "general_stats": {
                "total_combinations": stats.total_combinations,
                "unique_granque_names": stats.unique_granque_names,
                "unique_tomes": stats.unique_tomes,
                "unique_formes": stats.unique_formes
            },
            "distributions": {
                "by_tome": tome_distribution,
                "by_forme": forme_distribution
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul des statistiques: {str(e)}")