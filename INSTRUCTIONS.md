J'ai corrigé le problème dans `frontend/katula-dynamic.html`.

Pour que les changements prennent effet, veuillez suivre ces étapes :

1.  Assurez-vous que le serveur backend est démarré. Vous pouvez le faire en exécutant la commande suivante dans le terminal, depuis le dossier `c:\Users\User\eazzycalculator\backend`:
    ```
    python main.py
    ```

2.  Servez le frontend en exécutant la commande suivante dans le terminal, depuis le dossier `c:\Users\User\eazzycalculator\frontend`:
    ```
    python -m http.server 8080
    ```

3.  Ouvrez votre navigateur et allez à l'adresse `http://localhost:8080/katula-dynamic.html`.

La page devrait maintenant s'afficher correctement.