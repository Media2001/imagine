# Vérification A-17 — 2e et dernier tour

Vérificateur : Claude. Objet : contrôler que les neuf instructions de `corrections/A-17.md` ont été appliquées par Hermès, relancer les tests, relever toute régression. Je ne refais pas une relecture complète.

Méthode : `git diff` entre l'état où la fusion a été écrite (`36894e41`, 06h58) et HEAD, sur `wp/outils/bascule/a17`, `wp/outils/bascule/a11`, `wp/tests/a17` et `production/A-17` ; lecture des reçus régénérés dans `production/A-17/preuves/final` (horodatés 08h04, postérieurs aux corrections).

## 1. Instructions de corrections/A-17.md

| # | Instruction | État | Preuve (fichier:ligne) |
|---|---|---|---|
| 1 | **[bloquant — R5]** Code de refus fixe aux frontières ; ne jamais recopier un chemin/nom arbitraire ; test lien symbolique au nom-canari | **Appliquée** | Corrigé à la racine : `wp/outils/bascule/a11/Runtime.php:21-30` (`refusalMessage` ne renvoie que le code, sauf `A11_DROPIN_UNSUPPORTED` borné à la liste fermée `DROPINS:19`). Symlink et const dénommés : `Runtime.php:39,50,71`. Test : `wp/tests/a17/refusal-common.py` (lien `…CANARY`, const, dropins rejoués sur **6** points d'entrée a11→a17 ; vérifie stdout/stderr/artefacts sans identité). |
| 2 | **[important — R1]** Faire survivre le **nombre** de comptes à mot de passe d'application ; sinon, dès neutralisation détectée, publier « inconnu » et non `0` ; fixture traversant l'import | **Appliquée** | `wp/outils/bascule/a17/Inventory.php:55,76,90,93-95` : marqueur `imagine_staging_disabled_plugins` ⇒ `application_password_accounts = "inconnu après neutralisation"`, jamais `0` déduit. Fixture réelle : `wp/tests/a17/neutralise.php` (exécute `Engine::neutraliser()` puis `anonymiser()`), appelée dans `inside.py:89-106`. Reçu : `classic-neutralisation.json` = before 1 / after 0 ; `classic-neutralised/securite.json` = « inconnu après neutralisation » sur tous les rôles. |
| 3 | **[important — R2]** Compléter les capacités natives de gestion (dont `edit_users`, `update_plugins`, `switch_themes`) ; tests rôle isolé inclus / contenu exclu ; documenter | **Appliquée** | `Inventory.php:13-15` : ajout de `edit_users, update_plugins, switch_themes, delete_plugins, delete_themes, install_themes, update_themes, edit_theme_options, export, import, remove_users`. Tests : `unit.php:16-26` (11 capacités isolées incluses + désactivées exclues + contenu exclu) ; `inside.py:49` rôles `a17_edit_users/update_plugins/switch_themes` comptés, `a17_content_only` exclu. README documenté. |
| 4 | **[important — trou de test]** Cas natif classic+HPOS **sans** `wp-last-login` ⇒ `last_login` « inconnu », compteurs `null` | **Appliquée** | `inside.py:48,69-70,84-85` (env `A17_NO_LAST_LOGIN`) ; reçus `classic-/hpos-no-last-login/securite.json` : `last_login_adapter = "inconnu"`, chaque rôle `{status: inconnu, no_recent_record: null, unknown_accounts == accounts}`. |
| 5 | **[mineur]** Compte **pile** à `2025-11-26T12:00:00Z` non compté `no_recent_record` ; connexion **future** ⇒ `unknown_accounts` | **Appliquée** | `seed.php:25-29` (boundary + future, rôle editor) ; `inside.py:51` : `editor` = `{no_recent_record: 0, unknown_accounts: 2}` (borne non ancienne, future inconnue). |
| 6 | **[mineur — R3]** Coexistence de deux fournisseurs 2FA (un seul pris en charge), classic+HPOS ; mention de couverture | **Appliquée** | Fixture `other-2fa` : `inside.py:30-33`, `seed.php:33-35`. Champ `two_factor_coverage: "supported_adapter_only"` : `Inventory.php:120`. Test `coexisting_2fa_supported_scope_not_global_total` (`inside.py:53`) : 2 protections 2FA actives mais `shop_manager.two_factor_active == 0`. README maj. |
| 7 | **[mineur — R4]** `define(...)` sous conditionnel (syntaxe alternative ou tout contexte non démontré inconditionnel) ⇒ `null`, sans exécuter le fichier | **Appliquée** | `Inventory.php:137-141,165-168` : drapeau `$uncertain` levé par toute structure de contrôle. 7 variantes testées `unit.php:43-58` (`if/foreach/while/switch` alternatifs, `if` inline, `return`, fonction) ⇒ toutes `null`. |
| 8 | **[décision technique]** Préfixe `manage_` : garder inclusif, documenter ; ne remplace pas l'instruction 3 | **Appliquée** | Conservé `Inventory.php:12` ; test `manage_prefix_stays_inclusive` (`unit.php:25`) ; README note `manage_categories` sur-signalé volontairement. |
| 9 | **[décision technique]** `modify('-12 months')` un 29 février : laisser, documenter la bascule au 1er mars | **Appliquée** | README documenté ; test `leap_day_calendar_convention` (`unit.php:60`) : `2024-02-29 → 2023-03-01`. |

**Question « À arbitrer par Ced » (R1, touchant au réel)** — A-17 tourne-t-il sur la copie avant ou après anonymisation ? Le défaut prudent est désormais codé (instruction 2 : « inconnu après neutralisation »). La question reste ouverte pour Ced, mais le lot ne la bloque pas.

## 2. Résultat des tests

Je **ne peux pas** réexécuter en local : ni `php` ni `docker` sur le NUC (`where.exe` négatif), et `run.py` exige un conteneur Linux + extensions commerciales de staging, hors commande autorisée. Même limite de preuve qu'au 1er tour. Je me suis appuyé sur les reçus régénérés après correction, en vérifiant qu'ils portent sur les **octets courants** du code.

- `production/A-17/preuves/final/unit.json` : exit 0, **42/42** assertions PHP PASS.
- `result.json` : exit 0, **66/66** contrôles natifs (classic + HPOS) PASS — dont les 8 nouveaux (`isolated_management_roles_included_content_excluded`, `exact_boundary_not_old_and_future_unknown`, `coexisting_2fa_supported_scope_not_global_total`, `no_last_login_native_unknown_not_estimated`, `real_neutralisation_erases_application_passwords`, `neutralised_application_passwords_unknown_never_zero`, `neutralised_all_tables_and_files_readonly`).
- `refusal-common/refusal-common.json` : exit 0, **60/60** (6 lots × 10 cas de refus) ; `refusal-runner.json` : exit 0.
- `verification.json` (auto-contrôle Hermès) : exit 0, 38 checks PASS, dont `exact_current_sources` et `common_runtime_executed_current_bytes`.

**Liaison reçus ↔ code courant, revérifiée par moi :**
- sha256 des 14 sources A-17 de `sources.json` = arbre de travail (OK, dont `Inventory.php`, `inside.py`, `refusal-common.py`, `unit.php`, `seed.php`).
- sha256 de `a11/Runtime.php` enregistré dans `refusal-runner.json` = octets courants (`04168d07…`), et les points d'entrée a12/a16/a17 figurent dans le reçu. La correction partagée est donc bien celle qui a été exercée.

Bilan : **tout est au vert**, sur le code effectivement présent à HEAD.

## 3. Régressions / modifications non demandées

- **Correctif R5 porté dans `a11/Runtime.php` (runtime partagé par a11, a12, a14, a15, a16, a17, a18).** C'est le bon niveau — il ferme la fuite pour **tous** les points d'entrée — et l'instruction 1 visait explicitement `Runtime.php:59-61`. Ce n'est donc pas une modification non demandée. Les READMEs a11 et a12 sont mis à jour pour décrire le nouveau contrat de refus confidentiel (cohérence documentaire, pas de code).
- **Pas de régression détectée sur les lots voisins.** Les attentes de test à HEAD des autres lots sont déjà alignées sur la sortie à code fixe : `a11/inside.py:140,147`, `a12/inside.py:186,208` attendent `A11_SYMLINK_UNSUPPORTED\n` / `A11_CONFIG_OVERRIDE_UNSUPPORTED\n` **sans nom** ; les cas `dropin` (liste fermée) restent nommés partout (`a11/a14/a15/a16/a18`, `a17/inside.py:86`). `refusal-common.py` rejoue réellement a11→a17 et confirme ces sorties exactes (vert). `a11/unit.php:34` contrôle le code d'exception inchangé.
- **Point à surveiller (hors périmètre A-17, non bloquant) :** a14/a15/a16 sont déjà clos ; leurs **reçus livrés** ont été produits avant ce durcissement du runtime partagé. Leur **code de test** est déjà aligné, donc pas de régression de code, mais leurs paquets de preuves gagneraient à être rejoués pour rester datés du runtime courant. À noter pour Ced ; cela ne relève pas de la clôture d'A-17.
- Les fichiers modifiés non commités hors A-17 (git status : `a18/Forms.php`, `a18/Inventory.php`, `a18/inside.py`, `a18/unit.php`) relèvent du lot A-18 en cours (voie 1), pas d'A-17.
- Aucune modification A-17 hors des neuf instructions.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les neuf instructions sont appliquées, documentées et couvertes par des tests ; les reçus régénérés sont au vert et liés aux octets courants (A-17 + runtime partagé). Le bloquant R5 est corrigé à la racine et prouvé sur les 6 points d'entrée. Aucun problème de fond ne subsiste.

Reste pour Ced, non bloquant pour le code :
1. La question fermée R1 (copie avant/après anonymisation) — défaut prudent déjà codé.
2. Décider si les paquets de preuves d'A-14/A-15/A-16 doivent être rejoués suite au changement du runtime partagé.

**Rappel doctrine : ce verdict n'est pas un GO au sens du §3.**
