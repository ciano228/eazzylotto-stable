"""
Exemple d'utilisation du Service Manager avec Vérification d'Existence
Démontre l'optimisation et la réutilisation des instances
"""
from .service_manager import service_manager
from .enhanced_data_service import get_enhanced_data_service, EnhancedDataService

def demonstrate_service_optimization():
    """Démontre l'optimisation des services"""
    
    print("=== DÉMONSTRATION SERVICE MANAGER ===\n")
    
    # 1. Première utilisation - création
    print("1️⃣ Première demande de service:")
    service1 = get_enhanced_data_service()
    print(f"   Service ID: {id(service1)}")
    
    # 2. Deuxième utilisation - réutilisation
    print("\n2️⃣ Deuxième demande de service:")
    service2 = get_enhanced_data_service()
    print(f"   Service ID: {id(service2)}")
    print(f"   Même instance? {service1 is service2}")
    
    # 3. Vérification d'existence
    print("\n3️⃣ Vérification d'existence:")
    exists = service_manager.service_exists("enhanced_data_service")
    print(f"   Service existe? {exists}")
    
    # 4. Liste des services actifs
    print("\n4️⃣ Services actifs:")
    services = service_manager.list_services()
    for name, class_name in services.items():
        print(f"   - {name}: {class_name}")
    
    # 5. Test avec données réelles
    print("\n5️⃣ Test avec données réelles:")
    try:
        data = service1.get_real_structure_data("mundo")
        if "error" not in data:
            print(f"   ✅ Données récupérées: {data['total_entries']} entrées")
        else:
            print(f"   ⚠️ Erreur: {data['error']}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    return service1

def test_multiple_service_types():
    """Test avec différents types de services"""
    
    print("\n=== TEST SERVICES MULTIPLES ===\n")
    
    # Service personnalisé pour test
    class TestService:
        def __init__(self, name):
            self.name = name
            print(f"🔧 TestService '{name}' initialisé")
    
    # Créer plusieurs services
    test1 = service_manager.get_service("test_service_1", TestService, "Premier")
    test2 = service_manager.get_service("test_service_2", TestService, "Deuxième") 
    test1_bis = service_manager.get_service("test_service_1", TestService, "Ignoré")
    
    print(f"\nRésultats:")
    print(f"- test1.name: {test1.name}")
    print(f"- test2.name: {test2.name}")
    print(f"- test1_bis.name: {test1_bis.name}")
    print(f"- test1 is test1_bis: {test1 is test1_bis}")
    
    # Nettoyage
    service_manager.remove_service("test_service_1")
    service_manager.remove_service("test_service_2")

if __name__ == "__main__":
    # Exécuter les démonstrations
    service = demonstrate_service_optimization()
    test_multiple_service_types()
    
    print("\n=== RÉSUMÉ ===")
    print("✅ Avantages de cette approche:")
    print("   - Évite les doublons d'instances")
    print("   - Optimise l'utilisation mémoire") 
    print("   - Maintient les connexions DB")
    print("   - Thread-safe avec verrous")
    print("   - Gestion centralisée des services")