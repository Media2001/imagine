# A-02 — Vérification (2ᵉ et dernier tour)

Date : 2026-11-23. Vérificateur : Claude. Objet : contrôle des corrections d'Hermès après fusion `corrections/A-02.md`.

Méthode : `git diff a78e674..HEAD` (version relue = dernière avant corrections) sur `wp/outils/bascule/audit`, `wp/tests/a02-audit/` et `production/A-02/` ; relance des tests. Pas de nouvelle relecture complète.

SHA-256 du script courant `wp/outils/bascule/audit` = `7eb2b4bfa450e37d3f4265e3055cdba61a877b056f4feb0bfce06f681659c6dc` : identique à celui annoncé dans `notes-corrections.md`.

---

## 1. État de chaque instruction de `corrections/A-02.md` §4

**1 — C1, passerelles (héritage indirect + préfiltre).** **Appliquée.**
- Résolution statique des héritages : nouvelle `gatewayInventory()` (`audit:305`) qui tokenise les sources (sans instancier), suit la chaîne `extends` inter-fichiers jusqu'à `WC_Payment_Gateway`/`_CC`/`_eCheck`, et résout les constantes `const ID` héritées.
- Implémentations non résolues signalées : sortie `gateway_unresolved` (`audit:540`), motifs `ancestry_unresolved` / `id_unresolved`.
- Préfiltre `commerce()` corrigé : la boucle collecte désormais toutes les sources `.php` de l'extension sans le test `str_contains('WC_Payment_Gateway')` (`audit:524-531`). La classe concrète qui ne cite pas la classe mère n'est plus écartée.

**2 — C2, abonnements (doublons de métadonnées).** **Appliquée.**
- Nouvelle `subscriptionCounts()` (`audit:440`) : sous-requête `MIN(meta_id)` / `MIN(id)` qui retient une seule ligne par abonnement et par clé **avant** les `LEFT JOIN`, dans les deux branches (classique et HPOS). Plus de produit cartésien.
- Doublons et contradictions comptés à part et exposés : `subscription_meta_anomalies` + `subscription_meta_selection` (`audit:543`), sans valeur ni identifiant d'abonné.

