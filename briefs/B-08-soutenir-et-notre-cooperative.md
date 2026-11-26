# Lot B-08 — « Soutenir » et « Notre coopérative »

**Voie** : 2. **Chantier** : B. **Délai** : une demi-journée. **Dépend de** : B-00, B-01, B-05, B-06. **Cahier des charges** : §3.1 (menu principal), §3.12 (« Soutenir, coopérative et partenaires »). Relis-les.

## Pourquoi

« Notre coopérative » et « Soutenir » sont deux entrées du menu principal, et rien n'existe derrière. Leur contenu viendra d'Imagine ; leur structure, elle, est écrite dans le cahier des charges, et Ced doit pouvoir la parcourir sur la démonstration avant que les maquettes n'arrivent.

## Ce qu'on veut

**Le standard d'abord.** Des pages WordPress et le menu natif : dis en cinq lignes pourquoi il ne faut rien de plus, ou ce qu'il faut de plus.

- **« Notre coopérative »** : la page et ses sous-pages, aux intitulés exacts du §3.12 (projet éditorial et manifeste, charte d'indépendance, charte IA, baromètre égalité-diversité, équipe, gouvernance, Imagine COOP), vides, reliées entre elles, création idempotente comme B-06. Un lien vers l'espace coopérateurs de B-06, qui garde sa propre règle d'accès.
- **« Soutenir »** : quatre entrées, dans l'ordre du cahier des charges. L'abonnement renvoie vers « S'abonner ». Le don est **éteint** : un réglage fermé par défaut, rien n'est affiché tant qu'il l'est (le don est « configuré, activé en 2027 »). Le bénévolat est un texte vide. La prise de parts est un **lien** vers CoopHub, dont l'adresse est un réglage, vide par défaut ; vide, l'entrée s'affiche sans lien. Ce lien suit la règle de B-05 sur les liens sortants.
- **« Proposer un sujet »** : un formulaire sans mise en avant (pas dans le menu, un lien discret depuis « Notre coopérative ») : nom, adresse email, le sujet, une case de consentement à être recontacté, non cochée.

Règles :

- **Rien de CoopHub** : ni fenêtre intégrée, ni compteur, ni appel. Le niveau d'intégration n'est pas arrêté ; par défaut, le lien.
- **Pas de paiement, pas de don**, même en essai.
- **Rien ne part** : la proposition de sujet est enregistrée et visible de l'administration, c'est tout. Elle est une donnée personnelle : dis où elle est rangée, et déclare-la à l'export et à l'effacement de C-21 quand l'adresse est celle d'un compte.
- Le formulaire ne révèle pas si une adresse a un compte.
- Aucun texte inventé au nom d'Imagine, aucun style inventé : le squelette de B-01.
- Ajoute ces pages à la matrice de C-23 **seulement** si l'une d'elles est réservée ; elles sont publiques, donc en principe non.

## Preuve

Proportionnée. Les deux entrées du menu mènent aux bonnes pages ; les intitulés sont ceux du cahier des charges ; le don n'apparaît pas tant que son réglage est fermé, et apparaît (sans paiement) quand on l'ouvre ; la prise de parts est un lien quand l'adresse est renseignée, un texte sinon ; une proposition de sujet s'enregistre, sans email ni appel sortant ; propositions d'essai retirées à la fin, réglages remis.

## Livrables

Le code, ses tests, `production/B-08/A-VOIR.md`, `PRET`. Rapport court.
