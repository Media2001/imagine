# A22 — commandes et frontière parent

Toutes ces commandes ont été lancées depuis le poste Windows, avec `C:/Python314/python.exe` (3.14.6 mesuré). PHP ne tourne que dans les conteneurs jetables des runners existants. Les matrices fixent elles-mêmes les environnements enfants UTF-8 et cp1252, `PYTHONUTF8` et le scratch Hermes. Un nom de sortie déjà pris est refusé : pour un nouveau rejeu, remplacer le suffixe par un nom neuf.

## Commandes ayant produit les reçus sélectionnés

```text
C:/Python314/python.exe -B C:/Users/Ced/imagine/wp/tests/a22/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a22-matrix-final-07
C:/Python314/python.exe -B C:/Users/Ced/imagine/production/A-22/style.py C:/Users/Ced/AppData/Local/hermes/cache/scratch/a22-style-final-07
C:/Python314/python.exe -B C:/Users/Ced/imagine/wp/tests/a20/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a20-shared-final-04
C:/Python314/python.exe -B C:/Users/Ced/imagine/wp/tests/a21/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a21-shared-final-04
C:/Python314/python.exe -B C:/Users/Ced/imagine/wp/tests/a21/style.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a21-shared-style-final-04
```

`windows-matrix.json` contient les commandes enfants **réellement exécutées**, leur encodage et leur code de sortie. Les journaux de tests, reçus natifs, instantanés de sources/dépendances et noms exacts des conteneurs sont conservés dans le paquet de chaque lot. Les verdicts courants sont dans les notes/checkpoints, pas déduits de cette liste de commandes.

Rejeu ciblé d’une banque close, avec les mêmes assertions et les canaris additionnels, par exemple :

```text
C:/Python314/python.exe -B C:/Users/Ced/imagine/wp/tests/a22/run.py --lot=A18 --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a22-a18-reprise-NOUVEAU
```

Les lots autorisés sont A02, A03, A10, A11, A12, A14 à A21. A13 reste un lecteur de fichier hors ligne sans bootstrap WordPress. A02/A10 ne chargent pas non plus le WordPress du site ; leurs suites existantes sont néanmoins rejouées. Le tableau de qualification est dans `notes.md`.

## Assembler et sceller le paquet A22

Après la vraie sortie verte de la matrice, publication d’un paquet neuf (un paquet déjà présent est refusé) :

```text
C:/Python314/python.exe -B C:/Users/Ced/imagine/production/A-22/finalise.py --matrix=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a22-matrix-final-07 --style=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a22-style-final-07
```

Après les dernières écritures des documents et reçus, scellement sans aucun gate parent :

```text
C:/Python314/python.exe -B C:/Users/Ced/imagine/production/A-22/finalise.py --seal-only
```

## Vérifier les paquets livrés, sans Docker et sans écrire PRET

```text
C:/Python314/python.exe -B C:/Users/Ced/imagine/wp/tests/a20/verify.py C:/Users/Ced/imagine/production/A-20/preuves/final
C:/Python314/python.exe -B C:/Users/Ced/imagine/wp/tests/a21/verify.py C:/Users/Ced/imagine/production/A-21/preuves/final
C:/Python314/python.exe -B C:/Users/Ced/imagine/wp/tests/a22/verify.py C:/Users/Ced/imagine/production/A-22/preuves/final
```

Aucun vérificateur n’impose l’absence perpétuelle de PRET. La présence future du marqueur est testée sur un miroir **jetable**, jamais créée dans le dépôt par l’enfant. Le candidat reste un constat d’exécution de l’enfant ; il ne revendique aucun gate global.

## Au parent uniquement

- Ajouter au README partagé la ligne exacte de `production/A-22/readme-ajout.txt`. Ne pas refaire les lignes A20/A21 ni la ligne d’option directe A21 déjà préservées.
- Exécuter la préparation globale et le rejeu T01 sur les dernières sources, puis décider des PRET. Les anciennes gates ne couvrent pas ces changements.
- Facultatif : passer `--parent-proof=C:/chemin/preuve-parent.json` au vérificateur. Ce JSON contient `sources` (l’objet exact de `sources.json` du paquet), `preparation` et `T01` (chemins de vrais reçus JSON à `exit_code: 0`, avec des contrôles `checks`/`tests` tous verts). A22 vérifie aussi alors la ligne exacte du README partagé. Aucun reçu parent n’est synthétisé ni exécuté par cet enfant.

Images et dépendances natives doivent déjà exister ; aucun téléchargement, reconstruction globale, archive Imagine, accès réel, compte, Novamira, déploiement ou Git dans ces commandes.
