# Relecture indépendante Codex — C-23

26 novembre 2026. Références : brief C-23, cahier des charges §3.9 et §4.4, doctrine et décisions du dépôt.

**Deux faux négatifs du détecteur ont été reproduits localement : témoin dans les attributs/commentaires HTML et témoin dans une réponse de redirection.** Il ne s’agit pas de fuites constatées sur le site : aucun accès au site, à une base ou à un compte n’a été effectué. Le rapport Claude n’a pas été consulté.

## 1. Conformité

Les livrables sont présents : commande, tests, inventaire motivé, matrice, contrôle inverse, mutation, restauration et `PRET`. Les cinq publics obligatoires sont inclus. Les exclusions concernant le cache d’hébergement, les robots vérifiés et les plans de site actuellement désactivés sont explicites. L’examen des fichiers livrés ne révèle pas de correctif apporté au code du paywall.

**I1 — Important — `wp/outils/demo/c23-preparer.py:70` : le rejeu normal remplace la politique de découverte avant de la tester.** `prepare()` écrit systématiquement `imagine_decouverte_reglages` et force `imagine_decouverte_relecture` à `fermee`, même sans `--mutation`. La matrice porte donc sur une configuration temporaire, pas sur les réglages présents à la livraison. Ces options participent effectivement à la décision d’accès de C-12 ; la restauration finale ne prouve pas leur comportement initial. La séparation entre préparation et commande GET est documentée, mais ne suffit pas à satisfaire le test de livraison en lecture seule. **Correction proposée :** préparer durablement le personnage épuisé dans le jeu de démonstration, puis conserver les réglages courants pendant le rejeu normal ; refuser explicitement un prérequis incompatible. Réserver les changements de politique à une recette de mutation distincte et adapter les attentes aux droits légitimes de relecture.

## 2. Exactitude métier

Cas déroulés à partir du §3.9, du code et du reçu `production/C-23/livraison.json` ; les résultats HTTP ci-dessous sont ceux du producteur, sans rejeu distant indépendant :

- **Abonné actif :** accès attendu à l’article et au PDF T4. `inverse-article` et `inverse-pdf` indiquent chacun HTTP 200, un témoin trouvé et `ok=true`. Le code exige aussi le SHA-256 exact et le type PDF pour le téléchargement.
- **Acheteur du seul T1 :** accès attendu au T1, refus au T4. `inverse-achat-C14` et `pdf-inventorie-11-endpoint` trouvent leur témoin ; `article` et `pdf-telechargement` n’en trouvent aucun pour ce public. Le retrait des témoins T1 de ses absences attendues respecte le droit d’achat au numéro.
- **Découverte épuisée :** `c12-epuisee` est accepté sans témoin ; le code exige le bloc `decouverte_epuisee`. Cette preuve reste limitée à la politique temporairement imposée, conformément au point I1.

Les dates de clôture et changements d’année ne constituent pas des règles implémentées par ce lot de détection. Le rejeu et la restauration sont pertinents ici : les reçus finaux annoncent des métadonnées, profils et actions planifiées identiques avant/après. L’interruption antérieure et les limites de sa récupération sont explicitement conservées dans `INCIDENTS.md`.

## 3. Tests

Exécutions locales réalisées sans création de fichiers auxiliaires :

- `python -B wp/tests/demo/c23-tests.py` : **12 tests réussis**, code 0.
- Fonction `verify()` de `wp/tests/demo/c23-verifier.py` : **25 contrôles sur 25 réussis**. Son unique écriture de `verification.json` a été interceptée en mémoire avec `unittest.mock.patch.object(Path, 'write_text')`, afin de respecter l’interdiction de modifier les preuves.
- Contre-épreuves en mémoire du détecteur : quatre réponses contenant le témoin dans une métadonnée Open Graph, une métadonnée Twitter, un attribut `data-content` ou un commentaire sont acceptées ; le même témoin dans un paragraphe visible est correctement refusé. Une redirection simulée contenant le témoin est également acceptée après suivi vers une page publique. Aucun transport réseau n’a été utilisé.

