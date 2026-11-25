# Standard d'abord — A-12

Références officielles contrôlées par HTTP public, corps SHA-256 et statut dans `sources-officielles.json`. Aucun accès à un site client.

- `get_post_types()` / `get_taxonomies()` consultent les registres globaux construits lors de l'exécution de WordPress. Ils ne constituent pas un lecteur autonome de la base. L'oracle fictif utilise ces API avant gel ; le collecteur ne prétend pas les remplacer par une analyse statique exhaustive.
- `register_post_type()` / `register_taxonomy()` construisent ces objets et déclenchent leurs hooks d'enregistrement. Des noms calculés ou appels conditionnels expliquent pourquoi présence d'une chaîne dans un fichier et enregistrement effectif sont différents. Le banc exerce réellement les deux cas.
- `get_attached_file()` repose sur `_wp_attached_file` et peut appliquer un filtre ; le banc utilise sa variante non filtrée pour l'oracle. Le collecteur lit seulement ce chemin en mémoire, le borne aux fichiers locaux du site, fait un `stat` et n'exporte jamais le chemin.
- `wp_get_attachment_metadata()` offre notamment dimensions, variantes et taille mémorisée ; l'inventaire veut un poids réel de fichier, pas une taille mémorisée potentiellement périmée. Le poids livré porte sur l'original local, pas la somme des miniatures.
- HPOS déplace le stockage des commandes vers des tables dédiées via le CRUD WooCommerce ; ce n'est pas un déplacement des contenus éditoriaux et produits hors de `posts/postmeta`. Les deux modes sont créés et contrôlés avec les vraies extensions du banc A-02.

Sur-mesure limité : collecte PDO READ ONLY sans bootstrap, agrégations de structure, observation inerte des déclarations candidates et sortie privée liée au rapport A-02. Pas de nouveau modèle éditorial, pas de rattachement ou de décision de droits. Le manque d'exhaustivité runtime demeure **bloquant**, pas une règle métier à inventer.
