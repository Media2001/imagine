# A-11 — inventaire des adresses publiques

Complément **lecture seule** d'A-02 : une adresse relative unique par ligne, sans décider de redirection, sans crawl et sans outil de mesure des liens entrants. Rien de réel n'a été ouvert pour ce lot.

## Lancer

PHP 8.2+ avec mysqli, dans une copie vérifiée et confinée (réseau sortant coupé, fichiers du site montés en lecture seule, compte SQL SELECT seulement). **Pas en production, pas de GO implicite.** Le bootstrap natif charge les extensions et le thème pour conserver leurs types, taxonomies et filtres de permaliens : un code tiers arbitraire ne peut pas être rendu inoffensif par quelques hooks PHP. Le confinement système reste obligatoire, en plus des gardes de cet outil. Aucun cache externe/drop-in n'est accepté.

```sh
php wp/outils/bascule/a11/inventorier-adresses \
  --wp-path=/copie-verifiee/site \
  --audit=/rapports/audit-001/audit.json \
  --output=/rapports/adresses-001
```

Le parent `/rapports` doit exister. Le rapport A-02 et le nouvel inventaire sont deux dossiers frères, hors racine web **et hors dépôt**. Le dossier de sortie doit être nouveau. Refus des sorties dans le site/le dépôt, y compris via un parent symbolique; permissions 0700/0600 sous Linux. Les rapports d'un site réel ne rejoignent jamais le dépôt.

- `adresses.csv` : UTF-8 avec BOM, séparateur `;`, colonne `ancienne` directement réutilisable dans le plan A-09 (le plan lui-même conserve son en-tête et son séparateur A-09). Neutralisation des cellules de tableur commençant par un préfixe de formule.
- `adresses.json` : données structurées, nombres exacts et empreinte du rapport A-02 utilisé.
- `resume.md` : nombres par nature, comptes des exclus, structure de permaliens et bases WordPress/WooCommerce.
- Code de sortie 0 seulement après les trois fichiers; 1 et un code d'erreur fixe en cas de refus/échec. Une sortie partielle n'est pas un inventaire validé et n'est pas écrasée au rejeu.

## Ce qui est listé

Types publics et interrogeables sur le front : articles, pages, produits, autres types publics (nature `article`, type exact conservé), pages de pièces jointes, termes des taxonomies publiques/interrogeables (y compris termes vides), archives d'auteur et archives de types.

Les brouillons/auto-brouillons, privés et protégés sont comptés, jamais listés. Les autres états sont agrégés sans leurs adresses. Pour les pièces jointes : héritage natif de publication (y compris parent manquant), refus prudent d'un parent protégé, détection des cycles, et respect de l'option native `wp_attachment_pages_enabled`. Il s'agit des **pages de pièces jointes**, jamais des URLs de téléchargement.

Les auteurs sont ceux des contenus publiés non protégés des types publics hors pages/pièces jointes, comme le périmètre de types des sitemaps utilisateurs WordPress : pas de liste générale des comptes, pas de client sans contenu public, ni d'auteur seulement de pages. Aucun nom, email ou identifiant utilisateur séparé n'est écrit : seul le segment/paramètre déjà public de l'adresse native peut apparaître.

L'archive native des articles est incluse : accueil des derniers articles ou page des articles d'un accueil statique. L'archive produit dépend de l'enregistrement natif WooCommerce et du support du thème; on n'invente pas d'archive désactivée. Les flux, recherches, variantes paginées, pages techniques et URLs historiques ne sont pas énumérés : ce lot liste les adresses canoniques des natures du brief, pas toutes les requêtes possibles.

Une adresse commune (boutique/page/archive, page des articles/archive) garde une seule ligne et tous ses `contextes`. Le premier contexte donne les colonnes principales; les autres figurent dans le CSV. Les nombres par nature sont donc **non additifs**. Les dates UTC sont les dates natives `post_modified_gmt` des contenus. Termes/archives n'ont pas de date native propre : cellule vide, jamais de date inventée; leur état est `public`. Une pièce jointe garde son état stocké `inherit`.

## Convention A-09

