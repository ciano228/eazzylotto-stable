# 🚀 Guide de Démarrage Rapide - EazzyCalculator

## ✅ MÉTHODE RECOMMANDÉE : integrated_server.py

**La solution la plus simple et complète** :

```bash
python integrated_server.py
```

Ce script unique :
- ✅ Lance le backend API avec TOUS les routers (verdict, analytics, performance, etc.)
- ✅ Sert le frontend (HTML/JS/CSS)
- ✅ **Tout sur le port 8000**
- ✅ Accès frontend : http://localhost:8000/ai-center.html
- ✅ Accès API : http://localhost:8000/api/verdict/analyze

**C'est tout ce dont vous avez besoin !** 🎯

## URLs Principales

### 🎯 Interface Utilisateur (Frontend - Port 8081)
- **AI Prediction Center** : http://localhost:8081/ai-center.html ⭐
- **Dashboard** : http://localhost:8081/dashboard.html
- **Katula Dynamic** : http://localhost:8081/katula-dynamic.html
- **Smart Input** : http://localhost:8081/smart-input.html
- **Analyse Temporelle** : http://localhost:8081/pages/katula/katula-temporal-analysis.html
- **Win Tracker** : http://localhost:8081/win-tracker.html

### 🔧 API Backend (Port 8000)
- **Base API** : http://localhost:8000/api
- **Verdict AI** : http://localhost:8000/api/verdict/analyze
- **Analytics** : http://localhost:8000/api/analytics
- **Performance** : http://localhost:8000/api/performance

## Démarrage Manuel (Alternative)

Si vous préférez lancer les serveurs séparément :

### Backend (Terminal 1)
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (Terminal 2)
```bash
cd frontend
python -m http.server 8081
```

## Alternative : integrated_server.py

Vous pouvez aussi utiliser le serveur intégré (backend uniquement sur port 8000) :

```bash
python integrated_server.py
```

**Note** : Avec `integrated_server.py`, vous devrez lancer le frontend séparément.

## Arrêt des Serveurs

Avec `start_all.py` : Appuyez sur `Ctrl+C` dans le terminal

Avec le démarrage manuel : Appuyez sur `Ctrl+C` dans chaque terminal

## Résolution des Problèmes

### Port déjà utilisé
Si vous voyez "Le port 8000 est déjà utilisé" ou "Le port 8081 est déjà utilisé" :

**Windows PowerShell** :
```powershell
# Trouver le processus utilisant le port 8000
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess

# Tuer le processus (remplacer PID par l'ID du processus)
Stop-Process -Id PID -Force
```

### Le backend ne démarre pas
- Vérifiez que PostgreSQL est actif
- Vérifiez le fichier `.env` avec les bonnes informations de connexion DB
- Vérifiez que toutes les dépendances sont installées : `pip install -r requirements.txt`

### Le frontend affiche "Connection Refused"
- Vérifiez que le backend tourne bien sur le port 8000
- Vérifiez dans la console du navigateur l'URL exacte qui échoue
- Assurez-vous que le fichier `.js` utilise `http://localhost:8000/api`

## Structure des Ports

| Service | Port | Description |
|---------|------|-------------|
| **Backend API** | 8000 | FastAPI avec tous les routers (verdict, analytics, performance, etc.) |
| **Frontend** | 8081 | Serveur HTTP statique pour les fichiers HTML/JS/CSS |
| **PostgreSQL** | 5432 | Base de données (par défaut) |

## Logs et Debugging

Avec `start_all.py`, les logs sont préfixés :
- `[BACKEND]` en bleu : Logs du backend FastAPI
- `[FRONTEND]` en vert : Logs du serveur frontend

---

**Bon développement ! 🎯**
