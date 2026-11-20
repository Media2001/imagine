# Relecture indépendante Codex — C-04

Date : 20 novembre 2026. Périmètre : `briefs/C-04-file-connecteur.md`, exigences héritées de C-01, `production/C-04/`, bibliothèque et banc de tests dans `wp/`. Références : cahier des charges §2.2, §2.4, §2.5, §4.1, §4.5 et chapitre 8 ; décisions du dépôt ; cas R-39, R-40 et R-41. Doctrine et consignes de `relecteurs/AGENTS.md` appliquées. Le rapport de l’autre relecteur n’a pas été consulté.

## 1. Conformité

Le socle demandé est présent : quatre types d’événements, clé déterministe, transitions fermées, validation extensible, quarantaine, reprises plafonnées, interfaces et doubles, destination CSV. Les choix concernant les événements du même abonnement, les accusés perdus, les champs provisoires et les arrivées tardives sont explicités. L’absence de branchement WordPress/Odoo est conforme au périmètre. Le choix intégré/n8n reste ouvert.

**C04-01 — Important — Raccordement au contrôle C-02 encore absent.**

- **Localisation :** `wp/plugins/imagine-connecteur/src/Validator.php:43`.
- **Problème :** le contrôle d’entreprise reste un callable facultatif sans raccordement livré à C-02. Celui-ci existe désormais dans le dépôt (`Imagine\Pilotage\Entreprise\NumeroEntreprise`). Avec la construction documentée `Validator::billing(['fiction'])`, tout numéro non vide, même valide, part en quarantaine pour contrôle indisponible. Le test existant injecte uniquement une comparaison à `fiction-valid` : il ne prouve pas l’utilisation de C-02. L’explication historique de son absence dans les notes ne satisfait plus le point 3 du brief, « par le lot C-02 quand il existe ».
- **Correction proposée :** livrer une composition explicite avec `NumeroEntreprise::depuisSaisie(...)->estValide()`, son chargement et un exemple utilisable, tout en conservant l’injection indépendante du moteur. Ajouter un test avec le vrai C-02 sur un numéro fictif valide et un numéro invalide ; actualiser la mention « futur C-02 ».

## 2. Exactitude métier

Déroulés manuels à partir du code, sans prétendre à une nouvelle exécution PHP :

1. **R-39, §2.5 et §4.5 — trois pannes puis rétablissement.** Avec cinq essais autorisés et les délais 10/20/40 secondes, les trois échecs conservent l’événement ; les passages avant échéance ne rappellent pas la destination. Le quatrième essai le marque envoyé. Un rejeu ultérieur est refusé. Le cas d’accusé perdu réutilise la clé, et le double distant ne produit qu’un effet. Résultat conforme, sous le contrat d’unicité atomique à faire respecter par Step, correctement documenté.
2. **R-40, §2.5 — total incohérent.** Une création dont le total diffère de la somme des lignes est mise en quarantaine avec la règle `amounts`. Son renouvellement reste en attente ; un autre abonnement passe. Résultat conforme à l’interprétation signalée dans les notes, lorsque l’alerte réussit. Le cas d’échec de l’alerte révèle C04-03.
3. **R-41, §2.4 — minuit et heure d’hiver.** La veille est calculée à partir du minuit civil de Bruxelles. Les deux occurrences de 02 h 30 du 25 octobre 2026, avec leurs décalages UTC distincts, restent dans le même fichier et sont triées par instant. Le calcul n’impose pas une durée de 86 400 secondes. En revanche, la combinaison du rattrapage et de l’ordre par abonnement révèle C04-02.

**C04-02 — Bloquant — Le rattrapage CSV peut livrer le renouvellement avant la création.**

