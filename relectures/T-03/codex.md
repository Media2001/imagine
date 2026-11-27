# Relecture indépendante Codex — T-03

Date : 27 novembre 2026. Références : `relecteurs/AGENTS.md`, `doctrine/doctrine.md`, `doctrine/grille-relecture.md` et `briefs/T-03-rejeu-des-verificateurs-de-paquet.md`. Le brief ne cite aucun paragraphe du cahier des charges métier ; il renvoie au §6 de la doctrine. La relecture Claude n'a pas été consultée.

## 1. Conformité

L'essentiel du parcours demandé est présent : commande sans argument conservée, découverte déclarative, vérificateurs exécutés dans le conteneur, exclusions explicites, ligne `PAQUETS` et calcul du verdict des tests indépendant du contenu des résultats de paquet. Les trois lignes figurent dans `production/T-01/notes.md`. Python est ajouté au Dockerfile utilisé par la préparation existante. La limite concernant les matrices natives est indiquée.

Les adaptateurs A-20 à A-25 appellent les vérificateurs existants : paquet `preuves/final` pour A-20/A-21/A-22, options de contrôle documentaire `--require-shared-doc` pour A-23/A-25 et `--require-shared` pour A-24. L'exclusion actuelle d'A-20 est explicitement signalée dans la finalisation ; son lecteur est conservé. Aucun changement de contrôle n'est visible dans ces adaptateurs. L'absence de comparaison historique complète ne permet pas de certifier ici tous les fichiers antérieurs.

**C1 — Important — `wp/tests/t01/paquets.php:8` : le délai des paquets peut faire échouer des tests terminés au vert.** Le collecteur bénéficie de 150 secondes à partir de son lancement, après les tests et les outils (`wp/tests/t01/executer.php:200`), alors que l'ensemble reste sous le délai de 600 secondes de `wp/tests/rejouer.ps1:33`. Le budget Python de 120 secondes repart également de zéro. Cas limite : les tests et outils terminent au vert à 550 secondes ; un vérificateur attend ses 90 secondes autorisées. À 600 secondes, le délai extérieur interrompt le processus avant l'émission de `T01_RESULT`. Le lanceur produit alors un `REJEU ... FAIL`, bien que seul le paquet ait dépassé le temps disponible. C'est contraire à l'indépendance exigée par le brief. **Correction proposée :** calculer une échéance commune dès le début du processus, borner toute la phase paquets au temps réellement restant avec une marge pour publier le bilan, et convertir son expiration en erreur `PAQUETS` seulement, sans augmenter la limite T-01. Ajouter un test d'intégration avec un budget de tests presque épuisé et un vérificateur lent. Cas établi par lecture du code, non reproduit dans Docker ici.

## 2. Exactitude métier

Ce lot n'ajoute aucune règle d'abonnement, de calendrier, de paiement ou de droits. Deux cas du brief ont été déroulés dans le code :

1. **Journal déclaré absent.** `paquets.py:129` ajoute le lot aux exclusions avec `journaux absents`, puis poursuit sans appeler le vérificateur ni compter un échec. Le contrat automatisé correspondant vérifie également l'absence d'appel. Conforme.
2. **Reçu A-28 altéré d'un octet.** Le vérificateur A-28 compare l'inventaire et les empreintes, émet `PACKAGE_DRIFT`, puis le collecteur conserve ce nom autorisé. Le résultat paquet n'entre pas dans le calcul de `$pass`. Les journaux livrés confirment ce parcours nominal et l'égalité des deux dernières lignes `REJEU`. Conforme pour ce cas ; C1 reste un contre-exemple pour un paquet lent.

## 3. Tests

Commande réellement tentée depuis la racine, sans argument :

```text
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\wp\tests\rejouer.ps1
```

Résultat : code de sortie **1**, refus WSL **`Wsl/Service/E_ACCESSDENIED`** lors de la vérification initiale de Docker. Aucun test ni vérificateur n'a démarré et cette tentative n'a créé aucun conteneur. Dernières lignes :

```text
PAQUETS : 0 vérifiés, 1 échecs ; hors rejeu : aucun ; T-03 RUNNER_OUTPUT
OUTILS : 0 outils, 0 contrôles, 0 échecs ; hors rejeu : non evalue
REJEU : 0 tests, 0 assertions, 0 échecs, 1 erreurs, 0 ignorés — FAIL
```

Ce refus d'environnement n'est pas attribué au code T-03. Aucune préparation d'image, modification de permissions ou exécution de vérificateur sur Windows n'a été entreprise pour le contourner. Les contrats locaux et le banc de mutation n'ont pas été exécutés séparément ; les résultats ci-dessous sont ceux des pièces livrées, pas un rejeu indépendant réussi.

