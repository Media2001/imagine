# Vérification A-15 — second et dernier tour

Vérificateur : Claude. Date : 26/11/2026.
Objet : contrôler que les corrections de `corrections/A-15.md` (fusion, verdict « À corriger ») ont été appliquées par Hermès, relancer les tests, repérer toute régression. **Pas de relecture complète refaite.**

Version relue (point de départ) : commit `b708d1a7` (26/11 05:53), celui où `relectures/A-15/claude.md` a été écrit. Diff examiné : `git diff b708d1a7 -- wp/ production/A-15`.

## 1. Instructions de `corrections/A-15.md` — application

Les quatre instructions de fusion (§4) plus la décision technique.

### I1 — couvrir les variantes natives d'objet et de titre — **Appliquée**
- `wp/outils/bascule/a15/Inventory.php:35-50` : la détection ne lit plus `subject`/`heading` en dur. Elle parcourt `get_form_fields()`, retient toute clé `subject`/`heading` avec suffixe optionnel (`subject_full`, `subject_partial`, `subject_paid`, `heading_partial`…), compare chaque variante à son propre défaut (`placeholder` de repli, `get_default_*` pour les clés de base), et agrège en un seul `subject_customised` / `content_customised`. Aucun texte exporté (seulement des drapeaux, cf. `:82-91`).
- Tests ajoutés : `wp/tests/a15/unit.php:88,92,95` (`declared_variants_only_modified`, `declared_variants_own_defaults`, `declared_empty_variants_native_fallback`) ; oracle indépendant `wp/tests/a15/oracle.php:20-35` (5 modes × 2 emails) ; graine réelle remboursement/facture `wp/tests/a15/seed.php:26-42` ; banc `wp/tests/a15/inside.py` (`collected_refund_variant_and_invoice_default`).

### I2 — inventorier aussi les gabarits communs surchargés — **Appliquée**
- `Inventory.php:113-124` : `overrides()` construit une table des gabarits propres **et** communs (`emails/email-header.php`, `email-footer.php`, `email-styles.php`), ajoutés seulement si `template_html` existe et que l'email n'est pas `plain`. Résolution par `wc_locate_template` avec le bon chemin de défaut (`:125-141`), enfant avant parent, et comptage une seule fois par chemin (`array_unique`, `:142-143` ; `collect()` dédoublonne aussi dans `summary.overridden_template_files`, `:245-256`).
- Tests : `wp/tests/a15/inside.py` — `exact_theme_override` passe à 4 fichiers attendus, nouveaux cas `common_templates_alone_counted_once_child_priority` (le fichier propre masqué → 3 communs comptés une fois, priorité enfant) et `common_template_parent_fallback` (fichier enfant retiré → repli effectif sur le parent). `wp/tests/a15/verify.py:39` ajoute ces cas à la liste obligatoire.

### M1 — comparer le destinataire au défaut natif — **Appliquée**
- `Inventory.php:58-78` : `recipient`/`cc`/`bcc` ne sont plus « personnalisés » dès qu'ils sont non vides. Une normalisation en mémoire (`$list` : séparation `,;`/retours, minuscules, espaces retirés, dédoublonnage, tri) compare la destination configurée à son défaut natif ; égal au défaut → non personnalisé ; CC/BCC traités séparément. Aucune adresse exportée.
- Tests : `wp/tests/a15/unit.php:98,101,104` (`saved_default_recipient_list_not_custom`, `different_recipient_custom`, `cc_addition_separate_from_default_recipient`) ; oracle `wp/tests/a15/oracle.php:37-46` (cas `absent`/`saved_default`/`different`/`cc_addition`).

### Preuve — rejeu du banc natif + un seul paquet final — **Appliquée**
- `production/A-15/preuves/final/` régénéré (horodatage 06:25-06:26), paquet unique. Il contient les nouveaux dossiers de cas I2 (`classic-common-only`, `classic-parent-fallback`, idem hpos) et les cas I1/M1 dans `*-oracle.json`. `notes.md` confirme les anciens essais hors dépôt.

