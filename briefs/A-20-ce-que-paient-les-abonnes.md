# Lot A-20 — Ce que paient aujourd'hui les abonnés en ligne

**Voie** : 1. **Chantier** : A. **Délai** : trois heures. **Dépend de** : A-02, A-11. **Cahier des charges** : §3.4 (« Annuel, et seulement annuel », « Trois tarifs », « Livraison à l'étranger »), §4.3 (« Abonnés en ligne actuels »).

## Pourquoi

Le nouveau site porte un seul produit, annuel, à trois tarifs, payé en une ou quatre fois. Les abonnés en ligne, eux, restent en place avec ce qu'ils ont souscrit au fil des années : d'autres produits, peut-être d'autres durées, des montants d'époque. Imagine doit arrêter sa grille (décision 3 du chapitre 7) et dire ce que devient chaque ancien cas ; pour cela il faut une photographie : combien d'abonnés sur quel produit, à quel rythme, à quel montant, livrés où. A-02 compte les abonnements par état et par périodicité ; il ne croise pas avec le produit, le montant ni le pays.

**Ce lot ne modifie aucun abonnement, ne propose aucune correspondance entre un ancien produit et un nouveau tarif, et ne qualifie aucun cas d'anomalie.** La correspondance est une décision d'Imagine.

## Ce qu'on veut

Un complément du script d'audit, en **lecture seule**, par le lanceur confiné d'A-11. Pour les abonnements dans un état vivant (actif, en attente, suspendu, en annulation à terme), des **comptes seulement**, chacun avec la phrase qui dit comment il est compté :

- par produit ou variation (identifiant, jamais le nom) : le nombre d'abonnements, par état ;
- par produit, la périodicité réelle de l'abonnement (intervalle et période), et le nombre de ceux qui ne sont **pas** annuels ;
- par produit, les montants récurrents distincts et le nombre d'abonnements à chacun ; quand un montant est porté par moins de cinq abonnements, il est rangé dans une ligne « autres montants » qui ne donne que le nombre ;
- le nombre d'abonnements à plusieurs lignes de produit, avec une ligne de frais, avec une ligne de port ;
- par pays de livraison (code du pays) : le nombre d'abonnements, et combien portent une ligne de port ; les pays à moins de cinq abonnements sont regroupés sous « autres pays » ;
- le nombre d'abonnements dont la devise n'est pas celle du site, et de ceux dont le montant récurrent est nul.

**Aucun identifiant de compte, d'abonnement ou de commande, aucun nom, aucune adresse** dans les sorties : des identifiants de produit, des états, des codes de pays, des montants agrégés, des nombres. Règle de la voie 1 : aucune sortie, sortie d'erreur comprise, ne recopie un chemin ou un nom tiré du site.

## Preuve

Sur le banc fictif, classique et HPOS : deux produits, un abonnement annuel et un mensuel, deux montants dont un porté par un seul abonnement (il doit tomber dans « autres montants »), un abonnement livré à l'étranger avec une ligne de port, un abonnement à montant nul, un nom de produit canari. Les comptes sont exacts, le canari est absent de toutes les sorties, rien n'est écrit (empreintes identiques avant et après). **Un seul paquet de preuves.** Suite Python rejouable sous Windows (cp1252). Le parcours nominal du mode d'emploi, copié tel quel, fonctionne : un test le lance avec les seuls arguments que la ligne du mode d'emploi donne.

## Livrables

Le script, ses tests, deux lignes dans le mode d'emploi de l'audit, `production/A-20/PRET`. Rapport court.
