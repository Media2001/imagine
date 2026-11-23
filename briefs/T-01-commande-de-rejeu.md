# Lot T-01 — Une commande de rejeu des tests pour les relecteurs

**Nature** : outillage. **Délai** : une heure.

## Pourquoi

Depuis le début, les relecteurs écrivent la même réserve : ils ne peuvent pas exécuter PHP, donc ils contrôlent que le code correspond à tes preuves, sans rejouer eux-mêmes. La vérification n'est pas réellement indépendante. Il leur faut une commande unique, sûre, qu'on puisse leur autoriser.

## Ce qu'on veut

Un script `wp/tests/rejouer.ps1`, lancé depuis la racine du dépôt, sans argument :

- il exécute **toute** la suite PHP (toutes les extensions sur mesure) dans un conteneur jetable, **sans réseau**, dépôt monté **en lecture seule**, dépendances prises dans une image ou un cache préparé à l'avance ;
- il n'écrit rien dans le dépôt et ne laisse aucun conteneur derrière lui ;
- il affiche en dernière ligne un résumé stable : `REJEU : <n> tests, <n> assertions, <n> échecs, <n> erreurs, <n> ignorés — <PASS|FAIL>`, et sort avec le code 0 ou 1 ;
- il échoue clairement, sans rien installer, si Docker ou l'image manquent, en disant quoi préparer.

Il ne lance ni les bancs avec extensions commerciales, ni rien qui crée un site dans l'outil de staging : seulement les tests de bibliothèque.

Si l'image doit être construite une fois avec le réseau, fournis à part `wp/tests/preparer-image.ps1`, que Ced lancera lui-même.

## Livrables

Les deux scripts, une preuve d'exécution (sortie complète), la marche à suivre en cinq lignes dans `production/T-01/notes.md`, puis `production/T-01/PRET`. Claude ajoutera ensuite l'autorisation correspondante au script de relecture.
