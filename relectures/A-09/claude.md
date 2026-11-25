# Relecture A-09 — Le test des redirections (Claude, relecteur indépendant)

Lot : A-09, brief `briefs/A-09-test-des-redirections.md`, cahier des charges §4.3 (dernier point).
Production : `wp/outils/bascule/tester-redirections` + `a09/check.py`, tests `wp/tests/a09/`, mode d'emploi `tester-redirections.md`, exemple `plan-redirections.exemple.csv`, `production/A-09/`.
Je n'ai pas lu `codex.md`. Pas de fusion à ce stade.

## Rejeu des tests

Commande autorisée, sans argument :

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Dernière ligne obtenue :

`REJEU : 1022 tests, 34090 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`

**Réserve importante sur ce rejeu.** `rejouer.ps1` rejoue la suite **PHP T01** (plugin `imagine-site`). A-09 est un paquet **Python** en lecture seule : il **n'ajoute aucun test à cette suite**. Le PASS ci-dessus ne touche donc pas une seule ligne du livrable A-09. C'est assumé par Hermès (`notes.md`, `tester-redirections.md`, `PRET`), mais il faut le dire clairement : la commande de rejeu globale du projet ne couvre pas ce lot.

Les tests du lot vivent dans un banc dédié (`wp/tests/a09/run.py`, Docker `network=none`, HTTP loopback). Pour vérifier malgré tout :

- J'ai rejoué `test_check` à la main sur l'hôte : logique du plan et de l'autorisation **vertes** (seul échec résiduel : création de lien symbolique interdite par les privilèges Windows — limite d'environnement, hors logique).
- Les tests HTTP échouent sur l'hôte à cause du chemin `/report` codé en dur (il n'existe que dans le conteneur) : ce sont des erreurs d'environnement, pas de logique.
- La preuve de production `preuves/6fd5c1c30990/` montre **21 tests verts** dans le bon banc Docker. J'ai recalculé les SHA-256 des cinq sources livrées : ils **correspondent au `manifeste.json`**. La preuve porte donc bien sur le code livré, elle n'est pas périmée.

## 1. Conformité

Le lot fait ce que demande le brief, ni moins ni plus.

- Outil `wp/outils/bascule/tester-redirections` (lecture seule) : prend un plan CSV du dépôt + une adresse de base, dit pour chaque ligne conforme / défaut. ✓
- Ne décide, ne crée, ne pose aucune redirection. ✓ (`notes.md`, en-tête de `check.py`.)
- Ne suit jamais une redirection hors du site testé : `check.py:162-164` signale `cible_externe` et **arrête** sans visiter ; prouvé par le piège d'autre origine resté vide (`test_http.py:252`, `externes/rapport.md`). ✓
- N'interroge que l'origine déclarée : `authorize_site` (`check.py:81-101`) exige les **mêmes trois prédicats** du marqueur vérifié et les mêmes octets du MU de sécurité que A-04/A-05 (import de `a04/update.py` sans modification, fonctions `safe_path`/`load_json`/`digest`/`Refusal` confirmées présentes), plus une déclaration `.imagine-a09-http.json` liant l'origine au répertoire ; `kind` limité à `test`/`staging`, `base_url` lié à `--base-url`. `Client.get` (`check.py:113`) revérifie l'origine à chaque requête. Production impossible sans GO. ✓
- Cadence limitée : intervalle par défaut 0,5 s, minimum 0,1 s (`check.py:116`, `main:216`) ; espacement vérifié par horodatage dans les tests (`test_http.py:93,162`). ✓
- Plan validé **avant tout appel** : doublons et lignes contradictoires (`check.py:58`, même garde pour les deux), ancienne = cible (`:59`), adresse absolue / `//hôte` / fragment / segment `.`/`..` / encodage de séparateur (`relative`, `:31-41`). Zéro requête si le plan est invalide, même pour une première ligne valide suivie d'une mauvaise (`test_http.py:188`). ✓
- Sortie : `rapport.md` lisible + `nonconformes.csv` (tableur) + `rapport.json` ; code de retour **1** s'il y a au moins une non-conformité (`write_reports:203`). ✓
- `plan-redirections.exemple.csv` : trois lignes de données fictives + en-tête, codes 301/302/308, aucune adresse d'Imagine ; se charge sans erreur via `load_plan` (vérifié). ✓
- `production/A-09/PRET` présent. ✓

