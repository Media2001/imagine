# Relecture A-26 — Ce que le site charge chez des tiers (Claude, indépendant)

Lot : A-26. Brief : `briefs/A-26-ce-que-le-site-charge-chez-des-tiers.md`. Cahier des charges : §4.4.
Production relue : `wp/outils/bascule/a26/`, `wp/tests/a26/`, `production/A-26/`.
Je n'ai pas ouvert `relectures/A-26/codex.md`. Je ne fais pas la fusion (pas demandée à ce stade).

## Rejeu de la suite

Commande autorisée, sans argument :

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Conteneur jetable, réseau coupé, dépôt monté en lecture seule (`network=none ; rootfs=ro ; mount=…/wp:ro ; cap-drop=ALL ; no-new-privileges`). Dernière ligne :

`REJEU : 1149 tests, 36036 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`

Ligne complémentaire : `OUTILS : 20 outils, 521 contrôles, 0 échecs ; hors rejeu : aucun`. Le contrôle d'outils A-26 : `a26 ; 33 controls ; 0 failures ; exit=0`.

## 1. Conformité

Le lot fait ce que demande le brief, ni moins ni plus. Il n'évalue aucune conformité, ne désactive rien, ne retire aucun contenu intégré (`Command.php`, en-tête `Inventory.php`).

- Standard d'abord : dix lignes dans `wp/outils/bascule/a26/README.md:5-16`, chaque affirmation renvoyée à une page officielle (`parse_blocks`, `get_shortcode_regex`, `get_option`, `get_plugins`, `privacy`, `embeds`, `wp-consent-api`) avec empreintes dans `production/A-26/standard/sources.json`. Le point consentement du cœur (« rien, ou presque ») est dit (README §9-10).
- Deux lignes pour le mode d'emploi de l'audit : `production/A-26/readme-ajout.txt`, dont le vérificateur contrôle qu'elles figurent, à l'identique et une seule fois, dans `wp/tests/a02-audit/README.md` (`verify.py:41-44`). Conforme au livrable « deux lignes dans le mode d'emploi de l'audit ».
- Liste fermée de dix familles : `Analysis::FAMILIES` + `Analysis::PLUGINS` (`Analysis.php:10-33`). Dix-sept chemins exacts, une famille par chemin. Comptes par famille seulement. Zéro ≠ absence de tiers (README §Liste fermée).
- Identifiant de service : `oui/non/illisible`, jamais la valeur (`Analysis::families`, `siteKitIdentifier`, `Analysis.php:65-101`). Seul schéma qualifié : Site Kit GA4 champ `measurementID`. Les seize autres chemins → `illisible`, aucun parseur inventé.
- Contenus publiés : comptes par service d'une liste fermée de treize étiquettes, tout domaine hors liste → `autre` sans être nommé (`Analysis::services`, `Analysis.php:103-142`). Un contenu compte au plus une fois par service (`Analysis::content`, `array_unique`, `Inventory.php:140`, `Analysis.php:187`).
- Dix derniers numéros si A-16 sait les désigner, sinon par année GMT (`Analysis::content`, `Issues::select`, modes `postmeta`/`post_parent`/`taxonomie`).
- Neutralisation lue, non modifiée : marque `imagine_staging_disabled_plugins` lue dans la copie, import `staging/` non touché. Pour un nombre faussé, réponse `inconnu après neutralisation`, jamais zéro (`Analysis.php:94-98`, `content()` → UNKNOWN global, `Analysis.php:175-180`).
- Aucune adresse, domaine hors liste, identifiant ni titre ne sort : le schéma de sortie est fermé et validé octet à octet (`report.py:projection`), les codes d'erreur sont une liste fermée (`refusals.json`, `confine.py:closed_refusal`).

Lien §4.4 : le lot fournit la **liste** qui alimentera le futur bandeau et le registre ; il ne déclare rien « conforme ». Cohérent avec « ce lot ne dit pas ce qui est conforme ».

Interprétations signalées par l'auteur (acceptables) : (a) `illisible` par défaut pour toute famille sans schéma qualifié ; (b) Site Kit = unique schéma d'identifiant ; (c) les deux lignes du mode d'emploi intégrées au README de l'audit A-02. Aucune interprétation non signalée relevée.

## 2. Exactitude métier — déroulé à la main

Banc classique, sans correspondance A-16 (mode année). Contenus publiés du `seed.php` :

