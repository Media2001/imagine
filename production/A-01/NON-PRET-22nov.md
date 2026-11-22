# A-01 — PRET du 22 novembre invalidé par la fusion

22/11/2026, passe de corrections ouverte à 16 h 20 CET.

Le témoin `PRET` précédent est retiré ; sa copie historique est `PRET-invalide-22nov-historique.txt`. Les preuves de publication antérieures restent historiques, elles ne qualifient pas le code en cours de correction.

R4, R3, R1, R2, R6 et R7 sont en correction/tests. Aucun nouveau PRET ne sera déposé dans cette passe : **R5 nécessite le choix explicite de Ced « admin / scripts »**, absent des consignes. `DISALLOW_FILE_MODS=true`, `DISALLOW_FILE_EDIT=true`, mise à jour automatique désactivée et profil HTTP existant sont conservés, sans choisir à sa place.

Le contrôle R1 interdit désormais tout remplacement implicite de version : archive `package.json` et cœur épinglé devront être strictement égaux avant import SQL/bootstrap. La baseline commerciale 7.0.9 n'est pas remplacée par 6.9.1 ; ce dernier cœur de production n'est pas qualifié par la recette commerciale. Toute archive 6.9.1 sera explicitement refusée face au cœur 7.0.9 jusqu'à arbitrage/qualification dédiée. Ce refus n'autorise pas une mise à niveau.

Aucun import réel, archive Imagine, ancienne copie, accès agent, modification de l'outil partagé, installation hôte ou Git autorisé par cette note.