### Décision technique (transport déclaré par un thème) — **Appliquée (défaut conservé)**
- Aucun changement de `transports()` : les thèmes restent non listés comme transports, conformément au défaut proposé. Confirmé par `production/A-15/notes.md:9`.

## 2. Résultat des tests

Relancés par moi, sans Docker (seuls tests exécutables avec la commande autorisée en l'état) :

- **`python wp/tests/a15/test_contract.py`** → **2/2 OK** (A-15 ne possède que ses deux lignes de documentation partagée).
- **`python wp/tests/a15/verify.py production/A-15/preuves/final`** → **25 PASS, `exit_code=0`**. Ce vérificateur indépendant revalide : `unit_actual_green` (14 assertions PHP), `result_actual_green` (banc natif), `runner_actual_green` (gardes), `classic_mandatory_cases` **et** `hpos_mandatory_cases` incluant les 4 nouveaux contrôles obligatoires (I1/I2/M1), `canary_absent_from_entire_packet`, `strict_psr12_final_sources`, contrat documentaire. Noms d'assertions uniques.

Preuves commitées, lues et cohérentes avec les corrections :
- `preuves/final/unit.json` : **14/14 PASS**, `exit_code=0` (dont les 6 nouvelles assertions I1/M1).
- `preuves/final/result.json` : **tout PASS**, `exit_code=0`, `no_real_site=true`, classic + HPOS. Présents et verts : `native_variants_defaults_empty_and_recipient_defaults`, `collected_refund_variant_and_invoice_default`, `common_templates_alone_counted_once_child_priority`, `common_template_parent_fallback`. Empreintes base et fichiers identiques avant/après ; transaction READ ONLY tenue même root.

**Réserve de méthode (inchangée, importante, non bloquante).** Le banc natif A-15 (`run.py`) exige Docker **et** les extensions commerciales sous licence ; il n'est pas ré-exécutable indépendamment, exactement comme au premier tour (déjà reporté à Ced). Mon `verify.py` valide l'intégrité du paquet commité (checks verts, uniques, sans canari, liste obligatoire complète), il ne rejoue pas lui-même WooCommerce. La suite PHP générale (`rejouer.ps1`, 1088 tests) n'a pas été relancée ce tour (gate de permission dans cette session non interactive) ; elle ne couvre de toute façon pas A-15 et était verte à la relecture.

## 3. Régressions ou modifications non demandées

- **Dans le périmètre A-15 : aucune.** Les changements sont exactement I1/I2/M1, leurs tests, le paquet de preuves régénéré, et les mises à jour de `README.md`/`notes.md`/`PRET` qui les décrivent. `a15/README.md` documente fidèlement les trois corrections (variantes déclarées, recipient/CC/BCC comparés au défaut, gabarits communs comptés une fois, texte strict non concerné par l'HTML).
- **`wp/tests/a02-audit/README.md`** : les deux lignes ajoutées sont celles d'**A-17**, pas d'A-15 ; les deux lignes propres à A-15 sont inchangées (confirmé par `test_contract.py`).
- **Hors périmètre A-15** : le diff global touche aussi a14, a17, c20 (démo), `imagine-site` (Renouvellement), etc. Ce sont des lots travaillés en parallèle, hors de cette vérification ; non examinés ici.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les trois défauts de la fusion (I1, I2, M1) sont corrigés dans le code et couverts par de nouveaux tests ; la décision technique est appliquée au défaut retenu. Les tests que j'ai pu relancer sont verts (`test_contract.py` 2/2, `verify.py` 25 PASS), et le paquet unique commité est intègre et vert sur classic + HPOS, sans fuite. Aucune régression ni modification non demandée dans le périmètre A-15. Aucune question de fond restante côté métier/visuel/réel.

Point à garder en tête pour la clôture (pas un blocage) : la preuve native A-15 repose sur le paquet commité et un rejeu Hermès, pas sur une ré-exécution indépendante du banc Docker ; un rejeu `run.py` côté Ced reste la seule preuve pleinement indépendante si on la veut.

**Un verdict de vérification n'est pas un GO** (doctrine §3/§6) : il ne vaut que pour la clôture de ce lot de code, et n'autorise aucun accès réel, aucun envoi, aucun déploiement.
