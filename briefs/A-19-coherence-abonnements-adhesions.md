# Lot A-19 — La cohérence des abonnements et des adhésions

**Voie** : 1. **Chantier** : A. **Délai** : trois heures. **Dépend de** : A-02, A-11. **Cahier des charges** : §4.3 (« Abonnés en ligne actuels : comptes, abonnements, moyens de paiement et historique repris du site actuel »).

## Pourquoi

Les abonnés en ligne ne sont pas migrés : ils restent en place, et c'est Memberships mis à niveau qui portera leurs droits. A-02 compte les abonnements et les adhésions par état ; il ne dit pas s'ils **se correspondent**. Or le paywall lira l'adhésion, la liste d'envoi lira l'abonnement et ses paiements. Un abonnement actif sans adhésion, c'est un abonné qui paie et ne lit pas ; l'inverse, quelqu'un qui lit sans payer. Avant la mise à niveau, il faut savoir combien de cas de chaque sorte existent. Ce lot fournit l'outil, prêt pour le staging d'Imagine vérifié.

**Ce lot ne corrige rien, ne relie rien, ne change aucun état et ne dit pas lequel des deux a raison.**

## Ce qu'on veut

Un complément du script d'audit, en **lecture seule**, par le lanceur confiné d'A-11. D'abord le standard : dix lignes dans le mode d'emploi sur la façon dont Memberships relie une adhésion à un abonnement et dont les états se suivent, d'après la documentation officielle et le code installé.

Puis des **comptes seulement**, chacun avec la phrase qui dit comment il est compté :

- un tableau croisé : état de l'abonnement contre état de l'adhésion liée, par plan (identifiant du plan, pas son nom) ;
- les abonnements sans aucune adhésion liée, par état ; les adhésions sans abonnement lié, par plan et par état ; les adhésions liées à un abonnement qui n'existe plus ;
- les comptes qui portent plusieurs abonnements actifs, et ceux qui portent plusieurs adhésions actives au même plan ;
- les abonnements actifs en renouvellement automatique sans moyen de paiement enregistré, par passerelle ; les abonnements actifs dont la date de prochain paiement est passée ; ceux qui n'ont aucune commande payée ;
- les abonnements en renouvellement manuel, par passerelle déclarée.

**Aucun identifiant de compte, d'abonnement ou de commande, aucun nom, aucune adresse** dans les sorties : des états, des identifiants de plan et de passerelle, des nombres. L'outil ne qualifie rien d'« erreur » : certains de ces cas sont voulus (abonnement offert, accès donné à la main), et c'est Imagine qui le dira.

Règle de la voie 1 : aucune sortie, sortie d'erreur comprise, ne recopie un chemin ou un nom tiré du site.

## Preuve

Sur le banc fictif, classique et HPOS : un couple cohérent, un abonnement actif sans adhésion, une adhésion active sans abonnement, une adhésion liée à un abonnement supprimé, un compte à deux abonnements actifs, un abonnement automatique sans moyen de paiement, un identifiant de connexion canari. Les comptes sont exacts, le canari est absent de toutes les sorties, rien n'est écrit (empreintes identiques avant et après). **Un seul paquet de preuves.** Suite Python rejouable sous Windows (cp1252).

## Livrables

Le script, ses tests, deux lignes dans le mode d'emploi de l'audit, `production/A-19/PRET`. Rapport court.
