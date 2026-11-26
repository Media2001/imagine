# Relecture C-22 — Centre de préférences des newsletters (Claude, relecteur indépendant)

Brief : `briefs/C-22-preferences-newsletters.md`. Cahier des charges : §3.10, §4.2 (relus). Production : `wp/plugins/imagine-site/{Newsletters.php,NewslettersRegles.php,NewslettersReglages.php}`, intégration C-21 dans `Confidentialite.php`, `production/C-22/`.

**`relectures/C-22/codex.md` non lu (consigne respectée). Pas de fusion à ce stade.**

## Rejeu de la suite PHP

Commande autorisée, sans argument : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1` (conteneur jetable, sans réseau, dépôt en lecture seule).

Dernière ligne :

```
REJEU : 1114 tests, 34560 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Image T01 : `sha256:9a95dcbe…ca67dc`. Suite verte. Les cinq tests `NewslettersReglesTest` sont inclus.

## 1. Conformité

Le lot fait ce que demande le brief, ni moins ni plus.

- **Liste = donnée** : option `imagine_newsletters_catalogue`, quatre champs exactement (`id`, `titre`, `presentation`, `principale`), validés par `NewslettersRegles::catalogue()` (`NewslettersRegles.php:31`). Réglage ajouté à l'écran C-10 (`NewslettersReglages.php:97`). Démo : trois lettres fictives, une principale (`production/C-22/catalogue-demo.json`). → §3.10 « Centre de préférences … sans développement ».
- **« Mes newsletters » dans le compte** : `Newsletters::compte()` sur `woocommerce_account_dashboard` (`Newsletters.php:133`), une case par lettre, état daté en UTC. → §4.2 « préférences newsletter », §3.10.
- **Page « Nos newsletters »** : shortcode `imagine_newsletters`, présentation de chaque lettre ; lien vers les préférences pour un connecté admissible ; **emplacement nommé** `#imagine-newsletters-inscription-brevo` pour l'anonyme, sans formulaire actif (`Newsletters.php:177`). → §3.10 « Page Nos newsletters ».
- **Rien ne part** : aucun `wp_mail`, `wp_remote_*`, aucune API. Seul point d'accroche : `do_action('imagine_newsletters_preferences_modifiees', …)` sans écouteur ni transport (`Newsletters.php:72` et `:96`). → §3.10 (double confirmation Brevo repoussée au connecteur).
- **Défaut prudent** : option `imagine_newsletters_creation` = `non` par défaut ; `creation()` sort sans rien écrire (`Newsletters.php:79`). Aucune case cochée tant que le lecteur n'a pas agi. Réglage fermé « inscrire par défaut à la principale » présent et testé pour les deux valeurs.
- **Compte sans email** : `admissible()` exclut `.invalid` et le marqueur `SansEmail::META` ; `compte()` et `page()` affichent une phrase, sans rubrique (`Newsletters.php:32`, `:139`, `:185`).
- **Export / effacement C-21** : `Confidentialite::META` inclut `Newsletters::META` (`Confidentialite.php:10`) → export (`records()`/`exporter()`) et effacement (`retirer()` → `delete_user_meta`). C-21 est rendu : préférences déclarées, pas seulement signalées.
- **Pas d'étiquettes de persona** : aucune n'est produite. Conforme à la réserve du brief.

Interprétations faites et signalées par Hermès (A-VOIR.md), que je confirme comme raisonnables : exactement **une** principale exigée ; une lettre retirée disparaît des écrans mais son état reste exportable ; un identifiant retiré n'est jamais recyclé (consigne d'interface, non contrainte par le code).

## 2. Exactitude métier — cas déroulés à la main

1. **Coche / décoche / recharge, daté (§3.10)** — prefs vides → trois cases décochées, « Aucun choix enregistré ». Coche `lettre-fictive`, enregistre : `choisir()` écrit les trois entrées (`lettre-fictive`=true, les deux autres=false), toutes datées à T, origine `lecteur`. Recharge : case cochée, `Choisi — <time T>`. Décoche à T2 : `lettre-fictive`=false, date T2. **Conforme.**
2. **Intercompte (preuve)** — B poste `compte=IDA` : `traiter()` compare au `get_current_user_id()` courant → `wp_die` 403 (`Newsletters.php:112`). `enregistrer()` redouble la garde `id !== get_current_user_id()` (`:52`). Nonce lié à l'utilisateur. **Un abonné ne modifie pas un autre.**
3. **Quatrième lettre (preuve du « sans développement »)** — admin remplit la dernière ligne ; `nettoyerCatalogue()` valide, le catalogue passe à 4 ; `champs()`, `compte()` et `page()` itèrent `get_option` → la 4e apparaît partout sans toucher au code. Vider l'identifiant → ligne ignorée (`NewslettersReglages.php:61`), retour à 3, l'état historique reste exportable. **Conforme.**
4. **Aucun appel sortant / email (preuve)** — rien dans le parcours n'émet d'email ni d'appel HTTP issu du raccord ; constat cohérent avec `production/C-22/http-final-V2.json` et `native-final-V2.json`.
5. **A-SANSMAIL (preuve)** — `admissible()` false → phrase affichée, pas de case. **Conforme.**
6. **Cas limite — formulaire périmé** — si le catalogue change entre affichage et envoi, `version()` (hash catalogue+préférences) diffère → `hash_equals` échoue → 409 (`Newsletters.php:62`). Comportement voulu, non régressif.
7. **Cas limite — défaut `oui` à la création** — `creation()` n'écrit qu'une fois (`metadata_exists`), origine `defaut_creation`, affichée « pas un consentement explicite » (`Newsletters.php:166`). Ne vaut jamais consentement. **Conforme au défaut prudent.**

