# Relecture A-11 — inventaire des adresses publiques (Claude, indépendant)

Date : 2026-11-26. Relecteur : Claude, indépendant. `codex.md` existe mais n'a **pas** été ouvert. Pas de fusion à ce stade.

Brief : `briefs/A-11-inventaire-des-adresses.md`. Cahier des charges : §4.3, dernier point.
Code relu : `wp/outils/bascule/a11/` (Address, Inventory, Command, Runtime, ReadOnlyDb, `inventorier-adresses`, README) ; tests `wp/tests/a11/` ; production `production/A-11/`.

## 0. Rejeu autorisé

Commande lancée depuis la racine, sans argument : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1` (conteneur jetable, réseau `none`, dépôt monté en lecture seule).

Dernière ligne :

> REJEU : 1061 tests, 34263 assertions, 3 échecs, 0 erreurs, 0 ignorés — FAIL

(La capture console affiche « Ã©checs / ignorÃ©s » : simple artefact d'encodage du journal, le compte est exact.)

**Les 3 échecs ne sont PAS dans A-11.** Ils sont tous dans `imagine-site` :
- `ExtractionsReglesTest::testInvalidFiltersFailEvenWhenThereAreNoRows` (jeux #1 et #7) ;
- `ExtractionsReglesTest::testUnavailableReportsAreListedButNotExecutable`.

Ce sont des fichiers non commités d'un autre chantier (cf. `git status` : `M wp/plugins/imagine-site/tests/ExtractionsReglesTest.php`, `?? wp/plugins/imagine-site/ExtractionsRegles.php`, `?? wp/plugins/imagine-site/extractions/`). A-11 ne fait partie d'aucun paquet PHPUnit découvert par T01 (`imagine-connecteur`, `imagine-non-regression`, `imagine-pilotage`, `imagine-site`) : **la suite autorisée n'exerce pas une seule ligne d'A-11.** A-11 a sa propre suite hors ligne (`wp/tests/a11/run.py`), conforme au brief (« une suite dédiée, pas de rejeu global »).

Je n'ai **pas** ré-exécuté la suite dédiée d'A-11 : elle exige Docker + MySQL + extensions commerciales (`/home/ced/staging-wp/plugins/`), hors du cadre de ce rejeu. J'ai en revanche vérifié son **paquet de preuves** en lecture seule (voir §3) et déroulé les cas à la main (voir §2).

## 1. Conformité

Le lot fait ce que demande le brief, ni moins ni plus, sur l'essentiel.

- **Une ligne par adresse relative, 7 natures.** `Inventory::add` produit `article`, `page`, `produit`, `pièce jointe`, `terme de taxonomie`, `archive d'auteur`, `archive de type de contenu` (`Inventory.php:90-94`, `:120`, `:125`, `:131`). Colonnes : adresse relative, nature, type de contenu, état, date de dernière modification (`Inventory.php:17`). Conforme au brief.
- **Public et publié seulement ; non-publics comptés, pas listés.** Brouillons/auto-brouillons, privés, protégés : comptés dans `exclus` et exclus de la liste (`Inventory.php:61-68`). Pièces jointes à parent protégé, et pages de pièces jointes désactivées : comptées (`Inventory.php:74-81`). Conforme au brief (« comptés, pas listés »).
- **Règles natives, aucun HTTP.** URLs via `get_permalink`, `get_attachment_link`, `get_term_link`, `get_author_posts_url`, `get_post_type_archive_link` ; aucune requête réseau (`pre_http_request` bloqué, `Runtime.php:68-71`). Conforme.
- **Résumé lisible.** `resume.md` : comptes par nature, structure de permaliens, bases catégories/étiquettes et bases WooCommerce (`Command.php:66-70`, vu dans la preuve). Conforme.
- **Aucune donnée client.** Seules les archives d'auteur portent l'identifiant public (`user_nicename`) déjà dans l'adresse (`Inventory.php:125`). Aucun nom, email, login, titre ou contenu écrit. Conforme au brief et à la doctrine §3.
- **Hors racine web, frère du rapport d'audit, jamais dans le dépôt.** `Command::main` refuse une sortie dans le site ou le dépôt, un parent symbolique, une sortie existante, et impose que l'audit soit frère (`dirname(dirname($audit)) === $parent`) (`Command.php:30-44`). Conforme.
- **Convention A-09 identique.** Point central du brief (« même convention… si elles divergent, dis-le »). J'ai comparé ligne à ligne `Address::relative` (PHP, `Address.php:10-31`) et `a09/check.py:relative` (`check.py:31-44`) : mêmes règles — chemin relatif à l'origine commençant par `/`, refus de `//`, ASCII seul, refus des contrôles/`#`/antislash, refus requête vide, refus des séparateurs encodés (`%2f`, `%5c`, `%00-%1f`, `%7f`, `%20` dans le chemin), décodage des seuls non-réservés `[A-Za-z0-9_.~-]`, mise en majuscule du reste, préservation **octet par octet** de la requête, refus des segments `.`/`..`. La suite dédiée appelle **la vraie fonction A-09** comme oracle et vérifie que chaque adresse produite est un point fixe (`inside.py:79`). **Les conventions ne divergent pas.** Et une URL native d'une autre origine fait refuser l'export (`A11_URL_NOT_A09_COMPATIBLE`, `Address.php:16`) plutôt que d'inventer une 3ᵉ convention. Conforme.
- **Classique et HPOS, aucun écrit, aucune tâche, aucun envoi.** Les deux stockages sont couverts par la suite ; la base n'est pas modifiée (§3) ; cron/mail bloqués.
- **Interprétations signalées.** `production/A-11/integration.md` liste les choix par défaut (contextes regroupés sur une ligne, dates vides pour termes/archives, exception native de l'archive `post`, périmètre auteurs). Bien.

**Écart mineur (ni moins ni plus).** Le brief demande « un fichier tableur » + « un résumé » ; l'outil écrit **trois** fichiers : `adresses.csv`, `adresses.json`, `resume.md`. Le JSON (données structurées + empreinte de l'audit source) sert la preuve et l'outillage A-09 ; c'est utile et sans fuite, mais c'est un ajout au-delà de la lettre du brief. À noter, pas à corriger.

