#!/usr/bin/env python3
"""
🎯 EazzyLotto - Lanceur Automatique
Démarre automatiquement backend + frontend et ouvre l'application
"""

import os
import sys
import subprocess
import time
import webbrowser
import threading
from pathlib import Path

class EazzyLottoLauncher:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.backend_process = None
        self.frontend_process = None
        
    def print_banner(self):
        print("=" * 60)
        print("🎯 EAZZYLOTTO - LANCEUR AUTOMATIQUE")
        print("=" * 60)
        print("🚀 Démarrage automatique de l'application...")
        print()
        
    def check_dependencies(self):
        """Vérifier les dépendances Python"""
        print("🔍 Vérification des dépendances...")
        
        required_packages = ['fastapi', 'uvicorn', 'sqlalchemy']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package} - OK")
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package} - MANQUANT")
        
        if missing_packages:
            print(f"\n⚠️ Packages manquants: {', '.join(missing_packages)}")
            print("📦 Installation automatique...")
            
            for package in missing_packages:
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                    print(f"✅ {package} installé")
                except subprocess.CalledProcessError:
                    print(f"❌ Erreur installation {package}")
        
        print("✅ Dépendances vérifiées\n")
    
    def start_backend(self):
        """Démarrer le serveur backend"""
        print("🔧 Démarrage du backend...")
        
        backend_dir = self.root_dir / "backend"
        
        if not backend_dir.exists():
            print("❌ Dossier backend introuvable")
            return False
        
        # Chercher le fichier main
        main_files = ["main.py", "main_fixed.py", "app.py"]
        main_file = None
        
        for file in main_files:
            if (backend_dir / file).exists():
                main_file = file.replace('.py', '')
                break
        
        if not main_file:
            print("❌ Fichier main introuvable dans backend/")
            return False
        
        try:
            os.chdir(backend_dir)
            
            # Commande uvicorn
            cmd = [
                sys.executable, "-m", "uvicorn", 
                f"{main_file}:app", 
                "--reload", 
                "--host", "0.0.0.0", 
                "--port", "8000"
            ]
            
            print(f"🚀 Commande: {' '.join(cmd)}")
            
            # Démarrer en arrière-plan
            self.backend_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            # Retourner au dossier racine
            os.chdir(self.root_dir)
            
            # Attendre que le serveur démarre
            print("⏳ Attente du démarrage backend...")
            time.sleep(5)
            
            if self.backend_process.poll() is None:
                print("✅ Backend démarré sur http://localhost:8000")
                return True
            else:
                print("❌ Erreur démarrage backend")
                return False
                
        except Exception as e:
            print(f"❌ Erreur backend: {e}")
            os.chdir(self.root_dir)
            return False
    
    def start_frontend(self):
        """Démarrer le serveur frontend"""
        print("🌐 Démarrage du frontend...")
        
        frontend_dir = self.root_dir / "frontend"
        
        # Si pas de dossier frontend, utiliser le dossier racine
        if not frontend_dir.exists():
            frontend_dir = self.root_dir
            print("📁 Utilisation du dossier racine pour le frontend")
        
        try:
            os.chdir(frontend_dir)
            
            # Chercher server.py ou utiliser http.server
            if (frontend_dir / "server.py").exists():
                cmd = [sys.executable, "server.py"]
            else:
                cmd = [sys.executable, "-m", "http.server", "8081"]
            
            print(f"🚀 Commande: {' '.join(cmd)}")
            
            # Démarrer en arrière-plan
            self.frontend_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            # Retourner au dossier racine
            os.chdir(self.root_dir)
            
            # Attendre que le serveur démarre
            print("⏳ Attente du démarrage frontend...")
            time.sleep(3)
            
            if self.frontend_process.poll() is None:
                print("✅ Frontend démarré sur http://localhost:8081")
                return True
            else:
                print("❌ Erreur démarrage frontend")
                return False
                
        except Exception as e:
            print(f"❌ Erreur frontend: {e}")
            os.chdir(self.root_dir)
            return False
    
    def open_browser(self):
        """Ouvrir le navigateur"""
        print("🌐 Ouverture du navigateur...")
        
        urls_to_try = [
            "http://localhost:8081/launching-page.html",
            "http://localhost:8081/index.html",
            "http://localhost:8081"
        ]
        
        for url in urls_to_try:
            try:
                webbrowser.open(url)
                print(f"✅ Navigateur ouvert: {url}")
                break
            except Exception as e:
                print(f"⚠️ Erreur ouverture {url}: {e}")
                continue
    
    def show_status(self):
        """Afficher le statut de l'application"""
        print("\n" + "=" * 60)
        print("🎉 EAZZYLOTTO DÉMARRÉ AVEC SUCCÈS !")
        print("=" * 60)
        print("📱 URLs de l'application:")
        print("   🏠 Page d'accueil: http://localhost:8081/launching-page.html")
        print("   📊 Dashboard: http://localhost:8081/dashboard.html")
        print("   🎯 Saisie intelligente: http://localhost:8081/smart-input.html")
        print("   🔧 API Documentation: http://localhost:8000/docs")
        print("\n🔧 Serveurs actifs:")
        print("   ⚙️ Backend API: http://localhost:8000")
        print("   🌐 Frontend: http://localhost:8081")
        print("\n💡 Pour arrêter l'application, fermez cette fenêtre ou appuyez sur Ctrl+C")
        print("=" * 60)
    
    def cleanup(self):
        """Nettoyer les processus"""
        print("\n🛑 Arrêt de l'application...")
        
        if self.backend_process:
            self.backend_process.terminate()
            print("✅ Backend arrêté")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            print("✅ Frontend arrêté")
    
    def launch(self):
        """Lancer l'application complète"""
        try:
            self.print_banner()
            
            # Vérifier les dépendances
            self.check_dependencies()
            
            # Démarrer le backend
            backend_ok = self.start_backend()
            
            # Démarrer le frontend
            frontend_ok = self.start_frontend()
            
            if backend_ok and frontend_ok:
                # Ouvrir le navigateur
                time.sleep(2)
                self.open_browser()
                
                # Afficher le statut
                self.show_status()
                
                # Garder l'application en vie
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
            else:
                print("❌ Erreur lors du démarrage de l'application")
                
        except Exception as e:
            print(f"❌ Erreur critique: {e}")
        finally:
            self.cleanup()

if __name__ == "__main__":
    launcher = EazzyLottoLauncher()
    launcher.launch()
