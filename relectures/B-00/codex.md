# Relecture Codex — B-00

Date : 23 novembre 2026. Périmètre : brief B-00, production/B-00 et sources correspondantes dans wp/, y compris leurs interactions actuelles avec B-01 et C-08.

Consignes appliquées : `relecteurs/AGENTS.md`, doctrine et grille. Références : `docs/recette/profils.md`, décisions, cahier des charges §§3.1, 3.5, 3.9 et 4.2. Le brief ne cite pas de paragraphe numéroté du cahier des charges. Aucun accès à un site, une base ou un compte ; aucune lecture de `relectures/B-00/claude.md`. Seul le présent rapport est écrit.

## 1. Conformité

Le socle demandé est présent : cible fixe, création normale, identifiants hors dépôt, calendrier sur trois ans, cinq numéros dont un hors-série, médias générés, vingt articles, contenus complémentaires et modèle provisoire sans ACF. Les dates inventées et le chargement des bibliothèques non activables sont explicitement expliqués. L’exception Novamira est autorisée par le brief révisé et les décisions. Le constructeur prévoit bien l’activation du thème Imagine lorsqu’il existe.

**B00-01 — Bloquant — `wp/tests/demo/b00-recette.php:39`.** La sélection des articles compte tous ceux rattachés au numéro, puis exige exactement quatre articles et trois réservés. Or `wp/outils/demo/c08-seed.php:80` rattache au même numéro T1 deux articles réservés supplémentaires, sans les marquer comme fixtures B-00. Après installation des fixtures C-08, cette requête renvoie donc six articles dont cinq réservés. Le constructeur appelle obligatoirement cette recette et s’arrête sur son échec (`construire.py:250`). Le script de reconstruction du site permanent devient inutilisable dès le branchement de ce lot. **Correction proposée :** limiter les cardinalités aux objets B-00 du manifeste ou à leurs clés de fixture, préserver les objets des autres lots et ajouter un test de reconstruction après installation de C-08. Constat établi par lecture croisée ; reconstruction non exécutée.

**B00-02 — Mineur — `production/B-00/A-VOIR.md:14`.** Le parcours demande encore d’utiliser le mot de passe d’article pour voir le corps complet. Le plugin courant enregistre systématiquement C-08, qui refuse précisément d’en faire un droit de lecture. Ced ne peut donc pas obtenir le résultat annoncé avec ce parcours après une construction actuelle. **Correction proposée :** décrire le parcours réellement disponible avec C-08 et mettre à jour, dans ce même livrable, l’annonce du thème provisoire et du formulaire natif ; identifier explicitement les anciennes preuves comme historiques.

## 2. Exactitude métier

Deux cas du §3.5 ont été déroulés à la main avec le calendrier fictif B-00 et les méthodes `Numeros\Moteur::numeros()`, `horsSerie()` et `Numero::estCloture()` :

1. Commande le **4 octobre 2026**, avant la clôture fictive du 5 octobre : les quatre réguliers éligibles sont T4-2026, T1-2027, T2-2027 et T3-2027 ; le prochain hors-série non clôturé est celui d’août 2027. Le passage d’année et l’exclusion du hors-série du décompte de quatre sont cohérents.
2. Commande le **5 octobre 2026 à 00 h, Europe/Brussels**, exactement à la clôture : `estCloture()` utilise `>=`, donc T4-2026 est exclu ; restent T1 à T4-2027 et le hors-série 2027. Cela respecte l’interprétation documentée de la clôture incluse.

Il s’agit de comparaisons statiques, pas de commandes exécutées dans WordPress. B-00 charge la bibliothèque mais ne raccorde pas ces calculs à un abonnement. Le calendrier limité à 2028 ne permet pas quatre numéros futurs pour toute date : la bibliothèque expose les numéros non résolus, et B-00 ne prétend pas résoudre ce parcours métier.

Le rejeu simple est documenté par les snapshots historiques. Le rejeu après ajout de contenus par C-08 présente l’écart B00-01.

## 3. Tests

Exécution locale effectuée :

```text
python -B -m unittest discover -s wp/tests/demo -p "test_b00*.py" -v
Ran 4 tests in 0.064s — OK
```

L’option `-B` évite l’écriture de fichiers de cache Python. Un `ResourceWarning` concernant le faux HTTPError 404 apparaît sans faire échouer la suite.

Deux tests complémentaires ont été exécutés uniquement en mémoire, via l’entrée standard de `python -B -`. Ils appellent `ensure_site()` avec une API simulée et une liste enregistrant les attentes : refus `StagingBusy` au premier GET, puis refus au GET de suivi après un état `creating`. Résultat : **deux erreurs**, exception non interceptée aux lignes 32 et 46 ; aucune attente de 300 secondes. Aucun appel réseau ni fichier de test créé.

