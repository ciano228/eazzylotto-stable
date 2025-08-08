#!/usr/bin/env python3
"""
Serveur HTTP simple pour le frontend
"""
import http.server
import socketserver

PORT = 8081

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    import os
    # S'assurer qu'on est dans le bon répertoire
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print(f"📁 Répertoire de travail: {os.getcwd()}")
    print(f"📄 Fichiers disponibles: {os.listdir('.')}")
    
    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        print(f"🚀 Serveur frontend démarré sur http://localhost:{PORT}")
        print(f"🎯 Katula Dynamique: http://localhost:{PORT}/katula-dynamic.html")
        print(f"🧪 Test Simple: http://localhost:{PORT}/test-simple.html")
        print("💡 Appuyez sur Ctrl+C pour arrêter")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Serveur arrêté")