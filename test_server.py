import http.server
import socketserver
import os

# Changer vers le répertoire du projet
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Serveur simple sur port 8080
handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", 8080), handler) as httpd:
    print("Serveur démarré: http://localhost:8080/frontend/pages/katula/katula-dynamic.html")
    httpd.serve_forever()