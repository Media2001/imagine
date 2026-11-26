# Finalisation parent — 2026-11-26T17:06:28.715375+01:00

**PRET : prêt à relire, non clos.** Préparation commune et rejeu global exécutés par le parent sur les sources finales, en UTF-8 et cp1252 : 1 123 tests, 34 569 assertions ; 14 outils, 279 contrôles ; zéro échec, erreur ou ignoré. Vérificateur propre relancé vert dans les deux contextes. Preuve des commandes et sources : `files/rapports/2026-11-26-17h06-portes-parent.json`. Les portes en attente décrites ci-dessous sont le constat historique de l’enfant, désormais accomplies par le parent. Aucun GO réel.

---

# A22 — gardien commun livré, candidat vérifié

**Un seul gardien** `wp/outils/bascule/stream_guard.py` est utilisé par A20/A21 et tous les inventaires concernés. Leurs validations propres de rapports restent en place. A03/A11 gardent leurs commandes PHP publiques via le pont minimal ; les autres commandes et arguments documentés sont conservés. Les refus historiques d’arguments sont contrôlés avant staging.

## Preuves réellement exécutées

Paquet unique `production/A-22/preuves/final`, issu de **a22-matrix-final-07**, après les dernières écritures du banc : **42 commandes, code réel 0**, sources stables ; **22 commandes natives** sur les onze banques fermées. Chaque runner natif exerce classique et HPOS. Windows réel `C:/Python314/python.exe`, 3.14.6 mesuré ; UTF-8 et cp1252, encodage enfant explicite. Aucun PHP hôte.

Vérificateur livré : **159 contrôles PASS sous UTF-8, 159 sous cp1252**, codes 0, stderr vide. Source/dépendances exécutées, inventaire et hashes exacts, noms de cas uniques, canaris absents des preuves. Style commun : trois fichiers PHP, zéro erreur/avertissement ; runner exact supprimé et absence relue.

Contrôles par console (les deux consoles portent les mêmes banques) :

| Lot | Python | PHP pur | Natif classique+HPOS | Runner | Gardien additionnel |
|---|---:|---:|---:|---:|---:|
| A02 | 1 | 17 | 120 | 7 | 0 |
| A03 | — absent | 10 | 87 | 9 | 23 |
| A10 | 5 | 10 | 187 | 7 | 0 |
| A11 | — absent | 19 | 290 | 7 | 23 |
| A12 | 1 | 15 | 124 | 8 | 23 |
| A14 | 3 | 8 | 58 | 8 | 23 |
| A15 | 2 | 14 | 78 | 7 | 23 |
| A16 | 3 | 23 | 78 | 7 | 23 |
| A17 | 3 | 42 | 66 | 7 | 23 |
| A18 | 3 | 37 | 100 | 7 | 23 |
| A19 | 5 | 9 | 108 | 7 | 23 |

S’ajoutent **17 tests Python A22 par console**. A03/A11 n’ont pas de banque Python : absence explicitement vérifiée, jamais un code 5 converti en succès. Leurs banques PHP pures et natives sont intégralement exécutées. A13 est un lecteur hors ligne sans bootstrap ; qualification dans les notes.

Sept canaux réels par outil concerné, sur les deux magasins : stdout direct, stderr direct, affichage puis exit, exit silencieux, shutdown stdout, shutdown stderr, shutdown echo. Arrêts précoces 0 et sorties tardives refusés sans publication. Pour chaque magasin, retirer le seul gardien dans la copie jetable laisse réellement fuir le témoin ; restauration des sources et fixtures, aucun octet brut du témoin conservé. Parcours documentés exécutés avec leurs seuls arguments littéraux.

A20 et A21 ont de nouveaux paquets **04** après la modification du gardien, non des empreintes recyclées : vérificateurs **111 / 49 PASS par console**, mutations réelles et contrôles stricts propres conservés. Leurs notes donnent les comptes détaillés. Les anciens paquets sont hors dépôt ; aucun nouveau paquet par lot fermé.

Six sondes du vérificateur sont vertes sur un miroir jetable : base identique, PRET futur accepté, corruption refusée, omission native rescellée refusée, dérive du gardien refusée et restauration verte. Le dépôt réel et ses marqueurs ne sont pas modifiés par ces sondes.

Relecture indépendante des **29 noms exacts** des runners finaux A20/A21/A22 : tous absents sémantiquement (`docker inspect` retourne 1 avec un diagnostic de disparition pour chaque nom). Ce n’est pas une inférence tirée d’un échec quelconque du service Docker. Noms, commandes et reçu dans `runner-absence.json`.

## Frontière parent

**CANDIDAT_GATE_PARENT : aucun PRET créé par cet enfant.** Préparation globale, T01 global et décision de PRET restent au parent, non exécutés ici. Leurs anciennes gates ne prouvent pas les sources corrigées. Tous les vérificateurs permettent un PRET futur et une preuve parent optionnelle ; compatibilité testée seulement sur miroir jetable. La ligne commune exacte est livrée dans `readme-ajout.txt`, à intégrer/vérifier par son propriétaire. Le verrou et le README partagé n’ont pas été modifiés par cet enfant.

Aucun réel, archive Imagine, compte fournisseur, Novamira, Git, déploiement, voie2, T02 ou A23 touché. Commandes exactes : `COMMANDES.md` et reçus `windows-matrix.json`. Les essais intermédiaires rouges/annulés ne sont pas des preuves vertes ; récupérations de runners possédés dans `cancelled-intermediates.json`.
