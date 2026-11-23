# Relecture indépendante Codex — T-01

Date : 23 novembre 2026. Périmètre : `briefs/T-01-commande-de-rejeu.md`, `production/T-01/` et outillage correspondant dans `wp/`. Consignes de `relecteurs/AGENTS.md`, doctrine et grille appliquées. Rapport Claude non consulté. Aucun fichier de production modifié.

## 1. Conformité

Les deux scripts, les preuves complètes, les notes en cinq lignes et `PRET` sont présents. La préparation et le rejeu sont séparés. Le rejeu découvre les deux bibliothèques Composer, contrôle les empreintes des manifestes, copie sources et dépendances dans le stockage temporaire du conteneur et lance leurs configurations PHPUnit racines. Aucun banc commercial ni constructeur de staging n'est appelé. L'exclusion d'`imagine-site` correspond à son absence de suite de bibliothèque : sa recette nécessite WordPress et relève du staging, exclu par le brief.

Le brief ne cite aucun paragraphe du cahier des charges et n'ajoute aucune règle métier. Les exemples du §3.5 ont néanmoins été contrôlés en lecture, conformément à la grille.

**T01-C1 — Important — `wp/tests/rejouer.ps1:25` : conteneur persistant si le processus de rejeu est interrompu brutalement.** La création n'active pas la suppression automatique par Docker ; la suppression repose exclusivement sur le `finally` du processus PowerShell. Si ce processus est tué pendant `docker start -a` (arrêt de l'agent, fermeture forcée ou expiration d'un délai externe), ce `finally` ne s'exécute pas. Même si la commande interne se termine normalement ou grâce à `timeout 600`, le conteneur arrêté reste présent. La promesse du brief « ne laisse aucun conteneur derrière lui » n'est donc pas assurée dans ce cas. **Correction proposée :** confier aussi la suppression après arrêt au démon Docker, adapter la collecte du résultat et les inspections à cette suppression, et conserver un nettoyage de secours des objets créés mais non démarrés. Ajouter un test d'interruption du processus parent vérifiant l'absence finale du conteneur. Constat statique ; interruption réelle non testée dans cet environnement.

## 2. Exactitude métier

T-01 n'altère pas les calculs métier. Deux déroulés manuels du §3.5 ont été comparés au moteur et aux tests inclus dans le rejeu :

- **Commande le 8 octobre 2026 :** dans le calendrier fictif, la liste du n°170 est clôturée depuis le 20 septembre. Le filtrage des réguliers encore ouverts puis la sélection des quatre premiers donnent 171, 172, 173 et 174 ; le prochain hors-série non clôturé est celui de 2027. Résultat conforme à l'exemple du cahier des charges et à `wp/plugins/imagine-pilotage/tests/Numeros/MoteurTest.php:202`.
- **Renouvellement en octobre 2027 :** le dernier numéro précédent est 174 ; les quatre réguliers suivants sont 175 à 178. Le hors-série 2027 étant clôturé, le suivant est celui de 2028. Résultat conforme au second exemple et à `wp/plugins/imagine-pilotage/tests/Numeros/MoteurTest.php:178`.

Le mécanisme correspondant se trouve dans `wp/plugins/imagine-pilotage/src/Numeros/Moteur.php:80` pour les réguliers et à la ligne 117 pour le hors-série. Les deux tests figurent dans le JUnit livré. Les cas de clôture exacte, de changement d'année et de calendrier incomplet sont aussi présents dans cette classe ; le rejeu d'événements est couvert notamment par `wp/plugins/imagine-connecteur/tests/WorkerTest.php:64`. Cela constate leur présence, sans prétendre les avoir exécutés ici.

## 3. Tests

