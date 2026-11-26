# C-20 — PRET technique corrigé, périmètre réduit accepté le 26 novembre 2026 à 7 h 30
Visible : raccord actif jusqu’au terme payé ; Mon compte sans bouton ; quatre-fois : « faites la demande auprès d’Imagine ».
Reporté au branchement sur staging vérifié avec GO de Ced : bouton, confirmation, émission de `imagine_non_renouvellement_confirme` et preuve de fin native du quatre-fois.

## État courant après la fusion — 26 novembre 2026, 9 h 22

- **1. Bornes du vrai raccord** : `tests/C20PaywallAdapterTest.php`, doublures Memberships/WCS, horloge de requête contrôlée, véritable `Paywall::decisionPdf` et moteur C06. **7 cas / 21 assertions** : sans fin native fermé ; une seconde avant ouvert ; fin exacte/après fermés ; fin Memberships antérieure : juste avant ouvert, exacte/après fermés. Trois mutants jetables détectés (garde de fin, minimum Memberships, ouverture pending-cancel). Aucun changement Paywall/C06/C13, aucune règle recopiée.
- **2. i18n** : quatre codes en PHP pur ; phrases littérales traduites puis échappées dans WordPress. Test du véritable `Renouvellement::afficher`, extraction des quatre littéraux et traduction contenant du HTML hostile jamais rendu brut. Rouges avant correction conservés.
- **3. README** : état courant réduit ; ancien « Pas PRET : le point 2 reste bloqué » uniquement dans l’historique daté. Sections C21/B05/C22 identiques.
- **4. Ordre au branchement** : défaut technique appliqué, ordre actuel `arret_a_terme` avant `quatre_fois` conservé. Priorité pour un quatre-fois natif pending-cancel à décider à ce branchement, pas dans ce lot.
- **5. A-PAPIER hors démo** : méthode native vide ⇒ `EcheancesNatives::methode()` retourne `''`, le vrai papier reste inconnu et risque la présentation `quatre_fois`. Prévoir un raccord de méthode réelle validé au branchement ; aucun drapeau fictif promu en règle réelle.

### À ouvrir maintenant

Base `http://192.168.129.32:8085`, seule cible autorisée ; comptes fictifs C09 habituels, secrets hors dépôt. Route Mon compte native lue à l’exécution.

- A-CARTE : manuel, mention « aucune carte ni passerelle raccordée », sans bouton.
- A-SEPA4 : demande à Imagine, échéances du bloc dues, sans bouton.
- A-VIR/A-PAPIER : manuel, sans bouton.
- « Gérer cet abonnement dans WooCommerce » : vraie fiche native, Cancel/Reactivate absents sur la seule démo. Ne pas déclencher de paiement ni Renew now.
- `/wp-admin/admin.php?page=imagine-liste-envoi` : C13 inchangé, huit lignes restaurées après la sonde.

Nouvelles captures Chromium : `a-carte-fusion-http-1280.png`, `a-sepa4-fusion-http-390.png`. Validation visuelle de Ced toujours attendue.

### Preuves courantes réellement rejouées

- `fusion-V2/preparer-image.log` puis `fusion-V2/t01-final.log` : **1 111 tests, 34 499 assertions, 0 échec/erreur/ignoré**, PHP 8.2 ; conteneur hors réseau supprimé et absence vérifiée.
- `fusion-native-second-V2.json` : **11/11**, accès/contre-exemples, retrait postal attendu de la seule ligne 89 **8 → 7**, aucune tentative mail/HTTP, rollbacks et relecture fraîche exacts.
- `fusion-ui-second-V2.json` : **18/18**, vrais profils sans bouton et propriétaire tiers refusé.
- `fusion-http-second-V2.json` : **27/27**, sessions réelles, quatre dashboards/fiches et deux navigations Chromium, requêtes hors site bloquées.
- `fusion-regressions-second-V2.json` : **C08 30/30, C13 24/24, C09 382/382**, rollbacks et quatre profils/actions exacts.
- `fusion-V2/c22-readback.log` : vérificateur C22 réellement relancé, sources/successeurs/reset exacts. Ses preuves historiques restent **1 102 / 34 454**, natif 19 et HTTP 33 ; ce n’est pas une nouvelle recette C22.
- `fusion-V2/final.json` : nouveau reçu, sources installées relues, contrats partagés préservés. Aucun sceau historique réécrit ; ancien A-VOIR archivé sous `fusion-V2/A-VOIR.md.before`.

