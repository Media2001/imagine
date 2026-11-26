# A-21 — corrections R1 à R4, candidat enfant pour finalisation parent

- **Fait** : sorties PHP supervisées jusqu'à la fin, publication différée, dépendances courantes scellées, option magasin directe documentée, tests IP/IPv6.
- **Prêt à relire** : dernier paquet vert unique `C:/Users/Ced/imagine/production/A-21/preuves/final` ; aucun `PRET` écrit ni modifié par l'enfant.
- **À arbitrer par Ced** : rien ; défauts techniques de la fusion appliqués, aucune action sur le réel.
- **Bloqué** : rien sur le périmètre enfant. Les anciens `FINALISATION.md`, `verification.json`, `manifest.json` racine et `PRET` concernent la remise antérieure : le parent les remplace après ses nouveaux gates ; ils ne prouvent pas ces corrections.
- **Ensuite** : parent : delta exact `readme-delta.txt`, préparation globale, rejeu T-01, puis marqueurs finaux. Aucune dépendance partagée, T-02, verrou, autre voie ni rapport commun modifié.

## Résultats exécutés

Paquet final unique : `production/A-21/preuves/final`. Pour chacune des consoles Windows **cp1252** et **UTF-8** : **18 assertions PHP pures, 172 contrôles natifs (classique + HPOS), 8 contrôles runner**, plus **12 tests Python**, tous verts. Ce ne sont pas des tests PHPUnit. PSR-12 strict et syntaxe : huit fichiers PHP, **0 erreur, 0 avertissement** ; conteneur exact supprimé et absence relue. Inclusion pure rejouée dans chaque runner : 18 assertions, aucune API native, aucune sortie parasite ni modification des rapports.

Interpréteur mesuré : `C:/Python314/python.exe`, **3.14.6**, Windows win32 ; stdout/stderr et locale cp1252, UTF-8 désactivé pour le passage cp1252 ; stdout UTF-8 et mode UTF-8 activé pour l'autre. Chaque sous-processus fixe et décode explicitement son encodage. Les environnements et six commandes réellement exécutées sont dans `windows-matrix.json` et les deux reçus `*-environment.json`.

Le banc natif emploie WordPress 7.0.9, WooCommerce 11.1.1, Subscriptions 9.4.1 et Memberships 1.30.3 ; image compatible A-02 existante, sans téléchargement, port, montage ni réseau. Réemploi inchangé des helpers A-19/A-02 et du bootstrap A-11/Landlock A-12 ; inventaires de dépendances avant/après dans les reçus. L'ancien marquage `A02-real-commercial-fixture` du reçu interne indique ce moteur partagé, pas un passage d'A-02 sur Imagine.

Sur chaque magasin : deux clés (lecture et lecture/écriture), dont une jamais utilisée et une ancienne ; quatre webhooks dont deux actifs (un interne, un externe), un en pause et un désactivé ; lecture native de la connexion au magasin. Canaris de description, secret, fragment, URL, sujet libre, compte et bootstrap absents des rapports et de tous les artefacts exportés. Empreintes de **toutes** les tables, ordonnanceur compris, et fichiers identiques avant/après. Aucun appel HTTP, mail ni planification tenté au nominal ; sondes séparées prouvent refus SQL, noyau fichiers, mail, HTTP et cron. Liens symboliques, six fichiers de remplacement, configuration et exceptions chargées du site : refus fermés, aucune sortie créée.

L'outil de neutralisation **existant, non modifié**, a réellement tourné sur un clone de chaque base fictive : clés retirées, quatre webhooks désactivés et destinations/secrets vidés, jeton magasin effacé, marque relue. Le rapport répond alors « inconnu après neutralisation », jamais zéro/non historique, et la lecture laisse ce clone inchangé.

La commande du mode d'emploi a été copiée et exécutée avec **ses seuls trois arguments** (substitution des chemins fictifs uniquement), sans ajouter de date. Date courante capturée une seule fois, puis rejeu à date figée identique. **TDD réellement exécuté** : échec initial `classic/hpos:supervised_bootstrap:stdout` avec l'ancien lanceur ; échec réel des gardes Action Scheduler, puis vert ; échec de la mutation de rapport au shutdown, puis vert ; deux échecs Python sur JSON à clé dupliquée et tableau de sujets vide, puis vert. La dérive de dépendance a d'abord échoué faute de scellement dans le vérificateur, puis passe avec six mutations de fichiers réels sur copie jetable. Aucun journal RED n'est livré : tous restent dans le scratch A-21.

**R1.** Le superviseur extérieur draine stdout et stderr jusqu'aux deux EOF et à `wait()` ; il reconstruit uniquement les réponses fermées. Le PHP enfant garde Landlock, SQL READ ONLY, fonctions interdites et réseau Docker absent, et n'écrit que dans un sous-dossier privé temporaire. Les rapports ne sont renommés vers la sortie demandée qu'après terminaison et validation canonique JSON/Markdown, textes fermés et hash de l'audit original. Douze fixtures par magasin : écritures stdout/stderr, exit avec/sans texte, faux succès précoce, shutdown stdout/stderr, gros flux, octet non UTF-8, succès dupliqué, rapport supprimé, rapport altéré au shutdown. Pour chacune : refus exact, aucun canari sur les deux flux ni dans les artefacts, sortie non publiée, sous-dossier temporaire retiré, tables et fichiers du site inchangés.

La capture stricte a découvert des `error_log()` natifs d'Action Scheduler sur la file réellement vidée par la neutralisation. Aucun contournement du filtre et aucune liste blanche de ces textes : quatre pré-filtres natifs bloquent la planification avant écriture. La sonde native à `init` prouve les quatre refus, en plus de cron WordPress, mail, HTTP, SQL et noyau fichiers ; compte des planifications forcées = cinq. L'import et les dépendances partagées restent inchangés.

**R2.** Les 48 dépendances exécutées sont comparées aux fichiers courants, pour l'instantané principal et celui de chaque console ; A-11, A-12, audit/A-02, neutralisation et helpers A-19 sont couverts. Le README commun reste exclu des empreintes et contrôlé exclusivement par `readme_contract`. Les trois tests IP/IPv6 conservent le classement par chaîne sans DNS ; même adresse IPv6 écrite autrement = chaîne extérieure, sans adresse publiée. Lecture directe `get_option('woocommerce_helper_data', [])` gardée et testée, sans appel à `WC_Helper`.

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
