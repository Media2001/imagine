# Relecture B-16 — La page article (Claude, relecteur indépendant)

Brief : `briefs/B-16-la-page-article.md`. Cahier des charges : §3.3.
Production relue : `wp/themes/imagine/single.php`, `wp/plugins/imagine-site/PageArticle.php`, `wp/plugins/imagine-site/README.md` (section B-16), preuve dans `production/B-16/`.
Je n'ai pas ouvert `relectures/B-16/codex.md`. Pas de fusion à ce stade.

## Rejeu de la suite

Commande lancée, sans argument : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`
Conteneur jetable, réseau coupé, dépôt monté en lecture seule (`network=none ; rootfs=ro ; mount=…/wp:ro`). Dernière ligne :

```
REJEU : 1213 tests, 36709 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

`PageArticleB16Test` présent dans le journal (`testAppelSeulementCompletSansAbonnement`, `testUneValeurIndetermineeNeDonnePasUnAppelComplet`). Outils : 852 contrôles, 0 échec. Paquets : 13 vérifiés, 0 échec.

## 1. Conformité

- **Ordre de l'en-tête** conforme au brief. `PageArticle::entete()` émet dans l'ordre : titre (`PageArticle.php:81`), résumé (`:84`), mots-clés (`:88`), thématique (`:93`), signature (`:97`), numéro (`:101`) ; le temps de lecture est ajouté juste après dans `single.php:47`. Soit titre → résumé → mots-clés → thématique → signature → numéro → temps de lecture. La preuve navigateur contrôle cet ordre exact (`b16-browser.py:39`).
- **Standard d'abord** présent et justifié (`README.md:21-25`) : résumé = `post_excerpt` natif, mots-clés = `post_tag`, et explication que l'auteur du compte ne vaut pas le journaliste signé, d'où le seul champ ajouté `imagine_signature`. Cinq lignes, conforme à la demande du brief.
- **Résumé public, jamais tiré du texte réservé** : `resume()` lit `get_post_field('post_excerpt', …, 'raw')` (`PageArticle.php:48`) — colonne éditoriale brute, sans `get_the_excerpt()` ni filtre. Rangé dans l'extrait natif, dit dans le README. Champ vide → rien (`:83`).
- **Signature** : nom affiché, sans lien ni page d'auteur (`:97`, `data-b16="signature"` sans `<a>`). Vide → rien (`:96`).
- **Numéro d'origine** : lien vers la page numéro si le numéro existe et est publié (`:99-103`). Article sans numéro : `get_post(0)` → `null` → rien, la page ne casse pas.
- **Fin d'article** : appel seulement si `complet && !abonné` (`appel()` `:51-54`, `fin()` `:109`). Abonné actif : pas d'appel. Non-abonné : `complet=false` → pas d'appel, il ne voit que le bloc paywall de C08 → pas de second appel sous le premier. Lien unique vers `Navigation::abonnementUrl()` (`:112`), même destination que l'entrée « S'abonner » du menu (contrôlé `b16-browser.py:47`).
- **Corps C08 et têtes de page non modifiés** : `single.php` capture une seule sortie `imagine_article_body()` (`:10-12`) et ne touche ni au JSON-LD/descriptions ni au balisage payant. `PageArticle` ne lit jamais `post_content` (commentaire `:9`, prouvé `b16-runtime.php:18-20`).
- **HTML sémantique** : une balise `article` (`single.php:40`), un seul `h1` (`:81`). Preuve navigateur : `h1.count()==1` sur les trois identités et les trois articles (`b16-browser.py:36`).
- **Mode lecture B-03 inchangé** : l'en-tête (`single.php:41`, `data-imagine-distraction`) et l'appel final (`PageArticle.php:114`) portent le marqueur existant B-03, masqués par la règle CSS déjà en place (`assets/reading.css:33`). Aucun asset ni style ajouté. Ce que fait le mode lecture de l'en-tête : il le masque entièrement (titre compris), seul le corps reste. Documenté (`README.md:27`, `A-VOIR.md:9`), prouvé (`b16-browser.py:52`).

