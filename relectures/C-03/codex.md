# Relecture indépendante Codex — C-03

Date : 20 novembre 2026. Références : `relecteurs/AGENTS.md`, doctrine, brief C-03 et exigences héritées de C-01, cahier des charges §3.9 et §4.4, décisions et cas R-26/R-27/R-28. Lecture de `production/C-03/`, du moteur, de sa configuration, de ses tests et de son banc local. Le rapport Claude n'a pas été lu. Aucun autre fichier n'a été modifié.

## 1. Conformité

Le périmètre demandé est couvert : décision explicite, deux méthodes configurables, configuration initiale Google/Bing documentée, DNS injecté, comparaisons IPv4/IPv6, cache injecté et durées distinctes. Le moteur ne lit pas les en-têtes et ne fait aucun appel réseau direct. Les notes expliquent correctement la frontière de confiance de `X-Forwarded-For` et les réglages à convenir avec l'hébergeur.

Les choix supplémentaires sont déclarés : refus des agents ambigus, séparation du cache par configuration et identité, expiration des instantanés CIDR, absence de repli entre méthodes. Les durées et la sélection des robots restent présentées comme des propositions à arbitrer. Les références §3.9/§4.4 figurent dans le moteur, la configuration et les notes.

L'absence d'adaptateur DNS réseau et de branchement paywall correspond au périmètre du brief. R-27 est couvert au niveau de l'identité seulement ; la restitution HTTP et le balisage, ainsi que R-26/R-28, restent à recetter dans les lots d'intégration. Le délai dur devra être garanti par le futur adaptateur, limite explicitement signalée dans la livraison.

Deux défauts du cache empêchent néanmoins de conclure à la conformité : C03-01 et C03-02 ci-dessous.

## 2. Exactitude métier

Déroulés manuels du §4.4, à partir du code livré, sans requête réseau :

| Cas | Attendu | Chemin et résultat du code |
|---|---|---|
| `Googlebot/2.1`, IP fictive `192.0.2.1`, PTR `crawl-fictif.googlebot.com`, directe contenant `192.0.2.1` | Identité Google vérifiée | Agent reconnu, suffixe autorisé, égalité binaire de l'IP : `verifie_dns`, robot `google`. Conforme. |
| Même agent/IP/PTR, directe contenant seulement `192.0.2.2` | Faux robot refusé | Aucune adresse concordante : `adresse_differente`, robot null. Conforme. |
| PTR `googlebot.com.exemple.net` | Refus sans résolution directe | Le suffixe `.googlebot.com` ne correspond pas : `domaine_refuse`. Conforme. |

Les CIDR sont comparés en binaire, avec contrôle de la famille et des bits partiels. L'expiration des plages et celle des entrées de cache sont exclusives. Une configuration différente change la clé ; un agent inconnu est refusé avant DNS/cache. Les limites de clôture éditoriale et de calendrier du C-01 sont sans objet ici.

**C03-02 — important — Durées de cache calculées en temps civil au lieu de secondes écoulées.**

- **Localisation :** `wp/plugins/imagine-pilotage/src/Robots/Verificateur.php:64`.
- **Problème :** `modify('+' . $ttl . ' seconds')` effectue une modification de l'heure locale du `DateTimeImmutable` fourni. Avec le fuseau nommé `Europe/Brussels`, une expiration qui traverse le retour à l'heure d'hiver peut dépasser le TTL annoncé. Cas à reproduire : partir de `2026-10-25T00:59:30Z`, convertir en `Europe/Brussels` (02:59:30, UTC+02), puis calculer le TTL négatif de 60 secondes. L'heure civile obtenue, 03:00:30 UTC+01, se situe **3 660 secondes** après la création. Un positif créé à 02:30 UTC+02 avec 3 600 secondes expire à 03:30 UTC+01, soit **7 200 secondes** plus tard. Cela prolonge une ancienne autorisation et empêche de retenter rapidement une panne DNS. Les tests actuels utilisent novembre et des décalages fixes ; ils ne traversent pas cette transition.
- **Correction proposée :** calculer l'échéance sur une chronologie UTC, en conservant les fractions de seconde, puis normaliser l'affichage en `Europe/Brussels`. Ajouter des tests aux transitions de printemps et d'automne, avec un instant initial UTC converti en fuseau nommé et des échéances attendues exprimées en UTC. Vérifier le refus exactement à l'expiration positive et la nouvelle résolution exactement à l'expiration négative.
- **Niveau de preuve :** analyse statique ; le scénario PHP n'a pas pu être exécuté dans cette session, pour la raison indiquée ci-dessous.

