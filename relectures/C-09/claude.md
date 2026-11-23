# Relecture C-09 — Profils de test créés par script (Claude, relecteur indépendant)

Relecture du brief `briefs/C-09-profils-de-test.md`, du script `wp/outils/demo/profils.py`, du seed `wp/outils/demo/c09-seed.php`, du catalogue `wp/outils/demo/c09-profils.json`, des recettes `wp/tests/demo/c09-*` et des livrables `production/C-09/`.

**Rappel de méthode.** Les cas site (connexion, WP-CLI, objets natifs) exigent la démo `imagine-test-demo` démarrée : je ne m'y connecte pas (doctrine §3). Je me suis appuyé sur les preuves d'Hermès (`readback.json`, `http.json`, `integrite.json`) pour l'état runtime, et j'ai déroulé à la main les décisions du paywall. Seuls les tests **locaux** du lot ont été exécutés par moi (voir §3).

---

## 1. Conformité

- **Livrables présents.** Script rejouable `.py` (autorisé par le brief), `A-VOIR.md` (tableau créé/partiel/impossible + une phrase par profil + section de propositions pour `docs/recette/profils.md`), preuve de décision par profil (colonne « Décision réelle sur ID81 » + `readback.json`), `PRET`. Conforme au brief.

- **Objets natifs, pas de drapeaux.** Le seed crée de vrais `WC_Order`, `WC_Subscription`, `WC_Memberships_User_Membership` (`c09-seed.php:121-222`), jamais une méta posée à la main pour simuler un droit. Conforme à l'exigence centrale du brief et à la doctrine §4 (« pas des drapeaux posés à la main »).

- **Identifiants prévisibles.** `login = code.lower()` et `email = login@example.org` (`profils.py:12`, `c09-seed.php:86`). Mots de passe générés et écrits dans le fichier hors dépôt de B-00 (`~/.imagine-demo/identifiants.json`, clé `c09_accounts`, `profils.py:67-72`). Conforme.

- **Important — l'attribut « renouvellement activé » n'est pas représenté (`c09-seed.php:174`).** `set_requires_manual_renewal(true)` est appliqué à **tous** les abonnements natifs. Or le brief distingue A-CARTE/A-ECHEANCE « renouvellement activé » de A-NONRENOUV « a désactivé le renouvellement ». A-NONRENOUV est bien rendu par `pending-cancel` (`c09-seed.php:190`), mais A-CARTE/A-ECHEANCE se retrouvent en renouvellement **manuel**, c'est-à-dire reconduction automatique **désactivée** — l'inverse de leur état de départ. L'attribut qui définit ces deux profils est donc perdu. Hermès le mentionne (« renouvellement manuel de sécurité ») mais ne signale pas que cela inverse l'attribut testé. *Proposition : soit ne pas forcer le renouvellement manuel sur les profils « renouvellement activé » et laisser le drapeau natif de reconduction à `true` (sans jeton de paiement), soit dire explicitement dans A-VOIR que « renouvellement activé » n'est pas démontrable hors ligne. Choix à arbitrer — voir §Verdict.*

- **Important — les profils « mode de paiement » convergent vers un objet quasi identique.** A-CARTE (carte), A-SEPA4 (domiciliation 4×), A-PAYPAL, A-PAPIER produisent le même objet : abonnement annuel actif, sans moyen de paiement, à 0 €, renouvellement manuel (`c09-seed.php:164-199`). Sur la démo, on ne peut donc pas distinguer un abonné carte d'un abonné PayPal ou SEPA. C'est honnêtement déclaré profil par profil dans A-VOIR, et c'est inhérent à la démo hors ligne (passerelles coupées par B-00). Mais c'est la limite centrale du livrable : la valeur de test de ces quatre profils est fortement réduite. Non bloquant (le brief admet les partiels et liste impossible/ambigu), à connaître.

- **Interprétation du mot « créé ».** Hermès redéfinit « créé » = « état de départ **entièrement** disponible » et classe en « partiel » dès qu'un élément manque (A-VOIR, bloc « Lecture des résultats »). D'où seulement 5 « créé ». Interprétation signalée, donc acceptable au regard de la doctrine §1. Mais elle est stricte : V-INSCRIT (« compte vérifié, jamais abonné, découverte non ouverte ») a son état de départ réellement atteint — compte client sans commande ni adhésion, article fermé `sans_droit` — le seul manque étant un « workflow de vérification email » qui n'existe nulle part dans le projet. Le classer « partiel » est défendable mais discutable. Point mineur, à garder en tête quand Ced lira le tableau.

