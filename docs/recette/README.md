# Recette — profils et cas d'acceptance

**État : proposition du 19/11/2026, à relire par Ced, puis à faire valider par le pilote du projet.**

Ce dossier détaille les parcours de réception du chapitre 5 du cahier des charges. Il sert trois fois :

1. **Spécification** : un lot n'est terminé que si les cas qui le concernent passent.
2. **Tests automatiques** : chaque cas devient un test de bout en bout (Playwright), rejoué à chaque livraison.
3. **Cahier de recette** : c'est sur ces cas qu'Imagine prononcera la réception.

Ce qui n'est pas couvert par un cas accepté est une demande nouvelle (`docs/ecarts.md`).

## Fichiers

- `profils.md` : les comptes fictifs sur lesquels les cas s'appuient.
- `cas.md` : le catalogue des cas.

## Format d'un cas

- **Identifiant** stable (`R-07`), jamais réutilisé.
- **Référence** au paragraphe du cahier des charges.
- **Profil** de départ (`profils.md`).
- **Étant donné / Quand / Alors**, en français, vérifiable sans interprétation.
- **État** : `Prêt` (peut être automatisé), ou `Attend` suivi de ce qui manque (décision d'Imagine, réponse de Step, licence).

## Règles

- Les profils sont créés par un script rejouable, **sur le staging uniquement**. Aucun compte de test n'existe en production.
- Les paiements se font en mode test (Stripe, bac à sable PayPal).
- « Arrive dans Odoo » signifie : l'événement est dans la file du connecteur avec le bon contenu, puis dans l'environnement d'essai d'Odoo quand Step en fournit un, ou dans l'export quotidien tant que l'interface n'existe pas (§2.4).
- Un cas se termine toujours par ce que l'abonné voit **et** par ce que l'administration voit.
- Un agent ne modifie pas un cas pour faire passer un test. Si un cas lui semble faux, il le signale.
