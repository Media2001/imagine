# Finalisation parent du 2026-11-26T19:21:25.123860+01:00

**Prêt à relire, non clos.** Préparation commune réellement relancée, rejeu global UTF-8/cp1252 vert : **1 126 tests, 35 550 assertions ; 16 outils, 311 contrôles ; zéro échec, erreur ou ignoré**. Le dernier arbre inclut les changements concurrents de la voie 2, sans modification de notre part.

Preuves parent : `files/rapports/2026-11-26-19h21-verification/`. Les passages enfant ci-dessous sont historiques : leurs portes parent en attente sont maintenant accomplies. Les matrices A23/A24/A25 ont été réellement rejouées après la correction A22 de 17 h 53 ; les premiers essais parent interrompus/rouges restent en scratch, pas dans les paquets retenus. Aucun Git, archive Imagine, compte réel, Novamira, déploiement ou autorisation sur le réel.

---

# A-23 — reprise et portes du parent

Pas de PRET produit par l'enfant. Pas de `preparer-image.ps1` ni de T01 global
exécuté ici. Le verrou, les fichiers partagés et le rapport d'orchestration
restent au parent. Aucun autre lot n'a été modifié.

## Finalisation bornée du 26 novembre 2026

Le parent a figé les dépendances après les autres lots. Le contrôle initial
`--require-shared-doc` rendait code 1 uniquement pour
`utf8:current_dependencies` et `cp1252:current_dependencies`.
La matrice existante, non modifiée, a réellement été rejouée de 17 h 10 min 11 s
à 17 h 13 min 53 s ; ses cinq commandes rendent code 0. Le contrôle scratch
non scellé rend ensuite **65 PASS, zéro FAIL, code 0**.

Commandes de rejeu exécutées depuis `C:/Users/Ced/imagine` :

```sh
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 C:/Python314/python.exe -B wp/tests/a23/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a23-final-matrix-20261126-1710
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 C:/Python314/python.exe -B wp/tests/a23/verify.py --evidence=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a23-final-matrix-20261126-1710 --unsealed
```

Environnement supplémentaire du wrapper réel : `PYTHONDONTWRITEBYTECODE=1`
et `TMPDIR`, `TEMP`, `TMP` fixés chacun à
`C:/Users/Ced/AppData/Local/hermes/cache/scratch`. Le wrapper, ses horodatages,
les codes de fin réels et les photographies avant/après sont en
`C:/Users/Ced/AppData/Local/hermes/cache/scratch/a23-finalisation-20261126-1710/` :
`replay.py`, `replay-receipt.json`, `baseline.json`, `1.stdout`, `1.stderr`,
`2.stdout`, `2.stderr`, `before-verify.json`.

Sélection exécutée uniquement après ces deux codes 0 :

```sh
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 C:/Python314/python.exe -B C:/Users/Ced/AppData/Local/hermes/cache/scratch/a23-finalisation-20261126-1710/select.py
```

Ce script vérifie les sources/dépendances courantes, sort l'ancien dossier
exact vers `a23-finalisation-20261126-1710/previous-final`, puis copie le nouveau
paquet dans `production/A-23/preuves/final`. Son reçu `selection.json` constate
109 fichiers identiques après copie et la conservation exacte de l'ancien
paquet hors dépôt. Aucune preuve d'exécution ni empreinte de dépendance n'est
réécrite. Aucun correctif de code ou de test n'a été nécessaire.

Par console Windows 3.14.6 explicitement mesurée : 23 tests Python, 34 contrôles
purs, 14 du standard, 160 natifs classique/HPOS et 9 runner, tous verts.
PSR-12 : zéro erreur et zéro avertissement. Les contextes complets sont UTF-8
(`PYTHONUTF8=1`) et cp1252 (`PYTHONUTF8=0`).

Après les dernières écritures documentaires, scellement et readback finaux :

```sh
PYTHONIOENCODING=utf-8 C:/Python314/python.exe -B -c "import importlib.util,json; from pathlib import Path; s=importlib.util.spec_from_file_location('a23_verify','wp/tests/a23/verify.py'); v=importlib.util.module_from_spec(s); s.loader.exec_module(v); Path('production/A-23/manifest.json').write_text(json.dumps(v.inventory(v.PACKAGE),indent=2)+'\n',encoding='utf-8')"
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 C:/Python314/python.exe -B wp/tests/a23/verify.py --require-shared-doc
PYTHONIOENCODING=cp1252 PYTHONUTF8=0 C:/Python314/python.exe -B wp/tests/a23/verify.py --require-shared-doc
```

Leurs sorties et codes réels sont conservés dans le scratch de finalisation et
le reçu `candidate-verification.json` réservé hors sceau. Le README partagé
était déjà intégré par le parent ; l'enfant ne le modifie pas.

**La porte parent d'A-23 demeure en attente.** Le candidat conserve exactement
`CANDIDAT_GATE_PARENT`, `readiness_claimed=false`, `parent_preparation=pending`
et `parent_global_T01=pending`. Ce travail enfant ne revendique ni nouveau
PRET, ni préparation commune, ni T01 global, ni réception parent. Les portes
annoncées à 17 h 06 pour les autres lots ne sont pas transposées à A-23.
La preuve porte uniquement sur le banc fictif ; elle ne décide ni reconnexion
ni accès au réel. Si une dépendance change ensuite, rejouer avant réception.

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
