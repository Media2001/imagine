# Lanceur isolé C-01

À lancer depuis `C:/Users/Ced/imagine`, avec Python standard déjà disponible :

```sh
python wp/tests/numeros-runner/run.py prepare
python wp/tests/numeros-runner/run.py run --name final
python wp/tests/numeros-runner/run.py close
```

`--filter nomDuTest` est disponible pour un cycle RED/GREEN ciblé.
`--name` doit être un nom de passage local simple, sans séparateur de chemin.
Ne réutiliser un nom que pour remplacer volontairement ce passage de preuve.

## Frontière autorisée

- Docker existant de l'outil de staging, via `wsl.exe -d Ubuntu -- docker`.
- Image publique **synthétique** déjà présente
  `imagine-staging-e2e-public:644662e9cc4f`, PHP 8.2 avec extracteur ZIP.
  Son identifiant d'image exact est enregistré ; aucune image n'est reconstruite.
- Conteneur possédé par ce lanceur : `imagine-c01-<id>`, étiquette
  `org.imagine.c01-runner=true`, entrée `sleep` et non le démarrage de l'image.
- Aucun service partagé modifié ; aucune commande ni connexion à un site.
  Aucun WordPress, MySQL ou serveur web démarré ; le lanceur vérifie que le seul
  processus de fond avant la suite est `sleep`.
- Aucun montage d'hôte, volume Docker, port déclaré/publié, privilège ou socket.
  Toutes les capacités retirées, `no-new-privileges`, mémoire/CPU/PID limités.
- `prepare` télécharge le PHAR Composer public et vérifie son SHA-256 public,
  copie la bibliothèque seulement et exécute `composer install` dans le conteneur
  (plugins et scripts désactivés). Le réseau de préparation est ensuite détaché.
  `composer.lock` est rapatrié ; ni PHAR ni `vendor/` n'est installé sur l'hôte.
- `run` refuse un réseau attaché, un montage/port/privilège inattendu ; il recopie
  les sources, vérifie leurs SHA-256 à l'intérieur du conteneur et exécute
  **réellement** `composer test`, `composer lint`, la syntaxe PHP de tous les
  fichiers et `composer validate --strict --no-check-publish` sans réseau.
- `close` vérifie l'étiquette et l'isolation avant de supprimer uniquement son
  conteneur et de relire son absence. Rien n'est purgé globalement.

## Preuves et erreurs

Preuves sous `production/C-01/tests/` : journaux, XML JUnit, reçus JSON contenant
versions, codes de sortie, empreintes de la bibliothèque et du lanceur,
préparation Composer et nettoyage. Le fichier `runner-state.json` ne contient
que le nom/ID d'image ; il est supprimé au nettoyage, jamais un secret.

Si la préparation échoue après création, exécuter `close` avant de réessayer.
Si l'image existante ou Docker n'est pas disponible, ne rien installer sur
l'hôte : signaler le blocage et ne pas déposer de marqueur PRET non étayé.
L'image PHP CLI minimale essayée initialement n'avait ni zip ni unzip ; aucun
paquet n'a été ajouté à l'hôte. Le lanceur final réutilise l'image synthétique
outillée existante, sans démarrer ses services.
