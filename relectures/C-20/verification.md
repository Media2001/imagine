# Vérification C-20 — deuxième et dernier tour (Claude)

Lot : « Ne pas renouveler », deuxième passe. Corrections fusionnées : `corrections/C-20.md`. Code relu de nouveau : `wp/plugins/imagine-site/` ; preuves : `production/C-20/`.

Méthode : `git diff` entre le commit de la fusion `a82f4a7e` (« synchro 2026-11-26 08:53 », juste après l'écriture de `corrections/C-20.md`) et `HEAD`, sur `wp/` et `production/C-20/`, puis rejeu de la suite PHP. Pas de relecture complète refaite ; je contrôle uniquement l'application des cinq instructions, les tests et les régressions.

## 1. Instructions de `corrections/C-20.md` (§4)

### Instruction 1 — Couvrir le raccord `Paywall` (bloquant la clôture) — **Appliquée**

- Nouveau test de règle sur le **vrai** adaptateur : `wp/plugins/imagine-site/tests/C20PaywallAdapterTest.php`. Il appelle `Paywall::decisionPdf()` (pas une copie de la règle), pilote l'horloge de requête par `ReflectionProperty` sur `Paywall::requestInstant`, et asserte `motif !== 'adaptateur_indisponible'` (`:38`) pour garantir que l'adaptateur réel tourne.
- Doublures d'entrées natives seulement : `wp/plugins/imagine-site/tests/fixtures/c20-native-doubles.php` (WC_Subscription / Membership / fonctions WP ; commentaire explicite « No access decision/rule is reproduced here »).
- Le fournisseur de données `bornes()` (`:14-26`) couvre les quatre cas exigés :
  - `pending-cancel` **sans** fin native ⇒ fermé (`sans_fin_native_ferme`, `:16`).
  - une seconde avant la fin native ⇒ ouvert (`juste_avant_fin_ouvert`, `:17`).
  - à la fin exacte et après ⇒ fermé (`fin_exacte_ferme` `:18`, `apres_fin_ferme` `:19`).
  - priorité d'une fin Memberships antérieure à la fin Subscriptions ⇒ avant/exact/après (`membership_plus_court_*`, `:20-22`).
- C06 et C13 restent inchangés : `Paywall.php` n'a pas été modifié depuis la relecture (dernier changement commit `18c6027a`, 06:13, antérieur à la fusion) ; seul un test a été ajouté, comme demandé.

### Instruction 2 — i18n (M2) — **Appliquée**

- `RenouvellementRegles.php:13,17,21,25,28` : `message` renvoie désormais un **code** (`arret_a_terme`, `manuel`, `quatre_fois`, `indisponible`), plus aucune phrase.
- `Renouvellement.php:46-51` : `match` qui associe chaque code à un appel `__()` avec **chaîne littérale** (extractible), puis `esc_html($message)` en `:54`. L'ancien `__($view['message'], …)` est supprimé.
- Couvert par deux tests : `C20RenouvellementI18nTest.php` (vérifie la présence du littéral dans le catalogue et dans la source, l'échappement HTML, l'absence de `__($view['message']`) et l'ajout `testToutesLesPresentationsRetournentUnCodeSansPhrase` dans `RenouvellementReglesTest.php`.

### Instruction 3 — Aligner le README (M1) — **Appliquée**

- `wp/plugins/imagine-site/README.md`, section C-20 réécrite sur le périmètre réduit accepté (titre « livraison réduite acceptée le 26 novembre 2026 à 7 h 30 »). Décrit le raccord borné, les tests locaux `Paywall::decisionPdf`, l'i18n par codes, les écrans sans bouton.
- Le constat « Pas PRET : le point 2 reste bloqué » est déplacé sous une rubrique **« Historique daté — 26 novembre 2026 »**, qui rappelle que l'arbitrage de 7 h a changé le critère de réception, pas C13.

### Instruction 4 — Verrouiller l'ordre `quatre_fois` / `arret_a_terme` (au branchement) — **Appliquée (défaut conservé + documenté)**

- Instruction explicitement « au branchement », défaut proposé : conserver l'ordre actuel. L'ordre est inchangé dans `RenouvellementRegles.php` (`arret_a_terme` avant `quatre_fois`) et le point est documenté dans le README (« l'ordre actuel … est conservé ; décider explicitement sa priorité … au branchement »). Conforme au défaut.

### Instruction 5 — Noter la méthode A-PAPIER hors démo (au branchement) — **Appliquée (documentée)**

- Instruction « au branchement ». `EcheancesNatives.php` n'est pas modifié (correct : aucune règle de production ne doit s'appuyer sur le drapeau fictif). Le README note le risque hors démo (`methode()` renvoie `''` ⇒ chute en `quatre_fois`) et demande un raccord de méthode réelle validé au branchement.

## 2. Résultat des tests

- Rejeu autorisé, sans argument, en conteneur jetable (réseau `none`, dépôt monté en lecture seule) :
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`
- Dernière ligne :
  **`REJEU : 1114 tests, 34560 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`**
- Passage de **1101 → 1114 tests** : les nouveaux tests sont bien exécutés. Vérifié dans le JUnit :
  - `C20PaywallAdapterTest::testDecisionPaywallSurBornesNatives` : 7 cas (data provider), tous verts.
  - `C20RenouvellementI18nTest::testChaqueCodeTraduitUnLitteral` : vert.
  - `RenouvellementReglesTest::testToutesLesPresentationsRetournentUnCodeSansPhrase` : vert.
- Contrairement au premier tour, le cœur du lot (branche `pending-cancel` bornée) est désormais couvert par un test **rejouable par le relecteur**, et non plus seulement par les JSON `adapter-*` d'Hermès. Le trou de couverture I1 qui motivait le verdict de fusion « À corriger » est fermé.

## 3. Régressions ou modifications non demandées

- Dans le périmètre C-20 : **aucune**. `Paywall.php` n'a pas été touché ; les seuls fichiers de code C-20 modifiés sont ceux visés par les instructions (`Renouvellement.php`, `RenouvellementRegles.php`, `README.md`) et les tests ajoutés. La garde de propriété `Renouvellement.php:42` est intacte.
- Le `git diff` global montre aussi des changements hors C-20 (`Confidentialite*`, `Newsletters*`, `a18/a19`, `c21*`, `c22*`) : ils relèvent des lots C-21 / C-22 / B-05 traités en parallèle, hors de ce lot. Ils ne dégradent pas C-20 — la suite complète est verte.
- Écritures d'Hermès dans `production/C-20/` (reçus `fusion-*`, `A-VOIR.md`, `PRET`, `natif.md`) : son domaine, non bloquant.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les trois instructions actionnables (1, 2, 3) sont appliquées ; les deux instructions « au branchement » (4, 5) sont documentées conformément au défaut proposé. La suite PHP est verte et couvre maintenant le raccord `Paywall` qui manquait au premier tour. Aucun problème de fond restant, aucune régression.

**Rappel (doctrine §6) : ce verdict n'est pas un GO.** Le périmètre reste réduit (raccord borné + écrans sans bouton) ; le §3.4 côté utilisateur — bouton « ne pas renouveler », confirmation, émission de `imagine_non_renouvellement_confirme`, preuve de fin native du quatre-fois — est reporté au lot de branchement (staging vérifié, Stripe test, GO écrit de Ced), écart déjà tracé. La clôture ne doit pas se lire « §3.4 fait ».
