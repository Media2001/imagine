# Relecture B-05 — Les partenaires (Claude, relecteur indépendant)

Brief : `briefs/B-05-partenaires.md`. Cahier des charges : §3.12. Production : `production/B-05/`, `wp/`.
Codex non lu à ce stade. Pas de fusion (différée).

## Rejeu de la suite PHP

Commande autorisée, sans argument, lancée depuis la racine :

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Conteneur jetable, réseau `none`, dépôt monté en lecture seule. Dernière ligne :

**REJEU : 1114 tests, 34560 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS**

## 1. Conformité

Le lot fait ce que le brief demande, sans excès visible. Correspondance point par point :

- **Bloc « partenaire du mois », choix manuel, un seul, masqué sans désignation, sans rotation** — `wp/themes/imagine/front-page.php:41` appelle `imagine_partner_month()` (`wp/themes/imagine/inc/partenaires.php:13-25`), qui n'affiche rien si `Partenaires::selection()` est `null`. La désignation est une option native unique `imagine_partenaire_du_mois` (`Partenaires.php:10`), aucune logique de rotation. Conforme au §3.12 et au brief.
- **Page « Nos partenaires » : liste + fiche** — `archive-imagine_partenaire.php` (liste via `imagine_partner_list`) et `single-imagine_partenaire.php` (fiche). Conforme.
- **Étiquette « Partenariat » aux trois endroits, lisible sans couleur, conteneur distinct, classe et non style** — `imagine_partner_label()` émet `<p class="imagine-partnership-label">Partenariat</p>` (texte réel, pas une couleur) ; présente dans le bloc, chaque carte de liste et la fiche. Conteneurs portent `imagine-partnership`, distincte des `<li>` d'articles d'`imagine_list`. Aucun CSS ajouté. Conforme (« pose l'étiquette et une classe, pas un style »).
- **`rel="sponsored"` posé par le gabarit, y compris sur les liens saisis dans le corps de la fiche** — filtre `the_content` `imagine_partner_content` (`functions.php:155-172`) via `WP_HTML_Tag_Processor`, ajouté uniquement aux liens externes du corps partenaire, les relations existantes (`noopener nofollow`) conservées (`array_unique`). Conforme.
- **Un partenaire n'apparaît jamais dans les listes d'articles, la recherche interne, les flux** — CPT `exclude_from_search => true` (`Partenaires.php:45-50`) + `pre_get_posts` `exclureRechercheFlux` (`Partenaires.php:83-98`) qui ferme recherche et flux même quand le type est forcé. Conforme.

**Interprétation signalée (correctement par Hermès, à confirmer).** Le brief dit « tout lien **sortant** vers un partenaire porte la déclaration ». Hermès lit « sortant » = lien vers le **site externe** du partenaire : `sponsored` est posé sur les liens externes du corps de fiche, et défensivement sur les permaliens partenaire dans `imagine_list` (`functions.php:130`) ; les liens **internes** vers la fiche (titre du bloc `inc/partenaires.php:22`, cartes de liste `:38`) ne sont **pas** marqués. C'est l'usage SEO standard et A-VOIR le signale (« liens internes non commerciaux »). L'interprétation inverse (marquer aussi le lien interne vers la fiche, car le « Pourquoi » du brief parle de perception éditoriale par les moteurs) existe mais est moins conforme à l'usage. → voir « Décisions techniques, défaut proposé ».

## 2. Exactitude métier — cas déroulés à la main

Déroulé sur le code (sans accès au site) :

- **Aucune désignation (`get_option` → défaut `0`)** — `selection()` : `is_int(0)` vrai, `preg_match('/^[1-9][0-9]*$/D','0')` échoue → `null` → bloc absent. ✔ (couvert aussi par `bloc_absent_sans_choix` dans `b05-http.py:53`).
- **Désignation d'un partenaire dépublié** — `get_post` renvoie le post mais `post_status !== 'publish'` → `selection()` renvoie `null` → bloc masqué. ✔
- **Valeur invalide soumise au réglage** (`nettoyer('abc')` ou id d'un non-partenaire) — `add_settings_error` + renvoie l'ancien id valide (`:38-39`) ; « sélection conservée ». ✔ Cas limite : si l'ancien choix est lui-même dépublié, `selection()` renvoie `null` → `$old = 0` → retombe sur bloc masqué (dégradation prudente, acceptable).
- **Soumission vide (`null`)** — `nettoyer(null)` renvoie l'ancien id : un formulaire C10 prédécesseur ne peut pas effacer la désignation (`:26-28`). ✔
- **Recherche forcée `?post_type=imagine_partenaire&s=x`** — `exclureRechercheFlux` : `array_diff(['imagine_partenaire'],['imagine_partenaire'])` vide → `post_type=['post']` + `post__in=[0]` → zéro résultat. ✔
- **Flux forcé `?post_type=imagine_partenaire&feed=rss2`** — idem, `post__in=[0]`, flux vide. ✔
- **Flux par défaut (`?feed=rss2`, pas de type)** — `is_feed() && !$types` → `['post']` : seuls les articles, pas de partenaire. ✔
- **Archive partenaires (`/partenaires/`)** — ni `is_search` ni `is_feed` → garde en sortie anticipée, la liste s'affiche. ✔ (`exclude_from_search` ne touche pas les archives.)
- **Lien externe du corps de fiche** (`https://…`, `//example.org/…` protocole-relatif) — `wp_parse_url` renvoie un hôte ≠ hôte du site → `sponsored` ajouté, relations préservées. Lien interne (`/partenaires/`) et ancre (`#suite`) : hôte nul → ignorés. ✔ (correspond au canari `b05-http.py:27`).

Aucun écart détecté entre le code et le §3.12.

## 3. Tests

- **La suite rejouable passe** : 1114/34560, 0 échec (ci-dessus). ✔
- **B-05 n'ajoute aucun test PHPUnit à la suite rejouable.** Aucun test `Partenaire`/`partnership` dans `wp/plugins/imagine-site/tests/`. Toute la preuve de B-05 vit dans des scripts Python/HTTP (`wp/tests/demo/b05-http.py`, `b05-admin.py`, `b05-runtime.php`) qui tournent **contre la démo live `http://192.168.129.32:8085`** avec Playwright et réseau. Ils sont **hors** de la suite T01 et **hors de ma portée** (pas d'accès site ni réseau dans le conteneur de rejeu). Je ne peux donc pas vérifier indépendamment la preuve de B-05 ; je ne l'ai pu que par lecture du code et des reçus.
  - Le brief accepte explicitement une « Preuve. Proportionnée… un test qui relit les pages rendues » : le choix d'une preuve HTTP est donc légitime et bien construit (canari fictif réversible, ancres variées, trafic externe bloqué dans le navigateur). **Mais** la conséquence est qu'aucune règle de B-05 n'est couverte par la suite que je rejoue ; la vérification indépendante repose sur la confiance dans les reçus. La logique de validation d'`id` (`selection`/`nettoyer`, règles de conservation sur valeur invalide/nulle) était la plus simple à couvrir en test, même couplée à WordPress. → **point important pour la vérifiabilité.**
- **Écart de compteur dans les reçus.** `PRET`, `A-VOIR.md:24` et `final.json:11-12` affirment « le canonique demeure 1097 tests / 34443 assertions ». Mon rejeu donne **1114 / 34560** (+17 tests, +117 assertions). B-05 n'ayant ajouté aucun test, l'écart vient de lots postérieurs au `PRET` de 8h24 (l'arbre a avancé). Ce n'est pas un défaut de B-05, mais l'affirmation « demeure 1097 » est **fausse dans l'arbre actuel** : à ne pas prendre pour une régression. → **mineur / contexte.**

## 4. Sécurité et données

- Aucun secret, données fictives uniquement (partenaires B-00, adresses `@example.org` dans le canari). ✔
- Échappement systématique : `esc_html`, `esc_html__`, `esc_attr`, `esc_url`, `selected()` partout (`inc/partenaires.php`, `Partenaires::champ`, gabarits). ✔
- Droits/nonce : le réglage réutilise `options.php`, son nonce et la capacité `manage_options` du formulaire C10 existant ; `register_setting` dans le groupe `imagine_reglages` avec `sanitize_callback` (`Partenaires.php:51-55`). Aucune nouvelle surface d'écriture. ✔ (preuve annoncée dans `final-admin.json`, non rejouable ici.)
- `show_in_rest => true` sur le CPT expose les partenaires en REST : attendu (contenu public, éditeur de blocs), sans rapport avec le paywall. Pas de texte réservé en jeu dans ce lot. ✔

## 5. Doctrine

- **Standard d'abord** : Settings API, `register_setting`, `pre_get_posts`, `exclude_from_search`, `WP_HTML_Tag_Processor` — tout natif, aucune réécriture regex de HTML, aucune dépendance nouvelle. Sources officielles citées dans `A-VOIR.md`. ✔
- **Conventions §5** : `declare(strict_types=1)`, namespace `Imagine\…`, préfixe `imagine_`, textes FR traduits, hooks seulement (pas de modification d'extension tierce). ✔
- **Robustesse — réserve.** L'injection du champ dans le formulaire C10 (`Partenaires.php:58-79`) détecte la position par `strpos($html, '</form>')` **et** `preg_match('/value=[\'\"]imagine_reglages[\'\"]/', $html)`. Couplage fragile au balisage exact de C10 : si C10 change son HTML, le champ **disparaît en silence**, sans erreur ni avertissement — l'administrateur ne peut plus désigner de partenaire sans comprendre pourquoi. Le test `b05-admin.py` couvre l'état courant, mais rien ne détecte une rupture future. → **mineur** (dette de robustesse).
- Note mineure : la branche `sponsored` sur permalien partenaire dans `imagine_list` (`functions.php:130`) est défensive/morte (les partenaires sont exclus de recherche et flux, seuls contextes où `imagine_list` les croiserait). Sans danger ; à garder ou retirer, au choix.
- Note mineure : `archive-imagine_partenaire.php:10` affiche « Les liens vers les partenaires sont déclarés comme liens sponsorisés », alors que les liens de cette page sont des permaliens internes non sponsorisés. Texte trompeur pour le lecteur. → à reformuler.

## 6. Livrables

Code ✔, tests (Python/HTTP) ✔, `production/B-05/A-VOIR.md` ✔ (avec ce qui reste au designer), `PRET` ✔, deux captures (`accueil-partenaire.png`, `fiche-partenaire.png`) ✔, rapport ✔.

## Verdict

**À corriger** — fond conforme, mais vérifiabilité à renforcer.

**Bloquant** — aucun.

**Important**
1. Aucune règle de B-05 n'est couverte par la suite rejouable : la preuve (Python/HTTP contre la démo live) est hors T01 et hors de ma portée. La vérification indépendante repose sur la confiance dans les reçus. Au minimum, couvrir en test automatisé rejouable la validation d'id (`selection`/`nettoyer` : id valide, `0`, dépublié, non-partenaire, valeur invalide conserve l'ancien, `null` conserve) et le filtre `imagine_partner_content` (externe → `sponsored`, protocole-relatif → `sponsored`, interne/ancre → inchangé, relations existantes préservées).

**Mineur**
2. Reçus (`PRET`, `A-VOIR.md:24`, `final.json`) affirment « canonique 1097/34443 » ; le rejeu actuel donne 1114/34560. Écart dû à des lots postérieurs, pas à B-05 — mais l'affirmation est périmée. À noter, pas une régression.
3. Couplage fragile de l'injection du champ C10 (`Partenaires.php:58-79`) : rupture silencieuse si le balisage de C10 change. Prévoir une trace (log/avertissement admin) si l'ancre `</form>` + `imagine_reglages` n'est pas trouvée.
4. `archive-imagine_partenaire.php:10` : texte « déclarés comme liens sponsorisés » trompeur (liens internes non sponsorisés sur cette page). À reformuler.
5. Branche `sponsored` morte/défensive dans `imagine_list` (`functions.php:130`) : sans danger, à documenter ou retirer.

### Décisions techniques, défaut proposé
- **Liens internes vers la fiche partenaire (titre du bloc, cartes de liste) : faut-il aussi `rel="sponsored"` ?** Catégorie : technique (SEO). Défaut proposé (celui d'Hermès, à conserver) : **non** — `sponsored` réservé aux liens vers le site externe du partenaire ; les liens internes de navigation restent ordinaires, conformément à l'usage SEO. Hermès applique ce défaut, je l'arbitre après coup : je le valide, sous réserve d'un avis contraire explicite.

Rappel doctrine : ce verdict, même s'il était « Conforme », **n'est pas un GO**. `relectures/B-05/codex.md` existe mais n'a pas été ouvert ; la fusion (`corrections/B-05.md`) reste à faire et n'est pas demandée pour l'instant.
