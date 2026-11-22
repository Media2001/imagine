# Relecture indépendante — Lot A-01 (publication)

Relecteur : Claude. Date : 22/11/2026. Rapport écrit sans lire `codex.md`.

Briefs appliqués : `briefs/A-01-chemin-court.md`, complété par `briefs/A-01-reprise.md` et surtout `briefs/A-01-publication.md` (étape finale, consigne active n°1 de `A-FAIRE.md`). GO de Ced du 22/11 à 13 h 11 inscrit dans `A-FAIRE.md` : création/arrêt/suppression de sites `imagine-test-…` par l'usage normal de l'outil, activation automatique de la licence Novamira et de l'accès agent comprises.

Livrables relus : `wp/outils/staging-court/{publish.py,publication.py,inside.py,archive.py,run.py,bridge.php,publication_probe.php}`, les scripts natifs réutilisés `wp/outils/staging/*`, les tests `wp/tests/a01-court/*`, `production/A-01/notes.md`, `PRET`, et les reçus de `production/A-01/publication-22nov/`.

## Ce que j'ai vérifié moi-même

- **Intégrité code ↔ preuve.** Les 8 empreintes SHA-256 des sources de la commande calculées sur le dépôt sont **identiques** à `command_sources` du reçu `verification-final.json` et du reçu `3f837c790d4b/result.json`. Le code livré est bien celui qui a produit la preuve.
- **Tests unitaires du sas** : `python wp/tests/a01-court/test_publication.py` → **8/8 OK** chez moi.
- **Revalidation lecture seule du reçu** : `python wp/tests/a01-court/verify_publication.py --report …/3f837c790d4b/result.json` (sans `--live-cleanup`) → **PASS**, `source_payloads_match_current_files: true`, `report_sha256` identique à celui consigné dans `verification-final.json`. Reçu interne cohérent, non altéré.
- **Sécurité des données déposées** : aucun motif de clé (`sk_live`, `pk_live`, `whsec_`, `xkeysib-`, clé privée) dans `production/A-01`. Les seules occurrences `@` dans les reçus sont des noms de fichiers d'assets (`…@2x.gif`), aucun email réel (aucun `.com/.fr/.be/.net/.org/.io`).

Je **n'ai pas** rejoué `publish.py --self-test-publication` : voir limite de vérification ci-dessous.

## 1. Conformité

- **Conforme au brief de publication.** `publish.py` (`main`, l.352-520) enchaîne exactement les 6 étapes de `A-01-publication.md` : création d'un site vide par l'API normale (`api('POST','/api/sites',…)`, l.366), arrêt (`stop_site`, l.378), restauration + 3 scripts natifs hors ligne dans un runner `network=none` séparé (`fresh_runner`/`inside.restore_and_verify`), remplacement base + `wp-content` du site arrêté (`inject`, l.171-280), réécriture `home`/`siteurl` par SQL **sans démarrer WordPress** (l.270-275), démarrage, sonde, puis témoin `verified` ou arrêt. Le chemin ne modifie pas l'outil : `tool_sources_unchanged` prouvé et re-vérifié par empreintes.
- **Chemin court respecté.** Aucun nouveau frontal, aucun proxy réseau ; réutilisation des trois scripts natifs inchangés et du seul parseur SQL pur du worker partagé (`run.py` l.49, chargé en lecture comme `legacy_importer`). Les couches `staging-wp-integration` non nécessaires sont laissées et signalées comme non utilisées (`notes.md`).
- **Limite réseau après vérification = filtrage WordPress seulement.** Écrite telle quelle dans le rapport de la commande (`result.json.post_verified_network_limit`) et dans `notes.md`. Conforme à l'Arbitrage 1 du brief (pas de pare-feu système exigé). Interprétation correctement signalée.
- **Interprétation « vérifié ».** Le dashboard n'a pas de statut natif « vérifié » : Hermès écrit un témoin `/.imagine-staging-verified.json` à la racine du site + statut `verified` dans le rapport, le dashboard restant `running`. Interprétation signalée dans `notes.md`. Le brief acceptait « ou à un rapport ». → **voir « À arbitrer par Ced »** (les lots A-02+ qui « attendent un staging vérifié » devront lire ce témoin, pas le dashboard).

## 2. Exactitude métier

Deux cas déroulés à la main sur le code + reçu :

