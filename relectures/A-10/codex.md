# Relecture indépendante — A-10

Relecteur : Codex. Date : 25 novembre 2026. Paquet examiné : `eaeb5368fbca`.

Références : `relecteurs/AGENTS.md`, doctrine, grille, brief A-10, cahier des charges §4.3 et décisions du dépôt. Relecture de la production courante, de la commande et du banc A-10, ainsi que des éléments A-02 réutilisés. Aucun accès au réel ni à un site externe. `relectures/A-10/claude.md` n’a pas été lu. Seul le présent fichier est écrit.

## 1. Conformité

Les livrables sont présents : commande autonome, tests, deux lignes ajoutées au mode d’emploi A-02, notes et `PRET`. Les champs demandés sont représentés ; les restrictions email sont comptées ; les expirés et les compteurs d’usage nuls figurent dans des listes séparées. Aucun reclassement ni suppression n’est effectué. Les choix de fenêtre UTC, de statuts, de récurrence configurée et de compteur enregistré sont explicités.

**R1 — Important — `wp/outils/bascule/a10/Inventory.php:153` — Les codes encore portés sans fiche correspondante sont invisibles.** L’inventaire part exclusivement des lignes `posts` de type `shop_coupon`, puis recherche les porteurs par leur nom. Un abonnement actif portant `ancien-code`, dont la fiche a été supprimée ou renommée `nouveau-code`, n’entraîne donc aucune entrée pour `ancien-code` ; dans le second cas, la nouvelle fiche peut afficher zéro porteur. Aucune anomalie ne signale cette omission. Cela compromet l’inventaire complet des codes et abonnements rattachés demandé avant migration (§4.3), précisément sur un historique ancien. Constat par lecture du chemin de collecte, non reproduit sur une base pendant cette relecture.

Correction proposée : compléter les noms des fiches par les noms distincts des lignes coupon portées par les abonnements des états retenus. Pour un nom sans fiche, conserver les décomptes et signaler explicitement la configuration introuvable ; laisser type, montant, limites et récurrence inconnus. Ajouter un cas fictif de suppression ou renommage dans chaque magasin. Aucun identifiant d’abonné ne doit sortir.

## 2. Exactitude métier

Deux cas du périmètre §4.3 ont été déroulés à partir de la fixture, puis comparés aux rapports classique et HPOS enregistrés :

| Cas | Résultat attendu et comparaison |
|---|---|
| `a10-recurring-fee` porté par les abonnements | Un porteur dans chacun des états actif, suspendu, en attente et résiliation en attente. Les doublons de lignes ne doivent pas multiplier les comptes. Quatre commandes récentes explicites et un renouvellement donnent cinq commandes ; ancienne, future et corbeille sont exclues. Les deux rapports correspondent. La limite configurée de trois paiements est présentée séparément, sans prétendre calculer un solde. |
| `a10-expired-never-used` | Expiration au 1er janvier 2000 et compteur nul : le même nom doit apparaître dans `expired` et `never_used`. C’est le cas dans les deux rapports ; aucune utilisation ni aucun porteur n’est inventé. |

À la lecture, les comparaisons des commandes incluent les deux bornes ; l’expiration utilise une comparaison stricte, donc une égalité exacte à l’instant d’observation n’est pas classée expirée. Le calcul du 29 février est ramené au 28 février de l’année précédente. Ces règles sont cohérentes avec les conventions annoncées, mais leur preuve aux bornes reste à compléter (R3).

## 3. Tests

Commande réellement lancée : `python -B wp/tests/a10/verifier.py`. **Code retour 1**, erreur `OWNED_CONTAINER_NOT_CONFIRMED_ABSENT`. Le diagnostic sur le seul conteneur nommé par le reçu révèle `Wsl/Service/E_ACCESSDENIED` : l’environnement interdit l’accès à WSL. Cela ne prouve pas qu’un conteneur subsiste et ne constitue pas une régression fonctionnelle démontrée.

