# A-21 — candidat complet pour le build final parent

- **Fait** : outil confiné en lecture seule, moteur PHP pur, banc natif classique/HPOS, refus fermés, documentation et vérificateur.
- **Prêt à relire** : candidat `production/A-21/preuves/final` ; aucun `PRET` déposé par l'enfant.
- **À arbitrer par Ced** : rien de nouveau ; aucune intervention sur le réel autorisée ou effectuée.
- **Bloqué** : aucun blocage du périmètre enfant ; préparation de l'image et T-01 global réservés au parent.
- **Ensuite** : parent : `preparer-image.ps1`, T-01 global et décision de dépôt de `PRET`.

## Résultats exécutés

Paquet final unique : `production/A-21/preuves/final`. Pour chacune des consoles Windows **cp1252** et **UTF-8** : **15 assertions PHP pures, 98 contrôles natifs, 7 contrôles runner, tous verts**, plus **7 tests Python, 0 échec**. Ce sont des assertions nommées, pas des tests PHPUnit inventés. PSR-12 strict et syntaxe : sept fichiers PHP, **0 erreur, 0 avertissement**, conteneur supprimé et absence relue.

Interpréteur mesuré : `C:/Python314/python.exe`, **3.14.6**, Windows win32 ; stdout/stderr et locale cp1252, UTF-8 désactivé pour le passage cp1252 ; stdout UTF-8 et mode UTF-8 activé pour l'autre. Chaque sous-processus fixe et décode explicitement son encodage. Les environnements et six commandes réellement exécutées sont dans `windows-matrix.json` et les deux reçus `*-environment.json`.

Le banc natif emploie WordPress 7.0.9, WooCommerce 11.1.1, Subscriptions 9.4.1 et Memberships 1.30.3 ; image compatible A-02 existante, sans téléchargement, port, montage ni réseau. Réemploi inchangé des helpers A-19/A-02 et du bootstrap A-11/Landlock A-12 ; inventaires de dépendances avant/après dans les reçus. L'ancien marquage `A02-real-commercial-fixture` du reçu interne indique ce moteur partagé, pas un passage d'A-02 sur Imagine.

Sur chaque magasin : deux clés (lecture et lecture/écriture), dont une jamais utilisée et une ancienne ; quatre webhooks dont deux actifs (un interne, un externe), un en pause et un désactivé ; lecture native de la connexion au magasin. Canaris de description, secret, fragment, URL, sujet libre, compte et bootstrap absents des rapports et de tous les artefacts exportés. Empreintes de **toutes** les tables, ordonnanceur compris, et fichiers identiques avant/après. Aucun appel HTTP, mail ni planification tenté au nominal ; sondes séparées prouvent refus SQL, noyau fichiers, mail, HTTP et cron. Liens symboliques, six fichiers de remplacement, configuration et exceptions chargées du site : refus fermés, aucune sortie créée.

L'outil de neutralisation **existant, non modifié**, a réellement tourné sur un clone de chaque base fictive : clés retirées, quatre webhooks désactivés et destinations/secrets vidés, jeton magasin effacé, marque relue. Le rapport répond alors « inconnu après neutralisation », jamais zéro/non historique, et la lecture laisse ce clone inchangé.

La commande du mode d'emploi a été copiée et exécutée avec **ses seuls trois arguments** (substitution des chemins fictifs uniquement), sans ajouter de date. Date courante capturée une seule fois, puis rejeu à date figée identique. Les cycles RED→GREEN exécutés (clés, webhooks, projection/neutralisation, lanceur, parcours natif, sujet standard `product.published`, contrat partagé) restent dans le scratch `a21-red-*` / `a21-green-*`, hors dépôt. La première passe de style conservait 27 avertissements ; ils sont corrigés, seule la dernière passe stricte verte est livrée.

## Décisions prises à défaut et limites

- Les sujets standards sont une liste fermée issue du code installé ; les sujets libres et actions personnalisées sont regroupés sous `unknown`, plutôt que de laisser sortir un nom pouvant porter une identité. Pas de regroupement détaillé de ces sujets non standards.
- « Domaine du site » signifie hôte exact, sans DNS ; schéma/port/chemin ignorés, casse/point final normalisés ; un sous-domaine distinct est extérieur. URL douteuse = inconnue, jamais exposée.
- Dernier accès natif dans le fuseau local WordPress ; ancien = strictement avant l'anniversaire des douze mois, distinct de jamais utilisé. Seuil du 29 février rabattu au 28 février. Droits déclarés et connexion locale, pas validation distante ni décision de révocation.
- Marque de neutralisation existante conservée : aucun changement de l'import et aucune reconstruction historique. Schémas anciens, multisite, configuration dynamique, caches/pare-feu et liens non compatibles restent refusés.
- Aucune archive, donnée réelle, instance Imagine, opération Git, Novamira, autre voie ni déploiement. Ni `preparer-image.ps1` ni T-01 global lancés ; qualification de production 6.9.1 non prétendue.

## Fichiers et rejeu

Sources : `wp/outils/bascule/a21/` et `wp/tests/a21/`. Deux lignes seulement ajoutées par patch ciblé à `wp/tests/a02-audit/README.md`, contrôlées par contrat exact, pas par empreinte entière. `readme-ajout.txt` contient ces lignes ; les annexes d'autres lots sont autorisées. `unit.php` s'inclut sans effet de bord, dépend seulement de `Analysis.php`, et reste autodécouvrable par T-02 sans nouvel adaptateur PHPUnit. Preuve séparée `pure-include.json` : copie temporaire de ces deux seuls fichiers, 15 assertions vertes, sans API native chargée, sortie ni nouveau rapport. La première sonde supposait à tort que `/report` n'existait pas dans l'image ; l'oracle corrigé compare son contenu avant/après, sans changement du code testé.

Vérification sans Docker ni écriture :

```text
C:/Python314/python.exe -B wp/tests/a21/verify.py production/A-21/preuves/final
```

Nouveau rejeu complet, sortie scratch neuve :

```text
C:/Python314/python.exe -B wp/tests/a21/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a21-rejeu-matrice-nouveau
```

Le vérificateur lie sources courantes, rapports et empreintes, cas natifs obligatoires, consoles réelles, nettoyage et manifeste. Huit sondes sur copie jetable sont vertes (`verification-probes.json`) : original/restauration acceptés, annexe étrangère acceptée, omission/duplication/fin de ligne du lot refusées, dérive source refusée, cas natif obligatoire manquant refusé même après rescellement de cette copie. Son statut reste `CANDIDAT_GATE_PARENT`, sans allégation de préparation/T-01 global.
