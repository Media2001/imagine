# Vérification C-12 — 2e et dernier tour (Claude, vérificateur)

Date : 2026-11-24. Vérificateur : Claude. Objet : contrôler que `corrections/C-12.md` a bien été appliqué par Hermès, sans refaire une relecture complète.

Méthode : `git diff` entre le commit où la fusion a été écrite (`52f8f10`, 10:48 — état relu) et HEAD, sur `wp/` et `production/C-12/` ; lecture ciblée des fichiers touchés ; tentative de rejeu des tests.

---

## 1. Application des instructions de `corrections/C-12.md`

**Instruction 1 (Bloquant — P1) : rétablir le filtre éditorial par article. → Appliquée.**
- Forçage supprimé : `$content['decouverte'] = true;` n'existe plus dans `Decouverte::decider()`.
- Porte ajoutée : `Decouverte.php:194` refuse la découverte si `($content['decouverte'] ?? false) !== true` (retourne `$base`, extrait).
- Désignation réelle lue : `Paywall.php:80-81` renseigne `decouverte` via `metadata_exists('post', …, 'imagine_decouverte')` + valeur vraie, à la place du `false` codé en dur.
- Métadonnée native déclarée : `register_post_meta('post','imagine_decouverte',…)` (`Decouverte.php:24-30`), `auth_callback` = `edit_posts`.
- Absence / faux / invalide ⇒ fermé, et combiné avec la liste des numéros (`Decouverte.php:199-200`).
- Couvert par trois voies : PHPUnit `testOnlyDesignatedArticleOfSameIssueCanOpenAndConsume`, PHP `non_designe_sans_ouverture` / `non_designe_meme_numero_sans_credit`, HTTP `un_designe_par_numero_existant` / `non_designe_meme_numero_sans_ouverture_HTTP` / `designation_absente_HTTP_fermee_sans_etat`.

**Instruction 2 (Important — P7) : test rejouable du raccord, dont « deux articles d'un même numéro, un seul désigné ». → Appliquée.**
- Nouveau banc hors réseau : `wp/plugins/imagine-site/tests-c12/DecouverteTest.php` (7 tests), `tests-c12/fixture.php` (doublures WP/SQL, vrai Paywall + raccord + moteur C06), `phpunit.c12.xml`, plus `wp/outils/demo/c12-unit.py`.
- Le cas exigé est présent : `testOnlyDesignatedArticleOfSameIssueCanOpenAndConsume` (`DecouverteTest.php:46-55`) — article non désigné du même numéro reste en extrait, sans état ; seul le désigné ouvre et consomme.
- Ouverture, décompte, relecture idempotente, épuisement, contournement et persistance refusée également couverts.

**Instruction 3 (Important — P2) : ne pas figer la fermeture de la relecture après quota. → Appliquée.**
- Transformée en réglage : option `imagine_decouverte_relecture` (`Decouverte::RELECTURE`), valeurs `fermee` (défaut) / `rester_lisible`, sanitize + journal d'audit (`DecouverteReglages.php:18-21, 84-97, 141`).
- Branchement : `Decouverte.php:218-220` passe le **rang** de l'article déjà vu au moteur quand `rester_lisible` + forme `articles` + déjà vu, sinon `count(articles)` ; jamais de recrédit du stockage.
- Conforme à la doctrine §4 (« règle ouverte = réglage, défaut prudent fermé »). La question reste ouverte pour Imagine mais ne bloque plus. Testé : PHP `relecture_apres_quota_fermee_sans_credit` + `relecture_apres_quota_lisible_sans_recredit` ; HTTP `relecture_apres_quota_defaut_fermee_HTTP` / `…_rester_lisible_HTTP` / `relecture_lisible_aucun_nouveau_droit_HTTP`.

**Instruction 4 (Mineur — P3) : corriger l'attribution « conformément au moteur C06 ». → Appliquée.**
- `A-VOIR.md` ne contient plus « conformément au moteur C06 » ; l'étape 6 dit explicitement « deux politiques réglables du raccord, pas une contrainte C06 ». L'écran C-10 le répète (« pas une contrainte du moteur C06 »).

**Instruction 5 (Mineur — P4) : compléter A-VOIR d'un pas montrant le cas réel. → Appliquée.**
- `A-VOIR.md` étapes 3 à 6 ajoutent l'article `c12-decouverte-non-designe` (même numéro 39), la relecture après quota et le choix du réglage — P1 et P2 sont désormais visibles, non contournés.

**Instruction 6 (Mineur — P5) : rendre discriminant `futur_pas_de_credit`. → Appliquée.**
- `c12-runtime.php:53-57` : `futur_pas_de_credit` vérifie maintenant le motif exact `contenu_futur_ferme_par_reglage` **et** l'état identique (`=== $availableState`) avec quota disponible ; ajout de `futur_sans_etat_motif_sans_ouverture` (sans état). Repris en PHPUnit `testFutureWithNoStateAndAvailableQuotaIsNonConsuming`.

**Instruction 7 (Mineur — P6) : reformater la signature de `decider()` en PSR-12. → Appliquée.**
- `Decouverte.php:185-191` : un argument par ligne, parenthèse fermante et type de retour sur leur ligne. Comportement inchangé.