## 3. Tests

**PHPUnit n'a pas été rejoué pendant cette relecture.** PHP, Composer et `vendor/` ne sont pas disponibles dans le checkout. L'accès au banc autorisé a été tenté par `wsl.exe -d Ubuntu -- docker image inspect imagine-staging-e2e-public:644662e9cc4f --format '{{.Id}}'` : échec, code 1, `Wsl/Service/E_ACCESSDENIED`. Aucun conteneur n'a été créé, aucun paquet installé et aucune preuve livrée réécrite. Il ne s'agit pas d'un échec des tests PHP.

Contrôles réellement effectués, en lecture seule :

- Lecture du JUnit livré : la suite `Robots` annonce **89 tests, 199 assertions, zéro erreur/échec/ignoré**. Le total historique Numeros + Robots est de 128 tests et 300 assertions. Ce sont les résultats du producteur, pas une nouvelle exécution indépendante.
- Comparaison SHA-256 des **20 fichiers** PHP C-03 (sources, tests, configuration) avec `production/C-03/tests/final.json` : tous concordent. `composer.json` et `composer.lock` concordent également. Le README et `phpunit.xml` ont évolué avec les ajouts C-02 ; le reçu historique ne certifie donc pas l'intégralité du checkout actuel.
- Vérification locale de l'égalité des chaînes et de leurs hachages pour C03-01 : collision confirmée. Ce contrôle algébrique ne remplace pas un test d'intégration PHP du cache.
- Exécution de `check_artifacts.py` par `runpy`, bytecode Python désactivé et écritures `Path.write_text` remplacées en mémoire par un refus : échec à la ligne 49, avant toute écriture, sur les ajouts `src/Entreprise/` et `tests/Entreprise/` du lot C-02.

La suite livrée couvre les vigilances du brief : faux agent, inverse falsifiée, faux suffixe, IPv6, agent absent sans DNS, délai global, cache négatif plus court et en-têtes ignorés. Elle vérifie des résultats attendus et le nombre d'appels, pas seulement la structure du code. En revanche, elle ne couvre ni la collision entre deux couples identité/IP de C03-01, ni les transitions horaires de C03-02.

**C03-03 — mineur — Contrôle d'artefacts non rejouable après l'ajout d'un autre lot.**

- **Localisation :** `wp/tests/robots-runner/check_artifacts.py:49`.
- **Problème :** tout fichier ajouté depuis l'inventaire antérieur à C-03 doit appartenir à Robots. Les ajouts légitimes C-02 font donc échouer le contrôle documenté comme rejouable, alors que les 20 fichiers PHP propres à C-03 concordent avec le reçu. Les contrôles ultérieurs du fichier PHPUnit et de l'inventaire global reposent également sur l'ancien état complet du plugin. Cet échec ne prouve pas une régression du moteur C-03.
- **Correction proposée :** distinguer la vérification de l'instantané historique de la vérification du lot dans le checkout courant. Pour cette dernière, contrôler un manifeste explicitement limité à C-03 et les éléments partagés nécessaires à son exécution, sans refuser les ajouts des autres lots. Conserver les preuves historiques et produire les nouveaux résultats séparément.

## 4. Sécurité et données

**C03-01 — bloquant — Collision de clé permettant de réutiliser une identité vérifiée pour une autre IP.**

