"""
Serveur HTTP simple pour katula-dynamic.html
"""
import http.server
import socketserver
import os

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

if __name__ == "__main__":
    PORT = 3000
    
    # Changer vers le répertoire du projet
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"Serveur démarré sur le port {PORT}")
        print(f"Page Katula: http://localhost:{PORT}/frontend/pages/katula/katula-dynamic.html")
        print("Ctrl+C pour arrêter")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServeur arrêté")
            httpd.shutdown()