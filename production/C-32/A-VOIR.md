# C-32 — inventaire de cookies, prêt technique avec écart constaté

Ouvrir en navigation privée : http://192.168.129.32:8085/gestion-des-cookies/ . Sous le titre, une seule table de quatorze lignes : nom/motif, producteur, geste, durée et usage. Le texte éditorial WordPress reste vide ; pas de texte juridique, bandeau ou script ajouté.

Dans les outils du navigateur, l’accueil http://192.168.129.32:8085/ pose **sept cookies `sbjs_…` par JavaScript**, aucun `Set-Cookie` serveur. L’attendu « aucun cookie en lecture » n’est donc **pas tenu** : `strict-reading-V2.json` reste FAIL. Leur origine est l’attribution native WooCommerce activée. Le réglage WooCommerce → Réglages → Avancé → Fonctionnalités → Attribution des commandes (`woocommerce_feature_order_attribution_enabled=no`) les éteindrait ; il n’a pas été changé. Aucun arbitrage juridique pris ; consentement à voir avec Imagine et son conseil.

Le code suivi fictif http://192.168.129.32:8085/bienvenue/?code=fictif-affiche ajoute la session native WooCommerce ; un panier ajoute ses deux cookies ; une vraie connexion et un choix de langue natifs sont testés par automate. Les valeurs ne sont jamais déposées dans le dépôt. Le navigateur exécute les scripts et contrôle 44 pages publiques issues de l’inventaire C26/B09, sans changer la matrice C26. Deux cookies-sondes HTTP/JavaScript hors liste font lever le même refus, puis les sondes sont retirées. Témoins d’étanchéité C26 réutilisés.

Relecture sans mutation :
```bash
python -B production/C-32/verifier.py --live
```
Rejouer avec une étiquette neuve (les reçus sont immuables) :
```bash
python -B wp/outils/demo/c32.py native nouvelle-native-V2
python -B wp/outils/demo/c32-browser.py nouveau-browser-V2
python -B wp/outils/demo/c32.py image nouvelle-image-V2
python -B wp/outils/demo/c32.py replay nouveau-replay-V2
```
Le compte temporaire, ses métadonnées, les sessions et paniers d’essai sont retirés/restaurés et relus. Le premier essai a buté sur un nom de méta produit incorrect ; sa création native avait changé `user_count`. L’état initial a été retrouvé par l’empreinte exacte de sa préimage (`recovery-essai-V2.json`), puis le banc a ajouté cette option à son snapshot privé durable. Aucun ancien échec réécrit. Aucun compte, contenu ou lot réel touché ; pas de changement C30 ni de code clos, seulement le bloc d’amorçage partagé par contrat.
