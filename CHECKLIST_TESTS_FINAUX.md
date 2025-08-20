# CHECKLIST TESTS FINAUX - EazzyLotto

## 🚀 Démarrage des Serveurs

### Backend
- [ ] `cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`
- [ ] Vérifier: http://localhost:8000/docs (Documentation Swagger)
- [ ] Vérifier: http://localhost:8000/ (Message de bienvenue)

### Frontend
- [ ] `cd frontend && python -m http.server 3000`
- [ ] Vérifier: http://localhost:3000/index.html (Page de connexion)

## 🔐 Tests d'Authentification

### Inscription
- [ ] Aller sur http://localhost:3000/signup.html
- [ ] Créer un nouveau compte avec:
  - Username: `testuser`
  - Email: `test@example.com`
  - Password: `password123`
- [ ] Vérifier la redirection vers login après inscription

### Connexion
- [ ] Aller sur http://localhost:3000/index.html
- [ ] Se connecter avec les identifiants créés
- [ ] Vérifier la redirection vers dashboard
- [ ] Vérifier l'affichage du nom d'utilisateur dans le header

### Déconnexion
- [ ] Cliquer sur "Logout" dans le dashboard
- [ ] Vérifier la redirection vers login
- [ ] Vérifier que le token est supprimé (localStorage vide)

## 🛡️ Tests de Sécurité

### Pages Protégées
- [ ] Essayer d'accéder à `/dashboard.html` sans être connecté
- [ ] Vérifier la redirection automatique vers login
- [ ] Se connecter et vérifier l'accès au dashboard

### Token JWT
- [ ] Vérifier la présence du token dans localStorage après connexion
- [ ] Tester l'expiration du token (attendre ou modifier manuellement)
- [ ] Vérifier la gestion des erreurs 401

## 📊 Tests Fonctionnels

### Dashboard
- [ ] Vérifier l'affichage des informations utilisateur
- [ ] Tester la navigation vers les différentes sections
- [ ] Vérifier le header universel sur toutes les pages

### Sélecteur de Tirages
- [ ] Aller sur une page avec sélecteur (ex: advanced-journal.html)
- [ ] Tester la sélection de dates
- [ ] Vérifier la validation des dates
- [ ] Tester les filtres de tirages

### Journal Statistique
- [ ] Accéder au journal avancé
- [ ] Tester les filtres par date
- [ ] Vérifier l'affichage des statistiques
- [ ] Tester l'export des données

## 🔧 Tests API (Manuel)

### Endpoints Publics
- [ ] GET http://localhost:8000/ (Accueil)
- [ ] GET http://localhost:8000/docs (Documentation)

### Endpoints d'Authentification
- [ ] POST http://localhost:8000/register (Inscription)
- [ ] POST http://localhost:8000/login (Connexion)

### Endpoints Protégés
- [ ] GET http://localhost:8000/protected (Avec token)
- [ ] GET http://localhost:8000/protected (Sans token - doit échouer)

## 🎯 Tests d'Intégration

### Workflow Complet
- [ ] Inscription → Connexion → Dashboard → Navigation → Déconnexion
- [ ] Vérifier la persistance de session
- [ ] Tester le rafraîchissement de page avec token valide
- [ ] Tester la navigation entre pages protégées

### Gestion d'Erreurs
- [ ] Tester connexion avec mauvais identifiants
- [ ] Tester inscription avec email déjà utilisé
- [ ] Tester accès API sans token
- [ ] Vérifier les messages d'erreur utilisateur

## ✅ Critères de Réussite

- [ ] Tous les serveurs démarrent sans erreur
- [ ] L'authentification fonctionne complètement
- [ ] Les pages protégées sont sécurisées
- [ ] La navigation est fluide
- [ ] Les fonctionnalités métier sont accessibles
- [ ] Les erreurs sont gérées proprement
- [ ] L'interface utilisateur est cohérente

## 🚨 En Cas de Problème

1. Vérifier que les serveurs sont démarrés
2. Vérifier les logs dans les consoles
3. Vérifier la base de données (tables créées)
4. Vérifier les tokens dans localStorage
5. Vérifier les CORS dans la console navigateur