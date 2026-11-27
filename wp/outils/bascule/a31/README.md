# A-31 — Historique des commandes, lecture seule

L'outil compte, il ne répare, rattache ou supprime rien. La qualification native fait foi uniquement par l'unique paquet scellé `production/A-31/preuves/final/` et son lecteur sans argument ; `production/A-31/RECEPTION-PARENT.md` donne les commandes exactes. PHP s'exécute uniquement dans les conteneurs jetables déconnectés, jamais sur Windows. Un PRET technique n'est aucun GO réel.

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

Les branches publiques ne sont pas un numéro de version installé. `classic-standard.json` / `hpos-standard.json` lient par empreintes les sources effectivement installées avant le sujet, y compris `OrderInternalStatus` et `OrderStatus` : Woo 11.1.1 utilise des constantes natives, pas les anciennes chaînes littérales dans `wc_get_order_statuses()`. Aucun hash installé ne provient de GitHub.

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
- `orphan_renewals` : chaque commande à au moins une référence native de renouvellement positive absente du recensement des abonnements résolus par `wcs_get_subscription()` ; une fois par commande, même si plusieurs liens sont cassés. Les abonnements à la corbeille sont inclus dans le recensement d'existence, jamais dans les vivants. Le getter WCS n'est pas appelé sur un ID absent : son échec journalise dans les fichiers du site, ce qui contreviendrait à la lecture seule. Une référence opaque ne devient pas un lien numérique absent.
- **Vivants = exactement `active`, repris d'A-19 `Analysis::analyse` lignes 63–65, sans élargissement à A-20.** `living_without_parent` compte ces abonnements dont le parent est absent, nul ou n'est pas une commande ; cancelled/pending/on-hold/pending-cancel/expired/switched/draft exclus, comme A-19.
- `orders_missing_account` : commande à identifiant de compte positif dont `get_userdata()` ne retrouve pas le compte ; invité 0 exclu. `orders_link_unknown` distingue une commande native non lisible, sans la ranger arbitrairement dans les comptes supprimés. Abonnement/refund illisible : refus global fermé plutôt qu'un sous-comptage silencieux.
- K=5 : **uniquement `years` et `statuses` (années des commandes et années×états)** ; leurs cellules rares se fondent dans `autres` sans libellé. `orphan_renewals`, `living_without_parent`, `orders_missing_account`, `orders_link_unknown` sont quatre scalaires distincts exacts, de 0 à 4 inclus et au-delà, jamais additionnés. La consigne courante réserve K5 à ces deux ventilations : les natures et les remboursements par année sont donc exacts, sans fusion (`autres=0`), et `refunds.total` est la somme exacte de ses groupes. Cela remplace la réception antérieure qui masquait aussi leurs cellules rares. Une année rare de commande ne sort pas même via oldest : `fusionne`, jamais la première année visible suivante ; pas de commandes = null ; date manquante = `illisible`.
- JSON et Markdown publics à schéma fermé : aucun montant, identifiant de commande/compte/abonnement, jour, heure, numéro, email ou libellé source. Le seul lien technique est SHA-256 de l'audit ; pas de date d'audit recopiée. Tous les fichiers sont validés après fin réelle du processus, shutdown compris, avec liaison SHA-256 émise avant shutdown ; une altération cohérente JSON+Markdown est aussi refusée.

## Import A-28 gelé : lecture seule du code, pas de retouche

`wp/outils/staging/engine.php` : `sensitiveKey` (315–327) supprime notamment une clé de relation d'extension contenant une référence Stripe/PayPal ; `scrub`, puis `transform`, nettoient également des valeurs opaques. Notre fixture prépare `_subscription_stripe_subscription_id` : illisible avant import, clé supprimée ensuite, donc l'origine de la nature ne peut plus être certifiée. Les métadonnées WCS standards ne sont pas volontairement supprimées ; cela ne suffit pas à certifier les références tierces disparues.

Défaut prudent explicite : après le marqueur de provenance `imagine_staging_disabled_plugins`, **natures = `inconnu après neutralisation`** (pas zéro), car une relation tierce détruite ne doit pas redevenir une preuve « sans abonnement ». Restent lisibles : années/états des commandes, renouvellements orphelins **sur les clés WCS standards numériques**, parent original des abonnements actifs, comptes manquants, remboursements par année et oldest sous K5. L'import conserve leurs dates de création, états, IDs, clés `_subscription_renewal` et parents structurels ; les identités affichées sont anonymisées, mais A-31 ne les lit pas. Un lien de renouvellement opaque n'est jamais converti en ID, avant ou après import. La banque parent clone une DB fictive, appelle réellement `neutraliser()` puis `anonymiser()` de l'import inchangé, mesure la disparition de cette clé d'extension, la conservation des trois liens renewal numériques (corbeille comprise) et des empreintes structurelles, puis exige ce résultat partiellement inconnu. La validité de cette preuve dépend du reçu natif complet courant, jamais des seules assertions préparées.

## Tests

```sh
C:/Python314/python.exe -B -m unittest discover -s wp/tests/a31 -p "test_*.py" -v
C:/Python314/python.exe -B wp/tests/a31/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-python-neuf
```

Python ne simule pas un verdict PHP : il teste les vrais sous-processus Python/pipes A-22, les refus, les schémas, le confinement de publication et les mutations de validateurs dans des copies scratch. La matrice mesure Windows UTF-8 et cp1252 séparément. La qualification complète exige PHP pur, doubles de frontière, code installé, classique/HPOS, empreintes SQL/fichiers et refus mail/HTTP/cron/AS dans les quatre cellules, plus PSR-12 strict et les gates communs. Les seules exceptions de style sont les noms imposés par Woo/WCS et la cohabitation symboles/effets des deux scripts de fixture ; aucun contrôle de production n'est exclu. Un code 255 n'est jamais un succès. `production/A-31/verify.py` sans argument refuse une preuve Python seule ou l'absence du paquet final.
