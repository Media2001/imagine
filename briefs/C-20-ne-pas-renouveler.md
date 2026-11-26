# Lot C-20 — « Ne pas renouveler », dans Mon compte

**Voie** : 2. **Chantier** : C. **Délai** : une demi-journée. **Dépend de** : B-02, C-05, C-06, C-13. **Cahier des charges** : §3.7 (« Gestion du renouvellement : désactivation en un clic, confirmée par email, avec la date de fin et les numéros encore dus »), §3.8.

## Pourquoi

Un abonné doit pouvoir arrêter la reconduction sans écrire à personne. C'est une obligation légale autant qu'une promesse du cahier des charges, et un lien de gestion masqué expose Imagine à des remboursements forcés (§3.8). Subscriptions sait déjà annuler et couper le renouvellement automatique : ce lot vérifie ce que le standard fait, et ajoute seulement ce qui manque pour que l'abonné sache ce qui l'attend.

## Ce qu'on veut

D'abord le standard : dix lignes dans `production/C-20/natif.md` sur ce que Subscriptions propose (annulation en fin de période, bascule du renouvellement automatique), d'après sa documentation officielle, et sur ce que cela change à l'état de l'abonnement.

Puis, dans « Mon compte » (B-02), sur l'abonnement :

- une action « Ne pas renouveler », suivie d'une confirmation qui affiche **la date de fin** et **les numéros encore dus** (les mêmes que ceux que B-02 affiche déjà, par les mêmes règles) ;
- après confirmation : l'abonnement dit clairement qu'il s'arrêtera à cette date, et une action « Reprendre le renouvellement » reste disponible jusque-là ;
- l'abonné garde son accès et sa place dans la liste d'envoi jusqu'à la date de fin. Vérifie-le avec la décision d'accès (C-06) et la liste d'envoi (C-13) **telles qu'elles sont** ; ne les modifie pas. Si l'état natif choisi les referme trop tôt, arrête-toi et dis-le.

Règles :

- **Paiement en quatre fois** : l'engagement est un bloc de quatre numéros (décision du 22/11). Le non-renouvellement prend effet à la fin du bloc en cours et les échéances de ce bloc restent dues. Si le standard ne sait pas le faire sans annuler les échéances restantes, ne contourne pas : arrête-toi sur ce cas et dis-le.
- **Virement et mandat papier** : le renouvellement est manuel, il n'y a rien à désactiver. L'écran le dit, sans bouton.
- **Aucun email.** L'email de confirmation (n° 5 du §3.8) appartient au lot des emails, qui attend Imagine. Laisse un point d'accroche nommé, rien de plus.
- **La rétractation n'est pas dans ce lot** : ses modalités attendent le conseil juridique d'Imagine (§3.8).
- Aucun remboursement, aucun appel à un service de paiement. Règles en code pur, testables sans WordPress.

## Preuve

Proportionnée. Sur le site, avec les profils de C-09 : un abonné par carte désactive puis reprend, la date de fin et les numéros dus sont ceux de B-02, l'accès et la liste d'envoi ne bougent pas ; le profil en quatre fois garde ses échéances ; A-VIR et A-PAPIER n'ont pas de bouton ; un abonné ne peut pas agir sur l'abonnement d'un autre. Les profils sont remis dans leur état de départ, action planifiée comprise, et tu le relis.

## Livrables

Le code, ses tests, `production/C-20/A-VOIR.md`, `PRET`. Rapport court dans `files/rapports/`.
