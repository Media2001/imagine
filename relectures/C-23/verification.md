# Vérification C-23 (2ᵉ et dernier tour) — Test d'étanchéité de livraison

Date : 26 novembre 2026. Vérificateur : Claude (dernier tour). Base : `corrections/C-23.md` (fusion), code corrigé par Hermès.

Méthode : `git diff` entre l'état relu (commit `41053040`, 26/11 16:23, sans les corrections) et `HEAD` ; relecture ciblée des six points ; rejeu de la suite unitaire ; exécution du vérificateur de paquet (désormais possible, voir instr. 5). **Pas de relecture complète.**

La fenêtre de correction va de `dcaf471a` (17:38, première correction) à `0305f516` (HEAD). Les six fichiers du lot changent : `c23.py` (+199), `c23-preparer.py` (+141), `c23-tests.py` (+314), `c23-verifier.py` (refonte 129), `c23-inventaire.php` (+18), et un nouveau `c23-mutations.py` (+91). Aucun code de paywall, thème ou extension n'est touché.

## 1. Les six instructions de `corrections/C-23.md`

| # | Sévérité | État | Preuve (fichier:ligne) |
|---|---|---|---|
| 1 | Bloquant | **Appliquée** | Détection sur le corps brut. `canonical(text, raw=False)` : la branche `raw=True` n'efface plus balises/attributs/commentaires (`c23.py:37`). `assess` cherche chaque témoin dans la vue normalisée **et** dans le brut : `found = [w for w in witnesses if canonical(w) in text or canonical(w, raw=True) in raw]` (`c23.py:42-43`). Régression par support ajoutée : `og:description`, `twitter:description`, `meta name=description`, `data-*`, commentaire `<!-- -->`, chacun avec surface valide → `leak=True`, `ok=False`, et la version propre → `ok=True` (`c23-tests.py:22-34`), plus les mêmes supports injectés dans le corps de recherche (`c23-tests.py:352-356`). Exclusion des termes réfléchis conservée (`search_results_body`, `c23.py:50-72`). |
| 2 | Important | **Appliquée** | Inspection de chaque réponse intermédiaire avant de suivre. `DemoRedirect.redirect_request` renvoie `None` (suivi manuel borné, `c23.py:82-87`) ; `fetch` boucle, appelle `on_redirect(...)` sur chaque corps **avant** la requête suivante (`c23.py:111-136`, inspection `:128-129`) ; `assess_response` parcourt l'historique et propage `leak`/`ok` (`c23.py:97-108`, boucle `:101-106`), expose `redirects_inspected`. Refus hors démo conservé (`c23.py:85-86`, `:133-134`). Test chaîne 302→200, témoin dans le **premier** corps → `leak=True`, `ok=False`, `redirects_inspected=1` (`c23-tests.py:42-82`). |
| 3 | Important | **Appliquée** | Plus de réécriture de la politique de découverte au rejeu normal. `validate_discovery` accepte une politique livrée « fermée », sinon exige le personnage épuisé **durablement préparé** et **refuse** un prérequis incompatible, sans rien forcer (`c23-preparer.py:81-92`). `update_option` n'existe plus que derrière `if mutation or discovery_recipe` (`c23-preparer.py:171-174`) ; le rejeu normal valide avant toute écriture (`:177`). Tests : pas d'`update_option` en normal, une seule écriture de sessions (`c23-tests.py:116-128`), refus avant session (`:130-141`), fermée livrée acceptée + public renommé (`:100-114`). Confirmé côté reçu : `delivery_no_forced_policy=true`. |
| 4 | Mineur | **Appliquée** | Première régression renforcée : surface présente (`present='titre'`), puis `surface_present` **et** `leak=True` **et** `ok=False`, et un cas même surface sans témoin qui passe (`c23-tests.py:10-20`). |
| 5 | Mineur | **Appliquée** | Le vérificateur n'écrit plus dans `production/`. `verify()` fait `print(json.dumps(...))` et renvoie un booléen (`c23-verifier.py:105-106`) ; aucun `write_text`. Test : `write_text` patché pour lever, sortie lue sur stdout (`c23-tests.py:151-161`). J'ai pu l'exécuter en lecture seule (voir §2). |
| 6 | Mineur | **Appliquée** | SHA natif dérivé de l'état, plus figé en dur. `business_original_exact(state, *receipts)` calcule `sha256(json(state))` et compare `native_before == native_after == attendu` (`c23-verifier.py:17-21`, appelé `:59`). Test : deux états fictifs distincts acceptés, dérive refusée (`c23-tests.py:175-183`). Plus aucune constante `4d81b43e…`. |

**Six sur six appliquées.**

## 2. Tests

