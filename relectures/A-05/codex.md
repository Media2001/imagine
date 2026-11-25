# Relecture indépendante Codex — A-05

Date : 25 novembre 2026. Périmètre : `briefs/A-05-nettoyage.md`, `production/A-05/`, outil et tests A-05 dans `wp/`, dépendances A-03/A-04 nécessaires à la vérification.

Consignes appliquées : `relecteurs/AGENTS.md`, doctrine et grille. Le rapport Claude n'a pas été consulté. Aucun site, compte, archive Imagine ou service externe n'a été utilisé. Seul ce rapport a été écrit ; les essais complémentaires ont été exécutés en mémoire.

## 1. Conformité

Les livrables demandés sont présents : commande, tests, documentation, formulaire conservateur et `PRET`. Le formulaire reprend les 22 dossiers d'extensions, trois règles de tables et trois dossiers de médias du diagnostic ; toutes les actions sont `garder`. Les choix supplémentaires sont exposés : inventaire audité des propriétaires de tables, chemins conventionnels, WP-Cron par crochet exact, refus de reprise d'une désinstallation dont l'achèvement est incertain.

Le brief ne cite aucun paragraphe numéroté du cahier des charges. Les dispositions pertinentes relues sont les §4.1 (composants), §4.3 (conservation des comptes, abonnements et historique, précisée par les décisions de reprise de l'existant) et §4.4 (sécurité et sauvegardes). Le lot ne décide aucune suppression réelle.

**P1 — Bloquant — Une extension à seulement désactiver peut perdre ses fichiers.**

- **Localisation :** `wp/outils/bascule/a05/clean.py:155`.
- **Problème :** la protection d'un dossier partagé ne considère que les autres fichiers principaux dont l'action est `garder`. Avec `shared/one.php` à `retirer` et `shared/two.php` à `desactiver`, le plan est accepté. Le calcul produit successivement la désactivation de `one.php`, la suppression du dossier `shared`, puis la désactivation de `two.php`. L'exécution supprime donc aussi les fichiers de la seconde extension, contrairement à l'action demandée. Le défaut existe également si cette seconde extension était déjà inactive.
- **Preuve :** appel en mémoire de `validate()` et `operations()`, inventaire de deux extensions partageant leur dossier ; l'assertion interdisant la suppression du dossier échoue. Les lectures de chemins et les tailles sont doublées, sans suppression effective.
- **Correction proposée :** refuser la suppression d'un dossier contenant un autre fichier principal dont l'action n'est pas explicitement `retirer`, en nommant le conflit. Ajouter les variantes active/inactive et les deux ordres du plan. Si plusieurs retraits partagent un dossier, terminer leurs désactivations et désinstallations explicites avant de supprimer ce dossier une seule fois.

## 2. Exactitude métier

Deux cas applicables du cahier des charges ont été déroulés dans le code :

1. **§4.1 — Préserver le socle commercial.** Une demande de désactivation de WooCommerce, Subscriptions ou Memberships, même inactive, passe par `protected_plugin()` et est refusée avec le nom de l'extension. Les tests unitaires correspondants ont réussi. Une dépendance conservée doit bénéficier de la même protection ; P2 montre une lacune.
2. **§4.3 — Préserver les comptes et l'historique existants.** Une suppression explicite de `wp_users`, `wp_posts` ou `wp_wc_orders`, avec l'inventaire des propriétaires renseigné, est refusée par `protect()`. Une extension non nommée reste à `garder`. Les tests unitaires de ces protections ont réussi. Les preuves livrées classique/HPOS attestent séparément le retrait des seules ressources fictives ciblées et la conservation des autres.

**P2 — Bloquant — Une dépendance déclarée dans un commentaire de ligne est ignorée.**

- **Localisation :** `wp/outils/bascule/a05/clean.py:126`.
- **Problème :** le lecteur de `Plugin Name` accepte les commentaires `//` et `#`, mais celui de `Requires Plugins` n'accepte qu'une éventuelle étoile. Une extension conservée avec les en-têtes `// Plugin Name: Kept` et `// Requires Plugins: base` est inventoriée avec `requires: []`. Le retrait de `base/main.php` est alors autorisé. Le refus obligatoire d'une dépendance n'est pas assuré pour cette syntaxe d'en-tête.
- **Preuve :** exécution en mémoire de la véritable fonction `inspect_site()` sur ces sources fictives, puis de `protect()` : dépendances obtenues `[]`, aucun `A05_DEPENDENCY:base/main.php`. L'assertion attendant ce refus échoue.
- **Correction proposée :** utiliser un lecteur d'en-têtes conforme à celui de WordPress, sans charger les extensions, notamment pour les préfixes de commentaires et les fins de commentaires. Tester les variantes de syntaxe, puis vérifier le refus du retrait et de la désactivation de la dépendance avec son nom.

Les limites de dates métier, de calendrier éditorial et d'échéances ne relèvent pas de ce lot. La fraîcheur de sauvegarde et la reprise sont examinées au titre des tests et des garde-fous techniques.

## 3. Tests

**Rejeu effectué pendant cette relecture : 13 tests unitaires livrés exécutés, 13 réussis.** Chargement de `wp/tests/a05/test_clean.py` par `python -B -` et `unittest`, sans fichier de lanceur ajouté. Le chemin de lecture `/subject/plan-imagine.exemple.json` a été redirigé en mémoire vers le formulaire du dépôt ; les assertions sont inchangées.

Trois tests livrés n'ont pas été exécutés, car ils créent des répertoires ou liens temporaires : `test_directory_keep_wins_over_main_file_removal`, `test_upload_escape_and_symlink_are_refused`, `test_upload_kept_descendant_blocks_ancestor_deletion`. Cette restriction respecte l'écriture limitée au présent rapport.

Le préalable du banc natif a été tenté par l'adaptateur Docker livré : inspection de l'image via WSL. Résultat : code `4294967295`, `Wsl/Service/E_ACCESSDENIED`. L'intégration classique/HPOS et le lint PHP n'ont donc pas été rejoués ici. Le lanceur complet écrit automatiquement dans `production/A-05/preuves/` ; il n'a pas été lancé tel quel. Aucune preuve existante n'a été remplacée, et aucun contournement des permissions n'a été tenté.

**Compléments exécutés : trois assertions de sûreté en mémoire, trois échecs**, correspondant exactement à P1, P2 et P3. Ils vérifient les décisions du code réel avec des lectures de fichiers fictives ; ils ne constituent pas des essais natifs WordPress ou de suppression sur disque.

**Preuves livrées contrôlées :** le dossier final `production/A-05/preuves/3f1d3e3ce8f2/` rapporte 16 tests unitaires, 93 contrôles d'intégration/isolation et 7 contrôles du lanceur réussis. Les empreintes des 29 sources du manifeste et des 33 fichiers du scellement ont été recalculées : aucune dérive. Ces résultats historiques restent distincts du rejeu indépendant partiel ci-dessus.

La comparaison A-03 livrée rend, dans les deux stockages, `native_exit: 0`, `changes: []`, `anormal: 0`. La documentation explique correctement que cela ne constitue pas un inventaire exhaustif des extensions et de WP-Cron. Les inventaires et empreintes séparés prouvent leur nettoyage. La preuve d'interruption comporte un véritable SIGKILL après un checkpoint ; le cas ambigu de désinstallation est explicitement présenté comme un état construit, pas comme cette preuve d'interruption.

La couverture dépasse le nominal, mais ne couvre pas les trois combinaisons relevées : action `desactiver` dans un dossier partagé, variantes d'en-tête de dépendance et conservation d'un parent de médias face à la suppression d'un descendant. Ajouter ces cas aux tests du lot, puis refaire les preuves sur les sources corrigées.

## 4. Sécurité et données

**P3 — Important — Un dossier de médias conservé ne protège pas ses descendants.**

- **Localisation :** `wp/outils/bascule/a05/clean.py:165`.
- **Problème :** le contrôle protège un descendant marqué `garder` contre la suppression de son parent, mais pas la relation inverse. Le plan `archive: garder`, `archive/2020: supprimer` programme la suppression du sous-dossier. Cela contredit la règle documentée dans `nettoyer.md` : « Une règle `garder` l'emporte sur une suppression recouvrante ». Un opérateur peut donc perdre une partie d'un dossier qu'il a explicitement protégé.
- **Preuve :** `validate()` accepte ce plan ; `operations()` produit une opération `upload` sur `archive/2020`. Le test en mémoire attendant sa conservation échoue.
- **Correction proposée :** prendre en compte les ancêtres gardés dans la détection des recouvrements et appliquer la priorité de conservation annoncée, ou refuser explicitement le conflit avant toute mutation. Tester les deux sens de parenté et les deux ordres des règles.

Aucun secret ou donnée personnelle réelle repéré dans les sources et preuves du lot examinées. Les valeurs de requêtes SQL sont paramétrées et les identifiants de tables sont bornés. Le mode à blanc évite le bootstrap WordPress ; les contrôles de sauvegarde, maintenance et statut sont présents. Le GO de production est spécifique à A-05. Les routines tierces explicitement autorisées restent une limite documentée, et la reprise ambiguë est refusée.

L'outil est une commande locale sans interface HTTP : nonces et échappement HTML ne s'appliquent pas. Aucun changement du paywall n'est livré par ce lot ; son étanchéité n'a pas été requalifiée ici.

## 5. Doctrine

Les opérations natives de désactivation et de désinstallation sont utilisées ; les principales fonctions de garde A-04 sont importées et ses composants PHP sont réutilisés. Les fichiers PHP A-05 portent `strict_types=1` et l'espace de noms `Imagine\Nettoyage`. Le formulaire ne transforme pas le diagnostic en décision de retrait.

Le mode d'emploi donne les références officielles motivant les choix natifs. Ces pages n'ont pas été ouvertes, conformément à l'interdiction d'accès à un site pour cette relecture. Les défauts P1 à P3 concernent les garanties de conservation, pas une demande d'élargissement du périmètre.

### Décisions techniques, défaut proposé

Pour P1 à P3, catégorie **technique** : défaut prudent proposé, refuser tout retrait qui chevauche une ressource dont les fichiers doivent rester, et ne pas autoriser une suppression lorsque les dépendances ne sont pas correctement interprétées. Hermès peut appliquer ces corrections sans arbitrage préalable de Ced ; Claude arbitre après coup. Aucune question métier ou visuelle nouvelle, aucune demande d'autorisation sur le réel.

## 6. Études (lots sans code)

Sans objet : lot de code et de tests.

## Verdict

**À corriger.**

- **Bloquant — P1 :** suppression des fichiers d'une extension seulement destinée à être désactivée.
- **Bloquant — P2 :** retrait autorisé d'une dépendance déclarée mais mal interprétée.
- **Important — P3 :** suppression d'un descendant d'un dossier explicitement conservé, malgré la priorité de conservation documentée.
- **Mineur :** aucun point distinct retenu.

Le rejeu natif indépendant demeure non effectué à cause du refus d'accès WSL ; les preuves historiques vérifiées ne le remplacent pas. Ce verdict n'est jamais un GO.
