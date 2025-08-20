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
    # Changer vers le dossier frontend
    if os.path.exists('frontend'):
        os.chdir('frontend')
        print("[INFO] Changement vers le dossier frontend")
    else:
        print("[ERREUR] Dossier frontend non trouvé")
        exit(1)
    
    try:
        with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
            print(f"[FRONTEND] Serveur démarré sur http://localhost:{PORT}")
            print(f"[INDEX] Principal: http://localhost:{PORT}/")
            print(f"[KATULA] Dynamique: http://localhost:{PORT}/katula-dynamic.html")
            print(f"[ANALYSE] Temporelle: http://localhost:{PORT}/katula-temporal-analysis.html")
            print(f"[MULTI] Univers: http://localhost:{PORT}/")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("[FRONTEND] Serveur arrêté par l'utilisateur")
