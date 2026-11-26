# Vérification C-22 — second et dernier tour

Date : 26 novembre 2026. Vérificateur : Claude (indépendant). Objet : contrôler l'application de `corrections/C-22.md` par Hermès après la fusion, relancer les tests, repérer régressions et écarts.

Méthode : `git diff` entre l'état relu (commit du 26/11 ~14:43, avant les corrections) et l'arbre livré, sur `wp/` et `production/C-22`, puis relecture ciblée des zones modifiées et rejeu du vérificateur du lot. Je n'ai pas refait de relecture complète.

Fichiers métier modifiés par la correction : `NewslettersReglages.php`, `NewslettersRegles.php` et le vérificateur `c22-verifier.py` (plus ses satellites de test). `Confidentialite.php` et `Newsletters.php` sont **inchangés** (absents du diff) — conforme à la consigne de ne pas toucher le fichier partagé.

---

## 1. Application des instructions de `corrections/C-22.md`

### Instruction 1 — C22-01 : empêcher la réattribution par recyclage d'identifiant — **Appliquée**

- `NewslettersReglages.php:79-111` : `nettoyerCatalogue()` réserve les identifiants actifs (`reserver($current)`, `:79`), ceux présents dans les préférences lecteurs historiques (`reserverPreferences`, `:90`) et ceux des journaux C10 avant/après (`:100-106`), puis **refuse** toute ligne dont l'identifiant n'est pas actif mais déjà réservé (`:110-111`, `throw`).
- `NewslettersReglages.php:43-48` : un hook `delete_user_meta` réserve l'identifiant d'un ancien choix **avant** l'effacement personnel C-21, pour que la réserve survive à l'effacement.
- Réserves stockées en options sans donnée personnelle : `imagine_newsletters_reserve_<id>` = `'1'`, `autoload` off (`:198-210`).
- Message d'erreur mis à jour (`:119`) : « Identifiants uniques, **jamais réutilisés après retrait** ».
- Garde-fou désormais **dans le code**, plus seulement un avertissement d'interface. Comportement vérifié par le parcours HTTP (voir §2 : `C10_recyclage_refuse_erreur_visible`, `recyclage_compte_sans_case_ni_choix_reaffecte`, `historique_retire_exact_HTTP`).

Scénario du brief (choix `lecteur`, retrait, tentative de réutilisation) : le réglage refuse l'identifiant et aucun écran ne réaffiche l'ancien choix coché. Fail-closed si l'historique est illisible (`throw 'Historique indisponible.'`, `:87`).

### Instruction 2 — C22-03 : remettre le vérificateur en accord avec le code, tester le comportement et non la syntaxe — **Appliquée**

- `c22-verifier.py` : les assertions littérales sur `Confidentialite.php` (`privacy.count("'imagine_newsletters_preferences'")==1` et la déclaration exacte de `META`) ont été **supprimées** de `shared()`. Vérifié : le littéral n'apparaît plus dans `shared()` (`c22-verifier.py:61-70`).
- Nouveau contrôle **comportemental** : `privacy()` (`:56-59`) exécute les vrais callbacks C-21 d'export/effacement sur un choix historique retiré, via `c22-corrections.py`, et le résultat est remonté dans `shared()` (`C21_export_erase_result`, `:70`).
- La reconstruction de l'ancienne empreinte (ancien `--seal`, retrait de `b", 'imagine_newsletters_preferences'"`) est supprimée ; le sceau V2 ne ré-épingle plus le fichier partagé par hash entier (`c22.py` : `NAMES` réduit aux trois fichiers Newsletters, commentaire « contract-only »).
- Deux mutations témoins (`correction-mutation-export/erase-V2.json`) prouvent que le contrôle attrape réellement une omission d'export ou un effacement sans effet.
- Résultat : `python -B wp/tests/demo/c22-verifier.py` réussit sur l'arbre livré (voir §2) — le défaut de la chaîne de preuve est levé.

### Instruction 3 — C22-02 : compter les caractères, pas les octets — **Appliquée**

- `NewslettersRegles.php:49` : `strlen(...)` remplacé par `mb_strlen($row[$key], 'UTF-8') > $max`. Bornes 150/500 désormais comptées en caractères, cohérentes avec les `maxlength` du formulaire. Couvert par `correction-final-utf8-V2.json` (150/500 accentués acceptés, 151/501 refusés).

### Décision technique Claude-A (défaut : conserver, mais tester la présence de la section C10)

