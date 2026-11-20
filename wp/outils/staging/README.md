# Traitements de données d’une copie hors ligne

**A-01 reprise, 20/11/2026 : garder le site, retirer le dangereux, signaler l’inconnu.** Le schéma n’est plus une liste fermée ; aucune autorisation d’ouverture n’est produite par ces scripts.

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
    'table_decisions' => [], // Uniquement les décisions explicites de Ced.
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

Le worker peut appeler `Engine(Store, context, prefix, decisions)`, puis `Files(root)->purge()/verify()` ; sans Files, le disque n’est pas couvert. Codes : 0 phase réussie, 1 contrôles de données refusés, 78 erreur/refus de contexte, fichier ou commande. Aucune exception brute ni valeur de ligne ne sort. La commande unique, les statuts distincts imported/verified et le rapport final appartiennent à l’intégration, pas à ces phases.

Les trois phases acceptent aussi `--table-decisions <decisions-ced.json>` après le bridge. JSON indexé par nom exact de table ; chaque entrée contient seulement `action` = `garder`, `vider`, ou `anonymiser` avec `columns` = liste de colonnes exactes. Les colonnes email choisies deviennent `abonne-<id>@example.org` (pseudonyme aléatoire conservé à la relance sans id conventionnel), les autres colonnes choisies sont vidées (zéro pour une valeur numérique), le reste reste intact. Passer les mêmes décisions aux trois phases. API alternative : `context['table_decisions']`. Ne pas fournir simultanément fichier et bridge/contexte. Aucun choix de Ced n’est prérempli ; `{}` signifie aucune décision.

## Couverture et choix de prudence

- Inventaire de toute la base, autres préfixes compris. `schema.php` décrit les traitements connus, pas un refus des inconnus. Tables/colonnes/CPT inconnus gardés et listés. Toute table inconnue avec colonne évoquant email/téléphone/nom/adresse/IP attend une décision de Ced, même vide ; les autres ne bloquent pas. Vues lues/inventoriées, pas réécrites directement. Moteurs/vues/triggers/événements signalés sans définition SQL ; un moteur non transactionnel peut laisser des changements après erreur. Le worker garde la base exclusive et sans événements actifs. Multisite non traité.
- Toutes les options sont gardées. Seuls les champs de credentials connus et motifs de service/paiement sont retirés dans les structures PHP/JSON. Stripe/PayPal usuels et PPCP passent en mode test/sandbox sans clé ; libellés, activation, listes et présentation restent. Objets/références/formats opaques non reconnus restent sans instanciation avec avertissement. Aucune garantie qu’un credential inconnu soit sûr parce qu’il ne ressemble pas à une clé connue.
- État de toutes les extensions conservé, sauf la liste négative lisible `policy.php` : mail/SMTP, emailing, sauvegardes, statistiques/pixels, cache de pages. Désactivations nommées dans le rapport. Formulaire/SEO/ACF ne sont plus soumis à une liste positive. Les rôles existants restent. Les données classiques et HPOS sont traitées simultanément si présentes, sans bootstrap WooCommerce.
- Tokens de paiement, clés API WooCommerce, sessions et métadonnées d’identifiants supprimés. Motifs Stripe/Brevo/PayPal recherchés partout, y compris clés et valeurs JSON/PHP décodables. Les champs Stripe/PayPal de client/paiement sont reconnus même si leur valeur ne porte pas de préfixe.
- Toutes les actions AS en attente ou en cours sont annulées (sur-ensemble volontaire des actions extérieures). Les arguments, schedules opaques, claims et logs sont vidés sans désérialiser les objets de planification. Les actions terminées/échouées sont supprimées ; les autres lignes restent annulées. L’historique AS est donc volontairement sacrifié (pas les statuts/dates des commandes et abonnements). Le comportement d’affichage des schedules vides d’actions annulées dépend de la version AS et reste à tester. Cron stocké vidé, planification/replanification et demandes async AS bloquées ; tout essai d’exécution AS lève une exception.
- Utilisateurs, adresses classiques/HPOS, téléphone, TVA/entreprise, commentaires et notes de commande anonymisés. Pays, statuts, dates/heures, montants, références produits et nom historique de la passerelle sont conservés. Ne pas confondre conserver `payment_method=stripe` avec conserver un token.
- Purge sans lire les contenus : archives/dumps (compressions comprises), sauvegardes/imports/exports/caches/logs de données, dont ai1wm-backups. MU de production conservés/listés ; seuls object-cache.php et advanced-cache.php retirés parmi les drop-ins. Les autres drop-ins et les sources core/plugins/thèmes/MU restent. Verrou de ce lot installé avec hash SHA-256 relu. Liens refusés avant suppression ; worker toujours responsable des jonctions/montages et écrivains concurrents.
- MU : mail false, indexation, passerelles, WCS, Cron, AS async/queue verrouillés. HTTP tout bloqué avant vérification. Après seulement, le worker peut définir `IMAGINE_STAGING_VERIFIED === true` depuis son état persistant vérifié : WP_ACCESSIBLE_HOSTS et filtre MU n’autorisent alors que `*.wordpress.org,*.woocommerce.com`, HTTPS/443. Constantes contradictoires refusées. Pas de userinfo, IP, ports alternatifs ou suffixes frauduleux. Redirections automatiques désactivées : une mise à jour nécessitant une redirection échouera plutôt que suivre un hôte non revalidé. Aucun téléchargement ou changement de pare-feu fait ici. Le MU n’est pas un pare-feu pour SMTP direct/SDK/sockets.
- Les écritures `home`/`siteurl` sont relues avant ET après COMMIT. Les autres écritures utilisent un compare-and-swap transactionnel. `verifier` ré-inventorie et inspecte les valeurs, puis relit encore les données et le disque après la sonde. Aucun bootstrap de sonde n’est exécuté si les données sont déjà refusées.

