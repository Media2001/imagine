# A-24 — commandes exactes

Depuis `C:/Users/Ced/imagine`, bash Git Bash du poste Windows. Aucun PHP Windows, aucun Git. Les dossiers scratch doivent être neufs. Interpréteur explicite : `C:/Python314/python.exe` (la commande `python` du PATH est un autre environnement).

## Matrice complète finale

```sh
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 'C:/Python314/python.exe' -B wp/tests/a24/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a24-final-matrice-01
```

Cette commande lance séquentiellement les suites PHP pure et native classique/HPOS en conteneurs jetables, puis tous les `test_*.py` Windows sous UTF-8 et cp1252. Chaque sous-processus Python fixe son encodage. Les deux contextes photographient l’interpréteur, l’encodage effectif et les mêmes sources/dépendances. L’image locale du banc est épinglée dans `wp/tests/a02-audit/run.py` ; aucune préparation d’image globale ni téléchargement.

## Rejouer séparément

```sh
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 'C:/Python314/python.exe' -B -m unittest discover -s wp/tests/a24 -p 'test_*.py' -v
PYTHONIOENCODING=cp1252 PYTHONUTF8=0 'C:/Python314/python.exe' -B -m unittest discover -s wp/tests/a24 -p 'test_*.py' -v
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 'C:/Python314/python.exe' -B wp/tests/a24/run.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a24-rejeu-independant-neuf
```

Pour ne rejouer que PHP pur : même commande `run.py`, autre dossier neuf, ajouter `--unit-only`. Pas de site en argument au banc : il construit exclusivement son site fictif.

## Scellement et réception

Une fois la matrice verte et les quatre documents de livraison finalisés :

```sh
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 'C:/Python314/python.exe' -B wp/tests/a24/seal.py --source=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a24-final-matrice-01
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 'C:/Python314/python.exe' -B wp/tests/a24/verify.py
PYTHONIOENCODING=cp1252 PYTHONUTF8=0 'C:/Python314/python.exe' -B wp/tests/a24/verify.py
```

`seal.py` n’écrase jamais un paquet : il vérifie d’abord en scratch, prouve la réception avec/sans futur PRET sur un miroir jetable, refuse trois mutations et publie `production/A-24/preuves/final` seulement au vert. Le paquet est unique ; tous les essais intermédiaires restent dans le scratch. Un nouveau rejeu se conserve d’abord hors dépôt et se vérifie avec `verify.py --packet=CHEMIN_DU_PAQUET_SCELLE` ; le remplacement d’un paquet publié appartient au parent, jamais à ce worker.

Après intégration des deux lignes de `readme-ajout.txt` par le parent, réception finale du contrat partagé :

```sh
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 'C:/Python314/python.exe' -B wp/tests/a24/verify.py --require-shared
```

Sans cette option, la réception dit explicitement `delta_pending_parent`, jamais « README partagé intégré ». Les autres ajouts au fichier partagé sont ignorés ; seules les deux lignes exactes, uniques et terminées sont contrôlées. PRET reste au parent, ainsi que préparer-image/rejeu globaux.

## Parcours de l’inventaire

Commande opérateur copiée et exécutée avec ses seuls trois arguments sur chaque stockage et chaque contexte :

```sh
python3 wp/outils/bascule/a24/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/expedition-date
```

Sur une copie uniquement anonymisée/vérifiée sous Linux isolé ; pas sur le poste Windows, pas sur la production, pas avant un GO pour tout futur accès au réel. Voir les prérequis et l’interprétation des comptes dans le README propre à A-24.
