# Lot A-14 — Le rapprochement d'un export de contacts de la newsletter

**Voie** : 1. **Chantier** : A. **Délai** : trois heures. **Cahier des charges** : §4.3 (« Newsletter : rapprochement des contacts Brevo avec les comptes, attribution du statut »), §3.10.

## Pourquoi

Le jour de la bascule, les contacts de la newsletter devront être rapprochés des comptes du site, pour que chacun porte le bon statut. Avant de rapprocher quoi que ce soit, il faut savoir ce que donne le rapprochement : combien de contacts ont un compte, combien n'en ont pas, combien sont en double. Ce lot fournit l'outil qui le dit, sur un fichier fictif. Même esprit qu'A-13.

**Ce lot n'appelle pas Brevo, n'écrit rien dans le site, et ne réinscrit personne.**

## Ce qu'on veut

Un outil en **lecture seule** qui prend un export de contacts (fichier tableur) et un site, et rend un rapport :

- contacts qui ont un compte, contacts sans compte, comptes sans contact : des **nombres** ;
- doublons dans le fichier et adresses invalides, avec leur numéro de ligne, jamais l'adresse dans le résumé ;
- pour chaque contact rapproché, dans un fichier de sortie à part : ce que le site sait aujourd'hui (a un abonnement actif, ou non). Les colonnes « coopérateur » et « tarif » du §3.10 existent mais restent **vides** : le site ne les connaît pas encore. Ne les déduis de rien.

Règles :

- Le format de l'export n'est pas connu : la correspondance des colonnes est en configuration, comme dans A-13. Réemploie sa lecture de fichier.
- Rapprochement sur l'adresse électronique, sans tenir compte de la casse ni des espaces. **Rien d'autre** : pas de rapprochement par nom, pas de règle propre à un fournisseur d'adresses.
- Un contact marqué désinscrit ou bloqué dans le fichier est compté comme tel et le reste. L'outil ne propose jamais de le réinscrire.
- Un compte « sans email » (adresse technique) n'est jamais rapproché et n'apparaît dans aucune sortie avec cette adresse.
- Les sorties s'écrivent hors de la racine web et ne rejoignent jamais le dépôt quand elles viennent d'un fichier réel.
- Lecture du site par le chemin en lecture seule d'A-11, sans nouveau bootstrap. Classique et HPOS.

## Preuve

Un fichier fictif d'une trentaine de lignes (noms inventés, `@example.org`) contre le banc d'A-02 : comptes exacts, chaque doublon et chaque adresse invalide sur sa bonne ligne, le compte « sans email » absent, un contact désinscrit resté désinscrit, empreinte de la base identique avant et après. **Un seul paquet de preuves.**

## Livrables

L'outil, ses tests, son mode d'emploi en une page, `production/A-14/PRET`. Rapport court.
