# C09 — Rapport final

- **Fait** : script rejouable installé sur imagine-test-demo ; 27 comptes natifs, 13 commandes non payées, 12 souscriptions manuelles et 14 adhésions, sans transaction/passerelle/email sortant.
- **Prêt à relire** : C09, avec les partiels/impossibles explicitement admis par le brief ; ce n’est pas une validation métier ni une démonstration de paiements.
- **À arbitrer** : aucun choix financier ou droit réel inventé ; propositions de précision et raccords manquants dans A-VOIR.md, sans modifier docs.
- **Bloqué partiellement** : robot vérifié impossible hors ligne ; découverte/validation email, paiements/mandats/accords, compteurs, listes d’envoi, offert/groupé/solidaire/achat/coopérateur non entièrement raccordés.
- **Périmètre** : seulement fichiers C09/profils sous wp/outils/demo, wp/tests/demo et production/C-09. Aucun hook, thème, bibliothèque close, Git, verrou, rapport global ou autre site modifié.

## Catégories

- **créé (5)** : V-ANON, V-FAUX, A-EXPIRE, E-ADMIN, E-REDAC.
- **partiel (24)** : V-DEC, V-DEC-FIN, V-INSCRIT, A-CARTE, A-SEPA4, A-PAYPAL, A-VIR, A-PAPIER, A-GRACE, A-SUSP, A-NONRENOUV, A-ETRANGER, A-SANSMAIL, A-ECHEANCE, P-OFFRANT, P-OFFERT, P-GEST, P-BENEF, P-PRO, P-SOL-ATT, P-SOL-OK, P-NUMERO, P-COOP, E-ABO.
- **impossible (1)** : V-ROBOT.

Les trois V-ANON/V-FAUX/V-ROBOT ne sont pas des comptes. Les 27 comptes existants sont tous testés par authentification et par la décision native ; deux scénarios sans compte complètent les 29 décisions. V-ROBOT n’a aucune preuve positive inventée.

## Résultats après les sources finales

- unitaires : **7/7**.
- natifs : **364/364**.
- http : **192/192**.
- securite : **5/5**.
- reset : **4/4**.
- regression_c08 : **30/30**.
- integrite : **8/8**.
- Total de la dernière passe, sans compter les répétitions : **610 contrôles/tests réussis, 0 échec** (7 tests unittest et assertions de recettes pour les autres catégories).
- Installation, relance, altérations puis reset réel : ID principaux inchangés. Les altérations sont bien détectées avant restauration ; doublons natifs possédés supprimés, objet supplémentaire sur V-INSCRIT retiré.
- B00 conservé par comparaison avec le snapshot initial ; trois comptes C08, abonnements, adhésions, articles et manifestes conservés. Les fichiers PHP des bibliothèques closes et le thème installé correspondent aux sources (93 fichiers vérifiés).

## Limites et incidents résolus

- Le dossier littéral « C:\Users\Ced\imagine voie2 » n’existe pas. La consigne permanente définit voie 2 dans C:\Users\Ced\imagine ; aucune lecture de la file voie 1.
- L’extracteur officiel était indisponible (backend search-only). Les six pages officielles ont été récupérées par HTTP 200 et leurs passages ciblés lus avant l’implémentation native.
- Premier état expiré refusé par WCS : son alias historique last_payment reflétait la création de commande, même sans paiement. Dates administratives de création de fixture remises avant le terme ; aucune date_paid ni transaction ajoutée.
- Une première recette de reset a révélé un objet possédé supplémentaire sur un profil sans commande attendue : suppression ciblée ajoutée et vérifiée. Un test natif a aussi révélé l’absence de garde URL directe PHP : corrigée avant le feu vert.
- Les inventaires natifs utilisent les statuts explicites propres à Subscriptions (les statuts Woo par défaut omettaient les actifs) et le type natif string de billing_interval est interprété comme entier. Aucun objet n’a été inventé pour adapter les nombres aux tests.

Voir A-VOIR.md pour la vue profil par profil et readback.json/http.json pour les preuves nominatives. Le calendrier trois ans et la grille trois tarifs × une/quatre fois sont explicitement incomplets ; le zéro de fixture n’est pas un prix réel.
