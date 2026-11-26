# A-25 — Reprise / vérification exacte

Depuis `C:/Users/Ced/imagine`, avec `C:/Python314/python.exe` (3.14.6 mesuré). PHP n'est exécuté que par les conteneurs jetables du banc. Aucun Git, Novamira, site réel ou staging existant.

## Contrôle du paquet livré (lecture seule)

```sh
C:/Python314/python.exe -B wp/tests/a25/verify.py
```

Attendu : code 0, `status=CANDIDAT_GATE_PARENT`, `readiness_claimed=false`. Le vérificateur vérifie les sources exécutées, les dépendances communes actuelles, les rapports fermés, les empreintes avant/après, les canaux obligatoires, les reçus de nettoyage, les cinq commandes et le sceau du seul lot. Il ne requiert pas PRET et n'épingle pas son contenu futur.

Après intégration parent des **deux lignes exactes** de `production/A-25/readme-ajout.txt` dans `wp/tests/a02-audit/README.md` :

```sh
C:/Python314/python.exe -B wp/tests/a25/verify.py --require-shared-doc
```

Ce contrôle ne fige ni le fichier partagé entier, ni sa position, ni ses autres lignes. Ce worker n'a pas intégré ce delta.

## Refaire réellement la matrice complète

Le chemin de sortie doit être neuf et hors du dépôt ; remplacer le suffixe uniquement s'il existe déjà.

```sh
C:/Python314/python.exe -B wp/tests/a25/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a25-reprise-unique
C:/Python314/python.exe -B wp/tests/a25/verify.py --unsealed --evidence=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a25-reprise-unique
```

Cette matrice mesure Windows et ses flux ; joue Python puis PHP natif complet classique/HPOS en UTF-8 et cp1252 ; termine par PSR-12 dans un conteneur séparé. Pas de téléchargement ni préparation d'image. Elle exige les images locales et archives fictives déjà employées par A-02/T-01. Un manque produit un rouge, jamais une preuve simulée. `--unit-only` du runner existe pour diagnostic, mais ne remplace pas la matrice de réception.

Le paquet retenu est **uniquement** `production/A-25/preuves/final/`, issu du rejeu réel `a25-matrix-final-01` à code 0 ; aucun autre paquet ne doit être ajouté à `preuves/`. Un rejeu ultérieur reste en scratch tant que le parent n'a pas décidé de remplacer le paquet et de resceller. Il ne faut pas modifier les reçus d'une exécution.

## Parcours de l'outil

```sh
python3 wp/outils/bascule/a25/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/visiteurs-date
```

Ce parcours a été exécuté, en substituant seulement les trois chemins fictifs, sans argument ajouté. Préconditions et limites : `wp/outils/bascule/a25/README.md`. L'opérateur réel et toute porte globale restent au parent/Ced ; ces commandes ne sont aucun accord pour toucher au réel.
