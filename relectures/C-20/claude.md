# Relecture C-20 — « Ne pas renouveler », deuxième passe (Claude)

Lot : `briefs/C-20-ne-pas-renouveler-2.md`. Cahier des charges §3.4, §3.7, §3.8. Arbitrage `docs/arbitrages-2026-11-26.md` (passage de 4 h **et** passage de 7 h, qui réduit le périmètre). Code dans `wp/plugins/imagine-site/` ; production dans `production/C-20/`.

Relecteur sans accès au site de démonstration : le code pur est relu et rejoué ; les sondes du site (`c20-second.py`, probes HTTP) ne sont pas rejouables ici (hors réseau, dépôt en lecture seule, pas d'accès à `imagine-test-demo`). Je m'appuie sur les JSON d'Hermès pour ces preuves, liés au code par empreintes.

## 0. Périmètre réellement livré

Le brief C-20-2 demande quatre choses (raccord, bouton carte, fin native quatre-fois, reprise). Le **passage de 7 h** a réduit le périmètre à : raccord corrigé + écrans sans bouton + phrase quatre-fois. Bouton, confirmation, émission de `imagine_non_renouvellement_confirme` et preuve de fin native sont reportés au lot de branchement (staging vérifié, Stripe test, GO de Ced). Je juge la conformité au brief **tel qu'amendé par l'arbitrage de 7 h**, et je signale le reste comme écart (déjà tracé).

## 1. Conformité

- **Point 1 — raccord (fait).** `Paywall.php:249-253` ajoute une branche : adhésion Memberships `pending` + abonnement Subscriptions `pending-cancel` + date de fin native renseignée ⇒ lecture `actif`. Les bornes restent `min(fin adhésion, fin abonnement)` (`Paywall.php:224-225`) et passent au moteur C06 (commentaire `:251-252`). Conforme au §3.4 et au point 1 du brief. Les métadonnées natives sont lues dans le code **installé** (`native-details-second-V2.json`), pas déduites d'un libellé ; `natif.md` cite la doc officielle Memberships. Bien.
- **Contre-exemples fermés.** Adhésion `pending` liée à un abonnement `pending` (premier virement) ⇒ branche `:243-248` ⇒ `virement_non_valide` ; adhésion `pending` non liée ⇒ `subscriptionId` vide, état de base `virement_non_valide` ; adhésion `pending` liée à `active` ⇒ reste fermée. Conforme à l'exigence « tous les autres cas gardent leur lecture actuelle ».
- **C-13 non touché, à raison.** Le raccord de la liste d'envoi (`EnvoiNatif.php:60`) lit `$sub->get_status()` directement et ne consulte jamais l'état Memberships `pending` pour décider de l'abonné actif. Il ne porte donc pas la confusion ; laissé inchangé, conforme au point 1 (« s'il porte la même confusion »).
- **Point 2 — bouton carte (reporté).** Non livré : sur la démo, aucun abonnement n'est en reconduction automatique (toutes manuelles, passerelle vide — `c09-seed.php:264-265`), donc aucun profil honnête pour un bouton. Reporté. Autorisé par l'arbitrage de 7 h, écart tracé (`docs/ecarts.md:55`).
- **Point 3 — quatre-fois (repli livré).** `RenouvellementRegles.php:20-22` : période `month`, intervalle `3` ⇒ phrase « faites la demande auprès d'Imagine ; les échéances du bloc en cours restent dues », sans bouton. Conforme au repli prévu. La fin native n'a pas été essayée car la marge C05 est `null` et Hermès a refusé d'en inventer une (`c20-second-native.php:116-121`) — bon réflexe (doctrine §1). Ni prouvée ni écartée : écart tracé.
- **Point 4 — reprise (refusée, cause documentée).** `can_be_updated_to('active')` bloque sur `contains_unavailable_product()` (produits 192/193 `private`) ; cause lue dans le code installé (`natif.md`, point 4). Pas de faux bouton. Conforme.
- **Interprétation signalée.** Le critère « liste d'envoi inchangée » du premier brief est reconnu faux (terme payé 25/12/2026 avant clôture 05/01/2027 ⇒ ligne 89 sort, 8→7) ; c'est le comportement attendu de C-13 inchangé. Correctement assumé (arbitrage de 7 h, `ecarts.md:56`).

