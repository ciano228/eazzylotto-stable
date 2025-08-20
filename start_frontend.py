#!/usr/bin/env python3
"""
Serveur HTTP simple pour l'interface Katula
"""

import http.server
import socketserver
import os
import sys
from dotenv import load_dotenv

# 🔄 Charger les variables depuis .env
load_dotenv()
print(f"🔧 Configuration chargée :")
print(f"   FRONTEND_PORT = {PORT}")
print(f"   FRONTEND_DIR  = {FRONTEND_DIR}")


# 📦 Lire les variables d'environnement
PORT = int(os.getenv("FRONTEND_PORT", "8005"))
FRONTEND_DIR = os.getenv("FRONTEND_DIR", "eazzylotto-final")
frontend_path = os.path.join(os.getcwd(), FRONTEND_DIR)

# 📁 Vérification du dossier
if not os.path.isdir(frontend_path):
    print(f"❌ Dossier '{FRONTEND_DIR}' introuvable. Vérifie le chemin.")
    sys.exit(1)

# 📂 Changement de répertoire
os.chdir(frontend_path)



class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def send_error(self, code, message=None, explain=None):
        if code == 404:
            self.send_response(404)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            html = """
                <html><head><title>404 - Page non trouvée</title></head>
                <body style='font-family:sans-serif;text-align:center;padding:40px;'>
                <h1 style='font-size:3em;color:#fa541c;'>404</h1>
                <h2>Page non trouvée</h2>
                <p>Le fichier ou la page demandée n'existe pas.<br>
                <a href='/index.html' style='color:#1890ff;font-size:1.2em;'>Retour à l'accueil</a></p>
                </body></html>
            """
            try:
                self.wfile.write(html.encode('utf-8'))
            except ConnectionAbortedError:
                print("⚠️ Connexion interrompue avant envoi de la page 404")
        else:
            super().send_error(code, message, explain)

    def do_GET(self):
        if self.path in ('/', ''):
            self.path = '/index.html'
        try:
            return super().do_GET()
        except ConnectionAbortedError:
            print(f"⚠️ Connexion interrompue par le client pour {self.path}")

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        print(f"[REQ] {self.address_string()} - {format % args}")

try:
    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        print(f"[FRONTEND] Serveur démarré sur http://localhost:{PORT}")
        print(f"[INDEX] Principal: http://localhost:{PORT}/")
        print(f"[KATULA] Dynamique: http://localhost:{PORT}/katula-dynamic.html")
        print(f"[ANALYSE] Temporelle: http://localhost:{PORT}/katula-temporal-analysis.html")
        print(f"[MULTI] Univers: http://localhost:{PORT}/katula-multi-universe.html")
        print(f"[LAYOUT] Formes: http://localhost:{PORT}/katula-forme-layout.html")
        print("[INFO] Appuyez sur Ctrl+C pour arrêter")

        httpd.serve_forever()

except OSError as e:
    print(f"❌ Impossible de démarrer le serveur sur le port {PORT} : {e}")
except KeyboardInterrupt:
    print("\n[STOP] Serveur arrêté")
