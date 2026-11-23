# Lot C-10 — L'écran de réglages

**Voie** : 2. **Chantier** : C. **Nature** : administration WordPress. **Délai** : une demi-journée.
**Dépend de** : B-00 ; C-05, C-06, C-07 (clos, écrans exclus de la clôture).

## Pourquoi

La doctrine dit qu'une règle métier ouverte devient un réglage. Tu as déjà écrit trois adaptateurs d'administration (accès, échéancier, format d'export), restés hors des lots clos. Ce lot les réunit en **un écran**, que Ced puis Imagine pourront ouvrir : c'est là qu'Imagine tranchera ses questions ouvertes, sans nous.

## Ce qu'on veut

Dans l'administration du site de démonstration, un menu « Imagine » avec une page « Réglages » :

- une section par domaine : **Accès** (les trois réglages de C-06), **Paiement en quatre fois** (C-05), **Liste d'envoi** (C-07) ;
- chaque réglage a un libellé en français courant, une phrase d'explication (ce que ça change pour un abonné), sa valeur par défaut, et la mention « à confirmer par Imagine » quand la règle est encore ouverte (`docs/decisions.md`) ;
- réservé aux administrateurs ; nonce, validation et assainissement de chaque valeur ; une valeur invalide est refusée avec un message clair, l'ancienne est conservée ;
- chaque modification est journalisée (qui, quand, ancienne et nouvelle valeur) ;
- les bibliothèques closes ne changent pas : tu ne touches qu'aux adaptateurs d'administration et à ce qui les relie.

Sobre : les composants natifs de l'administration WordPress, rien de plus.

## Livrables

- Le code et ses tests (droits, nonce, valeurs invalides, journal).
- `production/C-10/A-VOIR.md` : l'adresse de la page, et pour **un** réglage, la manipulation qui montre son effet sur le site (par exemple : changer le réglage d'accès, recharger un article).
- `production/C-10/PRET`.
