# Vérification A-14 — second et dernier tour

Lot : A-14, rapprochement d'un export de contacts.
Base relue : commit `0680e355` (écriture de la fusion). Corrections appliquées par Hermès ensuite.
Méthode : `git diff 0680e355 HEAD` sur `wp/outils/bascule/a14/`, `wp/tests/a14/` et `production/A-14/` ; relecture des artefacts livrés ; relance des tests disponibles en local.
Périmètre : contrôle des quatre instructions de `corrections/A-14.md`, pas une relecture complète.

## 1. Instructions de corrections/A-14.md

**Instruction 1 — `resume.md` en français — Appliquée.**
`wp/outils/bascule/a14/command.php:77-100` : le titre et la phrase d'en-tête passent par `__(…, 'imagine')` ; une table `$labels` traduit chaque clé, et la boucle imprime `$labels[$name]` au lieu de la clé brute. `resume.json` et les clés techniques sont inchangés (vérifié : partition identique). Preuve livrée `production/A-14/preuves/final/classic-contacts/resume.md` : entièrement en français, plus aucune clé machine (`contacts_total` etc.) dans le texte lisible.

**Instruction 2 — documenter le choix SQL vs API native — Appliquée.**
`wp/outils/bascule/a14/README.md` : nouveau paragraphe « Standard d'abord : pourquoi cette projection SQL ». Il nomme les API natives examinées (`wcs_get_users_subscriptions`, `wcs_user_has_subscription`, `WC_Subscription`), donne deux références officielles (Subscriptions Core Automattic ; doc WooCommerce), et justifie le SQL direct par le contexte lecture seule / base clôturée, en précisant que c'est un choix et non une nécessité. La stratégie de collecte est **conservée** : `Accounts.php` et `Matcher.php` sont inchangés depuis la version relue (diff vide). Conforme au défaut arbitré.

**Instruction 3 — compléter les tests (3 cas, valeurs en dur) — Appliquée.**
`wp/tests/a14/seed.php` : `bob` passe de `cancelled` à `pending-cancel` ; un second abonnement `active` est ajouté sur `alice` (compte multi-abonnements) ; un compte `fictif@sans-email.imagine.invalid` sans marqueur `imagine_sans_email` est créé. L'oracle natif expose `branches` (pending_cancel, alice_active_count=2, reserved_domain_marker=false).
`wp/tests/a14/inside.py` ajoute trois contrôles à valeurs en dur :
- `pending_cancel_explicitly_not_active` : ligne 2 → `abonnement_actif = non` ;
- `reserved_domain_without_marker_excluded` : `contacts_without_account == 1`, lignes `['2','4']` ;
- `two_active_subscriptions_one_account` : `contacts_with_account == 2`, compté une fois.
`wp/tests/a14/verify.py` ajoute `*_fusion_required_cases` qui **exige** la présence de ces trois cas plus le libellé français dans le paquet scellé. Les trois cas passent sur `classic` et `hpos` (voir §2).

**Instruction 4 — clarté du comptage par ligne — Appliquée.**
`command.php:81-83` ajoute à `resume.md` une phrase : contacts comptés « par ligne source, pas par personne distincte », et renvoie à `duplicate_contact_lines`. Confirmé dans le `resume.md` livré. Le calcul n'a pas changé (partition et doublons identiques).

## 2. Résultat des tests

- **`verify.py` sur le paquet scellé** (`production/A-14/preuves/final`) : **15/15 PASS** (contre 13/13 au premier tour ; ajout de `classic_fusion_required_cases` et `hpos_fusion_required_cases`). `exit_code = 0`.
- **Banc natif en conteneur** (`result.json`) : **63/63 PASS**, 0 échec. Y compris, sur `classic` et `hpos` : `native_oracle`, `exact_counts`, `french_summary_and_source_line_convention`, `pending_cancel_explicitly_not_active`, `reserved_domain_without_marker_excluded`, `two_active_subscriptions_one_account`.
- Partition vérifiée : `contacts_total 30 = 4 avec compte + 23 sans compte + 1 ambiguë + 2 invalides`. Idempotence : `*_repeat` identiques.
- `PRET` indique un rejeu sous Python 3.14 UTF-8 **et** cp1252/`PYTHONUTF8=0`, les deux verts.

Réserve de méthode, inchangée depuis la fusion : la suite Docker/native propre n'est **pas rejouable** ici (pas de Docker, dépôt en lecture seule). La vérification s'appuie sur le paquet scellé livré par Hermès et sur `verify.py`, comme Codex au premier tour. Je n'ai pas régénéré le paquet.

## 3. Régressions ou modifications non demandées

- **Aucune régression fonctionnelle sur A-14.** Les quatre instructions sont tenues sans effet de bord sur les calculs ; `Accounts.php` et `Matcher.php` sont intacts.
- **Modification cosmétique mineure non demandée** : le titre de `resume.md` passe de « # Rapprochement **fictif** — lecture seule » à « # Rapprochement — lecture seule » (le mot « fictif » disparaît). Bénin, sans impact sur les données ni les compteurs. À signaler seulement ; ce n'est pas un défaut.
- **Hors périmètre A-14, rappel de la fusion** : la suite globale T01 (`TableauBordReglesTest`, extension `imagine-site`) restait rouge. Elle n'appartient pas à A-14 et n'a pas été rejouée ici. `imagine-site` a reçu entre-temps de nouveaux fichiers (`Renouvellement*`, lot distinct) non relus. Ce point **bloque toujours une clôture globale** mais pas la validation d'A-14.

## 4. Verdict

**Prêt pour la validation de Ced** (lot A-14).

Les quatre corrections de la fusion sont appliquées et prouvées, tests au vert (15/15 scellé, 63/63 banc), aucun défaut de fond restant propre à A-14. La seule modification non demandée est cosmétique et bénigne.

Rappel doctrine §3/§6 : ce verdict vaut pour la clôture du lot de code A-14, jamais pour un accès au réel. La clôture **globale** reste suspendue au T01 rouge de `imagine-site`, à traiter dans son propre lot.
