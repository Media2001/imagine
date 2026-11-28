# C-30 — Bienvenue, corrections du 28 novembre

Démo uniquement : http://192.168.129.32:8085/bienvenue/ . Texte Imagine vide et lien S’abonner, même page avec code fictif connu, inconnu ou absent. Aucun avantage financier, prix, coupon ni identité affichée.

Codes : `fictif-affiche`, `fictif-magazine`, `fictif-evenement`. Dernier code valide connu avant commande ; un inconnu n’écrase rien. Session native WooCommerce, aucun script ni traceur ajouté par C30. Inventaire effectif des cookies et écart de l’attribution native : C32, sans extinction de fonctionnalité ici.

Administration : Réglages → Codes suivis ; Imagine → Codes suivis. L’aide dit désormais **lettre minuscule initiale**, puis minuscules/chiffres/tirets, 1 à 40 caractères ; `2026-affiche` est refusé. Comptage **historique**, par code rangé sur la commande : retirer un code du catalogue ne retire pas les anciens nombres. Bornes UTC incluses, aucun nom de lecteur.

Candidat provisoire privé `_imagine_code_suivi_candidat` aux checkouts classique **et Store API**, par son hook natif `woocommerce_store_api_checkout_order_processed`. Seules les commandes payées/datées reçoivent la conversion scellée unique ; C16 exclu. Le raccord est prouvé sur le hook natif installé et dans l’adaptateur scellé ; il ne prétend pas qualifier un paiement HTTP Store API réel hors ligne.

Export/effacement C21 : union ordonnée des commandes du compte et des commandes **invitées** de la même adresse vérifiée, dédoublonnage ID, pagination stable. Compte/invité effacés ; tiers préservé, même s’il a utilisé cette adresse avec un autre compte. Panne de lecture/verrou/suppression relue : effacement incomplet (`items_retained`). Sceau conservé contre recréation.

Preuves courantes : `correction-native-final-V2.json` (32 contrôles, panier et commandes Woo réels), `correction-unit-final-V2.json` (9 tests / 165 assertions), `correction-browser-final-V2.json` (99 contrôles / 10 réponses), capture et restitution exacte des sessions. Le même produit fictif payant, quantité deux, est calculé et commandé avec/sans code ; comparaison des totaux, taxes, remises et coupons. Une remise-sonde liée au code fait échouer le même comparateur et est retirée. Produit/commandes rollbackés, tâches natives de cache WCS de shutdown restaurées depuis préimage privée et relues ; aucun paiement/email.

```bash
python -B production/C-30/verifier.py --live
python -B wp/outils/demo/c30-unit.py nouvelle-unit-V2
python -B wp/outils/demo/c30.py native nouvelle-native-V2
python -B wp/outils/demo/c30-browser.py nouveau-browser-V2
```

Réception : `reception-corrections-V2.json`, puis PRET technique. Anciens reçus et échecs conservés, préimages de code/lecteur/PRET/A-VOIR dans `avant-corrections-V2/`. Le premier test renforcé a révélé un produit B04 gratuit (remplacé uniquement dans le test par un produit fictif payant) et un rapport WCS différé hors transaction : échec conservé et restauration initiale exacte prouvée par `correction-recovery-essai2-V2.json`. Aucun profil réinitialisé, autre site ou bibliothèque close modifié. Coût des comptes par période laissé inchangé, optimisation SQL non urgente différée conformément à l’instruction 7.
