# Relecture B-07 — L'agenda (Claude, relecteur indépendant)

Date : 26 novembre 2026. Brief : `briefs/B-07-agenda.md`. Cahier des charges : §3.11, §4.2.
Rapport écrit avant toute lecture de `codex.md`. Pas de fusion à ce stade.

## Rejeu de la suite PHP (commande autorisée, sans argument)

Commande exécutée : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`
Conteneur jetable, réseau coupé, dépôt monté en lecture seule (`network=none ; rootfs=ro ; mount=…/wp:ro`). Dernière ligne reportée telle quelle :

```
REJEU : 1128 tests, 35565 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Ligne outils : `OUTILS : 16 outils, 331 contrôles, 0 échecs ; hors rejeu : aucun`.
Un seul avertissement, préexistant et sans rapport avec B-07 : `themes/imagine ; custom package without PHPUnit tests`.

## 1. Conformité

Le lot fait ce que demande le brief, sans billetterie ni paiement. Points vérifiés dans le code :

- **Trois types** (`Agenda.php:11`, `archive-imagine_evenement.php:11-16`) : sortie, rencontre, partenaire. Agenda trié du plus proche au plus lointain, passés séparés (`Agenda.php:66-77`, clé de tri `[$debut, $id]`). Conforme §3.11.
- **Fiche** : inscription simple nom + email + case de consentement décochée et facultative (`Agenda.php:162-164`) pour sortie/rencontre ; partenaire → lien externe, aucun formulaire (`single-imagine_evenement.php:24-29`). Conforme §4.2 et au brief.
- **Lien partenaire** : `rel="sponsored noopener noreferrer"` (`single-imagine_evenement.php:27`). La règle B-05 (`briefs/B-05-partenaires.md:16`) exige `sponsored` sur tout lien sortant partenaire ; présent. Conforme.
- **Balisage** (`Agenda.php:79-86`) : `Event` avec `name`, `startDate` (ISO avec fuseau du site), `location.name` = lieu, `description` = contenu affiché, `url` = permalien. Uniquement des champs affichés, aucun prix/billet/quota. Conforme au « minimum du standard ».
- **Rien ne part** : aucun `wp_mail`, aucun transport sortant ; l'inscription insère seulement un post privé (`Agenda.php:105-110`). Conforme.
- **Pas de billet/paiement/quota/tarif abonné/export des inscrits** : CPT inscription `can_export=false`, `show_in_rest=false` (`Agenda.php:24-32`). Conforme.
- **Doublon** : une adresse + un événement = une seule inscription (`Agenda.php:97-104`, verrou nommé `GET_LOCK` + relecture). Conforme.
- **Non-divulgation** : création et doublon renvoient la même valeur et la même redirection 303 (`Agenda.php:104/118`, `recevoir` 149) ; aucune différence selon compte/inscription existante. Conforme au brief.

Interprétations signalées par Hermès et jugées acceptables : conservation du CPT B-00 sans migration, raccord natif sans installer Event Tickets/Plus ni The Events Calendar (`STANDARD.md`), consentement facultatif (le brief dit « non cochée », pas « obligatoire »). Pas d'interprétation non signalée relevée.

## 2. Exactitude métier (deux cas déroulés à la main)

**Cas A — doublon sur une rencontre ouverte** (`Agenda.php:89-122`).
Premier POST : `ouvert()` vrai → `GET_LOCK` → `inscriptions(email, id)` vide → `wp_insert_post` privé → relecture des métadonnées → `true` → redirection 303 `?inscription=enregistree`.
Second POST identique : `GET_LOCK` → `inscriptions` trouve 1 ligne → `return true` sans insérer → même redirection 303. Résultat : une seule ligne, réponse identique. Conforme. Le reçu `recette-livraison-V2.json` confirme (`doublon_meme_reponse`, `doublon_une_ligne` vrais, contrôles de mutation inverses vrais).

**Cas B — événement passé** (`AgendaRegles.php:9-12`, `single-imagine_evenement.php:22-23`, `Agenda.php:60-64/137-151`).
Affichage : `debut <= time()` → mention « inscriptions closes », formulaire absent (`ouvert()` faux).
POST direct : `recevoir` → `inscrire` → `ouvert()` faux → `false` → `wp_die(400)`. Les deux voies refusent. Conforme au brief (« formulaire absent **et** envoi direct refusé »). Le reçu confirme (`passe_formulaire`/`passe_POST_direct_refuse`/`passe_POST_sans_ligne`).