**Limites maintenues** : terme payé 25/12/2026 18:01:50 UTC avant clôture 05/01/2027 00:00 Europe/Brussels : exclusion C13 attendue, pas un blocage. C05 sans marge : fin native quatre-fois non essayée, ni prouvée ni écartée. Produits 192/193 privés : pas de reprise. `restants=null` nommé non raccordé. A-PAPIER : abonnement **101**, action **8793 pending**, **2026-11-26 02:13:28 UTC**, exacts ; aucun reset C09.

### Commande parent ciblée

Depuis `C:/Users/Ced/imagine` :

```sh
PYTHONIOENCODING=utf-8 python -B wp/tests/demo/c20-fusion-verifier.py
```

Retour attendu **0**. L’ancien `python -B wp/outils/demo/c20-second.py --verify` dirige aussi vers ce reçu courant. Sans réinstallation ni mutation métier ; contrôle natif frais, C09 et successeur C22 compris. Rejeu unitaire facultatif avec labels neufs : `python -B wp/outils/demo/c20-unit.py LABEL C20`, puis sélection `RenouvellementRegles` avec un autre label.

File voie 2 et fusion C20 relues avant redépôt. Seul C20 traité ; aucun autre lot, verrou, Git ou site touché. **PRET technique réduit uniquement : ni clôture par l’agent, ni validation visuelle, ni GO réel.**

---

## Historique daté — réception de 7 h 30 avant la présente fusion

Tout ce qui suit est conservé pour traçabilité : anciens compteurs, commandes et conclusions ne décrivent pas le reçu courant ci-dessus.

## Preuves courantes après requalification

- `closure-0730-native-green-second-V2.json` : **11/11**, accès, contre-exemples fermés, postal attendu, aucune tentative mail/HTTP, rollbacks exacts et relecture fraîche des quatre profils/actions.
- `closure-0730-ui-second-V2.json` : **18/18**, vrais profils sans bouton, propriétaire tiers refusé.
- `closure-0730-regressions-second-V2.json` : **C08 30/30, C13 24/24, C09 382/382**, rollback exact et profils/actions inchangés.
- Canonique courant déjà exécuté par C21 : **1 097 tests, 34 443 assertions**, sans échec/erreur/ignoré (`production/C-21/rejouer-final.log`). Aucun paquet ajouté ici : pas de nouvelle préparation d’image.
- `final-closure-0730-successor-V2.json` : nouveau sceau du périmètre réduit, sources installées relues, C21 revérifié par ses contrats propres, fixtures absentes. Aucun payload ancien réinstallé.

**Postal attendu** : le terme payé du 25 décembre 2026 à 18:01:50 UTC précède la clôture du 5 janvier 2027 à 00:00 Europe/Brussels ; la seule ligne 89 sort (**8 → 7**, motif `expire`), les sept autres restent exactement identiques. Accès actif et B02 restent inchangés. Après rollback, la liste retrouve huit lignes. Assertion courante : `pending_cancel_paid_term_before_cutoff_excludes_only_this_subscription`. Règles C13 inchangées ; ancien rouge et `final-second-V2.json` conservés, pas réécrits.

**Commandes parent, depuis C:/Users/Ced/imagine** :

```sh
PYTHONIOENCODING=utf-8 python -B wp/outils/demo/c20-second.py --verify
PYTHONIOENCODING=utf-8 python -B wp/tests/demo/c21-verifier.py
```

