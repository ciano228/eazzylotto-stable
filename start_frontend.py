#!/usr/bin/env python3
"""
Serveur HTTP simple pour l'interface Katula
"""
import http.server
import socketserver
import os

PORT = 8080

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
            self.wfile.write(html.encode('utf-8'))
        else:
            super().send_error(code, message, explain)
    def do_GET(self):
        # Redirige / vers /index.html
        if self.path in ('/', ''):
            self.path = '/index.html'
        return super().do_GET()
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    # Changer vers le dossier frontend
    os.chdir('frontend')
    
    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        print(f"🚀 Serveur frontend démarré sur http://localhost:{PORT}")
        print(f"🎯 Katula Dynamique: http://localhost:{PORT}/katula-dynamic.html")
        print("💡 Appuyez sur Ctrl+C pour arrêter")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Serveur arrêté")