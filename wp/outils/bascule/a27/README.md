# A-27 — Moyens de paiement enregistrés, comptes en lecture seule

Aucun paiement, aucune passerelle interrogée, aucun avis sur la survie des renouvellements. Le lanceur ne fonctionne que dans l'enclos Linux déconnecté A-12 ; il refuse un lancement Windows ordinaire. Les tests Python, eux, tournent sur Windows sans PHP. **Corrections du passage de 1 h 30 : code corrigé, qualification native courante en attente du parent après gel de l'import A-28.** Voir `production/A-27/corrections-1h30.md`. `FINALISATION.md` et `preuves/final/` restent les preuves historiques de l'ancêtre, pas une qualification du code corrigé. Aucun PRET ni sceau nouveau ; jamais un GO réel.

## Le standard d'abord — dix lignes

1. L'API officielle WooCommerce représente les moyens enregistrés par `WC_Payment_Token`, spécialisés notamment en `CC` et `eCheck` [S1].
2. Le magasin natif écrit `token_id`, `gateway_id`, `token`, `user_id`, `type`, `is_default` dans `{prefix}woocommerce_payment_tokens` [S2].
3. Ses attributs supplémentaires, dont les échéances des cartes, sont stockés dans `{prefix}woocommerce_payment_tokenmeta` [S1, S2].
4. `WC_Payment_Tokens::get(id)` relit un jeton ; il faut vérifier séparément son compte et sa passerelle, sans confondre jeton du compte et jeton du renouvellement [S1, S2].
5. `get_customer_tokens()` est paginé/filtré : A-27 énumère tous les identifiants par SELECT puis utilise le lecteur unitaire, sans cette troncature [S2].
6. L'abonnement classique est un `shop_subscription` de `posts`, complété par `postmeta` ; HPOS utilise `wc_orders` et `wc_orders_meta` [S3].
7. `WC_Subscription`, ses getters `edit`, `get_meta()` et `get_payment_tokens()` lisent le magasin faisant autorité : pas de concaténation classique+HPOS [S1, S3].
8. Le renouvellement Woo est dispatché à `woocommerce_scheduled_subscription_payment_{gateway_id}` ; c'est la passerelle qui lit sa référence locale, pas un format universel de mandat [S4].
9. Le code officiel Stripe lit `_stripe_source_id`, avec repli historique `_stripe_card_id` ; une référence Stripe seule ne prouve ni carte ni conversion Bancontact→SEPA [S5].
10. A-19 fournit le lecteur de présence/schéma natif ; A-27 observe sa même évaluation de schéma pour préserver les valeurs opaques comme inconnues, sans modifier A-19 ; `standard.php` confirme les API Woo/WCS et la clé PayPal sur le code installé avant le sujet, avec empreintes et assertions dans chaque paquet natif final.

### Sources effectivement consultées le 26 novembre 2026

- S1 : https://developer.woocommerce.com/docs/woocommerce-payment-token-api/
- S2 : https://raw.githubusercontent.com/woocommerce/woocommerce/trunk/plugins/woocommerce/includes/class-wc-payment-tokens.php et https://raw.githubusercontent.com/woocommerce/woocommerce/trunk/plugins/woocommerce/includes/data-stores/class-wc-payment-token-data-store.php
- S3 : https://woocommerce.com/document/subscriptions/develop/data-structure/
- S4 : https://woocommerce.com/document/subscriptions/develop/payment-gateway-integration/
- S5 : https://raw.githubusercontent.com/woocommerce/woocommerce-gateway-stripe/develop/includes/abstracts/abstract-wc-stripe-payment-gateway.php et https://raw.githubusercontent.com/woocommerce/woocommerce-gateway-stripe/develop/includes/class-wc-stripe-order-helper.php

Les branches publiques mobiles ne remplacent pas une preuve sur le binaire installé. Le banc parent conserve les empreintes des sources installées dans `classic-standard.json` et `hpos-standard.json`. Stripe/PayPal externes ne sont ni installés ni connectés par ce lot ; les adaptateurs de données lisent seulement les champs locaux explicités ici. Autres schémas : `illisible`, pas une clé de stockage inventée. La consultation de la documentation n'est pas un appel du script d'audit.

## Parcours de l'outil — Linux confiné seulement

Prérequis : copie fictive ou copie vérifiée autorisée par Ced, A-22 clos avant toute copie du réel, PHP 8.2+, Python 3, réseau absent et Landlock disponible, audit A-02 déjà produit. Aucune commande ci-dessous ne constitue un GO sur des données réelles. Le parent du répertoire de sortie existe, hors dépôt et hors arborescence du site ; le nom de sortie est neuf, ASCII alphanumérique/tiret/souligné. L'audit se trouve dans un sous-dossier de ce même parent.

```sh
python3 wp/outils/bascule/a27/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/paiements-date
```

Le banc relit cette ligne et remplace uniquement les trois chemins d'exemple et le chemin installé du lanceur. Aucune option cachée. Succès exact : code `0`, stdout `A27_OK paiements.json paiements.md` suivi d'un saut de ligne, stderr vide. Refus : code `1`, stdout vide, une ligne de la liste fermée `refusals.json`, ou le refus drop-in A-11 portant exclusivement un nom de la liste fixe. Un préfixe de code accompagné d'une valeur libre n'est jamais admis. Pas de diagnostic PHP brut.