**B00-03 — Important — `wp/outils/demo/construire.py:32`.** Les refus de concurrence ne sont repris que pour le POST de création. Un refus pendant le GET initial ou le suivi interrompt immédiatement l’opération ; le GET préalable de `run_build()` a le même défaut. La règle du brief impose trois réessais espacés de cinq minutes lorsqu’une opération est refusée pour concurrence. Le test livré de `retry_busy()` ne vérifie pas son raccordement à ces chemins. **Correction proposée :** appliquer une politique de reprise commune aux appels concernés, sans multiplier les boucles imbriquées, et couvrir les lectures initiale et de suivi ainsi que l’épuisement des trois réessais.

**B00-04 — Important — `wp/tests/demo/b00-verifier.py:110`.** La recette annoncée dans le mode d’emploi exige encore qu’un cookie de mot de passe donne le texte réservé complet. Avec le plugin actuellement téléversé par le constructeur, `Paywall::register()` remplace cette autorisation par la décision de droits : cette assertion doit échouer. La même recette attend aussi le formulaire `post_password` et le libellé « Sommaire fictif », alors que B-01 affiche « Sommaire » et utilise son bloc de paywall. Même sans les fixtures supplémentaires de C-08, la recette livrée ne correspond donc plus à une construction neuve actuelle. **Correction proposée :** adapter la recette B-00 au thème et au contrôle d’accès présents, tester le refus du simple mot de passe et la lecture par un compte fictif autorisé, puis régénérer les preuves HTTP.

Tests non exécutés : constructeur, recette PHP dans WordPress et `b00-verifier.py`. Ils accèdent au staging ; les deux scripts Python écrivent aussi hors du rapport. `relecteurs/AGENTS.md` interdit ces accès au relecteur et l’utilisateur interdit les autres modifications. Les 81 contrôles WordPress et 81 assertions HTTP réussis sont des résultats archivés, pas une nouvelle validation indépendante.

La comparaison locale des SHA-256 avec `b00-final-verification.json` montre que `construire.py` et `imagine-site.php` ont changé depuis cette preuve. Les huit autres fichiers de sa liste correspondent. Les preuves historiques ne suffisent donc pas à certifier les sources relues, notamment pour B00-01 et B00-04.

## 4. Sécurité et données

Aucun secret ni donnée réelle identifié dans les sources et pièces B-00 examinées. Les secrets ne sont pas lus par cette relecture. Les comptes du seed utilisent `@example.org` ; les médias sont générés localement. Le contrôle du chemin des identifiants refuse le dépôt. La garde MU coupe les API WordPress de courrier et de HTTP ainsi que les passerelles disponibles ; sa portée limitée aux API WordPress est signalée dans la documentation.

La réponse HTML réservée archivée contient le formulaire natif sans le marqueur du corps réservé ; l’article ouvert contient son marqueur complet. Le code actuel C-08 prévoit une fermeture côté serveur et ignore le mot de passe comme droit. Cela ne constitue pas une vérification dynamique actuelle des sorties REST, flux, recherche et oEmbed. Les PDF sont volontairement factices et publics dans ce lot ; aucune validation de téléchargement protégé de production n’est déduite de B-00.

## 5. Doctrine

Le modèle s’appuie sur les types, taxonomies, métadonnées et fonctions WordPress. Les fichiers PHP B-00 examinés déclarent les types stricts, utilisent des espaces de noms Imagine et préfixent leurs données spécifiques. Le README de l’extension existe. Les bibliothèques métier restent séparées ; aucun remplacement inutile de Subscriptions ou Memberships relevé dans le périmètre B-00.

Les écarts de recette et de reconstruction empêchent de considérer le PRET historique comme une preuve de non-régression des sources actuelles. Ils doivent être corrigés sans rétablir l’ancien contournement du paywall par mot de passe.

## 6. Études (lots sans code)

Non applicable : lot de code et de contenu fictif. Les liens de documentation officielle sont consignés dans la production ; ils n’ont pas été ouverts, conformément à l’interdiction d’accès aux sites imposée au relecteur.

## Verdict

**À corriger.**

- **Bloquant : B00-01** — reconstruction interrompue après ajout des fixtures C-08.
- **Important : B00-03** — reprise de concurrence absente sur les lectures ; deux erreurs reproduites localement.
- **Important : B00-04** — recette HTTP incompatible avec les sources actuelles.
- **Mineur : B00-02** — parcours de consultation devenu inexact.

Ce verdict ne vaut ni GO, ni validation visuelle, ni confirmation de l’état actuel du staging.
