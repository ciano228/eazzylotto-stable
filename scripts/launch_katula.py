import subprocess
import time
import os
import sys

def kill_port_process(port):
    """Tuer le processus utilisant un port spécifique"""
    try:
        result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        for line in lines:
            if f":{port}" in line and "LISTENING" in line:
                parts = line.split()
                if len(parts) > 4:
                    pid = parts[-1]
                    print(f"Arret du processus {pid} sur le port {port}")
                    subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
                    return True
    except Exception as e:
        print(f"Impossible d'arreter le processus sur le port {port}: {e}")
    return False

def start_backend():
    """Démarre le serveur backend PostgreSQL"""
    print("=== DEMARRAGE BACKEND POSTGRESQL ===")
    
    # Tuer les processus existants
    kill_port_process(8000)
    time.sleep(2)
    
    # Démarrer le backend
    os.chdir("backend")
    cmd = [sys.executable, "servers/server_postgres_simple.py"]
    
    print(f"Commande: {' '.join(cmd)}")
    
    # Modifier le port dans le serveur pour éviter les conflits
    with open("servers/server_postgres_simple.py", "r") as f:
        content = f.read()
    
    # Remplacer le port 8081 par 8000 pour le backend
    content = content.replace('port=8081', 'port=8000')
    content = content.replace('localhost:8081', 'localhost:8000')
    
    with open("servers/server_postgres_simple.py", "w") as f:
        f.write(content)
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Attendre le démarrage
    for i in range(15):
        time.sleep(1)
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print(f"Erreur backend: {stderr}")
            return None
        
        # Test connexion
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 8000))
            if result == 0:
                print("Backend PostgreSQL demarre sur http://localhost:8000")
                sock.close()
                os.chdir("..")
                return process
            sock.close()
        except:
            pass
    
    print("Timeout backend")
    os.chdir("..")
    return None

def start_frontend():
    """Démarre le serveur frontend"""
    print("=== DEMARRAGE FRONTEND ===")
    
    # Tuer les processus existants
    kill_port_process(8081)
    time.sleep(2)
    
    # Démarrer le frontend
    os.chdir("frontend")
    cmd = [sys.executable, "-m", "http.server", "8081"]
    
    print(f"Commande: {' '.join(cmd)}")
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Attendre le démarrage
    for i in range(10):
        time.sleep(1)
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print(f"Erreur frontend: {stderr}")
            return None
        
        # Test connexion
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 8081))
            if result == 0:
                print("Frontend demarre sur http://localhost:8081")
                sock.close()
                os.chdir("..")
                return process
            sock.close()
        except:
            pass
    
    print("Timeout frontend")
    os.chdir("..")
    return None

def main():
    print("=== EAZZYCALCULATOR KATULA DYNAMIC ===")
    
    # Démarrer backend PostgreSQL
    backend_process = start_backend()
    if not backend_process:
        print("ERREUR: Impossible de demarrer le backend PostgreSQL")
        return
    
    # Démarrer frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("ERREUR: Impossible de demarrer le frontend")
        backend_process.terminate()
        return
    
    print("\n=== APPLICATION DEMARREE ===")
    print("Backend PostgreSQL: http://localhost:8000")
    print("Frontend: http://localhost:8081")
    print("Katula Dynamic: http://localhost:8081/katula-dynamic.html")
    print("API Health: http://localhost:8000/api/health")
    print("\nAppuyez sur Ctrl+C pour arreter...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nArret des serveurs...")
        backend_process.terminate()
        frontend_process.terminate()
        print("Serveurs arretes")

if __name__ == "__main__":
    main()