Les preuves fournies sont cohérentes avec les sources C-23 : **1 432 contrôles, 0 fuite, PASS**, puis preuve de mutation à **177 fuites, FAIL**, restauration et dernier vert postérieur. Ces résultats ne compensent pas les angles morts B1 et I2. Les tests HTTP et la mutation sur démonstration n’ont pas été relancés, conformément à l’interdiction d’accès du rôle relecteur.

**M1 — Mineur — `wp/tests/demo/c23-tests.py:15` : la première régression de fuite peut réussir pour une mauvaise raison.** Le test attend `ok=false` en exigeant `present='titre'`, alors que le corps ne contient pas ce titre. Il resterait vert si la détection du témoin régressait, puisque la surface absente suffit à échouer. **Correction proposée :** fournir le titre attendu, puis vérifier à la fois `leak=true` et `ok=false` ; conserver un cas sans témoin qui passe avec la même surface.

## 4. Sécurité et données

**B1 — Bloquant — `wp/outils/demo/c23.py:34` : la normalisation efface des emplacements de fuite obligatoires.** `re.sub(r'<[^>]*>', ' ', text)` supprime les balises avec leurs attributs et les commentaires avant toute recherche de témoin. Avec le témoin réel `CONTENU_FICTIF_RESERVE_DEMO-2026-T4_1` dans `<meta property="og:description" content="…">`, une page contenant le titre et les éléments de partage requis donne `ok=true`, `leak=false` et `structure=true`. Même résultat pour Twitter, un attribut HTML et un commentaire. Le contrôle « partage » vérifie l’existence des balises, mais pas leur contenu réservé ; cela contredit directement §3.9/§4.4 et le brief. **Correction proposée :** rechercher les témoins dans la réponse complète décodée, attributs et commentaires compris, en complément de la vue textuelle normalisée. Conserver une exclusion précisément délimitée des termes réfléchis de recherche. Ajouter une mutation de chaque support, avec surface valide, qui fasse échouer le contrôle.

**I2 — Important — `wp/outils/demo/c23.py:65` : le corps des redirections échappe à l’inspection.** Le gestionnaire suit la redirection native ; `fetch()` ne remet à `assess()` que la réponse finale. Reproduction sans réseau, avec un gestionnaire HTTP simulé : `/depart` renvoie 302 et le témoin dans son corps, puis `/arrivee` renvoie 200 et un extrait public avec le titre attendu. Résultat : `ok=true`, `leak=false`. Un visiteur peut pourtant lire le corps initial en désactivant le suivi des redirections. Cela concerne notamment les téléchargements refusés qui redirigent vers la page numéro. **Correction proposée :** inspecter chaque réponse intermédiaire avant de suivre sa destination, conserver le refus des destinations extérieures et tester une chaîne dont seul le premier corps fuit.

Aucun secret ni donnée réelle identifié dans les fichiers C-23 examinés. Les cookies et nonces restent en mémoire ; les reçus contrôlés ne les contiennent pas. Le transport est GET et borné à l’origine de démonstration, avec refus des redirections extérieures. Les problèmes B1 et I2 sont ceux du détecteur C-23 ; aucune correction de paywall n’est demandée sans fuite effective confirmée. Une fuite réelle révélée après correction devra être attribuée au lot propriétaire de la sortie, avec sa régression.

## 5. Doctrine

Le recours à la bibliothèque standard Python pour une recette HTTP et aux sessions natives WordPress évite de réimplémenter l’authentification. Le PHP d’inventaire déclare le typage strict. Aucun changement d’extension tierce n’apparaît dans le périmètre livré. Le point I1 reste un écart à la vérification de la configuration livrée ; B1 empêche de tenir la preuve d’étanchéité pour suffisante.

Aucun arbitrage métier, visuel ou touchant au réel n’est requis pour appliquer les corrections techniques proposées.

## 6. Études (lots sans code)

Sans objet : lot de code et de tests. Aucune consultation externe effectuée.

## Verdict

**À corriger.** Ce verdict n’est pas un GO.

- **Bloquant : B1** — témoins invisibles dans les attributs, balises de partage et commentaires HTML.
- **Important : I1** — politique de découverte remplacée avant le rejeu normal.
- **Important : I2** — corps des redirections non inspectés.
- **Mineur : M1** — régression de fuite pouvant passer grâce à l’absence du titre attendu.
