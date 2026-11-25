# A-04 — `mettre-a-jour`

Outil de bascule **hors ligne**, piloté par un plan explicite, sans compte WooCommerce, sans téléchargement depuis le site, sans Novamira, sans changement de thème ni nettoyage A-05. Python orchestre ; PHP et WP-CLI ne s'exécutent que dans le conteneur cible pendant la qualification. Linux, Python 3.11+, PHP 8.2+, WP-CLI et les extensions de départ sont requis.

## Commande opérateur

Depuis le conteneur autorisé, en conservant l'arborescence `wp/outils/` hors de la racine web :

```sh
python3 /opt/imagine/wp/outils/bascule/mettre-a-jour \
  --wp-path=/copie-fictive/site \
  --plan=/travail-fictif/plan.json \
  --backup=/travail-fictif/sauvegarde.json \
  --state=/travail-fictif/etat-a04
```

Ces chemins sont des exemples fictifs, pas des destinations existantes. Le même appel reprend la même exécution ; ne pas déplacer, réécrire ou effacer son état. Sorties : `0` terminé sous maintenance ; `75` arrêt contrôlé ; `1` refus/anomalie. Un succès ne lève **jamais** la maintenance et n'autorise pas une mise en ligne.

`--stop-after=woocommerce` s'arrête après la copie des fichiers de ce composant et avant ses migrations. Ajouter `--pause` attend à cet endroit en conservant les verrous ; cela sert aussi aux essais d'interruption. Ne pas lancer une autre commande WordPress pendant cette pause.

## Préalables obligatoires

- Site gelé : au **premier démarrage**, maintenance WordPress `.maintenance` récente (moins de dix minutes), et arrêt **opérateur** des autres queues, cron système, déploiements et écritures. À la reprise, un checkpoint valide lié au site, au plan et au `wp-config.php`, plus les octets conformes du MU A-04 persistant, autorisent le rafraîchissement de `.maintenance` sous les deux verrous, avant tout bootstrap. MU absent ou modifié : refus, jamais réinstallation implicite. Le script ne prétend pas administrer les services externes.
- Copie staging : marqueur A-01 `status=verified`, `offline_verified=true`, `runtime_probe_passed=true`, octets du MU de sécurité conformes à la référence du dépôt, puis sondes effectives mail/HTTP/paiements/cron/Action Scheduler. Un marqueur seul ne suffit pas.
- Base et fichiers sauvegardés hors du site **après résolution canonique des deux chemins**, fichiers non vides, SHA-256 conformes, date de création ni future ni vieille de plus de **six heures**. Tout lien symbolique dans le fichier ou l'un de ses répertoires parents est refusé, même s'il vise hors du site ; un chemin contenant `..` ne peut pas contourner le contrôle d'emplacement. La présence et l'intégrité des fichiers sont contrôlées, **pas leur restaurabilité** : Ced doit avoir vérifié séparément une restauration complète.
- Absence de drop-ins base/cache, de liens symboliques dans les chemins concernés, versions de départ exactes, pas de downgrade. Archives locales et SHA-256 figés ; version interne du paquet et exigences WordPress/PHP contrôlées avant copie. Espace libre : somme décompressée des paquets + 128 Mio.

Le fichier de sauvegarde est un JSON à clés `site` (chemin canonique exact), `created_at` (timestamp UTC), `database` et `files` ; ces deux dernières clés contiennent chacune `path` absolu et `sha256`. Le script ne crée aucune sauvegarde de site réel et n'en restaure aucune automatiquement.

## Plan strict

Racine : `schema: "imagine-a04-v1"`, `site_status: "verified-staging"`, `steps: [...]`. Les quatre premières étapes contiennent **exactement** les clés de cet exemple ; les suivantes ajoutent obligatoirement `audit` (voir ci-dessous) :

```json
{
  "component": "woocommerce",
  "main_file": "woocommerce.php",
  "before": "11.0.1",
  "after": "11.1.1",
  "archive": "/paquets-fictifs/woocommerce.zip",
  "sha256": "REMPLACER_PAR_LE_SHA256_VERIFIE_DU_PAQUET",
  "adapter": "woocommerce",
  "hooks": []
}
```

L'exemple est volontairement non exécutable tant que le hash n'est pas renseigné. Les quatre premières étapes sont obligatoirement `core`, `woocommerce`, `woocommerce-subscriptions`, `woocommerce-memberships` ; `adapter` porte le même nom. Cible du cœur : une **version exacte 7.0.x**, jamais `latest`.

