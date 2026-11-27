# Relecture indépendante Codex — C-27

## 1. Conformité

Lecture de `relecteurs/AGENTS.md`, de la doctrine, du brief, des §2.2, §3.7 et §4.2 du cahier des charges, des décisions, du code et des preuves C-27. Le rapport Claude n’a pas été consulté. Aucun site, compte ou service externe n’a été interrogé.

Le périmètre principal est livré : question facultative après paiement daté, choix fermés réglables et journalisés dans C-10, exclusion C-16, réponse par commande, source initiale du compte, nombres sans identité et callbacks de confidentialité. Les restrictions aux titulaires connectés, la proposition unique et les périodes UTC sont explicites. README, A-VOIR et PRET sont présents ; les limites visuelles sont déclarées.

## 2. Exactitude métier

Cas déroulés à la lecture du code, sans les présenter comme des exécutions PHP :

- **§3.7, avant/après paiement** : propriétaire connecté, commande impayée ou sans date de paiement → refus avant écriture. Commande payée et datée, bonne clé et liste non vide → proposition ; réponse valide → déclaration datée. Le deuxième envoi est refusé. Une commande `imagine-c16` reste exclue même payée.
- **§4.2, source initiale** : deux commandes payées du même compte, réponses « lune », puis « mars » → deux déclarations, source du compte conservée à « lune » en fonctionnement normal. Pour novembre, les déclarations aux instants `2026-11-01T00:00:00Z` et `2026-11-30T23:59:59Z` sont incluses, celle du 1er décembre est exclue.

**I1 — Important — `wp/plugins/imagine-site/Acquisition.php:123` : une lecture défaillante peut faire écraser une source existante.** Après invalidation du cache utilisateur, `get_user_meta(..., true) === ''` est traité comme une preuve d’absence, sans vérifier l’erreur SQL. Si le chargement des métadonnées échoue ponctuellement, WordPress peut retourner la valeur vide et mettre en cache un ensemble vide. L’`update_user_meta` suivant peut alors réussir et remplacer la source déjà présente ; la relecture du nouveau contenu valide cette réécriture. Cela contredit « seulement si le compte n’en a pas déjà une ». **Correction proposée :** sous le verrou, distinguer explicitement absence et échec de lecture avant toute initialisation ; annuler la transaction en cas d’échec. Ajouter un test où seule la première lecture des métadonnées échoue, puis les écritures fonctionnent : source antérieure intacte, nouvelle déclaration non validée.

## 3. Tests

- **Exécuté avec succès** : `C:/Users/Ced/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -B production/C-27/verifier.py` → **C27 PASS, 487 contrôles**. Les empreintes et les totaux archivés sont cohérents.
- **Rejeu PHPUnit tenté** : commande Docker hors réseau de `c27.py`, appelée directement avec le dépôt monté en lecture seule pour éviter la création de nouveaux reçus. Échec avant lancement de PHP : **`Wsl/Service/E_ACCESSDENIED`**. Aucun résultat PHPUnit indépendant n’est donc revendiqué.
- Les preuves vérifiées annoncent **7 tests / 55 assertions**, **47 contrôles natifs/HTTP**, **8 mutants de source** et **2 témoins natifs** ; le rejeu global archivé annonce **1 166 tests / 36 318 assertions**. Ce sont les résultats de livraison, pas des tests rejoués ici.
- Les contre-exemples Python créent des copies temporaires ; les lanceurs de mutations écrivent des reçus ; les recettes natives accèdent au site. Ils n’ont pas été lancés afin de respecter le périmètre d’écriture et d’accès de cette relecture.

Les tests couvrent notamment paiement, tiers, C-16, doublon, liste vide, bornes de période et confidentialité nominale. Le bouchon de métadonnées ne simule ni erreur de lecture ni cache ; les cas I1 et I2 restent donc hors couverture. La recette teste le redépôt après effacement d’une réponse, mais pas après effacement d’une simple proposition (M1).

## 4. Sécurité et données

Les contrôles de titulaire et nonce, les sorties échappées, les requêtes préparées et les droits C-19 sont présents. Aucun secret ni donnée réelle identifié dans les fichiers examinés. Aucun envoi Odoo/newsletter dans le chemin C-27 ; aucune modification du paywall.

**I2 — Important — `wp/plugins/imagine-site/AcquisitionConfidentialite.php:161` : l’effacement peut annoncer un succès en conservant la source du compte.** `compte()` est appelé avant la prise du verrou et peut charger les métadonnées utilisateur. Scénario concurrent : l’effacement charge un compte sans source ; une réponse prend le verrou, enregistre déclaration et source, puis le libère ; l’effacement prend ensuite le verrou. Ses lectures SQL voient et effacent la déclaration, mais son cache utilisateur local reste vide : les deux `get_user_meta` sautent la suppression et valident l’absence. Les registres étant vides, `done=true` et `items_retained=false` sont renvoyés alors que la source personnelle reste en base. Contrairement à `repondre()`, l’effaceur n’invalide pas ce cache après acquisition du verrou. **Correction proposée :** invalider puis relire les métadonnées sous le verrou, distinguer erreur et absence, et vérifier effectivement la suppression avant validation. Tester cet entrelacement avec deux requêtes et un cache préchargé.

**M1 — Mineur — `wp/plugins/imagine-site/Acquisition.php:111` : la protection annoncée contre le redépôt ne couvre pas les propositions effacées sans réponse.** Une confirmation affichée puis ignorée crée uniquement `VUE`. Son effacement conserve un marqueur `etat=effacee` dans cette option, mais `repondre()` ne consulte que `REPONSE`. Un ancien formulaire dont le nonce reste valide peut donc créer une réponse et une source après cet effacement. La promesse du README selon laquelle le marqueur interdit un redépôt est trop générale. **Correction proposée :** refuser aussi une proposition marquée effacée, sous le même verrou, et tester le POST de l’ancien formulaire après effacement d’une proposition sans réponse.

## 5. Doctrine

La justification « standard d’abord » tient en cinq lignes et renvoie aux documentations officielles. Les règles de liste, d’éligibilité et de comptage sont isolées en PHP pur. Les nouvelles classes suivent les conventions de namespace, préfixes, typage strict et traduction. Aucun code tiers ni style ajouté dans le périmètre examiné. Les références externes n’ont pas été rouvertes, conformément à l’interdiction d’accéder à un site.

Les corrections proposées sont techniques et n’appellent pas d’arbitrage de Ced. Défaut prudent : aucune écriture sur une source dont la lecture est incertaine ; aucun effacement déclaré terminé sans vérification sous verrou.

## 6. Études (lots sans code)

Sans objet : lot de code. Les sources officielles du choix standard sont consignées dans la livraison.

## Verdict

**À corriger.**

- **Bloquant :** aucun identifié.
- **Important :** I1, préservation de la première source en cas d’erreur de lecture ; I2, effacement incomplet en concurrence malgré un succès annoncé.
- **Mineur :** M1, redépôt possible après effacement d’une proposition sans réponse.

Les constats sont issus de la lecture du code ; leur reproduction PHP reste à effectuer, le lanceur local étant inaccessible dans cette session. Ce verdict n’est ni un GO ni une validation visuelle.
