# Parcours natif — 10 lignes (consultation officielle du 26 novembre 2026)
1. WooCommerce propose Commandes → Ajouter une commande : liste puis formulaire natif (deux écrans).
2. Le formulaire choisit un client existant, les lignes, les adresses et le statut « en attente de paiement ».
3. L’enregistrement ne demande pas d’inventer un registre de commandes.
4. Subscriptions propose Abonnements → Ajouter : liste puis formulaire de souscription.
5. On choisit client, calendrier et produits, puis on enregistre une souscription en attente.
6. L’action native « Create pending parent order » crée ensuite la commande parente impayée, ouvrable séparément.
7. Pour un client existant, liste + souscription + commande = trois écrans natifs, sans compter les fenêtres de lignes.
8. Un nouveau compte ajoute le parcours Utilisateurs ; la recherche par localité et « sans email » ne sont pas fournis dans ce flux.
9. Le raccord C16 ne remplace donc que la saisie : client, commande, confirmation ; les objets restent WC_Order/WC_Subscription.
10. Aucun envoi de facture, paiement, passerelle ou activation d’accès ; les produits et périodes sont ceux du catalogue fictif existant.

Sources officielles consultées :
- WooCommerce, « Single Order Page and Manually Adding an Order » : https://woocommerce.com/document/managing-orders/view-edit-or-add-an-order/
- WooCommerce Subscriptions, « Manually Add or Import a Subscription » : https://woocommerce.com/document/subscriptions/add-or-modify-a-subscription/
- WordPress `wp_insert_user` : https://developer.wordpress.org/reference/functions/wp_insert_user/
- WordPress `pre_wp_mail` : https://developer.wordpress.org/reference/hooks/pre_wp_mail/

Le comptage d’écrans est une lecture du parcours documenté, pas une mesure sur une installation commerciale neuve. Les extensions déjà actives sur la démo ne sont ni installées ni mises à jour par C16.

Décisions techniques prudentes : un brouillon serveur lié au référent expire après une heure ; aucune création avant la confirmation ; verrou par brouillon + email pour éviter les doublons ; sélection revalidée sur le catalogue à la confirmation ; aucun prix, taxe ou port Imagine inventé. Le compte « vente directe » n’a ni email envoyable ni identité personnelle.

Constat de départ : A-SANSMAIL ne portait aucun marqueur individuel natif (lecture réelle du 26/11). Le marqueur déjà employé dans la fixture sans email C13 est `imagine_sans_email` : C16 le réutilise, et C09 le pose désormais sur A-SANSMAIL, sans second marqueur. L’exclusion individuelle est raccordée à `pre_wp_mail`, y compris CC/BCC et adresses techniques `.invalid` ; aucun outil d’envoi externe n’est contacté.