Interprétations signalées par Hermès (`notes.md`, « Décisions prises à défaut ») : deux colonnes relatives + origine séparée ; déclaration HTTP supplémentaire ; conforme = premier code + première cible + un saut + 200. Toutes cohérentes avec le texte du brief. Aucune interprétation non signalée relevée.

## 2. Exactitude métier (déroulé à la main)

Déroulé de `check_row` (`check.py:129-178`) sur les cas du brief, comparé aux rapports de `preuves/6fd5c1c30990/` :

1. **Conforme** — `/ancien-fictif` →301→ `/nouveau-fictif` (200). Attempt 0 : code 301 = attendu ; saut 1 ; cible observée = cible attendue ; attempt 1 : 200, non-redirection, `final_status=200`, aucun défaut → `CONFORME`. Conforme au rapport. ✓
2. **Chaîne** — `/chaine` →301→ `/intermediaire` →302→ `/final` (200). Saut 2 → `chaine` ; première cible `/intermediaire` ≠ `/final` → `mauvaise_cible`. Rapport : `mauvaise_cible, chaine`, sauts 2, HTTP final 200. ✓
3. **Boucle** — `/boucle` →301→ `/boucle-b` →301→ `/boucle`. Au troisième tour, URL déjà vue → `boucle` (`check.py:135`). Auto-boucle `/auto`→`/auto` également reconnue. Rapports : `chaine, boucle` et `mauvaise_cible, boucle`. ✓
4. **Cible 404** — `/depart` →301→ `/attendu` (404). Attempt 1 : 404 non-redirection, `≠200` → `cible_non_200`. Rapport conforme ; 503 traité pareil. ✓
5. **Cible externe** — `/externe` →301→ origine tierce. `cible_externe`, arrêt, aucune visite de la cible. Variante tardive (`/plus-tard`→`/hop`→externe) : `chaine, cible_externe`. Schéma relatif au protocole (`//hôte`) et `mailto:` aussi arrêtés. ✓
6. **Ligne de plan invalide** — `load_plan` lève avant toute requête ; code de retour **2** (refus), distinct du **1** (non-conformité) ; zéro GET. ✓

Cas limites vérifiés dans les tests : les cinq codes 301/302/303/307/308 conformes en un saut ; `Location` absente / double → `redirection_invalide` ; source qui répond 200 (redirection absente) → `mauvais_code` ; délai dépassé → `delai_depasse` ; plafond de 9 GET par ligne → `limite_sauts` (chaîne de 20 bornée à 9 requêtes, confirmé par le journal des GET). Diagnostic borné, la limite n'est jamais une conformité. ✓

## 3. Tests

