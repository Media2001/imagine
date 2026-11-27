# A-26 — Ce que le site déclare charger chez des tiers

Ce complément de l'audit ne désactive rien, ne contacte aucun service et n'évalue ni les cookies réellement déposés ni la conformité. État courant après corrections du 27/11, file de 1 h 30 : `production/A-26/corrections-1h30.md`. Code corrigé, Python seul rejoué ; qualification PHP/native et nouveau sceau réservés au parent après stabilisation A-28. `production/A-26/FINALISATION.md` et `production/A-26/preuves/final/` restent historiques, pas une qualification du code corrigé. Aucun nouveau PRET.

## Le standard d'abord — dix lignes

1. WordPress conserve la liste locale des extensions actives dans l'option `active_plugins` ; les chemins sont comparés en mémoire, jamais publiés (référence officielle `get_plugins`, `get_option`).
2. Les installations multisites possèdent aussi des activations réseau ; le runtime réemployé les refuse, elles ne sont pas transformées en faux zéro.
3. Les réglages d'extensions sont généralement des options, mais leur schéma appartient à chaque extension, pas à WordPress (`get_option`).
4. Le contenu enregistré est `posts.post_content` ; cet outil lit uniquement les contenus publiés des types déclarés publics, hors pièces jointes et blocs réutilisables isolés.
5. `WP_Block_Parser` lit les blocs sans rendu ; `WP_HTML_Tag_Processor` lit les vraies balises/attributs HTML sans expression régulière, notamment les guillemets contenant `>` et les faux `src` dans un titre.
6. Les blocs `core/embed`, audio, vidéo et image peuvent déclarer une URL ; les blocs réutilisables `core/block` sont résolus localement, sans appel oEmbed.
7. WordPress sait intégrer une URL seule sur une ligne ; une URL dans un lien ordinaire n'est pas à elle seule une ressource chargée (`Embeds`).
8. Les codes courts sont reconnus par la grammaire native `get_shortcode_regex` et leurs attributs, jamais par `do_shortcode` ni un callback de rendu.
9. Les outils de confidentialité du cœur aident à rédiger une politique et à exporter/effacer des données ; ils ne fournissent pas un bandeau universel bloquant toutes les ressources (`Privacy`).
10. Même l'extension WP Consent API précise qu'elle communique des catégories et nécessite un gestionnaire de consentement ; elle ne gère ni le consentement ni le blocage à elle seule.

Références officielles : `production/A-26/standard/sources.json` et, pour le lecteur HTML natif, `production/A-26/standard/html-tag-processor-sources.json` (réponses officielles archivées et empreintes). Références : `https://developer.wordpress.org/reference/functions/parse_blocks/`, `https://developer.wordpress.org/reference/functions/get_shortcode_regex/`, `https://developer.wordpress.org/reference/functions/get_option/`, `https://developer.wordpress.org/reference/functions/get_plugins/`, `https://developer.wordpress.org/plugins/privacy/`, `https://wordpress.org/documentation/article/embeds/`, `https://wordpress.org/plugins/wp-consent-api/`.

## Parcours opérateur

Préconditions : copie **déjà vérifiée et autorisée** par l'opérateur ; Linux isolé avec réseau coupé, Landlock, PHP CLI 8.2+, WooCommerce, identifiants SQL SELECT. Photographie A-02 de cette même copie, dans un sous-dossier du parent privé de sortie. Le parent de sortie existe, hors site et dépôt, disjoint dans les deux sens ; ce n'est ni `/`, ni un ancêtre du site. La commande ne crée jamais ce parent. Le dossier final doit être neuf. L'accès à une copie réelle reste réservé à Ced : ce document ne l'autorise pas.

```sh
python3 wp/outils/bascule/a26/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/tiers-date
```

C'est toute la commande : pas de date, identifiant, numéro ou argument caché. Seuls les trois chemins fictifs sont remplacés par l'opérateur. Le banc lit cette ligne exacte, substitue seulement ces chemins et la rejoue. Résultat public : `A26_OK tiers.json tiers.md`, puis deux fichiers privés (0700/0600). Ne jamais exécuter directement `inventorier-tiers` : il exige le confinement.

### Dix derniers numéros lorsque la correspondance A-16 est connue

