# Relecture A-14 — Rapprochement d'un export de contacts (Claude, indépendant)

Date : 2026-11-26. Brief : `briefs/A-14-rapprochement-des-contacts.md`. Cahier des charges : §4.3, §3.10.
Production relue : `wp/outils/bascule/a14/`, `wp/outils/bascule/rapprocher-contacts`, `wp/tests/a14/`, `wp/tests/fixtures/a14-contacts-fictifs.csv`, paquet `production/A-14/preuves/final`.
Je n'ai pas lu `relectures/A-14/codex.md`. Pas de fusion à ce stade.

## Rejeu de la suite PHP autorisée

Commande lancée depuis la racine, sans argument :

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Dernière ligne :

`REJEU : 1087 tests, 34376 assertions, 1 échecs, 0 erreurs, 0 ignorés — FAIL`

- La suite est **rouge**. L'unique échec est `Imagine\Site\Tests\TableauBordReglesTest::testCatalogueIsMemoizedWithinRequest` (« Chaque fichier ne doit être exécuté qu'une fois », `wp/plugins/imagine-site/tests/TableauBordReglesTest.php:17`).
- Cet échec est **hors périmètre A-14** : c'est le tableau de bord natif de l'extension `imagine-site` (lot en cours, fichiers `TableauBordNatives.php`/`EcheancesNatives.php` modifiés et non committés). A-14 n'apporte **aucun** code à cette suite T01 (aucune occurrence de `a14`/`Contacts`/`Matcher`/`rapproch` dans la sortie).
- A-14 est testé par son **runner Docker propre** (`wp/tests/a14/run.py`), que je **n'ai pas pu rejouer** ici : dépôt en lecture seule, conteneur jetable sans réseau, pas de Docker côté relecteur. Je me suis donc appuyé sur le paquet scellé + un déroulé manuel (ci-dessous), qui concordent au cas près.

## 1. Conformité

Globalement conforme au brief, en lecture seule, sans appel Brevo ni écriture dans le site.

- Lecture seule et confinement (§4.3) : `command.php:58` exige `A14_CONFINED=1` et refuse si `mail`/`exec` existent ; `main.py:69` pose `disable_functions`, A11 charge sous transaction READ ONLY et coupe HTTP/mail/cron, A12 confine l'écriture au parent de sortie. ✔
- Rapprochement sur l'email seul, sans casse ni espaces (`Matcher::normalise`, `Matcher.php:9-12`). Aucun rapprochement par nom, point ou suffixe fournisseur : la fixture le prouve (`local+tag` et `first.last` restent **sans compte**). ✔ Conforme à « Rien d'autre ».
- Désinscrit/bloqué comptés et conservés, jamais réinscrits : ligne 3 (désinscrit) rapprochée garde `statut=desinscrit` dans `rapproches.csv`. ✔
- Compte « sans email » jamais rapproché, jamais exposé : exclusion sur `imagine_sans_email=1` **ou** domaine `@sans-email.imagine.invalid` (`Accounts.php:33-41`). ✔
- Colonnes `cooperateur`/`tarif` présentes mais vides, rien déduit (`Matcher.php:55`, en-tête CSV `command.php:81`). ✔
- Sorties hors racine web et hors dépôt (`disjointOutput`, dossier 0700 / fichiers 0600, jamais écrasés). ✔
- Lecture du site par le chemin A-11 sans nouveau bootstrap, classique **et** HPOS (`Accounts.php:21-30`). ✔
- Réemploi de la lecture A-13 : `main.py` charge `controler-export` et réutilise `decoder`, `lire_csv`, `objet_unique`, `SEPARATORS`, `Refus` (symboles vérifiés présents). ✔

Interprétations faites (signalées, à mes yeux acceptables) :
- **Contact pointant vers un compte technique** → compté « sans compte ». Le compte technique n'étant jamais rapproché, c'est la seule issue cohérente, mais ce n'est pas explicité dans le brief. Documenté en creux dans le README.
- **Plusieurs comptes au même email normalisé** → ligne « ambiguë », aucun statut d'abonnement, jamais le premier compte choisi (`Matcher.php:49-51`). Conforme au brief et au README.
- **Statut non configuré** → `inconnu`, compté mais jamais réinscrit (`main.py:45`). Conforme.

## 2. Exactitude métier — déroulé à la main

