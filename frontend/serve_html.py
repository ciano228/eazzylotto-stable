#!/usr/bin/env python3
import http.server
import socketserver
import os

PORT = 8081
DIRECTORY = "."

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serveur démarré sur http://localhost:{PORT}")
        print(f"Répertoire servi: {os.getcwd()}")
        print(f"Accédez à: http://localhost:{PORT}/katula-table-adaptive.html")
        httpd.serve_forever()