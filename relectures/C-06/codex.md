# Relecture indépendante Codex — C-06

Date : 21 novembre 2026. Périmètre : brief C-06, production C-06, moteur `Acces`, tests et lanceurs associés, contrat de décision C-03 et configuration commune de `imagine-pilotage`. Références : doctrine, exigences héritées de C-01, cahier des charges §3.4, §3.5, §3.8 et §3.9, décisions et arbitrages du 21 novembre. Le rapport de Claude n'a pas été lu. Aucun autre fichier n'a été modifié.

## 1. Conformité

Le périmètre fonctionnel demandé est présent : décision sans contenu, motif nommé, bloc, droits personnels/offerts/groupés, grâce, achats attachés au numéro exact, équipe, coopérateur et deux variantes de découverte. Les arguments sont explicites ; aucune lecture de base, de session, de réseau ou d'horloge dans le moteur.

La table de traçabilité de `production/C-06/notes.md`, section « Tests, preuves et reproduction », rattache les familles de règles au brief, aux paragraphes du cahier des charges et à l'arbitrage sur la suspension. Les limites de l'adaptateur et de l'étanchéité HTTP sont correctement distinguées du moteur pur.

Les anciens PDF, la grâce et la forme de la découverte restent explicitement signalés comme questions ouvertes. Le refus provisoire du PDF antérieur est isolé dans `Moteur::abonnement` et dispose d'un motif spécifique ; il ne constitue pas une règle métier validée. Les exigences de lancement standard et de documentation héritées de C-01 restent incomplètes : points C06-CX-01 et C06-CX-02 ci-dessous.

## 2. Exactitude métier

Cas déroulés manuellement dans le code, sans les présenter comme des exécutions PHP :

| Cas et référence | Chemin et résultat constatés à la lecture | Appréciation |
|---|---|---|
| §3.5 : ouverture numérique le 8 octobre 2026 après la sortie du n° 170 ; lecture d'un article de ce numéro à l'ouverture | Avec `debut` égal à l'instant de lecture et `fin` ultérieure, `Moteur.php:94` ne refuse pas le début égal ; la restriction d'ancienneté ne vise que le PDF. Résultat : complet, `abonnement_actif`, aucun bloc. | Conforme pour l'article du numéro en cours. Le PDF reste à arbitrer. |
| §3.9 : ancien abonné expiré ayant acheté le n° 170, lecture du PDF 170 en 2099 | `Moteur.php:127` n'applique aucune expiration à l'achat ; le motif `numero_achete` l'emporte sur `expire`. Résultat : complet, aucun bloc. Pour le n° 171, les deux droits refusent. | Conforme : droit perpétuel limité au numéro acheté, coexistence favorable. |
| §3.8 et arbitrage C-01/1 : grâce puis suspension, sans autre droit | Dans les dates du droit, `Moteur.php:103` renvoie complet avec `regularisation`. Avec l'état `suspendu`, la branche de la ligne 87 renvoie extrait. | Conforme au brief et à l'arbitrage. |

Les débuts sont inclus et les fins exclues. À la fin exacte d'un abonnement actif ou en grâce, le moteur refuse ; une seconde avant, il autorise dans le périmètre applicable. La durée découverte compare des secondes écoulées et le quota exige strictement `consommes < maximum`. Les achats comparent les identifiants sans conversion numérique. Aucun défaut métier supplémentaire établi dans les branches examinées.

Le calendrier papier et le calcul des anniversaires ne sont pas recalculés ici : les bornes sont fournies au moteur. Les lectures répétées ne consomment pas le quota ; la réservation atomique et la persistance sont explicitement reportées au branchement.

## 3. Tests

**C06-CX-01 — Important — `wp/plugins/imagine-pilotage/phpunit.xml:3`.** La configuration chargée par `composer test` déclare uniquement Numeros, Robots et Entreprise. La suite Acces n'est ajoutée que par `tests/Acces/phpunit.xml`, sélectionnée expressément par le lanceur C-06. Une régression du paywall peut donc laisser la commande standard verte sans exécuter un seul test C-06. Le brief reprend pourtant l'exigence C-01 « PHPUnit, lancé par `composer test` ». L'exception est reconnue dans les notes, mais ne satisfait pas cette exigence. **Correction proposée :** intégrer Acces à la configuration PHPUnit standard, conserver les suites existantes et vérifier que `composer test` exécute effectivement Acces avec les autres suites.