**Rejeu réel tenté**, depuis la racine, avec :

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\wp\tests\rejouer.ps1
```

Résultat : code **1**, avant tout lancement PHP. WSL refuse l'accès avec `Wsl/Service/E_ACCESSDENIED`. Le script annonce Docker indisponible et termine bien par :

```text
REJEU : 0 tests, 0 assertions, 0 échecs, 1 erreurs, 0 ignorés — FAIL
```

Il s'agit d'une limite de l'environnement de relecture, pas de la preuve d'un échec des bibliothèques. Aucune préparation d'image, installation ou tentative de contournement n'a été effectuée.

**Dix scénarios simulés rejoués** directement via `wp/tests/t01/mock-wsl.ps1`, sans les branches de préparation qui écrivent des fichiers temporaires : Docker absent, image absente, succès, échec PHPUnit, bilan mal formé, erreur de démarrage, erreur après création, erreur de nettoyage, image non conforme et montage non conforme. Les dix codes de sortie et résumés sont conformes aux attentes ; la confirmation de nettoyage apparaît dans les six scénarios où elle est attendue par le test livré. Le scénario de succès retourne 0 et les neuf autres retournent 1. Ces doubles ne constituent pas une exécution PHP.

`verifier-t01.py` n'a pas été lancé : sa ligne 30 réécrit les journaux de production et sa ligne 62 réécrit le reçu, contrairement à la restriction d'écriture de cette relecture. Les trois scénarios de préparation n'ont pas été relancés pour la même restriction ; le test réel d'isolation ne peut pas être rejoué tant que WSL refuse l'accès.

**Preuves livrées contrôlées indépendamment en lecture :** les 134 empreintes de sources du reçu correspondent aux fichiers présents. Les empreintes des trois journaux `final-contrat.log`, `final-isolation.log` et `final-rejeu.log` correspondent également au reçu. Le JUnit livré contient 37 tests / 224 assertions pour le connecteur et 765 tests / 33 143 assertions pour le pilotage, soit **802 tests / 33 367 assertions**, sans échec, erreur ou test ignoré. Ses fichiers de cas de test couvrent les 5 + 26 fichiers `*Test.php` actuellement présents. La preuve de préparation et celle de rejeu désignent la même image. Ces vérifications établissent la cohérence des pièces livrées, sans remplacer un rejeu PHP indépendant.

**T01-C2 — Important — `wp/tests/t01/executer.php:47` : le contrôle d'exhaustivité ignore les exclusions PHPUnit.** `verifyCoverage()` inventorie tous les `*Test.php` des éléments `directory`, mais ne tient pas compte des éléments `exclude` ni ne les refuse. Par exemple, ajouter `<exclude>tests/Acces</exclude>` dans la suite Acces conserve la même liste calculée par ce contrôle, alors que PHPUnit exclut ces tests. Les autres suites peuvent réussir et le bilan final rester PASS, sans exécuter toute la suite demandée. Les configurations actuelles ne comportent pas cette exclusion : le défaut concerne le garde-fou du rejeu lors d'une évolution de configuration. **Correction proposée :** refuser explicitement les filtres/exclusions non pris en charge, ou vérifier la sélection effective de PHPUnit contre l'inventaire attendu ; ajouter un test négatif avec une exclusion et exiger FAIL. Constat par lecture du chemin de sélection ; aucune configuration du dépôt n'a été modifiée pour le reproduire.

Les tests fournis vérifient utilement plusieurs erreurs et le nettoyage après exception, mais ne couvrent ni l'interruption du parent de T01-C1, ni la sélection partielle de T01-C2.

## 4. Sécurité et données

Le rejeu impose `--pull never`, `--network none`, un montage du dépôt en lecture seule, une racine de conteneur en lecture seule, un utilisateur non privilégié, la suppression des capacités, `no-new-privileges` et des limites de ressources. L'image est utilisée par identifiant après inspection ; les montages et le réseau sont contrôlés avant et après exécution. La suppression vérifie une étiquette de propriété propre à l'exécution. Les sorties temporaires et JUnit restent dans le conteneur.

La préparation limite son contexte au Dockerfile, au vérificateur et aux manifestes Composer ; l'installation désactive scripts et plugins Composer. Aucun secret ou donnée réelle identifié dans les fichiers propres au lot examinés. Aucun accès à un site, une base ou un compte effectué. Nonces, requêtes SQL et étanchéité du paywall ne relèvent pas du code ajouté ici. Le défaut de nettoyage est traité en T01-C1.

## 5. Doctrine

L'outillage réutilise Docker, Composer et PHPUnit ; il ne réimplémente pas une fonction métier d'une extension retenue. PHP 8.2 et `strict_types` sont présents. La logique métier reste dans les bibliothèques et la préparation réseau reste distincte de la commande autorisable aux relecteurs. Aucun changement Git, staging ou déploiement effectué pendant cette relecture.

La réserve d'exécution indépendante est explicitement conservée malgré les preuves PASS livrées.

## 6. Études (lots sans code)

Sans objet : lot d'outillage avec code. Aucune affirmation comparative sur une extension à sourcer.

## Verdict

**À corriger.**

- **Bloquant :** aucun défaut classé à ce niveau.
- **Important : T01-C1** — assurer le nettoyage après interruption du processus parent.
- **Important : T01-C2** — empêcher qu'une exclusion PHPUnit contourne le contrôle d'exhaustivité.
- **Mineur :** aucun point supplémentaire retenu.

Limite de validation : le rejeu PHP indépendant reste non réalisé à cause du refus d'accès WSL ; les preuves livrées sont cohérentes et les dix scénarios simulés du rejeu ont été contrôlés localement. Ce verdict n'est pas un GO.
