# C-14 — achat d'un numéro (démonstration uniquement)

**État : corrections C14-01/02/03 implémentées et exercées, relecture indépendante attendue. Le PRET initial du parent existe (25 novembre, 13:25 CET) ; il n’a été ni créé ni modifié ici et ne vaut pas validation des corrections. Relecture uniquement, pas clôture ni GO réel.**

## Parcours à ouvrir

Le « V-NUM » du brief correspond au profil existant **P-NUMERO**, login **p-numero** (compte 28). On conserve les identifiants C09, sans créer un 31e profil. Les mots de passe fictifs restent dans `C:\Users\Ced\.imagine-demo\identifiants.json`, jamais dans ce dossier.

1. Se connecter à `http://192.168.129.32:8085/wp-login.php` avec ce profil.
2. Ouvrir `http://192.168.129.32:8085/demo-2026-t1-reserve-1/` : article complet, pas de bloc d'abonnement. Le droit provient de la commande **126** du produit **271**, numéro **11**.
3. Ouvrir `http://192.168.129.32:8085/numeros/demo-2026-t1/`, puis `http://192.168.129.32:8085/?imagine_pdf=11` : lien et PDF fictif téléchargé après contrôle serveur ; octets vérifiés par HTTP.
4. Ouvrir `http://192.168.129.32:8085/demo-2026-t2-reserve-1/` et `http://192.168.129.32:8085/?imagine_pdf=18` : extrait/bloc abonnement, aucun PDF. L'achat n'ouvre pas ce numéro.
5. Refaire les deux liens T1 en navigation privée : article réduit et PDF refusé avec retour à la page du numéro.
6. Avec E-ADMIN : `http://192.168.129.32:8085/wp-admin/post.php?post=271&action=edit`. Champ **Numéro à l'unité**, valeur T1 (#11). Vider/réaffecter/supprimer le produit **conserve A, sans ouvrir B aux anciens acheteurs**. Seuls les achats suivants utilisent le nouveau mapping. Ne pas modifier durablement ce témoin : les tests mutateurs utilisent leurs propres objets jetables.
7. Avec E-ADMIN, **Réglages → Achats de numéros** : `http://192.168.129.32:8085/wp-admin/options-general.php?page=imagine-achats`. Réglage minimal « Portée des remboursements », défaut effectif final `commande`, question « À confirmer par Imagine ».

La commande fictive se consulte avec E-ADMIN à `http://192.168.129.32:8085/wp-admin/admin.php?page=wc-orders&action=edit&id=126` : processing/date payée **de fixture**, montant zéro, aucune passerelle ni transaction. Ce n'est pas une preuve de paiement bancaire.

## Règles et limites

- Propriétaire natif connecté, processing/completed, `is_paid()` et date payée valide : contrôles conservés. Commandes non payées/supprimées, quantité zéro, instantané retiré/invalide et numéro acquis dépublié/supprimé : fermé. Le moteur C06 reste inchangé.
- **Seule référence du numéro acquis : l’instantané figé sur la ligne à sa création**, indépendant du produit courant. Aucun rétro-octroi, aucune régénération d’instantané sur une ancienne ligne. Produits simples seulement.
- `imagine_achat_remboursement=commande` (défaut prudent, absent/invalide aussi) : tout remboursement natif, même partiel/non ventilé, retire toutes les acquisitions de la commande. Alternative `ligne` : seule la ligne produit référencée par `_refunded_item_id` perd son achat, même pour une quantité partielle ; les autres restent acquises. **En mode ligne, un partiel non ventilé ne retire aucune ligne** ; un remboursement uniquement sur le port ne désigne pas de ligne produit. Un remboursement **complet** ferme tous les numéros dans les deux modes. Une autre commande valide reste indépendante.
- Le cahier §3.7 prévoit l'achat papier invité et propose ensuite la création d'un compte pour le numérique. **L'achat invité reste fermé ici** tant qu'aucun compte n'est rattaché à la commande ; aucun rapprochement par email. Le parcours de revendication après achat n'est pas livré par C14.
- PDF : stockage et contrôleur C11 conservés ; pas de fichier/URL de téléchargement Woo public. Aucun achat réel, email sortant, compte externe, licence ou déploiement hors démo.
- Le brief cite §3.11, qui concerne les événements : les dispositions pertinentes sont §3.7 et §3.9 (articles/PDF sans durée de fin).

