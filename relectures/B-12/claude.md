# Relecture B-12 — Aucun appel sortant depuis le corps (Claude, indépendant)

Lot : `briefs/B-12-aucun-appel-sortant-depuis-le-corps.md`. Code : `wp/plugins/imagine-site/IntegrationsCorps.php`, branché dans `imagine-site.php:174-176`. Preuves : `production/B-12/`.

Je n'ai pas lu `codex.md`. Pas de fusion à ce stade.

## Rejeu de la suite (commande autorisée, sans argument)

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Conteneur jetable, sans réseau, dépôt en lecture seule. Dernières lignes :

```
OUTILS : 22 outils, 720 contrôles, 0 échecs ; hors rejeu : aucun
REJEU : 1201 tests, 36613 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Le paquet `imagine-site` est couvert (38 fichiers de test). Le test du lot `IntegrationsCorpsB12Test` est bien dans la suite : **5 tests / 37 assertions**, 0 échec, 0 erreur.

Je n'ai **pas** exécuté la matrice native (`wp/outils/demo/b12.py`, `b12-runtime.php`) : elle crée/supprime de vrais articles dans la base de la démo. Mes droits de relecteur l'interdisent (aucun accès site/base). Je l'ai donc **vérifiée par lecture** ; voir §3.

## 1. Conformité

Le brief est tenu, ni moins ni plus.

- **Verrou inconditionnel, indépendant de B-11.** `IntegrationsCorps` ne lit jamais `Medias::OPTION`. L'adresse externe devient un lien quel que soit le réglage B-11. Conforme à « quel que soit l'état du réglage de B-11 » (brief) et au premier point « aucune intégration externe n'est résolue ». Le cœur du §3.14 (« vidéos externes intégrées… liens vers les podcasts ») et l'exigence RGPD de gestion des cookies/consentement du §4.4 sont l'assise ; B-12 est le verrou tant que l'outil de consentement n'existe pas.
- **Quatre points d'accroche natifs, un par surface** (`IntegrationsCorps.php:13-18`) :
  - affichage / enregistrement : `wp_embed_register_handler` priorité `PHP_INT_MIN` (handler consulté avant les fournisseurs et avant le cache `_oembed_*`) ;
  - résolution directe `wp_oembed_get()` : `pre_oembed_result` ;
  - ancien HTML de bloc : `pre_render_block` (court-circuit avant le `render_callback`) ;
  - aperçu éditeur `/oembed/1.0/proxy` : `rest_dispatch_request` (après permissions, avant le cache transient du proxy, qui appelle `get_data()` et non `get_html()` — d'où l'insuffisance de `pre_oembed_result` seul).
- **Interne délégué, non concerné.** `externe()` renvoie `false` pour une URL du site (même hôte/schéma/port, chemin sous la racine) → handler `false`, résolution/bloc/aperçu inchangés. Constaté : délégation identique (`b12-runtime.php:119-136` compare la réponse native du proxy avec/sans B-12, seul le secret aléatoire natif est normalisé).
- **Rien n'est réécrit en base.** Le code n'agit qu'au rendu/résolution, aucun `wp_update_post` sur le contenu. Les contrôles `corps_*_exact_*` le prouvent.
- **Aucun réglage nouveau.** Confirmé. La levée future est en trois lignes dans `NOTE.md` (« Quand le consentement existera »), sans utiliser le réglage B-11 comme preuve de consentement.
- **Livrables présents** : code, test, cinq lignes dans le `README.md` de l'extension (section « B-12 », 5 lignes), `production/B-12/A-VOIR.md`, `PRET`, rapport court (`NOTE.md`).

Aucune interprétation implicite non signalée. La portée (intégrations natives uniquement, pas un assainisseur d'iframes collés à la main) est écrite dans le brief et répétée dans `NOTE.md`/`A-VOIR.md`.

## 2. Exactitude métier — cas déroulés à la main

Entrée fictive : hôte site `demo.example.invalid/magazine`, URL externe `https://www.youtube.com/watch?v=B12FICTIF01`.