Retour attendu **0**, prêt technique sur le seul périmètre réduit, pas clôture/validation visuelle/GO réel. Rejeu facultatif : `--probe parent-0730-native`, `--ui parent-0730-ui`, `--regressions parent-0730-regressions` sur `c20-second.py`, labels neufs, retour attendu 0. Aucun code fonctionnel modifié, aucune nouvelle capture. Premier essai de la nouvelle assertion : objet ListeEnvoi rencontré ; normalisation JSON corrigée dans le test seul, puis rejeu vert et restauration relue.

## Historique deuxième passe — ci-dessous remplacé par la consigne de 7 h 30

Les mentions « pas PRET », l’arrêt postal et les anciennes commandes/compteurs ci-dessous décrivent uniquement la réception antérieure, conservée pour traçabilité. La section courante ci-dessus et PRET font foi pour cette livraison.

## À ouvrir sur imagine-test-demo seulement

Base : `http://192.168.129.32:8085` ; comptes fictifs C09 habituels, secrets hors dépôt.

- `/my-account/`, A-CARTE : bloc Renouvellement manuel, sans bouton ; déclaration explicite « aucune carte ni passerelle raccordée ».
- Même page, A-SEPA4 : « Pour ne pas renouveler votre engagement en quatre fois, faites la demande auprès d’Imagine ; les échéances du bloc en cours restent dues. » Aucun bouton ; échéancier B02 inchangé.
- Même page, A-VIR et A-PAPIER : renouvellement manuel, sans bouton.
- Le lien B02 « Gérer cet abonnement dans WooCommerce » ouvre les vraies fiches natives : `/my-account/view-subscription/89/`, `/92/`, `/98/`, `/101/`. Sur ce **seul site fictif local**, Cancel/Reactivate sont également retirés : aucun détour par une action connue non sûre. Les autres actions Woo ne constituent pas une recette C20 ; ne pas cliquer Renew now ni lancer de paiement.
- `/wp-admin/admin.php?page=imagine-liste-envoi`, référent : écran C13 inchangé, liste courante restaurée de huit lignes.

Captures Chromium après vraie navigation native : `a-carte-http-final-source-1280.png`, `a-sepa4-http-final-source-390.png`. Messages lisibles, sans bouton ; validation visuelle de Ced encore attendue.

## Livré / arrêté, point par point

1. **Raccord livré.** Code installé et documentation officielle confirment pending-cancel → adhésion pending. Seul ce couple lié et borné devient actif dans Paywall ; pending non lié, lié à active ou au premier paiement reste fermé. C06, C05 et les règles/raccords C13 sont inchangés.
2. **Arrêt : maintien postal non obtenu.** La sonde native réelle conserve désormais `abonnement_actif` et les valeurs B02, mais le terme payé devient **25 décembre 2026 à 18:01:50 UTC**, avant la clôture du prochain numéro, **5 janvier 2027 à 00:00 Europe/Brussels** (sortie le 15 janvier). C13 retire réellement la ligne 89 : **8 → 7**. Le contrôle compare des JSON normalisés, pas l’identité d’objets PHP. Aucun droit postal forcé. Ni bouton de non-renouvellement ni confirmation d’action réussie livrés. Seule la présentation d’un état pending-cancel, date native et valeurs B02, a été éprouvée dans la sonde.
3. **Fallback quatre-fois livré ; écriture de fin native non essayée.** La marge C05 est `null` ; son planificateur refuse `MARGE_OBLIGATOIRE`. Impossible de lire la fin du bloc suivant sans choisir un réglage absent : arrêt **avant toute écriture de end**. Ce n’est pas une preuve d’échec du moteur natif Subscriptions ; cette sonde reste à exercer sur un échéancier C05 valide. Aucune date calculée à la main, échéance annulée ou valeur de réglage modifiée. La phrase Imagine sans bouton est un défaut prudent, pas un contournement.
4. **Reprise refusée, cause exacte documentée.** Produits natifs **192** et **193** privés ; `can_be_updated_to('active')` bloque d’abord sur `contains_unavailable_product()`. Les souscriptions sont déjà manuelles : la méthode vide n’est pas le verrou immédiat. Aucun produit publié, passerelle inventée ou statut forcé. Aucun cas natif permis disponible parmi ces profils, donc aucun faux bouton.