## 2. Exactitude métier (déroulé à la main)

Déroulé sur la sortie réelle `production/A-11/preuves/f77a1fcd8945/classic-pretty-addresses/adresses.csv` (25 adresses) et sur l'oracle. Le banc fictif correspond à la « Preuve » du brief.

**Cas 1 — les trois contenus non publics sont absents.** Brouillon `a11-draft`, privé `a11-private`, protégé `a11-protected` : **aucune ligne** dans le CSV. Comptes : `exclus.draft=1`, `private=1`, `password=1`. La pièce jointe du parent protégé (`hidden-attachment`) : absente aussi, `attachment_parent_not_public=1`. Conforme au brief.

**Cas 2 — une adresse de chaque nature, comptes exacts.** article 3, page 3, produit 1, pièce jointe 3, terme 11 (y compris termes vides et `uncategorized`), archive d'auteur 2, archive de type 3. Vérifié contre l'oracle (`exact_native_urls_and_natures`, `summary_counts_exact`).

**Cas limite A — collision boutique / archive produit.** `/a11-shop/` apparaît **une seule fois**, nature primaire `page`, avec `autres_contextes = "archive de type de contenu : product"` (CSV ligne 8). Les comptes par nature sont donc non additifs, comme annoncé. Correct.

**Cas limite B — pièce jointe à parent manquant (orphelin).** Parent `99999999` inexistant : `publicAttachment` suit l'héritage natif, `get_post_status` la rend `publish`, et `get_attachment_link` retombe sur `/?attachment_id=37` (CSV ligne 2). Listée, comme attendu. Détection de cycle présente (`Inventory.php:28-32`).

**Cas limite C — requête filtrée, octets préservés.** `/histoires/a11-story/?edition=a%2fb+z&host=a02.synthetic.test&ssl=yes` : `%2f` reste en minuscules et non décodé, le `+` est conservé, l'ordre des paramètres est intact (CSV ligne 18). Et `host`/`ssl` prouvent que `$_SERVER` est bien reconstruit depuis l'option `home` confinée (`Runtime.php:62-66`). Conforme à la règle A-09 (requête ni triée ni ré-encodée).

