# Relecture indépendante — Lot A-30 (import à blanc des abonnés hors ligne)

Relecteur : Claude. Date : 27 novembre 2026.
Périmètre lu : `briefs/A-30-...md`, `docs/cahier-des-charges-v3.1.txt` (§4.3, §3.7, §3.13, §2.3), `wp/outils/bascule/a30/`, `wp/tests/a30/`, `production/A-30/`.
`relectures/A-30/codex.md` **non ouvert** (consigne). Pas de fusion à ce stade.

## Vérification exécutée

Commande autorisée, sans argument, conteneur jetable, sans réseau, dépôt en lecture seule :

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Dernière ligne rapportée :

`REJEU : 1157 tests, 36234 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`

Lignes complémentaires de la même exécution :
`PAQUETS : 9 vérifiés, 0 échecs ; hors rejeu : A-20 (declaration absente), A-31 (journaux absents)` (A-30 est parmi les 9 vérifiés, via son lecteur `verify.py` sans argument).
`OUTILS : 22 outils, 584 contrôles, 0 échecs ; hors rejeu : aucun`.

Note de vérification (hors A-30) : le compte figé dans `rejeu.json`/`parent-gates.json` est 1153 tests / 36075 assertions ; mon rejeu neuf donne 1157 / 36234. L'écart vient de modifications **non committées d'autres lots** présentes dans l'arbre de travail (`wp/tests/a31/test_verify.py` modifié, `wp/tests/demo/b09-*.php` ajoutés) et non du lot A-30, dont le paquet reste cohérent avec son sceau (sinon `PACKAGE_DRIFT`). À reporter à la clôture : repartir d'un arbre propre.

## 1. Conformité

- **Standard d'abord** présent, cinq lignes, `a30/README.md:5-13` : distingue l'import CSV produit de WooCommerce, l'ajout manuel Subscriptions (écriture, pas simulation), le CSV Importer bêta, et justifie le sur-mesure en lecture seule. Conforme au brief (« Dis en cinq lignes… »).
- **Issues, liste fermée** : `core.ISSUES` et `Analysis::analyse` (`Analysis.php:18-36`) produisent exactement `compte_a_creer`, `compte_existant`, `sans_email`, `type_a_decider`, `refuse_a13`, plus l'état `null` réservé à la copie neutralisée. Renvoi aux paragraphes : §4.3 (abonnés hors ligne / sans email), §3.7 (un seul compte par adresse), §3.13 (encodage sans email). Conforme.
- **Type hors table → à décider, jamais deviné** : `core.prepare` (`core.py:188`) fait `config['types'].get(...)` → `None` → `type_a_decider` ; aucun rapprochement par titre/prix (`README:31`). Conforme.
- **Fichier refusé par A-13 refusé à l'identique** : `core.prepare` appelle directement `lire_config`, `decoder`, `lire_csv`, `analyser` d'A-13 (`core.py:173-179`) et jamais `controler`/`ecrire`/`main` (`core.py:1`). Un `Refus` remonte en code 2 avec le message A-13 exact (`confine.py:100-102`). Conforme au brief (« par le même code, sans le rejouer autrement »).
- **Sorties** : nombres par issue/produit/mode de paiement avec fusion des groupes < 5 (`core.grouped`, `core.py:51-54`) ; liste des numéros de ligne par issue écrite **à côté du CSV**, hors dépôt (`core.publish` + `core.safe_source` refusant tout dépôt et le répertoire du site, `core.py:133-168`). Aucune cellule recopiée (`public_reports` reconstruit des documents neufs, `core.py:57-75`). Conforme.
- **Copie neutralisée** : `accounts` et les deux listes de rapprochement passent à « inconnu après neutralisation », jamais zéro (`core.py:66-74`), documenté (`README:47-49`, `README-AJOUT-2-LIGNES.txt` ligne 2). Conforme.
- **Aucune règle métier nouvelle** : trois options (`importer_echus`, `resoudre_doublons`, `calculer_prochaine_echeance`) forcées à `false` ; toute mise à `true` refuse `A30_OPTION_UNSUPPORTED` (`core.py:42-43`). Signalé dans le rapport (`RECEPTION-PARENT.md:30`). Conforme au brief (« ce qui demanderait une règle est une option désactivée par défaut, et tu le signales »).
- **Livrables** : outil, tests, `types.exemple.json` (fictif, IDs 910001/910002), deux lignes intégrées au **vrai** mode d'emploi `wp/tests/a02-audit/README.md:104`, `production/A-30/PRET`. Conforme.
- Interprétation signalée, pas masquée : le produit d'une ligne rejetée peut rester connu sans la rendre importable (`README:58`). Correctement explicité.

