Fait : C-03, clé v2 existante et arbitrages écrits réunis après instruction directe de Ced.
Prêt à relire : C-03 après suite complète et vérification ; pas un GO.
À arbitrer : aucune question absente considérée décidée ; référenceur et prérequis hébergeur restent des conditions d'intégration.
Bloqué : pas de branchement autorisé, ni adaptateur réel à délai dur dans ce lot.
Ensuite : reprise A-00 puis A-01 chemin court ; preuves C-01/C-04/C-02 revérifiées sans rejeu inutile.

21 novembre 2026. Le premier PRET C03-01 a précédé l'application des arbitrages : rapport initial inchangé et reçus/marqueur conservés dans production/C-03/tests-21nov/premier-pret-avant-arbitrages/. Aucune réécriture de cet historique.

État corrigé courant : c03-v2 encode le tuple version/configuration/identité/IP canonique ; DNS 1 000 ms, positif 3 600 s, négatif 60 s seulement sur nom hors domaine, directe discordante ou IP hors plage. Panne/timeout refusés sans cache, nouvelle requête retentée immédiatement. Googlebot et Bingbot seuls dans la configuration. Prérequis IP unique et proxies de confiance conservés dans notes.

Tests défensifs uniquement sur code corrigé : séparation du tuple et identité, deux DST, budget total sous/à limite, panne inverse/directe, timeout explicite, refus établis à 59/60 s, liste et valeurs livrées. Suite complète isolée : 184 tests / 19 980 assertions (Robots 101 / 298). Zéro échec/erreur/ignoré ; PHPCS, syntaxe, Composer strict et lint config PASS. Conteneur sans montage/port/service, réseau coupé ; supprimé et absence relue. Manifeste ciblé C-03 PASS.

Preuves C-01/C-04/C-02 vérifiées : sources propres inchangées, vraie composition C-02 inchangée, JUnit et cleanup verts. Reçu files/rapports/2026-11-21-preuves-acquises.json. Aucun accès site, DNS réel, contenu, service partagé, Git, donnée réelle ou déploiement.