- **Localisation :** `wp/plugins/imagine-pilotage/src/Robots/Verificateur.php:45`.
- **Problème :** l'identifiant du robot et l'IP canonique sont concaténés sans séparateur ni encodage de leurs limites. Dans une même configuration contenant deux robots d'identifiants `robot` et `robot19`, avec des jetons d'agent distincts, les couples suivants produisent exactement le même suffixe de clé : `robot` + `192.0.2.1` et `robot19` + `2.0.2.1`, soit `robot192.0.2.1`. Les deux identifiants et les deux IP sont acceptés par les validations. L'exemple est purement local ; aucune IP n'a été contactée.
- **Conséquence :** après une vérification positive du premier couple, une requête présentant le second récupère la même entrée encore valide. Le retour du cache précède le DNS et renvoie directement la décision positive du premier robot. `estVerifie()` vaut donc vrai pour une IP qui n'a jamais été vérifiée. SHA-256 ne protège pas contre cette ambiguïté : les données hachées sont identiques. Les identifiants initiaux `google`/`bing` ne déclenchent pas cet exemple, mais la liste configurable demandée par le brief autorise cette configuration.
- **Correction proposée :** encoder sans ambiguïté le tuple complet (version, configuration, identifiant, IP), puis le hacher ; changer la version de clé pour invalider les anciennes entrées. Ajouter un test avec les deux robots, les deux IP et un cache partagé : le second couple doit effectuer sa propre vérification et être refusé si le DNS ne concorde pas. Vérifier aussi que l'identité rendue par un positif correspond au candidat.
- **Niveau de preuve :** égalité des chaînes et des hachages contrôlée localement ; conséquence établie par le chemin de retour du cache. Reproduction PHP complète à ajouter et à rejouer.

Aucun secret ni donnée d'abonné identifié dans les fichiers C-03 examinés. Les jeux DNS sont fictifs. Le contrôle de domaine impose une frontière de label et une résolution directe concordante ; les pannes DNS/cache donnent un refus. Le moteur n'expose aucun contenu et n'a ni SQL ni écran WordPress : droits d'administration, nonces, échappement et étanchéité HTTP seront à examiner lors du branchement. Aucune validation du paywall complet n'est revendiquée ici.

## 5. Doctrine

PHP pur, `strict_types`, espace de noms attendu, objets métier immuables et interfaces injectées respectent l'architecture prescrite. Le cache mémoire mutable est identifié comme adaptateur de démonstration. Le README documente l'API, les réglages, les commandes et les limites. Le reçu historique annonce des contrôles PSR-12 et de syntaxe réussis ; ils n'ont pas été relancés dans cette session.

Le principe « standard d'abord » est traité dans les notes avec une référence officielle à Memberships. Le lot ne remplace pas ses adhésions et ne modifie aucune extension tierce. Les paramètres non arrêtés et les responsabilités du futur adaptateur sont signalés. C03-02 reste un défaut de respect des durées exprimées en secondes, malgré la normalisation des dates exposées.

## 6. Études (lots sans code)

Sans objet comme catégorie principale : C-03 livre du code. Son volet documentaire contient des URLs officielles et de courtes citations dans `production/C-03/sources-officielles.json`, ainsi que les domaines et sources de plages dans la configuration. Les autres robots sont listés sans activation.

Les pages externes n'ont pas été consultées pendant cette relecture, conformément à l'interdiction d'accès à un site. Leur contenu actuel et la fraîcheur des sources de plages ne sont donc pas attestés indépendamment. La présence et la cohérence interne des références ont été examinées ; aucune plage réelle n'a été téléchargée.

## Verdict

**À corriger. Ce verdict n'est pas un GO.**

- **Bloquant — C03-01 :** supprimer l'ambiguïté de la clé de cache, qui peut transférer une décision positive entre deux IP et deux robots configurés.
- **Important — C03-02 :** calculer les TTL en secondes écoulées et couvrir les changements d'heure.
- **Mineur — C03-03 :** rendre le contrôle courant des artefacts C-03 indépendant des ajouts légitimes des autres lots.

Après correction, rejouer la suite Robots et ses nouveaux cas dans le banc autorisé. Cette relecture ne dispose pas d'une exécution PHP indépendante, l'accès WSL ayant été refusé.
