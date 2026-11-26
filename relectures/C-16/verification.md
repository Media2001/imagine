# Vérification C-16 — second tour (Claude vérificateur)

**Lot** : C-16 — Commande pour un client ; encodage sans email ; vente sans identité.
**Base** : `corrections/C-16.md` (fusion), relue contre le code après corrections d'Hermès.
**Version relue** : état C-16 au commit `3515cb18` (00:18). **Corrections** : commits `d24c16bf`/`78243601`/`4272b001` (03:23→03:33).
**Date** : 2026-11-26. Ce verdict n'est pas un GO (doctrine §6).

Méthode : `git diff 3515cb18 HEAD` sur les quatre fichiers C-16 et sur `production/C-16`, relecture du code modifié, rejeu de la suite autorisée, lecture des preuves HTTP déposées par Hermès (site interdit au relecteur). **Pas de relecture complète refaite.**

## 1. Instructions de `corrections/C-16.md`, une par une

| # | Nature | État | Où |
|---|---|---|---|
| 1 | Bloquant R1 — verrou avant lecture du brouillon, relecture fraîche sous verrou | **Appliquée** | `CommandeAdmin.php` |
| 2 | Bloquant R1 — test de concurrence + interruption | **Appliquée** (preuve site) | `c16-concurrence-probe.php`, HTTP V2 |
| 3 | Important R2 — adresse native du seul nouveau compte, UI révisée | **Appliquée** | `CommandeNative.php`, `CommandeRegles.php`, `CommandeAdmin.php` |
| 4 | Important R2 — test recherche par localité après création | **Appliquée** (preuve site) | HTTP V2 |
| 5 | Mineur R3 — `wp_unslash` sur la recherche GET + test apostrophe | **Appliquée** | `CommandeAdmin.php:242` |
| 6 | Important — test unitaire `SansEmail::filtrer` hors site | **Appliquée** (rejouée par moi, verte) | `tests/SansEmailTest.php` |
| 7 | Mineur — rafraîchir le décompte T01 dans `PRET`/`A-VOIR` | **Appliquée** (nuance ci-dessous) | `PRET`, `A-VOIR.md` |
| 8 | Mineur hors C-16 — lever le gate C-09, documenter la dérive du sceau | **Appliquée selon les preuves d'Hermès** (non rejouable par moi) | `gates-V2.log`, `A-VOIR.md:51` |

**Détail**

