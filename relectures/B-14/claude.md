# Relecture B-14 — Claude (relecteur indépendant)

Lot : B-14, page d'accueil dans l'ordre du cahier des charges.
Brief : `briefs/B-14-page-d-accueil-structure.md`. Cahier : §3.2, chapitre 5.
Code lu : `wp/plugins/imagine-site/Accueil.php`, `wp/themes/imagine/front-page.php`, appuis (`functions.php`, `inc/catalogue.php`, `inc/partenaires.php`, `Navigation.php`, `Agenda.php`, `Paywall.php`).
Je n'ai pas ouvert `relectures/B-14/codex.md`. Pas de fusion à ce stade.

## 1. Conformité

- **Ordre des sections conforme.** `Accueil::rendre` (Accueil.php:54-117) émet, dans l'ordre : numéro, conversion, reportage, newsletter, thématiques, événements, Soutenir, coopérative, partenaire du mois. C'est exactement l'ordre du §3.2 (lignes 350-359 du cahier) et des points 1-5 du brief. Le partenaire passe par `imagine_partner_month` (B-05) après la coopérative.
- **Numéro en cours = règle B-04, sans second réglage.** `Accueil::numero` (Accueil.php:15-19) appelle `imagine_issue_query(1)` (functions.php:107-114), tri `imagine_sortie DESC, ID DESC` : la même requête que le kiosque B-04. Conforme à « tu ne crées pas de second réglage ».
- **Couverture : image fixe, seule prioritaire.** Accueil.php:59 — `get_the_post_thumbnail(..., ['loading' => 'eager', 'fetchpriority' => 'high'])`. Le reportage est en `lazy`/`low` (Accueil.php:88). Pas d'autre image prioritaire dans le rendu (le partenaire du mois n'émet pas d'image). Conforme §3.2 et chapitre 5.
- **Conversion conforme.** Découvrir le numéro (permalink du numéro), Acheter (seulement si `imagine_issue_product` renvoie une URL, c.-à-d. produit publié, achetable et en stock — catalogue.php:28-48), S'abonner (page d'attente déclarée, Navigation.php:70-74). Ordre Découvrir / Acheter / S'abonner respecté.
- **Reportage en accès libre.** Accueil.php:21-40 : premier article du numéro (tri `menu_order ASC, ID ASC`) dont le statut est `libre`. Section absente si aucun. Conforme au point 3 du brief.
- **Newsletter par lien seul.** Accueil.php:90-92 : lien vers `/nos-newsletters/`, aucun `<form>` ni champ d'adresse. Conforme (l'inscription visiteur attend Brevo).
- **« Derniers articles » retiré.** Aucun hook résiduel sur `imagine_accueil` hors `Accueil::rendre` (seul `add_action` en Accueil.php:12). A-VOIR le signale. Conforme à « retire la section, et dis-le ».
- **Rien de réservé.** Le rendu n'émet que couverture, titre, date, résumé public du numéro et liens ; le reportage n'est montré que s'il est `libre` (code `libre` strict, pas `decouverte` ni `ouvert`), donc identique pour un anonyme et pour `A-PAPIER`. Pas d'extrait d'article réservé.
- **Interprétation à signaler.** Le reportage « que B-04 désigne déjà » est ré-obtenu, pas lu depuis B-04 : voir point mineur [a].

## 2. Exactitude métier — déroulé à la main

- **Cas A — anonyme, numéro en vente, reportage libre présent.** numéro récent affiché (couverture eager/high, titre, date, résumé) → conversion avec les trois liens → reportage (image lazy) → newsletter → thématiques → 3 événements au plus → Soutenir → coopérative → partenaire avec étiquette « Partenariat ». Conforme.
- **Cas B — produit pas en vente.** `imagine_issue_product` renvoie `''` (produit en brouillon / non achetable) → « Acheter ce numéro » absent (Accueil.php:72-76). Conforme à la preuve du brief.
- **Cas C — aucun article libre.** `libre` renvoie `null` → section reportage absente (Accueil.php:83-89). Conforme.
- **Cas D — profil A-PAPIER.** `libre` ne retient que le code `libre` (contenu réellement ouvert à tous), jamais un article débloqué par l'abonnement (qui serait `ouvert`). Les sections et le reportage sont donc identiques à l'anonyme — c'est bien ce que la preuve exige.
- **Cas limite — aucun numéro publié.** `numero` renvoie `null` → message « Aucun numéro publié. », conversion réduite à « S'abonner » (si page déclarée), reportage absent. Comportement raisonnable, non spécifié par le brief ; acceptable.
- **Cas limite — événements.** `premiersEvenements` (Accueil.php:42-45) conserve l'ordre de `Agenda::groupes()['futurs']` et coupe à 3. Correct (0, 2, 3, 5 donnent [], 2, 3, 3).

## 3. Tests