J'ai déroulé la fixture (30 lignes) contre le seed A-02 (`wp/tests/a14/seed.php`), à la main, puis comparé au `resume.json` produit.

Comptes du banc (après normalisation) : `alice`(actif), `bob`(annulé→inactif), `carol`(on-hold→inactif), `technical`(exclu), `local`, `firstlast`, `unmatched`, `shared`×2 (shareda+sharedb → **ambigu**), `invalid`(email invalide → injoignable), plus 4 comptes préexistants du banc (total users = 14, cf. oracle).

Résolution ligne par ligne :
- l.2 `alice` et l.3 ` ALICE ` → normalisent vers `alice@example.org` : **rapprochées** (compte unique), et **doublon** l.2+l.3.
- l.4 `bob` (bloqué), l.5 `carol` (inscrit) → rapprochées, abonnement `non`.
- l.6 `technical` → compte exclu → **sans compte**.
- l.7 `not-an-email`, l.8 vide → **invalides**.
- l.9 `local+tag`, l.10 `first.last` → pas de correspondance (pas de normalisation fournisseur) → **sans compte**.
- l.11 `shared` → deux comptes → **ambiguë**.
- l.12–31 (`absent11`–`absent30`) → **sans compte** (20).

Totaux attendus à la main = valeurs produites :

| Compteur | Attendu | `resume.json` |
|---|---|---|
| contacts_total | 30 | 30 ✔ |
| contacts_with_account | 4 (l.2,3,4,5) | 4 ✔ |
| contacts_without_account | 23 (1+1+1+20) | 23 ✔ |
| ambiguous_contact_lines | 1 (l.11) | 1 ✔ |
| accounts_without_contact | 7 (local, firstlast, unmatched + 4 comptes du banc) | 7 ✔ |
| accounts_unmatchable | 1 (invalid) | 1 ✔ |
| invalid_contact_lines | 2 (l.7,8) | 2 ✔ |
| duplicate_contact_lines | 2 (l.2,3) | 2 ✔ |
| unsubscribed_contacts | 1 | 1 ✔ |
| blocked_contacts | 1 | 1 ✔ |

Anomalies attendues, triées par ligne physique : l.2 et l.3 doublon, l.7 et l.8 invalide, l.11 plusieurs comptes → **identiques** au produit (classic et HPOS).
`rapproches.csv` attendu = 4 lignes (2;oui;inscrit / 3;oui;desinscrit / 4;non;bloque / 5;non;inscrit), cooperateur/tarif vides → **identique**.

Cas limites couverts et vérifiés :
- Partition `total = avec + sans + ambigu + invalide` (30 = 4+23+1+2), les trois chemins d'une ligne valide sont exclusifs. ✔
- Un email dédoublé **et** rapproché (l.2/l.3) : les deux lignes sont dans « avec compte » et signalées en doublon. Voir point mineur §conformité.
- Groupe ambigu présent ≠ « compte sans contact » (`seen[email]`, `Matcher.php:60-63`). ✔
- Désinscrit resté désinscrit ; aucun statut d'abonnement inventé pour l'ambigu. ✔
- Empreinte de base identique avant/après : `*-db-before.json` et `*-db-after.json` ont la **même empreinte** (classic et HPOS, confirmé par les hachages du manifeste). ✔

HPOS : `hpos-contacts/resume.json` donne les mêmes compteurs et anomalies, avec `storage=hpos`. ✔

## 3. Tests

- **Suite autorisée (T01)** : rouge, mais l'échec ne touche pas A-14 (voir § Rejeu).
- **Suite propre A-14** (non rejouée par moi, lue) : couverture forte et honnête.
  - `unit.php` : casse/espaces, exclusion technique, statut préservé, absence de `@` dans la sortie, doublons (tous les membres) + lignes invalides, invalide non compté comme « sans compte », ambigu jamais premier choix.
  - `test_input.py` : réemploi A-13, **ligne physique** conservée (multi-lignes entre guillemets), décodeurs UTF-8-SIG/UTF-16, refus (séparateur/guillemets/colonnes/IBAN), encodage de transport PHP explicite.
  - `inside.py` (natif classic+HPOS) : compteurs exacts, anomalies exactes, lignes CSV exactes, **aucun** email/nom/ID/valeur privée en sortie, permissions 0700/0600, **rejeu identique** (idempotence), refus des sorties qui s'échappent, argument inconnu, exécution non confinée, drop-in nommé non exécuté, empreinte base + fichiers identiques avant/après, config non exécutée, canari mail/HTTP/cron.