- **Cas propre (classique/HPOS).** `inside.restore_and_verify` enchaîne `neutraliser → anonymiser → verifier` ; `verified = len(steps)==3 and all(exit==0)`. Le sas `guarded_publish` (`publication.py` l.12-18) n'accepte la publication que si `data_verified is True`, phases dans l'ordre exact, tous `exit==0`, `report.ok is True`, `issues` vide. Puis `inject → start → probe`. Le reçu montre pour les deux stockages : `publication=verified`, HTTP 200 à l'URL exacte, témoin relu, fidélité (abonnements, adhésions, droits, extensions, thème, réglage) **égale** à la fixture. Cohérent.
- **Cas piégé (clé de service).** Le `verifier` natif rend `exit 1` + `issues:['SECRET_OU_IDENTIFIANT']` (voir `lib.php::verifier` l.618-620). `guarded_publish` renvoie `REFUSED_OFFLINE` **avant** tout `inject()`/`start()` ; `publish.py` l.459-470 vérifie en plus : aucune injection, trois conteneurs arrêtés, HTTP injoignable. Conforme à « sinon, laisse le site arrêté ».

- **Cinq points bloquants (brief reprise).** Présents dans le `verifier` natif : email hors `@example.org` sur comptes/commandes → `EMAIL_EXTERNE` (l.629-631) ; clé de service → `SECRET_OU_IDENTIFIANT` (l.618) ; identifiant Stripe/PayPal → `paymentIdentityKey`/`SECRET_OU_IDENTIFIANT` (l.618, 663) ; email non coupé → `EMAIL_NON_COUPE` via sonde (l.701) ; Subscriptions présent hors staging → `SUBSCRIPTIONS_NON_STAGING` (l.704-706). Table inconnue à colonne personnelle non tranchée → `TABLE_PERSONNELLE_A_TRANCHER` (l.596-597). La logique métier est celle qualifiée au lot précédent.
- **Cas limite couvert** : copie encore à l'URL de production refusée **avant écriture** (`Engine::__construct` l.71-78 + `Guard::context`), renouvellement AS forcé bloqué prouvé par sonde (`publication_probe.php` l.66-75 : `callback_calls==0`, renouvellements inchangés, statut `failed`).

## 3. Tests

- **Passent-ils ? Oui, pour la part que je peux rejouer** : 8 tests unitaires du sas + revalidation lecture seule du reçu (ci-dessus). Les tests unitaires vérifient **la règle** du sas, pas une répétition du code : ordre d'appel, refus sur drapeau tronqué (`'true'`), refus sans les trois reçus natifs, arrêt sur échec/exception runtime (`test_publication.py` l.36-100).
- **Suite hors ligne** `run.py --self-test` et la suite E2E native ne sont pas rejouées par moi (Docker, à lancer hors Windows) ; le reçu `tests-21nov/2a5c8c0fcbb1/result.json` (18 contrôles PASS) est référencé.
- **Couverture end-to-end limitée (mineur).** La preuve de publication n'exerce **qu'un** des cinq points bloquants (la clé de service). Les quatre autres et le blocage « table à trancher » ne sont prouvés que dans la suite hors ligne, pas de bout en bout à travers la publication. Comme `guarded_publish` se fonde sur l'agrégat `data_verified`, tout point bloquant refuse la publication ; le risque est faible, mais la preuve bout en bout reste partielle.

## 4. Sécurité et données

- **Secrets.** Mot de passe admin lu par `getpass`, transmis par **stdin** du conteneur (jamais argv), puis `del request['password']` avant toute écriture de reçu (`publish.py` l.386, 425). Salts WordPress générés neufs et non journalisés (l.232-235). Aucun secret de licence/accès agent lu ou réutilisé.
- **Isolation.** Runner hors ligne et helpers : `network=none`, sans port/montage/volume hôte, `cap-drop ALL`, `no-new-privileges`, MariaDB sur socket Unix (`skip-networking` vérifié dans `bridge.php` l.17-19). Contrôlé avant/après dans le reçu.
- **Données réelles.** Aucune. Fixtures `@example.org`, archives fictives. Contrôle de ma part ci-dessus : rien de réel dans les reçus déposés.
- **Novamira.** Après injection : extension absente, 0 enregistrement de mot de passe applicatif, aucune tentative d'authentification (`publication_probe.php` l.29-30, 86-89). Conforme au GO (« ne l'utilise pas »).

