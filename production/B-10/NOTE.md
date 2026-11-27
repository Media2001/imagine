# B-10 — points de vente

## Standard natif (cinq lignes)
1. Quelques centaines de commerces tiennent dans un type de contenu WordPress `imagine_vente`, sans table supplémentaire.
2. Le titre et une métadonnée structurée conservent uniquement les champs expressément mappés ; aucun compte ni raccord C-21.
3. Le type est privé, sans REST ni recherche générale ; une page native restitue la seule liste active.
4. Une option non autoloadée désigne les IDs actifs : un nouvel import est préparé puis basculé, un rejeu identique garde les IDs.
5. Administration, capacité `manage_options`, nonces et formulaires natifs ; CSV PHP, sans bibliothèque ni fournisseur distant.

Sources officielles consultées : https://developer.wordpress.org/reference/functions/register_post_type/ ; https://developer.wordpress.org/reference/functions/register_post_meta/ ; https://developer.wordpress.org/apis/settings/ ; https://www.php.net/manual/en/function.fgetcsv.php (échappement propriétaire désactivé explicitement).

## Décisions prises à défaut
- Recherche exacte après suppression des accents, passage en minuscules Unicode et trim ; pas de préfixe postal ni rayon. Tri localité puis nom, mêmes règles.
- CSV UTF-8 avec en-tête, BOM permis, séparateur configurable `;`, `,` ou tabulation ; guillemets doubles standard. Plafond technique 2 Mio, 2 000 lignes acceptées, champs de 500 caractères.
- Correspondance JSON : clés fermées `nom`, `adresse`, `localite`, `postal`, facultativement `personne` et `telephone`. Ces deux dernières exigent une ligne explicite ; aucune colonne inconnue n'est conservée. Les quatre champs requis ne peuvent pas être vides.
- En-tête/mapping invalide ou zéro commerce accepté : l'ancienne liste reste active. Refus de ligne : numéro physique initial et motif fixe, jamais la donnée. Doublon exact refusé. Un import valide remplace toute la liste, sans fusion.
- La carte est un réglage fermé `0|1`, défaut `0` et valeur inconnue ramenée à `0`. À `1`, emplacement seulement, sans script/image/iframe.
- Page de réglages dédiée Réglages → Points de vente ; aucun changement de l'écran C-10 clos. Pas de style nouveau.

## Carte ultérieure (trois lignes)
Il faudra choisir un fournisseur, son coût et les conditions de chargement, sans présumer de ce choix ici.
Il faudra disposer des coordonnées dans le fichier ou faire approuver un géocodage séparé ; aucun n'est tenté par B-10.
Tout fond de carte tiers devra attendre le consentement approprié et rester déchargé avant celui-ci (§4.4).

## Questions laissées ouvertes
Imagine attend-il une recherche par rayon ou préfixe postal ? Le défaut de ce lot reste strictement exact.
Validation visuelle de Ced attendue ; données et adresses entièrement fictives.
