# Relecture C-25 — Rétractation en ligne, en deux étapes (Claude, relecteur indépendant)

Date : 26 novembre 2026. Lot : C-25. Brief : `briefs/C-25-retractation-en-ligne.md`.
Cahier des charges : §3.7 (fonction de rétractation en deux étapes pendant le délai légal), §3.8 (cadre belge, loi du 19 juillet 2026).
Codex non ouvert ; fusion non faite (consigne). Ce verdict n'est pas un GO.

## Rejeu de la suite (commande autorisée, sans argument)

Commande : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`
Conteneur jetable, réseau coupé, dépôt en lecture seule (T01 ISOLATION : network=none ; rootfs=ro ; mount ...:ro).

Dernière ligne :

```
REJEU : 1149 tests, 36036 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Les 8 tests C-25 (7 dans `RetractationAdapterTest`, 1 dans `RetractationReglesTest`) passent, 146 assertions. `imagine-site` : 176 tests, 0 échec.
Note : `PRET` scelle 1143 tests / 35855 assertions ; mon rejeu en compte 1149 / 36036. L'écart tient à des tests ajoutés par d'autres lots depuis le scellement (B-07/B-08 dans le bootstrap) ; tout reste au vert. Aucun impact C-25.

## 1. Conformité

- **Standard d'abord** : `NOTE.md` donne les dix lignes demandées, avec trois sources officielles WooCommerce/Subscriptions. Conclusion justifiée : note Woo privée + métadonnée + journal C-10, aucun nouveau CPT. Conforme au brief.
- **Deux étapes + accusé** (`Retractation::panneau`, `wp/plugins/imagine-site/Retractation.php:200`) : étape 1 = objet/date/motif facultatif sans écriture ; étape 2 = confirmation explicite ; accusé daté, retrouvé ensuite sur la vue de commande et à la même adresse (`entree`, ligne 174). Conforme.
- **Hors délai** : l'entrée n'est ni dans les actions de commande (`woocommerce_my_account_my_orders_actions`, ligne 156) ni dans `entree` ; un POST direct est refusé deux fois (dans `panneau` ligne 215, puis sous verrou dans `demander` ligne 100). Conforme.
- **Administration** (`administration`, ligne 263) : liste datée, commande, motif ; aucune action automatique ; capacité `manage_options` contrôlée. Conforme.
- **Journal C-10** : la clé `imagine_reglages_journal_retractation_<id>` entre dans le `LIKE 'imagine_reglages_journal_%'` du journal partagé (`imagine-pilotage/src/Administration/Reglages.php:178`). Vérifié : la demande apparaît bien dans le journal C-10, rendue sans erreur (l'événement porte quand_utc/qui_id/qui_login/option/avant/apres, cf. rendu ligne 320). **Conforme** — la clé déterministe sert aussi de clé anti-doublon.
- **Deux réglages dans l'écran C-10** (`RetractationReglages::champs`, `RetractationReglages.php:74`) : délai 1–365 (défaut 14) et point de départ paiement/manuel (défaut paiement). Chaque valeur testée (`testReglagesC10EtDateManuelleConservatrice`). Conforme sur le fond ; réserve de forme en §5.
- **« Rien ne part »** : note privée (`add_order_note(..., false)`), aucun `wp_mail` ni appel HTTP. Vérifié par les mutations (mail/http) et les compteurs à zéro. Conforme.
- **Une demande par commande** : verrou MySQL + relecture `lire` sous verrou + `add_option` sur clé unique. Conforme.
- **C-21 export/effacement** : `RetractationConfidentialite` déclare un exporteur et un effaceur additifs, plus le raccord `delete_user`. Conforme.
- **C-09 restauration d'état** : aucun changement d'état de commande/abonnement/accès dans le code ; déroulé et recette le confirment. Conforme.
- **A-VOIR.md** : les trois questions (accès, remboursement, départ du délai pour abonnement) sont rangées en questions fermées pour Imagine. Conforme.
- Interprétation signalée : « borne finale du délai incluse » (NOTE § Choix) — déclarée, pas cachée.

## 2. Exactitude métier (déroulé à la main)

Logique pure dans `RetractationRegles` : `end = start + jours*86400`, `ouverte = now >= start && now <= end`.

- **Cas délai (origine paiement, 14 j), paiement 2026-11-25** : start=paiement ; now=start → ouvert ; now=start+14 j (2026-12-09 00:00:00) → **ouvert** (borne incluse) ; now=start+14 j+1 s → fermé. Conforme au code et aux tests.
- **Changement d'année (origine manuelle, 30 j), date manuelle 2030-12-20** : end=2031-01-19 ; now=2031-01-10 → ouvert. L'arithmétique en secondes epoch traverse l'année sans faute. `dateManuelle('2030-02-30')` → `null` (recontrôle de reformat strict). Conforme.
- **Date absente / calendrier incomplet** : origine paiement sans `date_paid` → `debut`=null → `ouverte`=false → entrée masquée, POST refusé. Fermeture prudente conforme à la doctrine (« dans le doute, fermé »).
- **Événement rejoué** : seconde `demander` renvoie le premier enregistrement (lecture sous verrou + clé unique du journal) ; aucune seconde note. Idempotent. Conforme.
- **Titulaire/tiers** : `commande` refuse `get_customer_id() !== $user` ; pour un abonnement, contrôle du titulaire de l'abonnement **et** de la commande initiale ; abonnement sans parent → fermé. Conforme.

## 3. Tests

- Tous passent (voir rejeu). TDD réel tracé (reçus `tdd-01`→`tdd-04`, rouges conservés).
- Couverture des cas limites : bornes du délai, origines paiement/manuelle, date invalide, titulaire/tiers, verrou occupé, échec note/journal, export paginé + panne SQL, effacement sans toucher les tiers, rejeu après effacement. Bon niveau, au-delà du nominal.
- Les tests vérifient la règle, pas le code : `RetractationReglesTest` balaie 4×2×4 combinaisons de bornes ; l'adaptateur exerce les vraies classes derrière des bouchons limités aux API WP/Woo (`RetractationWPStubs.php`). Le témoin positif précède chaque absence (`assertCount(2, ...)` avant les contrôles d'isolement). Bonne discipline.

