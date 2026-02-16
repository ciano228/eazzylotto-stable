#!/bin/bash
# Script de mise à jour GitHub pour EazzyCalculator v2.0.5
# Usage: ./update_github.sh

echo "=========================================="
echo "  MISE À JOUR GITHUB - EazzyCalculator"
echo "  Version 2.0.5"
echo "=========================================="
echo ""

# Vérifier si on est dans le bon répertoire
if [ ! -f "integrated_server.py" ]; then
    echo "❌ ERREUR: Exécuter depuis la racine du projet"
    exit 1
fi

echo "📋 Étape 1: Vérification de l'état Git..."
git status

echo ""
read -p "Continuer avec le commit? (o/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Oo]$ ]]; then
    echo "❌ Annulé par l'utilisateur"
    exit 1
fi

echo ""
echo "📦 Étape 2: Ajout des fichiers modifiés..."
git add integrated_server.py
git add frontend/assets/js/katula-dynamic.js
git add frontend/katula-dynamic.html
git add ETAT_APPLICATION_2025.md
git add README.md

echo ""
echo "✅ Fichiers ajoutés"
git status

echo ""
echo "💾 Étape 3: Commit des changements..."
git commit -m "v2.0.5: Dénominations multiples + UX univers sélectionné

✅ Support complet dénominations avec slash (rainbow 6/rainbow 9)
✅ Endpoint /api/formes/real/{universe}/all corrigé
✅ Bandeau coloré avec icônes dynamiques par univers
✅ Atténuation chips non sélectionnés
✅ Surbrillance chip actif avec bordure bleue
✅ Affichage nombre de formes par univers

Fichiers modifiés:
- integrated_server.py (endpoint formes/all)
- katula-dynamic.js (v11: API adapter + UX)
- katula-dynamic.html (version script v=11)
- ETAT_APPLICATION_2025.md (documentation complète)"

echo ""
echo "🚀 Étape 4: Push vers GitHub..."
git push origin main

echo ""
echo "🏷️  Étape 5: Création du tag v2.0.5..."
git tag -a v2.0.5 -m "Version 2.0.5 - Dénominations multiples + UX améliorée"
git push origin v2.0.5

echo ""
echo "=========================================="
echo "  ✅ MISE À JOUR GITHUB TERMINÉE"
echo "=========================================="
echo ""
echo "📝 Prochaines étapes:"
echo "1. Vérifier sur GitHub que tous les fichiers sont présents"
echo "2. Créer une Release sur GitHub (optionnel)"
echo "3. Mettre à jour la documentation si nécessaire"
echo ""
echo "🎉 Version 2.0.5 publiée avec succès!"