**Exécution indépendante limitée par l'environnement.** La vérification du prérequis `wsl.exe -d Ubuntu -- docker version --format '{{.Server.Version}}'` échoue avec `Wsl/Service/E_ACCESSDENIED`. Aucun test PHP n'a donc pu être rejoué dans le conteneur autorisé. Aucun PHP n'a été installé ou exécuté sur Windows. Le lanceur `prepare/run` n'a pas été lancé : il écrit des fichiers de preuves hors du seul rapport autorisé.

La commande de contrôle en lecture seule `python -B wp/tests/acces-runner/verify.py check` a été exécutée : elle échoue à la ligne 66, lors du contrôle de disparition du conteneur, car WSL refuse l'accès. Ce résultat ne démontre ni la présence du conteneur ni un échec des tests métier ; il empêche de confirmer le contrôle complet.

Contrôles locaux effectivement réussis, sans écriture : comparaison SHA-256 des **59 fichiers** référencés par `tests/final.json` et des **110 fichiers** du scellement `tests/artifact-verification.json`, sans divergence. Lecture du JUnit livré : **234 tests, 29 516 assertions**, dont **Acces : 50 tests, 9 536 assertions**, zéro erreur, échec ou test ignoré. Le reçu annonce aussi des codes 0 pour PSR-12, syntaxe et validation Composer. Ce sont des résultats de production dont les empreintes concordent avec les fichiers présents, **pas un nouveau passage PHPUnit par Codex**.

La couverture lue comporte les trente combinaisons type d'abonnement/type de contenu/état, les bornes avant/à/après, les deux changements d'heure pour la découverte, les achats perpétuels, les sous-ensembles de onze droits dans les deux ordres, les configurations invalides et une exception injectée. Les tests de coexistence encodent également le classement technique des motifs ; ils ne valent pas arbitrage métier de ce classement. Les tests serveur des pages, REST, flux et PDF restent hors du lot, comme prévu par le brief.

## 4. Sécurité et données

La validation précède les autorisations « ouvert », « robot » et « équipe ». Une entrée malformée ne se dissimule donc pas derrière un droit favorable. Le point d'entrée capture les `Throwable` et retourne un refus. Le résultat robot doit être une décision C-03 et une identité positive Google/Bing ; aucun simple booléen ne suffit.

`Decision` ne transporte que le booléen, le motif et le bloc. Aucun texte réservé, lien de PDF, secret ou donnée personnelle réelle relevé dans les sources et fixtures examinées. Les nonces, l'échappement HTML, les requêtes préparées et les caches HTTP ne sont pas applicables à cette bibliothèque pure. Cette lecture ne prouve pas l'étanchéité d'un futur branchement WordPress.

## 5. Doctrine

**C06-CX-02 — Mineur — `wp/plugins/imagine-pilotage/README.md:24`.** Le README de l'extension ne décrit pas C-06 et renvoie toujours au lanceur Numeros. Il ne permet pas de trouver depuis l'extension le contrat du moteur, les réglages de découverte et le lanceur propre à Acces. Ces informations existent uniquement dans les notes de production, alors que le §5 de la doctrine et C-01 exigent un README expliquant le fonctionnement et les tests. **Correction proposée :** ajouter une section C-06 avec un renvoi vers son contrat, ses réglages obligatoires et la procédure de tests en conteneur, cohérente avec la correction C06-CX-01.

Pour le reste, les sources examinées respectent PHP 8.2, `strict_types`, l'espace de noms demandé et les objets de décision immuables. Les blocs et motifs sont des identifiants, pas des textes d'interface à traduire. Le lot n'ajoute ni persistance de droits ni transitions d'abonnement concurrentes à celles des extensions retenues. `sources-officielles.json` consigne les références documentaires utilisées par la production ; aucune consultation externe n'a été effectuée pendant cette relecture.

## 6. Études (lots sans code)

Sans objet : lot de code PHP et de tests. Les constats documentaires sur les extensions ne sont pas présentés ici comme des comportements vérifiés sur une installation WordPress.

## Verdict

**À corriger.** Ce verdict n'est pas un GO.

- **Bloquant :** aucun défaut de code de cette gravité établi.
- **Important : C06-CX-01**, intégrer Acces à l'exécution standard `composer test`.
- **Mineur : C06-CX-02**, compléter le README de l'extension pour C-06.

Limite de validation : PHPUnit n'a pas pu être rejoué par ce relecteur en raison du refus d'accès WSL. Les preuves livrées concordent avec les fichiers présents ; le rejeu indépendant et le contrôle complet du lanceur restent à effectuer dans un environnement autorisé accessible.
