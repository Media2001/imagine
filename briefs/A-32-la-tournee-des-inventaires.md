# Lot A-32 — La tournée des inventaires : une commande, un bilan

**Voie** : 1. **Chantier** : A. **Délai** : trois heures. **Dépend de** : A-22 (le gardien des sorties), T-03 (`PRET`), et le resceau d'A-26, A-27, A-30, A-31 : à commencer après eux. **Cahier des charges** : §4.3 (migration), §4.4. Relis-les.

## Pourquoi

Le jour où la copie d'Imagine sera vérifiée, il faudra lancer une vingtaine d'outils d'inventaire, chacun avec sa commande, puis recommencer le jour de la bascule. Lancés à la main un par un, on en oubliera un, ou on ne saura plus lequel a refusé. Il faut une commande qui fait la tournée et un bilan d'une page qui dit, outil par outil, ce qui s'est passé.

**Ce lot enchaîne. Il ne compte rien lui-même, et ne change aucun outil.**

## Ce qu'on veut

**Le standard d'abord.** Trois lignes : A-08 enchaîne déjà l'audit, la non-régression, la mise à jour et le nettoyage. Dis pourquoi la tournée est une commande à part (elle ne contient que de la lecture seule, et rien de ce qu'A-08 exécute).

Une commande dans `wp/outils/bascule/tournee/`, qui :

- lance, dans un ordre fixe, les outils d'inventaire **clos**, chacun par la commande exacte de son mode d'emploi, par le gardien commun, sans rien y ajouter. La liste est fermée, écrite dans un fichier du lot ; y ajouter un outil est une ligne ;
- laisse hors tournée, en les nommant, les outils qui demandent un fichier d'Imagine (A-13, A-14, A-30) et ceux qui ne sont pas clos ;
- n'ajoute et ne retire aucun contrôle d'accès : ce sont les outils qui refusent un site non vérifié, la tournée rapporte leur refus ;
- continue quand un outil refuse ou échoue : les suivants tournent quand même ;
- écrit un bilan, hors du dépôt : par outil, « réussi », « refusé » (avec son code de refus) ou « en échec » (avec son code de sortie), et où se trouve son rapport. **Aucun nombre d'un rapport n'est recopié dans le bilan**, aucun nom tiré du site ;
- sort en erreur si un seul outil a refusé ou échoué. Un bilan partiel n'est jamais présenté comme une tournée complète.

L'import, le gardien et le lanceur de rejeu sont gelés : tu n'y touches pas. Si la tournée te semble demander un changement chez l'un d'eux, écris-le et arrête-toi là.

## Preuve

Sur le banc fictif, classique et HPOS : une tournée complète ; une tournée où un outil refuse et où un autre échoue (doubles déclarés comme tels), les autres ayant tourné et le bilan les nommant ; empreintes de la base et des fichiers du site identiques avant et après toute la tournée ; un canari absent du bilan et de chaque canal ; la commande du mode d'emploi, copiée telle quelle, fonctionne. **Un seul paquet de preuves**, vérificateur sans argument, déclaration `rejeu.json` dès la livraison. Suite Python rejouable sous Windows, sur une session propre (sans `TMPDIR`), en UTF-8 et en cp1252.

## Livrables

La commande, sa liste, ses tests, une section dans le mode d'emploi de la bascule, `production/A-32/PRET`. Rapport court : la liste des outils dans la tournée, et celle des outils laissés dehors avec la raison.
