# Traitements de données d’une copie hors ligne

Périmètre : `neutraliser`, `anonymiser`, `verifier`, bibliothèque PHP 8.2+, adaptateur PDO MySQL et un mu-plugin. **Aucun import, orchestration, démarrage de site, changement d’infrastructure, bascule, Novamira ou autorisation d’accès n’est effectué ici.** Un code 0 ne constitue pas une réception du staging.

## Contrat avec le worker

Ces commandes ne chargent **jamais** `wp-load.php`, `wp-config.php`, un export ou une sauvegarde. Elles reçoivent une connexion déjà confinée par le worker. Avant de les appeler, le worker doit :

- garder web/PHP normal et tous les consommateurs de queues arrêtés, bloquer DNS/SMTP/HTTP et les autres sorties au niveau système ; aucun filtrage WordPress ne bloque `curl`, sockets, SDK ou mail direct ;
- réserver une base exclusive dont le nom finit par `_staging` ou `_test`, avec un compte limité à cette base et une connexion locale (socket/loopback), sans réplication ni consommateur externe ;
- terminer la restauration et régénérer une configuration **staging** sans secrets de production, désactiver WP-Cron avant tout bootstrap ; aucune réutilisation du `wp-config` copié ;
- fournir la liste complète des hôtes de production (tous les alias), mettre la copie sous un hôte `.test`, `.localhost`, `.invalid` ou `localhost` ;
- réécrire `home` et `siteurl` **sans démarrer WordPress**, puis les lire après écriture. Si l’une des URL est encore de production, cette bibliothèque refuse d’y toucher. Ce prérequis résout volontairement la tension entre « changer l’URL » et « ne jamais exécuter ces scripts sur une URL de production » ;
- matérialiser une racine isolée dont le fichier `.imagine-staging-offline` contient exactement les octets `OFFLINE_COPY\n` (LF). Ce marqueur et les attestations du contexte ne prouvent pas à eux seuls l’isolation ; elle reste la responsabilité du worker ;
- fournir des sources PHP de confiance, sans anciennes configurations/secrets codés en dur. Aucun archive/import/dump ne doit être exposé par un autre montage ou chemin ; la bibliothèque ne visite jamais le répertoire source de sauvegarde.

Les commandes exigent `WP_ENVIRONMENT_TYPE=staging` dans leur environnement de processus. Le bridge PHP de confiance du worker, hors de la racine importée, renvoie :

```php
return [
    'context' => [
        'environment' => 'staging',
        'isolated' => true,
        'restored' => true,
        'database' => 'synthetic_staging',
        'target_url' => 'https://synthetic.test',
        'production_hosts' => ['production.invalid'], // Fictif : remplacer par l’inventaire du worker.
    ],
    'prefix' => 'wp_',
    'store' => $store, // Imagine\Staging\Store, ou new PdoStore($pdo, $context).
    'root' => $root,   // Racine de la copie, jamais le dossier des sauvegardes.
    'probe' => $probe, // Closure différée, non exécutée en chargeant le bridge.
];
```

Les classes sont déjà chargées quand le bridge est inclus. Pas de mot de passe, DSN, chemin de site réel, données ni secret dans ce dépôt. Le worker obtient lui-même le PDO sans écrire ses identifiants dans le bridge. Un bridge est du **code exécutable de confiance**, pas un fichier de la copie à importer.

Interfaces indépendantes, à appeler par le worker existant (pas de lanceur global dans ce lot) :

```text
php wp/outils/staging/neutraliser --worker-bridge <bridge-autorise.php>
php wp/outils/staging/anonymiser --worker-bridge <bridge-autorise.php>
php wp/outils/staging/verifier --worker-bridge <bridge-autorise.php>
```

