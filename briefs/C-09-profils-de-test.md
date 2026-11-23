# Lot C-09 — Les profils de test, créés par script

**Voie** : 2. **Chantier** : C. **Nature** : outillage. **Délai** : une demi-journée.
**Dépend de** : B-00.

## Pourquoi

`docs/recette/profils.md` décrit trente profils. Tant qu'ils n'existent pas sur un site, Ced ne peut ni les relire utilement ni tester. Ce lot les crée sur le site de démonstration ; le même script servira sur le staging d'Imagine.

## Ce qu'on veut

`wp/outils/demo/profils.ps1` (ou `.py`), rejouable :

- crée chaque profil de `docs/recette/profils.md` dans **l'état de départ décrit**, avec de vrais objets WooCommerce, Subscriptions et Memberships (commande, abonnement, adhésion), pas des drapeaux posés à la main ;
- identifiants prévisibles : le code du profil en minuscules (`a-carte`), adresse `a-carte@example.org` ; mots de passe générés, écrits dans le fichier hors dépôt de B-00 ;
- relancé, il remet chaque profil dans son état de départ ;
- refuse de s'exécuter sur un site dont le nom ne commence pas par `imagine-test-` (le staging d'Imagine sera autorisé plus tard, par consigne).

Les profils sont une **proposition non encore validée** par Ced : crée-les tels qu'ils sont écrits. Si un profil est impossible ou ambigu, ne l'invente pas : liste-le.

Les profils qui dépendent d'un lot non fait (abonnement groupé, offert, tarif solidaire, coopérateur) : crée ce qui est possible aujourd'hui et dis précisément ce qui manque.

## Livrables

- Le script.
- `production/C-09/A-VOIR.md` : un tableau des profils, **créé / partiel / impossible**, avec pour chacun une phrase sur ce qu'on voit en se connectant, et les profils à corriger dans `docs/recette/profils.md` selon toi.
- Preuve : pour chaque profil créé, la décision d'accès obtenue sur un article réservé (motif nommé).
- `production/C-09/PRET`.
