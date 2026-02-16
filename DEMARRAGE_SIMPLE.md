# 🎯 GUIDE DE DÉMARRAGE - EazzyCalculator

## ✅ SOLUTION SIMPLE : integrated_server.py

**Une seule commande pour tout lancer** :

```bash
python integrated_server.py
```

Ce script unique fait **TOUT** :
- ✅ Backend API avec TOUS les routers (verdict, analytics, performance, patterns, etc.)
- ✅ Frontend (sert tous les fichiers HTML/JS/CSS)
- ✅ **Tout sur le port 8881**

## 📱 URLs d'Accès (Port 8881)

### Pages Principales
- **AI Prediction Center** : http://localhost:8881/ai-center.html ⭐
- **Advanced Journal** : http://localhost:8881/advanced-journal.html
- **Katula Dynamic** : http://localhost:8881/katula-dynamic.html  
- **Katula Temporal Analysis** : http://localhost:8881/katula-temporal-analysis.html
- **Smart Input** : http://localhost:8881/smart-input.html
- **Win Tracker** : http://localhost:8881/win-tracker.html

### API Backend
- **Base API** : http://localhost:8881/api
- **Verdict AI** : http://localhost:8881/api/verdict/analyze
- **Analytics** : http://localhost:8881/api/analytics
- **Katula Table** : http://localhost:8881/api/formes/real/mundo/all

## 🔧 Configuration

**Port Unique : 8881**
- integrated_server.py démarre sur le port 8881
- Toutes les pages frontend sont configurées pour ce port
- L'AI Center pointe maintenant vers le port 8881

## ⚠️ Notes Importantes

1. **Un seul serveur suffit** : `integrated_server.py` fait backend ET frontend
2. **Ne lancez PAS** `start_all.py` en même temps - c'est redondant !
3. **Port 8881 = Standard** pour integrated_server.py dans votre projet

## 🛑 Arrêt du Serveur

Appuyez sur `Ctrl+C` dans le terminal

## ✅ Vérification Rapide

Après démarrage, testez :

```powershell
# Vérifier que le port 8881 est actif
Get-NetTCPConnection -LocalPort 8881

# Tester l'API
Invoke-WebRequest http://localhost:8881/api/analytics/katula/table/mundo

# Ouvrir dans le navigateur
start http://localhost:8881/ai-center.html
```

## 🐛 Résolution des Problèmes

### "Port already in use"
```powershell
# Trouver le processus utilisant le port 8881
Get-Process -Id (Get-NetTCPConnection -LocalPort 8881).OwningProcess

# Arrêter le processus
Stop-Process -Id <PID> -Force
```

### Pages ne chargent pas
- Vérifiez que PostgreSQL est actif
- Vérifiez le fichier `.env`
- Redémarrez integrated_server.py

---

**Bon développement ! 🚀**