Pour `anonymiser`, passer uniquement le nouveau mot de passe administrateur par **stdin**, une ligne de 20 à 72 octets, suivie de EOF. Pas d’argument secret, variable d’environnement secrète, fichier de secret, historique shell ou capture de stdin. L’administrateur `imagine-test-admin` est créé **après restauration**, son hachage bcrypt seul est stocké, puis son existence et son hachage sont relus. À chaque relance les autres mots de passe sont rendus inconnus et les sessions/app passwords sont supprimés ; l’idempotence est sémantique, pas une égalité des sels bcrypt.

Le worker peut aussi appeler `Engine(Store, context, prefix)` directement, `Files(root)->purge()/verify()`, puis les trois méthodes de l’Engine. Sans `Files`, la vérification de la bibliothèque seule ne couvre pas le disque : préférer les commandes. Les codes sont 0 (phase réussie), 1 (contrôles de `verifier` échoués), 78 (refus/erreur). Les sorties JSON ne contiennent ni ligne de base, identifiant, adresse, chemin, secret ou exception brute. Pas de fichiers de rapport produits.

## Couverture et choix de prudence

- Inventaire de **toute la base**, y compris les tables d’un autre préfixe : table/colonne non cataloguée, vue, trigger, événement SQL ou moteur non InnoDB => refus. Multisite non pris en charge. `schema.php` est fermé ; il ne prétend pas couvrir chaque version d’extension.
- Types de contenus fermés : un CPT de formulaire inconnu bloque. Les tables inconnues de formulaires, logs, extensions payantes ou intégrations bloquent au lieu d’être ignorées. Ajouter un adaptateur exige une fixture synthétique, une revue de schéma et des tests de pièges.
- Suppression des options hors liste positive : réglages Stripe/PayPal/Brevo/SMTP, licences, sécurité, analytics, sauvegarde, webhooks, transients et autres intégrations disparaissent. Aucun secret opaque n’est considéré sûr parce qu’il ne ressemble pas à `sk_live`. **Des réglages fonctionnels d’extensions disparaissent aussi** ; ce compromis volontaire n’est pas une migration de configuration.
- Seuls WooCommerce, Subscriptions et Memberships peuvent rester dans `active_plugins`. Aucun plugin inconnu n’est réactivé. Les rôles WP existants sont conservés. Les données métier classiques et HPOS sont traitées simultanément lorsqu’elles sont présentes ; aucun bootstrap/CRUD de WooCommerce n’est nécessaire pour modifier la copie arrêtée.
- Suppression des tokens de paiement, clés API WooCommerce et sessions ; retrait des métadonnées d’identifiants/tokens. Motifs de clés Stripe/Brevo et identifiants Stripe/PayPal recherchés dans toutes les valeurs, y compris les structures PHP sérialisées et JSON. Objets PHP, références et structures ambiguës échouent sans instancier de classe.
- Toutes les actions AS en attente ou en cours sont annulées (sur-ensemble volontaire des actions extérieures). Les arguments, schedules opaques, claims et logs sont vidés sans désérialiser les objets de planification. Les actions terminées/échouées sont supprimées ; les autres lignes restent annulées. L’historique AS est donc volontairement sacrifié (pas les statuts/dates des commandes et abonnements). Le comportement d’affichage des schedules vides d’actions annulées dépend de la version AS et reste à tester. Cron stocké vidé, planification/replanification et demandes async AS bloquées ; tout essai d’exécution AS lève une exception.
- Utilisateurs, adresses classiques/HPOS, téléphone, TVA/entreprise, commentaires et notes de commande anonymisés. Pays, statuts, dates/heures, montants, références produits et nom historique de la passerelle sont conservés. Ne pas confondre conserver `payment_method=stripe` avec conserver un token.
- Purge récursive sans ouvrir les contenus : archives/dumps selon extensions (y compris compressions), sauvegardes/imports/exports/caches/journaux dans les emplacements de données. Suppression des anciens mu-plugins et drop-ins, copie du seul mu-plugin de ce lot, hash SHA-256 relu. Les sources comme `wp-includes/cache.php` et les classes PHP d’import WooCommerce ne sont pas des caches/imports de données et sont préservées. Tout lien symbolique rencontré fait échouer l’inventaire avant suppression ; le worker doit également garantir l’absence de jonctions/montages et d’écrivain concurrent.
- Le mu-plugin refuse un environnement non staging, verrouille `pre_wp_mail` (retour false), `pre_http_request` (WP_Error), indexation, passerelles, WCS, WP-Cron, AS async et queue. Ce n’est pas un pare-feu et il n’est pas un mu-plugin de production.
- Les écritures `home`/`siteurl` sont relues avant ET après COMMIT. Les autres écritures utilisent un compare-and-swap transactionnel. `verifier` ré-inventorie et inspecte les valeurs, puis relit encore les données et le disque après la sonde. Aucun bootstrap de sonde n’est exécuté si les données sont déjà refusées.

