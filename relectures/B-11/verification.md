# Vérification B-11 — 2e et dernier tour (vérificateur)

Date : 2026-11-27. Portée : corrections de `corrections/B-11.md` appliquées par Hermès après la fusion (commit de la fusion `f372ab17`, 11h48). Méthode : `git diff f372ab17..HEAD` sur `wp/` et `production/B-11/`, relance des tests autorisés, lecture du code corrigé. **Pas de relecture complète refaite.** Ce verdict n'est pas un GO.

## 1. Instructions de `corrections/B-11.md`, une par une

### Instructions numérotées

1. **Débloquer l'arbre — stub `apply_filters` dans le banc B-04.** **Appliquée.** `wp/plugins/imagine-site/tests/b04-adapter-fixture.php:40` : `function apply_filters($hook, $value, ...$args): mixed { return $value; }` (commentaire « C28 »). Preuve directe : le rejeu PHPUnit est **vert** (voir §2), `CatalogueTest::testOwnershipDoesNotBecomeAnotherPurchaseBeforeRelease` passe désormais. C'est bien le correctif qui lève le FAIL du 1er tour.

2. **Renouveler la réception sur l'arbre courant, conserver les reçus historiques, pointer le vérificateur et A-VOIR, ne pas remplacer l'empreinte de `imagine-site.php` sans validation, réconcilier NOTE/README.** **Appliquée** — mais déjà **périmée** sur l'arbre courant (voir §3). Preuves : nouvelle réception `production/B-11/reception-politique1330-V2.json` (scellée 13h44) ; `historical_receipts` conserve `reception.json`, `reception-corrections-V2.json`, `recette-finale.json`, etc. ; le vérificateur courant `wp/tests/demo/b11-verifier1330.py` et `b11-verifier.py:76-80` pointent dessus ; `A-VOIR.md:7-9` et `NOTE.md:3` déclarent la réception courante. README : la section B-11 est réconciliée (plus d'affirmation « rejeu général 0 échec » non reproductible).

3. **Durcir la recette de persistance (T2) : valeurs différentes de la préimage, relecture après rechargement, effacement des champs, restauration.** **Appliquée.** `wp/outils/demo/b11-recette.py` : valeurs modifiées distinctes (`:206-207`, contrôle `valeurs_reellement_changees_`), relecture `save_<mode>_readback` (`:213`), effacement `effacement_<mode>_readback` (`:216`), mutation « no-persist » qui doit rougir (`:236-242`), restauration relue (`:343-350`). Réserve : en politique 13h30, l'écriture passe par le vrai hook serveur `save_post` (`:160-166`), pas par l'éditeur navigateur — voir instruction 5.

4. **Borner l'exception Gravatar à l'admin (T4).** **Appliquée.** `wp/outils/demo/b11-recette.py:52-55` (`forbidden_external`) : Gravatar n'est toléré que si `context=='admin'` **et** origine sous `/wp-admin/` **et** `netloc=='secure.gravatar.com'`. Un témoin Gravatar depuis une page publique doit rougir : `:136-139` et `:317-320`, agrégé par `seuls_gravatars_admin_bloques` (`:328`) et `Gravatar_public_temoin` (`b11-verifier1330.py:46`, avec `'/wp-admin/' not in event['origin']`).

5. **Compléter la recette champs/réglages sans substitution (T3) : observateur passif, sans forcer l'éditeur classique ni réduire `allowed_options`, sur l'éditeur et le formulaire réellement livrés.** **Partiellement.**
   - *Fait :* l'observateur est devenu **passif** — `wp/tests/demo/b11-observer.php` ne force plus `use_block_editor_for_post` ni ne restreint `allowed_options` (bloc supprimé, remplacé par « Observateur passif : aucun filtre d'éditeur, de formulaire ou de réglage autorisé »). Le **vrai** formulaire `options.php` est exercé avec ses **16 options**, OFF→ON→OFF, autres réglages conservés à l'identique (`b11-recette.py:142-159`, `b11-verifier1330.py:39-43`). Refus d'hôte/antislash, zéro appel B-11, atteignabilité de la boîte dans l'éditeur blocs livré par lecture du code natif installé (`wp/tests/demo/b11-editor-audit.php`, 11/11).
   - *Non fait, de façon délibérée :* la **persistance par l'éditeur réellement livré n'est pas automatisée**. Une politique ultérieure « A-FAIRE-2 13h30 » (hors `corrections/B-11.md`) a remplacé l'automatisation éditeur par le hook `save_post` sous nonce/capacité et **renvoie le geste de saisie/rechargement UI à Ced** (`A-VOIR.md:1-9`, `NOTE.md:3`, `PRET`). C'est donc une réduction de périmètre par rapport à l'instruction 5, assumée et tracée — à ratifier par Ced.

6. **Tracer l'écart C-28→B-11 dans `docs/ecarts.md` à la clôture.** **Appliquée.** `docs/ecarts.md:142` (fichier partagé changé après scellé, réception complémentaire, historiques conservés), plus `:144` (parcours éditeur non prouvé par automate) et `:145` (URL collée réveillant l'oEmbed, reportée en B-12) et l'entrée « cinq options rendues explicites ».

