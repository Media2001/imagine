# Vérification C-19 (2e et dernier tour)

Vérificateur : Claude. Base : `corrections/C-19.md` (fusion, verdict *À corriger*). Correctif appliqué par Hermès après la fusion. Comparaison faite par `git diff 32bbd96d..HEAD` (commit qui portait la fusion) sur `wp/` et `production/C-19`, puis relecture ciblée des fichiers touchés. **Ce n'est pas une relecture complète** : je ne contrôle que les instructions de la fusion, les tests et d'éventuelles régressions.

> **Limite de rejeu.** Pas de PHP ni de Docker sur cette machine : je n'ai pas pu relancer la suite PHPUnit / HTTP moi-même (même situation qu'au premier tour). Je m'appuie sur les reçus d'Hermès, **et** j'ai recalculé en Python les empreintes SHA-256 des sources livrées pour les confronter au reçu successeur.

---

## 1. Instructions de `corrections/C-19.md`

### Instruction 1 — Instant de référence unique pour les échéances (R2) — **Appliquée**
- `EcheancesNatives.php:59` : signature `lire(string $view, int $days, ?int $maintenant = null)`.
- `EcheancesNatives.php:114-115` : `$maintenant ??= time()` puis transmis à `EcheancesRegles::echeances/mandats` (plus de `time()` en dur). Les appels à deux arguments restent compatibles.
- `TableauBordNatives.php:12-16` : un seul `$maintenant ??= time()` capturé **avant** les lectures, injecté dans `EcheancesNatives::lire('echeances', 180, $maintenant)`.
- `TableauBordNatives.php:29` : `$data['maintenant'] = $maintenant` (même instant que la présélection).
- `indicateurs/echeances.php:14` : le recalcul 30/90/180 tourne sur `$data['maintenant']` → t₁ = t₂. La règle C15 n'est pas dupliquée.
- **Test à horloge contrôlée ajouté** : `tests/TableauBordNativesTest.php:23-36` + fixture `tests/fixtures/c19-horloge.php`. Le cas place un abonnement dont le prochain paiement franchit la borne des 180 jours pendant la lecture, et prouve la parité avec `EcheancesRegles::echeances` au même instant (180 = 1, pas 0). Le second test vérifie que l'horloge n'est lue qu'une fois (`c19_clock_reads == 1`). J'ai vérifié que la vue `echecs` sort en `EcheancesNatives.php:84` avant le `time()` de la ligne 114 — elle ne relit donc pas l'horloge, ce qui rend l'assertion « une seule lecture » cohérente.

### Instruction 2 — Réconcilier l'empreinte README du reçu (R4) — **Appliquée**
- `production/C-19/final-V2.json` **non modifié** : empreinte `34a0c577…` préservée (confirmé par recalcul et par `baseline-sources.json:11`). Aucune réécriture de reçu passé à la main.
- Reçu successeur `production/C-19/corrections-V2/final.json:70-84` : la garantie README passe d'une **empreinte figée du fichier entier** à un **contrat de section** (`README_contract` : `libelles`, `Catalogue mémoïsé`, `Un instant unique`, `Par moyen de paiement`, `Q-1 reste en attente`…). L'empreinte historique est conservée en `historical_README_sha256` (étiquetée comme telle), et l'empreinte observée au scellement est tracée en `README_at_receipt_observation_sha256` = `69b8df61…` — que j'ai recalculée identique sur le README actuel.
- `README.md` mis à jour pour documenter les corrections (section C-19). Reçus hérités C-17/C-18 contrôlés séparément (`final.json:65-69`).
- *Lecture du vérificateur :* la cause racine (figer dans un reçu de lot l'empreinte d'un README partagé qui évolue) est traitée au bon endroit, sans falsifier l'historique. Le reçu successeur est désormais interne­ment cohérent. Choix défendable ; à connaître de Ced car c'est un changement de nature de la preuve README.

### Instruction 3 — Co-localiser les libellés dans chaque indicateur (R3/M-3) — **Appliquée**
- `TableauBordAdmin.php:81` : le `match` central est supprimé, remplacé par `$metric['libelles'][$key] ?? (string) $key` (filet conservé).
- `TableauBordRegles.php:29-31` : `calculer()` renvoie `libelles` (tableau, ou fonction des valeurs évaluée).
- Libellés portés dans chaque fichier : `indicateurs/actifs.php:9-20` (fonction, pour les modes natifs dynamiques), `echeances.php:9`, `echecs.php:9`, `mouvements.php:7`.
- **Test** : `tests/TableauBordReglesTest.php:12-30` vérifie que chaque indicateur porte `libelles`, que les clés des libellés = clés des valeurs, et contrôle le cas `mode:paypal` dynamique.

