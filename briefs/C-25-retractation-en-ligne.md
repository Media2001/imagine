# Lot C-25 — La rétractation en ligne, en deux étapes

**Voie** : 2. **Chantier** : C. **Délai** : une demi-journée. **Dépend de** : B-02, C-09, C-10, C-21. **Cahier des charges** : §3.7 (« Fonction de rétractation en ligne, en deux étapes, disponible pendant le délai légal »), §3.8 (cadre légal belge). Relis-les.

## Pourquoi

Depuis août 2026, un site qui vend à distance doit offrir une fonction de rétractation en ligne. « Mon compte » ne l'a pas. Ce que la rétractation déclenche (remboursement, fin de l'accès, numéros déjà envoyés) n'est pas arrêté : c'est au conseil juridique d'Imagine de le dire. Mais la fonction elle-même, deux étapes et une trace datée, peut exister et être montrée à Ced.

**Ce lot enregistre une demande. Il ne rembourse rien, n'annule rien et ne ferme aucun accès.**

## Ce qu'on veut

**Le standard d'abord.** Dis en dix lignes ce que WooCommerce et Subscriptions offrent pour une demande du client sur sa commande (annulation, remboursement demandé, notes de commande), d'après leur documentation officielle, et pourquoi cela couvre ou non une rétractation en deux étapes. Si le standard suffit pour ranger la demande (une note de commande datée, par exemple), utilise-le.

- **Dans « Mon compte »**, sur une commande ou un abonnement encore dans le délai : une entrée « Me rétracter ». Première étape : ce sur quoi porte la rétractation, la date, un champ libre facultatif. Seconde étape : une confirmation explicite. Puis un accusé affiché à l'écran, daté, que le lecteur retrouve ensuite dans son compte.
- **Hors délai**, l'entrée n'est pas proposée, et un envoi direct est refusé.
- **Dans l'administration** : la liste des demandes, datée, avec la commande ; chaque demande s'ajoute au journal de C-10. Aucune action automatique.
- **Deux réglages**, dans l'écran de C-10, parce que la règle n'est pas arrêtée : la durée du délai en jours (défaut : 14) et son point de départ (défaut : la date de la commande payée ; autre valeur : une date posée à la main sur la commande). Chaque valeur est testée.

Règles :

- **Rien ne part** : aucun email, aucun appel à une passerelle. L'accusé par email viendra avec le lot des emails.
- Une demande ne se fait qu'une fois par commande ; une seconde tentative montre la première.
- La demande est une donnée personnelle du compte : déclare-la à l'export et à l'effacement de C-21.
- Les profils de C-09 que tu fais changer d'état reviennent à leur état de départ.
- Aucun style inventé : le squelette de B-01.

Dans `A-VOIR.md`, range pour Imagine, en questions fermées, ce que tu n'as pas décidé : l'effet sur l'accès, le remboursement, le point de départ du délai pour un abonnement dont le premier numéro n'est pas encore parti.

## Preuve

Proportionnée. Un profil dans le délai fait les deux étapes et retrouve son accusé ; l'abandon à la première étape n'enregistre rien ; une seconde demande n'en crée pas deux ; un profil hors délai n'a pas l'entrée **et** son envoi direct est refusé ; un autre compte ne peut pas se rétracter de la commande d'autrui ; après la demande, l'accès, l'abonnement et la commande sont inchangés ; aucun email ni appel sortant.

## Livrables

Le code, ses tests, `production/C-25/A-VOIR.md`, `PRET`. Rapport court.