**Interprétations signalées (et assumées dans le code) :**
- Numéro affiché *uniquement si publié* (`:100`) — un numéro en brouillon/privé ne donne pas de lien. Le brief ne tranche que « sans numéro ». Choix prudent (pas de lien vers une page non publique), dit au README (`:24`).
- Temps de lecture toujours rendu (`single.php:47`) ; le brief dit « s'il existe déjà ». B-03 existe, donc rendu — cohérent.

## 2. Exactitude métier — cas déroulés à la main

Déroulé sur les trois identités, à partir du harnais `b16-browser.py` et du contrat natif `b16-runtime.php`, recoupé avec le code.

**Cas A — article réservé, anonyme (post 14).** `complet=false` → corps = extrait + bloc paywall (`functions.php`), en-tête complet visible (résumé éditorial, mots-clés, thématique, numéro). `appel()` : `false === true` faux → pas d'appel final. Attendu brief : titre/résumé/thématique/numéro + extrait/paywall, pas d'appel. **Conforme.**

**Cas B — article réservé, `A-PAPIER` (abonné, post 14).** `abonne()` vrai (`b16-runtime.php:25`), `complet=true`. `appel(['complet'=>true], true)` = `true && !true` = faux → texte complet, **pas** d'appel. **Conforme** (abonné actif ne voit pas l'appel).

**Cas C — article réservé, `P-NUMERO` (acheteur, post 14).** `abonne()` faux (`:27`), `complet=true`. `appel(['complet'=>true], false)` = vrai → texte complet **puis** appel vers la page « S'abonner ». **Conforme** (acheteur du numéro = appel).

**Cas limite — valeurs vides (post 82, résumé/signature/numéro absents).** `resume()` = `''` même avec un corps réservé injecté (`b16-runtime.php:18-20`) → aucun `<p data-b16="resume">`. Signature et `imagine_numero_id` supprimés → aucun paragraphe signature/numéro (`b16-browser.py:43`). **Conforme** : vide = aucune trace, page intacte.

**Cas limite — type faible sur `complet`.** `appel()` exige `=== true` (`:53`) : `'true'`, `1`, `null` rejetés (`PageArticleB16Test:22-24`). Un `complet` douteux ne déclenche jamais l'appel. **Conforme**, et le test vérifie bien la règle, pas le code.

**Cas limite — adaptateur C08 indisponible.** `Paywall::decision` renvoie alors `['complet'=>false,…]` (`Paywall.php:104`) → `appel()` faux → pas de fuite d'appel. Cohérent avec « dans le doute, fermé ».

## 3. Tests

- Suite PHP rejouée au vert (voir ligne REJEU). `PageArticleB16Test` exécuté.
- **Couverture PHPUnit pure volontairement mince** : seule `appel()` (la logique pure) est testée en PHPUnit (2 méthodes, table de vérité + stricte-égalité). `resume()`, `entete()`, `sauver()`, `abonne()`, `fin()` dépendent de WordPress : couverts par le contrat natif `b16-runtime.php` (10 contrôles) et par la preuve navigateur (79 contrôles sur 9 réponses). Inhérent à un lot de présentation ; l'ensemble est néanmoins bien vérifié.
- **Preuve navigateur solide** : ordre, un seul `h1`, liens (numéro = 1 `<a>`, thématique > 0, signature = 0), présence/absence de l'appel par identité, destination = lien menu, mode lecture (en-tête + appel masqués, corps visible), JS désactivé (`java_script_enabled=False`) → lisible sans JavaScript. Données et sessions restaurées, `before == after` (`b16-browser.py:66`).
- **Témoin de régression** : `red-V2.json` prouve un échec attendu (`verifier.py:24`).

## 4. Sécurité et données

