Fait : corrections C13 appliquées au raccord natif : bénéficiaires, renouvellements C01, gel persistant, logique pure et libellés.
Prêt à relire : avec réserves d’acceptation C09 seulement ; ni recette complète, ni validation visuelle, ni clôture. PRET relève exclusivement du parent, sans création/modification par ce worker.
À valider par Ced : coexistence visuelle des menus C10/C13 ; aucune question technique n’attend Ced.
Bloqué : acceptation nominative C09 : 12/12 souscriptions sans paiement validé, 0 destinataire, A-SANSMAIL exclu ; liens offert/groupe C09 absents.
Ensuite : rejeu indépendant du parent ; aucun changement de C09, C14, B02 ou bibliothèque close.

## Corrections et décisions prises à défaut

- `EnvoiRegles.php` est pur : horloge/calendrier/observations injectés ; il délègue les blocs à C01 et les lignes/éligibilité/CSV à C07. `EnvoiNatif` conserve uniquement lectures, hooks et persistance.
- Cadeaux : lien natif WCS Gifting, identité bénéficiaire et adresse de livraison ; cadeau requis sans relation résolue = export fermé, jamais le payeur en remplacement. Groupes : attributions Memberships natives `_subscription_id`, identité/adresse des membres, capacité issue des quantités des produits des plans configurés. Deux places attribuées sur trois donnent deux personnes ; une place libre n’en invente aucune.
- **Réglage métier prudent**, visible seulement à l’administrateur dans l’écran : `imagine_envoi_groupes=ferme|liens_memberships`, défaut **ferme**. Les deux valeurs sont éprouvées. Le modèle « quantité = places, attributions Memberships » reste à confirmer par Imagine ; aucun adaptateur Teams absent n’est revendiqué.
- Renouvellements : commandes natives reliées, payées/date enregistrée, propriétaire cohérent, sans remboursement ; C01 `renouveler()` enchaîne les blocs sans toucher au début initial. Défaut annuel intervalle 1 ; les échéances trimestrielles ne sont pas des années. Pour un autre cycle, un début de bloc explicitement enregistré est requis. Un dernier paiement recopié par WCS ne reconstitue pas le paiement initial absent.
- Référence historique persistante et gel par numéro : calendrier, clôture, observations, blocs C01. Réécriture native d’une clôture passée ou d’un gel refusée ; liste figée relue sans calendrier courant. Historique/calendrier incomplet ou bénéficiaires requis non résolus ferment l’export. Égalité à la clôture exclue.
- Observations append-only sur les vrais hooks Subscriptions, Memberships et adresses client ; déduplication des rejeux. Le rafraîchissement GET reste idempotent avant clôture : coût linéaire à surveiller, aucune promesse de volume réel.

## Résultats réellement exécutés

- `preparer-image.ps1` : **0**, image préparée/vérifiée ; le paquet `imagine-site` est désormais découvert automatiquement sans toucher au runner fermé ni à T01.
- `rejouer.ps1` : **1010 tests, 33978 assertions, 0 échec/erreur/ignoré**, code **0**. Dont `imagine-site` : **46 tests, 230 assertions** (C11 conservé + C13).
- C13 pur autonome : **10 tests, 30 assertions**, code **0**, sans WordPress ni réseau.
- Démonstration PHP/HTTP réelle : **74 contrôles verts**, deux CSV de deux lignes BE/FR ; sources B02/C14/fermées relues conformes et préservées, états C09/rôles/options/contenus inchangés.
- Mode strict : **2**, `recette_complete=false` ; ce code n’est pas un succès d’acceptation. Les témoins fictifs C13 ne remplacent pas les profils C09.
- Les liens cadeau/groupe et renouvellements sont éprouvés sur de nouveaux objets jetables, nettoyés et relus absents. Une commande de renouvellement à zéro reçoit explicitement statut/date **fictifs** ; WCS recopie cette date sur sa souscription jetable. Aucun profil actif existant n’est transformé en paiement, aucun `payment_complete()`, transport ou règlement bancaire.

## Limites et écarts proposés à Claude (aucune écriture dans docs/)

1. « §3.13 contredit le brief C13 sur les abonnés sans email ; le brief postal est appliqué : aucun filtre email, sous réserve des autres droits. A-SANSMAIL reste exclu pour paiement non validé, pas pour absence d’email. »
2. « Le raccord cadeau/groupe est désormais livré et testé sur relations natives fictives ; les profils C09 correspondants restent sans lien natif, donc leur acceptation positive n’est pas acquise. Ne plus présenter cela comme une absence du code C13. »
3. « Un statut administratif actif sans paiement ne vaut pas expédition ; aucun complément C09 sans preuve native n’est créé. La préparation de fixtures est technique et autorisée, mais ne change ni états C09 ni règle de droit. Le modèle collectif est isolé derrière un réglage fermé par défaut, à confirmer par Imagine. »

Les rouges initiaux ont révélé notamment la fin WCS à `0`, l’intervalle natif chaîne `"1"`, la recopie du dernier paiement sur la souscription et le nonce de réglages distinct du nonce d’export ; corrections rejouées après écriture finale. Commandes : `COMMANDES.md` ; reçus compacts : `resultats.json`, `resultats-purs.json`. Aucun GO réel ni PRET émis.
