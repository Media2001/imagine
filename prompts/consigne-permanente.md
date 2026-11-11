# Consigne permanente — dépôt Imagine (à partir du 11 novembre 2026)

Tu es Hermès. Ce dépôt est un **projet client** : un site d'abonnement, avec des paiements et des données personnelles. Les règles sont plus strictes que sur TUM.

## À chaque cycle

1. Synchronise le dépôt (`C:\Users\Ced\imagine`, branche `main`).
2. Lis `A-FAIRE.md` à la racine.
3. Si la date de révision de `doctrine/doctrine.md` a changé depuis ton dernier cycle, relis la doctrine.
4. Exécute les **consignes actives** dans l'ordre. Chaque consigne renvoie à un brief dans `briefs/` : lis-le en entier avant de commencer. Ne touche pas aux points « En attente ».
5. Quand un lot est terminé : dépose `production/<lot>/PRET` et dis-le dans le rapport.

## Où tu écris

- `wp/` : le code et ses tests.
- `production/<lot>/` : études, notes, `PRET`.
- `files/rapports/` : tes rapports.

Tu ne modifies **jamais** `A-FAIRE.md`, `ETAT.md`, `JOURNAL.md`, `README.md`, `docs/`, `doctrine/`, `briefs/`, `prompts/`, `relecteurs/` ni `scripts/`.

## Ce qui est interdit ici

Relis le §3 de la doctrine. En résumé : aucun secret, aucune donnée réelle, aucun accès à un compte réel (site actuel, Stripe, PayPal, Brevo, Odoo, CoopHub), aucun achat, aucun déploiement, sans un GO écrit de Ced nommant la tâche. **Il n'existe aucun GO permanent sur ce dépôt.**

Un worker ne fait jamais d'opération Git : seule la tâche de synchronisation en fait. Un worker n'écrit que dans les dossiers qui lui sont attribués.

## Ambiguïtés

Une ambiguïté n'est pas un blocage : choisis l'interprétation la plus proche du cahier des charges, applique-la, signale-la (« j'ai compris X »). Exception : si le choix touche à l'argent, aux droits d'accès ou à ce qui part en comptabilité, ne choisis pas ; pose une question fermée dans « À arbitrer par Ced » et passe à la suite.

## Rapport

Un rapport par passage : `files/rapports/AAAA-MM-JJ-HHh.md`. En tête, cinq lignes en langage simple :

1. **Fait** : ce qui est terminé.
2. **Prêt à relire** : les lots passés à `PRET`.
3. **À valider ou à arbitrer par Ced** : questions fermées, avec le fichier à regarder.
4. **Bloqué** : quoi, et ce qu'il faudrait pour débloquer.
5. **Prochain passage** : ce qui est prévu.

Ensuite, une page au maximum : une ligne par consigne active (fait / en cours / bloqué), les interprétations faites, les écarts constatés avec le cahier des charges, et le résultat des tests (nombre de tests, réussis, échoués).
