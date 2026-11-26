# A-27 — Réception réservée au parent

**État : candidat construit, sans PRET et sans preuve native inventée.** Écritures du worker limitées à `wp/outils/bascule/a27/`, `wp/tests/a27/`, `production/A-27/`. Chemin effectif du dépôt : `C:/Users/Ced/imagine` (le « voie1 » du contexte désigne la voie, pas un dossier existant). Aucun Git, Docker, WSL, PHP Windows, site, compte, archive de production, Novamira, fichier partagé ou verrou utilisé par ce worker.

## Ce qui est réellement exécuté

- RED Python initial : trois échecs attendus faute de lanceur A-27 ; puis GREEN des mêmes refus.
- RED de la liaison au magasin de l'audit : la suite alors à 17 tests a donné 16 réussites et un échec (`test_published_storage_bound_to_audit`). La condition manquante a été ajoutée puis la suite complète est passée.
- Les mutations Python rejouables ôtent séparément la garde du magasin et celle du Markdown dans des copies jetables : elles reproduisent l'admission indue, sans mutation du dépôt.
- La dernière matrice Windows mesurée et ses empreintes sont dans `verification-python.json`. Elle exécute réellement la même suite en UTF-8/mode UTF-8 actif puis cp1252/mode UTF-8 inactif ; les sondes conservent exécutable, version, encodages, locale et mode UTF-8.
- Sur cette machine l'interpréteur découvert est **C:/Python314/python.exe, Python 3.14.6**, pas 3.14.7 annoncé dans le contexte. Aucune installation ni substitution.

Ces résultats ne valent PAS preuve PHP, native classique/HPOS, DB/fichiers immuables, code commercial installé ni réseau Docker. Ces preuves attendent les commandes ci-dessous. Les suites fournies ne sont pas déclarées exécutées.

## Commandes exactes — après sérialisation parent uniquement

Exécuter depuis `C:/Users/Ced/imagine`. Chaque sortie doit être neuve ; changer uniquement le suffixe si elle existe. Ne jamais lancer ces commandes en concurrence avec A-26 ou une autre porte Docker/WSL. Les runners imposent `--parent-serialized`, ne téléchargent rien, ne montent rien et ne traitent que des fixtures fictives jetables.

### 1. Préparation commune (parent)

```sh
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
```

Le worker ne l'a pas lancée. Le parent adapte lui-même toute intégration de la suite dans son orchestrateur global et colle lui-même les **deux** lignes de `readme-ajout.txt` au mode d'emploi partagé ; aucun fichier commun n'a été changé ici.

### 2. Style PHP détenu A-27 (si nécessaire, avant gel)

```sh
C:/Python314/python.exe -B wp/tests/a27/style.py --parent-serialized --fix --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a27-parent-style-fix-01
```

`--fix` n'écrit que les fichiers PHP A-27, jamais les dépendances. Un statut non nul ou le moindre avertissement PSR-12 reste à corriger ; ne pas le transformer en succès. La vérification stricte est rejouée sans `--fix` par la matrice. Toute correction du code invalide les anciens reçus : refaire la matrice entière ensuite.

### 3. Paquet unique final : Python et natif dans les deux consoles

```sh
C:/Python314/python.exe -B wp/tests/a27/matrix.py --include-native --parent-serialized --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a27-parent-final-01
C:/Python314/python.exe -B wp/tests/a27/verify.py --evidence=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a27-parent-final-01
```

Exiger les deux codes zéro, tous les contrôles PASS et aucun stderr inattendu. Le premier code zéro ne suffit pas si le vérificateur échoue. Le paquet contient cinq commandes mesurées (Python UTF-8, natif UTF-8, Python cp1252, natif cp1252, PSR-12) ; les commandes Docker sont sérielles. Le runner natif réemploie le banc A-02/A-23/A-25 et l'image déjà épinglée, avec le cœur Woo/WCS installé dans chaque fixture. Les paquets sous licence déjà autorisés du banc fictif sont seuls réutilisés ; aucune sauvegarde du site existant n'est ouverte.

