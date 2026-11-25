# Vérification C-14 — second et dernier tour

Vérificateur : Claude. Date : 25 novembre 2026. Base relue : commit `0a979e2` (25/11 13:48). État vérifié : `HEAD` + arbre de travail.
Référence : `corrections/C-14.md`. Méthode : `git diff 0a979e2..HEAD` sur `wp/`, `production/C-14/` et `docs/`, plus rejeu PHPUnit. Pas de relecture complète refaite.

## 1. Instructions de `corrections/C-14.md` (§4)

**1. C14-01 — préserver le numéro acquis malgré le catalogue. → Appliquée.**
- Dépendance au mapping courant supprimée : `AchatNumero::droit()` ne lit plus `numero`, il exige `instantane` entier > 0 et le renvoie (`AchatNumero.php:27`, `:33`). La clé `numero` du produit courant n'intervient plus.
- Côté adaptateur, le mapping courant (`self::numero(...)`) est retiré du contrat ; seul l'instantané figé de la ligne est passé (`AchatsNumeros.php:137`, `:148`).
- Contrôles conservés : propriétaire (`:60-63` inchangés), paiement (statut + `is_paid()`), remboursement.
- Disponibilité du numéro ajoutée : `publie` exige que le post ciblé par l'instantané reste `imagine_numero` / `publish` (`AchatsNumeros.php:149-150`, requis par `AchatNumero.php:28`).
- Réaffectation = achats suivants seulement, ni A fermé ni B ouvert : libellé produit mis à jour (`AchatsNumeros.php:175` « seuls les achats suivants changent »).
- Gel anti-rétro-octroi conservé (`AchatsNumeros.php:85-89`, « Zéro interdit le rétro-octroi »).

**2. Adapter les oracles de C14-01. → Appliquée.**
- `c14-runtime.php:130` inversé : `reaffectation_produit_conserve_sans_ouvrir_autre` = `$allowed()` **et** B fermé.
- `c14-runtime.php:133` inversé : `retrait_mapping_conserve` = `$allowed()`.
- `:128` conservé : `ancienne_ligne_sans_instantane_fermee_pas_de_retrooctroi` reste fermé (`c14-runtime.php:138`). Cas quantité conservé (`:142-145`).
- Cas « numéro acquis dépublié → fermé » ajouté : `c14-unit.php` (`publication_absente_fermee`, loop `publie => false`), et au niveau natif `c14-corrections-runtime.php:51` (`numero_acquis_depublie_articles_PDF_fermes`) + `:54` publication rétablie → droit rétabli.
- Unité : `AchatNumeroTest.php` (nouveau) `testSnapshotRemainsTheOnlyAcquiredIssue` balaie mapping 13/0/null → acquisition `12` inchangée.

**3. C14-02 — rendre réglable la portée du remboursement. → Appliquée.**
- Règle isolée derrière un réglage nommé `imagine_achat_remboursement` (`AchatsNumeros.php:15`), Settings API + options page `manage_options` (`reglages()` `:17`, `ecran()` `:52`, `register_setting` `:19`, `add_options_page` `:200`).
- Logique pure séparée : `AchatNumero::remboursement()` (`AchatNumero.php:13-16`), défaut prudent = `commande`, aussi appliqué aux valeurs absente/invalide (sanitize `:20`).
- Un remboursement **complet** ferme tout dans les deux modes (`$complete`, `AchatsNumeros.php:128-129`) ; acquis entièrement remboursé reste révoqué.
- Tests des deux positions : `AchatNumeroTest::testRefundScopeDefaultsClosedAndSupportsPerLine` (pur), et natif `c14-corrections-runtime.php:11-27` (modes `commande`/`ligne` × `ventile`/`non_ventile`/`total`, commande à deux numéros a/b).
- Réglage documenté au README (`imagine-site/README.md`, section « Réglages → Achats de numéros »).

**4. Aligner l'état documentaire (C14-03). → Appliquée.**
- `A-VOIR.md:3` corrigé : « Le PRET initial du parent existe (25 novembre, 13:25 CET) » — l'ancien « Aucun PRET créé » a disparu.
- `RAPPORT.md:3-4` : C14-03 marqué fait, distinction « Fait » / « Prêt à relire », PRET existant et inchangé. Cohérent.

