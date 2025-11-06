#!/usr/bin/env python3
"""
Script de test automatisé avec sauvegarde
"""
import subprocess
import sys
import time
import requests
import os
from datetime import datetime

class TestRunner:
    def __init__(self):
        self.test_results = []
        self.backup_created = False
    
    def create_pre_test_backup(self):
        """Créer un backup avant les tests"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M")
            branch_name = f"backup/pre-test-{timestamp}"
            
            subprocess.run(["git", "checkout", "-b", branch_name], check=True)
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", f"backup: pre-test state - {timestamp}"], check=True)
            
            # Revenir à la branche de développement
            subprocess.run(["git", "checkout", "dev/testing-katula-dynamic"], check=True)
            
            print(f"✅ Backup pré-test créé: {branch_name}")
            self.backup_created = True
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur backup pré-test: {e}")
            return False
    
    def test_environment(self):
        """Test 1: Vérifier l'environnement"""
        print("\n🔍 TEST 1: Environnement")
        
        # Vérifier PostgreSQL
        try:
            import psycopg2
            conn = psycopg2.connect(
                host='localhost',
                database='katooling_main_system',
                user='postgres',
                password='Katulaa_33',
                port=5432
            )
            conn.close()
            print("✅ PostgreSQL: Connexion OK")
            self.test_results.append(("PostgreSQL", True))
        except Exception as e:
            print(f"❌ PostgreSQL: {e}")
            self.test_results.append(("PostgreSQL", False))
        
        # Vérifier les dépendances
        try:
            import fastapi, uvicorn, sqlalchemy
            print("✅ Dépendances: OK")
            self.test_results.append(("Dépendances", True))
        except ImportError as e:
            print(f"❌ Dépendances manquantes: {e}")
            self.test_results.append(("Dépendances", False))
        
        # Vérifier les fichiers critiques
        critical_files = [
            "backend/main.py",
            "backend/app/routes/analytics.py",
            "app/pages/katula/katula-dynamic.html"
        ]
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                print(f"✅ Fichier: {file_path}")
                self.test_results.append((f"File-{file_path}", True))
            else:
                print(f"❌ Fichier manquant: {file_path}")
                self.test_results.append((f"File-{file_path}", False))
    
    def test_backend_startup(self):
        """Test 2: Démarrage du backend"""
        print("\n🚀 TEST 2: Backend")
        
        try:
            # Démarrer le serveur en arrière-plan
            process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "main:app",
                "--host", "0.0.0.0", "--port", "8000"
            ], cwd="backend")
            
            # Attendre le démarrage
            time.sleep(5)
            
            # Tester la connexion
            response = requests.get("http://localhost:8000/api/health", timeout=10)
            if response.status_code == 200:
                print("✅ Backend: Démarré et accessible")
                self.test_results.append(("Backend-Startup", True))
            else:
                print(f"❌ Backend: Status {response.status_code}")
                self.test_results.append(("Backend-Startup", False))
            
            # Arrêter le serveur
            process.terminate()
            process.wait()
            
        except Exception as e:
            print(f"❌ Backend: Erreur {e}")
            self.test_results.append(("Backend-Startup", False))
    
    def test_api_endpoints(self):
        """Test 3: Endpoints API"""
        print("\n🔗 TEST 3: API Endpoints")
        
        # Démarrer le serveur pour les tests
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0", "--port", "8000"
        ], cwd="backend")
        
        time.sleep(5)
        
        endpoints = [
            "/api/health",
            "/api/analytics/katula/table/fruity",
            "/api/analytics/formes/fruity"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"http://localhost:8000{endpoint}", timeout=10)
                if response.status_code == 200:
                    print(f"✅ API: {endpoint}")
                    self.test_results.append((f"API-{endpoint}", True))
                else:
                    print(f"❌ API: {endpoint} - Status {response.status_code}")
                    self.test_results.append((f"API-{endpoint}", False))
            except Exception as e:
                print(f"❌ API: {endpoint} - {e}")
                self.test_results.append((f"API-{endpoint}", False))
        
        # Arrêter le serveur
        process.terminate()
        process.wait()
    
    def test_katula_page(self):
        """Test 4: Page katula-dynamic"""
        print("\n🎯 TEST 4: Page Katula-Dynamic")
        
        # Vérifier que le fichier HTML existe et est valide
        html_path = "app/pages/katula/katula-dynamic.html"
        if os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "katula-grid" in content and "API_BASE" in content:
                    print("✅ Page Katula: Structure OK")
                    self.test_results.append(("Katula-Page", True))
                else:
                    print("❌ Page Katula: Structure incomplète")
                    self.test_results.append(("Katula-Page", False))
        else:
            print("❌ Page Katula: Fichier manquant")
            self.test_results.append(("Katula-Page", False))
    
    def generate_report(self):
        """Générer le rapport de test"""
        print("\n📊 RAPPORT DE TEST")
        print("=" * 50)
        
        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)
        
        print(f"Tests réussis: {passed}/{total}")
        print(f"Taux de succès: {(passed/total)*100:.1f}%")
        
        print("\nDétail des tests:")
        for test_name, result in self.test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} {test_name}")
        
        # Sauvegarder le rapport
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        report_path = f"test_report_{timestamp}.txt"
        
        with open(report_path, 'w') as f:
            f.write(f"RAPPORT DE TEST - {timestamp}\n")
            f.write("=" * 50 + "\n")
            f.write(f"Tests réussis: {passed}/{total}\n")
            f.write(f"Taux de succès: {(passed/total)*100:.1f}%\n\n")
            
            for test_name, result in self.test_results:
                status = "PASS" if result else "FAIL"
                f.write(f"{status}: {test_name}\n")
        
        print(f"\n📄 Rapport sauvegardé: {report_path}")
        
        return passed == total
    
    def run_all_tests(self):
        """Exécuter tous les tests"""
        print("🚀 DÉMARRAGE DES TESTS AUTOMATISÉS")
        print("=" * 50)
        
        # Créer un backup pré-test
        if not self.create_pre_test_backup():
            print("❌ Impossible de créer le backup. Arrêt des tests.")
            return False
        
        # Exécuter les tests
        self.test_environment()
        self.test_backend_startup()
        self.test_api_endpoints()
        self.test_katula_page()
        
        # Générer le rapport
        success = self.generate_report()
        
        if success:
            print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
            print("✅ L'application est prête pour la production")
        else:
            print("\n⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
            print("🔧 Vérifiez les erreurs avant de continuer")
        
        return success

if __name__ == "__main__":
    runner = TestRunner()
    runner.run_all_tests()