1. **R1 — Appliquée.** La lecture préalable du brouillon est retirée du tronc commun et renvoyée dans la seule branche `preparer` (`CommandeAdmin.php:160`). Dans l'action `creer`, le `GET_LOCK` est pris en premier (`:183`), puis les trois caches natifs du transient non autoloadé sont invalidés (`:190-192`) **avant** la relecture fraîche sous verrou (`:193`). La staleness du cache d'options que Codex décrivait est traitée à la racine. Objectif tenu : un `resultat` déjà posé est rendu tel quel (`:194`), un seul couple commande/souscription.
2. **R1 test — Appliquée (site).** Sonde-barrière `c16-concurrence-probe.php` (deux connexions distinctes synchronisées avant `GET_LOCK`, injection d'interruption après `commence`). `red-concurrence-V2.json` reproduit le défaut d'origine (deux commandes, deux souscriptions) ; `http-corrections-V2.json` repasse au vert : `deux_POST_meme_ID`, `exactement_une_commande_et_une_souscription`, `interruption_apres_commence_persistant`, `reprises_interruption_fermees_sans_nouvelle_creation`. **Je n'ai pas exécuté ces cas** (site/base interdits) ; je m'appuie sur les preuves.
3. **R2 — Appliquée.** `CommandeNative::creerClient` reçoit l'adresse (`:97`, appel `:149`) et, hors vente directe et si le réglage le permet, pose prénom/nom + adresses billing/shipping sur le **nouveau** compte via `WC_Customer::set_props`/`save` (`:114-126`). Un compte existant est rendu tel quel, sans aucune écriture (`:100-101`). La règle est isolée derrière `imagine_commande_adresse_nouveau` (défaut prudent `oui`, helper pur `CommandeRegles::adresseNouveau`, `CommandeRegles.php:11`), conforme à « une règle ouverte devient un réglage ». La phrase d'UI est corrigée : « Les coordonnées des comptes préexistants restent inchangées » (`CommandeAdmin.php:285`) et une ligne conditionnelle annonce, en mode `non`, l'absence de recherche par localité (`:286-288`).
4. **R2 test — Appliquée (site).** `avec_email_localite_distincte_retrouve`, `sans_email_localite_distincte_retrouve`, `compte_preexistant_adresse_nom_email_inchanges`, `reglage_non_pas_adresse_compte` tous verts (`http-corrections-V2.json`, `green-adresse-apostrophes-V2.json`).
5. **R3 — Appliquée.** `CommandeRegles::texte(wp_unslash($_GET), 'recherche')` (`CommandeAdmin.php:242`), l'échappement HTML à l'affichage restant en place. Cas site `GET_nom_apostrophe_reel_sans_slash` et `GET_localite_apostrophe_reel_sans_slash` verts (`O'Fictif`).
6. **Couverture offline — Appliquée et rejouée par moi.** `tests/SansEmailTest.php` (stubs `tests/fixtures/c16-sans-email-stubs.php`) couvre destinataire `.invalid`, marqué mêlé à un normal (chaîne et tableau), CC marqué, BCC marqué multiligne, et vérifie que **tout** le message est refusé (`false`) sans redirection ni suppression partielle (`$atts` inchangé). **Rejoué dans ma suite autorisée : 8 tests / 17 assertions, vert.** C'est l'étanchéité d'envoi exigée par §3.13, désormais prouvée hors site.
7. **Décompte T01 — Appliquée, avec une nuance.** `PRET`/`A-VOIR` ne portent plus `1040/34229` : ils annoncent `1077/34327` **et** renvoient vers `final-V2.json`/`rejouer-t01-V2.log`. Nuance : mon rejeu frais donne `1088/34410` (voir §2) — soit 11 tests de plus, ajoutés par les lots C-19 en cours depuis la passe V2. C'est une dérive de photo, pas un défaut C-16 ; le renvoi vers le log couvre ce cas.
8. **Gate C-09 / sceau — Appliquée selon les preuves, non rejouable par moi.** `gates-V2.log` : `C09 382/382`, action `#8793 pending` (souscription 101), `strict_global_exit: 0`. La réserve rouge du premier tour est donc présentée comme levée, via une correction du lot C-09 (`production/C-09/papier-restauration-V2.json`), hors des fichiers C-16. La dérive du sceau `c09-seed.php` est documentée comme venant de C-17, pas de C-16 (`A-VOIR.md:51`). **Je ne peux pas confirmer l'état `382/382` du site** (accès interdit au relecteur) : voir §4.

## 2. Résultat des tests

**Suite autorisée rejouée par moi** (`wp/tests/rejouer.ps1`, conteneur jetable, `network=none`, dépôt monté en lecture seule, `cap-drop=ALL`, image `sha256:eee396f1f7e6…`) :

```
REJEU : 1088 tests, 34410 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

- `SansEmailTest` : 8 tests / 17 assertions, vert (instruction 6, rejouée par moi).
- `CommandeReglesTest` : 7 tests (dont le nouveau `adresseNouveau` : `oui` seul `true`, seul `non` explicite `false`), vert.
- `imagine-site` global : 124 tests / 662 assertions, 0 échec.

**Preuves HTTP d'Hermès** (site de démo, non rejouées par moi) : `http-corrections-V2.json` 23/23 verts, `http-base-V2.json` 70/70, `green-concurrence-V2.json` 7/7, `green-adresse-apostrophes-V2.json` 15/15, `c09-final-V2.json` 382 / `failures []`. Aucun échec déclaré.

## 3. Régressions et modifications non demandées

- **Aucune régression** dans la suite autorisée (1088/34410, 0 échec), ni dans les quatre classes C-16.
- **Les quatre fichiers C-16 ne changent que pour les instructions** : aucune retouche parasite. Le branchement du réglage sur le formulaire Settings API de C10 (`CommandeAdmin::register`, capture `ob_start` de la bibliothèque close) est substantiel mais relève de l'instruction 3 (réglage R2) ; il est couvert par les contrôles site `reglages_autres_lots_restaures_exactement` et `reglage_C10_POST_natif_oui/non_reread` (verts) et n'altère aucun test T01. `$direct` est bien défini localement (`CommandeNative.php:103`) et le bloc adresse est sauté en vente directe — pas de notice ni d'écriture indue.
- **Churn hors C-16 dans la fenêtre de diff** : `ExtractionsNatives.php` (nouveau) et les tests `c17/c18/c19` apparaissent dans `git diff 3515cb18 HEAD` ; ils relèvent des lots parallèles, pas de C-16, et la suite reste verte. Pas d'impact C-16.

## 4. Verdict

**Prêt pour la validation de Ced** — pour la seule clôture du code C-16.

Justification : le bloquant R1 est corrigé à la racine (relu dans le code) et reprouvé RED→GREEN sur site ; la lacune de couverture offline est comblée par `SansEmailTest`, **verte dans mon propre rejeu** ; R2/R3 et les réglages suivent la doctrine ; aucune régression, aucune modification non demandée. Les cinq instructions de code sont appliquées proprement, les trois instructions de test aussi.

Réserves à porter à l'attention de Ced (elles ne sont pas des défauts de fond C-16, mais bornent ma vérification) :

1. **Preuves de bout en bout et gate C-09 non rejouables par moi.** Concurrence, interruption, localité, apostrophe et `strict-global = 0` / `C09 382/382` reposent sur les journaux frais d'Hermès, pas sur une exécution de ma part (site/base interdits au relecteur). La levée de la réserve C-09 passe par une correction du lot C-09 (`papier-restauration-V2.json`), hors C-16 : à confirmer au moment d'une clôture C-09 ou globale, pas à l'intérieur de C-16.
2. **Décompte T01 déjà un cran derrière l'arbre** : `PRET` annonce `1077/34327`, mon rejeu donne `1088/34410` (lots C-19 en cours). Le renvoi vers le log couvre la dérive ; rien à corriger côté C-16.

Rappel doctrine §6 : un verdict de vérification n'est jamais un GO. La décision d'avancer, et la confirmation des preuves site/C-09, appartiennent à Ced.