Le compteur B02 reste `restants=null`, nommé non raccordé ; aucun historique inventé. `Renouvellement::HOOK_CONFIRMATION` réserve `imagine_non_renouvellement_confirme`, **non émis** faute de succès sûr. Aucun email, appel bancaire, remboursement ou rétractation.

## Preuves courantes

- `t01-second-final.log` après préparation d’image et derniers octets PHP : **1 093 tests, 34 426 assertions, 0 échec/erreur/ignoré** ; conteneur hors réseau et nettoyage vérifié.
- `presentation-final-source-second-V2.json` : **18/18**, vrais profils, libellés, boutons natifs retirés, propriétaire tiers refusé.
- `http-final-source-second-V2.json` : **27/27**, vrais cookies, quatre dashboards/fiches, deux vrais parcours Chromium et captures ; aucune requête hors site.
- `non-regression-final-source-second-V2.json` : **C08 30/30, C13 24/24, C09 382/382**, recettes natives rollbackées, relecture fraîche exacte.
- `native-final-blocked-second-V2.json` : réception C20 maintenue rouge sur **pending_cancel_shipping_unchanged**, autres contre-exemples fermés et rollback exact.
- `final-second-V2.json` : sceau successeur **partiel**, sources actuelles/installées relues, bibliothèques closes intactes, profils/actions exacts, **PRET absent**.

A-PAPIER : **abonnement 101, action 8793, pending, date 2026-11-26 02:13:28 UTC**, inchangés. Pas de reset C09. Chaque mutation de sonde est annulée dans InnoDB puis les quatre profils/actions sont relus dans un processus distinct. Caches/sessions peuvent évoluer entre requêtes : pas de promesse d’identité globale de la base.

`natif.md` contient les références officielles, méthodes installées et limites. Treize preuves brutes de première passe inchangées ; anciens A-VOIR/natif archivés sous `legacy-*-before-second-V2.md`. Rouges TDD conservés. Aucun sceau historique d’un autre lot réécrit.

Delta : branche Paywall étroite, classes `Renouvellement{,Regles}.php`, chargement bootstrap et hook d’affichage B02 additifs, README complété. `c20-verifier.py::matches_predecessor()` fournit un pont lié **aux octets scellés** vers les hashes antérieurs, puis vers le contrat C19 si nécessaire ; les anciens gates à hash global ne sont pas réécrits pour les verdir.

## Commandes parent, depuis C:/Users/Ced/imagine

```sh
PYTHONIOENCODING=utf-8 python wp/outils/demo/c20-second.py --verify
PYTHONIOENCODING=utf-8 python wp/outils/demo/c20-second.py --ui parent-ui
PYTHONIOENCODING=utf-8 python wp/outils/demo/c20-second.py --regressions parent-regression
PYTHONIOENCODING=utf-8 python wp/tests/demo/c20-http.py http-parent
```

`--verify` retourne 0 pour **l’intégrité de la livraison PARTIELLE**, jamais « C20 accepté ». Le contre-exemple mutateur se rejoue explicitement avec `python wp/outils/demo/c20-second.py --probe parent-native` : **retour attendu 1**, réception postale rouge et rollback. Image : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1` ; suite : même commande avec `rejouer.ps1`.

File voie 2 et correction C19 relues ; pas de correction C20 présente. C19 Q1 reste en attente selon le parent. Aucun C21/B05/C22 pris. Aucun verrou ni Git touché. **Pas PRET : les critères autorisés du parcours sûr ne sont pas tous satisfaits.**
