# Lot B-09 — Les autres pages : FAQ, pages légales, contact

**Voie** : 2. **Chantier** : B. **Délai** : une demi-journée. **Dépend de** : B-00, B-01, B-08 (même façon de faire), C-21. **Cahier des charges** : §3.14 (« Autres pages et fonctions »), §4.4 (RGPD). Relis-les.

## Pourquoi

Le §3.14 liste des pages que tout visiteur cherche et que la démonstration n'a pas : la FAQ du service client, les pages légales, le formulaire de contact. Leur texte viendra d'Imagine et de son conseil ; leur place et leur structure peuvent être parcourues par Ced dès maintenant.

## Ce qu'on veut

**Le standard d'abord.** Des pages WordPress, la page de politique de confidentialité native, un menu de pied de page natif : dis en cinq lignes pourquoi il ne faut rien de plus, ou ce qu'il faut de plus.

- **FAQ du service client** : une page, quatre rubriques aux intitulés du §3.14 (accès numérique, abonnement, facturation, livraison), vides. Une question et sa réponse sont un contenu que la rédaction ajoute sans toucher au code : dis comment.
- **Pages légales** : conditions générales de vente, politique de confidentialité (la page native de WordPress, déclarée comme telle), gestion des cookies. Vides. **Pas de bandeau de cookies** dans ce lot : le choix de l'outil n'est pas fait.
- **Formulaire de contact** : nom, adresse électronique, message, une case de consentement à être recontacté, non cochée. Même mécanique que « Proposer un sujet » de B-08, corrections comprises : stockage privé, visible de la seule administration, déclaré à l'export et à l'effacement de C-21.
- Ces pages se rangent dans un **menu de pied de page**, créé de façon reprenable après une interruption (la leçon de B-08). Le menu principal du §3.1 ne change pas.

Règles :

- **Rien ne part** : aucun email, aucun appel sortant. Le message est enregistré, c'est tout.
- Le formulaire ne révèle pas si une adresse a un compte.
- Un message de contact est un message de formulaire : écris dans ta note où il est rangé (type, clés), pour que l'import de la voie 1 puisse le vider le jour venu.
- Aucun texte inventé au nom d'Imagine, aucun texte juridique, aucun style inventé : le squelette de B-01.
- Les bouchons de test reproduisent le déséchappement de WordPress (règle de la file) : un message avec un antislash est accepté et relu à l'identique.
- Pages publiques : hors de la matrice de C-23. Un seul contrôle d'étanchéité, avec sa mutation : un message de contact ne sort ni par l'interface REST, ni par la recherche.

## Preuve

Proportionnée. Les pages existent aux bons intitulés et sont reliées depuis le pied de page ; la page de confidentialité est celle que WordPress connaît ; un message s'enregistre sans email ni appel sortant, se retrouve dans l'export de son auteur et disparaît à l'effacement ; création rejouée après une interruption au milieu ; messages d'essai retirés à la fin.

## Livrables

Le code, ses tests, la section du README de l'extension, `production/B-09/A-VOIR.md`, `PRET`. Rapport court.
