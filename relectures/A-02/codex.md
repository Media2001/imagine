# Relecture indépendante Codex — A-02

Date : 23 novembre 2026. Périmètre : `briefs/A-02-audit.md`, collecteur `wp/outils/bascule/audit`, banc `wp/tests/a02-audit/`, livraison `production/A-02/`, notamment le paquet final `preuves/211ac0849094/`.

Consignes appliquées : `relecteurs/AGENTS.md`, `doctrine/doctrine.md`, `doctrine/grille-relecture.md`. Le rapport Claude n'a pas été consulté. Aucun site, compte, service externe ou base existante n'a été consulté. Seul ce rapport a été écrit.

## 1. Conformité

Les sept rubriques, les sorties Markdown et JSON et les cinq priorités finales sont présentes. Le script ne charge ni WordPress ni les extensions. Le marqueur `PRET` porte explicitement sur l'outil et ses fixtures, sans prétendre avoir audité Imagine.

Le brief ne cite aucun paragraphe précis du cahier des charges. Les §4.1 (composants), §4.3 (migration) et §4.4 (sécurité) ont été lus comme contexte, avec les décisions du projet. Ce lot inventorie l'existant ; les règles de calendrier et de paiement des autres lots ne lui sont pas applicables.

Les limites principales sont déclarées : cache local seulement, PHP CLI, configuration littérale, site simple, attribution prudente des tables, absence de validation des droits effectifs. Le banc WordPress 7.0.9 ne constitue pas une qualification de la version 6.9.1 d'Imagine ; la livraison le dit clairement.

**A02-C1 — Important — Passerelles à héritage indirect absentes de l'inventaire.**

- **Localisation :** `wp/outils/bascule/audit:299`.
- **Problème :** `gatewayIds()` ne reconnaît que les classes qui étendent directement `WC_Payment_Gateway`, `_CC` ou `_eCheck`. Cas statique : un fichier définit `A02_Base extends WC_Payment_Gateway`, un autre définit `A02_Gateway extends A02_Base` et affecte littéralement `$this->id = 'a02_inherited'`. Le premier n'apporte aucun identifiant ; le second est ignoré, également par le préfiltre de `commerce()`. La passerelle n'apparaît donc pas, alors que son identifiant et son héritage sont statiquement disponibles. La réserve sur les identifiants dynamiques ne décrit pas cette omission. L'inventaire des moyens de paiement demandé au point 2 du brief devient incomplet.
- **Correction proposée :** résoudre les héritages statiques des sources inventoriées avant de collecter les identifiants, sans instancier les classes ; signaler explicitement les implémentations non résolues. Ajouter une fixture avec classe de base et classe concrète dans deux fichiers, ainsi qu'une classe sans lien avec les passerelles. Constat par lecture du code ; pas d'exécution PHP de ce cas pendant cette relecture.

## 2. Exactitude métier

Deux cas du brief ont été déroulés à la main puis comparés aux résultats archivés, dans les deux stockages :

| Cas | Attendu | Résultat archivé |
|---|---|---|
| Trois abonnements : actif mensuel ×1, suspendu mensuel ×2, en résiliation annuel ×3 | Trois groupes, un abonnement par groupe, intervalles conservés | Conforme dans `classic/audit.json` et `hpos/audit.json` |
| Deux restrictions Memberships : un article immédiatement, une catégorie après sept jours | Première règle immédiate sans différé ; seconde règle différée de 7 jours avec la catégorie ciblée | Conforme dans les deux rapports ; aucun titre ni utilisateur exporté |

Le rejeu archivé conserve les mêmes sections. Les commandes de 2023 et 2025 sont distinguées. Les fixtures ne couvrent pas une frontière de changement d'année ; la base UTC des commandes est néanmoins explicitement annoncée. Les dates de clôture et calendriers incomplets ne concernent pas ce collecteur.

**A02-C2 — Important — Les doublons de métadonnées gonflent le nombre d'abonnements.**

- **Localisation :** `wp/outils/bascule/audit:320` ; même construction dans la branche classique du même fichier.
- **Problème :** les deux jointures sur les métadonnées sont suivies de `COUNT(*)`. Un abonnement avec deux lignes identiques `_billing_period=month` et une ligne `_billing_interval=1` est compté deux fois. Des doublons sur les deux clés multiplient encore le résultat ; des valeurs contradictoires peuvent placer le même abonnement dans plusieurs groupes. Un audit d'existant doit précisément supporter ou signaler ces anomalies, sans transformer des lignes de métadonnées en abonnements supplémentaires.
- **Preuve exécutée :** les deux requêtes SQL ont été extraites du script et exécutées sur SQLite en mémoire, sans fichier ni connexion externe. Pour chaque stockage, une seule ligne d'abonnement donne `count=1` ; l'ajout d'une deuxième métadonnée de période identique donne `count=2`. Le nombre réel d'abonnements reste 1. Ce contrôle porte sur les jointures SQL, pas sur un rejeu PHP/MariaDB.
- **Correction proposée :** ramener les métadonnées à une valeur déterministe par abonnement avant l'agrégation et signaler les doublons ou conflits. Tester les deux stockages avec doublons identiques et contradictoires. Un simple `COUNT(DISTINCT id)` par groupe ne suffit pas à éviter le classement d'un abonnement dans plusieurs groupes contradictoires.

**A02-C3 — Important — Une surcharge du thème parent masquée par l'enfant reste comptée comme risque actif.**

