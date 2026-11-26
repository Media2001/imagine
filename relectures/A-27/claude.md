# Relecture A-27 — Moyens de paiement enregistrés, comptés

Relecteur : Claude, indépendant. Date : 2026-11-27. Codex non lu (consigne respectée).
Périmètre lu : `briefs/A-27-moyens-de-paiement-enregistres.md`, cahier des charges §4.3 et §3.6 (via le brief), `wp/outils/bascule/a27/`, `wp/tests/a27/`, `production/A-27/`.

## Rejeu de la suite

Commande autorisée, sans argument :

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1
```

Dernière ligne obtenue :

```
REJEU : 1151 tests, 36062 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Ligne précédente : `OUTILS : 20 outils, 521 contrôles, 0 échecs ; hors rejeu : aucun`. Le conteneur est jetable, `network=none`, `rootfs=ro`, `wp` monté en lecture seule, nettoyage vérifié. L'outil `a27` y pèse `53 contrôles ; 0 échecs`.

**Ce que le rejeu couvre, et ce qu'il ne couvre pas.** `rejouer.ps1` lance un seul conteneur PHP (`t01/executer.php`) : il rejoue les suites PHPUnit du dépôt et la banque PHP pure `wp/tests/a27/unit.php` (les 53 contrôles `a27`). Il **ne rejoue pas** la suite Python d'A-27 (`test_*.py`, frontières de sortie, refus, validateur), ni la banque native classique/HPOS (`inside.py`, `standard.php`, `seed.php`, `neutralise.php`), ni l'immuabilité DB/fichiers, la purge réelle de l'import, l'isolation Docker et le confinement Landlock. Ces preuves exigent les portes parent (`matrix.py --include-native --parent-serialized`, voir `production/A-27/RECEPTION-PARENT.md`), que mes droits (lecture seule, sans réseau, sans accès site) m'interdisent de rejouer. Je les ai donc **lues**, pas réexécutées. Elles sont auto-déclarées dans `FINALISATION.md` / `verification-probes.json`. C'est une limite de ma vérification, pas un défaut constaté. Voir point important I-1.

## 1. Conformité

Globalement conforme au brief, sans débordement notable.

- **Standard d'abord.** `README.md` lignes 1-26 : dix lignes numérotées sur le rangement natif des jetons (`{prefix}woocommerce_payment_tokens` / `woocommerce_payment_tokenmeta`), le lecteur unitaire `WC_Payment_Tokens::get()`, le dispatch de renouvellement `woocommerce_scheduled_subscription_payment_{gateway}`, les clés Stripe `_stripe_source_id` / repli `_stripe_card_id` et PayPal `_paypal_subscription_id`. Chaque affirmation cite une source [S1]–[S5] avec URL (lignes 20-24) et renvoie en plus à une empreinte sur le **code installé** (`standard.php`). Conforme au §4.3 et au point « étude » de la grille.
- **Comptes demandés, tous présents.** Par passerelle et type (`automatic`, liste fermée `carte / mandat_sepa / accord_paypal / autre / illisible`) ; cartes expirées / dans les six mois (`cards`) ; références non rattachées à un jeton et jetons sans abonnement vivant (`relations.subscriptions_unlinked` / `tokens_without_living_subscription`) ; comptes à plus d'un moyen (`accounts_multiple_tokens`). `Analysis.php:128-177`.
- **Fusion des petits groupes < 5** (`pool()`, `Analysis.php:60-79`), identique à A-20. Sorties : nombres, identifiants de passerelle, types d'une liste fermée. Aucun jeton, aucune référence, aucun chiffre de carte, aucune date individuelle, aucun identifiant de compte/abonnement.
- **« illisible », jamais « absent »** : type illisible pour toute présence indéterminée ; la présence prouvée absente (via A-19) reste hors périmètre et n'est pas présentée comme moyen (`reference()`, `Analysis.php:122-125` ; README ligne 43).
- **Neutralisation.** Le marqueur `imagine_staging_disabled_plugins` suffit à rendre **tous** les nombres `inconnu après neutralisation` ; aucun zéro reconstruit (`Inventory.php:42-43`, `Analysis.php:131-133`). Le résultat « aucun compte utile après purge » est porté à Ced, sans modifier l'import. Conforme au brief qui anticipe cette issue.

Interprétations signalées (conforme doctrine §1, elles sont écrites dans le README) :

- **Fenêtre « six mois »** (README ligne 47) : une carte dont le dernier jour tombe **après** le jour d'audit du sixième mois est `later`, pas `within_six_months`. Audit 26/11/2026 midi → une carte de mai 2027 (fin 31/05) est `later`, car la borne est le 26/05 midi. Choix défendable mais c'est un **seuil métier** : voir « Pour Imagine ».
- **Split des non-rattachés** : le brief demande « non rattachée à aucun jeton » ; le code distingue `subscriptions_unlinked` (certain) et `subscriptions_link_unknown` (indéterminé). Raffinement documenté (README ligne 48), les deux sont reportés. Pas de perte d'information.
- **`cards` reporte aussi `later` et `illisible`**, au-delà des deux nombres demandés. Complétude inoffensive : les deux nombres du brief restent isolés. Mineur.