Le code natif installé est inspecté par `standard.php` **avant** le bootstrap du sujet A-27. Le banc couvre : carte valide/expirée, SEPA, PayPal, référence sans jeton, canari ; quatre états vivants et exclusion manuel/annulé ; deuxième jeu à cinq occurrences par cas ; expirations UTC et six mois en PHP pur ; purge réelle par l'import inchangé sur clone fictif ; tous les comptes neutralisés inconnus ; empreintes de toutes les tables et des fichiers avant/après ; HTTP/mail/cron/Action Scheduler bloqués ; réseau `none`, aucun montage/port ; canaris stdout, stderr, affichage/arrêt, shutdown et fichiers JSON/Markdown/supplémentaires ; témoins sans gardien strictement confinés et jetés.

`red-unit.json` est un **témoin de mutation attendu en échec**, produit dans le conteneur jetable en changeant CC→autre puis restauré avant GREEN. Ce n'est pas un résultat GREEN ni une simulation native. Le parent doit réellement l'exécuter ; le worker ne l'a pas fait.

### 4. Variante diagnostique PHP pur seulement (facultative)

```sh
C:/Python314/python.exe -B wp/tests/a27/run.py --parent-serialized --unit-only --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a27-parent-pure-01
```

Elle ne remplace pas la matrice complète ni les deux magasins.

### 5. Archivage et dernières portes

Après code figé et vérificateur vert : conserver **un seul** paquet final dans `production/A-27/preuves/final/` (copie des preuves réelles du scratch parent), puis rejouer `verify.py --evidence=production/A-27/preuves/final`. Les preuves Python partielles du worker restent un reçu de travail distinct, pas un deuxième paquet natif. Rejouer aussi les portes communes du parent après le dernier gel (préparation image, T-01 global dans les deux encodages et vérificateurs A-20/A-21/A-22 si leur dépendance commune a changé). Les commandes exactes de l'orchestrateur global appartiennent au parent ; aucun contrat global n'est inventé par A-27.

Deux relectures, fusion et vérification indépendante de paquet restent nécessaires. `PRET`, README partagé, rapport global et clôture appartiennent au parent. **Ce worker ne les pose pas.** Un vert technique n'est jamais un GO sur la copie du réel ; la réserve A-22 et la décision de Ced sur le comptage de la source restent distinctes.

## Décisions prises à défaut / limites explicites

- Tous les nombres demandés deviennent inconnus sur la copie marquée neutralisée : l'import purge jetons et références. Aucun compte utile n'est récupéré artificiellement. Le choix d'un procédé de comptage de la source reste à Ced, sans accès d'agent au réel.
- Liste fermée des passerelles : un identifiant non reconnu, même syntaxiquement technique, est `autre` ; pas de suffixe libre exporté. Types et champs de rapport fermés, audit lié par empreinte/date/magasin.
- L'horloge est celle de l'audit A-02, pas celle du lancement A-27 ; six mois calendaires à date/heure UTC, jour borné au mois cible. Aucune échéance individuelle ne sort.
- Plusieurs instruments candidats ou schéma opaque : illisible/liaison inconnue. Pas de choix bancaire, pas de conversion Bancontact→SEPA, pas de test de renouvellement. Schémas connus locaux seulement ; tout autre champ reste non interprété.
- La consultation documentaire officielle est faite ; la preuve sur le **code installé** est une porte parent fournie mais non exécutée ici (interdiction Docker/WSL/PHP hôte respectée). Ne pas remplacer cette limite par une empreinte supposée.
- Le garde Python protège les canaux et les fichiers. Il ne transforme pas un code WordPress arbitrairement malveillant en programme mathématiquement fiable : on réutilise les hypothèses du banc A-22, le compte SQL SELECT-only, la transaction lecture seule et Landlock.