- **Cible plus restreinte que le brief.** Le brief demande de refuser « un site dont le nom ne commence pas par `imagine-test-` », le staging d'Imagine devant être autorisé « plus tard ». `profils.py:17` n'autorise que `imagine-test-demo` (plus restrictif, donc plus sûr). Conforme à l'esprit ; le chemin staging reste à ouvrir plus tard par consigne.

- **Aucune modification de `docs/`.** A-VOIR liste 12 propositions de précision pour `docs/recette/profils.md` sans toucher le fichier. Conforme au brief (« les profils à corriger selon toi ») et aux droits de l'écrivain.

---

## 2. Exactitude métier

Décisions du paywall déroulées à la main contre `Paywall::rights`/`Moteur` (`wp/plugins/imagine-site/Paywall.php`) et comparées au catalogue.

- **A-GRACE (délai de grâce) — correct.** Fixture `grace` : fenêtre `[now-1j, now+2j]`, abonnement `on-hold`, adhésion `paused` (`c09-seed.php:197-201`). Trace : adhésion `paused` → `suspendu`, puis branche grâce (`Paywall.php:111-120`) : `from<=now<until` vrai → état `grace`, accès **ouvert** avec bandeau. A-VOIR : `delai_grace ; complet ; bloc regularisation`. Conforme.

- **A-SUSP (suspendu) — correct.** Fixture `suspended` : fenêtre `[now-4j, now-1j]`, déjà écoulée. Trace : branche grâce, `now<until` faux → `suspendu`, accès fermé (`Paywall.php:121-123`). A-VOIR : `suspendu ; fermé ; bloc regularisation`. Conforme. La « sortie de la liste d'envoi » du cahier n'est pas modélisée (adaptateur absent) — déclaré.

- **A-EXPIRE (expiré) — correct.** Fixture `expired` : `end = now-1j`, pas de prochain paiement (`c09-seed.php:191`). Trace : adhésion `expired` + abonnement `expired` → `expire`, fermé, bloc `abonnement`. Conforme ; profil justement classé « créé ».

- **À arbitrer — A-VIR : le motif `suspendu` masque le virement non validé.** Fixture `pending` : commande `on-hold`, abonnement `pending`, adhésion `pending` (`c09-seed.php:160,201,220`). Trace : l'adhésion `pending` donne d'abord `virement_non_valide` (`Paywall.php:98`), **puis** le lien d'abonnement `pending` l'écrase en `suspendu` (`Paywall.php:127-128`, `pending` ∉ `[active, pending-cancel]`). Résultat `suspendu`, alors que le cahier décrit « paiement non validé, accès fermé » (virement en attente). Hermès le signale honnêtement (A-VOIR point 4). **Ceci est un comportement de C08, pas un défaut de C09 : C09 le révèle correctement.** Question fermée pour Ced au §Verdict.

- **Cohérence des compteurs.** Les décomptes de A-VOIR correspondent au catalogue : 13 commandes (12 `native` + P-NUMERO `order_only`), 12 abonnements (12 `native`), 14 adhésions (12 `native` + P-SOL-ATT/P-SOL-OK `membership`), 27 comptes (30 − V-ANON/V-ROBOT/V-FAUX). Vérifié à la main contre `c09-profils.json`. Exact.

- **Cas limites couverts par la fixture et les recettes :** dates de clôture/grâce aux bornes (`A-GRACE`/`A-SUSP`, `c09-runtime.php:67-72`), terme à J+30 avec action à J+29 car WCS exige `next_payment < end` (`A-ECHEANCE`, `c09-seed.php:189`), échéance « ce mois-ci » bornée au dernier jour du mois (`A-PAPIER`, `c09-seed.php:192-195`), objet rejoué (reset). Bon.

---

## 3. Tests

- **Tests locaux exécutés par moi : au vert.** `python wp/tests/demo/test_c09_profils.py` → **7/7 OK** (cible exacte, refus avant tout transport, fusion d'identifiants idempotente et sans écrasement de B-00/C-08, refus d'identifiants corrompus, refus d'un chemin d'identifiants dans le dépôt, redirections HTTP hors démo refusées, catalogue de 30 sans faux comptes visiteurs). Ces tests valent une vraie règle (refus de cible, idempotence de la fusion), pas une répétition du code.

- **Suites site non rejouées par moi (doctrine §3).** `natifs 364/364`, `http 192/192`, `securite 5/5`, `reset 4/4`, `regression_c08 30/30`, `integrite 8/8` : lues dans les preuves d'Hermès, non revérifiées faute d'accès au site. À confirmer par le second tour sur le NUC.