## 2. Exactitude métier — deux cas déroulés à la main

J'ai déroulé le banc fictif du brief à partir de `seed.php`, à travers `reference()` et `analyse()`, et comparé aux attendus codés dans `inside.py`.

**Cas 1 — banc nominal (une occurrence par cas), attendu `inside.py:116` = `automatic` 6, `cards` 3, `relations` 4.**

Six abonnements vivants, non manuels (users 0-5) :

| i | user | passerelle | référence | type calculé | lien |
|---|---|---|---|---|---|
| 0 | 0 | stripe | méta `_stripe_source_id` = jeton valide (la clé `_stripe_card_id` périmée est ignorée par le `break` de `Inventory.php:72-78`) | carte | linked |
| 1 | 1 | stripe | jeton d'ordre, carte 2026-10 | carte | linked |
| 2 | 2 | stripe_sepa | jeton eCheck | mandat_sepa | linked |
| 3 | 3 | paypal | méta `_paypal_subscription_id`, sans jeton | accord_paypal | unlinked |
| 4 | 4 | stripe | méta `_stripe_source_id` sans jeton correspondant | illisible | unlinked |
| 5 | 5 | stripe | jeton d'ordre, carte 2026-11 | carte | linked |

- `automatic` : stripe/carte ×3 (i0,i1,i5), stripe_sepa/mandat_sepa ×1, paypal/accord_paypal ×1, stripe/illisible ×1 = **6**, tous < 5 → `autres:6`. ✓
- `cards` : i0 (2027-03) `within_six_months`, i1 (2026-10) `expired`, i5 (2026-11) `within_six_months` = **3** → `autres:3`. ✓
- `relations` : i3 paypal/unlinked, i4 stripe/unlinked, jeton orphelin user6 (pas d'abonnement vivant) stripe/`tokens_without_living_subscription`, user0 (2 jetons) `accounts_multiple_tokens` = **4** → `autres:4`. ✓

Point sensible : l'abonnement actif **manuel** de user0 (lié au jeton 0) est vivant, donc user0 compte comme « vivant » et ses jetons ne sont pas orphelins ; étant lié, il n'entre pas dans `relations`. Déroulé conforme.

**Cas 2 — banc à cinq occurrences, attendu `inside.py:261-271`.** Chaque cas répété ×5 avec des comptes indépendants. Les groupes franchissent le seuil de 5 et deviennent visibles : `automatic` stripe/carte 15, stripe/illisible 5, stripe_sepa/mandat_sepa 5, paypal/accord_paypal 5 ; `cards` stripe/expired 5, stripe/within_six_months 10 ; `relations` quatre métriques à 5. Mon calcul (×5 du cas 1) correspond exactement. ✓ Ce cas prouve que le seuil < 5 et la visibilité à 5 fonctionnent.

Cas limites vérifiés dans `unit.php` et recoupés : bord UTC de fin de mois (`utc_end_second_valid` / `utc_next_second_expired`, lignes 41-42), borne « sixième mois » exacte (ligne 35), clamp fin de mois (lignes 37-40), horloge invalide / non-UTC refusée (lignes 46-54), métadonnées multiples/non scalaires/contradictoires → illisible (lignes 76-81), jeton illisible ≠ absent (ligne 84), absence prouvée (`present === false`, ligne 88), neutralisation → tout inconnu (lignes 116-120).

Conclusion : logique métier **correcte et interne cohérente** sur les deux bancs et les bords.

## 3. Tests

- **Rejeu PASS** (voir en-tête). La banque PHP pure `unit.php` (53 contrôles), qui porte le cœur de la logique déroulée ci-dessus, est bien réexécutée, verte.
- **Vrais tests de règle, pas de répétition du code** : `unit.php` vérifie des valeurs attendues construites à la main (ex. `expiry('2027','05',...) === 'later'`), pas le retour du code sur lui-même. `inside.py` compare à des structures attendues écrites en dur. `test_mutations.py` fait de la mutation réelle (retrait d'une garde → rouge attendu). Bon niveau.
- **Témoins rouges réels** : `red-unit.json` (CC→autre) et transition native refusée (pending→on-hold via active) documentés. Non rejoués par moi (hors conteneur PHP du rejeu).
- **Couverture au-delà du nominal** : états vivants/non vivants, manuel exclu, canaux directs/shutdown, altération JSON+Markdown cohérente, refus de publication, purge import sur clone. Solide — pour la part que je peux lire.
- **Limite de couverture par le rejeu** (I-1) : la suite Python (38 tests annoncés) et la banque native (166 assertions annoncées) ne sont pas dans la commande autorisée. Leur vert est auto-déclaré.

## 4. Sécurité et données

- **Aucun secret, aucune donnée réelle.** Fixtures `@example.org`, logins `a27-fictif-*`, valeurs `*_PRIVATE_CANARY`. Les tests asservissent l'absence de `CANARY|@|4242|/scratch|a27-fictif|2027-03` dans toutes les sorties (`inside.py:120`, `279`).
- **Étanchéité de sortie** : schéma JSON fermé validé octet à octet (`report.py:projection` + `complete_report`), Markdown = rendu exact du même JSON, liaison SHA-256 pré-shutdown interne, bornage 64 Kio des flux, refus des fichiers inattendus/vides/partiels/liens symboliques. Modes 0700/0600. Publication parent-only après contrôles.
- **Lecture seule** : neutralisation des hooks Action Scheduler (`Inventory.php:28-33`), aucun handler de charge appelé, `disable_functions` + exigence `A27_CONFINED` + refus `mail`/`exec` (`Command.php:21-23`). Le lanceur PHP nu est refusé hors enclos (`A27_CONFINEMENT_REQUIRED`).
- **Gardes de sortie/audit** : chemin de sortie disjoint du site/dépôt, nom ASCII neuf, audit dans un sous-dossier du parent, taille bornée, schéma `imagine-a02-audit-v1` et `order_storage` vérifiés, refus fermés depuis `refusals.json` (`Command.php:24-60`).
- Pas de paywall ici (lot d'audit). Rien à signaler.

RAS bloquant côté sécurité, dans la limite de ce que le rejeu exerce réellement.

## 5. Doctrine

- **Standard d'abord** respecté : le sur-mesure se limite au comptage ; lecture via API native (`WC_Subscription`, `WC_Payment_Tokens`), aucune table réinventée, « autre schéma » → `illisible` plutôt qu'une clé fabriquée.
- **Logique métier hors WordPress** : toute la règle est dans `Analysis.php` (PHP pur, testable sans base), `Inventory.php` n'est que la couche de lecture. Conforme §4.
- **Conventions §5** : `declare(strict_types=1)`, espace de noms `Imagine\`, PSR-12 (contrôle `style.py` annoncé vert), README présent. ✓
- **Rejouable / non-régression** : empreintes avant/après tables et fichiers, rejeu identique (`replay_identical`). ✓ (auto-déclaré pour la part native).
- **Écart tracé** : le résultat « aucun compte utile après neutralisation » et le renvoi à Ced sont à inscrire dans `docs/ecarts.md` au moment de la fusion (ma plume, pas celle d'Hermès).

## Verdict

**Conforme** sur le code et la logique métier, dans la limite explicite du périmètre que le rejeu autorisé exerce réellement. Un verdict n'est jamais un GO.

- **Bloquant** : aucun.
- **Important**
  - **I-1 — Preuves natives non rejouables par moi.** La banque classique/HPOS, l'immuabilité DB/fichiers, la purge import, l'isolation Docker et le confinement sont lus et auto-déclarés (`FINALISATION.md`), hors de la commande autorisée. Je ne peux pas les contre-vérifier. À confirmer en fusion avec le reçu de Codex ; si Codex ne les a pas rejoués non plus, la clôture repose sur l'exécution parent d'Hermès, pas sur une relecture indépendante.
- **Mineur**
  - **M-1** — `cards` publie aussi `later` et `illisible`, au-delà des deux nombres demandés. Complétude, sans risque.
  - **M-2** — `eCheck` → `mandat_sepa` **uniquement** sous `stripe_sepa` ; un identifiant de passerelle SEPA différent du site réel donnerait `autre`. Documenté (README ligne 45), à garder à l'esprit si l'audit réel révèle un autre id.

## Décisions techniques, défaut proposé (Hermès applique, Claude arbitre après)

- Aucune. Le code est cohérent ; rien à trancher côté technique.

## Pour Imagine (réglage métier)

- **Seuil « six mois ».** Faut-il que la fenêtre inclue **tout le mois** d'expiration (une carte de mai 2027 comptée « dans les six mois » pour un audit de novembre 2026), ou garder la borne au jour d'audit du sixième mois (comportement actuel, carte de mai 2027 = `later`) ?
  - *Défaut prudent proposé* : garder le comportement actuel (borne au jour d'audit). C'est le plus littéral de « six mois suivant la date de l'audit » et le moins optimiste sur la survie d'une carte. À confirmer, car ce seuil change un décompte présenté à la décision bancaire.

## Pour Ced (touche au réel)

- **Procédé de comptage à la source.** Sur copie neutralisée, tous les nombres A-27 sont « inconnu après neutralisation » : l'import purge jetons et références. Le brief anticipe ce résultat et renvoie la décision à Ced. Question fermée : acceptes-tu que ce comptage soit fait, le jour venu, sur une **copie vérifiée non neutralisée** (sans accès agent au réel, par un script dédié sous GO écrit), ou préfères-tu l'obtenir d'une autre source (export passerelle) ?
  - *Défaut prudent* : ne rien compter de réel tant que le GO n'est pas écrit ; le lot reste un outil prêt, pas un résultat sur données réelles.

## Suite

`relectures/A-27/codex.md` existe. Conformément à `relecteurs/CLAUDE.md` (étape 4-5), je **ne l'ouvre pas** et **ne fais pas la fusion** à ce stade, comme demandé. Rapport arrêté ici.
