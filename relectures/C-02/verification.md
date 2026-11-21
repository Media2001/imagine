# Vérification — Lot C-02 (numéro d'entreprise), 2e et dernier tour

Vérificateur : Claude. Date : 21/11/2026.
Base comparée : version relue (commit `6638c9b`, fusion `corrections/C-02.md`) → état courant (`HEAD`).
Méthode : `git diff` sur `wp/` et `production/C-02`, lecture du code et des preuves,
contrôle de cohérence par empreintes SHA-256. Pas de relecture complète refaite.

## 1. Suivi des instructions de `corrections/C-02.md`

| # | Instruction | Statut | Preuve (fichier:ligne) |
|---|---|---|---|
| 1 | Rejouer la suite Entreprise dans le runner jetable, journal frais, confirmer 41 tests sans échec | **Appliquée** | `production/C-02/tests-21nov/final.xml:180` (Entreprise `tests="41"`, `failures="0"`) ; `final.log:12` (`OK 175 tests, 19912 assertions`) ; `artifact-verification.json` (status PASS) |
| 2 | Compléter l'annexe BCE/VIES **ou, à défaut, faire acter le report par Ced** | **Appliquée (branche « à défaut »)** | Report acté par Ced : `docs/arbitrages-2026-11-21.md:19` (« Reportée… l'instruction n'est pas à appliquer »). Tracé dans `production/C-02/notes.md:112`. Aucun appel réseau ajouté. |
| 3 | Ajouter une assertion littérale `0123.456.749` sur le format d'affichage | **Appliquée** | `wp/plugins/imagine-pilotage/tests/Entreprise/NumeroEntrepriseTest.php:132` : `self::assertSame('0123.456.749', $resultat->affichage());`. Base `01234567` → clé 49 vérifiée à la main, indépendante de la formule `substr()` de la ligne 130. |
| 4 | Documenter la comparaison « standard d'abord » face aux extensions A-00 | **Appliquée** | `production/C-02/notes.md:114-119` : confrontation aux besoins A-00 (WooCommerce/Subscriptions, Memberships/Teams, Stripe/PayPal, Rank Math/Event Tickets), absences marquées « doute ». Livrable cité présent : `production/A-00/couverture-extensions.md`. |
| 5 | (Optionnel, cosmétique) Séparer dénomination vide et mal encodée dans `ResultatRecherche` | **Non appliquée (optionnelle, report assumé)** | `src/Entreprise/ResultatRecherche.php` inchangé (SHA-256 identique à la preuve). Report motivé : `production/C-02/notes.md:112` (préservation des sources déjà vérifiées par C-04, aucun défaut fonctionnel). |

Arbitrages Ced également respectés :
- Q2 `PremierChiffre` « accepté tel quel » (`arbitrages-2026-11-21.md:20`) → motif conservé, contrôle maintenu.
- Q3 recherche en ligne « contrôle local seul » (`arbitrages-2026-11-21.md:21`) → aucun service activé.

## 2. Résultat des tests

Je **n'ai pas pu relancer** la suite de façon indépendante : `php`, `composer` et
`docker` sont refusés par l'environnement et aucun `vendor/` n'est présent. Même
limite qu'au 1er tour (relectures `claude.md`/`codex.md`).

À défaut, j'ai vérifié que les preuves fraîches portent bien sur le code **courant**
(et non sur une version antérieure). Les empreintes SHA-256 des fichiers livrés dans
`production/C-02/tests-21nov/final.json` et `artifact-verification.json` correspondent
exactement aux fichiers du dépôt :

- `tests/Entreprise/NumeroEntrepriseTest.php` → `8335abf…` (contient l'assertion de l'instruction 3).
- `src/Entreprise/NumeroEntreprise.php` → `50a5715…`
- `src/Entreprise/Motif.php` → `34f7a65…`
- `src/Entreprise/ResultatRecherche.php` → `7a2a4e3…`

Le rejeu couvre donc le code corrigé, assertion comprise.

Chiffres attestés (conteneur jetable, PHP 8.2.36, PHPUnit 11.5.58) :
- Suite complète : **175 tests / 19 912 assertions, 0 échec** (`final.log:12`, `final.xml:3`).
- Suite Entreprise : **41 tests / 19 561 assertions, 0 échec** (`final.xml:180`).
- `exit_code` 0, PSR-12 0, syntaxe 0, `composer validate` 0 (`final.json:4-8`).
- Isolation : `network_disconnected`, `no_mounts`, `no_ports`, base/WordPress « none » (`final.json:59-61`, `preparation.json`).

Cohérence confirmée ; relance indépendante à prévoir côté Ced si une preuve d'exécution par un tiers est requise.

## 3. Régressions et modifications non demandées (périmètre C-02)

- **Aucune régression ni modification non demandée dans le périmètre C-02.**
  Le code source `src/Entreprise/` est **inchangé** (SHA-256 identiques) : la correction
  s'est limitée à une assertion de test et à de la documentation.
- Diff C-02 depuis la version relue : 1 ligne ajoutée au test (instruction 3),
  ajouts documentaires dans `notes.md`, mise à jour de `PRET` et dépôt des preuves
  `tests-21nov/`. Rien d'autre.
- Les autres changements `wp/` présents dans le même intervalle de commits
  (connecteur, Robots, `staging-court`, A-01) relèvent d'**autres lots** et sont
  hors du périmètre de cette vérification.

## 4. Verdict

**Prêt pour la validation de Ced.**

Toutes les instructions applicables sont appliquées ; la seule instruction non
exécutée (n° 2, annexe documentaire) l'est par **décision explicite de Ced**
(report acté), et l'instruction 5 était optionnelle et reportée sans défaut
fonctionnel. Aucun défaut de fond ne subsiste, aucune régression. Le code reste
inchangé et les preuves fraîches portent sur l'état courant.

Rappel : ce verdict n'est pas un GO. Il n'autorise ni déploiement, ni branchement
WooCommerce → Odoo, ni activation d'un service. La décision 8 (recherche en ligne)
et la recette de bout en bout R-06 restent ouvertes pour un lot ultérieur.
