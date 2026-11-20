# Site WordPress + WooCommerce jetable et synthétique

> **Reprise du 20 novembre 2026 : lire d'abord `REPRISE.md` et `REPORT.md`.**
> Les sections ci-dessous documentent le passage historique du 19 novembre.
> Les versions gratuites, le chemin optionnel des deux ZIP payants autorisés,
> les reçus `reprise-*` et les nouveaux blocages sont décrits dans `REPRISE.md`.
> Ne pas confondre référence de fidélité avant traitement et preuve après nettoyage.

Ce dossier ne crée **aucun vrai staging**. Il fabrique, teste et détruit des sites entièrement inventés dans un nouveau conteneur Docker privé de réseau. Il ne lit aucune sauvegarde de site et ne monte aucun volume. Le code de `wp/outils/staging/` est uniquement copié pour être testé ; il n'est jamais édité par ce harness.

## Exécution

Depuis la racine du dépôt, avec **Python et Docker déjà disponibles** :

```bash
python wp/tests/staging-e2e/test_harness.py
python wp/tests/staging-e2e/harness.py prepare
python wp/tests/staging-e2e/harness.py fixture-selftest
python wp/tests/staging-e2e/harness.py acceptance
```

Sur Windows, le harness utilise le Docker existant dans la distribution WSL `Ubuntu` si le CLI Docker n'existe pas côté Windows. Il n'installe ni Python, ni PHP, ni Docker sur l'hôte.

- `prepare` est la seule phase autorisée à télécharger : dépendances **publiques** WordPress 6.9, WooCommerce 10.4.3, WP-CLI 2.12.0, image Debian épinglée et paquets Debian. Aucun site n'est installé/importé pendant cette phase. Les trois téléchargements sont contrôlés par les SHA-256 et tailles de `public-dependencies.json`.
- `fixture-selftest` prouve le bon fonctionnement du **jeu de données et de ses oracles indépendants**, pas celui des scripts de staging. Il n'a pas besoin des scripts de staging.
- `acceptance` appelle réellement `neutraliser`, `anonymiser`, puis `verifier` à partir d'une copie des sources nommées. Elle exige leur succès, la propreté observée indépendamment, les invariants métier, le remplacement des mots de passe, puis le refus de chaque résidu réintroduit. Si un prérequis ou une étape échoue, les étapes dépendantes ne sont pas annoncées comme testées.
- Codes de sortie du harness : `0` = contrôles de ce mode terminés ; `2` = échec ou dépendance indisponible. Le journal distingue `FAIL`, `BLOCKED` et `NOT_TESTED`. Un `fixture-selftest` réussi **ne signifie jamais** une acceptance réussie.

L'état réellement constaté est dans `REPORT.md` et `results/`. L'acceptance de la chaîne de staging n'est actuellement **pas validée**.

## Isolation et ressources nommées

Chaque exécution crée seulement un nouveau conteneur `imagine-staging-e2e-<12 hex>`, avec le label `org.imagine.synthetic-e2e=true`, `--network none`, aucune publication/déclaration de port, aucun volume/bind-mount, toutes les capacités Linux retirées et `no-new-privileges`. L'inspection Docker est contrôlée **avant le premier import** et après l'exécution ; une deuxième interface/réseau, un volume ou un port provoquent un refus.

MariaDB et PHP-CLI partagent ce seul conteneur ; MariaDB utilise uniquement `/scratch/mariadb.sock` et `--skip-networking`. Les interfaces et l'absence de listener TCP/IPv6 sont réellement vérifiées. Il n'y a ni serveur HTTP, ni accès navigateur, ni connexion à un service tiers. Les sites n'ont pas d'URL accessible depuis l'hôte.

Les bases autorisées sont exclusivement `imagine_e2e_classic_test` et `imagine_e2e_hpos_test`, créées à neuf dans ce conteneur. Les exports SQL sont générés, importés et détruits **à l'intérieur** du même conteneur. Aucun argument ne permet de fournir une archive ou un SQL provenant d'ailleurs. Le paramètre de sources ne peut viser que le répertoire `wp/outils/staging` de ce dépôt ; seule une liste fermée de fichiers PHP et des trois lanceurs est copiée, sans copie récursive d'un site.

Le conteneur est supprimé en `finally`, puis son absence est contrôlée par son nom exact. Aucun `prune`, aucune lecture ou suppression de conteneur/volume de site réel. Une création ratée n'autorise pas la suppression d'une éventuelle ressource homonyme antérieure.