**Instruction 8 : rejouer PHP/HTTP avec « deux articles d'un même numéro, un seul désigné ». → Appliquée (preuve fournie, non rejouée par moi — voir §2).**
- Le seed installe trois témoins désignés (numéros 39/25/18) + un non désigné du 39 (`c12-seed.php`) ; la recette HTTP exerce le cas (`c12-http.py`, checks `un_designe_par_numero_existant`, `non_designe_meme_numero_*`). `resultats.json` les rapporte verts.

---

## 2. Résultat des tests

**Je n'ai pas pu relancer les tests moi-même.** Dans cette session, toute exécution est refusée par le mode de permission : `php`, `pwsh` et la commande autorisée `./wp/tests/rejouer.ps1` renvoient « requires approval ». C'est la même limite qu'au 1er tour (dépôt en lecture seule, pas d'accès à la démo `192.168.129.32:8085`, pas d'exécution locale).

Ce que j'atteste donc :
- **Preuve fournie par le producteur** (`production/C-12/resultats.json`) : statut `VERT`, 186 contrôles — PHPUnit hors réseau 7 tests / 63 assertions, 32 PHP natifs, 85 HTTP, 29 C-11 ciblés, 33 unitaires Python. Toutes les clés sont à `true`.
- **Corroboration statique** : j'ai relu le banc PHPUnit hors réseau et les recettes PHP/HTTP. Ils couvrent réellement les points corrigés (P1 par désignation par article, P2 par réglage à deux valeurs, P5 discriminant). Le banc `tests-c12/` est bien rejouable sans réseau ni base (doublures WP/SQL, vrai moteur C06) : la doctrine « rejouable » est désormais satisfaite pour le raccord, là où elle ne l'était pas au 1er tour.

Réserve : les 186 verts restent une preuve **produite par Hermès**, non reproduite ici. Un rejeu dans un cadre où l'exécution est autorisée (NUC, hors cette session) reste nécessaire pour transformer cette preuve en vérification indépendante — en particulier le banc `phpunit.c12.xml`, que le runner partagé `rejouer.ps1` ne sélectionne pas (limite documentée dans `A-VOIR.md`).

---

## 3. Régressions et modifications non demandées

- **Aucune régression détectée sur le raccord découverte C-12.** Les corrections sont localisées ; la logique d'ouverture, de décompte atomique et d'étanchéité relue au 1er tour est inchangée.
- **Modifications hors périmètre `corrections/C-12.md` présentes dans `wp/` depuis l'état relu** — à signaler, non vérifiées par moi (hors mandat C-12) :
  - `wp/plugins/imagine-site/PdfNumero.php` (+52 lignes) : nouvelle frontière `withinDirectory()`, suppression centralisée des copies PDF publiques (`removePublicCopies()`), `protect()` prend un paramètre `$publicCopies`.
  - `wp/themes/imagine/single-imagine_numero.php` : le lien PDF est maintenant conditionné à `Paywall::decisionPdf(...)['complet']` (auparavant affiché dès que l'URL existait) — durcissement du chemin PDF C-11.
  - `wp/plugins/imagine-site/Paywall.php:108` : mémoïsation de l'instant via `self::$requestInstant ??= …` sur le chemin PDF.
  - `wp/outils/demo/c11-*.php|py`, `wp/tests/demo/c11-*.php|py`, `PdfNumeroTest.php` / `pdf-fixture.php` : changements liés au PDF C-11.
  - Ces changements touchent le **chemin PDF (C-11)**, pas le raccord découverte ; ils n'altèrent pas la conformité C-12.
  - **À réconcilier :** `production/C-12/RAPPORT.md` affirme « aucun … PdfNumero C11 touché », ce que le `git diff` contredit. Soit ces changements relèvent d'un lot C-11 concurrent synchronisé dans la même fenêtre (probable), soit la phrase du RAPPORT est inexacte. À attribuer à leur lot et à vérifier là-bas, pas sous C-12.

---

## 4. Verdict : **Prêt pour la validation de Ced**

Les 8 instructions de la fusion sont appliquées. Le point bloquant P1 (élargissement de l'accès à tous les articles réservés d'un numéro) est corrigé à la racine : désignation éditoriale native obligatoire, fermé par défaut, et prouvé par un banc rejouable hors réseau. Le point P2 est traité selon la doctrine §4 (réglage à deux valeurs, défaut prudent fermé) : la question à Imagine reste ouverte mais ne bloque plus la clôture du lot de code. Les mineurs P3–P6 sont faits. Aucun problème de fond ne subsiste sur le raccord découverte.

Deux réserves, qui ne sont pas des problèmes de fond mais que Ced doit connaître avant de valider :
1. **Preuve des tests non reproduite ici** (exécution refusée dans cette session). Les 186 verts sont fournis par Hermès et corroborés par lecture statique, pas rejoués indépendamment. Un rejeu dans un cadre autorisé reste à faire — il devra inclure `phpunit.c12.xml`, hors du runner partagé.
2. **Questions encore ouvertes pour Imagine** (relecture après quota ; déclencheur / forme / durée / nombre / périmètre). Elles sont isolées derrière des réglages à défaut fermé, conformément à la doctrine ; la clôture n'attend pas la réponse, mais ces arbitrages métier restent à faire remonter.

**Rappel : ce verdict n'est pas un GO.** Il vaut pour la clôture d'un lot de code ; il ne vaut ni validation visuelle, ni accord de mise en ligne, ni autorisation de paiement, d'installation ou d'envoi (doctrine §3 et §6).
