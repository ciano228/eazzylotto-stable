"""
Test fonctionnel du service Katula avec les variables d'environnement
"""
import os
from dotenv import load_dotenv
from katula_complete_service import katula_service

def test_katula_service():
    """Test les fonctionnalités principales du service"""
    # Les variables d'environnement sont déjà chargées
    
    # 1. Vérifier la configuration
    print("\nConfiguration de la base de données :")
    print(f"Host: {os.getenv('KATULA_DB_HOST')}")
    print(f"Database: {os.getenv('KATULA_DB_NAME')}")
    print(f"User: {os.getenv('KATULA_DB_USER')}")
    print(f"Port: {os.getenv('KATULA_DB_PORT')}")
    
    # 2. Tester la récupération d'un chip
    print("\nTest de récupération d'un chip :")
    chip_result = katula_service.get_chip_compartments("mundo", 1)
    print(f"Résultat du chip: {chip_result}")
    
    # 3. Tester les options de filtrage
    print("\nTest des options de filtrage :")
    filter_options = katula_service.get_filter_options("mundo")
    print(f"Options de filtrage: {filter_options}")
    
    # 4. Tester la matrice
    print("\nTest de la matrice :")
    matrix_result = katula_service.get_matrix_with_compartments("mundo")
    print(f"Dimensions de la matrice: {matrix_result.get('dimensions')}")

if __name__ == "__main__":
    test_katula_service()