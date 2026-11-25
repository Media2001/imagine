# Lot C-15 — L'écran des échéances

**Voie** : 2. **Chantier** : C. **Délai** : une demi-journée. **Dépend de** : C-10, C-13, complément de C-09. **Cahier des charges** : §3.13, « Écran des échéances ». Relis-le.

## Pourquoi

C'est l'écran de travail du référent administratif d'Imagine : chaque semaine, il y voit qui arrive à échéance, quels virements il attend, quels prélèvements sur mandat papier il doit lancer, et ce qui a échoué. Aujourd'hui tout cela se fait dans Access et dans la tête de quelqu'un. Avec les paiements fictifs du complément de C-09, le site de démonstration a enfin de quoi le montrer.

## Ce qu'on veut

Dans l'administration de `imagine-test-demo`, sous le menu Imagine existant (un seul menu, pas de doublon), un écran à cinq vues :

1. **Arrivent à échéance** : abonnements dont la fin ou le renouvellement tombe dans la période choisie (30, 90, 180 jours).
2. **Paiements en attente.**
3. **Virements à valider** : avec, par ligne, l'action « paiement reçu ».
4. **Prélèvements sur mandat papier à lancer** : liste **exportable** en fichier tableur (abonné, montant, référence du mandat, échéance), comme le demande le cahier.
5. **Paiements échoués.**

Règles :

- **L'écran lit l'état natif** (Subscriptions et commandes). Il ne tient aucun registre parallèle des paiements.
- **Une seule action d'écriture** : « paiement reçu » sur un virement, qui fait passer la commande native à l'état payé, par les fonctions de WooCommerce, avec le nom de l'opérateur et la date dans la note de commande. Confirmation avant d'agir, jeton de sécurité, droit dédié (celui de la liste d'envoi ou un voisin). Pas d'annulation en masse, pas de remboursement, rien d'autre.
- **Aucune règle nouvelle.** Ce qui ferme ou rouvre un accès reste la décision d'accès (C-06) et ses réglages. Si l'écran a besoin d'une règle que personne n'a écrite (délai avant de considérer un virement en retard, par exemple), c'est un réglage au défaut prudent, dans l'écran de réglages de C-10, et tu le signales.
- **Aucun IBAN**, nulle part. La référence du mandat est un identifiant fictif des profils.
- L'export suit les mêmes précautions que celui de la liste d'envoi (droit, jeton, pas de fichier laissé dans un dossier public, protection contre les formules de tableur).
- Aucun email, aucun appel sortant.

## Preuve

Proportionnée. Les règles de tri et de filtrage en code pur, testées. Sur le site : chaque vue montre les profils qui doivent y être (A-VIR dans les virements, A-GRACE et A-SUSP dans les échecs, A-PAPIER dans les mandats, A-ECHEANCE dans les échéances) et pas les autres ; « paiement reçu » sur A-VIR, puis retour à l'état de départ par le reset de C-09 ; un compte sans le droit reçoit un refus ; l'export ouvert.

Si un profil manque pour montrer une vue, dis-le : ne fabrique pas d'état en dehors du catalogue de C-09.

## Livrables

Le code, ses tests, `production/C-15/A-VOIR.md` (en quel compte, quelle adresse, quoi voir dans chaque vue), `PRET`. Rapport court.
