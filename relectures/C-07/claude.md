# Relecture C-07 — Liste d'envoi d'un numéro (relecteur Claude, indépendant)

Date : 22/11/2026. Lot : C-07, PHP pur, `wp/plugins/imagine-pilotage/src/Envoi/` et `tests/Envoi/`.
Brief : `briefs/C-07-liste-envoi.md`. Base : doctrine du 21/11, cahier des charges §3.4/§3.5/§3.8/§3.13, profils `docs/recette/profils.md`.
Je n'ai pas ouvert `relectures/C-07/codex.md`. Pas de fusion à ce stade.

Fichiers relus : `ListeEnvoi.php`, `Abonnement.php`, `Situation.php`, `Destinataire.php`, `ExportCsv.php`, les deux tests, et `imagine-connecteur/src/CsvProtection.php` (dépendance C-04).

**Intégrité de la preuve.** Les empreintes SHA-256 des 8 fichiers relus correspondent exactement à `production/C-07/tests/final.json`. La preuve enregistrée porte donc bien sur le code présent.

---

## 1. Conformité

Le lot fait ce que demande le brief, sans écran ni branchement WooCommerce : règles d'inclusion, offert, groupe, exclusions, gel/rejeu, anomalies séparées, export CSV avec protection C-04. Espace de noms `Imagine\Pilotage\Envoi`, données fictives. Conforme dans l'ensemble. Deux interprétations posent problème.

- **[Important] Grâce × paiement : interprétation non signalée, potentiellement contraire au brief.**
  `src/Envoi/ListeEnvoi.php:56-62` : un abonnement n'est inclus que si `paiementValide === true` **et** `etat ∈ {actif, grace}` (`ETATS_EN_REGLE`, ligne 14). Or un abonné en grâce est par définition celui dont « le dernier prélèvement a été rejeté » (`docs/recette/profils.md`, A-GRACE) : son paiement n'est pas validé. Avec une donnée réaliste (grâce + `paiementValide = false`), le code l'**exclut**, alors que le brief range explicitement la grâce parmi « ce que tu ne décides pas » : « il figure dans la liste ». Le test `ListeEnvoiTest.php:92` masque le risque en posant `paiement = true` pour la grâce. De plus, la décision « délai de grâce ou retrait immédiat au premier rejet » est encore **ouverte** (`docs/decisions.md:45`). L'interaction grâce × `paiementValide` n'est signalée ni dans `notes.md` (sa question 1 ne couvre que la durée), ni ailleurs.
  *Correction proposée* : expliciter dans `notes.md`/README le contrat attendu de l'adaptateur pour un abonné en grâce (quelle valeur de `paiementValide` ?), et ajouter un test grâce + `paiementValide = false`. Poser la question fermée ci-dessous.

