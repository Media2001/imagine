# Lot C-14 — L'achat d'un numéro ouvre ce numéro

**Voie** : 2. **Délai** : une demi-journée. **Dépend de** : C-08, C-11 (clos). **Cahier des charges** : §3.9 et §3.11 pour l'achat à l'unité.

Aujourd'hui, l'acheteur d'un numéro (profil V-NUM) ne voit rien de plus qu'un anonyme : il n'existe aucun lien entre une commande et un numéro.

## Ce qu'on veut

- Un produit WooCommerce « numéro à l'unité » rattaché à **un** numéro (champ sur le produit, provisoire comme le reste du modèle de démonstration).
- Une commande **payée** contenant ce produit donne au compte le droit sur ce numéro, et lui seul : ses articles et son PDF. Les états non payés (en attente, échouée, annulée) ne donnent rien ; un remboursement retire le droit.
- Le droit est lu par l'adaptateur de C-08 et passé à la décision d'accès, dont le moteur ne change pas.
- Commande passée sans compte : dis ce que le cahier des charges prévoit ; si rien, fermé, et signale-le.

## Livrables

Code, tests (payée, non payée, remboursée, autre numéro, PDF), profil V-NUM mis à jour dans le script de C-09, `production/C-14/A-VOIR.md`, `PRET`. Preuves proportionnées.