## 4. Sécurité et données

- **Nonces** : étape 2 liée à la cible **et** au hash du motif (`$confirmAction`, ligne 229) ; le nonce d'étape 1 ne vaut pas pour l'étape 2 (recette). Le champ date admin a son nonce (`sauverDate`, ligne 56). Bon.
- **Droits** : capacité `manage_options` (liste) et `manage_woocommerce` (date) contrôlées ; titulaire recontrôlé sous verrou.
- **Échappement** : sorties via `esc_html`/`esc_attr`/`esc_url` ; motif assaini (`sanitize_textarea_field`) à l'écriture et échappé au rendu ; `<script>` neutralisé (test admin).
- **Requêtes préparées** : `lignes` et les verrous passent par `$wpdb->prepare` ; noms de tables natifs. Pas d'injection.
- **Paywall / fuite** : la demande n'expose aucun texte réservé ; pas de voie concernée par ce lot.
- **Secrets / données réelles** : aucun ; fixtures en `@example.org`, noms inventés.
- **Interaction erasers C-21 ↔ C-25** (vérifiée) : C-21 (`Confidentialite::effacer`) classe l'entrée de journal de rétractation en « audit » (`qui_id === $id`) et la dépersonnalise (qui_id→0), **sans** supprimer la note privée ; C-25 (`RetractationConfidentialite::effacer`) supprime la note et dépersonnalise. Dans les deux ordres d'exécution, le résultat est idempotent : si C-25 passe d'abord, `audit()` ne reconnaît plus l'entrée (qui_id déjà 0) et ne la retouche pas. Pas de double traitement fautif. **Point positif.**