- Les tests vérifient la règle (valeurs attendues en dur), pas une simple répétition du code.
- Le `verify.py` scelle le paquet (inventaire des sources, verts, PSR-12, préparation d'image rejouée, before==after, manifeste exact).

Réserve : je n'ai **pas** pu réexécuter cette suite ici (pas de Docker/réseau, dépôt en lecture seule). Verdict appuyé sur le paquet scellé + déroulé manuel concordant, pas sur un rejeu indépendant du conteneur.

## 4. Sécurité et données

- Aucune donnée réelle : fixture de 30 lignes en `@example.org`, noms « Fictif NN », seed en `@example.org`. ✔
- Aucun secret. Sorties sans email/nom/ID (seulement numéros de ligne). ✔
- Requêtes préparées là où une valeur variable entre (`Accounts.php:33` `prepare(... %d ...)`). Les requêtes de collecte n'injectent que `$wpdb->prefix`. ✔
- Garde-fous de sortie : disjonction site/dépôt/entrées, liens symboliques refusés, taille d'entrée bornée (16 Mio), audit A-02 vérifié (schéma + `read_only`), concordance de stockage audit/site. ✔
- Pas de paywall ici (outil hors ligne).

## 5. Doctrine

- Standard d'abord : réemploi A-11/A-12/A-13/A-02 **sans modification** (snapshot de dépendances stable dans le runner). ✔
- §5 : `declare(strict_types=1)`, espace de noms `Imagine\`, PSR-12 strict vert (`style.json` code 0, 0 erreur/0 avertissement). Préfixe `imagine_` respecté (`imagine_sans_email`). ✔
- Logique métier en PHP pur (`Matcher`) testable sans WordPress ; couche fine `Accounts` pour la base. ✔
- Rejouable/idempotent : rejeu identique prouvé. ✔
- README présent et complet (ce que fait l'outil, réglages, comment lancer les tests). ✔

## 6. Points relevés

Rien de bloquant ni d'important côté A-14. Deux points mineurs.

- **Mineur — `resume.md` en libellés machine.** `command.php:78-79` recopie les clés anglaises (`contacts_total`, `accounts_without_contact`, …). Doctrine §5 veut des textes d'interface en français. Correction proposée : table de libellés français pour ce résumé lisible.
- **Mineur — double comptage des lignes dupliquées dans `contacts_with_account`.** Les lignes 2 et 3 (même adresse) comptent toutes deux dans « avec compte » (4 lignes pour 3 comptes distincts). C'est documenté (README) et réconciliable via `duplicate_contact_lines`, mais un lecteur pressé peut surcompter les personnes rapprochées.

## Décisions techniques, défaut proposé

- **Comptage par ligne vs par compte** pour « contacts_with_account ». Défaut appliqué : garder le comptage par **ligne source**, les doublons restant signalés séparément (`duplicate_contact_lines` + anomalies). À confirmer après coup.

## Pour Imagine (métier)

- Rien à trancher : aucune règle d'argent, de droit d'accès ni de comptabilité n'est engagée. Les champs `cooperateur`/`tarif` restent vides comme demandé.

## À arbitrer par Ced (visuel / réel)

- `resume.md` est le seul livrable « lu par un humain » : veux-tu des libellés français (ex. « Contacts avec compte : 4 ») plutôt que les clés techniques ? Défaut prudent proposé : libellés français, sans changer `resume.json`.

## Verdict

**Conforme** — sous deux réserves de méthode, non des défauts d'A-14 :
1. la suite PHP autorisée est rouge, pour un **autre lot** (tableau de bord natif) ;
2. je n'ai pas pu réexécuter la suite Docker propre d'A-14.

Points classés :
- **Bloquant** : aucun pour A-14. (À signaler quand même : T01 rouge sur `TableauBordReglesTest`, à corriger dans son lot avant toute clôture globale.)
- **Important** : aucun.
- **Mineur** : libellés anglais dans `resume.md` ; double comptage des lignes dupliquées (convention à confirmer).

Ce verdict n'est pas un GO.

---
`codex.md` existe déjà dans `relectures/A-14/`. Conformément à la consigne, je ne l'ai pas ouvert et je n'ai pas écrit de fusion. Étape suivante (`corrections/A-14.md`) à faire sur demande.
