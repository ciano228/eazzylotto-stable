#!/usr/bin/env python3
"""
Serveur frontend pour EazzyCalculator
"""
import os
import socketserver
import http.server
from urllib.parse import urlparse

PORT = 8081

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Handler HTTP avec support CORS"""
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        """Log personnalisé"""
        print(f"[FRONTEND] {format % args}")

if __name__ == "__main__":
    # Ne pas essayer de changer de répertoire, on est déjà dans frontend
    print(f"[INFO] Démarrage du serveur frontend sur le port {PORT}")
    print(f"[INFO] Répertoire de travail: {os.getcwd()}")
    
    try:
        with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
            print(f"[INFO] Serveur démarré sur http://localhost:{PORT}")
            print("Appuyez sur Ctrl+C pour arrêter")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur...")
    except Exception as e:
        print(f"[ERREUR] {e}")
        raise
