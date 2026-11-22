# A-01 — Relecture indépendante Codex

Date : 22 novembre 2026. Périmètre : `briefs/A-01-chemin-court.md`, son complément `A-01-reprise.md`, la production A-01 et les scripts associés dans `wp/`. Les arbitrages ultérieurs de `docs/decisions.md` et `briefs/A-01-publication.md` sont pris en compte : filtrage WordPress suffisant après vérification, création normale d'un site vide autorisée, témoin « vérifié » distinct de l'état du dashboard.

Consignes de `relecteurs/AGENTS.md`, doctrine et grille lues. Aucun accès à un site, une base, un compte ou une archive réelle. Aucun accès à la relecture Claude. Seul ce rapport est écrit.

## 1. Conformité

La commande `publish.py`, son mode d'emploi, les preuves et `PRET` existent. Le chemin normal réemploie les trois scripts, restaure hors réseau, injecte après leurs reçus, contrôle le runtime et écrit un témoin. Les limites réseau et les décisions de tables sont expliquées. L'absence de pare-feu système après vérification et l'état `running` du dashboard ne sont donc pas des anomalies.

- **R1 — important — `wp/outils/staging-court/inside.py:87`. Version du cœur remplacée sans contrôle de celle de l'archive.** La restauration copie systématiquement le cœur de l'image épinglée, puis utilise ce cœur au bootstrap et à la publication. La preuve actuelle porte sur WordPress 7.0.9, alors que `docs/decisions.md:24` donne 6.9.1 pour la production. `package`, récupéré à la ligne 90, n'est pas exploité pour vérifier cette correspondance. Une archive d'une autre version peut donc franchir les sondes et recevoir « vérifié » après changement implicite du cœur : la comparaison de `wp-content` ne prouve pas la fidélité de cette baseline. **Correction proposée :** sélectionner un cœur préparé correspondant à la version source, ou refuser explicitement une incompatibilité avant bootstrap ; réserver une montée de version à une étape annoncée et testée. Ajouter un cas source/cœur de versions différentes.

- **R2 — important — `wp/outils/staging-wp-integration/worker/worker.py:133`. Le moteur de table reste un motif de refus de l'import.** Le parseur SQL réutilisé impose `ENGINE = INNODB`. Un schéma fictif minimal accepté en InnoDB est refusé en MyISAM avec `SQL_DDL`, avant même l'inventaire des scripts natifs. Cela contredit la reprise, qui exige « Vues, déclencheurs, moteur de table : signalés, non bloquants ». La réserve générale sur le sous-ensemble SQL ne réalise pas cette exigence explicite. **Correction proposée :** prendre en charge les moteurs requis dans la grammaire contrôlée et les signaler au rapport, sans repli vers du SQL arbitraire. Tester la commande d'import avec une table MyISAM, pas uniquement le contrat PDO d'inventaire.

- **R3 — important — `wp/outils/staging-court/publish.py:428`. Les refus de restauration perdent leur cause exploitable.** Si `restore_and_verify` lève une erreur avant les reçus natifs — archive tronquée, limite dépassée, syntaxe SQL refusée, mot de passe invalide — le processus parent ne conserve qu'une empreinte de sortie et `OFFLINE_RESTORE_REFUSED`. Le programme enfant n'écrit alors pas `offline.json`, puis le runner est supprimé. Ced ne peut pas distinguer ces causes ni savoir quoi corriger, contrairement au rapport explicatif demandé. **Correction proposée :** produire et récupérer un reçu d'échec structuré contenant l'étape et un code appartenant à une liste sûre, avant destruction du runner ; ne pas exposer le stderr brut. Tester au moins archive tronquée et SQL non pris en charge, avec deux diagnostics distincts.

## 2. Exactitude métier

Deux cas du cahier des charges ont été déroulés par lecture du code et comparaison des instantanés du reçu `production/A-01/publication-22nov/3f837c790d4b/result.json`, sans nouvelle connexion :

1. **Abonné actif, §3.9 et §4.2.** Le nettoyage doit changer l'identité et les références dangereuses sans retirer le droit d'accès ni modifier l'abonnement. Dans les deux stockages, le droit `active` reste vrai ; les instantanés avant/après des six abonnements et des adhésions sont égaux. Les dates, états, montants, devise, produits et liens sont comparés, pas seulement le nombre de lignes. Conforme sur ces fixtures.
2. **Visiteur sans droit, §4.4 et réception du chapitre 5.** Le nettoyage ne doit pas ouvrir l'article protégé. Les droits API `guest`, `none`, `expired`, `cancelled` et `paused` restent faux dans les deux stockages. Conforme pour la conservation de ces droits. Cela ne démontre pas l'étanchéité HTTP/REST/flux/PDF : le thème de publication renvoie un marqueur fictif, et les notes annoncent correctement cette limite.

Cas limites A-01 également examinés : table personnelle sans décision, clé réintroduite au bootstrap, refus de sonde et erreur de nettoyage. Le reçu piégé établit un refus avant injection. Les réexécutions natives sont documentées dans les preuves antérieures ; elles n'ont pas été rejouées ici. Les limites de clôture, changement d'année et calendrier ne sont pas calculées par ce lot : A-01 doit conserver ces valeurs, non recalculer les échéances.

## 3. Tests

Exécutions locales effectuées sans création de fichiers annexes, avec bytecode Python désactivé :

