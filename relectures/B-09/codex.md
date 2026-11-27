# Relecture indépendante Codex — B-09

27 novembre 2026. Références : `relecteurs/AGENTS.md`, doctrine, grille, brief B-09, cahier des charges §3.14 et §4.4, décisions du projet. Lecture de la production et des sources, sans accès au site ni à une base. Le rapport de l’autre relecteur n’a pas été lu.

## 1. Conformité

Le périmètre nominal est couvert : cinq pages natives, quatre rubriques FAQ éditables par blocs, pages légales vides, désignation native de confidentialité, formulaire privé et menu de pied de page distinct du principal. L’absence de bandeau, d’envoi et de recherche de compte est respectée dans le code examiné. La note documente les cinq métadonnées à vider lors d’un futur import. Le consentement facultatif est une interprétation explicitée, cohérente avec B-08.

- **R1 — important — `wp/outils/demo/b09-seed.php:118` : reprise incomplète si l’interruption précède l’enregistrement de l’ID dans l’option.** Le callback écrit d’abord le marqueur de l’item, puis son ID dans `imagine_b09_menu`. Un arrêt entre ces écritures, ou un échec de la seconde, laisse un item marqué mais non rattaché au menu et absent de l’option. Au rejeu, le script cherche seulement les items rattachés et les IDs de cette option : il ne retrouve pas cet orphelin et crée un autre item. La coupure livrée, à la priorité 99, intervient après les deux écritures et ne couvre pas ce cas. **Correction proposée :** récupérer aussi les items par leur marqueur durable, vérifier leur propriété et leur absence de rattachement étranger, puis réutiliser l’ID ; refuser les ambiguïtés. Ajouter une coupure entre marqueur et option et vérifier l’absence d’orphelin après reprise.

## 2. Exactitude métier

Cas déroulés à la lecture du code, sans les présenter comme de nouvelles exécutions PHP :

1. **Contact sans compte, consentement absent, texte `C:\\dossier` :** nonce contrôlé, POST déséchappé une fois, consentement `0`, stockage privé avec métadonnées rééchappées à l’écriture, accusé indépendant de l’existence d’un compte. Le détail administratif et l’export relisent le texte. Le parcours correspond au brief.
2. **101 contacts d’une adresse et un contact tiers :** export en tranches 50/50/1 ; effacement reprenant toujours les 50 premiers éléments restants, donc sans saut lié au rétrécissement de la collection. Le tiers reste exclu. Le parcours nominal correspond au §4.4 et au brief.
3. **Interruption au troisième item après mémorisation de son ID :** la reprise retrouve l’item non rattaché et le complète. La preuve couvre correctement cette coupure précise ; R1 porte sur la coupure précédente, non couverte.

## 3. Tests

- **Exécuté :** `python -B production/B-09/verifier.py` — code de sortie 0, **463 contrôles réussis**. Ce programme vérifie le paquet et ses preuves archivées ; il ne réexécute pas WordPress.
- **Tenté :** commande Docker isolée de `b09-local.py`, appelée directement avec `b09-horslive.php` pour éviter l’écriture d’un journal dans `production/`. Échec avant PHPUnit : **`Wsl/Service/E_ACCESSDENIED`**. Aucun PHP ni Docker natif trouvé dans le PATH ; les six tests et les mutations PHP n’ont donc pas été réexécutés ici.
- **Preuves archivées vérifiées :** 6 tests / 188 assertions, 53 contrôles natifs, 12 mutations de sources et une mutation REST/recherche. Les quatre échecs de paquets A-26/A-27/A-30/A-31 sont explicitement exposés ; aucun succès global du dépôt n’est déduit.
- Les recettes sur la démonstration et la reconstruction d’image n’ont pas été lancées : les consignes du relecteur interdisent l’accès au site et limitent l’exécution aux tests locaux. Les scripts qui écrivent d’autres fichiers n’ont pas été lancés tels quels.

Les tests couvrent utilement les antislashs, la pagination, les tiers, les capacités, les nonces et des échecs de stockage. Ils ne couvrent ni la fenêtre R1, ni une suppression partielle des métadonnées : le double `wp_delete_post` retire post et métadonnées ensemble.

## 4. Sécurité et données

- **R2 — important — `wp/plugins/imagine-site/ContactConfidentialite.php:48` : l’effacement peut annoncer sa réussite sans vérifier la disparition des données du message.** Le succès repose sur le retour de `wp_delete_post` et l’absence du post. Si le post disparaît mais qu’une suppression de métadonnée échoue, les données restantes ne sont pas contrôlées. La relecture finale par `Contact::ids()` utilise une jointure avec les posts : elle ne peut plus retrouver ces métadonnées orphelines et permet `done=true`. La recette vérifie les postmeta après une suppression nominale, mais le callback ne garantit pas ce résultat en cas de suppression partielle. **Correction proposée :** vérifier explicitement l’absence des métadonnées pour chaque ID traité et conserver un moyen de reprendre leur nettoyage tant que cette vérification échoue ; ne terminer qu’après disparition vérifiée du post et de ses données. Ajouter un test de suppression partielle où le post disparaît et une méta personnelle subsiste.

Pour le parcours normal : capacités réservées à `manage_options`, nonce, échappement des sorties, requête préparée, type non public et non exposé en REST/recherche. Aucun secret ni contact réel relevé dans les fichiers B-09 examinés. Aucun transport ajouté dans le traitement. Les pages publiques restent hors de la matrice C-23, conformément au brief.

## 5. Doctrine

Le choix des pages, blocs, menu et registres de confidentialité natifs est justifié en cinq lignes et accompagné de références officielles archivées. La validation pure existante est réutilisée ; aucune extension tierce n’est modifiée.

- **R3 — mineur — `wp/plugins/imagine-site/Contact.php:26` : mise en forme non conforme à PSR-12.** Le cast `(string)get_post_meta(...)` n’est pas suivi de l’espace exigé ; la même forme apparaît ailleurs dans les nouveaux adaptateurs. **Correction proposée :** appliquer les conventions PSR-12 aux nouveaux fichiers, sans changement fonctionnel.

## 6. Études (lots sans code)

Sans objet : lot avec code. Les références documentaires présentes ont été lues dans le dépôt ; aucune consultation externe effectuée.

## Verdict

**À corriger.**

- **Bloquant :** aucun relevé.
- **Important :** R1, reprise laissant un item orphelin ; R2, réussite d’effacement insuffisamment vérifiée.
- **Mineur :** R3, conformité PSR-12.

Les corrections proposées sont techniques et ne nécessitent pas d’arbitrage métier ou visuel. Le rejeu indépendant de PHPUnit reste à réaliser dans un environnement où WSL est accessible. Ce verdict n’est pas un GO.