**3 — C3, surcharges Woo (parent masqué par l'enfant).** **Appliquée.**
- Rôles distingués : champ `role` (`stylesheet` / `template`, `audit:257`).
- Priorité résolue par chemin relatif (l'enfant masque le parent) : `childPaths` puis état `effective` / `resolution` = `masked_by_child` conservé pour le parent masqué (`audit:735`).
- Synthèse `outdated` calculée sur les seules surcharges effectivement servies : filtre `$t['effective'] && $t['outdated']` (`audit:785`).

**4 — `posts_by_year` base temporelle.** **Appliquée.**
- Passage à `YEAR(post_date_gmt)` (`audit:607`) **et** étiquette `post_year_basis = UTC_creation` (`audit:609`), aligné sur le commerce.

**5 — Fixtures et preuves.** **Appliquée.**
- (a) passerelle base + concrète en deux fichiers, plus classe sans lien et cas dynamiques : `inside.py:78-81`, unité `unit.php:54-64`.
- (b) abonnement à métadonnées de période dupliquées (identiques puis contradictoires) dans les deux stockages : `inside.py:117-118`.
- (c) thème enfant masquant une surcharge périmée du parent + parent sans équivalent enfant (`checkout/form-checkout.php`) : `inside.py:92-101`, `seed.php:68` (`stylesheet=a02-child`).
- Preuves régénérées sous `production/A-02/preuves/5d09a26acfb8/` ; `verify.py` relancé dans un environnement où Docker/WSL répond (voir §2).

**6 — Documentaire (mineur).** **Appliquée.**
- `production/A-02/sources-officielles.json` enrichi (phrase exacte, position, statut HTTP, SHA-256 par affirmation ; +112 lignes). Ancien reçu conservé dans `sources-officielles-avant-corrections.json`. `test_documentation.py` vérifie la présence des phrases exactes (vert).

**7 — Mineurs à documenter.** **Partiellement appliquée (conforme).**
- Étiquette `custom_fields` : **appliquée**, `custom_fields_scope = all_postmeta_keys_including_internal_core_and_woocommerce; names_and_counts_only` (`audit:610`).
- Sort de `requires_woo` : **non tranché par Hermès** — champ conservé et documenté comme choix propriétaire ouvert (README §Limites, `notes-corrections.md`). Ce n'est pas un défaut de code : c'est une question fermée qui revient à Ced (§5.2 de la fusion).

---

## 2. Résultat des tests

`python wp/tests/a02-audit/verify.py production/A-02/preuves/5d09a26acfb8` → **retour 0, `status: PASS`**.
- **144 assertions** : 17 unité, 120 intégration/qualification, 7 runner.
- `current_source_hashes_match: true` : l'inventaire et les empreintes des sources courantes correspondent au paquet (pas de dérive).
- `container_absent: true`, Docker répondant (contrôle `docker version` passé) : **le doute d'environnement du 1ᵉʳ tour (fusion §3, WSL/Docker inaccessible) est levé**. Rejeu fonctionnel désormais confirmé.
- `database_fingerprints_equal: [classic, hpos]` : empreintes logiques avant/après identiques dans les deux stockages.

Le vérificateur assertionne maintenant les valeurs corrigées elles-mêmes (`gateway_cross_file`, `gateway_unresolved`, `subscription_first_meta_deterministic`, `subscription_duplicate_conflict_notices`, `child_masks_parent`, `parent_fallback_effective`, `effective_template_risk_count`, `theme_roles`, `posts_utc_year_boundary`) : le PASS prouve réellement les correctifs, pas seulement leur présence.

`python -m unittest test_documentation` → **OK** (1 test, phrases exactes présentes).

PHPCS PSR-12 (hors replay fonctionnel) : 0 erreur, 98 avertissements, retour 1, déclaré honnêtement dans `style/` — n'est pas présenté comme vert et ne fait pas partie des 144 assertions.

---

## 3. Régressions ou modifications non demandées

- **Périmètre propre.** Hors `production/A-02/preuves/`, seuls ont changé : `wp/outils/bascule/audit` et `wp/tests/a02-audit/{README.md, documentation.py, inside.py, seed.php, style.py, test_documentation.py, unit.php, verify.py}`. Aucun `docs/`, `doctrine/`, autre code `wp/`, ni autre lot touché.
- Les ajouts de sortie (`role`, `gateway_unresolved`, `subscription_meta_anomalies`, `subscription_meta_selection`, `post_year_basis`, `custom_fields_scope`, `effective`/`resolution`) correspondent tous à une instruction de la fusion : **aucune fonctionnalité non demandée**.
- `orders_by_year` (déjà en UTC) est inchangé. Aucune régression observée.
- Point d'archivage, sans gravité et déclaré par Hermès : la première réexécution du runner de style a écrasé les anciens `style/phpcs.json` / `style/receipt.json` (ancien comportement d'écrasement), d'où le passage 99→98 avertissements et la perte du stdout détaillé antérieur. Signalé dans `notes-corrections.md` §Limites ; ne touche ni le code livré ni les 144 assertions.

---

## 4. Verdict

**Prêt pour la validation de Ced.**

Les trois défauts importants (C1, C2, C3) et les points mineurs 4 et 6 sont corrigés et prouvés par des assertions adverses ; le rejeu fonctionnel complet (`verify.py`, Docker) est maintenant confirmé dans un environnement autorisé. Aucun problème de fond ne reste côté code.

Restent deux arbitrages **métier/propriétaire** pour Ced, explicitement ouverts et non bloquants (fusion §5) : (1) extension éventuelle du registre d'attribution des tables avant l'audit réel ; (2) conservation ou retrait de `requires_woo`. Ce sont des décisions de Ced, pas des corrections manquantes.

**Rappel : ce verdict n'est pas un GO.** Il ne vaut que pour la clôture du lot de code A-02 (outil + banc fictif). Il n'autorise ni accès au staging d'Imagine, ni import de données, ni audit réel, ni déploiement.
