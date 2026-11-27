# Relecture indépendante — Lot C-29 « La fiche du contact pour Brevo, sans Brevo »

Relecteur : Claude (indépendant). Date : 2026-11-27.
Brief : `briefs/C-29-la-fiche-du-contact-pour-brevo.md`. Cahier des charges : §3.10, §4.4, §2.2.
Code lu : `wp/plugins/imagine-site/ContactBrevoRegles.php`, `ContactBrevo.php`, `tests/ContactBrevoC29Test.php`, `tests/fixtures/c29-cases.php` ; dépendances `Personnalisation.php`, `Newsletters.php`, `EnvoiRelations.php` ; production `production/C-29/`.

> `codex.md` existe dans `relectures/C-29/` mais n'a **pas** été ouvert. Fusion non faite (voir fin).

---

## 1. Conformité

- **Calcul pur unique** : `ContactBrevoRegles::fiche(array $source)` est bien une seule fonction, sans WordPress, réseau ni disque. Conforme au brief.
- **Qui a une fiche** : email recevable **et** au moins un choix d'origine `lecteur` (`ContactBrevoRegles.php:12-34`). Sans email → `email_non_recevable` ; sans choix → `aucun_choix_lecteur` ; désinscrit de tout → fiche réduite `{statut:a_retirer}`. Conforme.
- **Statut** : `active` seul ⇒ `abonne`, sinon `non_abonne` ; bénéficiaire offert/groupé ⇒ `inconnu` (`ContactBrevoRegles.php:48`). Réutilise l'état d'abonnement d'A-14 (pas le droit numérique C-06). Conforme à « abonné = abonnement actif ».
- **Tarif** : lu sur l'abonnement actif via liste fermée en réglage ; absent, hors liste, contradictoire ou incomplet ⇒ `inconnu`, jamais une valeur devinée (`ContactBrevoRegles.php:35-50`, `ContactBrevo.php:128-140`). Conforme.
- **Étiquettes** : prises **telles quelles** de `Personnalisation::attributsConnecteur($id)` (`ContactBrevo.php:198`), sans recopier la règle du consentement distinct. Conforme au brief et au §4.4 (consentement distinct) / §3.10 (étiquettes si consenti).
- **Écran lecture seule** « Ce qui partirait vers Brevo » : fiche/raison pour un compte choisi + totaux par statut, même droit que le tableau de bord C-19 (`ContactBrevo.php:88-125`, `TableauBordAdmin::autorise()`). Conforme.
- **Clés internes** : `email, statut, cooperateur, tarif, newsletters, personnalisation` ; correspondance Brevo repoussée au branchement. Conforme.
- **Le lot ne transmet rien** : aucun appel, clé, file, tâche, écouteur ; rien n'est enregistré (calcul à la demande). Odoo non concerné (§2.2 respecté). Conforme.
- **Cinq lignes « standard d'abord »** : présentes dans `README.md:560-568`, avec liens vers les pages officielles WordPress.org de l'extension Brevo (`mailin`) et de Brevo for WooCommerce. Sources citées, conforme à la doctrine §4.

**Aucune interprétation non signalée relevée.** Les « inconnu » assumés sont tracés dans `NOTE.md` et `A-VOIR.md`.

## 2. Exactitude métier — cas déroulés à la main

Déroulé manuel de `ContactBrevoRegles::fiche` sur les cas du cahier des charges et l'oracle indépendant `wp/tests/demo/c29-attendus.php` :

