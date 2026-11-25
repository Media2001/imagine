# B-02 — Mon compte, squelette à inspecter

**Complément C09 du 25 novembre 2026 : 140/140 contrôles, dont 55/55 HTTP ; recette stricte sortie 2, acceptation encore partielle. A-SEPA4 est le profil quatre fois requis (a-4x-j45 était une erreur de brief, arbitrage de 16h30). Les marqueurs B02 relèvent du parent.**

Site exclusivement fictif : `http://192.168.129.32:8085`. Ouvrir `/my-account/` (page Woo existante, ID 9), ou le lien « Mon compte » dans l'en-tête. Se déconnecter avant de changer de personnage. Identifiants déjà présents hors dépôt dans `C:\Users\Ced\.imagine-demo\identifiants.json`, clé `c09_accounts`. Aucun mot de passe dans les preuves.

## À ouvrir

- **`a-carte`** : cinq sections, formule C09 FICTIF normal-1, état Actif, projection premier/dernier DEMO-2026-T4/DEMO-2027-T3 après normalisation des dates C09. Commande initiale payée fictive, 120 EUR synthétiques, inclusion positive dans le CSV postal C13 ; aucune carte/transaction réelle. Le nombre restant reste non raccordé (historique C01 absent). Le moyen de paiement reste nommé non raccordé par B02, car l’identifiant de passerelle est volontairement vide. Les PDF viennent de C11, pas d’un droit ajouté par B02.
- **`a-sepa4`** : le profil requis quatre fois, sans alias créé. **Deux paiements natifs fictifs sur quatre** existent : initiale processing et renouvellement processing, compteur natif WCS 2, prochaine action manuelle planifiée ; les deux suivantes restent à venir. **Limite B02 visible et conservée** : sa table lit seulement la commande initiale, donc montre une seule « Payée » et trois états non raccordés, pas 2/4. Sans marge C05, les quatre dates théoriques restent non raccordées. Premier/dernier natifs : DEMO-2026-T3/DEMO-2027-T2. Aucun mandat/jeton SEPA ni renouvellement automatique.
- **`a-susp`** : état Suspendu, renouvellement natif **failed fictif** à J-4, grâce finie J-1 ; bandeau « Échéance échouée » désormais attesté par HTTP, lien natif de gestion, aucun PDF dans Mes numéros. Zéro euro, aucun rejet bancaire réel. A-GRACE possède aussi un failed fictif, à J-1, et garde sa lecture en grâce.
- **`p-numero`** (complément C14) : un seul numéro/PDF T1 ; pas d'abonnement inventé.

## Coordonnées et isolation

« Modifier cette adresse postale » ouvre le **formulaire natif** `/my-account/edit-address/shipping/?subscription=89` pour a-carte. L'adresse affichée est celle de cette souscription, la source C13 utilisée par le postal ; pas une copie décorative de l'adresse client. Le gel des listes closes relève de C13 : ses corrections ont depuis été livrées et rejouées par le parent, mais B02 ne revendique pas cette preuve comme la sienne. La recette a réellement changé la rue synthétique, relu souscription/client/relevé postal/HTTP, puis restauré la rue et la date de modification. Deux observations postales et les notes natives de cette action sont conservées par parcours, jamais effacées.

En a-carte, remplacer l'identifiant par `107` (A-SUSP) dans `view-subscription`, `edit-address`, ou ajouter `?subscription=107&user_id=15&customer_id=15` au dashboard : aucune donnée d'A-SUSP. GET et POST forgé d'adresse ont été exercés. Hors session, seul le formulaire Woo est visible.

## Factures et limites

« Mes factures et justificatifs » existe même vide ; le raccord documentaire reste manquant. Les commandes ne sont pas appelées factures. L’inclusion postale d’A-CARTE est désormais attestée par le vrai export C13 ; son formulaire d’adresse conserve la même source postale. Rien n’est envoyé (email, paiement, connecteur).

Recette stricte réellement rejouée par `python wp/tests/demo/c09-strict-recipes.py B02` : fonction B02 inchangée, sans déploiement ; reçus seulement sous `production/C-09/complement-b02-resultats.json` et `complement-b02-http.json`. Snapshot natif/lots clos préservés, adresse restaurée exactement, deux nouvelles observations append-only conservées. Les seuls changements B02 sont des attentes dans les tests de démonstration, aucun code produit.

**Réserves actuelles** : seconde échéance payée non lue par B02, marge C05, historique/compteurs C01 et documents. Le runner conserve trois anciens libellés désormais périmés (a-4x-j45, aucun failed, A-CARTE impayé) : reçu brut préservé, pas repris comme constats actuels. Les sorties strictes 2 ne sont pas maquillées en acceptation complète.

Le §3.10 du cahier porte en réalité sur newsletters/segmentation, pas Mon compte : le minimum de cinq rubriques du brief est appliqué, sans ajouter un centre Brevo. Visuel à valider par Ced, besoins dans `besoins-designer.md`. Les nouvelles fusions `corrections/C-13.md` et `corrections/C-14.md` ont été signalées au parent ; B02 ne les résout pas et ne vaut pas acceptation de ces lots.