Ajouter `--a16-map=/hors-web/audit-date/correspondance.json`, fichier privé de correspondance **au format A-16 existant**, pas le rapport agrégé `numeros.json`. Aucun titre, ID d'article/numéro ou nom de clé source ne sort. Validation réemployée depuis A-16 en lecture seule ; sélection bornée aux liaisons `postmeta` scalaires, `post_parent` et taxonomie de numéros, avec dates UTC strictes. Tri A-16 : date décroissante, ID décroissant en cas d'égalité ; au plus dix numéros. Un article lié à plusieurs numéros retenus n'est compté qu'une fois par service. Les orphelins restent dans le total général, pas dans cette sélection. Les numéros eux-mêmes suivent A-16 (tous états) ; seuls leurs articles publiés sont retenus.

Sans correspondance fournie, le rapport indique `mode=annee`, par année GMT de publication (0 = date absente/non reconnaissable). Une correspondance explicite invalide ou sans numéros est refusée, pas ignorée. Le banc prépare les trois modes, onze numéros, l'exclusion du plus ancien et des orphelins. Les contraintes PDF/thématiques d'A-16 non nécessaires à une sélection ne sont pas rejouées, aucun fichier média n'est ouvert.

## Liste fermée et sens des comptes

Le code `Analysis::PLUGINS` est l'unique liste de chemins d'extensions. Elle couvre dix familles : mesure, pixel, consentement, partage, carte, vidéo, audio, polices, formulaire externe, anti-robot. Dix-sept chemins exacts, une seule famille par chemin, doublons d'activation éliminés. Une extension multifonction ne contribue qu'à sa famille choisie : Site Kit en mesure, Facebook for WooCommerce en pixel. MU-plugins, thème, extensions hors liste et détection par nom commercial sont hors compte ; **zéro ne signifie pas absence générale de tiers**. L'état actif est une déclaration locale, pas une preuve de requête navigateur.

`identifier` vaut `oui` si au moins un adaptateur qualifié voit une valeur non vide, `non` si aucune extension de la liste n'est active ou si l'unique adaptateur qualifié a un identifiant absent/vide, `illisible` sinon. L'unique schéma de réglage qualifié est Site Kit GA4 : option `googlesitekit_analytics-4_settings`, champ `measurementID` (source officielle Google `includes/Modules/Analytics_4/Settings.php`, empreinte conservée). Les seize autres chemins n'ont **aucun parseur de réglage inventé** : actifs, ils donnent `illisible`, même si un réglage existe. Pour plusieurs extensions de mesure, un oui connu l'emporte ; sinon un schéma non couvert rend le résultat illisible. Tableau/objet/mauvaise sérialisation d'identifiant : illisible, aucune instanciation d'objet.

Les treize étiquettes de service sont `youtube`, `vimeo`, `dailymotion`, `soundcloud`, `spotify`, `mixcloud`, `google_maps`, `openstreetmap`, `facebook`, `instagram`, `twitter`, `tiktok`, `autre`. `Analysis::HOSTS` contient les domaines et alias exacts ; un sous-domaine avec frontière de point est admis. Google Maps ne couvre que `maps.google.com/fr` et `/maps` sous `google.com/fr`, pas tous les domaines Google ou tous les pays. Tout domaine non couvert devient `autre`, sans sa valeur. HTTP(S), casse/dot final et URLs protocol-relative sont normalisés en mémoire ; origine locale exclue. Aucune résolution DNS ni requête n'est faite. Une valeur locale relative n'est pas externe.

Un contenu compte au plus une fois par service, même avec plusieurs iframes, blocs ou URLs. Les sommes par service ne sont pas un nombre de visiteurs ni un nombre de contenus distincts tous services confondus. Détection statique bornée : HTML de ressources (`iframe`, `embed`, `object`, `script`, `img`, `audio`, `video`, `source`, `link`, `blockquote`), URL seule sur sa ligne, attributs `url/src` des blocs natifs listés, blocs réutilisables publiés et codes courts fermés `embed/video/audio/youtube/vimeo/dailymotion/soundcloud/spotify/mixcloud/googlemaps/google_maps` avec URL dans corps ou attribut URL connu. Pas de décodage d'un ID seul de code court, pas de rendu dynamique ni callback, pas de JavaScript/CSS réseau, widgets/options de thème, menus, champs de constructeurs, styles `url()`, srcset, blocs dynamiques tiers ou domaines internationaux décodés. Une intégration conditionnelle est une déclaration, pas une requête observée. Les extraits `<pre>/<code>` et commentaires HTML sont exclus du scanner HTML. Profondeur de références >16, cycle, référence absente/non publiée ou contenu >4 Mio : refus générique, pas de compte partiel.

