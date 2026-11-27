# A-31 — Historique des commandes, lecture seule

**Candidat non qualifié nativement : aucun PRET, aucun GO réel.** L'outil compte, il ne répare, rattache ou supprime rien. `production/A-31/RECEPTION-PARENT.md` est la réception exacte. Le parent possède Docker/WSL ; le worker n'a lancé ni PHP Windows, ni conteneur, ni site.

## Le standard d'abord — huit lignes

1. WooCommerce distingue `shop_order`, `shop_order_refund` et WCS `shop_subscription` ; un remboursement est un objet séparé, pas le montant négatif d'une commande [S1,S2].
2. Le parent d'un abonnement est sa commande d'origine ; le getter natif est `WC_Subscription::get_parent_id('edit')`, puis `wc_get_order()` vérifie que cette commande existe [S1,S3].
3. WCS déclare trois relations supplémentaires : `renewal`, `switch`, `resubscribe` ; une commande peut concerner plusieurs abonnements [S2,S3].
4. Les getters WCS usuels sont `wcs_get_subscriptions_for_order()` et `WC_Subscription::get_related_orders()` ; ils retournent des objets existants, donc seuls ils masqueraient un renouvellement orphelin [S1,S2].
5. Le lecteur natif `WCS_Related_Order_Store_CPT::get_related_subscription_ids($order,$type)` lit les références avant résolution ; le suffixe CPT n'interdit pas HPOS : il utilise `WC_Data::get_meta()` [S3].
6. Ces trois clés natives sont `_subscription_renewal`, `_subscription_switch`, `_subscription_resubscribe` ; les valeurs brutes sont contrôlées avant la normalisation native `absint`, sinon une valeur opaque deviendrait un faux lien [S3].
7. A-31 initialise le magasin WCS standard, puis appelle son lecteur natif non caché : le wrapper Cached peut écrire des caches de relations ; une substitution du magasin est refusée, une relation inconnue devient illisible [S3].
8. `OrderUtil::custom_orders_table_usage_is_enabled()` choisit l'unique magasin faisant autorité ; SELECT énumère tous ses IDs/types, même les états non enregistrés, puis Woo/WCS lisent les objets ; `standard.php` doit qualifier et empreinter le code réellement installé avant le sujet, dans chacun des magasins [S1,S4].

Sources primaires consultées le 27 novembre 2026 (documentation/code public, **pas** preuve du code installé) :
- S1 : https://woocommerce.com/document/subscriptions/develop/data-structure/
- S2 : https://woocommerce.com/document/subscriptions/develop/functions/order-cart-functions/
- S3 : https://raw.githubusercontent.com/Automattic/woocommerce-subscriptions-core/trunk/includes/abstracts/abstract-wcs-related-order-store.php et https://raw.githubusercontent.com/Automattic/woocommerce-subscriptions-core/trunk/includes/data-stores/class-wcs-related-order-store-cpt.php
- S4 : https://developer.woocommerce.com/docs/features/high-performance-order-storage/ et https://raw.githubusercontent.com/woocommerce/woocommerce/trunk/plugins/woocommerce/includes/wc-order-functions.php

Les branches publiques ne sont pas un numéro de version installé. Le parent produit `classic-standard.json` / `hpos-standard.json` avec les empreintes et contrôles des sources installées ; aucune empreinte installée n'est supposée ici.

## Commande de l'outil, sans option cachée

Linux déconnecté, PHP 8.2+, Python 3, Landlock ; copie fictive, ou copie vérifiée avec GO nominatif de Ced et réserve A-22 levée. Audit A-02 déjà produit ; sortie neuve dans un parent existant hors du site/dépôt, pas un ancêtre ; audit dans un sous-dossier de ce même parent.

```sh
python3 wp/outils/bascule/a31/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/commandes-date
```

La banque relit cette ligne et remplace seulement ses chemins, sans ajouter d'argument. Succès exact : code 0, stdout `A31_OK commandes.json commandes.md` puis LF, stderr vide. Refus : code 1, stdout vide et code fermé ; aucun chemin ni valeur du site recopié. Le gardien commun A-22 reste intact.

## Définitions de comptage

