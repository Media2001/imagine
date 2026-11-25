# Lot C-09 — Complément : des paiements fictifs, déclarés comme tels

**Voie** : 2. **Délai** : deux heures. **Dépend de** : C-09, C-13, B-02, C-14.

## Pourquoi

Trois lots butent sur le même mur. C-13 : la liste d'envoi des profils est vide (douze abonnements, aucun paiement validé). B-02 : « Mon compte » ne peut montrer ni deux échéances payées sur quatre, ni une échéance rejetée. Le prochain écran (les échéances) butera pareil. Tu as eu raison de ne rien inventer tant que personne ne l'avait écrit. C'est écrit ici.

Ce que la doctrine interdit, ce sont les données et les comptes **réels**. Une commande fictive payée à zéro euro, sur un site fictif, marquée fictive, est une donnée de test : tu l'as déjà fait pour P-NUMERO dans C-14. `docs/recette/profils.md` décrit des abonnés qui ont payé ; le site de démonstration doit pouvoir les montrer.

## Ce qu'on veut

Dans le script de profils de C-09, pour les profils dont l'état de départ **décrit** un paiement :

- A-CARTE, A-PAYPAL, A-ETRANGER, A-SANSMAIL, A-ECHEANCE, A-NONRENOUV : la commande initiale payée ;
- A-SEPA4 : deux échéances payées sur quatre, les deux suivantes à venir ;
- A-PAPIER : ce que son état décrit (actif, échéance à lancer ce mois-ci) ;
- A-GRACE et A-SUSP : une commande de renouvellement en échec, à la date que leur état suppose.

Comment :

- objets natifs (commande, renouvellement), état posé par les fonctions de WooCommerce et Subscriptions, **montant zéro ou montant de la grille fictive**, moyen de paiement nommé « Paiement fictif de démonstration », aucune passerelle chargée, aucun jeton, aucun mandat, aucun email ;
- chaque objet porte une marque de test lisible (métadonnée `imagine_demo_fictif`), et le script refuse toujours tout site qui n'est pas `imagine-test-…` ;
- rejouable : relancé, il remet les profils dans cet état.

Ce qui ne change pas :

- **A-VIR reste non payé** (c'est son rôle), comme tout profil dont l'état ne décrit pas de paiement. P-OFFERT, P-GEST, P-BENEF : seulement si le lien natif existe déjà ; sinon laisse-les, et dis-le.
- **Le renouvellement automatique reste non posé** (arbitrage du 23/11 : pas de reconduction sans moyen de paiement réel).
- **Aucune règle ne bouge** : un abonnement actif sans paiement validé reste exclu de la liste d'envoi. On donne aux profils les paiements que leur fiche décrit ; on n'assouplit pas l'exclusion.
- Tu ne modifies pas le code de C-13, de B-02 ni des bibliothèques closes. Si un de leurs tests attendait « aucun paiement », adapte l'attente du test de démonstration et signale-le.

## Preuve

Rejoue les recettes strictes de C-13 et de B-02 et dis, profil par profil, ce qui devient complet et ce qui reste partiel. Mets à jour le tableau créé / partiel / impossible de `production/C-09/A-VOIR.md`, et les `A-VOIR.md` de C-13 et B-02 pour ce que Ced peut maintenant ouvrir. Pas d'autre preuve.

## Livrables

Le script mis à jour, les trois `A-VOIR.md`, `production/C-09/PRET` redéposé. Rapport court.