## 5. Doctrine

- **Standard d'abord.** Réutilisation de `pre_wp_mail`, API HTTP WP, staging natif WCS, API Action Scheduler ; sources officielles empreintées dans `standard-docs.json`. Le sur-mesure se limite à l'enchaînement. Conforme §4.
- **Conventions §5.** PHP natif : `declare(strict_types=1)`, namespace `Imagine\Staging`, préfixe `imagine_`. Aucune modification d'extension tierce. Conforme.
- **Rejouable / pas d'action manuelle.** Tout passe par la commande ; sites de test supprimés et absence relue (20 relectures). Conforme.

## Limite de vérification (à lire avant le verdict)

La preuve centrale (3 cas réels) **ne peut pas être reproduite par le relecteur** dans les bornes de la doctrine : `publish.py --self-test-publication` crée de vrais sites de staging, déclenche l'activation de la licence Novamira/MCP et utilise des extensions commerciales — ce que mes droits d'exécution interdisent (« les tests du lot, en local ; aucun accès à un site, une base, un compte »). J'ai donc vérifié : l'intégrité code↔preuve par empreintes, la cohérence interne du reçu (revalidation lecture seule), les tests unitaires du sas, et l'absence de données réelles. **Mais les valeurs de sonde du reçu restent auto-déclarées par la commande.** C'est inhérent au lot et assumé par le brief : le premier import réel, lancé par Ced, fera foi et son rapport sera relu. Ce n'est pas un défaut ; c'est le périmètre de ce que la relecture peut attester.

## Verdict

**Conforme** — sous réserve des points ci-dessous. Verdict non-GO (rappel doctrine : une relecture ne vaut jamais GO §3 ; l'import réel Imagine reste à Ced).

**Bloquant** : aucun.

**Important**
1. *Qualification étroite du format.* `archive.py` + canonicalisation SQL de `inside.py` (l.97-137) ne qualifient que le `.wpress` **non compressé, site simple**, grammaire SQL fermée, versions épinglées. Une vraie archive Imagine (AI1WM potentiellement compressée/multi-volume, moteur/SQL hors grammaire) sera **refusée avec rapport**, pas traitée. C'est conforme au brief (« ou un rapport qui dit pourquoi »), mais Ced doit s'attendre à un refus possible au premier essai : la correction serait un nouveau lot de qualification, pas un correctif ici. À porter clairement dans `notes.md` comme attendu, c'est fait.

**Mineur**
2. Preuve bout en bout partielle des cinq points bloquants (voir §3) : seul le secret est exercé via la publication. Suggestion : ajouter au `--self-test-publication` un cas piégé « email externe » et un cas « table personnelle non tranchée » traversant tout le chemin, pour couvrir le sas sur plusieurs motifs.
3. Effet de bord licence : chaque création de site de test active/active-désactive une licence Novamira sur le compte distant de Ced (une dizaine sur la journée), **non auditée** (`notes.md` : « pas de révocation/audit du compte de licence distant »). Dans le périmètre du GO, mais à surveiller côté sièges de licence.
4. `inside.py` l.20 mute en mémoire `CREATE_WORDS` du parseur partagé importé (ajout `ON`/`UPDATE`/`UTF8MB3_GENERAL_CI`). N'altère pas le fichier partagé sur disque (copie en conteneur), et c'est signalé, mais c'est un élargissement de grammaire à garder documenté au cas où le parseur partagé évolue.

## À arbitrer par Ced (questions fermées)

1. Le statut « vérifié » est matérialisé par un **fichier témoin à la racine du site + statut dans le rapport**, le dashboard restant `running`. Les lots suivants (A-02 à A-05) devront lire ce témoin. Est-ce la convention retenue pour « staging vérifié », oui/non ?
2. Accepte-t-on que le premier essai sur l'archive **réelle** d'Imagine puisse être refusé pour cause de format/grammaire/version hors périmètre qualifié, et qu'un tel refus déclenche un lot de qualification dédié plutôt qu'un correctif immédiat, oui/non ?

---

*Étape suivante.* `relectures/A-01/codex.md` existe mais n'a pas été ouvert, et la fusion `corrections/A-01.md` n'est pas écrite, conformément à la consigne reçue (« ne fais pas encore la fusion »). Rapport arrêté ici.
