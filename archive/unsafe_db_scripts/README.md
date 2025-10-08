Archive: scripts pouvant modifier `table_de_katula`

Date: 2025-10-08
Auteur: action automatique (archivage sur demande)

But
- Conserver hors racine/projets actifs les scripts qui peuvent drastiquement modifier la base `katooling_main_system`.
- Permettre restauration / revue sans perdre l'historique git (fichiers déplacés sur une branche dédiée).

Liste (candidates) :
- backend/complete_katula_table.py
- backend/regenerate_katula_table.py
- backend/rebuild_katula.py
- backend/populate_variable_geometry.py
- backend/final_update.py
- backend/update_with_backup.py
- backend/update_safe.py
- backend/fix_sequence.py
- backend/update_bd_granque_tome.py
- backend/fix_katula_simple.py
- backend/clean_and_sync.py
- backend/reorganize_table.py
- backend/debug_universe_population.py
- extend_alignment_full.py
- extrapolate_full_bd.py
- correct_chip_alignment.py
- align_chips_logic.py
- regenerate_katula_table.py
- update_database.py
- final_update.py

Pourquoi archiver
- Ces scripts : suppriment ou recréent `table_de_katula`, insèrent massivement des données aléatoires ou heuristiques, et créent des backups nommés `table_de_katula_backup_*`.
- Ils doivent rester disponibles pour audit et pour reproduction en environnement de test, mais ne devraient pas être dans le flux de déploiement ou exécutés sur production.

Comment restaurer / revenir en arrière
- Cette action a été faite sur une branche `chore/archive-unsafe-scripts` (commit). Pour revenir:
  git checkout main
  git merge --abort  # si un merge est en cours
  # Pour restaurer les fichiers sur main (non recommandé sans revue):
  git checkout chore/archive-unsafe-scripts -- archive/unsafe_db_scripts/*

Recommandations
- Garder ces scripts dans `archive/unsafe_db_scripts/` et ajouter clairement en début de chaque script une protection :

  import os
  if os.getenv('ENV') == 'production':
      raise SystemExit('Refuse to run in production')

- Ajouter une politique dans `CONTRIBUTING.md` : "Les scripts qui touchent aux données de production ne doivent être exécutés qu'en environnement test/production only after explicit backup and approval".
- Ajouter une CI pipeline qui exécute en mode lecture-seule les smoke-tests avant tout merge.

Notes
- Aucune opération sur la base de données n'a été réalisée ici. Seules des opérations git et fichier ont lieu (déplacement des fichiers dans l'arborescence du dépôt).
- Après archivage, je vais committer sur la branche `chore/archive-unsafe-scripts` et afficher un résumé des fichiers déplacés et des fichiers non trouvés (si certains fichiers listés étaient absents).