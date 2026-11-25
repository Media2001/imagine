# Lot B-02 — L'espace « Mon compte », en squelette

**Voie** : 2. **Délai** : une demi-journée. **Dépend de** : B-01, C-09. **Cahier des charges** : §3.10.

Même principe que B-01 : toute la structure, aucun habillage. Relis §3.10 et fais la liste de ce que l'abonné doit y trouver ; à défaut de précision, au minimum :

- **Mon abonnement** : formule, état en clair (actif, en délai de grâce, suspendu, expiré, virement en attente), premier et dernier numéro couverts, nombre de numéros restants, prochaine échéance et son montant, moyen de paiement.
- **Mes échéances** (paiement en quatre fois) : les quatre lignes, payée ou à venir, et le bandeau de régularisation avec son action si une échéance a échoué.
- **Mes numéros** : les numéros auxquels j'ai droit, avec le lien vers le PDF protégé (C-11).
- **Mes coordonnées** : adresse de livraison du magazine, modifiable ; ce qui part à l'envoi postal est ce qui est affiché ici.
- **Mes factures et justificatifs** : la liste, même vide.

Les données viennent des vrais objets du site de démonstration (profils de C-09) et des bibliothèques closes (numéros, échéancier). Ce qui n'est pas branchable aujourd'hui apparaît comme emplacement nommé, pas comme donnée inventée.

Un abonné ne voit que ses données : teste qu'un compte ne peut pas afficher l'abonnement d'un autre en changeant un identifiant dans l'adresse.

## Livrables

Gabarits, tests, `production/B-02/A-VOIR.md` (quoi voir en `a-carte`, `a-4x-j45`, `a-susp`), la liste de ce dont le designer aura besoin, `PRET`.
