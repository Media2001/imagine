# A-18 — Candidat corrigé du 26 novembre 2026, sans PRET

**Fait :** R1, R2, R3 et mémoïsation corrigés, tests réellement rejoués. **Prêt à relire :** candidat A-18 uniquement, non clos. **À arbitrer par Ced :** rien touchant au réel ; question de provenance pour Imagine ci-dessous. **Gate restante :** le parent reconstruit l’image commune puis vérifie et scelle ; aucun PRET déposé. **Ensuite :** remise au parent, aucune autre voie ni lot traité.

## Corrections et TDD

- **R1 :** les deux paires de tables présentes sont lues indépendamment du flag HPOS. Provenance fermée `store=classique/hpos`, `commun` pour comptes/options. Les comptes sont ceux des **valeurs physiquement conservées**, pas des commandes logiquement dédupliquées. Preuves natives : IBAN seulement dans le magasin inactif, commande et abonnement, dans les deux sens ; même clé présente dans les deux magasins, deux groupes distincts. RED constaté dans les deux modes, puis GREEN.
- **R3 :** séparateurs multiples, tabulations, CR/LF, U+00A0 et U+202F dans l’extraction IBAN/carte. Douze régressions `scan()` → `groups()` ont échoué avant correction puis réussi ; preuve native mixant ces séparateurs sur chaque magasin.
- **R2 :** recherches carte et registre séparées, réexamen des frontières de groupes entiers après échec. Six régressions chiffres voisins en préfixe/suffixe ont échoué avant correction puis réussi ; six gardes interdisent les fragments arbitraires d’un nombre continu ou attaché à des lettres. Au plus une occurrence par forme et par ligne.
- **Mémoïsation :** le registre JSON est partagé en mémoire par `iban()` et `scan()`. Test réel sur copie jetable de la classe : après le premier chargement, remplacer son registre par `{}` ne change plus les appels suivants. RED puis GREEN observés.

Tous les RED et essais intermédiaires restent hors dépôt : `C:/Users/Ced/AppData/Local/hermes/cache/scratch/a18-corrections-20261126-101833/` (`red-r1`, `red-r3`, `red-r2`, `red-memo`, leurs GREEN). Seule la dernière matrice verte est publiée.

## Preuves et commandes réelles

Paquet **unique** `production/A-18/preuves/final` : cp1252 à la racine, UTF8 sous `utf8/`. Par console : **37 assertions PHP, 100 assertions natives classic/HPOS, 7 gardes runner, 3 tests Python**, tous verts ; PHPCS PSR12 strict : **0 erreur, 0 avertissement**. Vérificateur candidat : **36/36 contrôles**, décompte calculé dans `check_count`, identique à `production/A-18/verification.json`. L’ancien JSON et l’ancien vérificateur comptent en réalité **34 tous deux**, mesurés : le 33 annoncé en relecture n’est pas reproduit. Les deux contrôles supplémentaires imposent les nouvelles régressions unitaires dans chaque console.

Interpréteurs réellement découverts : `python` = venv Hermes **3.11.15** ; `C:/Python314/python.exe` = Windows natif **3.14.6**, non 3.14.7. Aucun renommage des preuves ni installation. Locale cp1252, stdout/stderr cp1252 et UTF8=0 mesurés, puis contexte UTF8 distinct ; chaque sous-processus Windows a son décodeur explicite. Environnements et quatre commandes détaillés dans `preuves/final/windows-matrix.json`.

Commandes finales réellement exécutées (toutes code 0) :

```text
C:/Python314/python.exe -B wp/tests/a18/windows_matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a18-corrections-20261126-101833/matrix-final-v2
C:/Python314/python.exe -B wp/tests/a18/run.py --style-only --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a18-corrections-20261126-101833/style-final-v2
C:/Python314/python.exe -B wp/tests/a18/verify.py production/A-18/preuves/final --candidate
```

Sans `--candidate`, le vérificateur a également été exécuté : **code 1 attendu**, seul échec `preparer_image_actual_exit`. `parent-gate.json` porte explicitement le build et la vérification indépendante restant au parent. L’ancien reçu de préparation a été retiré, non réutilisé. Ni `preparer-image.ps1`, ni T01, ni le build commun n’ont été exécutés/modifiés ici.

Deux stockages natifs, formes valides/invalides et bruitées, option sérialisée, jeton natif, trois fichiers exports et dossiers inconnus dont un vide, année exclue. Canaris absents de toutes les sorties et de tous les fichiers produits ; inotify confirme qu’aucun média n’est ouvert. Refus symlinks fichier/dossier par code seul, six drop-ins fermés, sorties disjointes, PHP non confiné refusé. Tentatives SQL/mail/HTTP/cron/fichiers bloquées ; empreintes de **toutes** les tables et fichiers identiques, y compris Action Scheduler. Neutralisation : « inconnu après neutralisation », jamais zéro. Confinement sans réseau/montage/port ; cleanup des seuls conteneurs créés, absence relue. Runtime commun et dépendances inchangés selon les reçus.

Fichiers de code modifiés : `Forms.php`, `Inventory.php`, `README.md` sous `wp/outils/bascule/a18/`. Tests modifiés : `inside.py`, `seed.php`, `unit.php`, `run.py`, `verify.py` ; ajouté : `windows_matrix.py` sous `wp/tests/a18/`. Sortie finale et manifestes régénérés dans `production/A-18/`. Le README partagé n’est pas modifié ; ses deux lignes A-18 déjà présentes restent exactes, détails corrigés dans le README propre au lot. `readme-ajout.txt` reste la paire existante. Aucun verrou, Git, A-19, archive, réel, Novamira, staging Imagine ou déploiement.

## Décision prudente et écart à faire relire

Défaut prudent confirmé par la fusion : `server_rule_file_present` = présence d’un nom technique fermé ; `reading_denied=null` = protection effective inconnue. Aucun contenu média/configuration serveur ni requête HTTP. **Écart à reporter par Claude dans `docs/ecarts.md`** (non modifié ici conformément au périmètre) : contradiction du brief A-18, oui/non effectif exigé contre interdiction d’ouvrir les fichiers. Aucun blocage ni demande de GO au réel.

Arbitrage de la file de 10 h 30 appliqué : marque de neutralisation conservée telle quelle ; cette question relève de notre import, pas d’Imagine. L’import demeure inchangé. Le défaut sur les règles serveur est acquis et Claude a déjà reporté l’écart ; aucune action dans `docs/` ni question sur ce point.

Les colonnes sont indépendantes et leur somme n’est pas un nombre de lignes distinctes ; une ligne contenant plusieurs formes peut alimenter deux colonnes. **Rectification factuelle de la fusion : un seul nombre de 11 chiffres ne peut pas être une carte ici (minimum 13).** Cette limite et le cumul possible sur une même ligne sont documentés et testés, sans élargir artificiellement le détecteur carte.

## Autres limites

Formes et sommes de contrôle seulement, pas preuve d’existence ni identité. Clés hors syntaxe technique masquées sous `autre`. Structures IBAN figées et sources historiques inchangées (89 pays, SWIFT v101 via données python-stdnum ; pas de fraîcheur nouvelle revendiquée). PHP seulement via `run.py` et ses helpers de conteneurs jetables. Le rejeu du code A-18 ne se confond pas avec les extensions T01 ; la reconstruction commune puis le contrôle parent restent requis avant PRET. Le passage sur une copie Imagine vérifiée appartient à l’opérateur autorisé.