## 5. Doctrine

- **Standard d'abord** : respecté (note Woo native plutôt qu'un moteur maison).
- **Conventions §5** : PHP 8.2, `declare(strict_types=1)`, namespace `Imagine\Site`, préfixe `imagine_`, textes FR via `__()`, aucune modification de code tiers (hooks seulement). README mentionne la rétractation. Conforme.
- **Idempotence / rejouable** : verrou + clé unique + transaction note/méta/journal. Conforme à l'esprit du §4.
- **Non-régression** : suite globale au vert après ajout. Conforme.

## 6. Études

Sans objet (lot de code). Les trois sources de `NOTE.md` sont citées avec adresse ; la conclusion « pas de combinaison standard équivalente » est prudente et ne revendique pas une preuve d'absence.

## Verdict

**Conforme.** Le lot fait ce que demande le brief, ni moins ni plus : il enregistre une demande en deux étapes, ne rembourse rien, n'annule rien, ne ferme aucun accès. Tests au vert (REJEU PASS). Points classés ci-dessous. Ce verdict n'est pas un GO ; la validation visuelle et juridique reste due.

### Points

- **Mineur / important (maintenabilité)** — `RetractationReglages.php:15` : les deux réglages sont injectés dans l'écran C-10 en bufferisant la sortie de la page et en détectant la chaîne `value="imagine_reglages"` (retrait/réajout de tous les callbacks du hook de page, priorité 150). Fonctionne et est testé, mais dépend du markup exact de C-10 : si C-10 change son `<form>` ou son `settings_fields`, les champs disparaissent **en silence**. Correction proposée : exposer côté C-10 un hook explicite (action/filtre) sur lequel se brancher, plutôt que la détection de HTML.
- **Mineur** — `RetractationConfidentialite.php:20` : le raccord `delete_user` fait `wp_die` si le nettoyage n'aboutit pas (panne SQL persistante), ce qui bloque la suppression de l'utilisateur. Fermeture prudente conforme à la doctrine, mais peut surprendre un administrateur ; à documenter dans le README.
- **Mineur** — `Retractation.php:32` : `ouverte` inclut l'instant exact `start + N*86400` (fenêtre = N jours + l'instant final). Interprétation déclarée dans `NOTE.md`. Sans portée tant que la règle juridique n'est pas arrêtée ; à confirmer par Imagine (voir questions).

### Décisions techniques, défaut proposé (Hermès applique, Claude arbitre après coup)

1. Injection des réglages dans l'écran C-10. **Défaut proposé** : conserver l'injection actuelle pour la démonstration, mais ouvrir dans C-10 un hook de rendu dédié et l'utiliser au prochain passage. Catégorie : technique.

### Pour Imagine (règles métier → réglages)

1. **Définition exacte du délai** : la borne finale est-elle incluse (fin au terme de la 14ᵉ journée) ou exclue ? **Défaut proposé** : incluse, comme aujourd'hui, jusqu'à arbitrage. Catégorie : métier.
2. **Effacement vs trace anti-doublon** : après un effacement C-21, le compte encore vivant conserve un accusé affiché (date + n° de commande) et le journal C-10 garde une ligne dépersonnalisée, pour empêcher de redéposer. Est-ce acceptable au regard du droit à l'effacement, ou faut-il effacer aussi la trace au risque de rouvrir le dépôt ? **Défaut proposé** : conserver la trace dépersonnalisée (anti-doublon), sans motif ni identité. Catégorie : métier. (Déjà signalé par Hermès dans `A-VOIR.md`.)

### Questions pour Ced (visuel / réel)

- Aucune question technique pour Ced. La validation **visuelle** du parcours (étapes 1/2, accusé, écran C-10, liste admin) reste à faire sur `imagine-test-demo` ; le lot n'utilise que le squelette existant, sans style inventé ni CSS livré (vérifié).