**Cas limite D — pages de pièces jointes désactivées.** Variante `attachments-disabled` : `wp_attachment_pages_enabled='0'` → `!'0'` vrai en PHP → les 3 pièces jointes passent en `attachment_pages_disabled=3`, cohérent avec l'oracle. Correct.

**Cas limite E — périmètre des auteurs (vie privée).** Seuls les auteurs de contenus publiés non protégés, hors pages/pièces jointes, donnent une archive : `a11-writer` et `a11-product-writer` (2). L'abonné sans contenu et l'auteur de pages seulement sont exclus — leurs `user_nicename` sont des canaris (`PRIVATE_..._CANARY`) ; s'ils fuyaient, `no_private_fields` échouerait. Bon test, bon résultat.

**Cas limite F — changement de front (accueil statique).** Couvert par la variante `static-front` (archive `post` = page des articles, accueil = page statique). Vérifié par l'oracle du paquet.

Aucun écart trouvé entre le code et le déroulé manuel.

## 3. Tests

- **Suite autorisée (rejouer.ps1)** : lancée, **FAIL** (3 échecs), mais **hors A-11** (voir §0). Pas de régression imputable à ce lot. Signal réel pour Ced/Hermès : le dépôt a un WIP rouge dans `imagine-site/ExtractionsRegles` (hors périmètre A-11).
- **Suite dédiée A-11** : non ré-exécutée par moi (Docker/MySQL/extensions commerciales requis). Vérification en lecture seule de `production/A-11/preuves/f77a1fcd8945` :
  - `unit.json` 13 PASS, `result.json` 284 PASS, `runner.json` 7 PASS ; **0 FAIL** sur tout le paquet ; `exit_code=0` partout.
  - Empreintes base **identiques avant/après** : `classic-pretty-before.json == -after.json` (sha256 `5872ec9b…`), `hpos-static-front` (`7d21432b…`). Preuve de lecture seule au niveau base.
  - `*-readonly.json` : `write_denied`, `server_readonly`, `escape_denied`, `http_denied`, `mail_denied`, `schedule_denied` tous `true`, même avec l'identité SQL `root` du banc.
  - `verification.json` (13/284/7) cohérent avec le paquet.
- **Couverture des cas limites** : forte. Les tests ne répètent pas le code — ils construisent un **oracle indépendant** via les vraies API WP/WC (`oracle.php`) avant gel, puis comparent ; et appellent la **vraie fonction A-09** sur les adresses produites. 10 configurations (classique/HPOS × pretty/plain/subdir/attachments-disabled/static-front). Refus testés : sortie dans le web/le dépôt, sortie existante, option inconnue, lien symbolique, audit manquant/invalide, config dynamique, drop-in, URL externe.

Réserve : je m'appuie sur un paquet produit par Hermès, pas sur ma propre exécution de la suite dédiée. Les preuves sont internes-cohérentes et vérifiables, mais ce n'est pas une ré-exécution indépendante.

## 4. Sécurité et données

- **Aucun secret, aucune donnée réelle.** Banc fictif, emails `@example.org`, noms inventés/canaris. La sortie ne contient qu'adresses, natures, types, états, dates, bases de permaliens. Le test `no_private_fields` interdit `PRIVATE_`, `@`, `user_email`, `post_content`, etc. Conforme doctrine §3.
- **Lecture seule à double barrière.** `ReadOnlyDb` ouvre `START TRANSACTION READ ONLY` + filtre les requêtes à `SELECT/SHOW/DESCRIBE`, refuse `INTO OUTFILE`, `GET_LOCK`, `FOR UPDATE` (`ReadOnlyDb.php:17-31`). Injecté **avant** `wp-settings.php`. Prouvé même avec `root` (`root_write_denied`).
- **Effets de bord natifs neutralisés.** HTTP, mail, planification/replanification/suppression cron, runner Action Scheduler bloqués aux points d'entrée natifs, à `PHP_INT_MAX`, avant le boot (`Runtime.php:68-83`). Compteurs à 0 dans chaque preuve (`no_http_mail_scheduling`).
- **Refus prudent d'une pile non standard.** Multisite, constantes de chemins/tables, config DB dynamique, drop-ins, symliens du site : refusés avant exécution (`Runtime.php:14-31`, `:86-88`). Fail-closed, conforme à « ne jamais publier un inventaire partiel comme complet ».
- **Écriture de sortie.** Fichiers en `xb` exclusif, 0700/0600, refus d'écraser (`Command.php:71-86`). Neutralisation d'injection de formule dans le CSV (`Command.php:60`). Bien.
- **Paywall** : sans objet pour ce lot (lecture seule, pas de contenu réservé servi).