- **Localisation :** `wp/plugins/imagine-connecteur/src/DailyCsvDestination.php:100`.
- **Problème :** `openBatch()` choisit le lot de chaque événement sans tenir compte du lot déjà attribué à son prédécesseur du même abonnement. Scénario : le 19 novembre, l’export vide du 18 est scellé. Le 20 novembre, avant l’export du 19, le worker traite dans le bon ordre une création survenue le 18 puis un renouvellement survenu le 19, tous deux déjà déposés et portant le même `subscriptionId`. La création est reportée au lot du 20, puisque le 18 est scellé ; le renouvellement reste dans le lot du 19, encore ouvert. L’export du 20 livre donc le renouvellement ; la création n’arrive que dans l’export du 21. Le tri du worker et le tri interne de chaque CSV ne corrigent pas cette inversion entre fichiers. Le point 5 du brief n’est plus assuré pour la destination de secours.
- **Correction proposée :** rendre l’affectation des lots monotone pour une même chaîne d’abonnement, sous le verrou et avec mémorisation durable : un successeur ne doit jamais rejoindre un lot antérieur à celui de son prédécesseur. Conserver le scellement et l’unicité des événements. Ajouter un test worker + export reproduisant ces trois journées, puis une relance après redémarrage.

**C04-03 — Important — Une alerte en échec est perdue définitivement.**

- **Localisation :** `wp/plugins/imagine-connecteur/src/Worker.php:104`.
- **Problème :** la quarantaine est enregistrée avant `Alerts::notify()`. Si cette méthode lève une exception, le chemin de validation l’attrape comme un incident de transport ; sa tentative de remplacement utilise cependant l’ancienne entrée `processing` et échoue au CAS. L’événement reste en quarantaine, sans alerte, puis tous ses rejeux sont refusés. La limite d’essais suit le même schéma : état épuisé enregistré avant notification, sans reprise de notification. Une interruption entre les deux opérations a le même effet. L’anomalie peut donc immobiliser un abonnement sans jamais être signalée, contrairement au §2.5 et au §4.5.
- **Correction proposée :** conserver un état de notification à effectuer avec la transition de la file, puis rejouer la notification indépendamment de l’envoi comptable jusqu’à son accusé. Préserver une clé de déduplication des alertes. Tester une alerte qui échoue une fois puis réussit, pour la quarantaine et pour l’épuisement des essais, sans nouvel appel à la destination.

## 3. Tests

**Réexécution PHPUnit impossible dans cette session.** La tentative d’accès au moteur local prévu par le banc, `wsl.exe -d Ubuntu -- docker image inspect imagine-staging-e2e-public:644662e9cc4f --format '{{.Id}}'`, échoue avec le code 1 et `Wsl/Service/E_ACCESSDENIED`. PHPUnit et PHPCS n’ont donc pas été relancés. Aucune installation ni connexion à un site, une base ou un compte n’a été effectuée.

Les lanceurs livrés écrivent dans `production/C-04/tests/` et la préparation réécrit aussi `composer.lock`. Ils n’ont pas été exécutés, afin de respecter l’interdiction de modifier un autre fichier. Le vérificateur `check_artifacts.py` écrit lui aussi un reçu ; il n’a pas été lancé tel quel.

**Vérification effectuée en lecture seule :** comparaison SHA-256 des 30 fichiers de la bibliothèque avec `production/C-04/tests/final.json`, inventaire de même taille et aucun écart. Le JUnit `final.xml` rapporte **22 tests, 161 assertions, 0 erreur, 0 échec, 0 test ignoré**. Le reçu annonce également les codes nuls du lint, de la syntaxe et de Composer. Ces résultats sont ceux de la production ; ils ne constituent pas une exécution indépendante de cette relecture.

La suite couvre utilement doublons, réponses perdues, temporisations, matrice des transitions, expiration du bail, quarantaine, ordre en mémoire, minuit, changements d’heure, scellement, corruption JSON et lien symbolique. Les assertions de nombre d’effets distants et d’identité des fichiers vérifient des résultats observables.

Les scénarios des points C04-01 à C04-04 ne sont pas couverts. L’ordre d’abonnement et le report des exports sont testés séparément, ce qui masque leur interaction. Le changement d’année et les événements d’un abonnement à instant exactement égal ne disposent pas de tests dédiés ; l’ordre par clé à égalité est toutefois documenté. Les cas de réception restent distincts des tests unitaires, conformément aux consignes actives.

## 4. Sécurité et données

**C04-04 — Bloquant — Le contenu conserve des références PHP permettant de contourner la liste blanche.**

