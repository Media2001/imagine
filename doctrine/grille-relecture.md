# Grille de relecture — code et études

Un rapport de relecture suit cet ordre. Un point = un fichier et une ligne (ou une citation exacte), un problème, une correction proposée. Le relecteur ne réécrit pas le code.

## 1. Conformité

- Le lot fait-il ce que demande le brief, ni moins ni plus ?
- Chaque règle métier renvoie-t-elle au paragraphe du cahier des charges qu'elle applique ?
- Une interprétation a-t-elle été faite sans être signalée ?

## 2. Exactitude métier

- Dérouler à la main au moins deux cas du cahier des charges (par exemple celui du §3.5) et comparer au résultat du code.
- Cas limites : dates égales à une date de clôture, changement d'année, calendrier incomplet, événement rejoué.

## 3. Tests

- Les tests passent-ils ? (Les lancer ; à défaut, le dire.)
- Couvrent-ils les cas limites, ou seulement le cas nominal ?
- Un test vérifie-t-il vraiment la règle, ou se contente-t-il de répéter le code ?

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle.
- Contrôle des droits, nonces, échappement des sorties, requêtes préparées.
- Paywall : une voie laisse-t-elle sortir le texte réservé ?

## 5. Doctrine

- Standard d'abord : ce code refait-il ce qu'une extension retenue fait déjà ?
- Conventions du §5 de la doctrine.

## 6. Études (lots sans code)

- Chaque affirmation sur une extension cite une page de documentation officielle, avec l'adresse et la phrase.
- Sans source : « doute ».

## Verdict

`Conforme`, `À corriger` ou `À refaire`, suivi des points classés : **bloquant**, **important**, **mineur**. Un verdict n'est jamais un GO.

## Format de fusion (`corrections/<lot>.md`)

1. Points retenus par les deux relecteurs.
2. Points vus par un seul, avec l'avis du fusionneur.
3. Désaccords.
4. Instructions pour Hermès, numérotées.
5. À arbitrer par Ced, en questions fermées.
