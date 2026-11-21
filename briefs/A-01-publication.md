# Lot A-01 — dernière étape : rendre le staging utilisable

**Date** : 21/11/2026. **Délai** : une demi-journée. Fait suite à `briefs/A-01-chemin-court.md`.

## Où on en est

Ton rapport du 21/11 l'établit : la commande hors ligne restaure une archive `.wpress`, neutralise, anonymise et vérifie, avec une fidélité prouvée des fichiers, du thème, des extensions et des réglages, en stockage classique et HPOS. Elle s'arrête en `DATA_VERIFIED_PUBLICATION_BLOCKED` parce que deux choses manquent : publier le site, et limiter sa sortie réseau au niveau système.

Tu t'es arrêté plutôt que de construire une nouvelle orchestration ou de toucher à l'outil partagé. C'était la bonne décision. Voici les deux arbitrages qui lèvent le blocage.

## Arbitrage 1 — la sortie réseau

**Le filtrage au niveau du système n'est plus exigé une fois le site vérifié.** La protection retenue est :

- pendant l'import et jusqu'à la vérification : aucun réseau, comme aujourd'hui ;
- après la vérification : le filtrage de WordPress suffit (`WP_HTTP_BLOCK_EXTERNAL` et `WP_ACCESSIBLE_HOSTS` limités à `*.wordpress.org` et `*.woocommerce.com`, plus le filtre du mu-plugin).

Raison : à ce stade, les clés, les jetons et les identifiants de paiement ont été retirés et leur absence est vérifiée. Un filtrage système serait une seconde barrière, pas la première. Écris cette limite telle quelle dans le rapport de la commande.

## Arbitrage 2 — la publication

**Tu n'écris pas de nouveau frontal.** Tu utilises l'outil de staging tel qu'il est, par son usage normal, sans modifier son code :

1. Créer un site vide par l'interface normale de l'outil (son API de création), avec la version de PHP voulue. Un site vide ne contient rien de dangereux.
2. Arrêter ce site.
3. Remplacer sa base et son `wp-content` par ceux que ta commande hors ligne a produits et vérifiés.
4. Régler `home` et `siteurl` sur l'adresse que l'outil a attribuée au site, sans démarrer WordPress.
5. Démarrer le site, lancer la sonde d'exécution (email coupé, requêtes sortantes filtrées, Subscriptions en mode staging, ordonnanceur verrouillé).
6. Si la sonde réussit : statut « vérifié », écrit dans un fichier témoin à la racine du site et dans le rapport. Sinon : arrêter le site et afficher le rapport.

Si une autre voie est plus courte et respecte « ne pas modifier le code de l'outil », prends-la et dis pourquoi. Si aucune voie ne tient sans modifier l'outil, arrête-toi et décris la modification minimale nécessaire : Ced décidera.

## Ce que tu as le droit de faire dans l'outil de staging

- Créer, arrêter, démarrer et supprimer des sites **de test** nommés `imagine-test-…`, par son API normale.
- Rien d'autre : pas de modification de son code, de ses modèles, ni des autres sites.
- Supprime tes sites de test à la fin et vérifie leur absence.

## Preuve attendue

Sur une archive `.wpress` fabriquée à partir d'un site jetable, avec Subscriptions et Memberships : la commande complète aboutit à un site de test **joignable dans l'outil**, au statut « vérifié », dont les extensions et les réglages sont intacts. Puis le cas d'échec : une clé piégée laissée dans l'archive, et le site reste arrêté.

## Livrables

1. La commande unique, et dans `production/A-01/notes.md` : comment Ced la lance sur l'archive d'Imagine, ce qu'il verra, la durée, quoi faire si une table est à trancher, comment relancer de zéro.
2. La preuve ci-dessus.
3. `production/A-01/PRET`.

## Limites inchangées

Aucun import d'Imagine, aucune ouverture de son archive, ancienne copie non relancée, Novamira non branché. Le premier import réel sera lancé par Ced et son rapport sera relu avant toute ouverture aux agents.
