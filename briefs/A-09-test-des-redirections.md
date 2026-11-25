# Lot A-09 — Le test des redirections

**Voie** : 1. **Chantier** : A. **Délai** : trois heures. **Cahier des charges** : §4.3, dernier point (« plan de redirections validé avant la bascule, test automatisé après »).

## Pourquoi

Le site change de structure : des adresses vont disparaître ou bouger. Le cahier des charges demande un plan de redirections et un test automatisé après la bascule. Le plan, lui, viendra du référenceur et de l'inventaire du site réel : ce n'est pas ce lot. Ce lot fournit l'outil qui vérifie un plan, pour qu'il soit prêt le jour où le plan arrive.

**Ce lot ne décide d'aucune redirection.**

## Ce qu'on veut

`wp/outils/bascule/tester-redirections`, lecture seule, qui prend un **plan** (fichier du dépôt : ancienne adresse relative, adresse attendue, code attendu) et l'adresse de base d'un site, et dit pour chaque ligne :

- conforme : le bon code, la bonne cible, en **un seul saut** ;
- chaîne (plusieurs sauts), boucle, mauvaise cible, mauvais code, cible qui répond autre chose que 200, délai dépassé.

Règles :

- il ne suit jamais une redirection hors du site testé : une cible externe est signalée, pas visitée ;
- il n'interroge que l'adresse de base donnée, refuse toute adresse qui n'est pas un site de test ou de staging déclaré (même contrôle de statut que les autres outils de bascule ; la production se teste plus tard, sur GO écrit de Ced) ;
- cadence limitée, pour ne pas charger un site ;
- le plan est validé avant tout appel : doublons, lignes contradictoires, ancienne adresse égale à la cible, adresse absolue là où on attend du relatif ;
- sortie : un rapport lisible et un fichier tableur des lignes non conformes ; code de retour non nul s'il y en a.

Livre aussi `plan-redirections.exemple.csv` : trois lignes fictives qui montrent le format. Pas d'adresse d'Imagine.

## Preuve

Sur un site jetable fictif (pas `imagine-test-demo`) où tu poses quelques redirections : une conforme, une chaîne, une boucle, une cible en 404, une cible externe, une ligne de plan invalide. Chaque cas est reconnu. Preuves proportionnées.

## Livrables

L'outil, ses tests, le mode d'emploi (une page), le plan d'exemple, `production/A-09/PRET`. Rapport court.