## 2. Exactitude métier (déroulé à la main)

- **Cas §3.13 — abonné sans adresse** : ligne admissible A-13, colonne email vide. `prepare` → `email=''` ; `Analysis::analyse` : non rejetée, `email===''` → `sans_email` (`Analysis.php:22-23`). `Inventory::collect` ignore ces lignes au rapprochement (`Inventory.php:47`). **Aucune adresse technique inventée ici** : la génération du §3.13 est laissée à l'import réel, conformément au brief. Résultat du code = attendu. ✔
- **Cas §3.7 — un seul compte par adresse** : `Inventory` fait `SELECT ID ... WHERE user_email=%s LIMIT 2` (`Inventory.php:50-52`). 0 → `compte_a_creer` ; 1 → `compte_existant` ; ≥ 2 → `A30_EXISTING_EMAIL_AMBIGUOUS`, l'outil ne choisit ni ne fusionne (`Analysis.php:32-35`). Vérifié aussi par `unit.php:28-33`. Résultat = attendu. ✔
- **Cas type hors table** : type `type-secret-inconnu` → produit `None` → `type_a_decider`, et non deviné (`test_core.py:147-154`). ✔
- **Cas fichier IBAN** : refusé par A-13 au même code 2, même message fermé, aucun fichier produit (`test_core.py:105-123`, `test_cli.py:31-38`). ✔
- **Cas limites couverts** : lignes physiques avec cellule multi-ligne entre guillemets (numérotation physique conservée, `test_core.py:147-154`) ; cp1252 explicite et BOM UTF-16 via le décodeur A-13 exact (`test_core.py:135-145`) ; fichier sale → code 1 et lignes rejetées exactes (`test_core.py:162-169`). Priorité des issues (rejet > sans email > type > compte) vérifiée (`unit.php:34-35`).

Les cinq issues tombent sur les bonnes lignes du jeu étendu : créer 2–6, existant 7–11, sans email 12–16, à décider 17–21, refus A-13 22–26 (`cases.py:21-23`, confirmé en natif classique et HPOS par `inside.py:110`).

## 3. Tests

- Suite rejouée par la commande autorisée : **PASS** (voir ci-dessus). Paquet natif A-30 (classique + HPOS, UTF-8 + cp1252) vérifié par `production/A-30/verify.py` sans argument, lui-même exécuté par T03 lors du rejeu.
- Couverture des cas limites réelle, pas seulement le nominal : empreintes base et fichiers identiques avant/après, dix canaux fermés (stdout/stderr/affichage/shutdown/dépassement/UTF-8 invalide/JSON encore valide mais modifié/clé ou fichier en trop/suppression), neutralisation réelle par le moteur gelé, rejeu idempotent, refus de sortie existante, commande du mode d'emploi jouée telle quelle (`inside.py`, `verify.py:78-105`).
- Les tests vérifient la règle, pas le code : `unit.php` déroule la table de priorité sur des lignes construites ; `test_boundary.py` prouve que le digest lie le contenu exact (une mutation de schéma valide au shutdown est refusée, `test_boundary.py:71-82`) ; `test_verify.py` prouve qu'un paquet Python seul n'est jamais vert (`native_proven=False`).
- Rejouable sous Windows cp1252 : `matrix.py` sonde les encodages réels et exige ≥ 17 tests PASS dans chaque contexte.

## 4. Sécurité et données

- **Aucun secret, aucune donnée réelle** : fixtures A-13 fictives, adresses `@example.org`, IDs produits inventés. Les identités ne transitent que par stdin/mémoire ; aucun nom, adresse, mandat, mot de passe ou identifiant de compte n'est sélectionné ou exporté (`Inventory.php:43-44`).
- **Lecture seule stricte** : CSV inchangé (tests `input_immutable`), sorties créées en exclusif (`open('x')`, mode 0600) et jamais écrasées (`A30_OUTPUT_EXISTS`), refus des liens symboliques et de tout chemin de dépôt ou du site (`safe_source`, `core.py:133-148`).
- **Confinement** : chemin PHP exigé sous Linux déconnecté, sinon `A30_CONFINEMENT_REQUIRED` ; `disable_functions` mail/exec/…, affichage absorbé, flux directs/tardifs refusés, digest du résultat lié avant shutdown et revérifié après EOF (`confine.py:54-88`, `observer.php`). SQL en lecture seule ; toute erreur SQL → `A30_QUERY_FAILED`. Requête préparée (`$wpdb->prepare`).
- **Pas de sortie de texte réservé** : seuls des nombres K5 et des numéros de ligne sortent ; le banc assert qu'aucun canari/`@`/chemin/libellé ne figure dans les sorties (`inside.py:115-116`).
- **Aucun accès au réel** : Windows refuse volontairement le chemin PHP ; aucun chemin de site/compte/archive accepté. Conforme au §3 de la doctrine.