Les 102 fichiers référencés par `production/T-03/manifest.json` sont présents et leurs SHA-256 concordent. Les journaux `preuves/final/native/copy-proof/green.log` et `one-byte.log` contiennent respectivement :

- **9 paquets vérifiés, 0 échec**, puis **9 paquets vérifiés, 1 échec : A-28 PACKAGE_DRIFT** ; lots : A-21, A-22, A-23, A-24, A-25, A-26, A-27, A-28 et A-30.
- Hors rejeu dans les deux passages : A-20 (`declaration absente`), A-31 (`journaux absents`).
- Même bilan final : **1153 tests, 36075 assertions, 0 échec, 0 erreur, 0 ignoré — PASS** ; outils : 22, 582 contrôles, aucun échec.
- Deux noms distincts de conteneurs avec absence vérifiée. Le reçu associé annonce copie supprimée et reçu original inchangé ; ces états historiques n'ont pas été reproduits ici.

Les preuves locales annoncent 15 tests collecteur et 9 tests d'intégration réussis dans chacun des contextes UTF-8/cp1252. La couverture traite les déclarations invalides, sorties malformées, exclusions, liens symboliques et erreurs de lancement. Toutefois, `test_paquets.py:167` ne prouve pas l'indépendance du délai T-01 : son horloge simulée couvre uniquement les 120 secondes du collecteur, sans temps déjà consommé par PHP. Compléter ce cas comme indiqué en C1, ainsi que la saturation décrite en S1.

## 4. Sécurité et données

Les options visibles conservent le réseau désactivé, les deux montages en lecture seule, le système de fichiers racine en lecture seule, l'utilisateur 65534, les capacités retirées et les limites de ressources. Les vérificateurs sont lancés sans shell ; leurs sorties brutes ne sont pas publiées. Les codes et raisons affichables sont encadrés. Aucun accès à un site, une base, un compte ou une API n'a été effectué pendant cette relecture. Les contrôles WordPress de nonces, SQL et paywall sont sans objet pour cet ajout d'outillage.

**S1 — Important — `wp/tests/t01/paquets.py:68` : la limite de sortie arrive après l'allocation mémoire.** `subprocess.run(..., capture_output=True)` accumule intégralement stdout et stderr. Le plafond de 1 Mio n'est vérifié qu'au retour du processus (`paquets.py:74`) ; stderr est lui aussi entièrement capturé. Un vérificateur qui boucle en écrivant, ou imprime accidentellement un gros journal, peut donc faire épuiser la mémoire du conteneur avant que `VERIFIER_OUTPUT` soit calculé. Les 768 Mio protègent l'hôte, mais ne garantissent pas la survie du processus PHP qui doit encore publier le bilan des tests. **Correction proposée :** plafonner les deux flux pendant leur lecture, arrêter le vérificateur et ses descendants dès dépassement, et restituer seulement un contrôle rouge borné. Ajouter un test avec un producteur réel de sortie excessive dans le conteneur, vérifiant la conservation du bilan des tests et le nettoyage. Le défaut de bornage est constaté statiquement ; aucun épuisement mémoire n'a été provoqué ici.

## 5. Doctrine

L'outillage utilise les mécanismes existants de T-01 et la bibliothèque standard Python ; aucune extension métier n'est réimplémentée. Les ajouts PHP lus déclarent les types stricts. Les preuves livrées sont cohérentes avec leur manifeste, mais le §6 ne peut pas être considéré comme satisfait par cette tentative indépendante, arrêtée avant les tests.

### Décisions techniques, défaut proposé

Pour C1 et S1, défaut prudent : conserver toutes les limites d'isolation T-01, interrompre la vérification de paquet dès épuisement de son budget effectif et préserver le résultat déjà acquis des tests. Hermès peut appliquer ces corrections techniques sans arbitrage métier ou visuel. Aucun arbitrage demandé à Ced ; le rejeu indépendant reste à effectuer dans un environnement où l'accès WSL autorisé fonctionne.

## 6. Études (lots sans code)

Sans objet : lot de code et d'outillage, sans affirmation nouvelle concernant une extension tierce.

## Verdict

**À corriger.** Ce verdict n'est pas un GO.

- **Bloquant :** aucun défaut classé à ce niveau ; réussite du rejeu indépendant non établie à cause du refus d'accès WSL.
- **Important : C1**, budget des paquets pouvant transformer un succès des tests en échec global.
- **Important : S1**, sorties capturées sans borne pendant l'exécution, pouvant épuiser les ressources communes.
- **Mineur :** aucun point supplémentaire retenu.