Pas de faille trouvée.

## 5. Doctrine

- **Standard d'abord.** L'outil appelle les générateurs natifs WP/WC, ne reconstruit pas les permaliens par concaténation SQL. README cite les fonctions et sources officielles (versions épinglées WP 7.0.9 / WC 11.1.1). Conforme §4.
- **Logique pure testable.** `Address::relative` est pure, sans WP ni base, couverte par `unit.php` (points fixes + refus). Conforme.
- **Conventions §5.** `declare(strict_types=1)`, PSR-12, espace de noms `Imagine\PublicAddresses`, PHP 8.2. Pas d'option/hook persistant à préfixer. Conforme.
- **README présent** (`a11/README.md`) : rôle, lancement, réglages, tests. Conforme §5.
- **Non-régression / rejouabilité.** Sortie idempotente prouvée (`repeat`), rejeu refusé si la sortie existe. Conforme.

## Verdict

**Conforme** pour le livrable A-11. Aucun point bloquant ni important **sur A-11**.

Points classés :

- **Important (hors périmètre A-11)** : la suite autorisée est rouge (3 échecs dans `imagine-site/ExtractionsRegles`, WIP non commité d'un autre chantier). À traiter par le chantier concerné / Hermès ; sans rapport avec A-11, mais signalé au titre de la non-régression du dépôt.
- **Mineur** : le README justifie le périmètre des auteurs par « parité avec les sitemaps utilisateurs natifs », alors que le code inclut les auteurs de **tout** type public hors page/pièce jointe, sans exiger le support `author`. Sur le banc aucun écart n'apparaît (tous les types concernés supportent `author`). Pour un inventaire d'adresses, l'inclusion est plutôt plus correcte que le périmètre sitemap ; c'est la **justification** qui est approximative, pas le résultat.
- **Mineur** : trois fichiers de sortie au lieu du « tableur + résumé » littéral du brief (ajout `adresses.json`, utile et sans fuite).
- **Mineur** : en cas d'échec d'écriture au milieu des trois fichiers, le dossier de sortie partiel subsiste et bloque le rejeu (`A11_OUTPUT_EXISTS`). Comportement documenté (« sortie partielle non écrasée »), mais l'opérateur doit le supprimer à la main.
- **Observation** : l'outil read-only vit sous `wp/outils/bascule/` que la doctrine décrit comme « scripts qui transforment l'existant ». A-02 (audit) a établi ce précédent ; cohérent, simple remarque.

Rappel doctrine : ce verdict **n'est pas un GO**. Il ne vaut que pour la clôture d'un lot de code, après deuxième relecture, fusion et absence de question ouverte pour Ced.

## Décisions techniques, défaut proposé

Questions techniques (Hermès applique le défaut sans attendre, Claude arbitre après coup) :

1. **Périmètre des auteurs** : aligner le code sur la justification (`post_type_supports($type,'author')`) **ou** corriger le texte du README ? *Défaut proposé : garder le comportement actuel (inclusion plus complète, adaptée à un inventaire de redirections) et reformuler le README.*
2. **Dossier de sortie partiel sur échec d'écriture** : nettoyer (rmdir) le dossier fraîchement créé ? *Défaut proposé : garder le fail-closed actuel (ne pas supprimer automatiquement une sortie), l'opérateur retire le dossier.*
3. **`adresses.json` supplémentaire** : le conserver ? *Défaut proposé : oui (preuve + empreinte audit + outillage A-09), en le mentionnant explicitement dans les deux lignes du mode d'emploi.*

## Pour Imagine

Aucune question métier à trancher dans ce lot.

## À arbitrer par Ced (visuel / réel)

Aucune question visuelle ni touchant au réel. Ce lot n'ouvre aucun site, aucune base, aucun compte.

---

**Suite** : `relectures/A-11/codex.md` existe mais n'a pas été lu. Je m'arrête après l'écriture de ce rapport. La fusion (`corrections/A-11.md`) reste à faire, séparément.