Le gardien A-22 draine les deux pipes jusqu'à EOF et fin réelle du processus (y compris shutdown), borne chaque flux à 64 Kio, puis valide le jeu exact de fichiers. Une liaison SHA-256 interne, émise après écriture mais avant shutdown, refuse aussi des nombres altérés avec JSON et Markdown encore cohérents ; ce protocole interne ne sort jamais du lanceur public. JSON canonique à schéma fermé, aucune clé libre, Markdown égal au rendu de ce même JSON, liaison au hash/date/magasin de l'audit. Aucun fichier inattendu, vide, partiel ou lien symbolique n'est publié. Le sujet ne peut écrire que dans son dossier privé ; seul le parent publie après ces contrôles. Les fichiers publiés ont les modes 0600, leur dossier 0700.

## Définitions et défauts prudents

- Vivants : `active`, `pending`, `on-hold`, `pending-cancel`, exactement A-20. Automatique = drapeau **enregistré** `get_requires_manual_renewal('edit')` faux ; pas `is_manual()` qui peut changer sur un staging.
- `automatic` compte un abonnement une fois par passerelle et type : `carte`, `mandat_sepa`, `accord_paypal`, `autre`, `illisible`. La présence prouvée absente reste dans le périmètre A-19 et n'est pas présentée comme un moyen enregistré ; une présence indéterminée entre dans `illisible`.
- Un lien de jeton exige même compte positif **existant**, même passerelle, référence non vide. À défaut de lien d'abonnement, une égalité exacte entre référence locale et jeton du même compte/passerelle est lisible. Jamais le jeton par défaut du compte, une recherche par email, ni une reconnaissance du préfixe `pm_`/`src_`/`B-`.
- Types : `CC`→carte ; `SEPA`→référence SEPA ; `eCheck`→SEPA seulement sous `stripe_sepa`, sinon autre. Une classe de jeton illisible donne `illisible`, même si une ligne physique existe. Les références locales Stripe/Stripe SEPA (`_stripe_source_id`, repli `_stripe_card_id`) et PayPal natif (`_paypal_subscription_id`) sont lues par `get_meta()` ; une source Stripe sans jeton typé reste illisible. PayPal et SEPA ici désignent des références enregistrées, pas une preuve de validité juridique ou bancaire.
- Plusieurs références candidates, références non scalaires ou contradiction entre lien explicite et référence : `illisible` et liaison indéterminée, sans choix d'un instrument. Les autres schémas déclarés par A-19 attestent éventuellement la présence, jamais un type fabriqué.
- `cards` compte les **abonnements automatiques** identifiés par carte (pas les cartes distinctes). Expiration à la dernière seconde UTC du mois ; passée si strictement avant l'audit. Fenêtre : date/heure de `audit.json.generated_at_utc` + six **mois calendaires**, jour borné au dernier jour du mois cible ; borne haute incluse. Audit au 26/11/2026 à midi : fin mai 2027 est au-delà du 26/05 à midi. Date individuelle jamais exportée ; date absente/invalide→`illisible`.
- `relations` : `subscriptions_unlinked` = abonnements vivants, manuels compris, à référence explicite sans jeton correspondant de leur compte ; `subscriptions_link_unknown` = correspondance indéterminée. `tokens_without_living_subscription` compte les jetons des comptes existants sans **aucun** abonnement vivant, et non les jetons non utilisés d'un compte vivant. `tokens_account_unknown` distingue invité/compte inexistant. `accounts_multiple_tokens` compte chaque compte existant avec plusieurs lignes de jetons une seule fois, toutes passerelles confondues.
- Chaque cellule passerelle/type, passerelle/expiration et passerelle/métrique n'apparaît qu'à partir de cinq ; les petites cellules sont additionnées sous `autres`, sans leur libellé. Les métriques de relation ont des unités différentes : leur somme `autres` n'est PAS un nombre de personnes. Les passerelles appartiennent à une liste fermée ; toute valeur non couverte devient `autre`, même si elle ressemble à un identifiant technique.
- Le marqueur de provenance `imagine_staging_disabled_plugins` suffit à déclarer **tous** les nombres demandés `inconnu après neutralisation`. Pas de zéro reconstruit à partir des tables purgées. Le code d'import inchangé `staging/lib.php` supprime les deux tables de jetons (lignes 340–343), les métadonnées sensibles Stripe/PayPal (266–272, 346–348) et conserve le marqueur (489). Il ne reste aucun compte de moyens de paiement interprétable sur cette copie : le mode de comptage de la source appartient à Ced, sans accès du worker.

## Preuves et limites

- Suite Windows : `C:/Python314/python.exe -B -m unittest discover -s wp/tests/a27 -p "test_*.py" -v` ; aucune dépendance PHP.
- Matrice Python seule : `C:/Python314/python.exe -B wp/tests/a27/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a27-python-neuf`.
- Réception parent, matrice native classique+HPOS, contrôle PSR-12, vérification du paquet, préparation d'image et gates restantes : `production/A-27/RECEPTION-PARENT.md`.

Les tests Python prouvent les frontières de sortie, les refus et le validateur, pas l'exécution de PHP, le code installé, l'immutabilité native DB/fichiers ou l'isolation Docker. `adapter-unit.php` traverse le lecteur A-19 réel sur une coque de hooks et d'abonnement fictive : opaque/non scalaire, vide, scalaire, exception et retrait de l'observateur. Le runner prépare les témoins rouges R2/R3 dans sa seule copie jetable, puis les suites vertes. Son banc natif prépare cinq abonnements sans jeton sous `ppcp-gateway`, schéma opaque fourni par le filtre natif et relu par A-19, puis trois cas SEPA séparés (contradiction, référence seule, correspondance unique), dans chacun des magasins classique et HPOS. Ces nouveaux tests PHP/natifs **n'ont pas été exécutés pendant cette correction** ; ils attendent le parent. Les preuves anciennes de `FINALISATION.md` ne prouvent pas ces changements. Aucune fixture fictive ne qualifie un site ni une donnée réelle.
