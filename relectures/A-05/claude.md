# Relecture A-05 — Le script de nettoyage (Claude, indépendant)

Date : 25 novembre 2026. Relecteur : Claude. Brief : `briefs/A-05-nettoyage.md`.
Périmètre lu : `wp/outils/bascule/nettoyer`, `a05/clean.py`, `a05/database.php`, `a05/native.php`, `a05/bootstrap.php`, `nettoyer.md`, `plan-imagine.exemple.json`, tests `wp/tests/a05/{test_clean,inside,run}.py`, `production/A-05/`. Dépendances A-04/A-03 lues en référence. `codex.md` **non ouvert**.

## Rejeu autorisé (suite PHP)

Commande exécutée depuis la racine, sans argument :

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1
```

Dernière ligne :

```
REJEU : 1012 tests, 34006 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Conteneur jetable, réseau `none`, rootfs en lecture seule, dépôt monté en lecture seule, isolation vérifiée avant/après, conteneur supprimé et absence vérifiée. Cohérent avec `scellement.json` (1012/34006). **Portée** : cette suite T-01 est la non-régression PHP de tout le dépôt ; elle **ne contient pas** les tests propres d'A-05 (16 unitaires + 93 contrôles d'intégration/isolation), qui tournent par `wp/tests/a05/run.py` — runner Python/natif distinct qui écrit dans `production/A-05/preuves/`. Je ne l'ai pas relancé : il écrit dans `production/` (interdit en écriture pour moi) et exige son image Docker. J'ai donc relu ce code de test à la main et recoupé la preuve figée `3f1d3e3ce8f2` (lue, non modifiée). `notes.md` indique honnêtement cette séparation.

## 1. Conformité

Le lot livre exactement l'outil demandé, ni moins ni plus : exécuteur d'un plan versionné (noms seulement), défaut « garder », mode à blanc, reprise/journal, second passage sans effet, et le formulaire d'exemple. Aucune décision de retrait réel n'est prise.

- **Défaut garder** : `plugin_action` (`clean.py:23`) et `selected` (`:53`) renvoient « garder » dès qu'aucune règle ne nomme la ressource, et « garder » l'emporte sur toute suppression recouvrante. Conforme au brief (« Tout ce que le plan ne nomme pas reste en place »).
- **Extensions** : `garder`/`desactiver`/`retirer`, `uninstall` booléen obligatoire, désinstallation seulement si `uninstall:true` **et** `retirer` (`:44`). Un nom de dossier seul n'est accepté qu'avec `garder` (`:44`) — fidèle au diagnostic qui ne donne que des dossiers. `retirer` = désactivation silencieuse native puis suppression des fichiers (`native.php:22`, `clean.py:152`).
- **Tables / options** : `match` exact|préfixe, préfixes littéraux, pas de SQL/joker (`clean.py:46`, `:54`). **Cron** : `exact` seulement, nom = crochet WP-Cron (`:46`), avec vérification dynamique « réellement orphelin » avant toute mutation (`native.php:14`).
- **Uploads** : chemins relatifs de dossiers dans `uploads` canonique, refus racine/fichier/lien symbolique, résolution anti-sortie (`safe_upload :90`).
- **Refus listés par le brief** : dépendance d'une extension gardée (`:66`), WooCommerce/Subscriptions/Memberships + passerelle (`protected_plugin :57`), thème actif (pas d'action de thème ; traversée `../themes/...` rejetée en `A05_NAME`), table du cœur/commerce/extension gardée (`:76`), chemin hors `uploads`. Chaque refus **nomme le fautif** (3ᵉ argument de `need`). Conforme.
- **Préalables A-04** réutilisés sans réécriture : `update.py` importé tel quel (`clean.py:14`) ; sauvegarde récente, maintenance, statut staging, drop-ins refusés, verrou partagé `.imagine-a04-bascule.lock`. GO production **distinct** et spécifique à la tâche `A-05-nettoyage` (`authorize :169`) — un GO historique A-04 n'autorise pas le nettoyage. Conforme au brief et à doctrine §3.
- **Mode à blanc** : SQL en lecture seule (`database.php:77` `START TRANSACTION READ ONLY` + rollback), sans bootstrap WordPress ni code de désinstallation ; sortie = noms, lignes, octets, fichiers ; effets d'une routine tierce explicitement « inconnus ». `a04.maintenance()` est un **contrôle** en lecture seule (`update.py:240`), donc le mode à blanc ne touche rien — prouvé par empreintes avant/après égales (`*-dry-fingerprints.json`, contrôle `dry_database_files_exact`).
- **Formulaire d'exemple** : `plan-imagine.exemple.json` reprend **exactement** le diagnostic de `docs/ecarts.md` (24–25/11) : 22 dossiers d'extensions (ligne 28), tables `ahm_`/`matomo_` (préfixe) + `fsmpt_email_logs` (exact, orthographe non corrigée), 3 dossiers uploads (ligne 31), **tout à `garder`**, `uninstall:false`, options/cron/`table_owners` vides. Interprétations signalées dans `nettoyer.md` et `notes.md` (« Décisions prises à défaut »). Conforme.