Chemin relatif à l'origine, commençant par `/`, y compris le sous-répertoire éventuel du site; ASCII URI, sans fragment ni double slash initial. Canonicalisation **du chemin seulement** : échappements hexadécimaux en majuscules, caractères non réservés décodés. La requête n'est ni triée, ni décodée, ni réencodée : doublons, `+` et casse des échappements restent exacts. Requête vide, contrôle, espaces, antislashs, segments `.`/`..` et encodages de séparateurs sont refusés comme dans A-09. Une URL native externe ou incompatible arrête l'export par `A11_URL_NOT_A09_COMPATIBLE` : aucune troisième convention ni troncature silencieuse. La suite appelle **la fonction A-09 inchangée** sur les adresses produites et sur l'oracle indépendant.

## Lecture seule et limites explicites

La configuration n'est pas exécutée : seules les cinq valeurs littérales reconnues par le parseur A-02 sont lues. La connexion native `wpdb` est injectée avant `wp-settings.php`, en transaction REPEATABLE READ / READ ONLY; sa méthode `query` n'autorise que les lectures et refuse notamment COMMIT et la sortie du mode lecture seule. Le serveur refuse aussi un UPDATE direct sur le handle mysqli, y compris avec l'identité SQL privilégiée du banc. HTTP, mail, programmation/réordonnancement/suppression de cron et runner asynchrone Action Scheduler sont bloqués par leurs points d'entrée natifs.

L'outil nécessite une configuration WordPress mono-site standard : refus des constantes de chemins/personnalisation de tables/URL, de Multisite, des configurations DB dynamiques, des symlinks du site et des drop-ins `db.php`, `object-cache.php`, `advanced-cache.php`, `sunrise.php`. Refuser une pile non qualifiée est volontaire : ne jamais publier un inventaire partiel comme complet. Les empreintes de toutes les tables (schéma avec auto-incréments et toutes les lignes), des fichiers, de WP-Cron et d'Action Scheduler sont prouvées identiques sur le banc. Cela ne prétend pas qualifier les effets arbitraires de chaque extension d'un futur site réel; conserver le confinement et refaire l'empreinte sur la copie vérifiée.

## Le standard avant l'inventaire spécifique

WordPress fournit les générateurs, WooCommerce enregistre ses bases et filtres : ce lot les appelle, il ne reconstruit pas leurs règles avec des concaténations SQL. Les sitemaps natifs sont un point de comparaison, pas un crawl à exécuter : ils ne livrent pas ce tableau réuni avec états, dates et comptes d'exclus. Le sur-mesure se limite au rassemblement, à la convention A-09, à la sécurité lecture seule et aux fichiers de restitution.

Références officielles consultées pour cette livraison :

- WordPress `get_permalink`, `get_attachment_link`, `get_term_link`, `get_author_posts_url`, `get_post_type_archive_link` : `https://developer.wordpress.org/reference/functions/` (pages portant ces noms).
- Hooks `pre_http_request`, `pre_wp_mail`, `pre_schedule_event` : `https://developer.wordpress.org/reference/hooks/` (pages portant ces noms).
- Source WordPress 7.0.9 : `https://github.com/WordPress/WordPress/blob/7.0.9/wp-includes/link-template.php`, `post.php`, `load.php` et `sitemaps/providers/class-wp-sitemaps-users.php` (l'exception native de l'archive `post`, l'héritage des pièces jointes et le périmètre des auteurs ont été vérifiés dans ces sources).
- Source WooCommerce 11.1.1 : `https://github.com/woocommerce/woocommerce/blob/11.1.1/plugins/woocommerce/includes/class-wc-post-types.php` (l'archive produit dépend du support WooCommerce du thème), et fonctions natives réellement exécutées sur la version épinglée du banc.

## Suite dédiée, sans rejeu global

Depuis la racine du dépôt, sans PHP Windows :

```sh
python wp/tests/a11/run.py
python wp/tests/a11/run.py --unit-only
python wp/tests/a11/run.py --final
python wp/tests/a11/verifier.py production/A-11/preuves/IDENTIFIANT
```

Sans `--final`, tous les essais restent dans le scratch Hermes hors dépôt. Une seule exécution finale verte est conservée dans `production/A-11/preuves/`. Le runner réutilise A-02 sans le modifier, avec une identité et un nom de conteneur **A11 distincts**; aucune image partagée n'est reconstruite par lui. Classique et HPOS, oracle par vraies API avant gel, permaliens simples/structurés, sous-répertoire, accueil statique, pièces jointes activées/désactivées, auteur produit sans support auteur, auteur de pages exclu, Unicode encodé, requête filtrée et collision boutique sont vérifiés. Le runner supprime seulement son conteneur et vérifie son absence, sans sweep de conteneurs voisins.