- `$old` 2024, iframe youtube → youtube. `$video` 2026, bloc `wp:embed` youtu.be → youtube (compté une fois malgré l'URL nue dupliquée). `$other` 2026, iframe+img vers domaine `.invalid` → `autre` une fois ; le `<a href="vimeo">` ordinaire **n'est pas** compté (href hors balise `link`, `Analysis.php:156-161`). Post `draft` vimeo → exclu. 2023 `[embed]vimeo[/embed]` → vimeo. `wp_block` spotify résolu via `core/block` (2023) → spotify. 2022 iframe youtube → youtube. Les onze `imagine_numero` 2025 (publics, vides) → année 2025 à zéro.
- Totaux attendus : youtube 3, vimeo 1, spotify 1, autre 1 ; années 2022,2023,2024,2025,2026.
- `classic-tiers/tiers.json` : **identique**. ✓

Sélection « dix derniers » (liaison `post_parent`). Onze numéros 2025-01…2025-11 ; les dix retenus écartent le plus ancien (2025-01). `$old` lié au plus ancien → exclu ; `$video`→2025-11 et `$other`→2025-10 retenus.

- Attendu : `last_ten` youtube 1, autre 1, reste 0 ; `all` inchangé.
- `classic-last-ten-post_parent/tiers.json` : **identique** (youtube 1, autre 1). ✓ L'exclusion du plus ancien et des orphelins est bien appliquée (`Issues.php:60-88`).

Cas neutralisé (`classic-neutralised/tiers.json`) : `neutralisation` = UNKNOWN ; mesure et pixel → `active`+`identifier` UNKNOWN ; familles encore actives → `active` observé mais `identifier` UNKNOWN ; `content` → UNKNOWN global. Jamais un zéro là où le nombre est faussé. ✓ Conforme au brief.

Cas limites couverts et vérifiés : changement d'année (partition annuelle, somme = total, `report.py:55-63`), dates UTC strictes et `0000`/date absente → année 0 (`Issues.php:50-56`, `Inventory.php:138`), article lié à plusieurs numéros compté une fois, orphelins hors sélection mais dans le total, profondeur de références >16 / cycle / >4 Mio → refus générique (`Inventory.php:37`, `73-83`).

## 3. Tests

- Suite rejouée : **PASS** (voir ci-dessus). Suite Python rejouable utf-8 **et** cp1252 contrôlée (`verify.py:74-79`).
- Les tests contrôlent la règle, pas le code : preuve rouge/vert TDD (`red-unit.json` doit **FAIL** sur `neutral_content_unknown_possible_whole_value_scrub`, `verify.py:96-99` ; mutant de neutralisation rouge, `red-green.json`). Cas nommés exigés : `exact_content_per_service_once`, `annual_fallback_utc`, `last_ten_exact_no_oldest_no_orphans` (trois modes), `neutral_unknown_never_zero`, `all_private_values_absent_all_report_files` (`verify.py:101-124`).
- Couverture classique **et** HPOS, nominal et limites. Non-régression de la base et des fichiers du site (empreintes avant/après identiques, `verify.py:113-119`).

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle. Fixtures manifestement inventées (`A26_…_CANARY`, domaines `.invalid`, `seed.php`). Doctrine §3 respectée.
- **Cinquième canari (A-22) tenu** : recherche de `CANARY`, `A26_DOMAIN`, `pi_a26fiction`, `measurementID`, identifiant GA4 sur tout `production/A-26/preuves/` → **aucune occurrence**. Aucune valeur privée ne sort sur aucun canal ni dans les fichiers de rapport.
- Lecture seule : SQL SELECT + transaction READ ONLY via A-11, pare-feu Landlock A-12, réseau nul, mail/exec refusés (`Command.php:21-23`, `confine.py:66-77`). `error_log` → `/dev/null`, jamais un chemin du site.
- Requêtes préparées partout (`$wpdb->prepare`, comparaisons `BINARY`, `Inventory.php`, `Issues.php`). Sortie écrite 0700/0600, dossier final neuf, parent disjoint du site et du dépôt (`Command.php:31-89`).
- Pas de paywall dans ce lot (inventaire en lecture seule) ; aucune voie ne recopie un chemin ou un nom tiré du site (codes d'erreur fermés, schéma fermé).

## 5. Doctrine

- Standard d'abord respecté : parseurs natifs `WP_Block_Parser`, `get_shortcode_regex`, options `get_option` ; aucun code ne refait ce qu'une extension fait déjà (le lot ne gère ni consentement ni blocage, il le dit).
- Conventions §5 : PHP 8.2, `declare(strict_types=1)`, namespace `Imagine\…`, préfixe `imagine_` (marque lue, non créée), `README.md` présent. Contrôle PSR-12 en conteneur (`style.json`, `verify.py:127-129`).
- Aucune modification d'extension tierce ; uniquement des hooks neutralisants sur Action Scheduler (`Inventory.php:95-100`).

## 6. Études

Sans objet (lot avec code). Les affirmations du volet « standard » citent chacune une page officielle avec adresse et empreinte conservée (`production/A-26/standard/`).

## Points

Aucun point bloquant. Aucun point important.

**Mineurs / à noter :**

1. *(technique)* `Analysis::families` rend `illisible` pour toute famille active sans schéma qualifié (toutes sauf Site Kit). Le `non` du brief (« aucun identifiant renseigné ») devient donc inatteignable hors mesure. Interprétation prudente et documentée (README §Liste fermée). **Décision technique, défaut proposé** : garder `illisible` (ne jamais affirmer un faux « non »). Pas bloquant ; j'arbitre après coup si Codex diverge.
2. *(observation)* Les dix lignes du standard vivent dans `a26/README.md`, les deux lignes du livrable dans le README de l'audit A-02 ; deux documents distincts là où le brief parlait d'un seul « mode d'emploi ». Conforme au livrable, signalé pour transparence.
3. *(positif)* Étanchéité des sorties : schéma fermé validé octet à octet, codes d'erreur fermés, canaris absents du paquet entier. Rien à corriger ; noté comme preuve que la règle de la voie 1 est tenue.

Aucune question pour Ced (lot de code, rien de visuel ni touchant au réel). Aucune règle métier à trancher.

## Verdict

**Conforme.** Points : aucun bloquant, aucun important, trois mineurs/observations ci-dessus.

Rappel : ce verdict n'est **pas** un GO. `production/A-26/PRET` annonce la disponibilité à la relecture, pas une mise en ligne. La clôture attend la seconde relecture, la fusion avec `codex.md` (non lu ici) et l'absence de question ouverte.
