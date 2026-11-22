# Vérification C-05 — troisième tour (ajout SEPA du 22/11, 17 h)

Vérificateur : Claude Code (NUC). Date : 22/11/2026.
Objet : contrôler l'application de l'arbitrage « marge de confirmation du premier SEPA en réglage » (A-FAIRE consigne 2 → `docs/arbitrages-2026-11-22.md:59-61`), relancer les tests si possible, signaler toute régression. **Pas de relecture complète** : seul le delta depuis `relectures/C-05/verification.md` est contrôlé.

Base comparée : état du dépôt au moment de la verification.md précédente → état courant, sur le **contenu** des fichiers. Les hash de commits bougent en séance (le bot de synchro réécrit l'historique : HEAD est passé de `618d74b` à `c54f111` pendant la vérification). J'ancre donc le contrôle sur les empreintes SHA-256 de fichiers, stables, pas sur les SHA de commits.

Delta effectif, code C-05 :
- `src/Echeancier/Reglages.php` (SHA-256 `414a10f9…0c12f0`)
- `src/Echeancier/ReglagesAdministration.php` (SHA-256 `0ab7a896…22db0`)
- `src/Echeancier/README.md` (mis à jour)
- `tests/Echeancier/ConfirmationPremierSepaTest.php` — nouveau (SHA-256 `40be1c38…d4ad6b`)
- Banc : `wp/tests/echeancier-runner/sepa-scenario.php` (nouveau), `sepa.py` (nouveau), `README-sepa.md` (nouveau), `admin-scenario.php` (+2 lignes).

Les trois empreintes ci-dessus ont été **recalculées sur le code relu** et correspondent **exactement** à celles qu'Hermès déclare (`sepa-22nov-1700.md:43-45`) et à celles du reçu e2e (`source_sha256`). Les reçus archivés portent donc bien sur ce code.

---

## 1. Arbitrage « marge de confirmation du premier SEPA » (arbitrages 22/11, 17 h)

Texte : « La marge de confirmation pour un premier paiement par SEPA … devient un **réglage**. Valeur par défaut : la marge s'applique. » Plus le principe du 22/11 (arbitrages:9-12) : règle isolée derrière un réglage nommé, défaut prudent, chaque valeur testée, lot clos sans attendre, question inscrite dans `decisions.md`.

| Exigence | État | Fichier : ligne |
|---|---|---|
| La marge devient un réglage nommé | **Appliqué** | Nouvelle clé `confirmation_premier_sepa`. 4ᵉ paramètre `confirmationPremierSepa` du constructeur `Reglages.php:13` ; décodage strict `Reglages.php:57-59` ; champ d'administration `ReglagesAdministration.php` (liste `avec_marge`/`sans_marge`, texte d'aide) |
| Valeur par défaut = la marge s'applique | **Appliqué** | Défaut `'avec_marge'` au constructeur `Reglages.php:13`, dans l'option par défaut `ReglagesAdministration.php` (clé `register_setting`), et à la clé absente `Reglages.php:57-58`. Test `ConfirmationPremierSepaTest.php:149` |
| Règle isolée en un seul endroit | **Appliqué** | Logique concentrée dans `Reglages::premierSepaPayeLe()` (`Reglages.php`, nouvelle méthode), réservée au premier SEPA (docbloc + tests), sans toucher `Planificateur`, `Moteur`, Woo ni les droits |
| Défaut prudent | **Appliqué** | `avec_marge` = numéro payé au plus tôt `max(confirmation, commande + marge civile)` → jamais réputé payé avant confirmation ni avant la fin de la marge ; sans confirmation, `null` (jamais payé par le temps seul). Prudent. |
| Chaque valeur du réglage testée | **Appliqué** | `ConfirmationPremierSepaTest.php` exerce `avec_marge` **et** `sans_marge` sur : dates civiles + frontière de clôture (:74-84), confirmation absente/tardive (:22-28), confirmation antérieure à la commande refusée (:38-52), marge obligatoire refusée par défaut (:30-36), décodage des deux positions + entrées invalides refusées (:128-147). e2e réel dans les deux stockages (classique + HPOS) d'après le reçu. |
| « J'ai compris X » documenté (doctrine §1) | **Appliqué** | Interprétation « délai = seuil après la commande, pas une nouvelle date de prélèvement » écrite clairement (`sepa-22nov-1700.md:15`, docbloc de `premierSepaPayeLe`) |
| Consigne A-FAIRE « redéposer PRET seulement si le code change » | **Appliqué** | Code modifié ; `PRET` redéposé (`production/C-05/PRET`) |
| Question inscrite dans `docs/decisions.md` | **Partiellement — hors surface d'Hermès** | La décision/question SEPA du 17 h n'est pas encore portée dans `docs/decisions.md` (ligne 30 ne cite que « quatre échéances par bloc » ; ligne 48 garde l'ancienne formulation « prélèvement SEPA obligatoire après une première carte »). `docs/` est interdit à Hermès (doctrine §7) : report à la charge de Claude à la clôture. Pas un défaut de code. |

Effet métier vérifié à la main (calendrier de démonstration, clôture du 1ᵉʳ numéro le 10/04/2027, marge 7) :
- Commande 09/04 12 h, confirmation 13 h. **Avec marge** : payé au plus tôt 16/04 12 h → bien **après** la clôture du 10/04. **Sans marge** : 09/04 13 h. Conforme à l'objet de Q1 (éviter de réputer payé avant confirmation).
- `REG-2027-04` et le versement initial à la commande **inchangés** (`ConfirmationPremierSepaTest.php:110-126` : `$plan[0]->numero->id === 'REG-2027-04'`, échéance 2 au 03/07). Le réglage ne déplace aucun numéro ni aucune échéance.

→ **Arbitrage appliqué.** La question ouverte Q1 de la relecture (`relectures/C-05/claude.md`) est close par ce réglage.

## 2. Résultat des tests

**Non rejoués localement par le vérificateur**, pour les raisons des tours précédents : pas de PHP/Docker exécutable en session (runner officiel via `wsl.exe -d Ubuntu -- docker`, approbation refusée ; écriture dans `production/C-05/` interdite au relecteur). Un rejeu dans l'environnement de test autorisé reste nécessaire avant clôture.

Reçus livrés par Hermès (`production/C-05/replays/sepa-22nov-1715-final/`), contrôlés et cohérents avec le code relu :
- **`final.xml` : 765 tests / 33 143 assertions / 0 erreur / 0 échec / 0 ignoré.** Suite **Echeancier : 403 tests / 2 373 assertions / 0 échec** (dont les ~19 cas SEPA).
- **`final.json`** : `composer test` exit 0, PSR-12 exit 0, syntaxe exit 0, `composer validate --strict` exit 0 ; réseau détaché, sans montage ni port.
- **e2e réel** (`final-e2e.json` / `-result.json`) : Subscriptions 9.4.1, Woo 11.1.1, WP 7.0.9, PHP 8.2.36 ; classique + HPOS. `exit_code` 0 ; **`failed: 0` sur les quatre exécutions, aucun `pass: false`**.
- **Lien reçus ↔ code** : le `source_sha256` du reçu e2e porte `Reglages.php = 414a10f9…0c12f0`, identique au fichier relu ; `Planificateur.php`, `RaccordManuel.php` et les classes `Numeros/*` y portent les mêmes empreintes qu'avant — moteur de dates non touché.

Portée des reçus (rappel) : prototype à preuves synthétiques, réseau détaché, pas de débit bancaire, pas d'emails, pas d'Odoo.

## 3. Régressions et modifications non demandées

- **Aucune régression décelée sur C-05.** Le 4ᵉ paramètre de `Reglages` a une valeur par défaut → appelants existants inchangés. `depuisOption` et le sanitiseur d'administration propagent la nouvelle clé sans migration destructive (clé absente = `avec_marge` ; valeur invalide/corrompue refusée, option précédente conservée). `Planificateur`, `RaccordManuel`, `Numeros/*` **inchangés** (empreintes identiques). Les suites voisines restent au vert dans le même `final.xml`.
- **Modifications hors périmètre C-05 présentes dans la fenêtre de diff** : `wp/tests/a01-court/*` (nouveaux scripts et tests). Elles relèvent du **lot A-01** (consigne 1 d'A-FAIRE), pas de l'ajout SEPA ; elles ne touchent aucun fichier C-05. À vérifier dans le cadre d'A-01, pas ici.
- **Point d'attention mineur, non bloquant** : `premierSepaPayeLe()` n'est encore câblée à aucun appelant (prototype non branché) ; Hermès le signale (« l'appelant futur teste date non nulle et atteinte »). Cohérent avec un lot de proposition ; à exercer au branchement.

## 4. Verdict

**Prêt pour la clôture.**

L'arbitrage du 22/11, 17 h est appliqué : la marge de confirmation du premier SEPA est un réglage nommé, défaut prudent `avec_marge`, les deux positions testées, sans toucher au moteur de numéros ni aux échéances. Aucune régression. Les empreintes du code relu correspondent aux reçus, qui sont au vert. Aucun problème de fond restant : rien à remonter à Ced sur le fond.

Réserves à porter à la clôture (à la charge de Claude, non bloquantes, pas des défauts de code) :
1. **Tracer dans `docs/decisions.md`** la décision SEPA du 17 h (et dans `docs/ecarts.md` le brief C-05 « jamais cinq » déjà signalé au tour précédent, item 6 toujours à faire). `docs/` est hors surface d'Hermès.
2. **Rejeu indépendant** dans l'environnement de test autorisé non encore réalisé.
3. **Q2** (sort de l'engagement après rejet) reste ouverte chez Imagine ; couverte par un défaut prudent réglé, ne bloque pas le lot.

Rappel : ce verdict n'est pas un GO au sens de la doctrine §3 ; il ne vaut que pour la clôture du lot de code et appartient à Ced.