- **A-CARTE** (abonné actif, choix lecteur, perso + consentement) → `statut=abonne, tarif=normal-1, newsletters=[principale], personnalisation=présente`. Conforme à l'oracle ligne 11.
- **A-GRACE / A-SUSP** (`on-hold`) → `actifs=∅` ⇒ `non_abonne, tarif=inconnu`, malgré l'accès de grâce. Conforme (oracle 16-17). Vérifie que l'état prime sur le droit d'accès.
- **A-NONRENOUV** (`pending-cancel`) → `non_abonne`. Conforme (oracle 19). Le lot ne confond pas « actif pour Brevo » et « accès jusqu'au terme ».
- **A-ETRANGER / A-ECHEANCE** (actif, produit hors liste) → code tarif `''`, `in_array('', autorisés)` faux ⇒ `complet=false` ⇒ `abonne, tarif=inconnu`. Conforme (oracle 20,22).
- **V-DEC-FIN** (désinscription de tout) → `newsletters=∅`, `retrait=true` ⇒ fiche strictement `{statut:a_retirer}`, sans email ni tarif. Conforme (oracle 9).
- **A-SANSMAIL** (email non recevable, choix préparé) → `email_non_recevable`, pas de fiche, **ne devient pas** une demande de retrait. Conforme (oracle 21) et au brief.
- **P-COOP** → `non_abonne, cooperateur=oui` (attribut B-06, sans droit d'abonné). Conforme (oracle 32).
- **Conflit de tarifs** (`conflit`, deux actifs normal-1 + normal-4) → deux tarifs distincts ⇒ `inconnu`. Conforme (fixture).
- **Changement de liste choisie** (`autre_liste`, principale refusée + coop choisie) → `newsletters=[coop]`, le retrait partiel est ignoré car un choix subsiste. Conforme.
- **Choix automatique seul** (`defaut_creation`, origine ≠ lecteur) → `aucun_choix_lecteur`, pas de fiche. Conforme : seul le choix du lecteur compte.

Les 27 profils C-09 de l'oracle correspondent au comportement tracé. Aucun écart métier détecté.

**Cas limites** : états WCS complets (5), retrait, liste supprimée, origine automatique, bénéficiaire, coopérateur, hors-liste, liste fermée, conflit, projection vide — tous couverts par la fixture et cohérents.

## 3. Tests

**Rejeu de la suite PHP autorisée, exécuté** (conteneur jetable, `network=none`, dépôt monté en lecture seule) :

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1
```

Dernières lignes du rejeu :

```
PAQUETS : 11 vérifiés, 1 échecs ; hors rejeu : A-31 (journaux absents) ; A-32 A32_PACKAGE_DRIFT
OUTILS : 22 outils, 791 contrôles, 6 échecs ; hors rejeu : aucun
REJEU : 1204 tests, 36667 assertions, 0 échecs, 1 erreurs, 0 ignorés — FAIL
```

Lecture :

- **Le lot C-29 est vert.** `ContactBrevoC29Test` : 3 tests, 47 assertions, 0 erreur, 0 échec (JUnit, `ContactBrevoC29Test.php:1331`).
- **Le rejeu global rend FAIL**, mais uniquement hors C-29 :
  - outil **a31** : 238 contrôles, **6 échecs**, exit 1 ;
  - paquet **A-32** : contrôle `A32_PACKAGE_DRIFT` ;
  - **A-31** exclu (« journaux absents »).
  Les fichiers `wp/tests/a31/` sont d'ailleurs modifiés dans l'arbre de travail (`inside.py`, `run.py`, `seed.php`, `verify.py`, `test_fusion.py`, `test_report.py`) : chantier A-31 en cours, **étranger à C-29**.
- `NOTE.md:65` annonce « A31/A32 restent rouges hors lot, aux codes connus ». Cohérent avec ce que montre le rejeu. Je ne peux pas, depuis les seuls éléments C-29, certifier que `A32_PACKAGE_DRIFT` est sans lien ; mais le code et les tests C-29 ne touchent pas ces paquets.
- Les recettes native/HTTP (`c29.py`, `c29-http.py`) ne font **pas** partie de `rejouer.ps1` : elles exigent le site et n'ont pas été rejouées (hors commande autorisée). Leur contenu est décrit en NOTE ; non vérifié de ma main.

**Qualité des tests C-29** : la matrice pure compare à un attendu écrit à la main (indépendant), et contrôle l'absence de mutation de l'entrée (`ContactBrevoC29Test.php:15-16`). Le test ne se contente pas de répéter le code. La sanitation de la liste fermée est testée sur valeurs hostiles (`<script>`, clé `0`). Bonne couverture des cas limites.

## 4. Sécurité et données

- **Aucun secret, aucune donnée réelle.** Fixtures en `@example.org`, noms inventés. Conforme.
- **Droits** : écran de consultation gardé par `verifier()` → `TableauBordAdmin::autorise()` + méthode GET/HEAD (403 sinon, 405 sur autre méthode) (`ContactBrevo.php:67-76`). Réglage gardé par `manage_options` (`ContactBrevo.php:55`, `pageReglages`). Conforme.
- **Échappement** : toutes les sorties passent par `esc_html`/`esc_attr`/`esc_url`/`esc_textarea` ; la fiche est `wp_json_encode` puis `esc_html` dans `<pre>` (`ContactBrevo.php:116`). Pas d'injection vue.
- **Entrée** : `compte` validé par regex `^[1-9][0-9]*$` + égalité stricte après cast (`ContactBrevo.php:96`). Robuste.
- **Lecture seule effective** : `nocache_headers()` + `Cache-Control: private, no-store` (`ContactBrevo.php:91-92`) ; aucune écriture d'option/méta par l'écran. Le formulaire est en GET. Conforme au brief (« zéro requête sortante, rien enregistré »).
- **Pas de paywall ici** : le lot n'expose aucun texte réservé.

## 5. Doctrine

- **Standard d'abord** : le code ne refait pas l'extension Brevo ; il calcule les règles du site (coopérateur, actif-seulement, tarif) que les extensions ne déduisent pas. Justifié et cité.
- **Logique métier hors WordPress** : règle pure isolée, couche fine native par-dessus. Conforme au §4 de la doctrine.
- **Conventions §5** : `declare(strict_types=1)`, namespace `Imagine\Site`, préfixe `imagine_` (`imagine_brevo_tarifs`, `imagine-contact-brevo`, `imagine-brevo-tarifs`), aucune modification d'extension tierce (lecture seule via `wcs_get_subscriptions`, `EnvoiRelations`). README à jour. Conforme.

---

## Verdict

**Conforme** pour le périmètre C-29 (le code fait ce que demande le brief, ni moins ni plus ; tests du lot au vert ; sécurité et doctrine respectées). Rappel : un verdict de relecture **n'est jamais un GO**.

Points classés :

**Bloquant**
- Aucun propre à C-29.

**Important**
1. `tests/rejouer.ps1` **rend FAIL** (section 3). L'affirmation « tests au vert » ne vaut donc **pas pour le dépôt**, seulement pour le lot C-29. À clôture, la doctrine exige une suite verte : il faudra soit que A-31/A-32 repassent au vert, soit un arbitrage explicite les sortant du périmètre de clôture. Voir « Décisions techniques ».

**Mineur**
2. `ContactBrevo.php:105-114` : `__($label, 'imagine-site')` et `__($reasons[$result['raison']], …)` passent une **variable** à la fonction de traduction. Les chaînes (`Abonné`, `Non-abonné`, …) sont littérales dans les tableaux, donc l'affichage fonctionne, mais l'extraction `.pot` (makepot/WPCS `WordPress.WP.I18n`) ne les voit pas. Proposition : déclarer les libellés avec `__()` sur chaîne littérale dans le tableau, puis indexer. Non bloquant.
3. `ContactBrevo.php:102` : `bilan(get_users(['fields'=>'ID']), …)` lit tous les comptes et, par compte, recalcule `attributsConnecteur`, `preferences`, `catalogue` et plusieurs métas (N lectures). Acceptable et **assumé** pour la démo (`NOTE.md:54`), mais à requalifier avant tout volume réel. Proportionné au lot.

---

## Décisions techniques, défaut proposé (Hermès applique, Claude arbitre après coup)

- **Rouge global du rejeu (A-31 / A-32).** Question : la clôture d'un lot de code tolère-t-elle que `rejouer.ps1` rende FAIL sur des paquets voisins déclarés « rouges connus » ? **Défaut prudent proposé** : non — tant qu'une suite autorisée rend FAIL, le lot reste « prêt technique pour relecture » (ce que dit `PRET`) mais **pas clôturable**. Reporter la remise au vert d'A-31/A-32 à leurs lots respectifs, sans y toucher depuis C-29.

## Pour Imagine (réglage, défaut prudent)

- **Fiche « à retirer » sans identifiant.** La fiche réduite ne porte que `{statut:a_retirer}` — strictement conforme au brief. Au branchement, le futur connecteur devra identifier le contact Brevo à retirer par le compte (email côté site), pas par la fiche. Question fermée : **le connecteur identifiera-t-il le contact à retirer par le compte WordPress (et non par un email porté dans la fiche) ?** **Défaut proposé** : oui — on garde la fiche réduite telle quelle (conforme au brief) ; identification par le compte au moment du branchement. À confirmer par Imagine quand le mapping Brevo sera arrêté.

---

## Ce qui a dû rester à « inconnu » (demandé par le brief)

- Statut et tarif d'un **bénéficiaire** offert/groupé (question chez Imagine).
- Tarif d'un abonnement **actif sans correspondance** dans la liste fermée, **hors liste**, **ligne absente** ou **tarifs contradictoires**.
- Grille tarifaire réelle et noms d'attributs Brevo : non arrêtés ; défaut de production **vide** (tout `inconnu`), six correspondances **fictives** C-09 pour la seule démo.

---

## Suite

Rapport écrit. `relectures/C-29/codex.md` existe mais n'a pas été lu, conformément à la consigne. **Fusion non effectuée** et non demandée à ce stade.