Interprétation signalée, non silencieuse : « préfixe ou crochet » lu comme options par préfixe et WP-Cron par crochet (`nettoyer.md`, `clean.py:11` du doc). Acceptable et explicite.

## 2. Exactitude métier (déroulé à la main)

**Cas A — retrait nommé uniquement (banc classique).** Plan : `retirer a05-remove/entry.php` (uninstall:false), supprimer `wp_a05_orphan` + préfixe `wp_a05_stats_`, option préfixe `a05_orphan_`, cron `a05_orphan_hook`, upload `a05-debris`. Déroulé du code : `protect` passe (ownership complet, `a05-keep` possède `wp_a05_kept`) → `operations` produit 8 opérations (désactivation + fichiers + 3 tables + option + cron + upload). J'ai vérifié que le mode à blanc figé (`classic-dry-run.json`) liste **exactement** ces 8 opérations avec lignes/octets (ex. table `wp_a05_orphan` rows=2 ; upload 1 fichier, 14 octets). Après passage réel, l'inventaire (`*:only_named_removed`) montre : `a05-remove` parti, `wp_a05_kept` et `a05-kept` intacts, options/tables/cron non nommés inchangés (`unlisted_*_intact`). **Résultat du code = attendu.** ✔

**Cas B — refus table d'extension gardée.** Plan : supprimer `wp_a05_kept`, déclaré dans `table_owners` comme possédé par `a05-keep` (gardé). Déroulé : `protect :80` boucle `kept` → `name.startswith(f)` vrai → `A05_KEPT_PLUGIN_TABLE:wp_a05_kept`, **avant toute suppression**. Empreintes base/fichiers identiques au témoin (`refusal_kept-table`). Idem pour dépendance (`A05_DEPENDENCY:a05-base/entry.php`), commerce, passerelle, table cœur, sortie uploads, thème. **Résultat = attendu.** ✔

**Cas limites vérifiés :**
- *Second passage / site déjà nettoyé* : ré-inspection → aucune opération → `A05_NOOP` ; `repeat_zero_effect` et `fresh_second_pass_zero_effect` prouvent empreintes identiques. Un checkpoint terminé avec dérive refuse `A05_COMPLETED_DRIFT` sans rien détruire. ✔
- *Arrêt + reprise* : vrai processus tué par SIGKILL (`actual_sigkill` renvoie -9), checkpoint `phase:done` sur l'op 1, reprise qui **ne rejoue pas** l'op déjà « done » (`clean.py:237`) — le `journal.txt` figé le montre (désactivation done → interruption → reprise à partir de `plugin`). Maintenance expirée (20 min fictives) rafraîchie sous les deux verrous seulement si MU intacte et checkpoint lié (`:209`). ✔
- *Crochet non orphelin* : un crochet encore enregistré par du code chargé → `A05_CRON_NOT_ORPHAN` sans mutation (preflight natif en lecture). ✔
- *Routine de désinstallation ambiguë* : `uninstall` « started » sans reçu → reprise refusée `A05_UNINSTALL_AMBIGUOUS` (`:240`), jamais rejouée aveuglément. ✔

## 3. Tests

- Suite PHP globale (T-01) : **verte**, 1012/34006 (voir ligne REJEU). Non-régression du reste du dépôt confirmée.
- Tests propres A-05 : non relancés ici (écriraient dans `production/`, interdit ; runner Docker dédié). Code relu : les unitaires (`test_clean.py`) couvrent vraiment les règles (défaut garder, dossier-garde > fichier, ownership obligatoire, cœur/commerce protégés, passerelle inactive, uploads traversée/symlink, GO spécifique, uninstall explicite) — ils vérifient la règle, pas le code répété. L'intégration (`inside.py`) exerce le vrai natif WordPress classique **et** HPOS, avec `uninstall.php` fictif, SIGKILL réel, empreintes complètes. Couverture des cas limites réelle et proportionnée.
- Preuve figée `3f1d3e3ce8f2` recoupée : `verification-finale.json` (16 unitaires, 93 contrôles, 0 échec ; 29 sources sans dérive ; 31 fichiers A-04 sans dérive), `scellement.json` cohérent. Honnêteté : les deux contrôles « checkpoint de désinstallation » sont déclarés comme compléments de refus fermé, **pas** la preuve d'interruption réelle.

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle : fixtures `a05-*` manifestement fictives, plan d'exemple = slugs publics du diagnostic sans valeurs, aucun préfixe/option/crochet effectif inventé. ✔
- SQL : identifiants validés par liste blanche `\A[A-Za-z0-9_]+\z` (`database.php:10`), requêtes **préparées** pour valeurs, suppression de cron par compare-and-swap binaire (`:133`) avec relecture. Désérialisation d'options bornée `allowed_classes:false` (`:30`). ✔
- Barrière d'écriture pendant la désactivation : seule `UPDATE … active_plugins` est laissée passer, le reste devient `SELECT 0` (`bootstrap.php:16`) — empêche les hooks Woo/Jetpack d'effacer des transients (régression rouge `593433826e29` corrigée). ✔
- Isolation : réseau `none` prouvé (`network_none`, `no_listener`), conteneur exact supprimé. Paywall : hors périmètre (outil de bascule, pas de texte réservé).