## Sonde runtime obligatoire

`verifier` échoue sans closure de sonde, ou si l’un des résultats demandés manque. Le worker doit exécuter la closure dans un bootstrap WordPress **quarantainé**, après les contrôles offline, sans serveur web normal et sans egress. `runtime-probe.php::runtimeProbe()` fournit les appels : vrai `wp_mail()` court-circuité, vrai HTTP WP bloqué, `WCS_Staging::is_duplicate_site()`, environnement, Cron, filtres AS/runner et passerelles WooCommerce. La fonction ne charge pas WP elle-même et ne tente rien si le court-circuit mail/HTTP n’est pas déjà présent. L’absence de Subscriptions ne devient jamais un succès « non applicable ».

Le bridge ne doit jamais charger WordPress lors de son inclusion. Il fournit une closure qui lance le bootstrap isolé approprié au worker puis renvoie la preuve. Un dictionnaire de booléens codé en dur, comme celui des tests unitaires, **n’est pas une preuve runtime utilisable pour un vrai site**. L’autorité de cette preuve appartient au worker ; ces scripts ne fabriquent pas de jeton d’accès ou d’autorisation de démarrer.

## Limites et validations encore nécessaires

Les tests livrés sont des **unitaires PHP/Python**, avec Store mémoire, moteur de hooks fictif et fichiers artificiels. Ils n’ont ouvert aucune sauvegarde, vraie base, vrai journal, vrai staging ou secret. L’adaptateur PDO est syntaxiquement validé mais **n’a pas été exercé contre un serveur MySQL/MariaDB**. Aucun WordPress/WooCommerce réel n’a été démarré ici. Les tests de hooks ne prouvent donc pas une exécution réelle de `wp_mail`.

Aucune licence Subscriptions/Memberships n’a été utilisée. La neutralisation WCS vise le filtre officiel `woocommerce_subscriptions_is_duplicate_site`; les abonnements classiques sont `posts/postmeta` (`shop_subscription`), les abonnements HPOS utilisent les tables de commandes ; Memberships utilise `wc_user_membership` dans `posts/postmeta`. Il reste à tester, sur environnement jetable licencié : les versions exactes, CPT/HPOS avec synchro active, renouvellements, droits Memberships, emails réels court-circuités, AS et WP-Cron réels. Les options recréées par les versions installées doivent être cataloguées explicitement ; une option inconnue créée pendant la sonde bloque aussi. Aucun succès complet n’est revendiqué avant ces essais.

Les fichiers à nom/extension mensongers, secrets codés dans du PHP, documents/factures/PDF, métadonnées d’images, médias personnels et textes libres arbitraires ne sont pas une anonymisation sémantique prouvable par regex. Le worker doit n’exposer que des sources de confiance et des médias revus, et fournir un inventaire fermé des artefacts importés ; **ne pas ouvrir le staging si ce prérequis n’est pas satisfait**. Cette bibliothèque n’atteste pas l’absence de données personnelles dans des octets qu’elle n’inspecte pas. Les formats propriétaires/formulaires inconnus nécessitent un traitement dédié, pas une exception permissive.

Sources officielles et mécanismes retenus : [SOURCES.md](SOURCES.md). Exécution des tests : [../../tests/staging-data/README.md](../../tests/staging-data/README.md).
