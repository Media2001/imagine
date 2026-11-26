# Relecture A-16 — Claude (indépendant)

Lot : A-16, l'état des lieux des dix derniers numéros. Brief `briefs/A-16-dix-derniers-numeros.md`, cahier des charges §4.3.
Relecture faite sans ouvrir `relectures/A-16/codex.md`. Pas de fusion à ce stade.

## Rejeu de la suite PHP

Commande autorisée, sans argument :

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Dernière ligne :

`REJEU : 1093 tests, 34426 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`

Portée : cette commande rejoue toute la suite PHPUnit de l'extension `imagine-site` dans le conteneur jetable T01 (réseau `none`, dépôt monté en lecture seule). Elle **n'exécute pas** les preuves propres à A-16 (7 assertions `unit.php` + 54 assertions natives classic/HPOS + 3 tests du lanceur) : celles-ci vivent dans le runner isolé `wp/tests/a16/run.py`, qui exige Docker avec les extensions sous licence et une copie de staging. Je ne peux pas les rejouer ici (droits §3) ; je les ai contrôlées sur le paquet de preuves livré (voir §3 ci-dessous).

## 1. Conformité

Conforme au brief. L'outil est un complément du script d'audit, en lecture seule, qui réemploie le lanceur confiné d'A-12 (`confine.py` → Landlock) et la connexion READ ONLY d'A-11 (`Runtime::boot`), frère du rapport A-02.