## Sonde runtime obligatoire

Les cinq blocages du brief : email hors domaine exact example.org dans comptes/commandes/abonnements ; motif connu de clé de service partout ; identifiant Stripe/PayPal client/paiement ; email non coupé par preuve exécutée ; Subscriptions présent non staging. Plus la décision personnelle inconnue. Le reste est averti, pas ajouté comme sixième blocage. Les guards cible/environnement, fichiers et intégrité MU restent des refus de sécurité distincts, jamais affaiblis.

`verifier` exige une closure de sonde exécutée dans le vrai bootstrap WordPress **quarantainé**, sans web normal ni egress. `runtimeProbe()` appelle réellement wp_mail, HTTP et WCS_Staging::is_duplicate_site(), contrôle Cron/AS/passerelles et ne tente pas de transport si le court-circuit n’est pas déjà présent. Subscriptions présent = classe OU fichier du package installé ; package présent sans classe donne false, pas absent. Le plugin actif en base ne peut pas être déclaré absent par la sonde.

Rapport JSON : ok/issues/warnings, unknown_tables (name/columns/rows/personal_columns/decision), unknown_columns, unknown_post_types, active_plugins, disabled_plugins, schema_details et files (noms MU/drop-ins) par CLI. Aucune valeur de ligne, email, identifiant ou credential ; ni définition SQL. Les blocages offline empêchent la sonde, puis données/fichiers sont relus après bootstrap. Le résultat n’est pas un jeton d’ouverture.

Le bridge ne doit jamais charger WordPress lors de son inclusion. Il fournit une closure qui lance le bootstrap isolé approprié au worker puis renvoie la preuve. Un dictionnaire de booléens codé en dur, comme celui des tests unitaires, **n’est pas une preuve runtime utilisable pour un vrai site**. L’autorité de cette preuve appartient au worker ; ces scripts ne fabriquent pas de jeton d’accès ou d’autorisation de démarrer.

## Limites et validations encore nécessaires

Tests synthétiques locaux : `PHP_BIN=<php-8.2+> IMAGINE_TEST_SCRATCH=<scratch-autorise> python wp/tests/staging-data/verify.py`. Résultats et hashes dans `wp/tests/staging-data/results.json`. Exécution réelle PHP/CLI/purge ; Store mémoire, transport PDO et hooks/API doubles, pas preuve WordPress/MySQL réelle. Ce worker n’a utilisé aucun site, archive réelle, compte, secret, service partagé, Git ni déploiement. E2E vrais classiques/HPOS et plugins gratuits enrichis au pair staging-e2e.

L’opérateur a confirmé Subscriptions et Memberships dans la bibliothèque de l’outil. Le pair doit les exercer dans les E2E synthétiques, sans dérogation d’absence. Ce dossier unitaire n’utilise pas ces packages. Filtre WCS : woocommerce_subscriptions_is_duplicate_site ; abonnements classiques posts/postmeta et HPOS, Memberships wc_user_membership. Restent à prouver par les E2E : versions exactes, synchro HPOS, renouvellements/droits, vrais emails court-circuités, AS/Cron et effets des MU/drop-ins gardés. Les options inconnues créées par bootstrap restent avec avertissement.

Limites : secrets inconnus, noms/extensions trompeurs, données en PHP, documents/factures/PDF, métadonnées d’images, médias et texte libre non prouvés absents par regex. Les warnings doivent être relus, pas présentés comme une certification. Tables lues en mémoire ; gros imports susceptibles de demander plus de mémoire. Une décision d’anonymisation sur une vue doit viser ses tables sources. Aucun accès ne découle du simple ok de cette bibliothèque ; les barrières externes du worker restent obligatoires. Contrat pair : HANDOFF-A-01.md.

Sources officielles et mécanismes retenus : [SOURCES.md](SOURCES.md). Exécution des tests : [../../tests/staging-data/README.md](../../tests/staging-data/README.md).
