# A-23 — reprise et portes du parent

Pas de PRET produit par l'enfant. Pas de `preparer-image.ps1` ni de T01 global
exécuté ici. Le verrou, les fichiers partagés et le rapport d'orchestration
restent au parent. Aucun autre lot n'a été modifié.

## Vérifier le paquet livré

Depuis `C:/Users/Ced/imagine`, shell Bash Windows :

```sh
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 C:/Python314/python.exe -B wp/tests/a23/verify.py
```

Ce vérificateur contrôle les sources propres, les dépendances réellement
exécutées, les logs des commandes, les reçus imbriqués, les rapports fermés,
les empreintes avant/après de toutes les tables et le manifeste exact du paquet.
Il n'écrit rien et ne réclame aucune porte globale. Sa sortie reste
`CANDIDAT_GATE_PARENT`, jamais « PRET ».

## Intégration des deux lignes partagées (parent uniquement)

Appliquer les deux lignes de `production/A-23/readme-ajout.txt`, une fois chacune,
à `wp/tests/a02-audit/README.md`. Puis :

```sh
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 C:/Python314/python.exe -B wp/tests/a23/verify.py --require-shared-doc
```

Le contrat ne compare ni l'empreinte ni le suffixe entier du README partagé ;
il accepte les autres lots avant et après ces deux lignes.

## Rejouer après stabilisation d'A-22, si nécessaire

Utiliser un dossier **nouveau**, hors dépôt. Cette commande lance les deux
contextes Windows complets, classique et HPOS dans chacun, puis PSR-12 :

```sh
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 C:/Python314/python.exe -B wp/tests/a23/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a23-parent-reprise
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 C:/Python314/python.exe -B wp/tests/a23/verify.py --evidence=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a23-parent-reprise --unsealed
```

`--unsealed` sert seulement au nouveau paquet scratch avant sa sélection ;
il n'allège ni les tests ni le contrôle des sources/dépendances. Ne jamais
copier un paquet dont l'une de ces deux commandes échoue. Aucun téléchargement,
montage de site, ouverture de port ou nettoyage global Docker n'est nécessaire.
Chaque runner se supprime par son nom exact, après contrôle de son label ; son
absence est vérifiée. La sortie Python standard du PATH n'est pas celle du
poste de contrôle : garder le chemin explicite 3.14 indiqué ci-dessus.

Si le parent doit remplacer la preuve (les anciens essais ne sont jamais des
preuves livrées), sortir l'ancien `production/A-23/preuves/final` vers un chemin
scratch exact réservé, copier le nouveau dossier vert dans `preuves/final`, puis
rescellage **du lot A-23 uniquement** :

```sh
PYTHONIOENCODING=utf-8 C:/Python314/python.exe -B -c "import importlib.util,json; from pathlib import Path; s=importlib.util.spec_from_file_location('a23_verify','wp/tests/a23/verify.py'); v=importlib.util.module_from_spec(s); s.loader.exec_module(v); Path('production/A-23/manifest.json').write_text(json.dumps(v.inventory(v.PACKAGE),indent=2)+'\n',encoding='utf-8')"
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 C:/Python314/python.exe -B wp/tests/a23/verify.py --require-shared-doc
```

Le manifeste exclut uniquement lui-même, le futur PRET et un éventuel reçu de
finalisation parent `candidate-verification.json`. Les dépendances d'autres
lots ne sont pas photographiées dans ce manifeste ; leurs instantanés d'exécution
séparés sont vérifiés contre l'arbre courant. Les fichiers d'orchestration ne
font jamais partie du sceau.

## Reste au parent

- Lire le besoin Action Scheduler dans `notes.md` ; ne pas introduire un deuxième
  gardien. A-23 utilise déjà le seam A-22 présent, sans le modifier.
- Vérifier A-22 fini et ses sources stabilisées ; rejouer A-23 si ses dépendances
  ont changé après le dernier paquet.
- Intégrer le delta partagé, puis les portes globales imposées par la consigne
  permanente (préparation d'image et rejeu global), sous le verrou parent.
- Déposer PRET seulement après ces portes et le readback parent. Aucun accord
  d'accès au réel ni aucune compatibilité de reconnexion ne découle de ce lot.
