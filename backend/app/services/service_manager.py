"""
Gestionnaire de Services avec Vérification d'Existence
Évite la création de doublons et optimise la gestion des instances
"""
from typing import Dict, Any, Optional, Type
import threading
from datetime import datetime

class ServiceManager:
    """Gestionnaire centralisé des services avec vérification d'existence"""
    
    _instances: Dict[str, Any] = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_service(cls, service_name: str, service_class: Type, *args, **kwargs) -> Any:
        """
        Récupère ou crée un service avec vérification d'existence
        
        Args:
            service_name: Nom unique du service
            service_class: Classe du service à instancier
            *args, **kwargs: Arguments pour l'initialisation
            
        Returns:
            Instance du service (existante ou nouvelle)
        """
        with cls._lock:
            # Vérifier si le service existe déjà
            if service_name in cls._instances:
                print(f"[INFO] Service '{service_name}' déjà existant - réutilisation")
                return cls._instances[service_name]
            
            # Créer nouvelle instance
            try:
                print(f"[INFO] Création nouveau service '{service_name}'")
                instance = service_class(*args, **kwargs)
                cls._instances[service_name] = instance
                print(f"[SUCCES] Service '{service_name}' créé avec succès")
                return instance
                
            except Exception as e:
                print(f"[ERREUR] Erreur création service '{service_name}': {e}")
                raise
    
    @classmethod
    def service_exists(cls, service_name: str) -> bool:
        """Vérifie si un service existe déjà"""
        return service_name in cls._instances
    
    @classmethod
    def remove_service(cls, service_name: str) -> bool:
        """Supprime un service du gestionnaire"""
        with cls._lock:
            if service_name in cls._instances:
                del cls._instances[service_name]
                print(f"🗑️ Service '{service_name}' supprimé")
                return True
            return False
    
    @classmethod
    def list_services(cls) -> Dict[str, str]:
        """Liste tous les services actifs"""
        return {
            name: type(instance).__name__ 
            for name, instance in cls._instances.items()
        }
    
    @classmethod
    def clear_all(cls) -> None:
        """Supprime tous les services"""
        with cls._lock:
            cls._instances.clear()
            print("🧹 Tous les services supprimés")

# Instance globale
service_manager = ServiceManager()