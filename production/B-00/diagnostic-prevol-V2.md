# B-00 — ancien blocage levé, voie 2

État actuel : **site construit et reconstruit, vérifications réussies**. L’interdiction de création provenait du brief antérieur ; la révision du 23 novembre 2026 à 13 h 45 autorise explicitement la création normale de `imagine-test-demo`, Novamira, sa licence et le MCP fournis par l’outil.

- Création normale réelle par `POST /api/sites`, via `ensure_site()` du constructeur, à partir du modèle `sandbox-wp-minimal`, PHP 8.3 ; l’outil a enregistré la création le 23 novembre 2026 à 13:03:15 UTC (14:03:15 CET).
- Aucune modification de l’outil, des modèles ou de sa configuration ; aucune écriture directe dans sa base. Aucun autre site, lot, voie, verrou ou rapport global touché.
- Après la création normale, installation de la garde MU avant WooCommerce, les extensions premium et les fixtures. API HTTP WordPress bloquée, email court-circuité avec résultat `false`, aucune passerelle disponible ; pas de compte WooCommerce.com ni activation de licence commerciale.
- Site : `http://192.168.129.32:8085` ; statut de l’API : `running`. Les six adresses d’`A-VOIR.md` sont observées : cinq HTTP 200 ; administration HTTP 302 vers la connexion, puis formulaire et administration authentifiée HTTP 200.
- Les deux erreurs de mise au point (inclusion `strict_types` via `eval-file`, permissions du dossier privé des secrets) ont été corrigées puis retestées. La preuve RED des quatre types absents est conservée ; aucune preuve d’échec n’est présentée comme un succès.

Les anciens constats du brief précédent restent sous `production/B-00/historique/`. Ils ne décrivent pas l’état actuel.

Preuves actuelles : `b00-creation-normale.txt`, `b00-construction.json`, `b00-reconstruction.json`, `b00-verification-http-idempotence.json`, `tests/b00-syntaxe-secrets.json`. Résultat détaillé et limites : `verification.md`.
