# A-12 — propagation des refus A-11, 26 novembre

Aucun nouvel inventaire ni modèle éditorial : le runtime A-11 corrigé reste l'unique bootstrap en lecture seule. Les refus de fichier de remplacement/cache/pare-feu/lien et de constante non reproduite sont maintenant transmis avec leur nom, y compris par le lanceur confiné A-12. La prévalidation de configuration utilise le même contrôle fermé. Tests d'attente adaptés au diagnostic nommé, sans rendre le refus permissif.

Rejeu réel hors réseau sur banc A-02 classique et HPOS : **7 contrôles unitaires, 118 natifs, 7 runner**, tous PASS ; **6 contrôles de style**, PHPCS PSR-12 strict code 0, 0 erreur et 0 avertissement. Vérificateur : **41 contrôles PASS**, code 0. Confinement Landlock réel, compte SQL lecture seule et garde serveur même avec root ; aucun email/HTTP/cron lancé, empreintes base/fichiers/schedulers inchangées. Aucun accès Imagine.

Paquet unique courant : `production/A-12/preuves/final`. L'ancien paquet est déplacé intact hors du dépôt dans le scratch Hermes, pas réécrit. Les dépendances A-02/A-11 sont liées à leur exécution figée et à leur invariance avant/après, pas épinglées comme fichiers actuels d'A-12. Le manifeste courant ne scelle que les fichiers A-12. Les preuves de style ont été réellement régénérées sur les sources finales, pas recopiées du paquet précédent.

Commandes :

```text
python wp/tests/a12/run.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a12-corrections-26nov-0233
python wp/tests/a12/style.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a12-corrections-26nov-0233/style
python wp/tests/a12/verify.py production/A-12/preuves/final
```

La préparation T01 réellement exécutée pour les corrections A-11/A-12 est conservée ; aucun paquet Composer nouveau. Les limites CLI, piles standard et absence de GO réel restent inchangées. Pas de modification d'A-10 clos pour son ancien vérificateur de réception intégrée à plusieurs lots.