## 5. Doctrine

- **Standard d'abord** : opérations natives `deactivate_plugins()`, `uninstall_plugin()`, sémantique `wp_unschedule_hook` réimplémentée en SQL borné pour ne pas lancer cron/hooks ; références officielles citées dans `nettoyer.md`. Le sur-mesure se limite au plan explicite, à l'inventaire à blanc et aux protections. Conforme §4.
- **Rejouable / non-régression** : script versionné, idempotent, A-03 avant/après. Conforme.
- Python (pilotage Docker) + PHP natif dans le conteneur ; pas de logique WordPress hors conteneur. Cohérent avec la famille `wp/outils/bascule/`.

## Observations (non bloquantes)

- **A-03 ne reflète pas le retrait du plugin/cron fictifs.** Le comparateur natif rend `0`, `changes:[]`, `anormal:0` : il n'inventorie pas exhaustivement plugins ordinaires et WP-Cron. Le retrait est prouvé **séparément** par inventaire avant/après. Conforme au brief (« ne requalifie rien… prouve par inventaire ») ; un ancien oracle de banc (`7d5190caa8a9`) qui attendait à tort une anomalie a été corrigé — **A-03 lui-même non modifié**. Traitement honnête, à garder tel quel.
- **Heuristiques de détection** (dépendance via en-tête « Requires Plugins », passerelle via chaîne `WC_Payment_Gateway` / slug) : correctes sur le périmètre connu (seule passerelle = Stripe), mais ne couvrent pas une dépendance non déclarée ou une passerelle sans ces marqueurs. Limitation inhérente au « standard d'abord », documentée. Mineur.
- **Plan nommant une extension non installée** : silencieusement ignorée (`clean.py:149`), visible en mode à blanc. Acceptable ; une mention dans la sortie à blanc (« nommé, absent ») faciliterait la relecture de Ced. Mineur.
- **Barrière de désactivation** sensible à la forme exacte de l'`UPDATE` WordPress (`bootstrap.php:16`) : en cas d'évolution du cœur, elle échoue **fermé** (`A05_DEACTIVATE_READBACK`), jamais en perte de données. Fragilité à surveiller, pas un défaut. Mineur.

## Verdict

**Conforme.** L'outil fait ce que le brief demande, ni moins ni plus ; les garde-fous, le mode à blanc, la reprise et le second passage sans effet sont prouvés ; le formulaire d'exemple est fidèle au diagnostic et entièrement à « garder » ; aucune donnée réelle, aucune décision de retrait réel.

Points classés :
- **Bloquant** : aucun.
- **Important** : aucun.
- **Mineur** : (1) sortie à blanc muette sur un nom planifié mais absent ; (2) fragilité de la barrière d'écriture `active_plugins` face à une évolution du cœur WordPress (échoue fermé) ; (3) heuristiques dépendance/passerelle limitées au périmètre connu (documentées).

## Décisions techniques, défaut proposé

- *Faut-il journaliser dans la sortie à blanc les noms du plan absents du site (ex. « nommé, absent ») ?* Défaut proposé : **oui**, ligne informative sans opération. Technique ; Hermès peut l'appliquer sans attendre, j'arbitre après coup.

## Pour Imagine / À arbitrer par Ced

Aucune question métier ni visuelle. Le lot ne décide aucun retrait réel : le plan rempli, les préalables et le GO écrit restent requis avant toute opération sur le vrai site (hors périmètre de cette relecture).

## Écarts

Rien à ajouter à `docs/ecarts.md` : le diagnostic A-05 y est déjà tracé (24–25/11, « rappel pour A-05 »), et le lot s'y conforme.

---

*Rappel doctrine : ce verdict de relecture n'est pas un GO. `codex.md` n'a pas été ouvert ; la fusion n'est pas faite.*