- **Couverture correcte des cas limites** (grâce aux deux bornes, terme J+30, échéance de fin de mois, rejeu, altération→reset). La recette d'altération (`c09-reset.py`) prouve que la recette **détecte** un état corrompu avant de restaurer (red avant green) : bonne pratique de non-régression.

- **Important — les tests de motif sont partiellement circulaires (`c09-runtime.php:27`).** `$checks[$key.':motif'] = $decision['motif'] === $row['motif'];` compare la décision au motif **déclaré par Hermès dans le catalogue**, pas au motif attendu par le cahier des charges. Pour A-VIR, le catalogue déclare `suspendu` et le test passe — alors que le cahier suggère « virement non validé ». La divergence n'est donc pas attrapée par un test ; elle n'existe qu'en prose (A-VOIR point 4). Acceptable puisque c'est une question d'arbitrage, mais à savoir : ces assertions vérifient la **stabilité** décision↔catalogue, pas la **justesse** métier.

- **Mineur — preuve HTTP limitée à la page.** `c09-http.py:65-75` ne vérifie le témoin de contenu réservé que sur l'article HTML. Les autres voies (REST, flux, oEmbed, recherche) ne sont pas re-testées ici. C'est acceptable : l'étanchéité multi-voies relève de C-08 ; C-09 n'a besoin que de la décision par profil. À ne pas confondre avec une preuve d'étanchéité complète.

---

## 4. Sécurité et données

- **Aucun secret dans le dépôt.** Mots de passe générés (`secrets.token_urlsafe(24)`, `profils.py:28`), stockés hors dépôt, et `c09-profils.json` n'en contient aucun. `c09-verifier.py:30-50` scanne les fichiers C09 pour toute valeur « password » et refuse le `PRET` en cas de fuite. Bon.

- **Données manifestement fictives.** Noms « Personnage Fictif C09 », adresses `@example.org`, descriptions « aucune personne réelle » (`c09-seed.php:86-90`). Conforme doctrine §3.

- **Garde d'exécution forte et redondante.** Côté Python : cible unique + site démarré + `home_url` exact + état `wp_get_environment_type()=local` (`profils.py:34-43`). Côté PHP : WP-CLI + env local + demo exact + `home_url` exact + refus si dossier `production` + garde hors ligne (mail coupé, HTTP coupé, passerelles vides) avant toute mutation (`c09-seed.php:6-17`). La recette `c09-safety.php` prouve chaque refus (mauvais nom, mauvaise URL avant écriture, mail non coupé, objet non possédé). Très bon.

- **Propriété stricte avant mutation.** Prévol refusant tout compte/commande/abonnement/adhésion non marqué `_imagine_c09_fixture` (`c09-seed.php:24-47`) : le script n'adopte ni n'écrase jamais un objet étranger, et supprime les doublons seulement s'ils sont possédés. Révocation des sessions à chaque passage (`c09-seed.php:96`). Conforme à la rejouabilité sans destruction.

- **Aucun paiement, aucune passerelle, aucun email.** Commandes `pending/on-hold`, 0 €, sans `date_paid` ni `transaction_id` ni méthode (`c09-seed.php:134-161`) ; abonnements manuels sans jeton ; jamais de `payment_complete()`. Conforme doctrine §3 (Stripe/PayPal interdits hors mode test).

- **Échappement/sorties.** Pas de surface d'affichage sur-mesure ici (seed CLI) ; le paywall réutilisé fait l'échappement (`esc_html`, `esc_attr`). RAS.

---

## 5. Doctrine

- **Standard d'abord — respecté.** Objets créés via les API officielles WooCommerce/Subscriptions/Memberships ; `references.md` cite six pages officielles (CRUD, `update_dates()` GMT, structure de stockage Subscriptions, référence Memberships, `wp_insert_user`, `set_role`). Note : l'extracteur officiel étant indisponible, les pages ont été récupérées par HTTP direct — citations plausibles mais non revérifiées par moi. Aucun SQL d'écriture, aucun hook nouveau, aucune bibliothèque close modifiée.

