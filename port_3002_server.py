"""
Serveur pour http://localhost:3002/katula-dynamic.html
"""
import http.server
import socketserver
import os
import shutil

class KatulaHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()
    
    def do_GET(self):
        # Rediriger katula-dynamic.html vers le bon fichier
        if self.path == '/katula-dynamic.html':
            self.path = '/frontend/pages/katula/katula-dynamic.html'
        super().do_GET()

if __name__ == "__main__":
    PORT = 3002
    
    # Changer vers le répertoire du projet
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), KatulaHTTPRequestHandler) as httpd:
        print(f"Serveur démarré sur le port {PORT}")
        print(f"Page Katula: http://localhost:{PORT}/katula-dynamic.html")
        print("Ctrl+C pour arrêter")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServeur arrêté")
            httpd.shutdown()