## Neutralisation : ne pas confondre absence et effacement

L'import existant (`staging/policy.php` et `lib.php`) n'est pas modifié. La marque `imagine_staging_disabled_plugins`, qui alimente aussi son rapport, est lue **dans la copie**, sans ouvrir une archive ou un ancien rapport libre. Si elle contient un chemin fermé désactivé, son nombre de famille et son identifiant donnent `inconnu après neutralisation`. Marque illisible : les familles mesure/pixel sont prudemment inconnues. Les nombres des familles non désactivées restent observés ; tout identifiant d'une famille encore active devient inconnu (le scrub peut effacer des réglages).

**Tous les comptes de contenus-source deviennent inconnus sur copie neutralisée**, et non des zéros : `dangerous()` peut vider un `post_content` entier dès qu'il contient un motif sensible, y compris une ressource sans rapport avec le motif. L'ancien contenu n'est pas récupérable depuis cette copie. Le banc clone sa base fictive, exécute réellement `neutraliser()` puis `anonymiser()` inchangés, et prépare une preuve d'extension retirée, réglage effacé et article vidéo effacé. La qualification native de cette couverture est liée au paquet final dans `production/A-26/FINALISATION.md` ; aucun reçu d'import n'est inventé.

## Sorties et refus

SQL SELECT et transaction READ ONLY via A-11, pare-feu Landlock A-12, réseau nul, mail/HTTP/cron refusés et quatre API Action Scheduler court-circuitées avant le bootstrap. Les `error_log()` natifs vont exclusivement vers `/dev/null`, jamais vers un chemin choisi par le site. Symlinks, configuration non littérale/personnalisée ou drop-ins : refus fermé avant bootstrap. Seuls les six noms techniques fixes des drop-ins peuvent apparaître dans ces refus historiques ; aucun chemin libre n'est publié.

A-22 `stream_guard.supervise` est le seul gardien de processus, réemployé inchangé. Les octets restent en mémoire bornée. La publication attend la fin et les deux EOFs, puis vérifie le protocole fermé, la liaison SHA-256 émise après l'écriture et avant les shutdowns, le schéma récursif fermé, les nombres entiers, la partition annuelle/sous-ensemble des dix derniers, les deux fichiers canoniques et leur projection Markdown exacte. Une modification finale de nombres restant valide JSON/Markdown est refusée par la liaison. Une erreur supprime le stage privé, ne publie rien et ne recopie jamais la valeur de l'exception. L'empreinte A-02 lie une photographie fournie ; ce n'est pas une preuve automatique que la base n'a pas changé depuis cette photographie : l'opérateur garantit ce prérequis.

## Rejeux réservés au parent

```sh
C:/Python314/python.exe -B wp/tests/a26/matrix.py --python-only --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a26-python-neuf
C:/Python314/python.exe -B wp/tests/a26/verify.py --python-only --packet=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a26-python-neuf
C:/Python314/python.exe -B wp/tests/a26/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a26-native-neuf
C:/Python314/python.exe -B wp/tests/a26/verify.py --packet=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a26-native-neuf --require-shared-doc
```

Les deux premières ne lancent jamais PHP/WSL/Docker et ne constituent pas une réception native. La troisième sérialise les bancs classiques/HPOS dans les deux consoles Windows puis le contrôle PSR-12 en conteneur. Le premier réemploi d'image exige les dépendances fictives locales déjà autorisées ; aucune image ni extension n'est téléchargée par ce lot. Une image manquante échoue explicitement. Le parent peut d'abord lancer `style.py --fix --output=...` dans un autre dossier neuf ; il faut ensuite geler et rejouer la matrice entière sur ces nouvelles sources. Préparation T-01 et portes globales appartiennent au parent. Voir `production/A-26/RECEPTION-PARENT.md`.