- **Logique métier hors de WordPress — respecté.** Les droits découlent du vrai `Paywall::decision`/`Moteur` (C06/C08) ; C-09 ne duplique aucune table de droits et ne pose aucun méta accordant un droit (`references.md` : les métas C09 ne servent qu'à marquer la propriété).

- **Idempotence/rejouabilité — respecté.** Relance, reset et readback donnent les mêmes ID principaux (`integrite.json`) ; sélection stable par `usort` + suppression des copies possédées (`c09-seed.php:73-78`).

- **Conventions §5 — respecté.** `declare(strict_types=1)`, espace de noms `Imagine\…`, préfixe `imagine_`/`_imagine_c09_fixture`, textes français. Pas de constructeur de pages.

- **Mineur — contrôle mort dans `validate_target` (`profils.py:17`).** `not slug.startswith('imagine-test-') or slug != 'imagine-test-demo'` : la seconde condition rend la première inutile (seul `imagine-test-demo` passe de toute façon). Sans conséquence, mais à nettoyer ou à commenter pour signaler que le préfixe large est volontairement désactivé jusqu'à l'ouverture du staging.

---

## 6. Études — propositions pour `docs/recette/profils.md`

Les 12 propositions d'A-VOIR (section « Profils et documentation à préciser ») sont pertinentes et bien ciblées (distinguer scénarios de requête vs comptes ; preuve de vérification email ; séparer lecture démontrable des paiements/mandats réels ; motif attendu pour un abonnement `pending` ; fenêtre UTC vs durée métier ; port chiffré pour A-ETRANGER ; objets offert/Teams ; « cohérence locale » vs « BCE attestée » pour P-PRO ; dépôt/décision du justificatif ; preuve d'achat P-NUMERO ; rôle administratif dédié pour E-ABO ; calendrier 3 ans et grille 3 tarifs incomplets). Elles relèvent de la doctrine §1 (choix engageant droits/argent → à arbitrer, pas à inventer) : Hermès a eu raison de ne pas trancher.

---

## Verdict : **À corriger**

Le lot fait l'essentiel de ce que demande le brief : script rejouable, objets natifs réels, identifiants prévisibles hors dépôt, garde de cible solide, preuves de décision par profil, partiels/impossible honnêtement listés. Rien de bloquant, aucun secret, aucune donnée réelle, périmètre propre. Les points à corriger sont surtout de la fidélité et des arbitrages.

**Important**
1. `c09-seed.php:174` — le renouvellement manuel forcé sur **tous** les abonnements fait que A-CARTE/A-ECHEANCE (« renouvellement activé ») ne représentent plus leur attribut de départ, qui devient indistinct de A-NONRENOUV. À corriger ou à déclarer explicitement comme non démontrable hors ligne.
2. Fidélité des profils de paiement : A-CARTE/A-SEPA4/A-PAYPAL/A-PAPIER produisent un objet quasi identique (`c09-seed.php:164-199`). Limite inhérente à la démo hors ligne, déclarée, mais à connaître : ces profils ne discriminent pas le moyen de paiement.
3. `c09-runtime.php:27` — les assertions de motif comparent au motif **déclaré** par Hermès, pas au cahier ; elles prouvent la stabilité, pas la justesse (cas A-VIR).

**Mineur**
4. `profils.py:17` — contrôle `startswith` mort (redondant avec l'égalité).
5. Classification « partiel » stricte sur quelques profils sans manque réel (ex. V-INSCRIT).
6. `c09-http.py` — preuve d'étanchéité limitée à la page ; les autres voies relèvent de C-08.

**À arbitrer par Ced (questions fermées, à reporter en fusion)**
- A-VIR : pour un abonnement `pending` (virement en attente), le motif doit-il être `virement_non_valide` plutôt que `suspendu` renvoyé aujourd'hui par C-08 ? (Comportement C-08, révélé par C-09.)
- « Renouvellement activé » des profils abonnés : accepte-t-on qu'il ne soit pas démontrable sur la démo hors ligne (renouvellement manuel), ou faut-il laisser le drapeau de reconduction natif à `true` sans jeton ?
- E-ABO : crée-t-on un rôle administratif dédié (matrice de capacités) au lieu de `shop_manager`, que C-08 ne reconnaît pas comme équipe de lecture et qui porte des capacités éditoriales de trop ?

**Vérifications non faites de mon côté** (à confirmer au second tour sur le NUC, hors de mes droits ici) : les suites site (natifs 364/364, http 192/192, securite, reset, regression_c08, integrite) et la connexion réelle des 27 comptes. Seuls les 7 tests locaux ont été exécutés et sont au vert.

> Ce verdict n'est pas un GO (doctrine §6).

---

*`relectures/C-09/codex.md` n'a pas été ouvert. La fusion (`corrections/C-09.md`) n'est pas faite, conformément à la consigne.*
