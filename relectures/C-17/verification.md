# Vérification C-17 — Justificatifs du tarif solidaire (2ᵉ et dernier tour)

Date : 26 novembre 2026. Vérificateur : Claude. Base : `corrections/C-17.md`, `relecteurs/CLAUDE.md`, `doctrine/doctrine.md`.
Méthode : `git diff 983938d8..HEAD` (commit de `corrections/C-17.md`) sur `wp/` et `production/C-17`, lecture ciblée du code corrigé, relance de la suite PHP conteneurisée. **Pas de relecture complète refaite.**

---

## 1. État de chaque instruction de `corrections/C-17.md`

### Instruction 1 (I-2, important) — Aligner la non-régression B-02 sur le contrat C-17 → **Appliquée**
- `wp/tests/demo/b02-runtime.php:43-54` : l'assertion `Aucune facture ou justificatif disponible` est remplacée. Le test vérifie désormais, à l'intérieur de `<ul data-imagine-factures>`, une **liste de factures distincte et vide** (`Aucune facture disponible` + `raccord documentaire Odoo non disponible`), la **présence du bloc justificatif pour la session** (`justificatif_session_distinct` : `name="justificatif"` + version de la session), et l'**absence de mélange** factures/justificatifs (`factures_sans_melange_justificatif`).
- Rejoué **avec C-17 chargé** : `production/C-17/corrections-20261126/b02-final.json` (84/84, dont les trois nouvelles assertions à `true` pour A-CARTE et A-SEPA4), reçu rouge/vert joints (`b02-red.json`, `b02-green.json`, `b02-http-final.json`). Vérification non supprimée. Conforme à l'instruction.