**5. Optionnel — N+1 remboursements. → Non appliquée (assumée).**
- La lecture reste une requête `shop_order_refund` par commande (`AchatsNumeros.php:122`, `limit => -1`). Choix explicitement conservé et documenté (README : « N+1 optionnel de la relecture, volume démo »). Instruction optionnelle sans urgence : acceptable.

**6. Reporter les écarts et la décision. → Appliquée.**
- `docs/ecarts.md:40-41` : brief §3.11 à tort → §3.7/§3.9 ; achat invité §3.7 laissé ouvert.
- `docs/decisions.md:57-58` : réglage `imagine_achat_remboursement` (commande|ligne) et achat invité fermé.

## 2. Résultat des tests

- **Rejeu PHPUnit de première main**, commande autorisée (conteneur jetable, sans réseau, dépôt en lecture seule) :
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`
  → **1012 tests, 34006 assertions, 0 échec, 0 erreur, 0 ignoré — PASS.**
  Inclut le nouveau `AchatNumeroTest` (paquet `imagine-site` découvert par T01). Chiffre identique au reçu `validation-corrections.json` (`T01.pass=true`).
- **Recettes natives WP et HTTP non rejouées** : elles exigent un site + une base, interdits au relecteur (doctrine §3). Chiffres **repris des reçus, sans vérification indépendante** : C14 natif **686/686**, non-régression **205/205**, PSR-12 code 0 (`validation-corrections.json`, `resultats.json`, `regressions.json`, `reception-parent.json`). Même limite qu'au premier tour, pour les deux relecteurs.
- Nettoyage déclaré propre : 0 utilisateur / 0 contenu / 0 remboursement temporaire, défaut `commande` (`reception-parent.json`).

## 3. Régressions et modifications non demandées

- **Moteur C-06 intact** : aucun changement sous `wp/plugins/imagine-pilotage/` depuis la version relue. L'adaptateur C-08 (`Paywall`) n'est pas modifié par C-14.
- **Aucune modification C-14 hors périmètre** : le diff des fichiers C-14 correspond exactement aux six instructions ; pas de comportement durci ailleurs.
- **Bruit inter-lots (hors C-14)** : le diff `0a979e2..HEAD` sur `wp/` contient de nombreux fichiers d'autres lots synchronisés en parallèle (C-13 / Envoi : `EnvoiNatif.php`, `EnvoiRegles.php`, `EnvoiRelations.php`, `ListeEnvoiAdmin.php` ; B-02 ; outils `a01`/`a03`/`a04`, `staging`). Hors périmètre de cette vérification ; non évalués ici.
- **Incident C-13 signalé (pas une régression C-14)** : lors des diagnostics C11 pendant la correction, 12 observations synthétiques C13 append-only ont été ajoutées (inventaire `incident-observations-c13.json`), désormais contenues dans une transaction InnoDB rollbackée. Rien d'effacé, incident déclaré et remonté au parent (`RAPPORT.md:34`, `reception-parent.json`). À prendre en connaissance côté C-13, sans effet sur C-14.
- **PRET** : existant du parent, inchangé (SHA-256 `e3aa30e…`, `PRET_unchanged=true`). Il ne vaut pas validation des corrections.

## Verdict

**Prêt pour la validation de Ced.**

Les six instructions sont traitées (cinq appliquées, l'optionnelle N+1 assumée et documentée). C14-01 aligne l'achat payé sur §3.9 « sans limite de durée » : le numéro acquis survit au catalogue et ne s'éteint que si le post `imagine_numero` ciblé est dépublié/supprimé ; le gel anti-rétro-octroi est conservé. C14-02 est isolé derrière un réglage prudent (`commande`) testé dans les deux positions. C14-03 et les écarts/décisions sont alignés. Le cœur pur + moteur passe au rejeu PHPUnit de première main (1012, 0 échec) ; les suites natives/HTTP restent reprises des reçus, limite identique au premier tour.

Aucun problème de fond restant. Deux questions « Pour Imagine » demeurent ouvertes mais, conformément à la doctrine §4 et à la décision du 22/11, elles sont livrées en réglage à défaut prudent et ne bloquent pas le lot.

Un verdict de vérification n'est pas un GO au sens de la doctrine §3.