**Cas limites.**
- Date **égale** à l'heure courante : `inscription()` exige `debut > maintenant` (strict) ; `groupes()` classe `debut > time()` en futurs, sinon passés. Bornes cohérentes entre règle, agenda et fiche. Testé (`AgendaReglesTest.php:15-17`, `debut=100,now=100 → false`). Conforme.
- Partenaire : jamais ouvert à l'inscription (`AgendaRegles.php:11`), POST refusé même sans passer par le gabarit. Conforme.

## 3. Tests

- **Le rejeu autorisé est vert** (1128/35565, cf. ci-dessus). Il couvre la **totalité des règles pures** `AgendaRegles` (`AgendaReglesTest.php`, 2 méthodes : borne d'inscription, clé anti-doublon normalisée).
- **Limite de couverture reproductible, à connaître avant clôture** : dans le conteneur, **seule** `AgendaRegles` est exercée. `Agenda.php`, `AgendaConfidentialite.php` et les deux gabarits n'ont **aucun test PHPUnit** rejouable en bac à sable (cf. avertissement « themes/imagine … without PHPUnit tests »). Toute la logique WordPress — nonce, droits, anti-doublon en base, redirection, JSON-LD, callbacks RGPD — repose sur la recette HTTP (`b07-recette.py`, 83 contrôles) et les runtimes (`b07-runtime.php`, `b07-privacy.php`) qui tournent **contre la démo live `192.168.129.32:8085` et le staging via `docker exec`** — hors du rejeu, et hors de ce que je peux réexécuter (réseau coupé, accès staging interdit au relecteur). J'ai **lu** ces reçus (`recette-livraison-V2.json`, `confidentialite-V2.json`, `adaptateur-livraison-V2.json`) : tous les contrôles y sont verts, avec des contrôles de mutation (témoins inverses) crédibles. Mais ce sont des **reçus pris au mot**, pas une preuve que j'ai rejouée. Classé « important » parce que « 1128 verts » ne doit pas se lire comme couvrant l'adaptateur.
- Qualité des tests purs : ils vérifient la règle (bornes, normalisation de casse/espaces, non-présence de l'adresse dans la clé), pas seulement le code. Bon.

## 4. Sécurité et données

- **Nonces** : réception (`Agenda.php:142`) et sauvegarde admin (`Agenda.php:195-196`) vérifiés. CSRF couvert.
- **Droits** : CPT inscription entièrement cartographié sur `manage_options`, `create_posts=do_not_allow`, boîte admin gardée par `current_user_can('manage_options')` (`Agenda.php:29-31/183`). Réservé à l'administration. Conforme.
- **Requêtes préparées** : `wpdb->prepare` partout (`Agenda.php:98/120/133`). Échappement de sortie systématique (`esc_html`, `esc_url`, `esc_attr`) ; JSON-LD via `wp_json_encode` avec drapeaux `JSON_HEX_*` (`single-imagine_evenement.php:31`).
- **Lien partenaire** : double garde — `esc_url_raw` au stockage avec liste `['http','https']` (`Agenda.php:200`) et regex `^https?://` au rendu (`single-imagine_evenement.php:26`). `javascript:` exclu. Bon.
- **Lecture robuste** : `inscriptions()` renvoie `null` sur erreur SQL, jamais une liste vide ; l'effacement RGPD ne se déclare pas « fait » sur une lecture ratée (`AgendaConfidentialite.php:42-55`). Un défaut de lecture ne devient pas un effacement/export complet. Bon.
- **Données personnelles** : rangées en posts privés `imagine_inscription` + métadonnées `imagine_agenda_*`, liées par `post_parent` ; déclarées à l'export et à l'effacement natifs par filtres additifs clés `imagine-agenda`, sans toucher C-21 (`AgendaConfidentialite.php:10-20`). Conforme au brief.
- **Fixtures** : adresses `@example.org`, titres « … — fictive » (`b07-seed.php:7/16`). Aucun secret, aucune donnée réelle. Conforme §3 doctrine.

Point d'attention (non bloquant) : `admin_post_nopriv_imagine_agenda` laisse un visiteur anonyme créer un post privé par (adresse, événement). Pas d'anti-spam. Le brief demande une « inscription simple » et ne réclame pas de garde ; acceptable pour la démo. Voir « Décisions techniques ».

## 5. Doctrine

- **Standard d'abord** : fait et sourcé. `STANDARD.md` cite les readme officiels SVN (Event Tickets, The Events Calendar) et justifie en dix lignes de ne pas installer les extensions, de conserver le CPT B-00 et de faire un raccord natif minimal. Conforme §4 doctrine et au brief.
- **Logique métier hors WordPress** : `AgendaRegles` est du PHP pur testable sans base ni WP ; `Agenda` est la couche fine WordPress. Conforme §4.
- **Conventions §5** : `declare(strict_types=1)`, espace de noms `Imagine\`, préfixe `imagine_`, textes passés par les fonctions de traduction. Respecté. Réserves mineures ci-dessous.

## 6. Études (volet standard)

Les affirmations de `STANDARD.md` citent des pages officielles (readme SVN) avec adresses et passages, empreintes dans `sources-standard.json`. Pas d'affirmation sans source relevée. Conforme à la grille.

## Verdict

**À corriger** (rien de bloquant ; le code est conforme au brief et le rejeu autorisé est vert). Points classés :

**Bloquant** — aucun.

**Important**
1. **Couverture reproductible limitée à `AgendaRegles`** (`AgendaReglesTest.php`). L'adaptateur, la confidentialité et les gabarits ne sont prouvés que par des reçus live non rejouables dans le bac à sable. Correction proposée : ajouter des tests PHPUnit de l'adaptateur avec des bouchons WordPress (type/date invalides → `evenement()` renvoie `null` ; `inscrire` doublon ; borne `ouvert`), afin que la clôture ne repose pas que sur des reçus externes. À défaut, l'écrire noir sur blanc dans la clôture.

**Mineur**
2. **Événement incomplet invisible sans alerte** (`Agenda.php:49-53`). Si l'heure est vide ou au mauvais format (ex. `HH:MM:SS`), `createFromFormat('!Y-m-d H:i', …)` échoue, `evenement()` renvoie `null`, et l'événement disparaît de l'agenda **et** de sa fiche (ni type, ni date, ni formulaire, ni balisage), sans message en administration. Correction proposée : signaler en administration un événement dont le type/la date/l'heure ne valident pas, plutôt que de le masquer silencieusement.
3. **Partenaire passé** (`single-imagine_evenement.php:22-29`). La branche `debut <= time()` l'emporte sur la branche partenaire : un événement partenaire passé affiche « inscriptions closes » et **masque le lien partenaire**. Incohérent (un partenaire n'a jamais d'inscription) mais sans danger. Correction proposée : pour un partenaire, garder le lien et ne pas afficher la mention d'inscription close.
4. **i18n** (`archive-imagine_evenement.php:14`, `single-imagine_evenement.php:17`). `esc_html__(Agenda::TYPES[$type], 'imagine-site')` traduit une chaîne dynamique : non extractible, et mélange des domaines `imagine` (thème) et `imagine-site` (extension) dans le même gabarit. Correction proposée : passer les libellés de type par des chaînes littérales traduisibles et uniformiser le domaine.
5. **Redondance** (`archive-imagine_evenement.php:14`). Le ternaire `$type === 'partenaire' ? 'Événement partenaire' : Agenda::TYPES[$type]` est inutile : `Agenda::TYPES['partenaire']` vaut déjà « Événement partenaire ». Correction proposée : garder `Agenda::TYPES[$type]`.

## Décisions techniques, défaut proposé (Hermès applique, Claude arbitre après)

- **Anti-spam de l'inscription anonyme** (`Agenda.php:17`). Catégorie technique. Défaut prudent proposé : ne rien ajouter pour la démo (le brief dit « inscription simple », la billetterie viendra avec sa garde) ; si une limite devient nécessaire, un plafond par IP/fenêtre côté serveur, jamais un service tiers.

## Pour Imagine (question métier, défaut proposé)

- Aucune question métier ouverte propre au code. La seule validation restante est **visuelle** (rendu des gabarits sur le squelette B-01) et relève de Ced, comme l'indique `A-VOIR.md`.

---

**Rappel doctrine** : ce verdict n'est pas un GO. `codex.md` existe mais n'a pas été ouvert ; la fusion n'est pas faite, conformément à la consigne.