- **[Important] A-SANSMAIL : contradiction interne non tracée.**
  Brief règle 5 : « Abonné sans adresse électronique : il y figure comme les autres. » `docs/recette/profils.md` dit l'inverse pour A-SANSMAIL : « adresse technique interne, **exclu des envois** ». Le code suit le brief — correctement — et le modèle `Destinataire.php` n'a aucun champ email, donc « sans mail » n'a structurellement aucun effet sur l'inclusion (`ListeEnvoiTest.php:94` l'inclut). Mais la contradiction entre le brief et les profils n'est tracée ni dans `notes.md` ni dans `docs/ecarts.md`, alors que la doctrine §7 l'exige.
  *Correction proposée* : ajouter une ligne à `docs/ecarts.md` (tâche de Claude) et poser la question fermée à Imagine (email exclu des campagnes Brevo, mais inclus dans la liste postale ?).

- **[Mineur, positif] Clôture incluse / minuit Bruxelles** : interprétation bien signalée (`notes.md` §Gel, `ListeEnvoi.php:47,52`, cohérente avec `Numero::estCloture` de C-01). Rien à corriger.

## 2. Exactitude métier (déroulé à la main)

J'ai déroulé à la main plusieurs cas sur `ListeEnvoi::etablir` (lignes 45-112) :

- **A-CARTE (§3.5, actif/payé, 171 dû)** → situation retenue = dernière par effet avant clôture, paiement validé, état actif, 171 dans `numerosDus` → **1 ligne**. Conforme.
- **A-VIR (actif, paiement non validé)** → `!paiementValide` → **exclu**. Conforme (règle 4).
- **Offert** → l'acheteur est absent du modèle ; seul le `Destinataire` sort. Fuite d'acheteur structurellement impossible. Conforme (règle 2).
- **Groupe, place non attribuée** → `situation->destinataires` vide → aucune ligne. Conforme (règle 3).
- **Paiement à la seconde (`ListeEnvoiTest:105-114`)** → `23:59:59` inclus, `00:00:00` et `00:00:01` exclus : le filtre `effet < cloture` strict (ligne 52) le produit bien. Conforme (règle 7).
- **Correction rétrodatée enregistrée après clôture** → filtrée par `enregistre < cloture` (ligne 52) → la projection antérieure ne bouge pas. Conforme (gel).
- **Rejeu** → tri par `abonnement_id` puis `destinataire_id` (78-80), indépendant de l'ordre d'entrée. Même entrée, même sortie. Conforme.

- **[Mineur] Borne `fin` incluse/exclue** : `ListeEnvoi.php:58` exclut si `fin <= cloture`. Cohérent avec « borne effective exclusive » (`notes.md`), mais c'est une interprétation de borne ; un numéro clôturant exactement à la date de fin ne part pas. Faible enjeu, à confirmer avec le sens métier de `fin`.

## 3. Tests

Preuve enregistrée (non rejouée par moi, voir §Exécution) : **270 tests / 29 594 assertions**, Envoi **36 / 78**, connecteur C-04 **37 / 224**, zéro échec. Les cas prioritaires du brief sont présents : profils, paiement aux bornes, adresse avant/après clôture, remplacement de bénéficiaire, premier/dernier numéro et hors-série via C-01, rejeu, anomalies, CSV. Bon niveau global. Réserves :

- **[Mineur] `testProfilsACloture` (`ListeEnvoiTest:98-103`) rejoue la règle au lieu de la vérifier.** L'attendu codé est exactement `etat ∈ {actif,grace} && paiement` — le code lui-même. Valeur documentaire (lie les noms de profils), mais pas de contrôle métier indépendant (grille §3).
- **[Mineur] A-SANSMAIL et A-ETRANGER peu discriminants.** Sans champ email, le cas A-SANSMAIL est identique à A-CARTE → faux confort. A-ETRANGER n'est distingué que par le pays, et seulement dans le test CSV (`ListeEnvoiTest:247-256`).
- **[Mineur, lié à §1] Chemin grâce incomplet.** Aucun test de grâce avec `fin` dépassée (sortie au terme du délai), ni de grâce avec `paiementValide = false`. C'est justement le cas réaliste qui révélerait le point important ci-dessus.

## 4. Sécurité et données

- Aucune donnée réelle (« Camille Fictive », villes fictives), aucun secret, aucun email réel.
- Protection d'injection de formules réutilisée de C-04 sans modification : `CsvProtection::cellule()` (empreinte confirmée identique à `final.json`), appliquée à chaque cellule (`ExportCsv.php:33`). Guillemets doublés, pas d'échappement antislash, UTF-8 sans BOM, LF. Round-trip testé.
- `ExportCsv::liste()` **refuse par défaut** une liste présentant des anomalies (`ExportCsv.php:18-21`) : bonne barrière avant transmission au routeur.
- **[Mineur]** `ExportCsv::lignes()` est public et contourne cette barrière. Documenté dans `notes.md` comme sérialiseur bas niveau ; acceptable, mais reste une porte à ne pas câbler directement sur l'expédition.
- Pas de paywall ni de texte réservé ici (hors périmètre) : sans objet.

## 5. Doctrine

- §5 respecté : PHP 8.2, `declare(strict_types=1)`, objets `readonly`, `DateTimeImmutable`, aucune lecture d'horloge, espace de noms conforme. PSR-12 du périmètre Envoi vert (preuve `final.json`).
- §4 « standard d'abord » : logique métier pure, aucune réimplémentation d'une extension retenue ; réutilisation de C-04 plutôt que duplication. Bon.
- **[Mineur]** Couplage à maintenir à la main entre `ExportCsv::COLONNES` (`ExportCsv.php:11-14`) et les clés construites dans `ListeEnvoi` (`ListeEnvoi.php:65-74`). Une colonne ajoutée d'un seul côté casserait silencieusement l'autre. Risque faible.

## Exécution des tests — réserve

**Je n'ai pas pu relancer les tests moi-même** : `docker` et `php` exigent une approbation non disponible dans cette session non-interactive. Conformément à la grille (« à défaut, le dire »), je me suis appuyé sur les journaux enregistrés (`production/C-07/tests/final.log`, `final.json`, `rapport.md`) **après avoir confirmé que les empreintes SHA-256 du code relu correspondent exactement à celles testées**. Le lanceur global retourne `1` à cause de six avertissements PSR-12 préexistants de C-05 (`tests/Echeancier/run.php`), hors périmètre et correctement documentés ; les tests ciblés C-07 et C-04 passent, code 0. À rejouer réellement lors du second tour de vérification.

---

## Questions fermées pour Ced / Imagine

1. **Grâce × paiement** — Pour un abonné en grâce à la clôture (dernier prélèvement rejeté, donc `paiementValide = false`), confirme-t-on qu'il doit **figurer** dans la liste ? Si oui, le contrat de l'adaptateur doit forcer `paiementValide = true` pour la grâce, ou la condition du code doit être assouplie. (Rappel : « grâce ou retrait immédiat » est encore ouvert, `decisions.md`.)
2. **A-SANSMAIL** — Confirme-t-on que « exclu des envois » dans les profils ne vise que les campagnes email (Brevo), et qu'un abonné sans email **figure** bien dans la liste postale du routeur (brief règle 5) ?
3. **Bornes et format** (déjà posées par Hermès, `notes.md`) — colonnes/ordre/format CSV du routeur ; deux exemplaires pour deux abonnements même personne/adresse ; sens exact de la borne `fin`.

---

## Verdict

**À corriger.** Le lot est bien construit, testé et globalement conforme au brief ; aucun point **bloquant**.

- **Important** : (1) interaction grâce × `paiementValide` non signalée et potentiellement contraire au brief, sans test du cas réaliste ; (2) contradiction A-SANSMAIL brief vs profils non tracée (doctrine §7).
- **Mineur** : tests profils tautologiques, cas A-SANSMAIL/A-ETRANGER peu discriminants, chemin grâce incomplet, borne `fin`, barrière `lignes()` publique, couplage `COLONNES`.

Ce verdict n'est pas un GO. Clôture conditionnée au second rejeu réel des tests, à la fusion avec Codex, et au traitement des questions fermées ci-dessus.