- **Étanchéité C-26** : les témoins sont absents de l'en-tête et de l'appel final pour chaque identité, et une **mutation témoin** (injection d'un marqueur) est bien détectée (`b16-browser.py:49-50`). Sans extension de la matrice (`A-VOIR.md`, `README.md:29`). Le résumé affiché à l'anonyme sur l'article réservé passe le contrôle d'étanchéité → l'extrait éditorial est propre.
- **Paywall côté serveur** : `PageArticle` ne lit pas `post_content` ; `resume()` lit la colonne brute, jamais un extrait généré du corps. Aucune voie ne laisse sortir le texte réservé par l'en-tête de B-16.
- **Droits / nonce / échappement** : `sauver()` contrôle révision, autosave, `current_user_can('edit_post')`, nonce `imagine_b16` (`PageArticle.php:32-39`). Entrée `sanitize_text_field` + `wp_slash` (`:40-41`). Sorties échappées : `esc_html` (titre, résumé, mots-clés, signature), `esc_url` (numéro), `wp_kses_post` (liste thématiques), `esc_attr` (champ admin). Signature avec antislash relue à l'identique (`b16-runtime.php:34`).
- **Données** : jeux fictifs manifestes (`FICTIF`, `Journaliste FICTIF \ Test`), champs temporaires restaurés et relus. Aucun secret, aucune donnée réelle.

## 5. Doctrine

- **Standard d'abord** respecté : extrait, étiquettes et liens de thématique natifs réutilisés ; seul `imagine_signature` est ajouté, justifié (`README.md:25`).
- **Conventions §5** : `declare(strict_types=1)`, espace de noms `Imagine\`, préfixe `imagine_` (options/métas/nonce), textes passés par les fonctions de traduction. `PageArticle` final, méthodes statiques pures. Conforme.
- **README** présent et décrit le rangement, les réglages (lien `abonnement-en-attente`, dépendance Memberships) et comment lancer les tests.
- **Rejouable / non-régression** : preuve restaure l'état de départ ; rejeu conteneurisé reproductible.

## Verdict

**Conforme** — sous réserve de la validation **visuelle** de Ced (aucun design livré ici, c'est voulu : structure seule). Un verdict de relecture n'est jamais un GO.

Aucun point **bloquant**, aucun **important**.

**Mineurs / à surveiller :**
1. `Navigation::abonnementUrl()` renvoie `''` si la page `abonnement-en-attente` n'est pas publiée (`Navigation.php:72-73`) → l'appel final disparaît même pour un acheteur (`PageArticle.php:113`). Dégradation propre (pas de lien mort), mais l'appel attendu par le brief est alors silencieusement absent. À garder à l'esprit si cette page bouge.
2. Numéro d'origine affiché seulement si le numéro est `publish` (`:100`) ; un numéro dépublié masque le lien sans message. Interprétation prudente, documentée.

### Décisions techniques, défaut proposé
- `PageArticle::abonne()` renvoie `true` pour tout utilisateur connecté quand l'extension Memberships est absente (`PageArticle.php:63-65`) → appel final masqué pour tous dans ce cas. **Catégorie : technique. Défaut proposé : conserver (masquer un rappel d'abonnement est sans risque d'accès ; `abonne()` est de la présentation, n'octroie aucun droit).** Arbitrage a posteriori.

### Pour Imagine
- Rien à trancher côté métier dans ce lot : les règles d'accès viennent de C-08 ; B-16 n'en ajoute aucune.

### À arbitrer par Ced (visuel / réel)
- Validation visuelle de la page article quand les maquettes arriveront (le brief et `A-VOIR.md` renvoient à `browser-final5-V2.png`). Question fermée : la structure et l'ordre des éléments de l'en-tête conviennent-ils tels quels, oui/non ?

---
Fusion non effectuée : `codex.md` existe mais n'a pas été ouvert, conformément à la consigne.