- Périmètre : toutes les commandes natives non mises à la corbeille dans le magasin faisant autorité, indépendamment du compte, du paiement et de la nature. Les remboursements sont comptés séparément. Les backups classiques/HPOS ne sont pas additionnés. Aucun montant lu par A-31.
- Année : création de la commande, en UTC, jamais paiement/modification/renouvellement prévu. Une date absente devient `illisible`. `statuses` croise année × état ; liste fermée Woo : pending, processing, on-hold, completed, cancelled, refunded, failed, checkout-draft ; toute autre valeur devient `autre`, sans son nom.
- Nature : parent, renewal, switch, resubscribe, none ; référence illisible, extension hors contrat, lecteur natif contradictoire ou plusieurs natures simultanées = `illisible`, jamais none. Plusieurs abonnements d'une même nature ne doublent pas la commande. Parent porte sur tous états d'abonnement, pas seulement les vivants.
- `orphan_renewals` : chaque commande à au moins une référence native de renouvellement positive dont `wcs_get_subscription()` ne retrouve pas l'abonnement ; une fois par commande, même si plusieurs liens sont cassés. Une référence opaque ne devient pas un lien numérique absent.
- **Vivants = exactement `active`, repris d'A-19 `Analysis::analyse` lignes 63–65, sans élargissement à A-20.** `living_without_parent` compte ces abonnements dont le parent est absent, nul ou n'est pas une commande ; cancelled/pending/on-hold/pending-cancel/expired/switched/draft exclus, comme A-19.
- `orders_missing_account` : commande à identifiant de compte positif dont `get_userdata()` ne retrouve pas le compte ; invité 0 exclu. `orders_link_unknown` distingue une commande native non lisible, sans la ranger arbitrairement dans les comptes supprimés. Abonnement/refund illisible : refus global fermé plutôt qu'un sous-comptage silencieux.
- K=5 : chaque cellule année, année/état, nature, relation et remboursement/année n'a un libellé qu'à partir de cinq ; les cellules rares se fondent dans `autres` sans libellé. Les métriques structurelles n'ont pas la même unité ; leur somme rare n'est pas un nombre de personnes. Une année rare ne sort pas même via oldest : `fusionne`, jamais la première année visible suivante ; pas de commandes = null ; date manquante = `illisible`.
- JSON et Markdown publics à schéma fermé : aucun montant, identifiant de commande/compte/abonnement, jour, heure, numéro, email ou libellé source. Le seul lien technique est SHA-256 de l'audit ; pas de date d'audit recopiée. Tous les fichiers sont validés après fin réelle du processus, shutdown compris, avec liaison SHA-256 émise avant shutdown ; une altération cohérente JSON+Markdown est aussi refusée.

## Import A-28 gelé : lecture seule du code, pas de retouche

`wp/outils/staging/engine.php` : `sensitiveKey` (315–327) supprime notamment une clé de relation d'extension contenant une référence Stripe/PayPal ; `scrub` (219–284), puis `transform` (451–492), nettoient également des valeurs opaques. Notre fixture prépare `_subscription_stripe_subscription_id` : illisible avant import, clé supprimée ensuite, donc l'origine de la nature ne peut plus être certifiée. Les métadonnées WCS standards ne sont pas volontairement supprimées ; cela ne suffit pas à certifier les références tierces disparues.

Défaut prudent explicite : après le marqueur de provenance `imagine_staging_disabled_plugins`, **natures et renouvellements orphelins = `inconnu après neutralisation`** (pas zéro). Le second inconnu est conservateur pour les références complémentaires détruites ; ce n'est pas l'affirmation que chaque clé `_subscription_renewal` est purgée. Restent lisibles : années/états des commandes, parent original des abonnements actifs, comptes manquants, remboursements par année et oldest sous K5. L'import conserve leurs dates de création, états, IDs et parents structurels ; les identités affichées sont anonymisées, mais A-31 ne les lit pas. La banque parent clone une DB fictive, appelle réellement `neutraliser()` puis `anonymiser()` de l'import inchangé, mesure la disparition de cette clé, la conservation des deux liens renewal et des empreintes structurelles, puis exige ce résultat partiellement inconnu. **Cette preuve est préparée, non exécutée par le worker.**

## Tests

```sh
C:/Python314/python.exe -B -m unittest discover -s wp/tests/a31 -p "test_*.py" -v
C:/Python314/python.exe -B wp/tests/a31/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-python-neuf
```

Python ne simule pas un verdict PHP : il teste les vrais sous-processus Python/pipes A-22, les refus, les schémas, le confinement de publication, les mutations de validateurs dans des copies scratch et les contrats des banques préparées. La matrice mesure Windows UTF-8 et cp1252 séparément. PHP pur, doubles de frontière, code installé, classique/HPOS, empreintes SQL/fichiers et sorties mail/HTTP/cron/AS attendent la matrice parent documentée dans la réception. Un code 255 n'est jamais un succès. `production/A-31/verify.py` sans argument refuse une preuve Python seule ou l'absence du paquet final.