### Instruction 4 — Nettoyer les inefficacités en lecture seule (M-4) — **Appliquée**
- `TableauBordRegles.php:12-15` : `catalogue()` mémoïsé (`static $out`), plus de `glob`/`require` rejoués par indicateur.
- `TableauBordNatives.php:30` : `$definition` mort retiré (`foreach (array_keys(...) as $id)`).
- `TableauBordNatives.php:17-18` : commentaire documentant que le `30` d'`echecs` ne sert qu'à passer la validation de période (la vue échecs n'a pas de filtre temporel).
- **Test** : `tests/TableauBordReglesTest.php:33-40` prouve que `catalogue()` rend les mêmes closures à deux appels (fichiers exécutés une fois).

### Instruction 5 — Ligne grisée « Par moyen de paiement » (selon arbitrage Q-2) — **Appliquée (défaut prudent (b))**
- `TableauBordAdmin.php:92` : ligne « Par moyen de paiement » → « Distinction mode/moyen à arrêter à l'atelier. », sans chiffre ni formule, dans le tableau « À venir ».
- Conforme au défaut proposé dans la fusion. **Reste à confirmer par Imagine/Ced** et à tracer dans `docs/ecarts.md` (cf. §3).

### R1 / Q-1 — Droit « dédié » — **Non appliquée, volontairement (conforme à la consigne)**
- `TableauBordAdmin.php:33-35` : `map_meta_cap` **inchangé** (toujours la composition `imagine_extraire_abonnes` + `imagine_gerer_echeances`). La fusion demandait explicitement d'**attendre l'arbitrage Q-1** avant toute modification, car il touche au modèle de rôles C09. Hermès a bien laissé le code en l'état et isolé la question (`QUESTIONS.md` Q-1). Ce n'est donc pas un manquement.

---

## 2. Résultat des tests

Je n'ai **pas pu relancer** la suite (ni PHP ni Docker sur la machine). Preuves retenues :

- **Reçu successeur** `production/C-19/corrections-V2/final.json` : canonique **1088 tests, 34410 assertions, 0 échec / 0 erreur / 0 ignoré** ; unité ciblée C19 10 tests / 79 assertions (exit 0) ; racine 124 tests / 662 assertions ; natif C09 382/382 ; C18 62 contrôles ; runtime 18, HTTP 29 ; PSR-12 0 erreur (9 erreurs pré-existantes partagées, inchangées).
- **Contre-vérification indépendante (recalcul SHA-256 en Python)** : les 10 fichiers sources corrigés (`TableauBordAdmin/Natives/Regles.php`, `EcheancesNatives.php`, les 4 `indicateurs/*.php`, `TableauBordNativesTest.php`, fixture `c19-horloge.php`) correspondent **exactement** aux `source_sha256` du reçu successeur. `final-V2.json` historique et `README.md` correspondent aussi aux empreintes attendues. Le reçu décrit donc bien le code livré.

Conclusion : les garanties de comptage, étanchéité HTTP et droits reposent, comme au premier tour, sur les reçus d'Hermès, non rejoués par la relecture ; mais la correspondance code ↔ reçu est, elle, vérifiée de première main.

---

## 3. Régressions ou modifications non demandées

- **Aucune régression repérée** dans les fichiers C-19. Les cinq corrections sont ciblées ; `map_meta_cap`, l'échappement, les verbes GET/HEAD et la sortie « nombres seulement » sont intacts.
- Le `git diff 32bbd96d..HEAD` contient beaucoup de fichiers **hors C-19** (lots A-16, A-17, C-17 instruction 5, C-18 corrections, C-20 en cours, démos). Ils sont hors de mon périmètre ici et ne touchent pas le code C-19 ; je ne les ai pas audités.
- **Item de traçabilité non fait (pour Claude, pas pour Hermès)** : l'écart §3.13 « mode / moyen de paiement » (Q-2) **n'est pas encore reporté dans `docs/ecarts.md`** — seul un item C-13 §3.13 y figure. La doctrine §7 confie ce report au fusionneur Claude, pas au worker ; `QUESTIONS.md` le signale correctement. À faire hors de ce rapport (je n'ai pas le droit d'écrire `docs/`).

---

## 4. Verdict

**Prêt pour la validation de Ced.**

Les cinq instructions qui revenaient à Hermès (1 à 4 + le défaut Q-2) sont **appliquées et cohérentes avec le code livré** ; R1 a été, comme demandé, laissé en attente de l'arbitrage. Aucun défaut technique résiduel ni régression repérés. Il **ne reste aucun problème de fond imputable à Hermès** — c'est pourquoi je ne « remonte » pas.

Rappels avant clôture (doctrine : un verdict n'est pas un GO) — ce qui reste est **du ressort de Ced**, pas du worker :
- **Q-1 (droit dédié, touche au réel)** : décision attendue — garder la composition actuelle, ou créer un vrai cap dédié (seed de rôle, mutation C09). Tant qu'elle n'est pas tranchée, le lot ne clôt pas.
- **Q-2 (mode / moyen de paiement)** : confirmer le défaut appliqué + report dans `docs/ecarts.md` par Claude.
- **Validation visuelle** : capture `corrections-V2/tableau-de-bord-referent.png` + parcours `A-VOIR.md` (quatre tableaux, sept emplacements grisés, phrases de comptage).
- **Rejeu indépendant HTTP/droits** : toujours non reproduit par la relecture (pas d'environnement) ; reçus à conserver au dossier de clôture.