### Décisions techniques (défaut proposé)

- **Stub `apply_filters`, côté C-28 :** appliqué (instruction 1). Conforme au défaut.
- **Catch trop large de `Paywall` :** **non repris ici, délibérément.** `docs/ecarts.md` le note « repris au gel du code, pas avant ». Hors périmètre B-11 (C-06) — conforme au défaut proposé.
- **T1→T4, défaut « conserver le comportement fermé, compléter par de nouveaux reçus sans affaiblir d'assertions ni altérer les historiques » :** respecté — comportement fermé inchangé, reçus neufs, historiques intacts.

## 2. Résultat des tests

- **PHPUnit hors-ligne** (`wp/tests/rejouer.ps1`, conteneur jetable, réseau `none`, dépôt en lecture seule) : **PASS**.
  > REJEU : 1201 tests, 36613 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
  > OUTILS : 22 outils, 720 contrôles, 0 échecs.
  Le FAIL unique du 1er tour (`CatalogueTest`, régression C-28) est **levé** par le stub `apply_filters`. Les tests propres B-11 (`MediasB11Test`, 4/34) sont dans le vert. (Les paquets `A-31 A31_PARTIAL_EVIDENCE` et `A-32 A32_PACKAGE_DRIFT` restent rouges : connus, hors périmètre, non réparés ni rescellés.)
- **Vérificateur de réception B-11 hors-ligne** (`python wp/tests/demo/b11-verifier.py`) : **ÉCHEC** sur `sources_finales` (`b11-verifier1330.py:26`). `manifest['sources'] != b11.sources()` : la réception scellée à 13h44 ne rejoue plus sur l'arbre courant. Cause unique isolée en §3.
- **Recette runtime/navigateur** (`b11-recette.py`, Playwright + staging) : **non rejouable par le vérificateur** (lecture seule, hors réseau, pas d'accès au staging). Preuves prises dans les reçus `politique1330-*`, sur parole.

## 3. Régression / modification non demandée

- **Contamination par B-12 (même classe que la contamination C-28 du 1er tour).** Un seul fichier source de B-11 a changé depuis le scellé 13h44 : `wp/plugins/imagine-site/imagine-site.php`, au commit **19b3286e (14h58)**, pour enregistrer **B-12** (`IntegrationsCorps`) :
  > `+ require_once __DIR__ . '/IntegrationsCorps.php';`
  > `+ IntegrationsCorps::register();`
  Comme `b11.sources()` inclut ce bootstrap, la réception **politique1330** est de nouveau périmée : le vérificateur hors-ligne est **rouge** (`sources_finales`). **Le code fonctionnel B-11 est intact** : `Medias.php`, `MediasRegles.php`, `AudioNumero.php` ont des empreintes **identiques** à la réception (vérifié hash par hash). Donc aucune régression fonctionnelle, mais la **preuve renouvelée ne rejoue plus**. C'est exactement le motif « fichier partagé modifié après le scellé d'un lot voisin », cette fois B-12 au lieu de C-28. À noter : le verrou oEmbed que B-12 implémente est précisément le suivi demandé pour le risque résiduel B-11 (`ecarts:145`) — travail attendu, mais tombé sur le bootstrap partagé de B-11.
- **Réduction de périmètre assumée (politique A-FAIRE-2 13h30).** Hors `corrections/B-11.md` : l'automatisation de la persistance par l'éditeur livré a été abandonnée au profit du hook `save_post` + renvoi du geste UI à Ced (voir instruction 5). Tracée, mais c'est une décision qui n'était pas dans les corrections.

## 4. Verdict

**Remonte à Ced.**

Le travail de correction est fait et le rejeu PHPUnit est **vert** : les six instructions sont appliquées (la 5 partiellement, par décision délibérée), le blocage C-28 du 1er tour est levé. Mais **B-11 n'est pas clôturable en l'état**, pour deux raisons de fond qui appellent Ced :

1. **La réception renouvelée (instruction 2) est déjà périmée sur l'arbre courant** : B-12 a modifié le bootstrap partagé `imagine-site.php` après le scellé 13h44, le vérificateur de réception hors-ligne est rouge (`sources_finales`). On ne peut pas attester « la réception rejoue sur l'arbre courant ». C'est la **récurrence** du problème structurel déjà remonté au 1er tour (un lot voisin touche un fichier partagé après le scellé) — il faut une décision de Ced : stabiliser l'arbre, renouveler la réception B-11 une dernière fois une fois B-12 posé, ou statuer sur le fait qu'une ligne d'amorçage d'un autre lot n'invalide pas le scellé B-11.
2. **La persistance finale dans l'éditeur réellement livré n'est plus prouvée par automate** (politique 13h30) et revient à un **parcours manuel de Ced** (A-VOIR) — validation touchant au réel/visuel, du ressort de Ced de toute façon.

Rien à réécrire dans le code fonctionnel B-11.
