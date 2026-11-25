# Relecture B-03 — Mode lecture (Claude, relecteur indépendant)

Lot : B-03, « Le mode lecture ». Brief : `briefs/B-03-mode-lecture.md`. Cahier des charges : §3.3 (paragraphe « Mode lecture » et sa note technique), §3.9.
Production relue : `wp/themes/imagine/` (thème), `wp/tests/demo/b03-*`, `production/B-03/`.
Je n'ai pas ouvert `relectures/B-03/codex.md`. Pas de fusion à ce stade.

## Rejeu de la suite PHP autorisée

Commande, sans argument, depuis la racine :

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Conteneur jetable, réseau absent (`network=none`), dépôt monté en lecture seule (`rootfs=ro`, `mount=…/wp:ro`). Dernière ligne du reçu :

> REJEU : 1012 tests, 34006 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS

**Honnêteté sur la portée** : cette commande rejoue l'exécuteur canonique T01 (extension `imagine-site`). Elle **ne contient pas** les assertions propres à B-03 (les 10 contrôles PHP de `imagine_reading_minutes`, les 5 tests JS, l'HTTP, le contrat CSS). Ces derniers vivent dans `wp/tests/demo/b03-*` et sont lancés par `b03-final.py`, qui exige le site fictif, un second exécuteur et des wheels hors ligne — hors de ma commande autorisée et de mon périmètre (pas d'accès site/réseau). Je les ai donc vérifiés **par lecture** du code et du code de test, pas en les exécutant. L'environnement a refusé l'exécution locale de `node --test` ; poids du script mesuré autrement (ci-dessous).

## 1. Conformité

Le lot fait ce que demande le brief, ni moins ni plus. Points vérifiés, chacun rattaché au texte :

- Bouton « Lire l'article » basculant la vue par une classe sur la racine (`html.imagine-reading`) — `single.php:16-18`, `functions.php:39-45`, `assets/reading.css:6`. Conforme §3.3 « une classe sur la racine, plus un script léger ».
- Menu, pied de page et appels périphériques à l'abonnement masqués ; une seule colonne — `reading.css:30-42`. Le **bloc d'abonnement du paywall reste visible** en mode lecture — `reading.css:22` du contrat interdit `display:none` sur `.imagine-paywall-bloc`. Conforme à §3.3 note technique (« elle montre l'extrait puis le bloc d'abonnement »), pas seulement au résumé du brief. Interprétation correctement explicitée dans `A-VOIR.md`.
- Colonne 70ch (plage 65–75 signes) — `tokens.css:23`, `reading.css:44-48`.
- Réglage de taille (Confort/Grand/Très grand, Grand par défaut) et fond (Clair/Sépia/Sombre) — `single.php:22-33`, `reading.css:14-29`.
- Réglages + position mémorisés dans le navigateur, sans compte, rien au serveur — `reading.js:38-55,98-104` ; le contrat interdit `fetch|XMLHttpRequest|sendBeacon|WebSocket` (`test_b03_contract.py:46`). Conforme §3.3.
- Temps de lecture estimé + barre de progression — `single.php:35,53-56`, `inc/reading.php`.
- Paywall inchangé, corps par le point de sortie unique B-01 `imagine_article_body()` appelé **une seule fois** — `single.php:11`, contrat `single.count('imagine_article_body();')==1` + absence de `the_content`/`post_content` dans `single.php` (`test_b03_contract.py:41-44`). Conforme à la contrainte B-01/C-08.
- Sans JavaScript : bouton absent (`#imagine-reading-tools` porte `hidden`, `reading.css:2-4`), article lisible. Conforme.
- Accessibilité : vrai `<button type="button">`, `aria-pressed`, `aria-controls`, labels entrée/sortie, sortie clavier Échap avec retour du focus (`single.php:16-18`, `reading.js:79-80,108-110`). Conforme.
- Poids du script annoncé : **5 756 octets** (confirmé : `wc -c reading.js` = 5756). Aucune bibliothèque. Conforme à « Dis le poids du script ».
- Vitesse fixe à un seul endroit : `IMAGINE_READING_WORDS_PER_MINUTE = 200` dans `inc/reading.php:8`. Conforme à « dis laquelle ».

Aucune interprétation non signalée relevée ; les trois décisions à défaut sont écrites dans `RAPPORT.md` et `A-VOIR.md`.

## 2. Exactitude métier (cas déroulés à la main)

**Cas A — temps de lecture (§3.3).** `imagine_reading_minutes()` retire d'abord l'`<aside data-imagine-bloc>`, remplace les fins de bloc par une espace, décode, compte les mots `[\p{L}\p{N}]+(…)`, puis `max(1, ceil(mots/200))`.
- 0 mot → 1 minute (plancher). ✔
- 200 mots → `ceil(200/200)=1`. ✔
- 201 mots → `ceil(201/200)=2`. ✔
- `<p>mot</p>×201` sans espace → fins de bloc transformées en espaces ⇒ 201 mots ⇒ 2. ✔ (empêche la fusion de mots collés entre paragraphes).
Résultats cohérents avec `b03-runtime.php:11-19`.

**Cas B — non-abonné, article réservé (§3.9 + §3.3).** Branche `!complet` de `imagine_article_body()` (`functions.php:57-66`) : seul l'extrait sort, puis le bloc. Le temps est calculé sur ce seul HTML servi : la longueur du texte interdit ne fuit pas. Le témoin « Les lucioles violettes… » doit être absent de la réponse, du REST, du flux et de la recherche — c'est exactement ce que sonde `b03-http.py:35-67`. Logique correcte **à la lecture** ; non rejouée par moi (voir portée ci-dessus), reçu invoqué par Hermès : `http-release.json`.

**Cas limites.**
- Texte plus court que la fenêtre → progression 100 % quand tout est visible : `progress()` branche `distance ≤ 0` (`reading.js:23-27`). Cohérent avec l'article court de recette.
- Reprise isolée par article **et** longueur du texte servi : clé `…:id:textContent.length` (`reading.js:41`) ⇒ pas de reprise partagée entre texte complet et extrait. ✔
- Stockage refusé / corrompu / quota : défauts prudents, lecture maintenue (`reading.js:11-16,38`), couvert par le test JS.
- Après sortie puis rechargement : `active:false` persiste, le mode ne se rouvre pas, préférences reprises. Cohérent avec `A-VOIR.md` point 6.

## 3. Tests

- Suite PHP autorisée : **PASS** (ligne REJEU ci-dessus), conteneur isolé, réseau absent, dépôt en lecture seule.
- Les tests B-03 testent la **règle**, pas le code : `b03-runtime.php` passe des entrées réelles (unicode, apostrophes, entités HTML, scripts, bloc exclu) et compare des minutes ; `b03-reading.test.cjs` exerce défauts prudents, aller-retour/refus de stockage, bornage de la progression, et un parcours DOM complet (activation, réglages, reprise, Échap). Couverture des cas limites réelle, au-delà du nominal.
- Réserve mineure : `b03-http.py:54` recalcule le temps avec le nombre magique `200` codé en dur plutôt que de lire la constante serveur. C'est un contre-calcul indépendant (sain), mais si la vitesse changeait, ce test ne suivrait pas seul. À noter, non bloquant.

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle : identifiants lus hors dépôt (`~/.imagine-demo/identifiants.json`), témoin manifestement fictif, site `imagine-test-demo` uniquement. Conforme doctrine §3.
- Échappement : `single.php` utilise `esc_html/esc_attr/esc_url` et `wp_kses_post` pour la liste des thématiques. L'`echo $articleBody` brut (`single.php:59`) provient du point de sortie C-08 déjà filtré — acceptable, correctement commenté.
- Paywall côté serveur : le texte réservé n'entre jamais dans la réponse (page, données de page, REST, flux, recherche) — vérifié à la lecture, sondé par le test HTTP. Le calcul du temps ne lit pas le texte interdit pour en révéler la longueur. Conforme doctrine §4 « paywall côté serveur ».

## 5. Doctrine

- Standard d'abord : enqueue conditionnel (`is_singular('post')`) et différé (`strategy=defer`, `in_footer`), sans dépendance ; références officielles consignées (`references-officielles.json`). Le sur-mesure se limite au mode de présentation, comme le demande le cahier.
- Conventions §5 : `declare(strict_types=1)`, namespace `Imagine\Theme`, préfixe `imagine_`, textes d'interface passés par les fonctions de traduction, PHP 8.2. Conforme.
- Rejouabilité / périmètre : aucun fichier de `production/`, `wp/` tiers, file, verrou, fixture ou autre lot touché ; `REJOUER.md` documente le rejeu sans réensemencement.

## 6. Études

Sans objet (lot de code).

## Verdict

**Conforme.** Le lot répond au brief et à §3.3/§3.9, la logique métier et le paywall sont corrects à la lecture, la suite PHP autorisée passe. Ce verdict **n'est pas un GO** (doctrine §6) ; la validation visuelle (valeurs du designer) reste pour Ced, comme signalé par Hermès.

Points classés :

- **Bloquant** : aucun.
- **Important** : aucun. Réserve de méthode, non un défaut : la suite rejouée (T01) ne couvre pas les assertions propres à B-03 ; je les ai vérifiées par lecture, non exécutées, car `b03-final.py` sort de ma commande et de mon périmètre (site/réseau). Un relecteur disposant du site devrait rejouer `b03-final.py` avant clôture.
- **Mineur** :
  1. `b03-http.py:54` — vitesse `200` codée en dur dans le test au lieu de lire la constante serveur ; contre-calcul sain mais couplé à la main.
  2. `reading.css:92-95` — le bloc `@media (prefers-reduced-motion)` ne fait que redéclarer `scroll-behavior: auto` déjà posé ligne 11 ; la vraie garantie « aucun mouvement animé » tient au JS (`behavior:'instant'`, `reading.js:70`). Le bloc est décoratif, pas une protection supplémentaire.
  3. Accessibilité, observation : la valeur de `<progress>` et le `<span>` de pourcentage (aria-hidden) ne sont pas dans une région live ; un lecteur d'écran n'entend pas la progression défiler. Le brief n'exige pas cette annonce (seul l'état du bouton doit l'être, et il l'est) ; probablement un choix volontaire pour éviter le bavardage. Non bloquant.

### Décisions techniques, défaut proposé

Aucune question technique ouverte : rien à appliquer par défaut côté Hermès.

### Pour Imagine

Aucune règle métier à trancher dans ce lot.

### Pour Ced (visuel / réel)

Aucune question nouvelle. Seul point déjà connu : fixer les variables de `production/B-03/besoins-designer.md` et revalider le contraste AA après choix des couleurs. Défaut prudent en attendant : valeurs neutres actuelles, contraste ≥ 4,5:1 testé sur les trois fonds.
