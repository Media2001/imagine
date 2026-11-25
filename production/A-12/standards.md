# Standard d'abord — A-12

Références officielles contrôlées par HTTP public, corps SHA-256 et statut dans `sources-officielles.json`. Aucun accès à un site client.

- `get_post_types()` / `get_taxonomies()` consultent les registres globaux construits à l'exécution. L'oracle fictif utilise ces API avant gel ; le collecteur les appelle après le bootstrap natif READ ONLY d'A-11, sans analyse statique de remplacement.
- `register_post_type()` / `register_taxonomy()` construisent ces objets et déclenchent leurs hooks d'enregistrement. Des noms calculés ou appels conditionnels expliquent pourquoi présence d'une chaîne dans un fichier et enregistrement effectif sont différents. Le banc exerce réellement les deux cas.
- `get_attached_file()` repose sur `_wp_attached_file` et peut appliquer un filtre ; le banc utilise sa variante non filtrée pour l'oracle. Le collecteur lit seulement ce chemin en mémoire, le borne aux fichiers locaux du site, fait un `stat` et n'exporte jamais le chemin.
- `wp_get_attachment_metadata()` offre notamment dimensions, variantes et taille mémorisée ; l'inventaire veut un poids réel de fichier, pas une taille mémorisée potentiellement périmée. Le poids livré porte sur l'original local, pas la somme des miniatures.
- HPOS déplace le stockage des commandes vers des tables dédiées via le CRUD WooCommerce ; ce n'est pas un déplacement des contenus éditoriaux et produits hors de `posts/postmeta`. Les deux modes sont créés et contrôlés avec les vraies extensions du banc A-02.

Les hooks d'enregistrement sont préinitialisés selon `WP_Hook::build_preinitialized_hooks`, sans charger de PHP du site avant les gardes A-11. La pile des appels réellement exécutés donne le fichier déclarant ; le registre final donne les objets encore présents. Les arguments de pile ne sont jamais capturés ni exportés.

Landlock (documentation noyau Linux, `https://docs.kernel.org/userspace-api/landlock.html`) borne les mutations de fichiers au parent des rapports, avant l'exec PHP. ABI >= 3 pour la troncature ; ABI 7 observée sur le banc. Les droits noyau s'héritent et ne dépendent pas des hooks WordPress. Les tentatives réelles de création et troncature depuis un MU-plugin échouent ; le conteneur déconnecté bloque la sortie réseau et la fonction mail directe est désactivée.

Sur-mesure limité : attribution runtime, agrégations de structure sur la connexion A-11 existante et sortie privée liée au rapport A-02 ; aucun modèle éditorial, rattachement ou droit choisi. Les références complémentaires des hooks, de la préinitialisation et du confinement sont contrôlées dans `sources-runtime-officielles.json`.