## Standards consultés

Références officielles consultées le 25 novembre 2026, sans achat ni compte fournisseur :

- WooCommerce, requêtes de commandes et pagination : https://developer.woocommerce.com/docs/extensions/core-concepts/wc-get-orders/
- WooCommerce, états de commande : https://woocommerce.com/document/managing-orders/order-statuses/
- WooCommerce, objets CRUD et hooks de sauvegarde : https://developer.woocommerce.com/docs/best-practices/data-management/crud-objects/
- WooCommerce, restrictions Memberships par plans/contenus : https://woocommerce.com/document/woocommerce-memberships-restrict-content/
- WooCommerce, téléchargements et limites de protection des URL : https://woocommerce.com/document/digital-downloadable-product-handling/
- Source officielle du hook produit : https://github.com/woocommerce/woocommerce/blob/trunk/plugins/woocommerce/includes/admin/meta-boxes/class-wc-meta-box-product-data.php
- WordPress Settings API (correction C14-02) : https://developer.wordpress.org/plugins/settings/settings-api/
- Source officielle `wc_create_refund`, `line_items`, `_refunded_item_id`, `refund_payment=false`, filtre partiel/complet : https://raw.githubusercontent.com/woocommerce/woocommerce/trunk/plugins/woocommerce/includes/wc-order-functions.php

Choix : utiliser les commandes/produits/lignes/refunds CRUD natifs ; ne pas créer un plan Memberships par numéro, ni un second circuit PDF contournant C08/C11. Le sur-mesure ne fait que relier la ligne native au contrat `achat` déjà fourni par C06.

## Terminé / encore attendu

Terminé : oracles purs/natifs/HTTP corrigés ; deux numéros, deux modes, partiels ventilés/non ventilés et complets ; dépublication/republication et retrait d’instantané ; vrais POST Settings API avec persistance native, nonce et refus client ; nettoyage exact relu ; préparation image et suite complète autorisée.

Dernier rejeu : **686/686** contrôles C14 et raccords, **205/205** régressions complémentaires, **T01 1012 tests / 34006 assertions**, zéro échec/erreur/ignoré. Les suites se recouvrent : ne pas les additionner comme des tests distincts. `COMMANDES.md`, `validation-corrections.json`, reçus et `validation-*.log` donnent commandes/résultats réels.

Attendu : vérification indépendante du parent et relectures des corrections. Aucun accord visuel, clôture ni GO sur le réel. La question métier ne bloque pas : réglage livré au défaut fermé. `PROPOSITIONS-DOCS.md` fournit les ajouts proposés à `docs/ecarts.md` et `docs/decisions.md`, sans modifier ces fichiers interdits.

Incident transparent : les deux premiers diagnostics de C11 ont ajouté **12 observations synthétiques C13**, souscriptions C08 77/79, lors des changements temporaires de plans. Plans restaurés, aucun ancien événement modifié/effacé ; noms et dates dans `incident-observations-c13.json`. Depuis la correction du runner, cette seule recette tourne en transaction InnoDB rollbackée, callbacks inclus ; les derniers rejeux conservent exactement l’état partagé, historique compris. Ne pas confondre cette conservation finale avec une absence d’effet lors des diagnostics antérieurs.

Les remboursements exercés sont à zéro, sans restock, passerelle ni transfert. Pour un partiel non ventilé à zéro, le filtre natif `woocommerce_order_is_partially_refunded` est borné à la seule commande de fixture pour lever l’ambiguïté 0=0 ; ce n’est pas une preuve bancaire. N+1 des remboursements conservé (optionnel, volume démo).
