# Relecture C-26 — Le test d'étanchéité suit les sorties nouvelles

Relecteur Claude indépendant. Lot de **test uniquement** : il ne touche ni au paywall, ni au thème, ni à un plugin. Cible unique `imagine-test-demo`, fictive. Rapport écrit sans ouvrir `codex.md` ; fusion non faite.

## Rejeu de la suite autorisée

Commande rejouée depuis la racine, sans argument (conteneur jetable, réseau `none`, dépôt monté en lecture seule) :

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Dernière ligne :

`REJEU : 1151 tests, 36062 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`

Ligne outils : `OUTILS : 20 outils, 521 contrôles, 0 échecs ; hors rejeu : aucun`. Isolation vérifiée (`network=none ; rootfs=ro ; mount=…/wp:ro ; cap-drop=ALL ; no-new-privileges`), conteneur nettoyé.

**Portée de cette preuve** : `rejouer.ps1` rejoue la suite PHP (PHPUnit des quatre bibliothèques + tests purs des outils A). Elle prouve la non-régression du PHP du dépôt, mais **n'exécute pas** les tests Python livrés par ce lot (`c26*.py`), qui visent le site de démonstration. Voir §3.

## 1. Conformité

Le brief est tenu, ni moins ni plus.

- **Inventaire une ligne par sortie** : `production/C-26/INVENTAIRE.md` liste 131 sorties nouvelles ou communes, chacune avec voie, chemin GET exact et public visé (T = texte réservé, D = donnée d'un autre compte). Conforme au livrable demandé.
- **Entrée dans la matrice** : `wp/outils/demo/c26.py:146` (`matrix`) rejoue d'abord C23 inchangé (`base_code = c23.matrix(...)`, ligne 153) puis étend le catalogue (`routes`, ligne 15) sur 15 publics (`c23.audience_order(f) + ['abonne-actif']`, ligne 155). 131 × 15 = 1 965 contrôles, cohérent avec le reçu `livraison-finale.json`.
- **Un témoin par famille nouvelle** : `wp/outils/demo/c26-preparer.py:111-147`. Quatre mutations de raccord sur les callbacks d'export natifs (agenda B07, personnalisation C24, rétractation C25, sujet B08), plus deux mutations persistées traversant un vrai GET (Soutenir B08 ligne 136, coopérateurs B06 ligne 120). Chaque reçu `mutation-*` est attendu rouge (`assert receipt['failures'] and receipt['leaks']`, ligne 116 ; `assert verdict['leak'] and not verdict['ok']`, lignes 126, 141).
- **Pages coopérateurs dans le périmètre de relecture** : `production/C-26/A-VOIR.md` nomme précisément fichiers, fonctions et lignes B06 (`c23.py:139-193` routes et contrôle, `c23-inventaire.php:74-91` inventaire des cinq pages, `c23-preparer.py:125-143` pose/retrait du témoin, `c23-tests.py:195-332` recettes). Soumis comme code neuf, non déclaré clos par cette livraison. Conforme.
- **Correctif TMPDIR** : `wp/tests/demo/c23-tests.py:10-17` (`test_scratch`) lit désormais `os.environ.get('TMPDIR') or <repli LOCALAPPDATA/hermes/cache/scratch>`, au lieu d'un accès direct qui échouait sans la variable. Régression dédiée : `wp/tests/demo/c26-tests.py:87` (`test_scratch_sans_tmpdir_hors_systeme`).
- **Réglages lus sans rien forcer** : `wp/tests/demo/c26-verifier.py:87` vérifie que la découverte reste à l'état livré (`c23['discovery']['policy']==f['discovery_policy']` et `exhausted_played is False` quand `ouverture=='fermee'`). Aucune règle métier ni droit d'accès n'est choisi pour les besoins du test ; rien à arbitrer par Ced.

Aucune interprétation silencieuse relevée.

## 2. Exactitude métier

Deux voies déroulées à la main sur la logique du code (le site n'est pas accessible en relecture) :

- **Visiteur anonyme → inscription privée B07 par REST** : route `agenda-prive-rest` `/wp-json/wp/v2/imagine_inscription/30`, `kind='rest-denied'`, statuts attendus `(404,)` (`c26.py:35`). `assess` (c26.py:81-91) exige un JSON d'erreur natif (`code` + `data`) et `denied_markers` (c26.py:137) interdit `C26_AGENDA_FICTIF`. Si l'inscription fuyait, le témoin serait trouvé → `leak=True`, `ok=False`. Comportement correct.
- **Acheteur d'un autre numéro → page réservée** : `denied_markers(f,'acheteur-autre-numero')` (c26.py:137-143) retire du lot des témoins interdits les seuls numéros possédés (`str(p['issue']) not in f['buyer_issues']`), et garde les données privées D. Le test unitaire `test_droit_numero_achete_non_qualifie_fuite` (c26-tests.py:78-85) le confirme : `['C26_PRIVE','CONTENU_FICTIF_RESERVE_T4']` pour l'acheteur du T1. Un texte légitimement lu n'est pas classé fuite. Correct.

Cas limites couverts par les tests : surface vide refusée (c26-tests.py:54), mauvaise page refusée (c26-tests.py:111), recherche vide refusée (c26-tests.py:113), réflexion d'un terme/date dans le lien RSS encodé masquée aux seules positions natives mais commentaire fuyant toujours détecté (c26-tests.py:116-123), inverse propriétaire positif exigé côté privacy (c26-tests.py:63). Le masquage de réflexion (`c26.py:63-72` + `c23.search_results_body`) est étroitement borné aux positions de réflexion (titre/h1 « Recherche », input `s`, lien de flux) : un même marqueur ailleurs dans `<main>` resterait une fuite.

## 3. Tests

- **Suite PHP** : rejouée, **PASS** (ligne REJEU ci-dessus). Non-régression du dépôt confirmée.
- **Suite Python du lot non rejouée en indépendance.** La commande autorisée pour ce tour est `rejouer.ps1` ; l'exécution directe des trois commandes offline du lot (`c26-tests.py`, `c26-verifier.py`, `c26-paquet-tests.py`) a été refusée par le harnais de permissions. En conséquence, la matrice verte (3 951 contrôles, 0 fuite), les six mutations rouges et les 42 tests `TMPDIR` absent / réseau bloqué reposent ici sur **la lecture du code, la logique du vérificateur et les reçus livrés**, pas sur mon propre rejeu. À confirmer au second tour en exécutant ces trois commandes (elles bloquent `socket.connect`, ne touchent ni le site ni `production/`).
- **Qualité des tests lue (non vacuité)** : les tests ne se contentent pas de répéter le code. `c26-verifier.py:22-32` (`matrix_checks`) recompte totaux, cases (produit cartésien exact, une occurrence chacune), fuites et surfaces à partir des lignes, et `re-dérive` le catalogue (`record['routes']==catalog`, ligne 73) au lieu de faire confiance au reçu. `c26-paquet-tests.py` éprouve réellement le vérificateur par neuf falsifications **rescellées** (ligne 44-68) et exige leur rejet (`all_rejected`). Les mutations exigent `witnesses_found>0` sur les lignes rouges (c26-verifier.py:96,99), donc une fuite réellement observée, pas un drapeau fabriqué.

## 4. Sécurité et données

- **Aucun secret, aucune donnée réelle** : cibles et emails fictifs. Vérifié : aucun email non `@example.org` dans les reçus `production/C-26/*.json` ; aucun `wordpress_logged_in_`, `X-WP-Nonce`, `Set-Cookie` ni `PHPSESSID`. Le vérificateur l'impose aussi (`no_session_dump`, c26-verifier.py:103).
- **Transport sûr** : seul GET, chemins validés (`c23.validate_path`, refus `//`, `\`, netloc, caractères de contrôle), redirections bornées à l'hôte de la démo (`c23.py:82-136`). Aucun POST, envoi, export HTTP ou appel extérieur depuis la commande visiteur (`c26-tests.py:125-130` vérifie l'absence d'import `subprocess`/`profils` et de `update_option` dans `c26.py`).
- **Garde-fou de cible** : `c26-fixture.php:10-25` refuse de s'exécuter hors `local` / `imagine-test-demo` / `home_url` de la démo, et exige un propriétaire fictif `@example.org` porteur de `_imagine_c09_fixture`. `pre_wp_mail` et `pre_http_request` doivent être neutralisés, passerelles de paiement vides.
- **Paywall (étanchéité §4.4)** : la matrice couvre les voies citées au cahier des charges (page, REST, flux, oEmbed, recherche interne) plus embed/admin/compte/refus, pour 15 publics tiers dont l'anonyme et le faux-robot. Aucune voie observée ne laisse sortir T ou D dans les reçus. La limite assumée des flux de types privés (repli natif sur les articles publics, A-VOIR « Restauration et limites ») est honnêtement déclarée et ne sert pas de fausse preuve.
- **Restauration** : `c26-preparer.py:155-170` compare 14 collections métier exactement, les options `imagine_*`/`cron`, et des empreintes avant/après ; supprime fixtures et commande `created_via='c26-fixture'`, remet les pages B06 vides. L'assertion finale bloque si la restauration n'est pas prouvée. Lu, non rejoué (voir §3).

## 5. Doctrine

- **Standard d'abord** : les exports de données privées passent par les callbacks d'export natifs enregistrés (`wp_privacy_personal_data_exporters`, `c26-fixture.php:82`), les sorties REST/oEmbed/flux par WordPress natif. Le sur-mesure se limite à l'inspection. Conforme.
- **Logique hors WordPress** : détection et matrice en Python pur, testables sans base (`c26.py`, `c26-tests.py`). Conforme.
- **Conventions §5** : fixture PHP en `declare(strict_types=1)`, espace de noms `Imagine\`, préfixes `imagine_`. Conforme.
- **Aucune modification d'extension tierce ni du code métier** : seul `c23-tests.py` (test) est modifié côté C23, pour le correctif TMPDIR autorisé ; le manifest épingle son empreinte.

## Verdict

**Conforme** — ce verdict n'est pas un GO et ne clôt pas le lot (une seule relecture, fusion non faite, suite Python du lot non rejouée en indépendance).

Points, classés :

- **Important** (traçabilité, pas défaut du code) : la suite Python livrée par ce lot n'a pas été exécutée dans cette relecture (seul `rejouer.ps1` était autorisé, et le lancement direct des tests offline a été refusé par le harnais). Au second tour, exécuter `c26-tests.py`, `c26-verifier.py` et `c26-paquet-tests.py` pour vérifier par soi-même matrice verte, mutations rouges et 42 tests sans TMPDIR.
- **Mineur** — `wp/outils/demo/c26.py:142` : `__import__('re').findall(...)` alors que `re` est déjà importé en tête (ligne 6). Redondance sans effet.
- **Mineur** — `wp/outils/demo/c26.py:41` : défaut `account_path` = `/mon-compte/`, chemin connu comme faux (le compte natif est `/my-account/`, cf. A-VOIR). Sans effet car la fixture renseigne toujours `account_path` (`c26-preparer.py:100`), mais le défaut reste trompeur.
- **Mineur** — `wp/tests/demo/c26-fixture.php:80` : le marqueur `accuse` (`$record['date']`, horodatage ISO à la seconde) est injecté dans les témoins interdits via `denied_markers`. Distinctif en pratique (reçus verts), mais une date à la seconde reste un témoin plus fragile qu'un marqueur dédié `C26_*`.

## Décisions techniques, défaut proposé

Questions techniques — Hermès applique le défaut sans attendre, Claude arbitre après coup :

1. Redondance `__import__('re')` (c26.py:142) : **défaut** — remplacer par `re.findall(...)`, `re` étant déjà importé.
2. Défaut `account_path` trompeur (c26.py:41) : **défaut** — mettre `/my-account/` comme valeur par défaut, ou lever si la clé est absente, pour qu'aucun chemin présumé faux ne subsiste.
3. Témoin `accuse` daté (c26-fixture.php:80) : **défaut** — conserver tel quel (aucune collision observée) ; si l'on veut durcir, remplacer par un marqueur dédié `C26_ACCUSE_FICTIF` plutôt qu'une date.

Aucune question visuelle ni touchant au réel : rien à arbitrer par Ced dans ce lot.

## Suite

`codex.md` existe mais n'a pas été ouvert (consigne). Fusion non effectuée. En attente du second tour pour croiser les deux relectures et, le cas échéant, exécuter la suite offline du lot.
