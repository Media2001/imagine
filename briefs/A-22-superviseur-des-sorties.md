# Lot A-22 — Un seul gardien pour les sorties des outils d'inventaire

**Voie** : 1. **Chantier** : A. **Délai** : trois heures. **Dépend de** : les corrections d'A-20 et d'A-21 (le gardien y est écrit). **Cahier des charges** : §4.4 (sécurité), §2.5 (protection du flux).

## Pourquoi

Les relectures d'A-20 et d'A-21 ont trouvé un trou qui ne leur est pas propre. Nos outils d'inventaire chargent le WordPress du site entier, donc tout le code de ses extensions. Leur promesse est qu'aucun chemin ni aucun nom tiré du site ne sort, sortie d'erreur comprise. Or le lanceur passe la main à PHP sans surveiller ses deux flux : une extension qui écrit directement sur la sortie, qui s'arrête en plein chargement, ou qui imprime quelque chose en fin de processus, parle à l'opérateur sans filtre. Les bancs ne le voyaient pas : leur canari était un simple affichage, que le tampon retenait.

Le même lanceur sert aux outils déjà clos. Aucun n'a encore tourné sur une copie du site réel : c'est le moment de fermer la porte partout, une fois, au même endroit.

**Ce lot ne change aucun compte, aucun rapport, aucune règle d'un outil clos. Il ne change que ce qui peut sortir du processus.**

## Ce qu'on veut

Le gardien écrit pour A-20 et A-21 (un processus qui lance PHP, retient ses deux flux jusqu'à la fin, et ne rend à l'opérateur que des messages d'une liste fermée) devient **le point commun**, et tous les outils qui chargent le WordPress du site passent par lui.

- Commence par la liste : pour chaque outil de `wp/outils/bascule/` (A-02, A-03, A-10 à A-19), dis s'il charge le WordPress du site et s'il laisse PHP hériter des flux. Un tableau dans tes notes. Un outil qui retient déjà les deux flux (A-14 semble le faire) est contrôlé par les mêmes canaris, pas réécrit.
- Chaque outil concerné passe par le gardien commun. Sa commande du mode d'emploi ne change pas, ses arguments non plus, ses codes de refus non plus.
- Un arrêt avant la fin, même avec un code de sortie zéro, est un refus. Une sortie apparue après l'annonce de succès est un refus.
- Ce qui a été retenu n'est écrit nulle part : ni dans un journal, ni dans un reçu.

Si un outil clos ne peut pas passer par le gardien sans changer de comportement, arrête-toi sur celui-là et dis pourquoi ; continue les autres.

## Preuve

Sur le banc fictif, par outil concerné, quatre canaris posés par une extension fictive : une écriture directe sur la sortie, une écriture directe sur la sortie d'erreur, un affichage suivi d'un arrêt pendant le chargement, une fonction de fin de processus qui imprime. Chaque canari est absent des deux flux et de tous les fichiers produits, et l'outil refuse avec un code fermé. Une mutation témoin : sans le gardien, au moins un canari sort (le contrôle peut échouer).

Les lots clos le restent : pour chacun, le rejeu de sa suite existante, verte, suffit, comme pour la correction commune d'A-17. Pas de nouveau paquet de preuves par lot clos : **un seul paquet, celui d'A-22**. Suite Python rejouable sous Windows (cp1252). Le parcours du mode d'emploi de chaque outil, copié tel quel, fonctionne toujours.

## Livrables

Le gardien commun, le tableau des outils, les tests, une ligne dans le mode d'emploi commun, `production/A-22/PRET`. Rapport court.