- Correspondance opérateur **obligatoire** : sans `--correspondance`, le lanceur sort sur `A16_MAPPING_REQUIRED` (`confine.py:16`). Exemple fictif livré (`correspondance.exemple.json`). Conforme au brief (« il lit un fichier de correspondance… sans fichier, l'outil s'arrête en le disant »).
- Une ligne par numéro avec exactement les champs demandés : id + date sans titre, articles publiés/non publiés, sans thématique / plusieurs thématiques, sans image principale, médias attachés, fichiers manquants, PDF (oui / non / déclaré mais fichier absent) + emplacement public (`Inventory.php:167-198`).
- Hors numéros : orphelins publiés par année UTC, comptés sur **tous** les numéros et non sur la sélection N (`Inventory.php:135,151-158`). Conforme.
- Sorties en comptes et identifiants seulement, aucun titre, texte, auteur ni chemin (`Command.php:75-86`, aucun libellé n'est lu).
- Aucun rattachement, aucune thématique déduite : les liaisons `postmeta` / `post_parent` / `taxonomy` sont celles désignées par l'opérateur, et aucune équivalence terme↔contenu n'est inventée (`Inventory.php:112-118`).

Interprétations faites, toutes signalées dans `LIVRAISON.md` (« Décisions prises à défaut ») : dates UTC, tous les états d'article, égalité tranchée par ID décroissant, PDF dans `uploads` = emplacement public et non preuve HTTP. Elles collent au texte du brief et du §4.3 ; rien d'inventé sur un silence.

## 2. Exactitude métier

Déroulé à la main du banc fictif (`seed.php`) et comparé à la sortie `production/A-16/preuves/final/classic-issues/numeros.json`.

Banc : 3 numéros (janv./févr./mars 2026) ; 4 articles (publié, brouillon, publié, publié), tous datés 2025-02-01 ; liaison par `_a16_numero_id` → art.0 et art.1 sur mars, art.2 sur février, art.3 orphelin.

- **Numéro de mars** (art.0 + art.1) : articles 2, publiés 1, non publiés 1 ; sans thématique 1 (art.0 n'a pas de terme), plusieurs thématiques 1 (art.1 en a deux) ; sans image principale 1 (art.0 n'a pas de vignette, celle d'art.1 existe) ; médias attachés 2 (`present.jpg` + `missing.jpg`, parent art.0), fichier manquant 1 (`missing.jpg`) ; PDF « oui », public true. → **concorde**.
- **Numéro de février** (art.2) : articles 1, publiés 1 ; thématique présente ; sans image principale 1 (pas de vignette) ; aucun média attaché ; PDF déclaré mais fichier absent (`missing.pdf`), public true. → **concorde**.
- **Numéro de janvier** : aucun article, tout à zéro, PDF « non », public null. → **concorde**.
- **Orphelins** : art.3 publié, daté 2025 → `{année 2025 : 1}`. → **concorde**.

Cas limites vérifiés sur les preuves :
- **Variante `post_parent`** : même regroupement, mêmes comptes (`classic-parent`). Concorde.
- **Variante `taxonomy`** (numéros = termes, date en termmeta `_a16_date`, liaison taxonomique) : mêmes comptes, identifiants = ID de terme (`classic-taxonomy`). Concorde. Un numéro-taxonomie avec `date_cle = post_date_gmt` est bien refusé (`Inventory.php:78-83`).
- **Clé absente nommée** : une liaison vers une clé inexistante sort `A16_MAPPING_KEY_ABSENT {"key":"absent_key"}` sans révéler de valeur (`classic:absent_mapping_key_named`).
- **Limite** : `--limit=2` ne garde que les 2 numéros les plus récents, ordre date UTC décroissante puis ID (`classic:configurable_last_n_and_deterministic_order`).
- **Rejeu identique** : deux exécutions produisent des octets identiques (`classic:replay_identical`).
- Date `0000-…`, référence sérialisée, doublon de métadonnée, chemin externe / traversée / lien symbolique : refus explicites prévus (`Inventory.php:31-33,41-43,56-70,127-129`).

## 3. Tests

- Suite globale PHP : **PASS** (ligne REJEU ci-dessus).
- Suite isolée A-16 (contrôlée sur `production/A-16/preuves/final`, non rejouable ici) : `unit.json` → 7 PASS / exit 0 ; `result.json` → **54 PASS, 0 FAIL** sur les deux stockages (classic et HPOS), `native.log` sans aucune ligne FAIL, `runner.json` exit 0. Le banc couvre le nominal **et** les cas limites (absent, limite, variantes, rejeu, gardes de sortie, drop-in refusé, exécution non confinée refusée, empreintes base/fichiers identiques avant/après, canari absent, permissions 0700/0600).
- Les tests vérifient bien la règle et ne répètent pas le code : `inside.py:44-48` fixe un oracle attendu numéro par numéro et compare l'égalité stricte des lignes ; `inside.py:50` cherche activement toute fuite (`CANARY|@|/scratch|present\.|missing\.|post_title|…`).
- Les deux lignes du mode d'emploi partagé (`wp/tests/a02-audit/README.md:69-70`) sont verrouillées par `verify.py:38` (chacune présente une seule fois).
- Style PSR-12 strict : `style.json` → phpcs exit 0.

Vérifié aussi de ma main : canari absent de toutes les sorties relues (`grep CANARY` sur les dossiers `*-issues`, `*-audit`, `*-limit`, `*-parent`, `*-taxonomy` → rien).

## 4. Sécurité et données

- Sorties : comptes, identifiants internes (ID de post/terme, autorisés par le brief) et dates seulement. Aucun titre, texte, auteur ni chemin. Vérifié.
- Fixtures fictives, adresse `fictif@example.org`, titres manifestement inventés.
- Lecture seule effective : connexion READ ONLY avant bootstrap (A-11), gardes mail/HTTP/cron tentées pour de vrai dans le runtime fictif (`inside.py:29-35`), empreintes base + Action Scheduler + fichiers identiques avant/après (`classic:all_tables_scheduler_identical`, `files_identical`).
- Confinement obligatoire : hors conteneur (`A16_CONFINED` absent, `mail`/`exec` présents) → `A16_CONFINEMENT_REQUIRED` (`Command.php:55`).
- Durcissement des chemins : sortie disjointe du site et du dépôt dans les deux sens, parent frère du rapport d'audit, refus des `..`, octets de contrôle, liens symboliques et realpath divergent (`Command.php:31-47`, `Inventory.php:56-70`). `filesize` plafonnée sur l'audit (16 Mo) et la correspondance (64 Ko).
- Aucun secret, aucune archive, aucun compte/service réel, aucune donnée de production.
- Paywall : sans objet ici (outil d'audit hors ligne, aucune diffusion de contenu).

## 5. Doctrine

- Standard d'abord : l'outil n'ajoute que ce que l'audit ne fait pas, en réutilisant A-02/A-11/A-12 ; aucune réécriture d'extension tierce, uniquement de la lecture SQL préparée.
- Logique métier en PHP pur testable (`Inventory`, `Mapping`), couche fine de lanceur.
- Conventions §5 : `declare(strict_types=1)`, espace de noms `Imagine\`, préfixe `imagine_`/`a16_`, PSR-12 vert, requêtes préparées (`$this->db->prepare`), comparaisons `BINARY` sur les clés de métadonnée. README présent.
- Rejouable et idempotent : rejeu bit à bit identique prouvé.

## 6. Points relevés

**Mineur — `Command.php:71-72`, encodage mort.**
`$report['audit_sha256'] = …;` puis `$json = json_encode($report, …);` (ligne 72) sont aussitôt écrasés par les lignes 73-74, qui ajoutent `mapping_sha256` et ré-encodent. Le `$json` de la ligne 72 n'est jamais utilisé. Aucun impact fonctionnel (la sortie finale contient bien les deux empreintes, confirmé dans `numeros.json`), simple redondance. Correction proposée : supprimer la ligne 72 et ne garder qu'un seul `json_encode` après l'ajout des deux empreintes.

## Verdict

**Conforme.** Un verdict de relecture n'est **jamais un GO** (doctrine §6).

Points classés :
- **Bloquant** : aucun.
- **Important** : aucun.
- **Mineur** : 1 (encodage mort `Command.php:72`).

Aucune question pour Ced (rien de visuel ni touchant au réel). Une seule question technique, de défaut évident, à trancher après coup.

### Décisions techniques, défaut proposé

1. Encodage mort `Command.php:72` (voir §6). **Défaut proposé** : supprimer la ligne redondante. Catégorie : technique. Hermès applique sans attendre ; j'arbitre après coup.

## Suite

`relectures/A-16/codex.md` existe mais n'a pas été ouvert, conformément à la consigne. Fusion non réalisée : à faire dans un second temps.