## 5. Doctrine

- **Standard d'abord** respecté : l'outil réemploie le parseur A-13 et les lecteurs natifs WordPress/Woo, n'appelle jamais les importeurs ni les créations (`README:11`). 
- **Logique hors WordPress** : `Analysis.php` est une projection pure (ni WP, ni SQL, ni dates) testée sans base (`unit.php` en mode `A30_PURE`, 0 écriture, 0 extension). Conforme au §4 de la doctrine.
- **Conventions §5** : `declare(strict_types=1)`, espace `Imagine\`, PSR-12 strict (0 erreur / 0 avertissement, banc A-20 réemployé). Option globale lue avec préfixe `imagine_`. Codes machine en ASCII, seuls messages utilisateur = refus A-13 en français.
- **Une règle ouverte devient un réglage** : les trois décisions métier (échus, doublons, prochaine échéance) sont isolées derrière des options par défaut fermées et signalées. Conforme.

## 6. Études

Sans objet (lot avec code). Réserve documentaire : voir point mineur M1.

## Points relevés

**Bloquant** : aucun.

**Important** : aucun.

**Mineur**
- **M1 — citations « standard d'abord » non vérifiables ici.** `a30/README.md:13` affirme avoir consulté deux URL WooCommerce le 27/11/2026 et que deux anciennes URL ont répondu 404. En conteneur sans réseau je ne peux pas vérifier ces sources (grille §6 : « sans source : doute »). Proposition : conserver hors dépôt une capture datée des pages citées, pour la clôture.
- **M2 — détection de neutralisation reposant sur un seul marqueur.** `Inventory.php:24-31` déduit l'état « neutralisé » de la seule présence de l'option `imagine_staging_disabled_plugins`. La sûreté « jamais zéro sur copie neutralisée » dépend donc entièrement de ce marqueur posé par le moteur de staging gelé (testé par `neutralise.php`). Si le contrat de neutralisation du staging évolue, A-30 pourrait rapprocher des adresses anonymisées sans le signaler. Proposition : documenter explicitement, dans `Inventory.php` ou le README, que ce marqueur est le signal canonique de neutralisation et qu'un changement du moteur impose de mettre A-30 à jour. Risque faible aujourd'hui (staging vérifié obligatoire avant accès, §3).

## Décisions techniques, défaut proposé

- **Axe produit et libellé `0`.** Les lignes sans produit natif reconnu sont comptées sous la clé produit `0` (`core.py:72`), y compris des lignes `sans_email` ou `refuse_a13` qui ont pu garder un type connu. C'est cohérent avec le brief (« les axes comptent les lignes du fichier contrôlé, rejets compris ») et documenté (`README:55-58`). **Défaut proposé** : conserver tel quel ; Claude arbitre après coup si Ced veut au contraire un axe produit restreint aux seules lignes importables.

## Pour Imagine (métier)

- Aucune question métier nouvelle à trancher dans ce lot : les trois règles ouvertes (import des échus, résolution des doublons, calcul de la prochaine échéance) restent volontairement chez Imagine et deviennent des réglages désactivés par défaut. **Défaut prudent déjà en place** : les trois options sont `false` et `true` est refusé. Rien ne bloque la clôture du lot.

## Verdict

**Conforme.** Le lot fait ce que le brief demande, ni moins ni plus : simulation en lecture seule, cinq issues fermées, réduction K5, numéros de ligne hors dépôt, copie neutralisée traitée en « inconnu », aucune règle métier nouvelle, trois options fermées. Tests au vert par la commande autorisée. Deux points mineurs (M1 documentaire, M2 robustesse) et une décision technique à arbitrer après coup ; aucun n'est bloquant.

Rappel de doctrine : ce verdict, même « Conforme », **n'est pas un GO**. Il ne vaut que pour la relecture de code ; la clôture passe par la fusion avec Codex puis la vérification du second tour.

## Suite

`relectures/A-30/codex.md` existe mais n'a pas été ouvert (consigne). **Je m'arrête après la relecture et ne fais pas la fusion.** Prochaine étape, sur instruction : lire `codex.md`, puis écrire `corrections/A-30.md` au format de fusion.