`main_file` est **déclaré explicitement** : chemin POSIX relatif au dossier de l'extension dans le paquet et sur disque, par exemple `fiction-entry.php` pour le composant `a04-rest`. Le fichier n'a pas à porter le nom du dossier. Aucun chemin absolu, `.`/`..`, antislash, URL ou suffixe autre que `.php` n'est accepté ; les liens de destination restent refusés. Pour `core`, `main_file` vaut obligatoirement `null` (métadonnées dans `wp-includes/version.php`). La même identité sert aux métadonnées du ZIP et aux versions installées avant/après/reprise. Les anciens plans sans cette déclaration sont refusés : préparer un nouveau plan pour une **nouvelle** exécution ; ne jamais réécrire le plan d'un checkpoint en cours.

Les étapes suivantes nomment explicitement chaque autre extension et n'acceptent **que** `adapter: "bootstrap-only"`, réservé aux mises à jour **auditées sans migration de base différée**. Elles ajoutent une trace `audit` à clés exactes `component` (identique à l'étape), `path` (fichier d'audit absolu hors liens symboliques), `sha256` (empreinte exacte du fichier) et `conclusion: "no-deferred-database-migrations"`. Le fichier non vide est relu et vérifié avant bootstrap. Ce lien obligatoire ne certifie pas la qualité de l'audit humain. Le balayage générique reste délibérément `(?!)` pour ces composants ; il n'est pas élargi à des tâches légitimes.

**Aucun adaptateur additionnel n'est accepté au-delà des quatre premiers**, même qualifié : `validate_plan` le refuse par conception. Une extension nécessitant une migration spécifique est exclue des plans actuellement acceptés ; son support demanderait un lot d'extension de l'outil et une qualification dédiés. `hooks` est réservé et doit rester vide : aucune commande, URL, requête SQL ou fonction arbitraire n'est acceptée dans le plan.

Ordre : le cœur satisfait les minima du nouveau Woo ; Woo fournit les API et schémas des deux premium ; Subscriptions précède l'intégration Memberships ; les autres suivent. Aucun changement de stockage classique/HPOS n'est entrepris.

## Migrations et vérification

- Cœur : commande native `wp core update-db`, égalité du marqueur `db_version` avec celui du cœur chargé.
- Woo : API native `WC_Install::run_manual_database_update()`, puis callbacks **exacts** de la file `woocommerce-db-updates`. Fonctions présentes dans le registre natif, plus le callback natif Variation Gallery précisément nommé et qualifié pour Woo 11.1.1 ; arguments et action finale de version contrôlés. Chaque action est marquée terminée et relue par son ID. Aucune queue globale ne tourne et le verrou AS du staging n'est pas retiré.
- Le lancement automatique Woo est suspendu uniquement dans le processus opérateur, pour ne pas doubler une exécution CLI synchrone avec sa file déjà planifiée. Une vérification sur un **nouveau bootstrap** détecte les migrations natives créées tardivement ; au plus dix vagues, puis refus. La fixture vérifie que les quatre callbacks de version ne sont pas exécutés deux fois.
- Subscriptions : upgrader natif seulement si la version persistée diffère ; contrôle des versions extension/bibliothèque et des travaux de migration connus. Memberships : cycle natif `init()` avec ses fonctions administratives, puis marqueur `wc_memberships_version`.
- Migration historique, traitement différé ou état `failed`/`in-progress` non couvert : **arrêt**, pas de purge et pas de faux « terminé ». Le processeur natif de notifications WCS est explicitement distingué d'une migration : il reste en attente et n'est pas envoyé.
- Après chaque étape : nouveau bootstrap CLI, marqueurs de base, queues pertinentes et absence de fatal/retour d'erreur ; vérification générale finale, y compris lors d'un rejeu déjà terminé. La réception A-03 avant/après reste un contrôle séparé obligatoire.

## Reprise et journal

`etat.json` est atomique, synchronisé sur disque et lié au hash exact du plan, au site et au hash du `wp-config.php`. Phases : `copying`, `copied`, `migrating`, `verified`. Une copie interrompue est terminée avant de recharger WordPress ; les étapes déjà vérifiées ne sont pas mises à jour à nouveau. Les migrations de l'étape interrompue suivent la sémantique native de reprise : **pas de promesse exactly-once pour un callback coupé entre son effet SQL et son marquage**.

Une reprise après plus de dix minutes reste automatique **uniquement** si le checkpoint est valide et le MU persistant strictement conforme. Après acquisition des verrous site et état, puis contrôles staging/sauvegarde/identité, le script vérifie ce MU et rafraîchit `.maintenance` avant PHP/WP-CLI. Un état invalide, un MU absent/modifié ou une contention ne rafraîchit pas le fichier et n'amorce pas WordPress. Ne pas enlever les verrous ni fabriquer un checkpoint pour forcer une reprise.

`journal.json` est la source structurée des étapes, versions, durées, arrêts et vagues ; `journal.txt` reste un en-tête suivi d'une ligne JSON par événement (statu quo accepté, pas une table humaine). `migrations.jsonl`, synchronisé après chaque événement, conserve noms de callbacks, ID d'action, début/fin et codes d'erreur sans arguments, données métier ni erreurs SQL brutes.

Deux `flock` : par état et par site (`.imagine-a04-bascule.lock`). Un autre répertoire d'état ne contourne donc pas le verrou. Les enfants WP-CLI héritent des mêmes descripteurs : tuer le parent ne libère pas le site tant qu'un enfant natif travaille encore. Les fichiers de verrou restent présents ; leur présence ne signifie pas qu'un processus tient encore le verrou. Ne jamais les supprimer pour « débloquer ».

Copie atomique fichier par fichier, sans suppression des fichiers non listés. Le paquet du cœur exclut totalement `wp-content`, `wp-config.php`, `.htaccess` et le fichier d'exemple de configuration. **Les anciens fichiers retirés par l'éditeur restent donc présents** : risque à instruire, pas un nettoyage caché.

## Maintenance et production future

Un MU A-04 persistant est installé après les contrôles et bloque toute requête non-WP-CLI avec HTTP 503, même lorsque le délai natif `.maintenance` expire. Chaque commande opérateur porte en plus un garde-fou temporaire mail/HTTP/paiements/cron/AS. Après réception complète, **l'opérateur** enlève les deux maintenances ; ce script ne le fait pas et ne bascule aucun DNS.

Production : `site_status: "frozen-production"` et option `--go=/chemin/hors-depot/go-ced.json`. Sans GO : refus avant bootstrap. Le JSON, écrit par Ced pour la tâche, contient exactement `author: "Ced"`, `task: "A-04-mise-a-jour"`, `go: true`, `site`, `plan_sha256`, `expires_at` (timestamp futur, six heures maximum). Le runtime doit réellement être `production`. Ce fichier est une **attestation locale**, pas une signature cryptographique : le script ne sait pas authentifier Ced. Il ne remplace ni le GO écrit initial ni la procédure opérateur. **Aucun GO réel n'est livré ici.** La branche production n'a été exercée que sur les mêmes fixtures fictives isolées.

## Rejouer sans réel

```sh
python -B wp/tests/a04/prepare_public.py
python -B wp/tests/a04/run.py --unit-only
python -B wp/tests/a04/run.py
python -B wp/tests/a04/style.py
```

Depuis Windows, seuls les orchestrateurs Python hôtes tournent ; PHP/WP/MariaDB sont exécutés dans le Docker WSL existant. Paquets publics épinglés par `wp/tests/a04/public.lock.json`, premium déjà autorisés par les bancs A-02/A-03, aucun téléchargement à l'exécution des fixtures, aucune licence/compte activé. Le runner ne fait aucun nettoyage large : chaque conteneur a son nom et son label A-04, inspectés avant/après et avant suppression.

Le rejeu complet dépasse parfois le watchdog de l'outil terminal : le lancer comme **processus suivi en arrière-plan**, puis attendre son vrai code de sortie ; ne pas annoncer un succès sur le seul démarrage. La réception utilise exclusivement le **verdict natif A-03** : après cette montée de versions, code **3**, aucun écart anormal et tous les changements classés « attendu » ; après un rejeu identique, code **0** et liste des changements vide. Un code 2 n'est jamais accepté ni requalifié par A-04.

Le banc copie aussi `wp/tests/a03-non-regression/http-rollback.php` vers `/opt/a03`, conserve la copie dynamique de tous les PHP A-03 et reprend le champ obligatoire `php_error_log` des settings. Son serveur HTTP tourne avec `log_errors=1`, `display_errors=0`, `date.timezone=UTC` et `error_log` égal à ce chemin. Les photos sont **régénérées réellement** ; les anciennes, sans `php_log`, restent historiques et ne sont jamais complétées artificiellement. Le journal UTC borné doit être contrôlé et sans diagnostic avant/après et après l'aller-retour production fictif. L'adaptateur HTTP de fixture exécute les écritures natives en rollback et restaure la séquence synthétique des options : cela ne prouve pas que le HTTP réel ne fait aucune écriture.

L'ancienne qualification additive A-04 a été retirée du code actif ; ses sources et reçus antérieurs restent dans `production/A-04/historique-avant-complements-a03/` et les anciens paquets de preuves. Voir `production/A-04/COORDINATION.md`, `risques.md` et le rapport du lot pour les limites de réception.