- Suite dédiée A-09 : **21 tests, verts** dans le banc Docker (`preuves/6fd5c1c30990/tests.log`, `OK`). `test_check` revérifié vert sur l'hôte (hors symlink, limite d'environnement).
- Les tests vérifient la **règle**, pas le code : serveur HTTP loopback réel avec routes, assertions sur le contenu des rapports **et** sur le journal des GET (ordre, espacement ≥ 0,09 s, empreinte du site inchangée, piège d'autre origine resté vide). Ce ne sont pas des répétitions du code.
- Cas limites couverts largement : chaîne, boucle, auto-boucle, plafond de sauts, 404/503, délai, `Location` absente/double, externe immédiat/tardif, schéma de protocole relatif, `mailto:`, source 200, tous les codes, cibles absolues même-origine et avec paramètres, injection de formule CSV neutralisée, plan invalide → zéro requête, site non vérifié, limites interdites, sortie déjà existante ou interne au site.

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle : fixtures fictives, `@example.org`, aucune adresse d'Imagine. ✓
- Sorties échappées : `rapport.md` passe par `html.escape` et neutralise `|` et sauts de ligne (`write_reports:192`) ; `nonconformes.csv` préfixe les cellules commençant par `= + - @` / tab / CR / LF pour empêcher l'interprétation en formule (`:201`), testé avec une cible `=/formule-fictive`. ✓
- Pas de SQL, pas de WordPress booté : aucune requête préparée à vérifier, pas de nonce applicable. L'outil n'ouvre ni site, ni base.
- Étanchéité à l'origine : chaque requête revérifie schéma/hôte/port ; aucune autre origine atteinte même au deuxième saut (prouvé). Refus de toute URL avec identifiants, chemin ou paramètres dans `--base-url`. ✓
- `GET` seulement, pas de cookies, pas d'authentification, pas de proxy d'environnement, pas de nouvelle tentative, corps non téléchargés. ✓

## 5. Doctrine

- **Standard d'abord** : le brief scope volontairement un outil sur mesure qui **vérifie** un plan en lecture seule avant bascule, sans gérer de redirections (le plan vient du référenceur). Les extensions de redirection gèrent, elles ne testent pas un plan hors-ligne avant bascule. Le sur-mesure est justifié, pas de réinvention d'un standard.
- Lot Python (famille `wp/outils/bascule/`, cohérent avec A-04/A-05) : le §5 de la doctrine (PHP 8.2, `strict_types`, PSR-12) vise le code WordPress et ne s'applique pas ici. Préfixes `imagine_` / `org.imagine.*` respectés pour les marqueurs et le label. Textes de sortie en français.
- Rejouable et isolé : banc jetable `network=none`, dépôt monté en lecture seule, nettoyage du conteneur vérifié par nom et ownership, sources suivies inchangées. ✓
- Non-régression : 80 sources acceptées conservées byte-identiques (`baseline.json`, `PRET`) ; aucun correctif hors A-09.

## Verdict

**Conforme** (ce verdict n'est pas un GO).

Points classés :

**Bloquant** — aucun.

**Important**
- La commande de rejeu globale `rejouer.ps1` renvoie `PASS` **sans exécuter aucun test A-09** ; la couverture du lot repose entièrement sur le banc dédié `wp/tests/a09/run.py` (hors harnais partagé). C'est transparent et documenté, mais à garder en tête pour la clôture : un futur « rejeu global vert » ne prouvera rien sur cet outil. Défaut proposé : accepter la commande dédiée comme preuve du lot, et ne pas conclure sur A-09 à partir du seul `rejouer.ps1`.

**Mineur**
- Sur une chaîne dont la destination **finale** est pourtant la cible planifiée, le rapport affiche `mauvaise_cible, chaine` : le `mauvaise_cible` porte sur la **première** cible (intermédiaire), ce qui est exact mais peut se lire comme « mauvaise destination » alors que l'arrivée est bonne. Les colonnes « Cible observée » et « HTTP final » du `rapport.md` lèvent l'ambiguïté. Correction possible (facultative) : une mention distinguant « première cible ≠ plan » d'une « destination finale fausse ». À laisser tel quel si on préfère la règle stricte « un saut » du brief.
- `tester-redirections.md:59-62` renvoie à `python -B wp/tests/a09/run.py` et `production/A-09/verifier.py --replay` comme commandes de rejeu. Cohérent avec le lot, mais à signaler côté doctrine de relecture, dont la commande autorisée unique est `rejouer.ps1`. Aucune action côté code.

### Décisions techniques, défaut proposé
- Déclaration HTTP supplémentaire `.imagine-a09-http.json` en plus du marqueur vérifié A-04/A-05 : garde plus **restrictive** que les autres outils de bascule. Défaut proposé : **conserver** (ferme par défaut, conforme à la doctrine du doute). Claude arbitre après coup si Hermès veut aligner strictement sur A-04/A-05.

### Pour Imagine
- Aucune question métier introduite par ce lot : il ne décide d'aucune redirection. Le plan réel et son arbitrage restent hors périmètre (ils viendront du référenceur).

### À arbitrer par Ced (visuel / réel)
- Aucune question visuelle ni touchant au réel. Aucun accès à un site, une base ou un compte. Aucune autorisation production demandée.

---
`codex.md` existe mais n'a pas été lu. Fusion non faite : je m'arrête après la relecture, conformément à `relecteurs/CLAUDE.md` (la fusion n'intervient qu'une fois mon rapport écrit, et sur demande).
