# B-02 — Mon compte, squelette à inspecter

**Technique vérifiée ; acceptation nominative partielle. Aucun PRET déposé.**

Site exclusivement fictif : `http://192.168.129.32:8085`. Ouvrir `/my-account/` (page Woo existante, ID 9), ou le lien « Mon compte » dans l'en-tête. Se déconnecter avant de changer de personnage. Identifiants déjà présents hors dépôt dans `C:\Users\Ced\.imagine-demo\identifiants.json`, clé `c09_accounts`. Aucun mot de passe dans les preuves.

## À ouvrir

- **`a-carte`** : cinq sections, formule C09 FICTIF normal-1, état Actif, projection premier/dernier DEMO-2026-T1/T4. Le nombre restant est nommé non raccordé (historique C01 absent). Prochaine date native et total récurrent natif 120 EUR de fixture, **aucune carte ou transaction attestée**. Les PDF admissibles sont ceux de C11, pas un nouveau droit.
- **`a-4x-j45`** : **impossible à ouvrir : compte absent de C09 et du site**. Il n'a pas été créé, renommé ou assimilé à A-SEPA4. Pour inspecter uniquement la structure quatre fois, utiliser **`a-sepa4`**, profil partiel existant : quatre lignes, première commande réellement en attente, autres états nommés non raccordés. Sans marge C05, dates non raccordées ; aucun 2/4 ni mandat SEPA inventé. Ce témoin ne satisfait pas la réception nominative A-4x-J45.
- **`a-susp`** : état Suspendu, bandeau avec lien natif de gestion, aucun PDF dans Mes numéros. Le texte ne prétend pas qu'un rejet bancaire a réellement eu lieu. Aucun ordre `failed` disponible dans ces profils : l'action de paiement échoué n'a donc pas sa preuve HTTP positive.
- **`p-numero`** (complément C14) : un seul numéro/PDF T1 ; pas d'abonnement inventé.

## Coordonnées et isolation

« Modifier cette adresse postale » ouvre le **formulaire natif** `/my-account/edit-address/shipping/?subscription=89` pour a-carte. L'adresse affichée est celle de cette souscription, la source C13 utilisée par le postal ; pas une copie décorative de l'adresse client. Le gel des listes closes relève de C13 : ses corrections ont depuis été livrées et rejouées par le parent, mais B02 ne revendique pas cette preuve comme la sienne. La recette a réellement changé la rue synthétique, relu souscription/client/relevé postal/HTTP, puis restauré la rue et la date de modification. Deux observations postales et les notes natives de cette action sont conservées par parcours, jamais effacées.

En a-carte, remplacer l'identifiant par `107` (A-SUSP) dans `view-subscription`, `edit-address`, ou ajouter `?subscription=107&user_id=15&customer_id=15` au dashboard : aucune donnée d'A-SUSP. GET et POST forgé d'adresse ont été exercés. Hors session, seul le formulaire Woo est visible.

## Factures et limites

« Mes factures et justificatifs » existe même vide ; le raccord documentaire est nommé manquant. Les commandes restent accessibles par leur lien natif et ne sont pas appelées factures. A-CARTE n'a pas de paiement validé : cette recette prouve la **même source postale**, pas son inclusion positive dans un export C07. Rien n'est envoyé (email, paiement, connecteur).

Le §3.10 du cahier porte en réalité sur newsletters/segmentation, pas Mon compte : le minimum de cinq rubriques du brief est appliqué, sans ajouter un centre Brevo. Visuel à valider par Ced, besoins dans `besoins-designer.md`. Les nouvelles fusions `corrections/C-13.md` et `corrections/C-14.md` ont été signalées au parent ; B02 ne les résout pas et ne vaut pas acceptation de ces lots.