**Cas A — adresse seule sur une ligne.**
- Affichage (`the_content` → autoembed → `WP_Embed::shortcode`) : le handler catch-all (`~^(?:https?:)?//~i`) matche, `lien()` → `externe()=true` → `html()` = `<a href="…échappé…">…</a>`. Le handler ayant répondu, le pipeline oEmbed n'est pas atteint : pas d'appel distant, pas d'iframe. **Lien ordinaire. Conforme.**
- Enregistrement (`cache_oembed` via l'AJAX natif) : passe par `run_shortcode`/`autoembed` → même handler → aucun `_oembed_*` distant écrit. **Aucune sortie. Conforme.**
- Aperçu (`/oembed/1.0/proxy`) : permission `edit_posts` native validée en amont, puis `apercu()` → route reconnue, URL externe → `WP_REST_Response` de type `link`. Le callback distant n'est jamais appelé. **Lien, pas de vignette. Conforme.**

**Cas B — bloc natif `core/embed`.** `pre_render_block` → `bloc()` : `blockName === 'core/embed'`, URL externe → `<p><a …></p>`, le `render_callback` (donc l'ancien iframe mémorisé) est court-circuité. **Pas de cadre/script/vignette. Conforme.** Vérifié aussi contre un bloc portant un ancien `<iframe>/<script>/<img>` (`b12-runtime.php:107-108`).

**Cas limites vérifiés (code + matrice native lue) :**
- **Réglage B-11 OFF puis ON** : `matrix_*_0_*` et `matrix_*_1_*` identiques, lien dans les deux cas. Conforme au brief.
- **Détournement d'authentification** `https://demo.example.invalid@evil.invalid/…` : `isset($target['user'])` → `externe()=true` → bloqué (rendu lien). Testé.
- **Préfixe voisin** `…/magazine-other/a` : non classé interne (`str_starts_with('/magazine-other/a','/magazine/')` faux) → externe. Testé.
- **Sous-domaine piège** `demo.example.invalid.evil.invalid` : hôte ≠ → externe. Testé.
- **Caches périmés** (meta `_oembed_*`, HTML de bloc, transient du proxy) : ne ressortent pas (`b12-runtime.php:100-115`).
- **Mutation témoin** (verrou retiré) : sur save/render/preview une tentative sortante est observée puis arrêtée par B-00 `imagine_demo_offline` **avant transport** (`transport===0`) ; verrou remis → zéro tentative. Le contrôle prouve d'abord qu'il peut échouer. Conforme à la « Preuve » du brief.
- **Permissions du proxy** conservées : requête anonyme → 401/403 (`b12-runtime.php:139-142`).

Aucun écart constaté entre le code et le résultat attendu sur ces cas.

## 3. Tests

- **Suite complète verte** : voir la ligne REJEU ci-dessus. Le test du lot y est inclus et passe.
- **PHPUnit du lot** (`tests/IntegrationsCorpsB12Test.php`) : vérifie l'échappement (`&amp;`, pas de `<iframe|script|img>`), le court-circuit du bloc, l'ordre des accroches (handler `PHP_INT_MIN`, filtres `PHP_INT_MAX`) et la non-violation des permissions/autres routes. Les tests vérifient bien la règle, ils ne se contentent pas de répéter le code.
- **Limite de ces tests** : ils tournent sur des doublures maison (`IntegrationsCorpsB12Stubs.php`), pas sur le vrai WordPress. Ils ne couvrent donc pas le comportement réel du pipeline (vrai `esc_url`, ordre réel du dispatch REST, vrai `cache_oembed`). La garantie « zéro sortie » repose sur la **matrice native** `b12-runtime.php`, exécutée hors de ma portée. Je l'ai relue : elle exerce save/render/preview pour URL seule et bloc, shortcode et résolution directe, caches périmés, OFF/ON, délégation interne et mutation B-00, avec un observateur réel sur `pre_http_request`/`http_api_debug`. Le dispositif est cohérent et couvre les cas limites, pas seulement le nominal.

## 4. Sécurité et données

- **Échappement des sorties** : `html()` passe par `esc_url($url, ['http','https'])` + `esc_html($url)`. Une URL sans schéma http/https (ex. `javascript:`) donne un `href` vide, le texte reste échappé : pas d'injection. Le handler ne matche de toute façon que `http(s)://` ou `//`.
- **Permissions** : l'aperçu ne contourne jamais la permission native (`rest_dispatch_request` s'exécute après le contrôle `edit_posts` du cœur ; `apercu()` re-vérifie `current_user_can('edit_posts')` et rend `$response` inchangé sinon). Pas d'élargissement de droit.
- **Pas de sous-blocage dangereux** : `externe()` ne classe « interne » que sur égalité stricte d'hôte (+ schéma/port/chemin). Aucune URL d'un hôte tiers ne peut être prise pour interne. Le biais du code est vers « externe » (donc lien), c'est-à-dire le côté sûr pour ce lot.
- **Données** : aucun secret, aucune donnée réelle ; fixtures fictives (`demo.example.invalid`, `*.example.invalid`), URL d'essai `B12FICTIF01`. Articles d'essai supprimés et état restauré (annoncé et vérifié par la matrice native).
- **Paywall** : non touché (confirmé par le brief et le rejeu vert des paquets C-08 et voisins). B-12 n'ouvre aucune voie de sortie du texte réservé.

## 5. Doctrine

- **Standard d'abord** : le lot n'ajoute aucune mécanique propriétaire ; il se branche sur des points d'accroche natifs documentés (`wp_embed_register_handler`, `pre_oembed_result`, `pre_render_block`, `rest_dispatch_request`). Sources officielles listées dans `production/B-12/sources-officielles-V2.json`. Conforme au §4 de la doctrine.
- **Conventions §5** : `declare(strict_types=1)`, espace de noms `Imagine\Site`, préfixe `imagine_` pour le handler (`imagine_corps_externe`), aucune extension tierce modifiée (hooks seulement), README présent. Conforme.
- **Non-régression** : mutation témoin + matrice avant/après, corps relu identique, voisins B-11/C-28 contrôlés par complément (`reception-complement-voisins-V2`). Démarche conforme.

## 6. Études

Sans objet (lot avec code).

## Verdict

**Conforme** — sous réserve que ce verdict n'est **jamais un GO** (doctrine §6) : il ne vaut que pour la clôture d'un lot de code, pas pour une validation visuelle, une mise en ligne ni un accord sur le réel.

Aucun point **bloquant**. Aucun point **important**. Points **mineurs** :

1. **Dépendance à l'ordre interne du cœur WordPress.** Le dispositif suppose : handlers consultés avant les fournisseurs ; `rest_dispatch_request` après les permissions et avant le cache transient du proxy. Vrai en WP 7.0.9, mais non garanti par contrat public. `IntegrationsCorps.php:16-18` et `NOTE.md` le reconnaissent. *Correction proposée* : au moindre changement de version du cœur, re-jouer la matrice native avant clôture, et le noter comme condition de non-régression du lot.
2. **Tests PHPUnit sur doublures, non sur le vrai WP.** La preuve de « zéro sortie » n'est pas dans la suite scellée (`rejouer.ps1`), elle est dans la matrice native hors conteneur. *Correction proposée* : le dire explicitement dans le README du lot (actuellement le README renvoie à `A-VOIR.md` ; ajouter que la suite scellée ne prouve pas le comportement pipeline réel).
3. **Compteurs du worker légèrement périmés.** `NOTE.md`/`A-VOIR.md` annoncent « 1 200 tests / 36 610 assertions » ; le rejeu observé donne **1 201 / 36 613**. Les deux verts. *Correction proposée* : aligner les chiffres pour la traçabilité.

Observation (pas un défaut) : la portée exclut les `<iframe>` collés à la main dans le corps — conforme au brief, qui l'exclut explicitement. La garantie combinée B-11 + B-12 continue donc de supposer qu'aucun lecteur tiers n'est inséré en HTML brut ; c'est bien dit dans `A-VOIR.md`.

### Décisions techniques, défaut proposé

- **Faut-il intégrer la matrice native à la suite scellée `rejouer.ps1` ?** Elle exige un vrai WordPress + base, que le conteneur scellé (sans réseau, dépôt en lecture seule) ne peut héberger. *Défaut proposé* : **non** — la laisser en preuve native documentée, rejouée manuellement à chaque montée de version du cœur (cf. mineur 1). Hermès applique ce défaut sans attendre ; j'arbitre après coup.

### Pour Ced (visuel / réel)

Rien à arbitrer dans ce lot. Le résultat visible (un lien à la place d'un lecteur) est décrit dans `A-VOIR.md` ; à constater sur `imagine-test-demo` si souhaité, sans que cela conditionne la clôture code.

---

`codex.md` existe mais n'a pas été ouvert. Fusion non faite, conformément à la consigne.