### Instruction 2 (I-1, important) — Rendre le remplacement récupérable → **Appliquée** (défaut proposé)
- `wp/plugins/imagine-site/Justificatifs.php:191-196` (`recevoir()`) : après `supprimerFichier($old)`, la révision détruite est **explicitement invalidée** (`enregistrer()` d'un état `en_attente` + `indisponible => true`, sans blob) **avant** toute écriture du remplacement. En cas d'échec d'écriture, le `catch` (`:213-218`) nettoie le nouveau fichier et relance ; l'état reste `indisponible`.
- Garde-fou de validation : `disponible()` (`Justificatifs.php:~302-315`) exige `decision === 'en_attente'`, `empty(indisponible)` **et** fichier présent/lisible ; `decider()` refuse si `!disponible($old)` (`:~282`). L'invariant « jamais deux fichiers » est préservé, le lien mort et la décision sur dossier sans pièce sont fermés.
- Affichage de l'indisponibilité côté compte (`compte()` `:~377-379`) et côté file référent (`page()` `:~425-430`) : « Document indisponible — nouveau dépôt nécessaire, aucune décision possible ».
- Test du scénario ajouté : `replacement-red/green/final.json` + `wp/tests/demo/c17-corrections.py` (échec après suppression, ancien formulaire référent encore ouvert → décision refusée). Conforme au défaut proposé par la fusion.

### Instruction 3 (I-3, important) — Raccorder le nettoyage à la suppression de compte → **Appliquée**
- `wp/plugins/imagine-site/Justificatifs.php:160-177` (`supprimerCompte()`), branchée sur le hook `delete_user` priorité 0 (`:27`). Sous `verrou()`, elle supprime le fichier privé **et** l'option `imagine_justificatif_<id>`, puis relit (`get_option(... ) !== null` → exception).
- Gestion explicite de l'échec physique : en cas d'impossibilité de retrait, `wp_die(409)` — la **référence est conservée**, pas d'abandon silencieux.
- Choix : `delete_user` (avant disparition du titulaire, requis par `verrou()`) au lieu de `deleted_user` nommé dans l'instruction. C'est l'intention exacte du défaut proposé (« avant la perte du titulaire ») et c'est nécessaire au verrou ; justifié en commentaire. Instruction **respectée**, pas d'écart de fond.
- Tests : `deletion-red/green/final.json` (17/17), couvrant les trois états (en_attente/valide/refuse), l'absence du fichier et de l'option, et le cas où le fichier ne peut être retiré (`suppression_physique_impossible_erreur_explicite`, `echec_physique_compte_option_reference_conserves`).

### Instruction 4 (tests, mineur) — Cas limites manquants → **Appliquée**
- `wp/plugins/imagine-site/tests/JustificatifReglesTest.php` :
  - `testEndDateEqualToTodayIsAccepted` (`:25-34`) — borne de date positive (fin = aujourd'hui acceptée).
  - `testCompletePngAndJpegAreAcceptedFromContent` (`:36-43`) — JPEG/PNG **valides complets** (fixtures `tests/fixtures/c17-fictif.jpg` / `.png`, dimensions vérifiées).
  - `testCompletePdfAtExactlyFiveMibIsAccepted` (`:45-51`) — taille **exactement au plafond** (`MAX`).
- Reçus `boundaries-green.json` / `boundaries-final.json`. Les trois cas limites signalés par Codex sont couverts.

### §5 — Arbitrage « champs conservés » (question à Ced, défaut prudent §4.4) → **Appliquée** selon le défaut, **reste à trancher par Ced**
- `wp/plugins/imagine-site/JustificatifRegles.php:75-76` : `decider()` ne retourne plus que `categorie`, `decision`, `fin` (suppression de `date_decision` et `operateur`). Conforme au défaut prudent §4.4 proposé par la fusion.
- Trace d'audit référent (décision, date, opérateur) portée au **journal C-10** via `journalDecision()` (hooks `updated_option`/`added_option`, `Justificatifs.php:54-96`), sans modifier de moteur tiers. Reprise d'une décision fictive antérieure avec sa date/auteur d'origine prévue.
- Arbitrage tracé : `docs/ecarts.md:47-49` (« brief contre §4.4 »), `production/C-17/ATTENTE-ARBITRAGE-RGPD.md`, renvoi `docs/arbitrages-2026-11-26.md`. Reste une **question touchant au réel (RGPD)** adressée à Ced, réversible (« À défaire si Ced préfère »).

---

## 2. Résultat des tests

Suite PHP conteneurisée rejouée (conteneur jetable, réseau `none`, dépôt monté en lecture seule) :

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Dernière ligne :
`REJEU : 1088 tests, 34410 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`

(Relecture initiale : 1077 tests. +11 tests, cohérent avec les cas limites C-17 ajoutés et les tests des lots concurrents.)

- Gates de démo HTTP non rejoués par moi (staging interdit à ce rôle, doctrine §3). Reçus joints par Hermès et cohérents avec le code lu : `instruction5-20261126/verification-successeur-V2.json` — C-17 réel **54/54** HTTP (égalité stricte des trois champs après chaque décision, puis journal + écran C-10), panne du journal **6/6**, **B-02 84/84 natifs avec C-17 chargé**, **C-09 382/382**. Non recertifiés par exécution indépendante.

---

## 3. Régressions et modifications non demandées

- **Aucune régression détectée.** La suite est au vert ; B-02 (84/84) et C-09 (382/382) passent avec C-17 chargé ; l'état natif commercial/droits/options est identique avant/après (action 8793 `pending` sub 101 inchangée, `before-final.json` = `after-final.json`).
- **Modification présente mais hors périmètre des instructions C-17** : `wp/plugins/imagine-site/MonCompte.php:32-56` scinde `etat()` en `etat()` + `etatCle()` (« clé stable pour C18 »). Le comportement public d'`etat()` est préservé (même projection, traduction en bout) ; B-02 et la suite restent verts. Rattachement affiché C-18, non requis par C-17 — sans effet négatif constaté, mais à noter : ce n'est pas une correction demandée dans `corrections/C-17.md`.
- Le `git diff` depuis le commit de fusion contient aussi des fichiers d'autres lots (C-18, C-19, C-20, a16, a17) : **travail concurrent du dépôt**, sans rapport avec les corrections C-17, non évalué ici.
- Point mineur « capacité dédiée hors démo » : conforme à la décision de fusion (**laisser tel quel**, moindre privilège, report au lot de mise en production). Aucune action attendue, aucune apparue. Conforme.

---

## 4. Verdict

**Prêt pour la validation de Ced.**

Les quatre instructions importantes/mineures de `corrections/C-17.md` sont **appliquées** et couvertes par des tests (rouge→vert joints) ; la suite PHP est au vert (1088/0) ; aucun problème de fond ne subsiste ; aucune régression. La seule question ouverte restante — les champs conservés après décision (§4.4 vs brief, RGPD) — est précisément celle qui **relève de Ced** : le défaut prudent §4.4 est appliqué et réversible, l'arbitrage est tracé dans `docs/ecarts.md`.

Rappels doctrine : ce verdict **n'est pas un GO** (§3). Il ne vaut que pour la clôture du lot de code et reste sous réserve (a) de la validation de l'arbitrage RGPD par Ced et (b) des gates staging HTTP qu'aucun relecteur n'a rejoués par exécution indépendante (interdiction de rôle).