## 3. Tests

- Suite PHPUnit verte (voir REJEU). `NewslettersReglesTest` vérifie la **règle** (datation, idempotence, défaut ≠ consentement, identifiant inconnu refusé, doublon refusé, 4e lettre sans code) et non une copie du code.
- **Limite de couverture (observation)** : les tests PHPUnit portent sur la logique pure. Les preuves d'intégration (intercompte HTTP, hooks WordPress, export/effacement C-21, ajout/retrait réels) reposent sur les scripts de démonstration (`c22-http.py`, `c22-runtime.php`, `c22.py`) et leurs `*.json`, **que la commande autorisée ne rejoue pas** et que je n'ai pas exécutés. J'ai vérifié la logique correspondante par lecture ; la vérification dynamique de ces parcours tient aux artefacts fournis par Hermès.

## 4. Sécurité et données

- Nonce `imagine_newsletters_<id>` vérifié, méthode POST imposée, `compte` recoupé à l'utilisateur courant, `version` anti-rejeu, `GET_LOCK` par utilisateur (`Newsletters.php:104-131`, `:56`).
- Sorties échappées (`esc_html`, `esc_attr`, `esc_url`, `checked`, `selected`) partout ; requêtes du journal et de confidentialité préparées.
- Capacité : les deux options sont dans le groupe `imagine_reglages`, couvert par `option_page_capability_imagine_reglages` = `manage_options` (C-10) ; page admin en `manage_options`.
- Aucun secret, aucune donnée réelle : catalogue et comptes manifestement fictifs, adresses hors dépôt.
- Pas de paywall concerné ici.

## 5. Doctrine

- **Standard d'abord** : réglages via Settings API, export/effacement via les outils natifs WordPress (hooks `wp_privacy_personal_data_*`), aucun écran parallèle. Le sur-mesure se limite à ce que l'existant ne fait pas.
- **Conventions §5** : `declare(strict_types=1)`, espace `Imagine\Site`, préfixe `imagine_`, textes FR traduits, aucune modification d'extension tierce. README mis à jour (`imagine-site/README.md`, section « C-22 »).
- **Logique hors WordPress** : `NewslettersRegles` est pur, testable sans base ; `Newsletters`/`NewslettersReglages` sont la couche fine. Conforme.

## Décisions techniques, défaut proposé

Hermès applique le défaut sans attendre ; j'arbitre après coup.

1. **Injection des champs sous le bouton d'enregistrement de C-10.** `champs()` est insérée juste avant `</form>` (`NewslettersReglages.php:37`), donc **après** le bouton « Enregistrer » de C-10. Enregistrement correct (même formulaire), mais ordre visuel inhabituel. *Défaut proposé : conserver* (capture `reglages-newsletters.png` fournie à Ced pour la validation visuelle). Catégorie visuelle → voir aussi « Pour Ced ».
2. **Couplage au rendu de C-10.** L'injection repose sur un `ob_start()` et la détection de `value="imagine_reglages"` + `</form>` dans le HTML de C-10. Si C-10 change son rendu, la section newsletters disparaît **silencieusement** (aucune erreur). L'ordre des priorités (`admin_menu` 10 puis 140) est correct aujourd'hui. *Défaut proposé : conserver, mais garder un test de présence de la section à l'écran C-10* (le parcours `http` le couvre d'après l'A-VOIR ; à maintenir).

## Pour Ced (visuel)

- Vérifier sur `production/C-22/reglages-newsletters.png` que la place de la section Newsletters sous le bouton d'enregistrement de C-10 est acceptable, ou demander son déplacement au-dessus du bouton.

## Pour Imagine (métier)

- **Faut-il inscrire par défaut à la newsletter principale à la création d'un compte, et si oui avec quel consentement explicite recueilli à cet instant ?** *Défaut appliqué : **Non*** (aucune case cochée tant que le lecteur n'a pas agi). La valeur « Oui » existe, testée mais inactive, porte l'origine `defaut_creation` et ne vaut jamais preuve de consentement. Question fermée, isolée derrière le réglage `imagine_newsletters_creation`, conforme à la doctrine « une règle ouverte devient un réglage ».

## Verdict

**Conforme** — le lot répond au brief et aux §3.10 / §4.2, suite verte, intégration C-21 réelle, aucun appel sortant.

- **Bloquant** : aucun.
- **Important** : aucun.
- **Mineur** : (1) champs injectés sous le bouton d'enregistrement de C-10 — visuel, à trancher par Ced ; (2) couplage silencieux de l'injection au rendu de C-10 — décision technique, défaut « conserver » ; (3) couverture PHPUnit limitée à la logique pure, les parcours d'intégration reposant sur des artefacts de démonstration non rejoués par la commande autorisée.

Ce verdict n'est pas un GO. `codex.md` existe : la fusion (`corrections/C-22.md`) reste à écrire dans un second temps ; je m'arrête ici comme demandé.
