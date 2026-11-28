# Vérification C-33 — second et dernier tour

Vérificateur : Claude. Base : `corrections/C-33.md` (fusion), état relu `47e84833` (28/11 02:33) → `HEAD`.
Méthode : `git diff` sur `wp/` et `production/C-33/`, relance des tests reproductibles, exécution du vérifieur hors ligne. Pas de nouvelle relecture complète.

Périmètre modifié depuis la version relue (C-33 seul) : `wp/outils/demo/c33-browser.py`, `wp/outils/demo/c33_control.py` (nouveau), `wp/tests/demo/c33-runtime.php`, `wp/tests/demo/c33-control-tests.py` (nouveau), `wp/plugins/imagine-site/tests/ComptesPublicsC33AdapterTest.php` + `ComptesPublicsC33WPStubs.php` (nouveaux), `wp/plugins/imagine-site/README.md` (section C-33), `production/C-33/verifier.py` et artefacts `*-corrections-V2`.
**`ComptesPublics.php` et `ComptesPublicsRegles.php` ne sont pas touchés** : la correction est bien de niveau *preuve*, pas *fonction*, comme la fusion l'exigeait.

## 1. Instructions de la fusion

### Instruction 1 (P1, important) — en-têtes complets avant occultation + mutation témoin + fix `verifier.py:24`
**Appliquée.**
- Réception de **tous** les en-têtes : `c33-browser.py:41` (`all_headers=response.headers_array`) passés à `control()` au lieu du dictionnaire filtré à trois noms.
- Inspection noms **et** valeurs, doublons compris, avant toute sélection : `c33_control.py:48-52` (`header_text` sur toutes les paires, `leak` dessus, `all_headers_inspected`).
- Occultation repoussée après inspection : `c33-browser.py:57` (`archive_headers(all_headers)`), commentaire explicite `c33-browser.py:56`. Seuls les trois noms sûrs gardent leur valeur (`c33_control.py:8,20`) ; les autres valeurs sont caviardées (`other_values_redacted:True`, `c33-browser.py:60-61`). Noms archivés sans valeur (`c33-browser.py:58`) : aucun jeton ni valeur de cookie enregistré.
- Mutation témoin hors `location/content-type/link` (`X-C33-Audit-Compte`) exigeant le rejet : `c33-browser.py:45-48`, assertion `P1_entete_hors_trois_noms_refuse` (`:47`).
- `verifier.py:24` corrigé : la fausse assertion « pas de Set-Cookie » sur dictionnaire déjà filtré est supprimée, remplacée par un contrôle réel d'inspection complète (`production/C-33/verifier.py`, commentaire « Pas d'affirmation … sur un dictionnaire qui le filtre » + `all_headers_inspected`/`headers_inspected`).

### Instruction 2 (P2, important) — auteur XML exact, URI séparées, mutation de retrait, repli RSS2 **et** Atom
**Appliquée.**
- Extraction de l'unique article témoin et comparaison **exacte** après décodage XML de `dc:creator` (RSS2) / `author/name` (Atom) : `c33_control.py:23-44` (`feed_author`), verdict feed `c33_control.py:80` (`author_fields==1 and author==expected_signature`), remplace `expected_signature in body`.
- Contrôle séparé de l'absence d'URI/url de compte : `c33_control.py:41-44` (`account_uri_absent`), assertion `_uri_url_compte_absentes` (`c33-browser.py:51`).
- Mutation de retrait du champ auteur exigeant le rejet : `remove_feed_author` (`c33_control.py:91-102`), assertion `_P2_retrait_auteur_refuse` (`c33-browser.py:54`), rejet vérifié même si le nom du site subsiste ailleurs.
- Repli au nom du site couvert en RSS2 **et** Atom : ajout de `atom-repli` à côté de `rss2-repli` (`c33-browser.py:78`) ; le vérifieur impose les quatre voies `{rss2, atom, rss2-repli, atom-repli}`.

