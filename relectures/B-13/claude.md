# Relecture B-13 — menu principal et menu étendu (Claude)

Lot : B-13. Brief : `briefs/B-13-menu-principal-et-menu-etendu.md`. Cahier des charges : §3.1.
Code relu : `wp/plugins/imagine-site/Navigation.php`, son enregistrement dans `imagine-site.php`, les tests `NavigationB13Test.php`, `wp/tests/demo/b13-runtime.php`, `b13-observer.php`, `wp/outils/demo/b13.py`, `b13-browser.py`, `b13-seed.php`, la section README et la réception `production/B-13/`.

## Rejeu de la suite

Commande autorisée, sans argument, rejouée telle quelle :

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Dernières lignes :

```
OUTILS : 23 outils, 852 contrôles, 0 échecs ; hors rejeu : aucun
REJEU : 1208 tests, 36685 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Conteneur jetable, isolé : `network=none`, `rootfs=ro`, dépôt monté en lecture seule, `cap-drop=ALL`. Le test `NavigationB13Test` est bien présent et au vert dans le rejeu (1 cas).

Réserve : le rejeu scellé s'appuie sur des doublures. La preuve du pipeline natif et du zéro appel sortant vient des scripts `b13-runtime.php` (19 contrôles, transaction annulée) et `b13-browser.py` (45 contrôles, vrai navigateur sans JS). Ces deux-là exigent le WordPress fictif vivant et Playwright : hors de mes droits de relecteur, je ne les ai pas rejoués. Je les ai relus ligne à ligne et j'ai contrôlé les JSON enregistrés (`native-final-V2.json`, `browser-final-V2.json`) via la réception `verifier.py`.

## 1. Conformité

- Menu principal, huit entrées dans l'ordre du §3.1 : `b13-runtime.php:20` compare `array_column($top,'title')` à la liste exacte ; `b13-browser.py:105` la revérifie dans le vrai rendu. Pas d'« Espace digital ». Conforme.
- Menu réutilisé sans recréation ni doublon : `b13-seed.php:9-11` exige le menu B-08 existant et ne le recrée pas ; `b13-runtime.php:23` vérifie que les ID sont ceux de B-08. Conforme.
- « S'abonner » → page d'attente déclarée telle : `Navigation::abonnementUrl()` et `b13-seed.php:22-31` créent `/abonnement-en-attente/`, statut `publish`, contenu explicitement fictif, sans paiement. Conforme.
- « Connexion » pour un lecteur connecté : le choix retenu est documenté (README `:615`, A-VOIR `:9`) — l'entrée reste « Connexion » et pointe vers la page « Mon compte » WooCommerce (`b08-seed.php:74`), comportement natif de B-01/B-08. Le brief demande « garde ce que B-01 fait, et écris-le » : fait. Voir point visuel plus bas.
- Menu étendu sous « Thématiques » : `Navigation::thematiques()` liste chaque thématique puis, pour chacune, une sélection titre + image à la une + lien, sans extrait ni corps (`Navigation.php:106-124`). Les plus récents par défaut (`orderby date DESC`), nombre = réglage (défaut 3). Conforme.
- Nombre d'articles = réglage borné : `Navigation::nombre()` défaut 3, borné 1–10 ; page d'options sous Réglages → Menu principal. Conforme. Le choix manuel des articles est bien laissé en question pour Imagine, non construit (A-VOIR `:23`). Conforme à la consigne.
- Structure seule : listes `<ul>/<li>` imbriquées, aucun style ni script ajouté, lisible sans JavaScript (tests navigateur en `java_script_enabled=False`). Conforme.
- Thématique sans article : conservée, sans sélection — `Navigation.php:118` n'ajoute le `<ul>` que si `$posts` ; vérifié `b13-runtime.php:45`. Conforme.
- Renouvellement du cache : un transient `imagine_b13_thematiques` reconstruit sur `save_post`, `deleted_post`, `set_object_terms`, `created_term`, `edited_term`, `delete_term`, les métas, et le changement de réglage (`Navigation.php:16-23`). Le brief demande « publication, dépublication, changement de thématique » : couvert et au-delà. Dit dans le README `:613`. Conforme.

Aucune interprétation non signalée relevée. L'ordre des thématiques (alphabétique, `orderby name`) n'est pas fixé par le cahier des charges ; choix prudent, sans incidence, mentionné ici pour mémoire.

## 2. Exactitude métier (déroulé à la main)

Cas A — anonyme sur l'accueil (§3.1). Attendu : huit entrées une seule fois, menu étendu avec les trois thématiques de la démonstration, chacune jusqu'à 3 articles récents (titre/image/lien). Lecture du code : `thematiques()` parcourt les termes `hide_empty=false`, `get_posts` limité à `self::nombre(...)=3`, sortie = titre + miniature + permalien. Résultat conforme ; confirmé par `browser-final-V2.json` (surface `anonyme`/`/`).

Cas B — anonyme sur un article réservé (étanchéité, témoins C-26). Attendu : le titre attendu présent, puis absence des corps/extraits réservés. La fixture crée des corps `CONTENU_FICTIF_RESERVE_B13_*` et des extraits `EXTRAIT_B13_INTERDIT_DANS_MENU_*` (`b13-seed.php:43-44`). Le code n'émet que titre/image/lien, jamais extrait ni corps. Le contrôle `b13-browser.py:109` trouve d'abord le titre, puis vérifie `c26.c23.assess(...)` et l'absence de `EXTRAIT_B13_INTERDIT_DANS_MENU_`. La contre-épreuve `:110` injecte un témoin et exige que le contrôle échoue : il prouve donc qu'il sait détecter. Étanchéité conforme, matrice C-26 non étendue comme demandé.

Cas limites déroulés :
- Dépublication : `b13-runtime.php:38-40` passe l'article en `draft`, vérifie que le transient est invalidé puis que l'article disparaît ; `:41-42` le republie et le réintègre. Conforme.
- Thématique créée vide : `:43-45` — reste listée sans sélection. Conforme.
- Retrait de la thématique d'un article : `:47-49` — l'article quitte la sélection après invalidation. Conforme.
- Réglage ramené à 1 : `:50-53` — invalidation puis nombre appliqué. Conforme.
- Réglage hors bornes / non numérique : `Navigation::nombre('bad')=3`, `nombre(0)=1`, `nombre(99)=10` (`:54`, et test PHPUnit). Conforme.

## 3. Tests

- Au vert : REJEU PASS (voir en-tête), 19 contrôles natifs transactionnels, 45 contrôles navigateur, 1 PHPUnit.
- Cas limites couverts (dépublication, thématique vide, désaffectation, bornes du réglage, cache) — au-delà du cas nominal.
- Les tests vérifient bien la règle et pas le code : le contrôle d'étanchéité porte une mutation témoin qui doit faire échouer l'assertion (`b13-browser.py:110`) ; le rejeu négatif `red-V2.json` prouve l'échec attendu quand la classe est absente.
- Restauration éprouvée : essais natifs dans une transaction annulée (`b13.py:34`), sessions A-PAPIER restaurées et sonde retirée (`b13-browser.py:85-88`), aucun menu ni profil laissé altéré.

Point mineur : le test PHPUnit scellé `NavigationB13Test` ne couvre que `nombre()`. L'essentiel de la preuve est porté par les scripts runtime et navigateur, qui ne tournent pas dans le rejeu scellé. C'est cohérent avec la nature WordPress de `thematiques()` (non testable hors WP), mais la seule brique rejouée hors-ligne reste étroite. Sans gravité : la couverture réelle existe et est vérifiée par la réception.

## 4. Sécurité et données

- Échappement systématique : `esc_url`, `esc_html`, `esc_attr` sur toutes les sorties du menu étendu (`Navigation.php:106-123`). Page de réglage échappée.
- Droits : `page()` exige `manage_options` et `wp_die` 403 sinon (`:56-58`) ; `settings_fields('imagine_navigation')` pose le nonce de `options.php` ; `register_setting` borne l'entrée via `nombre()` (`:47-51`).
- Paywall : seuls titre, image et lien sortent ; aucun extrait ni corps. Aucune voie de fuite repérée (page menu, transient public identique pour tous). Le filtre `post_password => ''` exclut en plus un article protégé par mot de passe. Conforme à « Rien de réservé ».
- Données : fixtures manifestement fictives (`@example.org`, titres « fictive », `example.invalid`), sonde `b13-observer.php` gardée hors production et conditionnée au site démo, retirée après usage. Aucune donnée de visiteur collectée ni exportée. Conforme à la doctrine §3.

## 5. Doctrine

- Le standard d'abord : menus natifs conservés, enrichissement par le filtre natif `walker_nav_menu_start_el`, cache par Transients natifs — pas de réimplémentation. Cinq lignes « standard » présentes et sourcées (README `:608-613`, liens developer.wordpress.org). Conforme.
- Conventions §5 : `declare(strict_types=1)`, espace de noms `Imagine\Site`, préfixe `imagine_` (option, transient, hooks), textes passés par `__()`/`esc_html__()`. Conforme.
- Logique testable, cache côté serveur, aucune modification d'extension tierce (uniquement un filtre). Conforme.

## 6. Études

Sans objet (lot de code).

## Points classés

Bloquant : aucun.

Important : aucun.

Mineur :
1. `Navigation.php:16` — `save_post` invalide le cache pour toute écriture (révisions, enregistrements automatiques), pas seulement les publications. Sans danger (le fragment se reconstruit), mais sur-invalidation. À laisser tel quel, ou filtrer sur le type de post ; sans urgence.
2. `Navigation.php:83-84` — l'injection du menu étendu dépend de la classe `imagine-nav-thematiques` portée par l'entrée B-08. Si un administrateur édite le menu et retire la classe, le menu étendu disparaît en silence. Fragilité héritée de B-08, non introduite ici ; à noter.
3. Couverture PHPUnit scellée étroite (voir §3). Acceptable, mentionné pour traçabilité.

## Décisions techniques, défaut proposé

- Ordre des thématiques dans le menu étendu : le code applique l'ordre alphabétique (`orderby name`). Le cahier des charges ne le fixe pas. Défaut proposé : garder l'alphabétique. Hermès applique sans attendre ; arbitrage a posteriori.

## À arbitrer par Ced (visuel / touchant au réel)

- Libellé « Connexion » pour un lecteur déjà connecté : l'entrée garde le mot « Connexion » (comportement B-01/natif retenu et écrit). C'est visible par l'utilisateur. Faut-il garder « Connexion » même connecté, ou afficher « Mon compte » ? Défaut prudent proposé : garder « Connexion » (ce que fait B-01), inchangé tant que la maquette ne tranche pas.
- Forme du menu étendu (panneau latéral ou grand déroulant) : non livrée, arbitrée sur maquette (§3.1). La « grande hauteur » actuelle est volontairement non maquettée (A-VOIR `:9`). Rien à corriger ; validation visuelle attendue.

## Verdict

**Conforme** — sous réserve de la validation visuelle (libellé « Connexion », forme du menu) qui revient à Ced, et des trois points mineurs ci-dessus, non bloquants. Ce verdict n'est pas un GO.

---

Note de procédure : `relectures/B-13/codex.md` existe déjà, mais, conformément à la consigne reçue, je ne l'ai pas ouvert et je n'ai pas écrit la fusion. Étape fusion à faire dans un second temps.
