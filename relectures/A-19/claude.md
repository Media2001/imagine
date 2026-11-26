# Relecture A-19 — Cohérence des abonnements et des adhésions (Claude, indépendant)

Date : 2026-11-26. Relecteur : Claude, lancé depuis la racine du dépôt.
Je signale, je cite, je propose. Je ne réécris pas le code. Ce verdict n'est pas un GO.

Codex a déjà déposé son rapport (`relectures/A-19/codex.md`). Je ne l'ai pas ouvert.
Fusion non faite : voir la fin.

## Rejeu de la suite autorisée

Commande, sans argument :

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Conteneur jetable, hors réseau, dépôt monté en lecture seule. Dernière ligne :

```
REJEU : 1111 tests, 34504 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Image : `T01 IMAGE : sha256:d34fed02a45318da2527e5c8e1cb583734b0ee0a6ba71c0729fc6f9fcaf4d281`.

**Important** : cette commande rejoue la suite PHPUnit **globale T01**, pas la suite d'A-19.
`grep` sur `wp/tests/t01` ne trouve aucune mention de `a19`, `A19` ni `SubscriptionCoherence`.
Le REJEU prouve donc la **non-régression globale**, pas qu'A-19 fonctionne.
La suite propre d'A-19 (9 assertions PHP pures, matrices natives classic/HPOS, gardes du lanceur,
tests Python) vit dans `wp/tests/a19/run.py`. Elle exige Docker, le banc sous licence
(`/home/ced/staging-wp/plugins/…`) et des conteneurs natifs : **non rejouable** sous mes
contraintes de relecture (hors réseau, dépôt en lecture seule, extensions commerciales absentes).
Je l'ai donc vérifiée autrement : déroulé à la main (§2) et inspection du paquet de preuves (§3).

## 1. Conformité

Le brief demande un **complément d'audit en lecture seule**, par le lanceur confiné d'A-11/A-12,
des **comptes seulement**, chacun avec sa phrase de définition, sans aucun identifiant de compte,
d'abonnement, de commande, ni nom, email, adresse ou montant. Tout cela est présent.

Correspondance des sorties exigées (`wp/outils/bascule/a19/Analysis.php:14-114`) :

- tableau croisé état abonnement × état adhésion, par plan → `cross` (`:43`). ✓
- abonnements sans adhésion liée, par état → `subscriptions_without_membership` (`:58`). ✓
- adhésions sans abonnement, par plan et état → `memberships_without_subscription` (`:36`). ✓
- adhésions liées à un abonnement disparu → `memberships_missing_subscription` (`:38`). ✓
- comptes à plusieurs abonnements actifs → `multiple_active_subscription_accounts` (`:95`). ✓
- comptes à plusieurs adhésions actives au même plan → `multiple_active_membership_accounts`
  + détail `_by_plan` (`:85,96`). ✓
- actifs auto sans moyen enregistré, par passerelle → `automatic_without_saved_payment` (`:72`). ✓
- prochain paiement passé → `active_past_next_payment` (`:77`). ✓
- actifs sans commande payée → `active_without_paid_order` (`:78`). ✓
- renouvellement manuel, par passerelle → `manual_by_gateway` (`:61`). ✓

Mode d'emploi : dix lignes sur le standard (`wp/outils/bascule/a19/README.md:3-16`), et deux
lignes propres pour le README de l'audit partagé (`production/A-19/readme-ajout.txt`). ✓
`production/A-19/PRET` présent, daté. Le lot ne corrige rien, ne relie rien, ne change aucun état,
ne qualifie rien d'« erreur » (`README.md:38`). ✓

Plan rendu par identifiant, jamais par nom (`Analysis.php:32`). ✓

**Interprétation signalée** (mineur) : Hermès ajoute un onzième seau,
`automatic_payment_reference_unknown` (`Analysis.php:73-74`), pour séparer « moyen absent » de
« schéma de passerelle inconnu ». Le brief (item 7) ne demandait que « sans moyen enregistré, par
passerelle ». Le choix est prudent (ne pas accuser d'« absent » par supposition) et **est signalé**
dans `README.md:33` et `LIVRAISON.md`. Conforme à l'esprit, mais c'est une sortie en plus : à
confirmer par Imagine (voir fin).

## 2. Exactitude métier — déroulé à la main

J'ai déroulé `Analysis::analyse` sur deux jeux.

**Cas A — jeu unitaire** (`wp/tests/a19/unit.php:13-25`, `asOf=200`) :
trois abonnements (10 actif/auto/réf présente/échéance 300 ; 11 actif/auto/réf absente/échéance 100 ;
12 on-hold/manuel/chèque) et trois adhésions (plan 20 : liée à 10 ; sans lien ; liée à 999 absent).
Résultat attendu que j'ai recalculé pas à pas :
- `cross` = [{20, active, active, 1}] ;
- `subscriptions_without_membership` = [{active,1},{on-hold,1}] ;
- `memberships_without_subscription` = [{20,active,1}] ;
- `memberships_missing_subscription` = [{20,active,1}] ;
- `multiple_active_subscription_accounts` = 1, `_membership_accounts` = 1, `_by_plan` = [{20,1}] ;
- `automatic_without_saved_payment` = [{fixture,1}] ;
- `active_past_next_payment` = 1 (100 < 200), `active_without_paid_order` = 1 ;
- `manual_by_gateway` = [{cheque,1}].

Mon calcul est **identique** aux assertions du test. ✓

**Cas limite — égalité à l'instant de clôture** (`unit.php:43-52`) : échéance = 200 = `asOf`.
`Analysis.php:77` compte `next > 0 && next < asOf` → **strict**, l'égalité n'est pas comptée
(`active_past_next_payment` = 0). Conforme à `README.md:34` (« égalité à cet instant non comptées »).
Le compte invité (`user = 0`) est exclu (`Analysis.php:66`), et une passerelle au nom interdit
`/PRIVATE_CANARY` est ramenée à `autre` par `technical()` (`:9-12,56`). ✓ canari neutralisé.

**Cas B — banc natif** (`wp/tests/a19/seed.php`, `inside.py`), que j'ai déroulé contre le seed :
quatre abonnements, un couple cohérent, un actif non lié, une adhésion autonome, une adhésion liée
à un abonnement supprimé, un compte à deux abonnements actifs, un doublon d'adhésion, un automatique
sans moyen, un parent et un renouvellement réellement payés, une échéance passée relue après
activation. Mon calcul donne exactement le bloc `counts` attendu par `inside.py:50-60`. ✓

## 3. Vérification des preuves (la suite A-19 n'étant pas rejouable chez moi)

- `production/A-19/preuves/final/classic-coherence/coherence.json` : le bloc `counts` est
  **identique** à mon déroulé du cas B (cross 1 ; sans-adhésion 2 actifs + 1 on-hold ;
  sans-abonnement 2 ; lien mort 1 ; multiples 1/1 ; auto-sans-moyen a19_fixture 1 ; inconnu [] ;
  manuels bacs+cheque ; échéance passée 1 ; sans commande payée 1). ✓
- Empreintes avant/après, classic **et** HPOS : `cmp` → **identiques** (lecture seule prouvée). ✓
- `grep CANARY` sur tout `production/A-19` : **0 occurrence**. Aucun ID de compte/abonnement/commande,
  aucun nom, email, adresse, montant dans les sorties. ✓
- `as_of_utc` figé une fois, `audit_sha256` lié au rapport A-02 ; dépendance au schéma
  `imagine-a02-audit-v1` contrôlée (`Command.php:49-54`), mismatch de stockage refusé (`:59`). ✓

Réserve : ces artefacts viennent du banc d'Hermès ; je les ai jugés cohérents entre eux et avec le
brief, mais je n'ai pas pu les **régénérer** indépendamment (voir §Rejeu).

## 4. Sécurité et données

- Confinement obligatoire : PHP direct refusé hors conteneur (`Command.php:55`,
  test `inside.py:68-69` → `A19_CONFINEMENT_REQUIRED`). ✓
- Sorties hors site et hors dépôt, disjointes (`Command.php:31-40`), permissions 0700/0600
  (`:66-71`, test `inside.py:64`). ✓
- Codes d'erreur sur **liste littérale fermée** (`inventorier-coherence:36-74`) ; toute exception
  d'extension au nom ressemblant est ramenée à `A19_INVENTORY_FAILED` (`:75-76`, test
  `inside.py:96-98`). Aucune sortie d'erreur ne recopie un chemin ou un nom du site : règle de la
  voie 1 respectée. ✓
- Liens symboliques, drop-ins, surcharges de config, date impossible : tous refusés par code seul,
  sortie vide (`inside.py:70-90`). ✓
- Passerelles passées par `technical()` : `^[a-z][a-z0-9_-]{0,79}$` sinon `autre` (`Analysis.php:9-12`).
  Aucun titre de passerelle, aucun jeton sorti. ✓
- Aucun secret, aucune donnée réelle ; jeux fictifs en `@example.org` et canaris. ✓
- Non applicable : paywall (outil de lecture seule, aucune sortie de texte réservé).

## 5. Doctrine

- **Standard d'abord** : lecture par objets natifs (`Inventory.php:50-69`), lien explicite
  `_subscription_id` via `get_post_meta` (`:82`), `get_related_orders('all','any')`,
  `get_requires_manual_renewal('edit')` plutôt que `is_manual()` (choix signalé, `README.md:14`,
  `sources-officielles.json`). Documentation officielle citée avec URL et SHA256. ✓
- **Logique métier hors de WordPress** : `Analysis.php` est PHP pur, testable sans base ;
  `Inventory.php` ne fait que la projection native. Conforme au §4 de la doctrine. ✓
- **Conventions §5** : PHP 8.2, `declare(strict_types=1)`, espace de noms `Imagine\`, préfixe
  `imagine_`/`a19`, textes FR. PSR-12 : le paquet revendique `phpcs` strict zéro erreur
  (`preuves/final/style/`). ✓
- README présent avec rôle, réglages de confinement, et commande de rejeu. ✓

## 6. Études

Sans objet (lot avec code).

## Verdict

**À corriger** — un point important, un mineur. Aucun bloquant. Le code fait ce que le brief
demande et mon déroulé à la main concorde avec les preuves ; la réserve porte sur la
**reproductibilité indépendante**, pas sur une faute de logique.

**Important**
1. La commande autorisée (`rejouer.ps1` → suite T01 globale) **ne couvre aucun test d'A-19**
   (grep : 0 mention). La vérification d'A-19 repose entièrement sur le paquet de preuves d'Hermès,
   non rejouable sous les contraintes de relecture. Or `wp/tests/a19/unit.php` (9 assertions sur
   `Analysis.php`) est **PHP pur** et n'exige ni extension, ni base, ni réseau : il pourrait entrer
   dans la suite T01 et devenir rejouable par un relecteur indépendant. Les matrices natives
   classic/HPOS, elles, resteront liées au banc sous licence — limite structurelle commune à la
   famille A-02/A-11/A-12, à assumer explicitement.

**Mineur**
1. Seau `automatic_payment_reference_unknown` en plus de la liste du brief (item 7). Interprétation
   prudente et signalée ; ne pas supprimer sans arbitrage. Voir « Pour Imagine ».

### Décisions techniques, défaut proposé
- **Câbler les 9 assertions de `unit.php` dans la suite T01** afin que la commande autorisée couvre
  la logique métier pure d'A-19. *Défaut proposé* : le faire (Hermès applique, j'arbitre après).
  Les matrices natives restent hors T01, documentées comme limite de banc.

### Pour Imagine
- Faut-il garder « schéma de passerelle **inconnu** » distinct de « moyen **absent** »
  (`automatic_payment_reference_unknown`), ou tout regrouper sous « sans moyen enregistré » ?
  *Défaut proposé* : **garder distinct** (prudent : n'accuse pas un paiement d'être absent quand
  la passerelle n'expose simplement aucun schéma lisible).

## Fusion

`relectures/A-19/codex.md` existe mais je ne l'ai pas ouvert, comme demandé. Je **n'ai pas** écrit
`corrections/A-19.md` et je n'ai pas fait la fusion. Étape suivante, sur instruction : lire
`codex.md`, croiser, puis écrire la fusion.