- **Localisation :** `wp/outils/bascule/audit:537`.
- **Problème :** l'inventaire marque le parent et l'enfant actifs, puis `risks()` parcourt leurs surcharges indépendamment. Si le parent contient une ancienne version de `woocommerce/myaccount/form-login.php` et que l'enfant fournit la version actuelle du même fichier, les deux entrent dans le rapport. La version périmée du parent est ensuite comptée dans la synthèse, sans indication qu'elle est masquée par l'enfant. Le nombre de surcharges périmées à traiter ne représente donc pas les fichiers effectivement utilisés.
- **Correction proposée :** distinguer les rôles parent/enfant et résoudre la priorité des surcharges par chemin. Conserver éventuellement les fichiers masqués dans l'inventaire, avec leur état explicite, mais calculer la synthèse sur les surcharges effectives. Ajouter un cas où l'enfant masque un parent périmé, et un autre où le parent reste utilisé faute de surcharge enfant. Constat par lecture ; la fixture livrée utilise un seul thème.

## 3. Tests

Commande réellement lancée, sans écriture :

```text
python -B wp/tests/a02-audit/verify.py production/A-02/preuves/211ac0849094
```

**Résultat : code 1, vérification incomplète.** Le programme atteint l'assertion de disponibilité Docker à `wp/tests/a02-audit/verify.py:74`. Une seconde exécution avec affichage du diagnostic du sous-processus, uniquement en mémoire, identifie `Wsl/Service/E_ACCESSDENIED` (« Accès refusé »). Aucun contournement ni changement de permissions n'a été tenté.

Avant cet arrêt, les contrôles locaux du vérificateur ont passé : résultats archivés, égalité et recalcul des empreintes logiques, cohérence Markdown/JSON, rejeu des sections, variantes sans cache et correspondance des empreintes et de l'inventaire des sources actuelles. Les reçus contiennent **15 assertions unitaires, 100 d'intégration et 7 du runner, toutes PASS**. Ce sont les résultats archivés de la livraison, pas 122 tests fonctionnels rejoués par Codex. L'absence actuelle du conteneur n'a pas pu être confirmée.

Le lanceur complet `run.py` n'a pas été exécuté : il crée d'emblée un répertoire et des fichiers dans `production/A-02/preuves/`, contrairement à la restriction d'écriture de cette mission. L'accès WSL nécessaire est par ailleurs refusé. Les suites PHP et l'intégration sur sites fictifs n'ont donc pas été rejouées pendant cette relecture.

Le contrôle SQL en mémoire décrit en A02-C2 a, lui, été exécuté et reproduit le défaut dans les deux branches. Aucun fichier de test n'a été ajouté.

La couverture existante est substantielle : commerce réel synthétique, deux stockages, empreintes indépendantes, absence de bootstrap, refus des écritures, canaris, rejouabilité et inconnues explicites. Les trois cas A02-C1 à C3 manquent toutefois aux fixtures. Les tests de passerelles vérifient seulement la présence de `bacs`, `cheque` et `cod` ; celui des surcharges vérifie un thème unique. Après correction, ces cas doivent intégrer le banc et les preuves doivent être régénérées dans une session autorisée à les écrire.

## 4. Sécurité et données

Aucune fuite constatée dans les sorties finales examinées. Les données de test sont fictives ; les rapports exportent des identifiants structurels et des agrégats, sans valeurs de contacts, arguments de tâches, titres ni lignes brutes du journal.

Les valeurs SQL sont paramétrées, les noms de tables contrôlés, la connexion est placée en transaction de lecture seule, les données sérialisées sont décodées sans instanciation des classes. La sortie refuse un répertoire déjà existant ou situé dans le site. Les preuves archivées comparent les 55 tables et les fichiers avant/après, avec une sonde de refus d'écriture même sous le compte privilégié de la fixture.

Ces garanties ont été examinées dans le code et les artefacts ; leur exécution PHP n'a pas été reconfirmée ici. Les nonces et contrôles de droits HTTP ne s'appliquent pas à ce CLI. Le collecteur n'expose pas d'interface de paywall ; il précise correctement que les règles sauvegardées ne prouvent pas l'étanchéité des droits effectifs.

## 5. Doctrine

Le choix d'un collecteur spécifique sans bootstrap est motivé par la lecture seule. Il observe les formats des extensions retenues sans remplacer leur logique de droits ou de paiement. Le script déclare les types stricts et utilise l'espace de noms `Imagine\Audit`.

Le contrôle PSR-12 livré annonce honnêtement 0 erreur, 99 avertissements et un retour 1 ; il n'a pas été relancé. La qualification et les limites du banc sont séparées de celles du futur audit d'Imagine. Aucun arbitrage d'argent, de droits ou de comptabilité n'est introduit par les corrections proposées.

## 6. Études (lots sans code)

Non applicable comme catégorie de lot : A-02 livre du code. Les références officielles sont présentes dans `production/A-02/notes.md` et `sources-officielles.json`. Le reçu documentaire contient URL, statut HTTP, empreinte et occurrences d'un mot, sans citation exacte des passages : **doute documentaire** sur la démonstration de chaque affirmation par ces seuls reçus. Les pages n'ont pas été consultées pendant cette relecture, conformément au périmètre local imposé. Ce constat documentaire n'est pas un défaut fonctionnel supplémentaire.

## Verdict

**À corriger.**

- **Bloquant :** aucun défaut classé dans cette gravité.
- **Important — A02-C1 :** passerelles à héritage indirect omises.
- **Important — A02-C2 :** comptage des abonnements multiplié par les doublons de métadonnées, défaut reproduit.
- **Important — A02-C3 :** surcharges parent masquées comptées dans les risques actifs.
- **Mineur :** aucun point supplémentaire.

La vérification locale des artefacts a passé avant le contrôle Docker, mais le rejeu fonctionnel reste non confirmé dans cette session en raison du refus d'accès WSL et de la restriction d'écriture. Ce verdict ne constitue jamais un GO pour accéder à un staging, importer des données ou déployer.
