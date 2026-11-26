# Relecture B-06 — L'espace coopérateurs (Claude, relecteur indépendant)

Date : 2026-11-26. Brief : `briefs/B-06-espace-cooperateurs.md`. Cahier des charges : §3.9, §3.12, §4.2.
Production relue : `wp/plugins/imagine-site/Cooperateurs.php`, `CooperateursRegles.php`, `README-B06.md`, `production/B-06/`, tests `wp/tests/demo/b06-*`.

> Je n'ai pas ouvert `relectures/B-06/codex.md`. Pas de fusion à ce stade.

## Rejeu de la suite PHP

Commande lancée depuis la racine, sans argument (conteneur jetable, sans réseau, dépôt en lecture seule) :

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Dernière ligne du rejeu :

```
REJEU : 1123 tests, 34569 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Ligne outils : `OUTILS : 16 outils, 311 contrôles, 0 échecs ; hors rejeu : aucun`. Isolation confirmée dans la sortie (`network=none`, `rootfs=ro`, montage `wp` en lecture seule, conteneur nettoyé).

**Réserve de méthode.** Cette suite ne contient **aucun test B-06** : les tests du lot (`wp/tests/demo/b06-rules.php`, `b06-space.php`, `b06-runtime.php`) sont hors de la découverte PHPUnit T01 et ne tournent que via la recette Python, qui vise un site HTTP. Je n'ai pas lancé cette recette (accès à un site + commande non autorisée). Ma vérification de B-06 repose donc sur la **lecture du code**, la **lecture des fichiers de test** et les reçus du producteur, pas sur un rejeu reproductible de B-06 dans le bac à sable. Voir point important ci-dessous.

## 1. Conformité

- **Attribut + source + date** (`§4.2`, `§3.9`) : méta `imagine_cooperateur` = `{cooperateur: bool, source: 'administration', date_utc}`. Posé/retiré depuis la fiche native (`show_user_profile`/`edit_user_profile`), nonce lié au titulaire, rôle strict `administrator`, droit natif `edit_user`, verrou MySQL par titulaire, relecture après écriture. Conforme.
- **N'ouvre pas les articles** (`§3.9`, règle du brief) : `Cooperateurs.php` ne touche jamais `Paywall`. `grep` de « cooperateur » dans `Paywall.php` : aucune occurrence. L'attribut est hors de la décision d'accès aux articles. Conforme et vérifié.
- **L'espace et ses quatre sous-pages** (`§3.12`) : `wp/outils/demo/b06-seed.php` crée exactement `Espace coopérateurs` + `Appels à bénévolat`, `Lettre de missions`, `Cadastre des compétences`, `Relais des événements`. Intitulés identiques au cahier des charges, contenu vide, création idempotente (refus d'une page étrangère, relecture divergente = exception). Conforme.
- **Journal daté C10/C17** (brief) : chaque vrai changement écrit un événement append-only avec `quand_utc`, `qui_id`, `qui_login`, `avant`/`apres` ; l'échec du journal restaure le statut (`Cooperateurs::enregistrer`). Conforme.
- **Point d'accroche sans écouteur** : `do_action('imagine_cooperateur_modifie', …)` émis après audit, aucun écouteur, aucun appel CoopHub. Conforme.
- **Export/effacement C21** (brief) : callbacks privacy natifs distincts sous la clé `imagine-cooperateurs`, `C21` inchangé. L'export sort l'attribut et l'historique du titulaire sans identité de tiers ; l'effacement retire l'attribut et anonymise la cible des événements. Conforme.
- **Standard d'abord** : `production/B-06/standard-V2.md` compare usermeta natif et Memberships, écarte le plan d'adhésion (éviterait de confondre l'attribut avec un droit d'article), cite cinq pages officielles avec dates. Exigence du brief remplie.
- **Interprétations signalées** : rôle `administrator` strict plutôt que `manage_options`, affichage de la source dans « Mon compte ». Signalées en `A-VOIR.md`. Pas d'interprétation masquée détectée.

## 2. Exactitude métier — cas déroulés à la main

- **Cas §3.9 (coopérateur non abonné sur un article réservé).** Attendu : extrait public, jamais le corps. Déroulé : `autorise()` ouvre l'espace, mais aucun filtre paywall ne lit l'attribut → l'article reste réduit à l'extrait. Le code et le test `b06-space.php` (contrôle inverse : le coopérateur lit l'espace) ne touchent pas le paywall article. **Résultat conforme.**
- **Cas §3.12 (visiteur non coopérateur sur l'espace).** Attendu : « réservé aux coopérateurs », texte réservé absent des cinq voies. Déroulé sur `CooperateursRegles::lecture` : anonyme → `false` ; abonné `subscriber` → `false` ; état `source=coophub` ou `date_utc` malformée → `false` ; `administrator` → `true` ; coopérateur valide → `true`. Les cinq surfaces (contenu, REST unitaire 403, recherche, flux, sitemap natif) sont neutralisées dans `Cooperateurs.php` et exercées par `b06-space.php` avec témoins positifs puis mutations. **Résultat conforme.**
- **Cas limite « attribut retiré referme l'espace »** : `b06-space.php` supprime la méta puis relit le contenu → le témoin disparaît. Conforme.
- **Cas limite « événement rejoué, pas de doublon »** (idempotence, doctrine §4) : `enregistrer()` retourne tôt si l'état relu est identique → aucun événement journal. Conforme à « une sauvegarde identique ne crée pas d'événement ».
- Les cas limites « dates / clôture / changement d'année » de la grille ne s'appliquent pas : B-06 n'a pas de logique calendaire.

## 3. Tests

- **Rejeu autorisé** : vert (ci-dessus) mais **ne couvre pas B-06**. Voir point important §Doctrine.
- **Couverture B-06 (lue, non rejouée)** : `b06-rules.php` teste la règle pure et ses cas limites (rôles, source, date, `cooperateur=false`) ; `b06-space.php` teste étanchéité des cinq voies, refus de l'édition native pour un éditeur à capacités larges, fiche absente pour non-admin, fermeture après retrait ; via mutations qui rendent les contrôles rouges. Les tests vérifient la règle, ils ne répètent pas le code.
- **Lacune de test** : la neutralisation de la **collection REST** `/wp/v2/pages` (titres listés) n'est pas couverte explicitement ; seul l'unitaire `/wp/v2/pages/{id}` l'est. Voir point mineur.

## 4. Sécurité et données

- Nonce lié au titulaire, `REQUEST_METHOD=POST`, rôle `administrator` strict, `current_user_can('edit_user')`, verrou `GET_LOCK` par titulaire : pose/retrait correctement gardés.
- Sorties échappées (`esc_html`, `esc_url`, `esc_attr`), requêtes préparées (`$wpdb->prepare`, `esc_like`). Objet `WP_Post` cloné avant d'écrire le refus — le cache objet partagé n'est pas empoisonné.
- Étanchéité serveur : le corps réservé n'est jamais dans la réponse d'un visiteur non autorisé (contenu → refus, extrait → vide, REST unitaire → 403, recherche/flux/sitemap → exclusion). Aucun secret ni donnée réelle ; fixtures en `@example.org`.
- Aucune voie trouvée laissant sortir le texte témoin à un anonyme.

## 5. Doctrine

- PHP 8.2, `declare(strict_types=1)`, namespace `Imagine\`, préfixe `imagine_`, textes traduits : conformes. Règle métier isolée en PHP pur (`CooperateursRegles`) testable sans WordPress : conforme à « logique métier hors de WordPress ».
- **Écart doctrine (voir points) :** la règle pure n'est pas branchée sur la suite rejouable (T01) alors qu'elle n'a besoin ni de base ni de WordPress. Le relecteur indépendant ne peut pas reproduire la vérification de B-06 avec la commande autorisée.

## 6. Études — sans objet (lot avec code).

---

## Verdict : À corriger

Le code est soigné et conforme au fond ; aucun point bloquant, aucune fuite de texte réservé trouvée. Les corrections portent sur la reproductibilité des tests et deux détails.

**Important**

1. **La commande autorisée ne vérifie pas B-06.** `wp/tests/rejouer.ps1` (1123 tests) exclut par construction les tests du lot ; ceux-ci ne tournent que via la recette Python visant un site HTTP, non rejouable dans le bac à sable en lecture seule. `CooperateursRegles` est du PHP pur et `b06-rules.php` existe déjà : rien n'empêche de le brancher sur la découverte PHPUnit d'`imagine-site`. En l'état, « tests au vert » pour B-06 repose sur les reçus du producteur, pas sur mon rejeu. *Correction proposée : ajouter un `CooperateursReglesTest` (ou intégrer `b06-rules.php`) à la suite T01, pour qu'un rejeu autorisé couvre au moins la règle pure.*

**Mineur**

2. **`Cooperateurs::compte()` (ligne 390-392).** Après décochage, la méta subsiste avec `cooperateur=false` ; « Mon compte » affiche alors « Coopérateur : non — Source : administration — <date> », alors qu'un compte jamais touché n'affiche pas de source. Incohérence d'affichage et légère sur-information. *Correction proposée : n'afficher « Source … — date » que lorsque `cooperateur===true`.*

3. **Collection REST `/wp/v2/pages` (méthode `rest`, ligne 285).** L'unitaire est en 403 et le corps est neutralisé en refus, mais la collection liste encore la page réservée et son **titre** ; recherche, flux et sitemap, eux, l'excluent entièrement. L'étanchéité du *texte* est respectée (exigence §3.9) ; la *présence* ne l'est pas sur cette voie. *Correction proposée : exclure aussi les pages réservées de la collection REST pour un non-coopérateur, ou confirmer que masquer le texte suffit (question ci-dessous).*

**Observation (non bloquant)**

4. `<time>` sans attribut `datetime` et date UTC brute affichée à l'utilisateur dans la fiche et « Mon compte » : présentation à valider par Ced (non technique).

---

## Décisions techniques, défaut proposé

- **Branchement des tests B-06 sur la suite rejouable** (point 1). Défaut à appliquer sans attendre : intégrer la règle pure à la découverte PHPUnit T01. Claude arbitrera la portée après coup.

## Pour Imagine (questions fermées, défaut prudent appliqué)

Reprises de `A-VOIR.md`, défaut = le plus fermé (conforme à la doctrine « dans le doute sur un droit d'accès, fermé ») :

1. **Garder le seul rôle `Administrateur` pour poser/retirer le statut : oui/non ?** Défaut appliqué : oui (`manage_options` seul ne suffit pas).
2. **Garder `Administrateur` comme seul rôle lisant l'espace sans être coopérateur : oui/non ?** Défaut appliqué : oui (éditeurs/gestionnaires non coopérateurs refusés, y compris via l'édition native).
3. **Étanchéité de la collection REST (point 3) : masquer seulement le texte, ou aussi l'existence des pages réservées ?** Défaut appliqué par le code : texte masqué, pages listées. Proposition : les exclure aussi de la collection, par cohérence avec recherche/flux/sitemap.

---

*Verdict de relecture, pas un GO. Clôture du code par la fusion une fois `codex.md` disponible ; présentation à valider par Ced.*
