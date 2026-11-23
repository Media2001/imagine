# Vérification B-00 — 2e et dernier tour

Date : 23/11/2026. Vérificateur : Claude (relecteur indépendant). Ce n'est pas un GO (doctrine §6).

Périmètre : contrôle que chaque instruction de `corrections/B-00.md` §4 a été appliquée par Hermès, rejeu des tests, détection de régression. Pas de relecture complète refaite.

Base de comparaison : commit `3bf7dae` (synchro 15:43, celui qui porte `corrections/B-00.md`) → `HEAD`. `git diff` lu sur `wp/` et `production/B-00/`. Arbitrages de Ced lus dans `docs/arbitrages-2026-11-23.md` (les trois questions fermées du §5 sont tranchées).

---

## 1. Instructions de `corrections/B-00.md` §4

### 1 — B00-01 : recette robuste au site augmenté (bloquant) — **Appliquée**
- `wp/tests/demo/b00-recette.php:39` : le comptage des articles est désormais filtré par `meta_query` exigeant `imagine_demo_key EXISTS` en plus de `imagine_numero_id`. Les cardinalités `quatre_articles` (`:40`) et `trois_reserves` (`:42`) ne portent que sur les objets B-00.
- `b00-recette.php:53` : événements et partenaires filtrés par `meta_key => 'imagine_demo_key'`.
- Cohérent avec le seed C08 : `wp/outils/demo/c08-seed.php:95` rattache ses deux articles au numéro T1 avec `imagine_c08_fixture` (jamais `imagine_demo_key`) et `post_password => ''` (`:93`). Le filtre les exclut : le sommaire porte six articles, la recette n'en exige que ses quatre. Conforme à l'arbitrage Ced §5 Q1 (« rejouable sur le site augmenté : oui »).
- Test de reconstruction après seed C08 ajouté : `wp/tests/demo/b00-integre.py --rejouer` (nouveau fichier) appelle le vrai seed C08 puis relance le CLI. Preuve jointe par Hermès : `production/B-00/tests/b00-post-c08-reconstruction.txt` (tous les steps, dont `recette-runtime`, `autres-lots-avant/apres`, `conservation-c08-c09-c10`, à OK).

### 2 — I-1 : recette HTTP et autorisation par mot de passe — **Appliquée**
- `wp/tests/demo/b00-verifier.py` : l'ancienne assertion `article_complet_avec_secret_fictif` est remplacée par deux assertions :
  - `ancien_password_ne_donne_aucun_droit_c08` (`:100`) : avec le cookie du mot de passe natif, le corps réservé n'est **pas** restitué et le bloc de connexion C08 est présent (refus du simple mot de passe).
  - `compte_c08_actif_lit_article_b00` (`:107`) : un compte fictif C08 `actif` authentifié lit bien le corps complet (parcours positif).
- Libellés alignés sur le thème `imagine` : « Sommaire » au lieu de « Sommaire fictif », marqueur `data-imagine-bloc="connexion"` au lieu de `post_password` (`:73`). Ajout de `_langue_fr` (`:71`).
- Étanchéité multi-voies (REST/flux/recherche/oEmbed) retirée de B-00 et confiée à C08 (`:84`), conforme à l'arbitrage §5 Q2.
- Preuves HTTP régénérées sur l'état actuel : `production/B-00/http/*.html` et `*.json` réécrits (git diff le confirme), `b00-verification-http-idempotence.json` régénéré.

### 3 — I-1 (livrables) : `A-VOIR.md`, `verification.md`, `notes.md` — **Appliquée**
- `production/B-00/A-VOIR.md` : la phrase du mot de passe est corrigée — l'ancienne clé `article_password` « n'accorde aucun droit », les mots de passe d'article sont retirés dès que C08 est actif, « l'étanchéité appartient entièrement à C08 ». Parcours réel décrit (connexion compte C08 `actif`). Les anciennes preuves « 81/81 » et démos par mot de passe sont explicitement marquées historiques (`historique/avant-corrections-23nov-16h30/`).
- `production/B-00/notes.md` : commandes mises à jour (recette limitée aux clés B00, C08 propriétaire des accès sans mot de passe, politique de reprise résumée).
- `production/B-00/verification.md` (rapport Hermès) : réécrit, section « Retrait de la protection native par mot de passe » et preuves actuelles vs historiques.

### 4 — I-3 : thème dans les livrables — **Appliquée**
- `A-VOIR.md:1` : « thème **`imagine`** actif et langue **`fr_FR`** » ; la mention Twenty Twenty-Five / « B-01 n'existe pas encore » a disparu.
- `verification.md` (Hermès) `:5` : thème `imagine`, `fr_FR` relus.
- Captures `http/*.html` régénérées sous le thème `imagine` (diff massif confirmé). Les captures TT25 déplacées en `historique/`.

### 5 — I-2 : reprise de concurrence — **Appliquée**
- `wp/outils/demo/construire.py` : `retry_busy` (`:63`) distingue mutation (3 reprises à 300 s) et lecture (12 reprises à 5 s) puis **arrêt propre** (plus de traceback brut, plus de boucle infinie, `:70`).
- `request_api` enveloppe systématiquement le transport (`:16`) ; `ensure_site` applique la reprise au **GET initial, au GET de suivi et au POST** via un wrapper unique sans imbrication (`:34`) ; `remote` enveloppe aussi ses mutations (`:97`). Un `StagingBusy` est toujours rattrapé ; `__main__` sort proprement en code 1 sans forçage.
- Tests ajoutés et verts : `test_initial_get_busy_is_retried`, `test_followup_get_busy_does_not_repeat_creation`, `test_exhausted_read_is_bounded_and_handled`, `test_remote_mutation_exhaustion_is_exactly_four_attempts`, `test_remote_mutations_retry_three_times_not_nested`.
- Conforme à l'arbitrage §5 Q3 (reprise 3× pour toute mutation). Nuance : Ced a écrit « une lecture d'état refusée se retente **librement** » ; Hermès a borné les lectures à 12 reprises puis arrêt explicite. Choix d'ingénierie raisonnable (éviter la boucle infinie), à considérer comme un resserrement prudent, pas un écart bloquant.

