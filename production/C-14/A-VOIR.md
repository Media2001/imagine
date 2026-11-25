# C-14 — achat d'un numéro (démonstration uniquement)

**État : implémenté et exercé, vérification indépendante du parent attendue. Aucun PRET créé.**

## Parcours à ouvrir

Le « V-NUM » du brief correspond au profil existant **P-NUMERO**, login **p-numero** (compte 28). On conserve les identifiants C09, sans créer un 31e profil. Les mots de passe fictifs restent dans `C:\Users\Ced\.imagine-demo\identifiants.json`, jamais dans ce dossier.

1. Se connecter à `http://192.168.129.32:8085/wp-login.php` avec ce profil.
2. Ouvrir `http://192.168.129.32:8085/demo-2026-t1-reserve-1/` : article complet, pas de bloc d'abonnement. Le droit provient de la commande **126** du produit **271**, numéro **11**.
3. Ouvrir `http://192.168.129.32:8085/numeros/demo-2026-t1/`, puis `http://192.168.129.32:8085/?imagine_pdf=11` : lien et PDF fictif téléchargé après contrôle serveur ; octets vérifiés par HTTP.
4. Ouvrir `http://192.168.129.32:8085/demo-2026-t2-reserve-1/` et `http://192.168.129.32:8085/?imagine_pdf=18` : extrait/bloc abonnement, aucun PDF. L'achat n'ouvre pas ce numéro.
5. Refaire les deux liens T1 en navigation privée : article réduit et PDF refusé avec retour à la page du numéro.
6. Avec E-ADMIN : `http://192.168.129.32:8085/wp-admin/post.php?post=271&action=edit`. Dans les données générales du produit simple : **Numéro à l'unité**, valeur T1 (#11). Vider ou réaffecter ce champ ferme les anciens droits, sans les déplacer. Ne pas modifier durablement le témoin pendant la relecture.

La commande fictive se consulte avec E-ADMIN à `http://192.168.129.32:8085/wp-admin/admin.php?page=wc-orders&action=edit&id=126` : processing/date payée **de fixture**, montant zéro, aucune passerelle ni transaction. Ce n'est pas une preuve de paiement bancaire.

## Règles et limites

- Seuls le propriétaire natif connecté, processing/completed, `is_paid()` et une date payée valide donnent un achat au moteur C06 inchangé. Commandes non payées, remboursées ou supprimées : fermées. Tout remboursement natif, y compris partiel/non ventilé, retire le droit de cette commande ; une autre commande valide reste indépendante.
- Instantané du numéro sur la ligne à sa création, concordance obligatoire avec le mapping courant. Pas de reprise automatique d'anciennes lignes, ni de transfert de droits lors d'une réaffectation de produit. Produits simples seulement, modèle provisoire du brief.
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

Choix : utiliser les commandes/produits/lignes/refunds CRUD natifs ; ne pas créer un plan Memberships par numéro, ni un second circuit PDF contournant C08/C11. Le sur-mesure ne fait que relier la ligne native au contrat `achat` déjà fourni par C06.

Rejeu et résultats : `COMMANDES.md`, `resultats.json`, `regressions.json`. Aucun accord visuel ou GO sur le réel n'est revendiqué.
