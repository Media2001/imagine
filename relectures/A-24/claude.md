# Relecture indépendante — A-24 (adresses d'expédition)

Relecteur : Claude. Date : 2026-11-26. Je n'ai pas lu `codex.md`. Pas de fusion à ce stade.

## Rejeu de la suite

Commande autorisée, sans argument :

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Dernière ligne :

`REJEU : 1126 tests, 35550 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`

Ligne outils : `OUTILS : 16 outils, 311 contrôles, 0 échecs ; hors rejeu : aucun`. Outil A-24 : `a24 ; 17 controls ; 0 failures ; exit=0`. Isolement confirmé par la sortie : `network=none ; rootfs=ro ; mount=…/wp:ro ; ports=none ; cap-drop=ALL ; no-new-privileges`.

**Portée du rejeu autorisé.** Pour A-24, `rejouer.ps1` ne rejoue que l'**unité PHP pure** (`unit.php`, 17 contrôles). L'adaptateur natif (classique + HPOS, 206 contrôles), le confinement et la **suite Python** (14 tests/contexte, cp1252 compris) ne sont **pas** couverts par cette commande. Je ne les ai pas réexécutés (la commande imposée est sans argument) : je les ai relus et contrôlés sur la matrice de preuves `production/A-24/preuves/final/`. Si Ced veut une preuve indépendante du natif/Python, il faut la rejouer hors de cette commande.

## 1. Conformité