Les dépendances publiques restent dans `public/` et dans une image `imagine-staging-e2e-public:<id>`, nom et ID consignés dans `dependencies.lock.json`. Ce ne sont pas des données de site. `.dockerignore` exclut tout le dépôt et les journaux du contexte de build, hormis ces dépendances publiques. `evidence/`, `public/` et le reçu local des dépendances sont ignorés ; les reçus nettoyés du passage livré sont conservés dans `results/`.

## Fixtures et pièges

Chaque stockage est testé avec une installation WordPress/WooCommerce réelle et neuve :

- **30 comptes** : un administrateur fictif et 29 clients fictifs ; **30 commandes**, dont une commande invitée ; un produit de magazine inventé.
- États, dates, EUR, montants, quantités, produits, pays BE/FR/DE et méthodes `bacs`/`stripe`/`paypal` sont inventés et servent d'invariants. Aucun plugin Stripe/PayPal ni compte marchand n'est connecté.
- Les identités, téléphones et sociétés sont manifestement inventés. Les comptes propres utilisent `@example.org`. Les emails `@invalid.example` sont exclusivement des pièges intentionnellement hors domaine ; aucune adresse réellement utilisable n'est employée.
- Options imbriquées/sérialisées : faux `sk_live_`, `pk_live_`, `rk_live_`, `whsec_`, `xkeysib-` ; réglages Stripe, PayPal et SMTP entièrement inventés.
- Métadonnées client/commande et table réelle de tokens Woo : faux `cus_`, `pm_`, `src_`, `seti_`, références PayPal factices.
- Email piégé dans compte, adresse de commande, note, formulaire enregistré ; IP de documentation synthétique ; sessions de test.
- Vrais enregistrements Action Scheduler et WP-Cron et un webhook Woo inventé. Ils ne sont jamais exécutés : cron est désactivé, aucun worker ne démarre et le conteneur n'a pas de réseau.

Les fixtures sont créées via les API WordPress/Woo. Les résidus de l'acceptance sont insérés directement par PDO pour éviter de réactiver des plugins ou de modifier d'autres options après nettoyage.

## Oracles et intégration

- `fixture.php`, `mutate.php` : création et injection de données fictives.
- `snapshot.php`, `oracle.php` : contrôle initial avec WordPress/Woo chargés.
- `db-probe.php` : oracle et snapshots **indépendants**, en PDO sans bootstrap WordPress. Cela permet de contrôler les données même lorsque les scripts de staging désactivent les plugins.
- `mail-probe.php` : `PHPMailer::send()` remplacé par un espion mémoire qui ne transmet rien. Le selftest démontre d'abord qu'un site non bloqué atteint bien l'espion. L'acceptance exige ensuite zéro appel de transport. Le filtre anti-email de création des fixtures n'existe que dans le processus de seed et n'est jamais installé durablement.
- `worker-bridge.php`, `subject-adapter.json` : interface réelle `--worker-bridge` des lanceurs existants. Le mot de passe de test est aléatoire, transmis sur stdin, jamais écrit dans une configuration, un journal ou un argument sauvegardé. Le bridge construit uniquement le PDO local synthétique. Son callback de preuve ne charge WordPress qu'après les contrôles du vérificateur ; il utilise la vraie sonde du sujet, jamais des booléens de succès fabriqués.
- `subject-preflight.php` : diagnostic en lecture seule du garde et du schéma, sans lignes privées et sans changement du catalogue sujet.

Les sorties brutes des sujets ne sont pas exportées : seuls leurs codes, empreintes et diagnostics de schéma sans valeurs sont conservés. Chaque passage conserve les empreintes exactes du code du harness et des sources sujet copiées ; un changement pendant la copie provoque un refus.

Les données métier sont déterministes, **pas** les mots de passe aléatoires, identifiants de ressources ou empreintes de dumps. La répétabilité porte sur les contrôles et les invariants. Le reçu local fixe l'ID exact de l'image pour les répétitions ; une reconstruction de l'image n'est pas annoncée comme bit-à-bit reproductible, car les paquets Debian peuvent évoluer. Leur inventaire réellement installé figure dans `results/public-packages.tsv`.

## Limites fermes

Subscriptions et Memberships ne sont ni téléchargés sans licence ni imités par des classes factices. Leur fonctionnement réel, le mode staging Subscriptions, les renouvellements et les droits Memberships restent **non testés**. La sonde réelle peut donc refuser le passage même après correction des données ; cela ne doit jamais être converti en succès.

Ce harness ne valide pas l'orchestrateur réel, le refus de son premier démarrage HTTP, Novamira, une bascule ou des services tiers. Il n'explore aucun vrai staging. Son oracle est ciblé sur les données inventées et les invariants listés, pas une certification générale d'anonymisation de données inconnues.

Références techniques officielles utilisées : `SOURCES.md`.