### 6 — M-2 : traçabilité dans `docs/ecarts.md` — **Appliquée** (par Hermès)
- `docs/ecarts.md:22` : « L'extension `imagine-site` réunit le modèle de contenu provisoire (B-00) et le branchement du paywall (C-08) : B-00 ne se relit plus isolément. » Daté dans le fichier (révision 23/11). Le fusionneur n'y touchait pas ; c'est bien Hermès qui l'a écrit.

### 7 — Rejeu réel sur le banc autorisé — **Appliquée côté Hermès, non reproductible par le vérificateur**
- Le relecteur ne se connecte pas au staging (doctrine §3). Je ne peux donc **pas** rejouer `construire.py`, `b00-verifier.py`, `b00-recette.php`, `b00-integre.py`.
- Preuves jointes par Hermès et cohérentes : `b00-reconstruction.json` (vrai CLI, régénéré), `b00-post-c08-reconstruction.txt` (tous steps OK après seed C08), `b00-c08-seed-reel.txt`, `b00-integre-actuel.txt` (1 059 assertions de suites, 0 échec), `b00-final-verification.json`, `b00-livraison-verifiee.json`. Ce sont des preuves **produites par Hermès**, pas reproduites par moi.

---

## 2. Résultat des tests (rejoués par le vérificateur)

- `python -m unittest discover -s wp/tests/demo -p "test_b00*.py"` → **11/11 OK** (4 construction + 7 corrections). Au moment de la fusion, seuls 4 tests existaient ; les 7 nouveaux couvrent les corrections B00-01 et I-2.
- Suite complète `test_*.py` → **30/31 OK, 1 ERROR**. L'unique échec est `test_b01_theme.test_b01_html_validator_rejects_structural_regressions` : `ModuleNotFoundError: No module named 'html5lib'`. C'est une **dépendance d'environnement manquante** sur un test **B-01**, pas une régression B-00. Tous les tests B-00 passent.
- Recettes staging (`b00-recette.php`, `b00-verifier.py`, `b00-integre.py`) : non rejouables hors banc ; preuves Hermès au vert (voir §1.7).

## 3. Régressions et modifications non demandées

- **`imagine-site/Paywall.php` : nombreux ajouts au-delà de l'instruction B-00.** La seule correction demandée à B-00 était le retrait du mot de passe natif — présent et correct : filtre `wp_insert_post_data` forçant `post_password=''` sur les `post` (`:345`) et `post_password_required` ne dépendant plus que de la décision C08 (`:351`). Les autres ajouts (masquage SQL de la recherche `searchSql` sur `posts_search`/`posts_orderby` `:285,:334`, mémoïsation de décision à l'échelle de la requête, schéma `NewsArticle`, gardes `metadata_exists`) **ne figurent pas dans `corrections/B-00.md`**. Ils correspondent toutefois aux **arbitrages C08 du 23/11** (`docs/arbitrages-2026-11-23.md:34-36` : recherche interne bloquante §3.9, JSON-LD `NewsArticle`, mémoïsation à l'échelle d'une requête). Ils relèvent donc du cycle de corrections **C08**, pas de B-00 ; à vérifier dans la relecture C08, hors de ce rapport. Aucun impact négatif constaté sur les tests B-00.
- **`imagine-site.php:33` : `NumeroPublication::register()`** ajouté (classe nouvelle) — même remarque, hors instructions B-00, à rattacher à C08/B-01.
- Nombreux fichiers d'autres lots modifiés dans le même intervalle (C09, C10, B01, T01) : hors périmètre B-00, non examinés ici.
- Aucune régression B-00 détectée par lecture ni par les tests B-00.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les six instructions actionnables de `corrections/B-00.md` §4 (B00-01, I-1 recette, I-1 livrables, I-3, I-2, M-2) sont appliquées et citées ci-dessus ; les trois questions fermées du §5 ont été tranchées par Ced et le code reflète ses réponses. Les tests B-00 sont au vert (11/11) ; l'unique échec de la suite est une dépendance d'environnement d'un test B-01 (`html5lib`), étrangère à B-00.

Réserves à la connaissance de Ced, aucune n'étant un problème de fond B-00 :
1. Le rejeu réel des recettes staging (instruction 7) est attesté par les preuves d'Hermès mais **n'a pas pu être reproduit par le vérificateur** (banc interdit, doctrine §3). Si Ced veut une certitude totale, lui seul peut relancer le CLI sur le banc.
2. Les lectures d'état en reprise sont bornées à 12×5 s puis arrêt, là où l'arbitrage disait « librement » : resserrement prudent, à valider implicitement.
3. La relecture du code du paywall enrichi (recherche SQL, mémoïsation, `NewsArticle`) relève de **C08**, pas de B-00 ; elle doit être close dans le lot C08.

Rappel doctrine §6 : ce verdict de vérification n'est pas un GO de production ni une validation visuelle ; il clôt le second tour de relecture du lot de code B-00.
