#!/usr/bin/env python3
"""
Serveur HTTP simple pour tester l'interface EazzyCalculator
"""
import http.server
import socketserver
import webbrowser
import threading
import time

PORT = 8080

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def start_server():
    """Démarre le serveur HTTP"""
    try:
        # Changer vers le dossier frontend
        import os
        os.chdir('frontend')
        
        with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
            print(f"🚀 Serveur démarré sur http://localhost:{PORT}")
            print(f"🌐 Interface principale: http://localhost:{PORT}/test-interface.html")
            print(f"🎯 Katula Dynamique: http://localhost:{PORT}/katula-dynamic.html")
            print("💡 Appuyez sur Ctrl+C pour arrêter")
            
            # Ouvrir le navigateur après 2 secondes
            def open_browser():
                time.sleep(2)
                webbrowser.open(f"http://localhost:{PORT}/katula-dynamic.html")
            
            threading.Thread(target=open_browser, daemon=True).start()
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    start_server()