- **Suite unitaire du lot** (`python -B wp/tests/demo/c23-tests.py`) : **31/31 OK** lorsque `TMPDIR` est défini (comme dans le conteneur de rejeu). Sur Windows nu, **1 erreur** : `test_snapshot_prive...` lève `KeyError: 'TMPDIR'` (`c23-tests.py:267`, `os.environ['TMPDIR']`). Purement **environnemental** : le test passe dès que `TMPDIR` est positionné. À noter (robustesse mineure) : ligne 267 `os.environ['TMPDIR']` (dur) alors que ligne 299 `os.environ.get('TMPDIR')` (souple) — incohérence sans effet dans le conteneur.
- **Vérificateur de paquet** (`python -B wp/tests/demo/c23-verifier.py`), désormais exécutable par le relecteur **grâce à l'instr. 5** (lecture de `production/`, sortie sur stdout, aucune écriture) : **74/74 contrôles, `failures: []`**. Détail des reçus liés au hash de la source courante (`*_source=true`, `command_sha256` concordant) :
  - livraison (`livraison-arbitrage1930`) : 1922 contrôles, **0 fuite** — PASS ;
  - B06 (`b06-arbitrage1930`) : 503 contrôles, 0 fuite — PASS ;
  - mutation (`mutation-arbitrage1930`) : 1922 contrôles, **177 fuites, 205 échecs** — FAIL **attendu** (rouge), `article × anonyme` fuit, code 1 ;
  - découverte ouverte épuisée (`decouverte-ouverte-arbitrage1930`) : 1922 contrôles, 0 fuite — PASS.
  - Transverses verts : `main_GET_only`, `no_session_dump`, restaurations exactes, `delivery_no_forced_policy`.
- **Portée de ce vert** : le vérificateur recoupe la **cohérence interne** des reçus et les **lie au code courant** ; c'est un vrai progrès vs le 1ᵉʳ tour (où il écrivait dans `production/` et n'était pas rejouable). La **matrice HTTP live** (site `192.168.129.32:8085`) reste, elle, non reproductible hors ligne — limite inhérente assumée au brief (hébergement).
- **Rejeu PHP conteneur** : non relancé ; comme établi au 1ᵉʳ tour, il n'exerce pas C-23 (outillage Python).

L'« Important (c) » de la fusion (preuve live non reproductible / vérificateur écrivant dans `production/`) est donc **nettement atténué** : le vérificateur est maintenant rejoué, vert, par le relecteur.

## 3. Régression ou modification non demandée

- **Aucune régression** sur les six comportements corrigés : tous verts, aucune détection affaiblie.
- **Modification non demandée (à signaler) — couverture B06 « coopérateurs ».** Ajoutée pendant la fenêtre de correction (`cooperator_routes` à 17:43, inventaire à 17:48), **absente de la version relue** et **hors des six instructions**. Elle introduit : `cooperator_routes`/`assess_cooperator` (`c23.py:139-193`), l'inventaire des 5 pages coopérateurs et de leurs publics (`c23-inventaire.php:74-92`), `seed_cooperator_witness`/`restore_cooperator` écrits-puis-restaurés hors commande GET (`c23-preparer.py:130-143`), et une nouvelle recette `c23-mutations.py`.
  - **Dans l'esprit du brief** : il demande « l'inventaire des sorties ajoutées depuis C-08 » et les pages coopérateurs (B06) en sont une. La couverture est **plus complète**, entièrement testée et vérifiée verte (503 contrôles B06, 0 fuite).
  - **Mais** : cette fonctionnalité nouvelle n'a **pas** reçu les **deux relectures indépendantes** qu'exige la doctrine §6 pour clore du code. Elle est entrée par un tour censé être une pure correction.
- Robustesse mineure déjà notée : dépendance dure à `TMPDIR` dans un test (`c23-tests.py:267`).

## 4. Verdict : **Remonte à Ced**

Non pour un défaut des corrections : **les six sont correctement appliquées**, sans régression, et le paquet est **vert de bout en bout**, vérificateur indépendant inclus (74/74). La remontée porte sur un seul point de fond :

> Une couverture fonctionnelle substantielle (étanchéité des pages coopérateurs B06, ~500 contrôles + ~400 lignes) a été **ajoutée pendant le tour de correction**, hors des six instructions et hors de la version relue. Elle est alignée sur le brief, testée et vérifiée verte, mais n'a pas eu les **deux relectures indépendantes** de la doctrine §6.

**Décision pour Ced** : clore le lot tel quel en actant cette couverture B06 comme renfort brief-aligné déjà vert, **ou** commander une courte relecture ciblée des seuls ajouts B06 (`cooperator_routes`/`assess_cooperator`, `c23-inventaire.php:74-92`, `seed/restore_cooperator`, `c23-mutations.py`) avant clôture. Question fermée, défaut prudent proposé : **relecture ciblée B06 avant clôture**.

**Rappel : un verdict de vérification n'est jamais un GO.**
