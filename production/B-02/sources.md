# B-02 — Standard avant le raccord

Actualisation du 25 novembre 2026 (corrections) : documentation officielle relue directement, sans installation :
- `https://woocommerce.com/document/subscriptions/customers-view/` : gestion native des souscriptions, commandes initiales/renouvellements, adresses et moyens de paiement.
- `https://woocommerce.com/document/subscriptions/develop/functions/` : `get_date(type, 'gmt')`, méthodes de relations natives de WC_Subscription ; aucune mise à jour de dates invoquée par B02.
- `https://woocommerce.com/document/bacs/` : circuit de virement manuel distinct d’une simple attente administrative. B02 n’active ni ne configure ce circuit.

La source de droits reste C11/C14 ; le cœur B02 ne fait que projeter des libellés/positions. Aucun code ou réglage des bibliothèques closes modifié.

Documentation officielle consultée dans le navigateur (extraction directe indisponible sur ce backend ; aucune installation pour la contourner) :

- `https://woocommerce.com/document/subscriptions/customers-view/` : My Account natif, liste et détail de souscription, dates/total/méthode, commandes associées, changement d'adresse et paiement des renouvellements échoués.
- `https://developer.woocommerce.com/docs/extensions/core-concepts/wc-get-orders/` : CRUD/query Woo, filtrage client, compatibilité HPOS ; pas de SQL métier pour lire les commandes.

Source native installée lue : `woocommerce-subscriptions/includes/core/class-wc-subscriptions-addresses.php` (9.4.1). Les routes `edit-address`, vérification de propriétaire/capacité, nonces Woo et `_wcsnonce`, préremplissage et sauvegarde de souscription existent déjà. B02 réutilise ces parcours, sans formulaire ni paiement maison.

Bibliothèques closes lues et inchangées : `Numeros/{Annee,Moteur,Calendrier,Numero}`, `Echeancier/{Planificateur,Versement,ReglagesAdministration,RaccordManuel}` ; C01 donne la projection des quatre numéros, C05 exige une marge explicite. C13 `EnvoiNatif` reste la source du relevé postal. C11/C14 restent seuls juges du droit PDF.

Contradiction documentaire : le brief B02 renvoie au §3.10 ; ce paragraphe est « Newsletters et segmentation ». Les cinq rubriques explicites du brief sont donc le contrat du squelette ; aucun centre Brevo ajouté.
