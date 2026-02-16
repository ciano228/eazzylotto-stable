import http.server
import socketserver
import os

# Changer vers le dossier frontend
os.chdir('frontend')

PORT = 3002
Handler = http.server.SimpleHTTPRequestHandler

print(f"Serveur web démarré sur http://localhost:{PORT}")
print("Ouvrez: http://localhost:3002/katula-dynamic.html")
print("Ou: http://localhost:3002/smart-input-fixed.html")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()