Le vérificateur atteint ce contrôle après ses vérifications des reçus, des rapports, des oracles, des empreintes de base et de la préservation A-02. J’ai vérifié séparément les 50 fichiers scellés : aucune divergence SHA-256 ; le manifeste des sources correspond également. Les reçus enregistrent **6 assertions unitaires, 97 natives et 7 de runner**, toutes vertes. Les empreintes avant/après sont identiques pour les 55 tables de chacun des magasins. Ce sont des preuves enregistrées contrôlées, pas 110 assertions natives réexécutées par moi.

Aucun PHP hôte n’est disponible dans le PATH. Le rejeu natif n’a pas été lancé : WSL est inaccessible et `--replay` appelle un runner qui crée d’autres fichiers dans `production/A-10/preuves/`, contrairement à la restriction d’écriture de cette relecture.

**R2 — Mineur — `wp/tests/a10/seed.php:114` — L’oracle étiquette une date locale comme UTC.** `date('Y-m-d\TH:i:s\Z')` formate la date dans son fuseau courant et ajoute un `Z` littéral ; il ne convertit pas en UTC. Le même procédé est utilisé pour les dates de création et modification. Le banc UTC masque ce défaut ; avec un fuseau non nul, l’oracle peut contredire à tort la projection UTC.

Correction proposée : convertir explicitement les dates de l’oracle en UTC, sans modifier les objets métier, puis ajouter un passage avec `Europe/Brussels`, couvrant hiver et été.

**R3 — Mineur — `wp/tests/a10/seed.php:87` — Les bornes temporelles annoncées ne sont pas éprouvées.** Les commandes fictives sont placées à quelques jours, deux ans ou dans le futur ; aucune n’est exactement à la borne des douze mois ou à l’instant d’observation. Une inversion de `>=` en `>` passerait donc ces tests. Les expirations de la fixture sont également très éloignées de l’instant observé.

Correction proposée : fixer l’horloge du banc et tester les égalités ainsi qu’une seconde de part et d’autre des bornes, pour les commandes et l’expiration, dans les deux magasins. Conserver le test unitaire du 29 février.

## 4. Sécurité et données

Aucune fuite identifiée dans les sorties fictives examinées. Les noms de codes constituent l’exception autorisée ; les autres valeurs personnelles ne sont pas projetées. Les requêtes de valeurs sont préparées, les noms de tables dérivent d’un préfixe validé, la désérialisation interdit les classes, et les erreurs de commande sont réduites à des codes techniques.

La collecte ne démarre pas WordPress ; elle utilise une transaction `READ ONLY`, termine par rollback et n’appelle aucun envoi ni planificateur. Les gardes de chemin, l’ouverture exclusive et les permissions 0700/0600 sont présents. Les empreintes enregistrées incluent les tables de planification. La liaison à l’audit par SHA-256 n’authentifie pas le site, limite correctement déclarée. Nonces, routes publiques et paywall : hors périmètre de cette commande CLI.

## 5. Doctrine

Le recours au stockage natif sans bootstrap est motivé par l’exigence d’absence d’écriture ; les getters natifs servent d’oracle sur le banc. La projection pure est séparée de l’accès SQL. PHP strict et espace de noms `Imagine\` sont présents dans le module, avec un README. Les références officielles sont consignées dans la production ; elles n’ont pas été consultées en ligne lors de cette relecture.

### Décisions techniques, défaut proposé

Pour R1, défaut prudent : conserver les codes orphelins et leurs nombres de porteurs, signaler les réglages inconnus, sans déduire une remise future ni décider de supprimer un code. Pour R2 et R3 : oracle réellement UTC et horloge de test déterministe. Ces corrections ne nécessitent aucun arbitrage de Ced ni accès au réel.

## 6. Études (lots sans code)

Sans objet : lot de code. Aucune étude d’extension à valider ici.

## Verdict

**À corriger.** Ce verdict n’est pas un GO.

- **Bloquant :** aucun défaut classé à ce niveau.
- **Important :** R1 — omission des codes encore portés sans fiche correspondante.
- **Mineur :** R2 — fuseau de l’oracle des dates ; R3 — couverture des bornes temporelles.

Limite de vérification : contrôle local des artefacts effectué, mais vérificateur complet et rejeu natif non validés dans cette session en raison du refus d’accès WSL. Après correction, refaire les preuves classique/HPOS dans l’environnement autorisé.
