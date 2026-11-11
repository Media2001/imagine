# Lot 00 — Étude de couverture des extensions

**Nature** : étude, sans code, sans installation, sans achat.
**Livrable** : `production/lot-00/couverture-extensions.md`, puis `production/lot-00/PRET`.

## Pourquoi

Le cahier des charges impose des extensions (§4.1) et demande de vérifier, avant tout développement, que le prélèvement récurrent et PayPal sont pris en charge (§3.6). Avant d'écrire une ligne de sur-mesure, on veut savoir ce que le standard fait déjà.

## Ce qu'il faut établir

Pour chaque ligne ci-dessous : ce que l'extension fait nativement, ce qui demande un module complémentaire officiel, ce qui reste à développer. **Chaque affirmation cite la documentation officielle de l'éditeur : adresse et phrase exacte.** Sans source : « doute ». Les articles de blog et les forums ne comptent pas.

| N° | Besoin | Référence | Extension à examiner |
|---|---|---|---|
| 1 | Abonnement annuel à reconduction tacite, payé en une fois | §3.4 | Subscriptions |
| 2 | Même abonnement payé en quatre fois, les quatre échéances étant dues, à des dates **irrégulières** fixées par un calendrier de parution | §3.4, §3.5 | Subscriptions : peut-on fixer ou déplacer par code la date de chaque prochain paiement ? |
| 3 | Carte et Bancontact au premier paiement, puis prélèvement SEPA pour les suivants | §3.6 | Passerelle Stripe officielle pour WooCommerce |
| 4 | Domiciliation en ligne (SEPA) avec mandat accepté par case à cocher | §3.6 | Idem |
| 5 | PayPal : premier paiement et renouvellements automatiques ; conditions côté compte PayPal | §3.6 | WooCommerce PayPal Payments |
| 6 | Renouvellement manuel (virement, mandat papier) validé par un administrateur | §3.6, §3.13 | Subscriptions |
| 7 | Désactivation des emails de Stripe et réduction de ceux de PayPal | §3.8 | Stripe, PayPal |
| 8 | Abonnement offert : coordonnées du destinataire, compte du destinataire, renouvellement au choix de l'acheteur | §3.4 | Subscriptions (fonction cadeau) |
| 9 | Abonnements groupés : un gestionnaire, des bénéficiaires remplaçables, chacun son compte | §3.4 | Teams for WooCommerce Memberships |
| 10 | Codes de réduction limités à la première année, ou à une campagne | §3.4 | Subscriptions |
| 11 | Droits d'accès par abonnement actif, et par numéro acheté, sans limite de durée | §3.9 | Memberships |
| 12 | Accès découverte unique, en durée ou en nombre d'articles | §3.9 | Memberships |
| 13 | Étanchéité : que renvoient REST, les flux, oEmbed, la recherche interne et les aperçus de partage pour un contenu restreint ? | §3.9, §4.4 | Memberships |
| 14 | Fichiers PDF protégés, droit contrôlé à chaque téléchargement | §3.9 | WooCommerce (téléchargements), Memberships |
| 15 | Délai de grâce après un paiement échoué, nouvelles tentatives | §3.8 | Subscriptions |
| 16 | Supplément de port par pays, recalculé au renouvellement après un changement d'adresse | §3.4, §3.7 | Subscriptions, WooCommerce |
| 17 | Billets payants avec QR code, tarif réduit pour abonné connecté, quotas | §3.11 | Event Tickets Plus |
| 18 | Reprise d'abonnements d'un site WooCommerce Subscriptions vers un autre en conservant les moyens de paiement Stripe | §4.3 | Subscriptions (import/export) |
| 19 | Balisage de contenu payant (`isAccessibleForFree`, `hasPart`) | §3.9 | Rank Math Pro |

## Format du livrable

Un tableau de synthèse (besoin · natif / module / sur mesure · source), puis une section par besoin avec les citations. Terminer par :

- la liste des modules complémentaires nécessaires, avec leur éditeur ;
- la liste de ce qui reste à développer ;
- « À arbitrer par Ced » : questions fermées.

## Limites

Aucune installation, aucun compte créé, aucun achat. Si une documentation est inaccessible, le dire.