### Instruction 3 (M2, mineur — défaut technique, Hermès applique) — test léger enregistrement + priorités des accroches
**Appliquée.**
- `ComptesPublicsC33AdapterTest.php` avec bouchons isolés (`ComptesPublicsC33WPStubs.php`) :
  - `testEnregistrementExactPrioritesEtArguments` (`:21-32`) : priorités exactes, dont `template_redirect` prio **0** pour `auteur`.
  - `testArchiveFermeeAvantCanonicalEtGardes…` (`:34-51`) : `set_404`, retrait de `redirect_canonical`, gardes connecté/non-auteur.
  - `testFiltresFluxNeTouchentNiHorsFluxNiConnectes` (`:53-65`) : garde `is_feed` et compte connecté sur `the_author`/`get_the_author_user_url`.
- Régression de câblage désormais détectable sans conteneur navigateur.

## 2. Résultat des tests

- **Contrôleur pur C-33** (`python -B wp/tests/demo/c33-control-tests.py`) : relancé par moi → **7 tests, OK**.
- **Preuve rouge/vert** (`controleurs-red-green-corrections-V2.json`) : l'ancien contrôleur rejoué (`--legacy`) **échoue — 17 failures** sur les mêmes 7 tests ; le contrôleur corrigé **passe (OK)**. Les tests détectent donc réellement les trous P1/P2.
- **PHPUnit ciblé** (conteneur hors ligne, read-only, `--cap-drop ALL`, `--network none`, `--filter ComptesPublics`) : **OK (5 tests, 26 assertions)** — inclut le nouvel `ComptesPublicsC33AdapterTest` (`cible-corrections-V2.log`).
- **Rejeu complet** (`replay-corrections-final-V2.log`, `T01_RESULT`) : **1243 tests, 37036 assertions, 0 failures, 0 errors, 0 skipped**, 23 outils / 852 checks sans échec, `pass:true`, `ComptesPublicsC33AdapterTest` présent, **aucun paquet rouge** (`packets.failures=[]`).
- **Vérifieur de bout en bout** (`python -B production/C-33/verifier.py`) : relancé par moi → **`C33: PASS`** (native 14, browser 89 contrôles, 20 réponses, 6 mutations natives, 5 mutations de preuve, 7 tests contrôleur, état restauré, fixtures/sondes retirées).

PHP n'est ni installé ni autorisé en local ; les suites PHPUnit tournent, par doctrine, dans le conteneur jetable. J'ai relancé tout ce qui est reproductible en Python et revérifié les reçus PHPUnit archivés via le vérifieur et les logs horodatés 05:12-05:19.

## 3. Régressions / modifications non demandées

- Aucune régression. Le code métier (`ComptesPublics.php`, `ComptesPublicsRegles.php`) est inchangé.
- Le vérifieur est devenu **plus strict** que la version relue : il n'accepte plus aucun paquet rouge (l'ancienne tolérance A-32/A-33/A-34 est retirée) ; `packets.failures=[]` le confirme. Durcissement, pas régression.
- `c33-standard.py` (nouveau) et la section README C-33 documentent les corrections : documentation, pas de changement de comportement.
- Hygiène des données : aucun secret, aucune donnée réelle ; témoins fictifs, valeurs d'en-têtes sensibles caviardées, état restauré. Conforme à la doctrine §3.
- Q1 (abonné connecté) reste une question « Pour Imagine », non adressée à Ced ; défaut prudent inchangé. Aucune question visuelle ni touchant au réel en suspens.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les trois instructions de la fusion (P1, P2, M2) sont appliquées et prouvées, la preuve est désormais réellement gardée (démonstration rouge/vert à l'appui), les tests reproductibles et le vérifieur passent, aucune régression ni modification non demandée. Aucun problème de fond restant, aucune question ouverte pour Ced sur ce lot.

**Rappel doctrine : un verdict de vérification n'est pas un GO** (§3/§6). Il ne vaut que pour la clôture de ce lot de code ; déployer ou toucher à un site, une base ou un compte réel reste une décision de Ced.