| Commande | Résultat de cette relecture |
|---|---|
| `python -B wp/tests/a01-court/test_publication.py` | 8 tests réussis |
| `python -B wp/tests/a01-court/test_publication_preflight.py` | 7 tests réussis ; diagnostic historique, pas une nouvelle interdiction de création |
| `python -B -m unittest discover -s wp/tests/staging-e2e -p test_harness.py -v` | 17 tests réussis ; chargement via unittest pour éviter l'écriture du reçu par le lanceur |
| `python -B wp/tests/a01-court/verify_publication.py --report production/A-01/publication-22nov/3f837c790d4b/result.json` | PASS : 3 cas et concordance des empreintes avec les sources actuelles |

**32 tests Python passent.** La vérification des preuves est documentaire et locale ; `--live-cleanup` n'a pas été utilisé. Elle n'est pas une nouvelle exécution des trois publications.

Deux contrôles supplémentaires, uniquement en mémoire, reproduisent des écarts : appel du vrai parseur avec une table InnoDB puis MyISAM (R2) ; exécution du bloc `finally` original extrait par AST, avec suppression du runner en erreur et espion d'arrêt (R4). Le second n'appelle jamais l'arrêt. Ces contrôles constatent les défauts ; ils ne constituent pas une recette Docker.

Les tentatives `php -n wp/tests/staging-data/mu-plugin.php`, `php -n wp/tests/staging-data/runtime.php` et `php wp/tests/staging-data/pdo-contract.php` n'ont pas démarré : `php` absent du PATH. Aucune installation effectuée. Les suites qui écrivent des fixtures/reçus et les recettes qui accèdent aux sites ou bases n'ont pas été lancées, conformément aux restrictions de cette relecture. Les 12 tests archive et les 337 assertions de données restent des résultats déposés, non reproduits ici.

Les tests du sas couvrent les reçus manquants, le mauvais ordre, les exceptions d'injection/sonde et le refus runtime. Ils s'arrêtent cependant à `guarded_publish` et ne couvrent pas le nettoyage final de `main`, les diagnostics de restauration, le moteur MyISAM ni la version source du cœur.

## 4. Sécurité et données

- **R4 — important — `wp/outils/staging-court/publish.py:499`. Une erreur de nettoyage court-circuite l'arrêt obligatoire du site refusé.** La suppression des helpers et du runner précède `stop_site`, sans protection indépendante. Exemple : le site a démarré, l'écriture du témoin échoue, le reçu passe à `FAIL`, puis la suppression du runner échoue. L'exception sort du `finally` avant la ligne 515 ; le gestionnaire extérieur écrit l'échec mais n'arrête pas le site. Le contrôle en mémoire du bloc original confirme l'absence d'appel à l'arrêt. **Correction proposée :** tenter et relire l'arrêt du site refusé avant les suppressions, garantir les actions de sûreté par des blocs indépendants et conserver séparément les erreurs de nettoyage. Ajouter un test d'orchestration avec échec du témoin puis de suppression, qui exige quand même l'arrêt.

Dans les fichiers inspectés, aucun secret réel identifié. Le mot de passe opérateur transite par stdin ; les rapports natifs évitent les valeurs de lignes. L'isolation initiale, l'annulation des tâches et le renouvellement forcé bloqué sont étayés par les preuves déposées. Les accès agent ne sont pas utilisés par la commande. L'absence actuelle de ressources et les protections sur un vrai import ne sont pas certifiées par cette relecture locale.

## 5. Doctrine

- **R5 — important — `wp/outils/staging-court/publish.py:224`. Les modifications de fichiers restent interdites après publication vérifiée.** La configuration finale conserve `DISALLOW_FILE_MODS=true`, qui bloque les installations et mises à jour standards de WordPress, des extensions et des thèmes. Autoriser les hôtes de mise à jour ne rétablit pas ces opérations. Le staging livré ne permet donc pas le parcours normal de mise à jour de l'existant, objectif explicite de la reprise A-01. **Correction proposée :** permettre les mises à jour manuelles autorisées une fois la vérification acquise, en conservant la désactivation des mises à jour automatiques et les protections de sortie ; tester la capacité standard correspondante après publication.

Les scripts réemploient les mécanismes WordPress/WooCommerce documentés dans `wp/outils/staging/SOURCES.md` ; les sources PHP principales déclarent les types stricts et utilisent l'espace de noms Imagine. Aucune réécriture d'extension tierce n'est nécessaire aux corrections demandées. Les écarts R1 et R5 touchent directement l'exigence de staging fidèle et exploitable pour la non-régression.

## 6. Études (lots sans code)

Sans objet : lot de code. Les références officielles et leur reçu documentaire existent ; elles n'ont pas été consultées en ligne, l'accès à un site étant interdit au relecteur.

## Verdict

**À corriger.** Les preuves nominales sont substantielles et correspondent aux sources actuelles, mais les chemins de refus et plusieurs exigences de fidélité restent incomplets.

- **Bloquant :** aucun point classé à ce niveau sur le périmètre effectivement contrôlé.
- **Important :** R4 — arrêt contourné par une erreur de nettoyage ; R3 — cause du refus de restauration perdue ; R1 — changement implicite de version WordPress ; R2 — moteur de table encore bloquant ; R5 — mises à jour standards interdites après vérification.
- **Mineur :** aucun point distinct retenu.

Ce verdict n'est pas un GO d'import réel, de déploiement ou d'ouverture aux agents.
