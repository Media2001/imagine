# Relecture A-20 — Ce que paient aujourd'hui les abonnés en ligne

Relecteur : Claude, indépendant. Date : 2026-11-26. Je n'ai pas ouvert `codex.md`. Pas de fusion à ce stade.

Code relu : `wp/outils/bascule/a20/` (Analysis.php, Inventory.php, Command.php, confine.py, inventorier-tarifs, README.md). Tests : `wp/tests/a20/` (unit.php, seed.php, inside.py, run.py, matrix.py, test_launcher.py, verify.py, style.py, pure-probe.php). Production : `production/A-20/`.

## Rejeu de la suite autorisée

Commande jouée, sans argument : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Dernière ligne :

> `REJEU : 1123 tests, 34569 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`

Dont, parmi les 13 outils : `T01 TOOL : a20 ; 23 controls ; 0 failures ; exit=0`. Conteneur jeté, réseau=none, dépôt monté en lecture seule, nettoyage vérifié.

Limite de ce rejeu : `rejouer.ps1` ne joue que la **couche PHP pure** d'A-20 (les 23 contrôles de `unit.php`). L'acceptation native (banc classique + HPOS, empreintes avant/après, absence de canari dans les sorties réelles, parcours nominal du mode d'emploi exécuté) vit dans `inside.py` / `matrix.py`, qui exigent un conteneur Linux + un staging et ne sont **pas** rejouées par la commande autorisée. Je les ai relues statiquement et j'ai lu les reçus scellés du paquet (`production/A-20/candidate-verification.json` : 216 PASS, 0 FAIL ; `verification.json` : exit 0 ; matrice Windows exit 0). Je n'ai pas pu les rejouer indépendamment ici (exécution Python hors `rejouer.ps1` refusée par le bac à sable). Voir point mineur 1.

## 1. Conformité

Le lot fait ce que demande le brief, en lecture seule, via le lanceur confiné d'A-11/A-12. Correspondance exigence → code :

- comptes par produit/variation et par état → `Analysis::analyse`, `products[].states` (Analysis.php:68-73).
- périodicité réelle (intervalle + période) et nombre de non-annuels → `products[].schedules` et `non_annual` (Analysis.php:74-79).
- montants récurrents distincts + effectif, seuil 5 → « autres montants » (effectif seul) → `products[].amounts` / `other_amounts` (Analysis.php:91-99).
- abonnements à plusieurs lignes produit, avec ligne de frais, avec ligne de port → `multiple_product_lines`, `with_fee_line`, `with_shipping_line` (Analysis.php:50-53).
- par pays de livraison : effectif + nombre avec port, seuil 5 → « autres pays » → `countries` / `other_countries` (Analysis.php:57-60, 104-115).
- devise ≠ site, montant récurrent nul → `foreign_currency`, `zero_recurring_total` (Analysis.php:54-56).

Rattachement au cahier des charges : §3.4 (produit annuel, trois tarifs, livraison à l'étranger) et §4.3 (« Abonnés en ligne actuels ») — cités dans le brief, respectés dans l'esprit : le lot **ne modifie rien, ne propose aucune correspondance ancien/nouveau tarif, ne qualifie aucune anomalie**. Les définitions embarquées (Analysis.php:116-146) le répètent champ par champ.

Vie privée des sorties : seulement identifiants de produit, états, codes pays ISO, montants agrégés, nombres. Aucun identifiant de compte/abonnement/commande, aucun nom, aucune adresse, aucun chemin. Règle de la voie 1 respectée : refus = codes fermés `A20_/A11_/A12_` ; le seul nom technique possible (`A11_DROPIN_UNSUPPORTED {"file":"wp-content/db.php"}`) vient de la liste fermée A-11, pas du site (README.md:22).

Interprétations faites et **signalées** (notes.md:17-19, README.md:26-34), conformes à la doctrine §1 :
- « annuel » = `1 year` ou `12 month`, sans conversion semaines/jours ;
- montant = total récurrent enregistré `get_total('edit')` (taxes/frais/port/remises inclus), pas un prélèvement futur garanti ni un prix catalogue ;
- plusieurs produits : total entier compté dans chaque groupe, sans répartition (les groupes ne s'additionnent pas) ;
- pays = livraison enregistrée, sans repli sur la facturation ; vide/inconnu séparé ;
- seuil 5 des montants par couple produit/variation + devise/montant ; seuil 5 des pays global, tous produits.

## 2. Exactitude métier (déroulé à la main)

J'ai déroulé le banc de `seed.php` (9 abonnements, 1 expiré exclu) et comparé au code et aux attendus des tests.

Entrée vivante (8 abonnements) :
- i0–4 : actif, `year`/1, 100.00 EUR, BE, 1 ligne (produit simple) ;
- i5 : pending, `month`/1, 9.17 EUR, FR, ligne de port (2.00) + ligne de frais (0) ;
- i6 : on-hold, `year`/1, 0 USD, pays vide, variation ;
- i7 : pending-cancel, `year`/1, 80.19 EUR, DE, 3 lignes (produit ×2 + variation), port (0.00) ;
- i8 : `expired` → **exclu**.

Résultat recalculé à la main :
- `live_subscriptions` = 8 ✓.
- Produit simple : count 7 (i0–5 + i7, dédoublonné), états {active:5, pending:1, on-hold:0, pending-cancel:1}, schedules [{month,1,1},{year,1,6}], non_annual 1, amounts [{EUR,100.00,5}], other_amounts 2 (9.17 et 80.19, chacun <5) ✓.
- Variation : count 2 (i6 + i7), états {on-hold:1, pending-cancel:1}, schedules [{year,1,2}], non_annual 0, amounts [] (0.00 et 80.19 <5), other_amounts 2 ✓.
- Pays : BE count 5 visible (0 port) ; FR + DE <5 → other_countries count 2, with_shipping 2 ; vide → unknown_country count 1, with_shipping 0 ✓.
- Globaux : multiple_product_lines 1 (i7), with_fee_line 1 (i5), with_shipping_line 2 (i5, i7), foreign_currency 1 (i6 USD), zero_recurring_total 1 (i6) ✓.

Tout concorde avec les attendus codés (inside.py:51-56) et avec le code. Montant à un seul abonnement (9.17, 80.19) correctement basculé en « autres montants ». Canari produit (`A20_PRODUCT_NAME_PRIVATE_CANARY`, etc.) absent, car seuls les identifiants techniques transitent.

Cas limites vérifiés à la main sur `Analysis::decimal` et le seuil (couverts par unit.php) :
- `-0.00`, `000.0000` → `0.00`, comptés comme nuls (Analysis.php:150-160) ✓.
- `12 month` compté annuel, `week`/`day` non convertis (Analysis.php:78-79) ✓.
- lignes produit répétées dédoublonnées par couple produit/variation via `$seen` (Analysis.php:61-67) ✓.
- pays à exactement 5 mais inconnu : ne fuit jamais, reste dans `unknown_country` (Analysis.php:106-108) ✓.
- même montant, deux devises : jamais regroupé (clé `devise:montant`, Analysis.php:80) ✓.
- bascule du seuil à 4 (masqué) / 5 (visible) ✓ (unit.php:63-66).
- données hors forme (`interval` 0, devise non `[A-Z]{3}`, `1e3`, produit non entier) → refus fermé `A20_DATA_UNSUPPORTED`, aucune donnée source (Analysis.php:33-47) ✓.
- ordre d'entrée indifférent (tris déterministes), `deterministic_input_order` ✓.

Aucun écart trouvé.

## 3. Tests

- Suite autorisée au vert (voir ligne REJEU). Les 23 contrôles PHP purs (`unit.php`) sont exécutés dans le rejeu.
- Les tests vérifient la règle, ils ne répètent pas le code : `unit.php` code en dur les agrégats attendus et les recompare ; `inside.py` construit un vrai banc WCS puis compare à un oracle indépendant (`seed.php` renvoie `A20_JSON`) ; vérification systématique de l'absence de canari dans toutes les sorties et empreintes.
- Cas limites couverts (seuils, zéro signé, 12 mois, dédoublonnage, devises mixtes, refus) — pas seulement le nominal.
- Parcours nominal du mode d'emploi : testé (inside.py:62-67) en relisant la ligne du README et en la lançant avec ses **seuls** cinq jetons (python3 + script + 3 arguments), sortie `A20_OK tarifs.json tarifs.md`, rapport identique au nominal. `test_launcher.py:24-31` fixe en plus le contrat des deux lignes partagées. **Mais** cette exécution n'est jouée que dans la matrice native, hors `rejouer.ps1`.
- Pureté : `Analysis.php` ne contient ni `wpdb`, ni `wc_get`, ni `get_option`, ni `PDO`, ni `WC_Subscription` (test_launcher.py:32-35) ; rejouée sous `php -n`, écritures interdites, puis déplacée hors arborescence WordPress avec reçu identique (run.py:44-51).

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle. Fixtures `@example.org`, noms manifestement inventés, canaris.
- Lecture seule prouvée : compte SQL SELECT + transaction READ ONLY (réemploi A-11/A-12), empreintes des 55 tables et des fichiers identiques avant/après, même avec compte `root` (inside.py:90-91, 101-108). Confinement obligatoire : sans `A20_CONFINED=1` et sans absence de `mail`/`exec`, refus `A20_CONFINEMENT_REQUIRED` (Command.php:55-57) ; PHP brut hors lanceur refusé (inside.py:70-71).
- Sorties hors site et hors dépôt (`disjointOutput` réutilisé), dossier 0700, fichiers 0600 (Command.php:66-72), refus si la sortie existe, est un lien, ou n'est pas sœur de l'audit (Command.php:38-47).
- Garde d'audit : schéma `imagine-a02-audit-v1`, cohérence du stockage classique/HPOS, sinon `A20_AUDIT_GUARD` / `A20_AUDIT_STORAGE_MISMATCH` (Command.php:49-60).
- Refus fermés et sans donnée source : symlink, dropins, surcharge de config, cache/pare-feu (inside.py:72-98). Canari absent de tous les artefacts (inside.py:109).
- Paywall : sans objet (aucune sortie web, aucun texte réservé).

Rien à signaler.

## 5. Doctrine

- Standard d'abord : objets et lectures délégués à WooCommerce/Subscriptions (`wcs_get_subscriptions`, CRUD `get_*('edit')`), quatre sources officielles citées et empreintées (README.md:7-10, `official-sources.json`). Le sur-mesure se limite au comptage PHP pur et au masquage. ✓ (doctrine §4).
- Logique métier hors WordPress : `Analysis.php` testable sans base ni WP ; `Inventory.php` est la couche fine de branchement. ✓ (doctrine §4).
- Conventions §5 : `declare(strict_types=1)`, namespace `Imagine\`, PSR-12 (PHPCS 0 erreur / 0 avertissement), textes FR, aucun code tiers modifié (hooks/CRUD seulement), `README.md` présent. ✓
- Rejouable, conteneur jetable, aucun Git/déploiement/compte réel. ✓

## 6. Études

Sans objet : lot de code.

---

## Verdict : Conforme

Aucun point bloquant ni important. Points mineurs ci-dessous. **Ce verdict n'est pas un GO** : il ne vaut que pour la clôture d'un lot de code, et il reste la seconde relecture + la fusion.

**Mineur 1 — couverture du rejeu autorisé.** `rejouer.ps1` ne rejoue que la couche PHP pure (23 contrôles). Les preuves lourdes (native classique+HPOS, empreintes avant/après, parcours nominal exécuté, absence de canari dans les sorties réelles) ne sont pas dans cette commande ; je les ai relues et j'ai contrôlé les reçus scellés (216 PASS / 0 FAIL, exit 0), sans pouvoir les rejouer ici.

**Mineur 2 — `without_product_line` : léger dépassement du périmètre.** Le brief n'énumère pas « sans ligne de produit » parmi les comptes demandés. Le code l'ajoute (Analysis.php:51) comme compte neutre, utile à la complétude et sans donnée sensible. À confirmer comme souhaité.

**Mineur 3 — « annuel » = `1 year` ou `12 month`.** Interprétation signalée (brief silencieux sur l'équivalence). Elle n'engage ni argent, ni droit, ni comptabilité ; elle fixe seulement un comptage.

**Observation — emplacement.** L'outil, en lecture seule, vit dans `wp/outils/bascule/` (famille des scripts de transformation, doctrine §4), par cohérence avec la famille audit A-02/A-11/A-12 dont il réutilise le lanceur confiné. Acceptable vu le précédent ; à garder tel quel.

**Observation — `PRET`.** `production/A-20/PRET` existe et dit honnêtement « pret a relire, non clos ; aucun GO reel ». Cohérent avec un candidat à relire, pas une mise en production.

### Décisions techniques, défaut proposé (Hermès applique, Claude arbitre après)

- **Q1** — `without_product_line` : le garde-t-on ? *Défaut proposé : oui* (compte neutre, aide à la cohérence des totaux, aucune donnée sensible).
- **Q2** — « annuel » = `1 year` ∪ `12 month` : *Défaut proposé : oui* (équivalence sémantique, déjà documentée).
- **Q3** — rejeu de la matrice native hors `rejouer.ps1` : *Défaut proposé : accepter la preuve scellée + relecture statique pour la relecture ; le parent/Ced rejoue la matrice native avant clôture définitive.*

### Pour Imagine (métier)

Rien à trancher dans ce lot : la grille et toute correspondance ancien/nouveau tarif sont des décisions d'Imagine (chapitre 7), hors de cet outil, comme le brief l'exige.

### À arbitrer par Ced (visuel ou réel)

Aucune question visuelle ni touchant au réel dans ce lot.

---

**Suite** : `relectures/A-20/codex.md` existe mais n'a pas été ouvert. Je m'arrête après cette relecture ; la fusion (`corrections/A-20.md`) n'est pas faite, conformément à la consigne.
