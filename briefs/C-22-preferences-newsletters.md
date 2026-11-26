# Lot C-22 — Le centre de préférences des newsletters

**Voie** : 2. **Chantier** : C. **Délai** : une demi-journée. **Dépend de** : B-02. **Cahier des charges** : §3.10 (« Centre de préférences », « Page Nos newsletters »), §4.2 (compte : préférences newsletter). Relis-les.

## Pourquoi

Brevo envoie, mais le site reste la référence : c'est lui qui sait à quelles newsletters un lecteur veut être inscrit, et il le dira à Brevo par le connecteur. Le connecteur attend ; le choix du lecteur, lui, peut déjà exister, être montré à Ced et servir de source au futur envoi. Le cahier des charges demande aussi qu'une nouvelle newsletter (celle des coopérateurs en 2027) s'ajoute « sans développement ».

## Ce qu'on veut

- **La liste des newsletters est une donnée, pas du code** : un réglage dans l'écran de C-10 (identifiant, intitulé, une phrase de présentation, « principale » oui ou non). Sur la démonstration : trois newsletters fictives, dont une principale. En ajouter une dans le réglage la fait apparaître partout, sans toucher au code : c'est la preuve du « sans développement ».
- **Dans « Mon compte »**, une rubrique « Mes newsletters » : une case par newsletter, enregistrée sur le compte. L'état de chaque case est daté.
- **Une page « Nos newsletters »** : la présentation de chacune ; pour un lecteur connecté, un lien vers ses préférences. Pour un visiteur anonyme, un emplacement nommé à la place du formulaire d'inscription : l'inscription d'un anonyme et sa double confirmation sont gérées par Brevo (§3.10), elles viendront avec le connecteur.

Règles :

- **Rien ne part.** Aucun appel à Brevo, aucun email, aucune confirmation. Laisse un point d'accroche nommé pour le connecteur, rien de plus.
- « Inscription par défaut à la newsletter principale » (§3.10) : à quel moment, et avec quel consentement, n'est pas décrit. **Défaut prudent : aucune case cochée tant que le lecteur ne l'a pas fait lui-même** ; un réglage « inscrire par défaut à la principale à la création du compte », fermé. Écris la question fermée pour Imagine dans ton rapport.
- Un compte « sans email » n'a pas cette rubrique : l'écran le dit en une phrase.
- Ces préférences entrent dans l'export et l'effacement des données du compte (C-21) : déclare-les si C-21 est rendu, sinon signale-le.
- Pas d'étiquettes de persona : elles dépendent du formulaire de personnalisation, qui n'est pas arrêté.

## Preuve

Proportionnée. Un profil coche, décoche, recharge : l'état est le bon et il est daté ; un abonné ne modifie pas les préférences d'un autre ; une quatrième newsletter ajoutée dans le réglage apparaît dans le compte et sur la page, puis est retirée ; aucun appel sortant ni email pendant le parcours ; A-SANSMAIL n'a pas la rubrique. Profils remis dans leur état de départ.

## Livrables

Le code, ses tests, `production/C-22/A-VOIR.md`, `PRET`. Rapport court.