- **Localisation :** `wp/plugins/imagine-connecteur/src/Event.php:19`.
- **Problème :** le tableau reçu est stocké directement dans la propriété `readonly`. Une copie de tableau PHP conserve les références présentes dans ses éléments ; `readonly` ne détache pas ces références. Cas à reproduire : fournir `content['identity']` par référence à une variable contenant initialement seulement `name` et `email`, construire et déposer l’événement, puis ajouter `preferences` à cette variable externe. Le contenu de l’événement change après son contrôle initial. Le validateur de facturation ne revérifie pas les clés autorisées et accepte toujours le nom ; une destination reçoit alors les préférences interdites par le §2.2 et le brief. La destination CSV les enregistre également dans son journal JSON, avant que sa relecture ne rejette ce journal. La même faiblesse permet de modifier des montants sous une clé d’idempotence inchangée. Constat issu de l’analyse du passage des tableaux par référence, non réexécuté ici.
- **Correction proposée :** construire un instantané détaché de toute référence, à tous les niveaux autorisés, avant de le conserver et de le valider, ou refuser explicitement les références entrantes. Ajouter un test modifiant les variables d’origine après construction et après dépôt : aucun champ ni montant de l’événement ne doit changer et aucune donnée interdite ne doit atteindre la destination.

Aucun secret ni donnée personnelle réelle identifié dans le périmètre examiné ; les exemples utilisent des personnages fictifs et `@example.org`. Les messages de transport bruts ne sont pas conservés. Les chemins d’export sont bornés au dossier fourni et les cibles symboliques sont refusées, sous l’hypothèse documentée d’un dossier privé de confiance.

Le CSV conserve les valeurs textuelles telles quelles ; l’obligation d’importer les colonnes comme texte est annoncée et reste à contractualiser avec Step. Ce cœur PHP n’expose ni route WordPress ni contenu éditorial : droits, nonces, SQL et étanchéité du paywall ne sont pas applicables à ce lot.

## 5. Doctrine

PHP strict, espace de noms, séparation de WordPress, dates immuables et horloge injectée sont présents. L’immuabilité du contenu doit être corrigée selon C04-04. Le README explique les réglages et les tests. Les choix ayant une incidence future sur la comptabilité sont identifiés dans les notes et ne valent pas autorisation de branchement.

Le cœur sur mesure est expressément demandé par le brief ; aucune réimplémentation supplémentaire d’un parcours WooCommerce n’a été trouvée. La couverture native des extensions reste renvoyée à A-00. Cette relecture n’a effectué aucune consultation externe.

**C04-05 — Mineur — La correspondance entre règles et paragraphes de référence manque.**

- **Localisation :** `production/C-04/notes.md:45`.
- **Problème :** la section décrit les règles de facturation et leurs interprétations sans renvois précis au cahier des charges ; les sections sur l’ordre, le rejeu et l’export ont la même lacune. Le lecteur doit reconstruire leur justification depuis le brief, alors que la grille demande un rattachement de chaque règle métier à sa source.
- **Correction proposée :** ajouter une table règle → paragraphe du cahier des charges ou point du brief → test, en distinguant les exigences des interprétations soumises à arbitrage. Inclure notamment §2.2, §2.4, §2.5, §4.5 et les points 3 à 7 du brief.

## 6. Études (lots sans code)

Sans objet : lot de code et de tests. Les notes intégré/n8n exposent des conséquences d’architecture, sans valider le choix d’un produit ni la couverture d’une extension.

## Verdict

**À corriger.** Ce verdict n’est pas un GO.

- **Bloquant : C04-02** — inversion possible de l’ordre d’un abonnement entre exports quotidiens.
- **Bloquant : C04-04** — événement modifiable par références externes, contournement de la liste blanche.
- **Important : C04-03** — perte définitive d’alerte après échec de notification.
- **Important : C04-01** — composition avec le C-02 désormais disponible et test d’intégration manquants.
- **Mineur : C04-05** — traçabilité des règles vers leurs paragraphes de référence.

La nouvelle exécution des tests reste à faire dans un environnement autorisé où WSL est accessible, avec les cas de régression associés aux corrections.