- **Périmètre respecté.** Lecture seule, comptes seulement ; aucun repli facturation→livraison, aucune correction, aucun jugement postal. Conforme au brief (« Ce lot ne corrige aucune adresse… ») et à §3.13 (liste d'envoi) / §4.3 (abonnés repris).
- **Vivants = A-20.** `active, pending, on-hold, pending-cancel` (`Inventory.php:31`), les terminaux exclus (seed `cancelled`/`expired`). Conforme.
- **Obligations natives, pas inventées.** `WC()->countries->get_address_fields($country,'shipping_')` (`Inventory.php:44`) ; liste des champs fermée (`Analysis::FIELDS`), refus fermé si un champ hors liste apparaît (`A24_NATIVE_FIELDS_UNSUPPORTED`). Le « standard d'abord » (10 lignes) est présent dans `README.md` avec trois sources officielles datées. Conforme.
- **Aucune donnée ne sort.** Sorties = nombres, codes pays, noms de champs d'une liste fermée. Les refus sont des codes fermés (`refusals.json`), un seul détail possible (nom technique de drop-in). Conforme à la règle voie 1.
- **Neutralisation observée sans la modifier** (`Inventory.php:66` lit la marque `imagine_staging_disabled_plugins`, A-01 inchangé). Conforme au brief (« Regarde ce qu'il en fait, sans le modifier »).

Interprétation signalée par Hermès (notes.md, README.md) — voir point important ci-dessous.

## 2. Exactitude métier

Déroulé à la main du banc (`seed.php`, 12 vivants + 2 terminaux exclus) et comparaison à `preuves/final/cp1252/classic-addresses/expedition.json` :

- 12 abonnements ; BE = {i0,i1,i2,i3,i4,i11} = 6 ; « autres pays » = {FR, absent×2, ZZ, AE, US} = 6. **Exact.**
- `shipping_empty` = 1 (i6, adresse vide), `empty_with_billing` = 1 (i6, facturation remplie). **Exact.**
- `country_absent` = 2 (i6, i7), `country_unknown` = 1 (i8=ZZ). **Exact.**
- `missing_required` : `first/last/addr1/city` = 1 (i6) ; `country` = 2 (i6, i7) ; `postcode` = 2 (i5=FR sans CP, i6) ; `state` = 2 (i10=US, **et i8=ZZ** — défaut natif `state.required=true` non surchargé pour un pays inconnu) ; `company/address_2/phone` = 0 (optionnels). `missing_any` = 5 (i5,i6,i7,i8,i10). **Exact.**
- `different_from_account` = 2 (i1 casse, i2 espace), `account_unavailable` = 1 (i11, `customer_id=0`). **Exact** — mais voir le point important sur la sémantique.

Cas limites bien couverts : AE (ni CP ni État requis) → i9 ne manque rien ; pays inconnu ZZ → État requis par défaut natif ; `missing_any` ≤ somme ; cohérence overall = somme des groupes (vérifiée aussi par `report.py:77`).

**Neutralisé** (`classic-neutralised/expedition.json`) : tout passe à `inconnu après neutralisation` sauf effectifs (12/6/6), pays (`country_absent`=2, `country_unknown`=1, `missing_required.shipping_country`=2) et `account_unavailable`=1. Jamais de zéro faux. **Conforme** au brief.

**Immobilité** vérifiée : `classic-db-before.json` == `classic-db-after.json` et idem HPOS (comparaison binaire OK). Canari `A24_STREET_PRIVATE_CANARY` **absent** de toutes les preuves (grep récursif : aucun match).

## 3. Tests

- `unit.php` (17 contrôles) teste de vraies valeurs dérivées, pas une copie du code : seuil 5/4, mise en commun « autres pays », optionnels, chaîne « 0 » non vide, espaces seuls = vide, refus champ hors liste, neutralisation. Bonne qualité.
- `boundaries.py` : canari sur chaque canal réel (stdout, stderr, affichage, shutdown ×3, débordement, UTF-8 invalide), faux succès / faux refus forgé, fichier en trop, markdown altéré, JSON invalide, rapport partiel → tous refusés avant publication ; **mutation sans gardien → canari effectivement détecté en mémoire** (prouve la valeur du gardien A-22) ; override natif → obligations non codées en dur (`native-required-override` : company/address_2/phone=8, postcode=1). Couverture des cas limites sérieuse.
- Refus confinement (`A24_CONFINEMENT_REQUIRED` hors conteneur), audit (schéma, stockage), symlink, drop-ins, override wp-config, transaction READ ONLY même avec `DB_USER=root`. Bien couvert.

Réserve : je n'ai **pas** rejoué moi-même le natif/Python (commande autorisée limitée) — attesté sur la matrice de production uniquement.

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle. Fixtures `@example.org`, noms manifestement inventés. Conforme §3 doctrine.
- Sorties fermées, aucun chemin ni nom tiré du site, y compris en erreur. Confinement A-12 + façade SQL + READ ONLY + gardien A-22 réutilisé **sans modification du code tiers**.
- Étanchéité : le canari ne sort sur aucun canal ; prouvé que sans le gardien il sortirait. Bon.

## 5. Doctrine

- Standard d'abord : respecté (API natives, aucune liste postale inventée).
- §5 conventions : `declare(strict_types=1)`, namespace `Imagine\…`, PHP 8.2, README présent. Conforme.
- Rejouable / non-régression / idempotence : outil en lecture seule, rejeu identique (`classic-repeat` prévu), empreintes stables. Conforme.

## Points classés

**Important**

1. **Sémantique « à la casse et aux espaces près » (brief, puce différence au compte) — interprétation à confirmer.** Le code compare **à l'octet près** (`Analysis.php:29` ; README « casse/espaces significatifs »), et le banc ne fabrique de différence au compte que par la casse (i1) et l'espace (i2) : `different_from_account`=2 repose **entièrement** sur ces deux écarts. Or « à … près » en français se lit le plus souvent comme « en ignorant … » (deux adresses ne différant que par la casse/les espaces seraient alors **identiques** → le nombre serait 0). Lecture inverse défendable (« précis jusqu'à la casse et l'espace »), et Hermès l'a signalée — mais le choix pilote directement le chiffre remis à Imagine. Comme aucune donnée réelle n'est engagée, c'est une question **métier** avec défaut.

**Mineur**

2. **SHA du gardien A-22 périmé dans le rapport.** `RAPPORT.md` annonce « gardien commun A-22 réutilisé tel quel, SHA-256 `ce62d8…db9` ». Le gardien actuel `wp/outils/bascule/stream_guard.py` fait `c913c792…` (corrigé par A-22 à 17 h 53, après A-24 — cf. `FINALISATION.md`). La réutilisation fonctionnelle reste verte (rejeu PASS), mais l'empreinte citée ne correspond plus. À réaligner pour ne pas tromper une vérification ultérieure.

3. **Portée de preuve.** Dire explicitement, côté livraison, que `rejouer.ps1` ne rejoue pour A-24 que l'unité PHP pure ; le natif/Python/confinement ne sont attestés que par la matrice scellée. (Observation, pas un défaut du code.)

## Décisions techniques, défaut proposé

- Point 3 : garder la matrice scellée comme preuve du natif/Python, et ajouter une phrase de portée dans le rapport. Défaut : **inchangé**, mention ajoutée.

## Pour Imagine (question fermée)

- Point 1 : la différence entre l'adresse de livraison de l'abonnement et celle du compte doit-elle **ignorer** la casse et les espaces (deux adresses ne différant que par là = identiques), ou les **compter** comme des différences ? Défaut prudent proposé en attendant : **comparaison à l'octet près** (état actuel) — elle sur-signale plutôt qu'elle ne masque, ce qui est le sens prudent pour un audit « combien sont à vérifier ». Si la réponse est « ignorer », il faut normaliser casse + espaces avant comparaison et adapter le banc (ajouter un cas de différence réelle de contenu).

## Verdict

**À corriger** — un point **important** (sémantique de comparaison à faire trancher, défaut prudent en place) et deux points **mineurs** (SHA du gardien périmé dans le rapport ; portée de preuve à préciser). Le cœur métier est exact sur le banc, l'étanchéité et l'immobilité sont prouvées. Ce verdict n'est pas un GO.

`codex.md` existe mais n'a pas été lu. Fusion non faite, conformément à la consigne.