## 2. Exactitude métier — cas déroulés à la main

- **Cas §3.4, raccord (carte qui désactive).** Abonnement → `pending-cancel`, Memberships → `pending`. `Paywall::rights` : match de base `pending`→`virement_non_valide`, puis branche `:249` (pending-cancel + pending + end≠'') → `actif` ; bornes = min(fins natives). Attendu : accès maintenu jusqu'à la date de fin. Code conforme ; sonde `adapter-green-with-shipping-blocker-second-V2.json` et `c20-second-native.php:59-60` le confirment.
- **Cas contre-exemple A-VIR (premier virement non reçu).** Abonnement `pending`, adhésion `pending`. Branche `:243-248` → `virement_non_valide` → fermé. Attendu : fermé. Conforme (`A_VIR_first_payment_closed`, `c20-second-native.php:156-158`).
- **Cas §3.4 quatre-fois (A-SEPA4, `normal-4`).** `methode` = '' (non A-VIR/A-PAPIER, `EcheancesNatives.php:32-33`) ⇒ condition 2 sautée ⇒ condition 3 (`month`/`3`) ⇒ `quatre_fois`, pas de bouton. Attendu : phrase Imagine, échéances du bloc dues. Conforme.
- **Cas limite liste d'envoi (ligne 89).** Terme payé 2026-12-25 18:01:50 UTC < clôture 2027-01-05 00:00 Europe/Brussels ⇒ exclusion `expire` de la seule ligne 89, sept autres identiques. Attendu par les règles C-13 inchangées. Conforme (`c20-second-native.php:69-76`).

## 3. Tests

