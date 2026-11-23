# C09 — Rapport final

- **Fait** : script rejouable installé sur imagine-test-demo ; 27 comptes natifs, 13 commandes non payées, 12 souscriptions manuelles et 14 adhésions, sans transaction/passerelle/email sortant.
- **Prêt à relire** : C09, avec les partiels/impossibles explicitement admis par le brief ; ce n’est pas une validation métier ni une démonstration de paiements.
- **À arbitrer** : aucun choix financier ou droit réel inventé ; propositions de précision et raccords manquants dans A-VOIR.md, sans modifier docs.
- **Bloqué partiellement** : robot vérifié impossible hors ligne ; découverte/validation email, paiements/mandats/accords, compteurs, listes d’envoi, offert/groupé/solidaire/achat/coopérateur non entièrement raccordés.
- **Périmètre** : seulement fichiers C09/profils sous wp/outils/demo, wp/tests/demo et production/C-09. Aucun hook, thème, bibliothèque close, Git, verrou, rapport global ou autre site modifié.

## Catégories

- **créé (4)** : V-ANON, V-FAUX, A-EXPIRE, E-ADMIN.
- **partiel (25)** : V-DEC, V-DEC-FIN, V-INSCRIT, A-CARTE, A-SEPA4, A-PAYPAL, A-VIR, A-PAPIER, A-GRACE, A-SUSP, A-NONRENOUV, A-ETRANGER, A-SANSMAIL, A-ECHEANCE, P-OFFRANT, P-OFFERT, P-GEST, P-BENEF, P-PRO, P-SOL-ATT, P-SOL-OK, P-NUMERO, P-COOP, E-REDAC, E-ABO.
- **impossible (1)** : V-ROBOT.

Les trois V-ANON/V-FAUX/V-ROBOT ne sont pas des comptes. Les 27 comptes existants sont tous testés par authentification et par la décision native ; deux scénarios sans compte complètent les 29 décisions. V-ROBOT n’a aucune preuve positive inventée.

## Résultats après les sources finales

- unitaires : **7/7**.
- natifs : **377/377**.
- http : **197/197**.
- securite : **10/10**.
- reset : **6/6**.
- regression_c08 : **30/30**.
- integrite : **8/8**.
- corrections : **41/41**.
- horloge : **11/11**.
- plan : **4/4**.
- Total de la dernière passe, sans compter les répétitions : **691 contrôles/tests réussis, 0 échec** (7 tests unittest et assertions de recettes pour les autres catégories).
- Installation, relance, altérations puis reset réel : ID principaux inchangés. Les altérations sont bien détectées avant restauration ; doublons natifs possédés supprimés, objet supplémentaire sur V-INSCRIT retiré.
- B00 conservé par comparaison exacte avec son snapshot initial ; trois comptes C08, abonnements, adhésions, articles et manifestes conservés. Aucune nouvelle collecte d’empreintes des bibliothèques closes ou du thème.

## Limites et incidents résolus

- Le dossier littéral « C:\Users\Ced\imagine voie2 » n’existe pas. La consigne permanente définit voie 2 dans C:\Users\Ced\imagine ; aucune lecture de la file voie 1.
- Les échecs de garde passive, de plan et de grille/rôle/classement ont été observés avant leur correction. Les tests de transports utilisent des sentinelles qui interdisent l’acte même sur le code fautif : aucun transport réel déclenché.
- Les prix synthétiques ont été relus avec leurs types PHP ; les assertions comparent explicitement des float. Aucun objet inventé pour adapter les nombres aux tests.
- Lecture et création administrative de commande réellement ouvertes pour E-ABO (HTTP 200) ; éditorial/réglages refusés (403). E-REDAC est également refusé par le parcours natif de réglages (403), en plus du contrôle de sa capacité réelle.

Une première recette PHP incluait le seed dans sa portée et son $id local a été écrasé : le numéro fictif B00 ID32 a subi une mutation transitoire. Restauration ciblée immédiate, snapshot B00 relu exactement égal au snapshot initial ; seed désormais isolé dans une fermeture dans les tests plan/horloge. Aucun compte ni donnée réel. Incident signalé, pas masqué par un reseed général.

Le calendrier trois ans et les six produits tarifaires fictifs sont complets ; cinq numéros sont matérialisés, raccords métier toujours distincts. E-REDAC partiel, E-ABO rôle dédié sans éditorial et lecture équipe ; renouvellement activé explicitement non démontrable accepté à 21h10. Inventaire C10 27/13/12/14 inchangé ; six produits ajoutés, pas six commandes. Aucun cron ajouté, aucun C10/Paywall.php, verrou ou rapport central modifié. Voir A-VOIR.md, corrections.json, clock.json, plan.json, safety.json et readback.json.
