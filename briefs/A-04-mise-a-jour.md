# Lot A-04 — Le script de mise à jour

**Voie** : 1. **Chantier** : A. **Délai** : une journée. **Dépend de** : A-03.

## Pourquoi

Le cœur du chantier A : amener le site d'Imagine de sa pile actuelle (WordPress 6.9.1, extensions à auditer) à la pile cible (WordPress 7.0.x, WooCommerce, Subscriptions et Memberships dans les versions déposées par Ced), sans perdre un abonnement ni une adhésion. Cette opération sera rejouée à l'identique le jour de la mise en ligne : c'est donc un script de bascule, jamais une suite de clics.

## Ce qu'on veut

`wp/outils/bascule/mettre-a-jour`, qui sur un site donné :

1. vérifie les préalables (sauvegarde présente et récente, mode maintenance, statut du site, versions de départ attendues) et refuse sinon ;
2. met à jour dans un ordre justifié (cœur, WooCommerce, Subscriptions, Memberships, puis le reste), à partir des archives du dossier des extensions premium et des sources publiques, **sans connecter le site à un compte** ;
3. après chaque étape : lance les migrations de base de l'extension jusqu'au bout (y compris celles qui tournent en tâche de fond), vérifie l'absence d'erreur fatale, et s'arrête à la première anomalie en disant où il en est ;
4. est **reprenable** : relancé après un arrêt, il reprend à l'étape en cours sans refaire les précédentes ;
5. écrit un journal lisible : étape, version avant, version après, durée, migrations exécutées.

Il ne supprime rien, ne nettoie rien (c'est A-05) et ne touche pas au thème.

## Preuve

Sur site fictif construit dans la pile de départ la plus proche possible de celle d'Imagine (WordPress 6.9.1, WooCommerce 11.0.1, Memberships 1.30.3 ; pour Subscriptions, seule la version récente est disponible : dis clairement ce que ça empêche de prouver) :

- non-régression (A-03) avant, mise à jour, non-régression après : la comparaison ne montre que des changements attendus ;
- un arrêt provoqué en cours de route, puis une reprise qui aboutit ;
- classique et HPOS.

La vraie preuve se fera sur le staging d'Imagine, avec ses vraies versions : ce lot prépare l'outil, il ne prétend pas plus.

## Livrables

Le script, ses tests, le mode d'emploi, la liste des risques que tu vois pour le site réel (une page), `production/A-04/PRET`. Rapport court.