- Suite PHP rejouée en conteneur jetable (sans réseau, dépôt en lecture seule), commande autorisée sans argument :
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`
  Dernière ligne :
  **`REJEU : 1101 tests, 34451 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`**
- `RenouvellementReglesTest.php` couvre les cinq modes de présentation (quatre_fois, manuel prime sur trimestriel, automatique non prouvé → indisponible, arret_a_terme sans promesse de reprise, manuel sans bouton). Tests de règle, pas de simple répétition du code.
- **Limite.** Le raccord `Paywall::rights` (branche pending-cancel) est couplé à WordPress ; il n'est pas testé par la suite pure mais par la sonde du site (`c20-second-native.php`, JSON `adapter-*`), que je ne peux pas rejouer. Les contre-exemples y figurent (pending lié actif, pending non lié, A-VIR), rollback transactionnel exact vérifié. Preuve d'Hermès, non reproduite ici.

## 4. Sécurité et données

- **Propriété vérifiée partout.** `Renouvellement::afficher` (`Renouvellement.php:42`) refuse si le propriétaire ≠ utilisateur courant ; `MonCompte::donnees` filtre par `get_current_user_id()` ; filtre d'édition d'adresse (`MonCompte.php:28-29`) idem. Un abonné ne peut pas agir sur l'abonnement d'un autre. Aucun ID pris dans GET/POST.
- **Pas de fuite paywall.** Le raccord n'accorde `actif` que jusqu'à la date de fin native (bornes min + moteur C06), pour un état que Memberships considère lui-même encore ouvert pendant l'attente d'annulation (doc citée dans `natif.md`). Étanchéité C-08 inchangée (suite verte).
- **Hors ligne.** Sonde sans mail ni HTTP (`no_mail_http_attempt`), transactions InnoDB annulées. Données fictives `@example.org`, aucun secret. `Renouvellement::actions` retire Cancel/Reactivate natifs **uniquement** sur la démo (garde environnement + `home_url` + option, `Renouvellement.php:32-33`) : présentation démo, pas une politique réelle.
- **Filtre WCS.** `wcs_view_subscription_actions` est bien appliqué avec 3 arguments côté WCS installé (`native-details-second-V2.json`, `wcs_get_all_user_actions_for_subscription`) ; la signature `actions(array, $sub, int $user)` en `accepted_args 3` ne provoque pas d'erreur d'arité. OK.

## 5. Doctrine

- **Standard d'abord.** Aucune table de droits dupliquée, aucun ordonnanceur maison ; on s'appuie sur l'API native (`update_dates`, statuts Subscriptions/Memberships). Conforme §4.
- **Rien inventé.** Marge C05 absente → arrêt avant toute écriture de `end`, pas de date calculée à la main. Conforme §1.
- **Conventions §5 — à corriger (mineur).** Les messages de `RenouvellementRegles` sont des chaînes françaises brutes passées à `__()` via **variable** (`Renouvellement.php:48` : `__($view['message'], …)`). Les outils d'extraction i18n ne les voient pas ; le texte s'affiche en français mais n'est pas traduisible proprement (doctrine §5 « passés par les fonctions de traduction »).

## Verdict

**Conforme** — dans le périmètre réduit autorisé par l'arbitrage de 7 h. Ce verdict n'est pas un GO (doctrine §6) ; il ne vaut que pour la clôture d'un lot de code, et le lot ne tient pas encore le §3.4 côté utilisateur.

Points classés :

**Important**
1. **§3.4 non tenu côté utilisateur.** Le cœur du brief (bouton « ne pas renouveler » + confirmation) n'est pas livré. Ce n'est pas un défaut de code : c'est un report autorisé et tracé (`ecarts.md:55`, arbitrage de 7 h) faute de profil honnête sur la démo. À rouvrir au lot de branchement. Je le signale pour que la clôture ne soit pas lue comme « §3.4 fait ».

**Mineur**
2. `Renouvellement.php:48` — message passé à `__()` par variable : non extractible par l'i18n (doctrine §5). Enregistrer les chaînes littéralement dans `RenouvellementRegles` et ne traduire que des littéraux.
3. `RenouvellementRegles.php:12` — l'ordre des conditions fait primer `arret_a_terme` (pending-cancel) sur `quatre_fois`. Hors périmètre aujourd'hui (pas de bouton, Cancel natif retiré sur la démo), mais si un quatre-fois passait un jour en `pending-cancel` natif, l'écran dirait « s'arrêtera à la date indiquée » alors que le natif coupe le bloc. À verrouiller au lot de branchement.
4. `EcheancesNatives.php:32-33` — la méthode de A-PAPIER (`normal-4`) ne vaut `imagine_papier` que si le drapeau fictif passe ; hors démo, A-PAPIER tomberait dans `quatre_fois` au lieu de `manuel`. Sans effet sur la cible (tout est scoped démo), à noter pour le branchement.

## Décisions techniques, défaut proposé

- **Preuve du raccord non rejouable par le relecteur.** Technique. Défaut proposé : accepter la preuve d'Hermès (JSON `adapter-*`, rollback exact, contre-exemples présents) liée au code par empreinte, comme pour les autres lots démo (C-16/C-17/C-18). Claude arbitre après coup si une divergence apparaît.

## Pour Imagine

- **Abonné qui ne renouvelle pas et numéro suivant son terme.** Question métier déjà rangée (arbitrage de 7 h) : reçoit-il le numéro dont la clôture tombe après son terme payé ? Défaut : règles C-13 actuelles, donc non. Rien à trancher dans ce lot.

## Suite

`codex.md` existe mais n'est pas ouvert (consigne). Pas de fusion à ce stade (consigne). Je m'arrête après ce rapport.
