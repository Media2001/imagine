# Lot B-07 — L'agenda

**Voie** : 2. **Chantier** : B. **Délai** : une demi-journée. **Dépend de** : B-00, B-01, B-05. **Cahier des charges** : §3.11 (« Agenda »), §4.2 (« Événement : type, date, lieu, description, inscription, billets, quota, tarif abonné »). Relis-les.

## Pourquoi

« Nos événements » est une entrée du menu principal, et B-01 n'en a posé que la liste et la fiche vides. L'agenda a trois sortes d'événements qui ne se comportent pas de la même façon : la sortie d'un numéro et la rencontre gratuite, où l'on s'inscrit simplement ; l'événement d'un partenaire, qui renvoie ailleurs. La billetterie payante dépend d'une extension dont la licence n'est pas confirmée ; l'agenda, lui, peut exister et être montré à Ced.

## Ce qu'on veut

**Le standard d'abord.** Dis en dix lignes ce que l'extension imposée par le cahier des charges offre **dans sa version gratuite** (agenda, fiche, inscription simple, balisage), d'après sa documentation officielle, et si le modèle d'événement de B-00 doit s'y ranger. Si la version gratuite, installée sur la seule démonstration, fait le travail, utilise-la et n'écris que le raccord ; sinon dis pourquoi et fais au plus simple. **N'installe ni n'active Event Tickets Plus.**

- **L'événement** : type (sortie de numéro, rencontre, événement partenaire), date et heure, lieu, description.
- **L'agenda** : les événements à venir, du plus proche au plus lointain ; les événements passés à part, sans inscription possible. Les deux événements fictifs de B-00, plus ce qu'il faut pour montrer les trois types et un événement passé.
- **La fiche** : pour une sortie de numéro ou une rencontre gratuite, une inscription simple (nom, adresse email, une case de consentement à être recontacté, non cochée) ; pour un événement partenaire, un lien externe et **aucune inscription sur le site**. Le lien externe d'un événement partenaire suit la règle de B-05 sur les liens sortants.
- **Le balisage** : les données structurées d'un événement, à partir des seuls champs affichés. Le plan de balisage complet relève du référenceur ; ici, le minimum que le standard fournit.

Règles :

- **Rien ne part** : aucun email de confirmation, aucun appel extérieur ; l'inscription est enregistrée et visible de l'administration, c'est tout.
- **Pas de billet, pas de paiement, pas de quota, pas de tarif abonné, pas d'export des inscrits** : c'est la billetterie, elle viendra avec sa licence.
- Les inscriptions sont des données personnelles : dis où elles sont rangées, et déclare-les à l'export et à l'effacement de C-21 quand l'adresse est celle d'un compte.
- Une inscription en double (même adresse, même événement) n'en crée pas deux.
- Le formulaire d'inscription ne révèle pas si une adresse est déjà inscrite ou a un compte.
- Aucun style inventé : le squelette de B-01.

## Preuve

Proportionnée. Les trois types s'affichent comme dit ; un visiteur s'inscrit à une rencontre, une seconde fois sans doublon ; l'événement passé refuse l'inscription, formulaire absent **et** envoi direct refusé ; l'événement partenaire n'a pas de formulaire ; aucun email ni appel sortant pendant le parcours ; le balisage d'une fiche se lit et correspond aux champs affichés. Inscriptions d'essai retirées à la fin.

## Livrables

Le code, ses tests, `production/B-07/A-VOIR.md`, `PRET`. Rapport court.