- **Suite PHP rejouée**, commande autorisée, conteneur jetable sans réseau, dépôt en lecture seule :
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`
  Dernière ligne :
  `REJEU : 1208 tests, 36685 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`
  (`OUTILS : 23 outils, 852 contrôles, 0 échecs` ; `PAQUETS : 12 vérifiés, 0 échecs` ; isolation `network=none`, `rootfs=ro`, mont `wp` en lecture seule.)
- **Dérive de comptage, hors B-14.** L'A-VOIR annonce 1206 tests / 36680 assertions ; le rejeu actuel donne 1208 / 36685. L'écart vient des travaux A-32/A-33 en cours (visibles dans `git status`), pas de B-14 — aucun paquet B-14 en échec. À confirmer, mais non bloquant.
- **Couverture rejouable très mince — voir point important [1].** Dans le rejeu, B-14 n'apporte qu'un seul `testcase` : `AccueilB14Test::testEvenementsConserventOrdreAvecMaximumTrois` (le découpage à 3). L'ordre des sections, l'unique image prioritaire, l'absence de vidéo/iframe, « Acheter » conditionnel et l'étanchéité ne sont vérifiés QUE par `wp/tests/demo/b14-runtime.php` (17 contrôles natifs + 45 navigateur), qui tourne dans la démo WordPress vivante et **n'est pas dans le rejeu**. `verifier.py` relit des JSON enregistrés (`native-final-V2.json`, `browser-final-V2.json`) ; je ne les ai pas ré-exécutés (pas de WP dans le conteneur, pas de droit démo).

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle. Sorties échappées partout : `esc_html`, `esc_url`, `esc_attr` (Accueil.php). `datetime` et texte de `<time>` passent par `esc_attr`/`esc_html`.
- Pas de requête à préparer ici (pas de SQL direct ; `get_posts`/`WP_Query` paramétrés).
- **Paywall respecté.** Rien de réservé n'est émis ; le reportage est filtré sur `libre` strict. Preuve démo : `external == []`, `observation == {http: [], mail: []}`, `buy == 0`, témoins C-26 absents. Aucun appel sortant (rejeu `network=none`). Conforme.

## 5. Doctrine

- **Standard d'abord : respecté globalement.** `front-page.php` natif, hook `imagine_accueil`, API `loading`/`fetchpriority` de WordPress, réutilisation de B-04 (numéro), B-05 (partenaire), B-07 (agenda), B-13 (abonnement). Pas de constructeur de pages, HTML sémantique, lisible sans JavaScript.
- **Conventions §5 respectées** : `declare(strict_types=1)`, espace de noms `Imagine\`, préfixe `imagine_`, textes passés par les fonctions de traduction.
- Voir points mineurs [a] (duplication de la règle de sélection du reportage) et [b] (slugs en dur).

## Points classés

### Important
1. **Les règles centrales du lot ne sont pas couvertes par un test rejouable.** Dans le rejeu, seul le découpage des événements est testé (`AccueilB14Test.php:12`). L'ordre des neuf sections, l'unique image `eager/high`, l'absence de `<video>`/`<iframe>`, « Acheter » hors vente et l'étanchéité ne sont garantis que par la démo `b14-runtime.php`, hors de la commande rejouable. Une régression d'ordre dans `Accueil::rendre` ne serait pas rattrapée par le rejeu standard. Le brief scope sa preuve sur la démo, mais la doctrine (« Les tests d'abord », « Rejouable », « Non-régression ») préfère un garde-fou rejouable. Je le signale au lieu de trancher.

### Mineur
- **[a] Duplication de la règle du reportage libre.** `Accueil::libre` (Accueil.php:21-40) refait exactement la requête + boucle de `single-imagine_numero.php:11-24` (articles du numéro, tri `menu_order ASC, ID ASC`, premier au statut `libre`). Même résultat aujourd'hui, mais pas de source unique : si B-04 change sa désignation, l'accueil ne suit pas. Proposition : extraire un helper partagé (p. ex. `imagine_issue_free_article($issue)`) que les deux appellent.
- **[b] Slugs de pages en dur sans garde.** `/nos-newsletters/`, `/soutenir/`, `/notre-cooperative/` (Accueil.php:91, 112, 114) sont émis sans vérifier que la page existe/est publiée, contrairement à l'abonnement qui passe par `Navigation::abonnementUrl` (Navigation.php:70-74). Risque de lien mort si une page est renommée ou dépubliée. Ce sont des dépendances dures du lot, donc impact faible, mais le garde manque.
- **[c] « S'abonner » disparaît en silence** si la page d'attente n'est pas déclarée (Accueil.php:78-81). Interprétation conforme au brief (« la page d'attente déclarée telle… sinon la même règle »), mais le CTA d'abonnement du §3.2 peut alors manquer sans trace. À confirmer que c'est voulu.

## Décisions techniques, défaut proposé
- **Garde-fou rejouable (point 1).** Défaut proposé : ajouter un test rejouable léger sur l'ordre des sections et l'unicité de l'image prioritaire, avec des bouchons WP minimaux, sans attendre la démo. À défaut, documenter explicitement que le staging vérifié est le seul garant de ces règles. Hermès applique le défaut ; j'arbitre après coup.
- **Helper partagé pour le reportage (point a).** Défaut proposé : factoriser la sélection de l'article libre en une fonction unique appelée par B-04 et B-14.

## Verdict

**À corriger.** Aucun point bloquant. Fonctionnellement conforme au brief et au §3.2, paywall et échappements corrects, rejeu au vert. Un point important (couverture rejouable des règles du lot) et trois mineurs.

Ce verdict n'est pas un GO. Validation visuelle (maquette) réservée à Ced. `codex.md` non lu ; fusion non faite, en attente de consigne.