- **Appliquée.** Le couplage de l'injection au rendu de C-10 est conservé (défaut proposé) et désormais couvert : le parcours HTTP teste la présence **et** la position de la section (`C10_champs_meme_formulaire`, `C10_section_sous_bouton_inchangee`). Une disparition silencieuse serait détectée.

---

## 2. Résultat des tests

- **Vérificateur du lot** : `python -B wp/tests/demo/c22-verifier.py` → **code 0**.
  Sortie : `C22 VERIFIED: T01 1123/34569; native 19; HTTP/browser 40; C09 382; action 8793 pending / subscription 101; C21 export/erase behavior; sources and reset exact`.
  Ce rejeu contrôle l'intégrité des reçus scellés, exécute en direct le contrat de confidentialité C-21 (export/effacement réels) et relit l'état du site (profils, action 8793 *pending*, souscription 101, C09 382/382, observateur absent).
- **Receipt PHPUnit (scellé, vérifié par le vérificateur)** : `correction-t01-V2.log` → **1 123 tests / 34 569 assertions**, zéro échec/erreur/ignoré ; **14 outils / 279 contrôles**, zéro échec. Les cinq tests `NewslettersReglesTest` (dont `testConfirmerUnDefautNInferePasUnConsentementAvantAction`) sont découverts ; `T01 CLEANUP : absence verifiee` présent.
- **Parcours de correction (reçus vérifiés)** : `retired` 9/9, `history` 8/8, `utf8` 6/6, `privacy` 6/6 ; HTTP/Chromium 40/40 ; natif 19/19 ; mutations témoins rouges-attendues détectées.

**Limite de ce tour :** le rejeu complet de la suite PHPUnit via `wp\tests\rejouer.ps1` n'a pas pu être lancé directement dans cette session non interactive (commande bloquée par la couche de permissions). Je m'appuie donc, pour les compteurs PHPUnit, sur le reçu scellé dont le vérificateur contrôle l'intégrité (empreintes des 39 reçus historiques comparées, marqueur `T01_RESULT` unique, `REJEU : … PASS`). Le contrat de confidentialité C-21 et l'état du site, eux, ont bien été **ré-exécutés en direct** par le vérificateur. Ce n'est pas un défaut du lot : même limite environnementale que Codex au tour précédent, pas un rouge.

---

## 3. Régressions ou modifications non demandées

Aucune régression ni modification hors périmètre détectée.

- `Confidentialite.php` et `Newsletters.php` : **non modifiés** (absents du diff) — le fichier partagé C-21 est resté intact, comme demandé.
- `NewslettersReglages.php` / `NewslettersRegles.php` : changements strictement limités aux corrections C22-01 et C22-02.
- `c22-verifier.py`, `c22.py`, `c22-http.py` : alignés sur C22-03 (contrat comportemental, identifiant de 4e lettre rendu unique par label pour éviter les collisions entre rejeux). Pas d'affaiblissement des contrôles existants.
- Un reçu rouge est conservé honnêtement (`correction-http-V2.json`, sélecteur CSS d'erreur obsolète) ; le rejeu vert vise l'identifiant Settings API réel, sans toucher au code métier. Aucun rouge rebaptisé vert.
- Incident de rangement signalé par Hermès (un log temporaire déposé un instant sous `production/B-05/` puis déplacé) : sans effet sur C-22. À noter hors de ce lot, il reste dans l'arbre un répertoire parasite `prefix}u0024s` et un fichier `production/B-05/correction-preparation-V2.log` — **à vérifier côté ménage**, mais étranger au périmètre C-22.
- Questions ouvertes **inchangées** et non bloquantes : position visuelle de la section C-10 (défaut : conserver — pour Ced) ; inscription à la création (défaut : Non — pour Imagine). Les deux sont des choix déjà identifiés dans la fusion, pas des problèmes de fond nouveaux.

---

## 4. Verdict

**Prêt pour la validation de Ced.**

Les trois instructions de `corrections/C-22.md` (C22-01, C22-02, C22-03) sont appliquées, ainsi que la décision technique Claude-A. Le vérificateur du lot passe au vert (code 0), le contrat de confidentialité C-21 a été ré-exécuté en direct, et le reçu PHPUnit scellé est intègre (1 123/34 569, zéro échec). Aucune régression ni modification non demandée côté C-22. Aucun problème de fond restant : les seuls points ouverts sont la question visuelle (Ced) et la question métier de consentement à la création (Imagine), toutes deux dotées d'un défaut prudent et non bloquantes.

Rappel doctrine : ce verdict de vérification n'est pas un GO. La clôture visuelle et la décision sur le consentement à la création restent à Ced.
