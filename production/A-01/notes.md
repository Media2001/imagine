# A-01 — corrections fusionnées du 22 novembre : vérifiées, NON PRÊT global

**Le PRET précédent est invalidé et retiré**, conservé uniquement sous `PRET-invalide-22nov-historique.txt`. Les sections antérieures ci-dessous sont historiques. **R5 reste bloqué sur le choix Ced « admin / scripts »** ; aucun nouveau PRET. Aucun import réel, archive Imagine, ancienne copie, accès agent, Git, installation hôte ou modification de l'outil/modèles partagés.

## Résultat courant, dans l'ordre de la fusion

- **R4 — corrigé en premier.** Sur refus/échec, arrêt du site et relecture des trois conteneurs **avant** suppression des helpers/runner. Chaque erreur de nettoyage est conservée séparément dans `cleanup_errors` sans masquer l'erreur primaire ; les autres nettoyages sont tout de même tentés. Test réel : site effectivement démarré, écriture du témoin volontairement refusée, puis suppression runner volontairement refusée ; relecture API `stopped` et trois services non tournants avant cette seconde panne. Le runner restant est ensuite récupéré/supprimé explicitement, absence relue.
- **R3 — corrigé.** Le programme hors ligne écrit maintenant un reçu même en exception ; le parent le relit **avant** destruction. `offline_failure` porte une étape et un code d'une liste fermée, jamais le stderr/SQL/texte d'exception brut. Réels et distincts : `archive_restore / ARCHIVE_TRUNCATED`, `sql_preflight / SQL_DDL_UNSUPPORTED`. Une cause inconnue devient `offline_restore / IMPORT_REFUSED` ; reçu impossible à récupérer : `OFFLINE_RECEIPT_UNAVAILABLE`, pas un faux détail. Les codes sont destinés au diagnostic, pas une autorisation de poursuivre.
- **R1 — corrigé sans changement de baseline.** Lecture en données seules de `package.json → WordPress.Version` et de `$wp_version` du cœur épinglé : égalité textuelle stricte obligatoire **avant import SQL et tout bootstrap**. Métadonnée absente/invalide : `SOURCE_CORE_METADATA_REFUSED`. Discordance : `SOURCE_CORE_VERSION_MISMATCH`, avec les deux versions numériques au reçu. Test réel **source 6.9.1 / cœur 7.0.9** refusé, base d'import encore absente à la relecture. La recette commerciale reste 7.0.9 ; elle ne qualifie pas 6.9.1 et ne met plus à niveau implicitement une archive 6.9.1. Sélection/qualification d'un cœur de production correspondant : à arbitrer séparément, sans contourner les minima des ZIP commerciaux.
- **R2 — corrigé.** Le parseur pur réellement utilisé est **`wp/outils/staging-wp-integration/worker/worker.py`**, chargé comme `legacy_importer.py` par `run.py`. Le chemin autonome choisit explicitement les seuls moteurs locaux InnoDB/MyISAM/Aria/Memory ; les autres appels gardent le défaut InnoDB. Aucun suffixe SQL arbitraire, moteur externe, procédure, déclencheur ou repli SQL ouvert. Les moteurs sont relus dans `information_schema` après import, sans conversion ; les non-InnoDB figurent dans `warnings` avec noms/engine, sans valeurs. **MyISAM réellement importé et publication réussie en classique/HPOS**, non bloquant. Aria/Memory : grammaire seulement, non qualifiés par cette recette E2E.
- **R5 — non choisi, protection conservée.** `DISALLOW_FILE_MODS=true`, `DISALLOW_FILE_EDIT=true`, `AUTOMATIC_UPDATER_DISABLED=true`, `WP_AUTO_UPDATE_CORE=false` et allowlist HTTP existante restent inchangés. L'incohérence de capacité de mise à jour reste ouverte : **Ced choisit « admin » ou « scripts »** avant une remise complète. Ce n'est ni une permission de mise à jour admin, ni une décision de fermer l'egress à sa place.
- **R6 — documentation explicite.** `inside.py` mute **en mémoire seulement**, dans sa copie locale du parseur importé, `CREATE_WORDS.update({'ON', 'UPDATE', 'UTF8MB3_GENERAL_CI'})` ; cela n'écrit ni la bibliothèque déployée ni l'outil partagé. La canonicalisation porte seulement sur les groupes CREATE (ordre du suffixe AUTO_INCREMENT), pas les littéraux INSERT. L'extension de moteurs R2 est un paramètre explicite de `sql_plan`, pas une ouverture générale de cette grammaire.
- **R7 — exécuté.** Le self-test comporte désormais quatre cas : classique, HPOS, secret résiduel, **table personnelle non tranchée**. Les deux refus traversent l'archive, les trois scripts natifs, le sas et la relecture d'arrêt/HTTP ; aucun `inject`/`start` ni témoin verified sur ces branches. `--case personal` permet le rejeu ciblé ; le défaut exerce les quatre.

## Preuves finales et tests réellement exécutés

- **Publication complète :** `publication-22nov/6d5fac463e61/result.json`, sortie **0**, **4 cas PASS**, dont deux publications HTTP 200 à l'URL exacte avec vrais Subscriptions 9.4.1/Memberships 1.30.3, et deux refus `SECRET_OU_IDENTIFIANT` / `TABLE_PERSONNELLE_A_TRANCHER`. Source/cœur 7.0.9 égaux, table MyISAM conservée et signalée. Durée observée **330.988372 s** pour ces quatre fixtures seulement.
- **Pannes/diagnostics réels :** `corrections-22nov/faults-a4d2ca414cea/result.json`, pilote `wp/tests/a01-court/exercise_corrections.py`, sortie **0**, **4 scénarios PASS**. Chacune des quatre exécutions sujet conserve honnêtement sa sortie **1 / FAIL attendue** : double panne R4, archive tronquée, SQL non pris en charge, mismatch de cœur. Rien n'a été converti artificiellement en succès dans les reçus sujets.
- **Régression hors ligne :** `tests-21nov/3c4e0cfbc8c4/result.json`, sortie **0**, **18 contrôles PASS / 0 FAIL**, 12 tests archive, 17 tests banc, 9 cas données / 337 assertions, lint PHP. Le `full_staging_ready=false` de cet ancien entrypoint reste attendu ; ce n'est pas une publication.
- **Unitaires hôte sans PHP :** 4 corrections, 8 sas publication, 7 diagnostic preflight, 6 parseur, 17 banc, tous verts ; journaux `corrections-22nov/unit-*-final.log`. Ils se recoupent avec les suites embarquées : **ne pas additionner ces compteurs**. RED puis GREEN conservés séparément pour R4/R3/R1/R2/R7.
- **Nettoyage :** huit nouveaux sites de cette passe supprimés et absence API/conteneurs/volume/réseau/répertoire relue. Huit runners de publication absents, dont celui récupéré après panne simulée, plus le runner hors ligne supprimé. `corrections-22nov/verification-live.json` vérifie aussi les anciens noms de tests historiques, tous absents, et les empreintes de l'outil déployé inchangées. Aucun compte/licence distant audité ni accès agent utilisé ; effets automatiques de provisioning uniquement dans le GO du 22/11.

## Périmètre qualifié / refus attendus

`.wpress` **non compressé**, site simple, en-têtes de **4 377 octets**, SQL du sous-ensemble fermé et version déclarée obligatoire égale au cœur de l'image. Chiffré/compressé/multivolume/multisite, syntaxe SQL hors sous-ensemble (y compris vues/déclencheurs non qualifiés), moteurs hors ensemble local et versions différentes sont refusés avec diagnostic, **pas exécutés par un SQL de repli**. Les vues/déclencheurs restent une limite de format/grammaire, pas une suppression silencieuse. Le champ de version est celui de l'exporteur officiel AI1WM ; URL et empreinte de la source lue dans `corrections-22nov/package-format-source.json`.

Le réseau reste coupé pendant import/vérification. Après vérification : filtrage HTTP WordPress seulement, pas un pare-feu système. **La mise à jour d'extensions n'est pas qualifiée**, précisément à cause de R5. La fixture ne qualifie ni l'archive réelle d'Imagine ni une restauration de production ; Ced seul lance un éventuel premier import, avec rapport relu avant accès agent.

## Commandes de revue sans mutation de site

```sh
PYTHONDONTWRITEBYTECODE=1 python wp/tests/a01-court/test_corrections.py
PYTHONDONTWRITEBYTECODE=1 python wp/tests/a01-court/test_publication.py
PYTHONDONTWRITEBYTECODE=1 python wp/tests/a01-court/verify_publication.py \
  --report production/A-01/publication-22nov/6d5fac463e61/result.json --live-cleanup
```

Les commandes opérateur, mot de passe stdin, JSON de décisions et reprise sur nouveau nom documentés dans la section historique suivante restent leur interface ; **elles ne valent pas GO de lancement**. Sur table à trancher : aucune décision fictive par défaut ; JSON Ced puis copie fraîche. Sur mismatch de cœur : arrêter, pas modifier le package pour le faire correspondre. Les ZIP commerciaux n'ont pas été rétrogradés et leurs gardes ne sont pas contournés.

---

# Historique — livraison précédente invalidée par les corrections fusionnées

# A-01 — publication réelle qualifiée sur archives fictives, 22 novembre 2026

**Livraison à relire : commande complète et trois cas réels PASS.** Le GO de Ced du 22/11 à 13 h 11, inscrit dans `A-FAIRE.md`, lève le blocage licence/MCP du 21/11. L'usage de l'accès agent créé reste interdit et n'a jamais été fait. Aucun import d'Imagine, aucune ouverture de son archive, aucun accès à l'ancienne copie.

## Preuves actuelles

- Commande : **`wp/outils/staging-court/publish.py`**.
- Acceptance finale : **`production/A-01/publication-22nov/3f837c790d4b/result.json`**, sortie **0**, **3 cas PASS** : classique publié/vérifié, HPOS publié/vérifié, archive piégée refusée avant injection/publication.
- Vérification finale : **`production/A-01/publication-22nov/verification-final.json`** ; synthèse et chemins dans **`production/A-01/publication-22nov/acceptance.json`**.
- Nouveau sas : **8 tests OK**, `publication-22nov/unit-final.log`. Rouges conservés : refus avant vérification, arrêt sur échec runtime, nom tronquable, booléen seul sans les trois reçus natifs.
- Non-régression hors ligne rejouée : **`production/A-01/tests-21nov/2a5c8c0fcbb1/result.json`**, **18 contrôles PASS, 0 FAIL** ; 12 tests archive, 17 tests du banc, 9 cas/337 assertions données et lint PHP. Le dossier conserve un nom historique, mais le reçu est daté du 22 novembre.

Les tests ont tous été supprimés après preuve. Le vérificateur relit leur absence par noms exacts : API 404, trois conteneurs, volume HTML, réseau de site et répertoire. Il couvre aussi les passes intermédiaires et le nom tronqué récupéré explicitement. Les cinq empreintes du code/modèles déployés consignées sont identiques avant/après et lors de la revérification. Ni code de l'outil, ni modèle, ni autre site modifié.

## Commande unique pour Ced

Depuis **`C:/Users/Ced/imagine`**, Python, WSL Ubuntu et Docker déjà présents :

```sh
PYTHONDONTWRITEBYTECODE=1 python wp/outils/staging-court/publish.py \
  --operator-ced \
  --archive "$ARCHIVE_WPRESS" \
  --name imagine-test-a01-ced-01 \
  --production-url "$URL_SOURCE" \
  --table-decisions "$DECISIONS_CED" \
  --php-version 8.2
```

Ced fournit lui-même chemins et URL source. Omettre `--table-decisions` sans décision écrite ; aucune décision synthétique n'est reprise par défaut. Le mot de passe neuf du compte **`imagine-test-admin`** est demandé sans écho, puis passe par stdin, jamais argv/rapport (20 à 72 octets UTF-8). Aucun secret d'accès agent ou de licence de la plateforme n'est récupéré ou réutilisé par la commande ; les valeurs DB de l'environnement du site ne sont pas affichées ni journalisées.

Nom : préfixe `imagine-test-`, minuscules/chiffres et tirets simples entre composants, **40 caractères maximum**. Un nom existant ou qui serait normalisé/tronqué est refusé, pas réparé. PHP **8.2** est la version qualifiée. **Ced seul lance le premier import réel ; son rapport est relu avant tout accès agent.** Le PRET livre du code et des preuves, pas un GO d'import ou d'ouverture aux agents.

### Enchaînement réel

1. Création normale `POST /api/sites`, template `sandbox-wp-minimal` ; licence et provisioning MCP automatiques normaux autorisés par le GO, sans usage de leurs identifiants. Attente de fin, arrêt normal et relecture des trois services arrêtés.
2. Restauration dans un runner neuf **network=none**, sans port, montage ou volume hôte ; MariaDB sur socket Unix uniquement. Réemploi inchangé de **neutraliser → anonymiser → verifier**. WordPress n'est bootstrapé qu'après le contrôle initial des données/fichiers.
3. **Les trois reçus natifs réussis sont obligatoires** : un booléen seul ne publie rien. Sur refus, rien n'est injecté dans le site web.
4. Site toujours arrêté : remplacement du core préparé et de tout `wp-content`, puis de sa seule base WordPress. Helpers jetables sans réseau, exclusivement sur les volumes de ce test, base cible avec sa propre image et socket sans accès réseau. Les comptes système DB de l'outil ne sont pas remplacés ; helpers supprimés avant démarrage.
5. Comparaison des empreintes de **tous** les fichiers copiés au résultat hors ligne. Configuration de confiance neuve, sans licence/identifiants plateforme, variables DB déjà prévues par le site et salts neufs non journalisés. `home`/`siteurl` sont réglés par SQL vers **l'adresse exacte attribuée par l'outil**, sans démarrer WordPress, comme demandé au brief.
6. Démarrage API normal, sondes réelles email/HTTP/Subscriptions/cron/AS/passerelles et allowlist. Sur les seules fixtures : vrai renouvellement AS forcé, bloqué avant callback et sans nouvelle commande de renouvellement.
7. HTTP 200 sans redirection exigé sur le port local **et l'URL exacte depuis la machine opérateur**. Puis écriture et relecture de **`.imagine-staging-verified.json` à la racine du site**, et `verified` dans le rapport.

Le dashboard n'a pas de colonne native A-01 « vérifié » : son état reste `running`. Le statut vérifié est celui du **témoin racine et du rapport**, selon le brief ; aucune colonne inventée ni écriture dans sa base. Ses anciennes métadonnées MCP peuvent rester périmées après remplacement.

### Sortie, table à trancher, reprise fraîche

Sortie finale : `status` et chemin `production/A-01/publication-22nov/<run_id>/result.json`. Succès **0** : site conservé en marche avec témoin `verified`. Refus **1** : étape/tag et site arrêté, jamais faux verified ; helpers/copie de travail détruits. Syntaxe de commande invalide : argparse 2. Le self-test supprime même ses tests refusés, après la preuve d'arrêt ; le mode Ced conserve le site refusé **arrêté**.

Le rapport donne tables/colonnes/nombres de lignes, jamais leurs valeurs. Sur `TABLE_PERSONNELLE_A_TRANCHER`, Ced choisit explicitement `garder`, `vider`, ou `anonymiser` les colonnes désignées. Exemple **de syntaxe fictive, pas une décision de production** :

```json
{"wp_table_fictive": {"action": "anonymiser", "columns": ["email", "telephone"]}}
```

Ne pas reprendre le `garder` Woo de la recette comme décision sur Imagine. Après arbitrage : supprimer **le test exact dans l'outil par son usage normal**, contrôler sa disparition, prendre un nouveau nom et relancer la même commande sur copie fraîche. Pas de réparation/écrasement en place.

**Durée mesurée : 258.975339 s pour les trois cas**, archives fictives d'environ 127 Mo, créations et suppressions comprises. Ce n'est pas une prévision pour Imagine : sa taille, sa grammaire SQL et ses tables ne sont pas connues de l'agent. Appels bornés, aucun pull/téléchargement prévu par le runner.

## Acceptance : ce qui a été exécuté

Deux stockages, vrais **Subscriptions 9.4.1 / Memberships 1.30.3**, WooCommerce **11.1.1**, WordPress **7.0.9** ; PHP publié **8.2.32**, worker réutilisé **8.2.36**. Versions exécutées/épinglées, pas annoncées comme les plus récentes. ZIP commerciaux opérateur vérifiés par empreinte, seulement copiés dans le conteneur ; pas d'achat, téléchargement ou activation de licence WooCommerce.

- Six abonnements : IDs, état, client, période/intervalle, dates, devise, montants, produits, quantités, taxes, pays et moyen de paiement inchangés.
- Quatre adhésions : liens utilisateur/plan, états/dates et empreinte des règles inchangés. Droits API réels identiques avant/après : actif admis ; invité, non-membre, expiré, annulé, en pause refusés.
- Extensions actives, thème et réglage fictif conservés ; fichiers plugins **7 338→7 338**, thèmes **396→396**. Tous les fichiers restaurés sont d'abord comparés à leur source ; chaque fichier conservé garde son empreinte. Ajouts consignés : MU sécurité et fichiers/journal régénérés dans `uploads/wc-logs` par le bootstrap Woo. Pas une archive de production conservée ; aucune promesse d'absence perpétuelle de nouveaux journaux après bootstrap.
- Email réellement coupé, HTTP interdit effectivement bloqué, staging WCS réel, allowlist/configuration exactes. Vraie action AS forcée : **0 callback, 0 renouvellement ajouté**, statut `failed`. Aucun email ni paiement réel.
- Clé entièrement fictive conservée dans un MU de l'archive, réinsérée au bootstrap : relecture native → **`SECRET_OU_IDENTIFIANT`, code 1**. **Aucune injection**, trois conteneurs arrêtés et endpoint HTTP non joignable, aucun témoin verified, puis suppression normale du test.

### Novamira après injection, sans utiliser son accès

Dans les deux copies acceptées : **extension Novamira/Pro absente**, **0 enregistrement non vide de mot de passe applicatif**. Les identifiants applicatifs créés automatiquement ne peuvent donc plus authentifier sur la copie remplacée. Conclusion par absence du mécanisme/enregistrements, **pas essai de connexion** ; aucun secret récupéré, révélé ou réutilisé.

Le diagnostic distingue la présence éventuelle d'une extension provenant de l'archive, sans la supprimer arbitrairement ; la présence seule n'invente pas un sixième blocage de données. Des mots de passe applicatifs résiduels empêchent de certifier l'absence de l'accès créé. Les anciennes métadonnées/identifiants de l'outil peuvent rester chez lui, périmés : ni lus ni réimportés. Pas de révocation/audit du compte de licence distant. Le test piégé n'est pas injecté : site vide arrêté puis supprimé, sans usage agent.

## Limites assumées et incidents conservés

**Avant vérification : aucun réseau/port/sortie système. Après vérification : filtrage des API HTTP WordPress seulement, pas pare-feu système.** `WP_HTTP_BLOCK_EXTERNAL=true`, `WP_ACCESSIBLE_HOSTS=*.wordpress.org,*.woocommerce.com`, MU aligné, redirections interdites. Les sockets PHP directs ne sont pas filtrés par ces constantes : limite expressément arbitrée dans le brief et écrite dans chaque rapport/témoin. Les hôtes de mises à jour sont testés par filtre, pas par téléchargement/installation.

L'IP LAN depuis WSL produit `ConnectionResetError`, mais **l'URL exacte depuis Windows et le port local répondent 200 avec le même marqueur**. Les deux observations restent dans la preuve ; pas de modification réseau/frontal de l'outil ni substitution de réponse. Les échecs antérieurs sont conservés : transport WSL programmes/SQL corrigé par stdin ; droits tar corrigés dans le helper isolé post-vérification ; nom tronqué à 40 récupéré et supprimé (`4fde653a20f2/cleanup-recovery.json`).

Formats qualifiés : `.wpress` non compressé, en-têtes 4 377 octets, SQL du sous-ensemble fermé, simple site. Chiffré/compressé/multivolume/multisite, SQL hors grammaire et autres versions non qualifiés ; refus sans repli arbitraire. Première qualification d'Imagine réservée à Ced. La fidélité formulaire/SEO/champs est aussi rejouée dans le banc hors ligne distinct.

Les scripts natifs et bancs frères restent inchangés. `staging-wp-integration` n'est pas développé/utilisé comme runtime : seul son parseur SQL pur est lu. Aucun Git, installation hôte, accès à l'ancien staging, écriture de rapport parent ou du verrou. L'ancien diagnostic licence du 21/11 et l'ancien `run.py --archive` sont **historiques**, pas la nouvelle commande opérateur.

### Réemploi du standard

Relecture des mécanismes standards réutilisés : `pre_wp_mail`, API HTTP WP, staging natif WCS et API Action Scheduler. Le sur-mesure ajouté enchaîne l'import déjà qualifié, l'API normale et les sondes/témoins. Références officielles vérifiées HTTP 200 et empreintées dans `publication-22nov/standard-docs.json` :

- https://developer.wordpress.org/reference/hooks/pre_wp_mail/
- https://developer.wordpress.org/apis/making-http-requests/
- https://woocommerce.com/document/subscriptions-handles-staging-sites/
- https://actionscheduler.org/api/

## Revérification bornée pour le parent

Depuis la racine, aucune archive/import/connexion agent/mutation de site :

```sh
PYTHONDONTWRITEBYTECODE=1 python wp/tests/a01-court/test_publication.py
PYTHONDONTWRITEBYTECODE=1 python wp/tests/a01-court/verify_publication.py \
  --report production/A-01/publication-22nov/3f837c790d4b/result.json --live-cleanup
```

Bornes outil : **60 s** pour les 8 tests ; **300 s** pour reçus/empreintes puis GET/inspect d'absence par noms exacts et hashes déployés, sans create/start/stop/delete. Ne pas employer `publication_preflight.py` comme gate actuel : son verdict licence historique ne tient pas compte du GO ; la commande complète n'en utilise que la collecte en lecture seule.

Rejeu complet, avec nouveaux tests nommés puis suppression finale :

```sh
PYTHONDONTWRITEBYTECODE=1 python wp/outils/staging-court/publish.py --self-test-publication
```

Borne outil **600 s**, propriétaire A-01 unique. `--case classic|hpos|trap` ne qualifie qu'un cas ; l'acceptance complète exige les trois. `run.py --self-test` reste la régression **hors ligne**, avec `full_staging_ready=false` attendu : ce n'est pas la commande de publication.

---

# Historique du 21 novembre — remplacé par la livraison du 22 novembre ci-dessus

Les questions/blocages ci-dessous sont conservés pour traçabilité, pas comme consignes encore ouvertes.

# A-01 publication — 21 novembre 2026 : blocage concret de l’API normale, aucun PRET

## État de la passe publication

**BLOQUÉ avant création d’un site.** La limite réseau du brief du 21/11 est acceptée : après vérification, pas de pare-feu système exigé, uniquement `WP_HTTP_BLOCK_EXTERNAL=true`, `WP_ACCESSIBLE_HOSTS=*.wordpress.org,*.woocommerce.com` et le filtre MU existant. L’ancien blocage « sortie système requise » n’est donc plus un motif d’arrêt.

Le prérequis nouveau est attesté sur le **dashboard effectivement déployé**, sans appeler une fonction métier ni lire une valeur secrète : `production/A-01/publication-21nov/preflight-live.json`. Le moteur Docker WSL existant répond ; aucun besoin d’installation hôte ou de téléchargement n’a été constaté.

### Pourquoi ne pas appeler POST /api/sites

- Le template normal `sandbox-wp-minimal` indique bien zéro extension premium dans son JSON. Mais `_provision_site` ajoute systématiquement `_MCP_PLATFORM_ZIPS` (`novamira.zip`, `novamira-pro.zip`) à **tout** template, y compris celui-ci. Les deux fichiers sont présents ; seul leur booléen de présence est lu, pas leur contenu.
- La variable de licence Novamira est configurée : le diagnostic ne récupère qu’un booléen, jamais sa valeur. La même fonction appelle alors `activate_novamira_pro_license`, puis `provision_mcp` ; cette dernière active les abilities, crée les identifiants applicatifs et valide la connexion. On atteste le **chemin d’appel et la tentative prévue**, pas la validité de la licence ni une activation réussie (non tentée).
- `CreateSiteRequest` requiert `template_slug` et n’offre aucun champ de création vide sans licence/MCP. `create_site` exige un template reconnu. Le retour anticipé `if not template: return` de `_provision_site` n’est pas atteignable par ce contrat normal de création.

Sources exactes dans le reçu : `/app/api/orchestrator.py`, fonctions `activate_novamira_pro_license` lignes 251–261, `provision_mcp` 271–284, `create_site` 493–525, `_provision_site` 542–623. Le reçu conserve ces extraits de code sans valeurs de configuration, les champs OpenAPI observés et cinq empreintes du code/modèles de l’outil ; leur égalité après diagnostic est vérifiée.

Une création suivie d’un arrêt « assez rapide » serait une course contre l’activation ; elle n’est pas une solution. Supprimer ultérieurement Novamira dans le wp-content remplacé n’annulerait pas un appel de licence déjà parti. Modifier les modèles, vider la licence du service ou insérer directement une ligne de site contournerait l’usage normal demandé. Aucune de ces voies n’a été utilisée. La doctrine §3 (pas de compte réel sans GO) et la limite « Novamira non branché » empêchent de transformer l’autorisation de créer un test en autorisation d’utiliser une licence configurée.

### Seam minimale à décider, non appliquée

L’API normale doit pouvoir créer un **vrai site vide sans plateforme** : une option explicite de création évitant ensemble l’ajout des ZIP Novamira, l’appel d’activation de licence et le provisioning MCP. Garder les comportements par défaut des autres sites. Cela touche le code partagé de l’outil ; le brief impose donc l’arrêt et l’arbitrage de Ced, pas un patch ici.

**Question fermée au parent/Ced : autoriser cette option ciblée dans l’outil partagé, oui/non ?** Autre possibilité à fournir par l’opérateur : un parcours normal déjà existant sans ces effets, non présent dans l’API examinée. Aucune autorisation générale ou activation de licence n’est déduite de cette question.

### Exécuté et preuves de cette passe

- Diagnostic livré : `wp/outils/staging-court/publication_preflight.py` ; lecture seule, aucun import, aucune mutation API, aucun accès à une ligne/site WordPress ou à une archive. Reçu réel `production/A-01/publication-21nov/preflight-live.json` : sortie **78**, `BLOCKED`, trois motifs précis, `full_staging_ready=false`.
- Test dédié : `wp/tests/a01-court/test_publication_preflight.py` ; **7 tests réussis**. RED préalable de la détection de licence conservé dans `publication-21nov/preflight-red.log`, GREEN complet dans `publication-21nov/preflight-green.log`. Ces tests portent sur le diagnostic, pas sur une publication.
- Banc PHP existant réutilisé sans modification : `python wp/outils/staging-court/run.py --self-test`. Nouveau reçu `production/A-01/tests-21nov/30953141a691/result.json` : **18 contrôles PASS, zéro FAIL** en classique/HPOS et entrypoint exact hors ligne ; 12 tests archive, 17 tests banc, 9 cas/337 assertions data, lint PHP. Exécution réelle dans un conteneur jetable sans réseau ni montage/port ; archives uniquement fictives créées dans ce même conteneur. Ce banc continue de vérifier honnêtement le refus 78 `DATA_VERIFIED_PUBLICATION_BLOCKED`, pas une publication.
- Pas de nouveau site créé dans l’outil, donc aucun site de cette passe à supprimer ; pas de GET de la liste des sites ni accès aux autres sites. Le seul conteneur jetable du self-test est supprimé ; contrôle indépendant de son absence enregistré dans `publication-21nov/artifact-verification.json`.
- **Non exécutés** : commande complète de publication avec les vrais Subscriptions/Memberships, site joignable vérifié, canari secret empêchant la publication. Les preuves commerciales du 20/11 demeurent historiques et ne sont pas revendiquées comme ces acceptances. Aucun faux site positif ni reçu canari fabriqué.
- `run.py`, l’importeur, les traitements natifs, tous les fichiers partagés et les modèles de l’outil sont inchangés. Aucun `PRET`, Git, rapport `files/rapports`, modification de `.hermes.lock`, archive Imagine, secret, donnée réelle, Novamira connecté par nous, ou installation hôte.

### Revérification sûre par le parent

Depuis `C:/Users/Ced/imagine` (prendre un nom de reçu neuf ; aucun écrasement) :

```sh
PYTHONDONTWRITEBYTECODE=1 python wp/tests/a01-court/test_publication_preflight.py
PYTHONDONTWRITEBYTECODE=1 python wp/outils/staging-court/publication_preflight.py --output production/A-01/publication-21nov/preflight-parent.json
```

Attendu : 7 tests OK ; diagnostic seul en lecture seule, **code 78**. Un changement de l’API nécessite une nouvelle qualification, jamais une autorisation implicite. Rejeu synthétique PHP possible séparément : `PYTHONDONTWRITEBYTECODE=1 python wp/outils/staging-court/run.py --self-test`. La commande d’import réel antérieure ci-dessous reste **à ne pas lancer** ; la commande complète pour Ced et sa durée ne sont pas qualifiées tant que le prérequis API n’est pas levé. Sur table à trancher, conserver la procédure explicite de décisions puis copie fraîche, sans décision automatique.

---

## Historique antérieur conservé — remplacé pour les motifs de blocage par le point ci-dessus

# A-01 — chemin court du 21 novembre : fidélité prouvée, publication encore bloquée

## État courant au 21/11 — sous-lot exécuté, pas de PRET global

Commande autonome livrée dans wp/outils/staging-court/run.py, distincte du service partagé. Rejeu exécuté : `python wp/outils/staging-court/run.py --self-test`. Guide et commande réservée à Ced : wp/outils/staging-court/README.md. Aucun import réel n'est autorisé ou exécuté.

Preuve finale production/A-01/tests-21nov/d1cc212680fd/result.json : 18 contrôles d'aller-retour et d'entrypoint PASS, 12 tests défensifs du lecteur, 17 tests du banc, 9 cas/337 assertions de données, lint des PHP ajoutés, sources et cleanup PASS. Archives .wpress exclusivement exportées depuis les deux sites fictifs créés dans le même conteneur ; aucune archive réelle/dérivée, aucun fichier d'archive sorti sur l'hôte. Les deux stockages sont exercés et leurs commandes métier conservées.

Fidélité : restauration complète par empreinte avant nettoyage ; extensions et thème actifs inchangés ; fichiers plugins 7 704→7 704, thèmes 396→396, uploads 9→9, MU 2→3 (ajout de sécurité attendu). Seuls advanced-cache.php, object-cache.php et l'archive fictive ai1wm-backups/fiction.wpress sont retirés. Les empreintes de thème/média/MU/formulaire sont consignées ; bootstrap réel, rendu Contact Form 7, réglages SEO et lectures Meta Box inchangés. Ces nombres décrivent uniquement la fixture, pas Imagine.

La première restauration refuse la table wp_yoast_primary_term non tranchée ; le second passage utilise garder uniquement comme décision de fixture clairement nommée, jamais comme autorisation Ced réelle. Le vrai entrypoint opérateur est invoqué avec l'archive générée : code 78, status imported, data_verified true, verification_state DATA_VERIFIED_PUBLICATION_BLOCKED et arrêt de MariaDB constaté. Pas de faux statut global verified.

Suite native complète fraîche : wp/tests/staging-e2e/evidence/9ff611303d90/result.json = 131 PASS / 2 hors périmètre, zéro échec ; journal hôte 4 PASS, dont suppression/absence relue. Cela inclut classique/HPOS, anonymisation, conservation métier, mail réellement bloqué, résidus refusés et tables à trancher. Les paquets commerciaux n'ont pas été recherchés hors checkout ni rejoués : les preuves commerciales du 20/11 restent historiques, et les onze sources natives ont été comparées à leur manifeste, toutes inchangées.

Chemin utilisé : lecteur fidèle du format non compressé (en-têtes 4 377 octets), parseur SQL fermé du worker existant, trois scripts natifs inchangés. Les ajouts de grammaire locaux requis par le SHOW CREATE synthétique et le réordonnancement du suffixe AUTO_INCREMENT concernent seulement CREATE ; pas de modification des littéraux INSERT, pas de SQL arbitraire de repli. Les refus initiaux et corrections sont conservés dans tests-21nov/28c3342a2b5a, 3063981f4044 et 2080a11739f5 ; premiers verts 8adfc0346b0d et aacd8ee179c7. Le reçu final couvre le code après tous les correctifs.

Blocage restant : publication web et confinement système des sorties aux domaines de mise à jour non implémentés. Une whitelist WordPress ne suffit pas à filtrer les sockets d'une extension ; aucun bridge général n'est ouvert pour obtenir artificiellement un succès. Le prototype partagé disponible dans le checkout élimine les fichiers ; un simple enchaînement de celui-ci ne peut pas être fidèle. Il n'a pas été recherché de site/importeur/archive hors checkout, et aucune écriture sur le service partagé n'est faite. Ajouter une nouvelle orchestration frontend/proxy/réseaux dépasserait le chemin court : arrêt de cette extension au titre de la proportion, sans GO inventé. Les exports chiffrés/compressés/multivolumes/multisites, SQL hors sous-ensemble et versions non qualifiées sont refusés ou non qualifiés.

Ce que Ced verrait : rapport daté par exécution, étapes et codes, liste de tables/colonnes/nombres de lignes/décisions sans valeurs, runtime arrêté et motif de non-publication. En table personnelle manquante : fournir un JSON explicite garder/vider/anonymiser telles colonnes, puis nouvelle copie fraîche ; rien n'est choisi automatiquement. Le mot de passe neuf transite par stdin sans journal. Temps : variante exécutée dans la demi-journée ; aucune durée de vrai import annoncée sans vraie archive, réservée à Ced.

Couches non utilisées et laissées en l'état : overlay/API, worker runtime partagé, bascule, Novamira, images déployées et services partagés. Seul le parseur SQL pur est lu. Aucun host install, Git, compte/site réel, réseau de test sortant ou déploiement. Tous les conteneurs possédés par cette passe ont été supprimés et leur absence vérifiée. Aucun PRET A-01 n'est déposé tant que le chemin complet n'est pas qualifié.

## Historique du 20 novembre conservé

# A-01 — compléments commerciaux réels, import opérateur toujours non prêt

**20 novembre 2026, 15 h 34 CET — PASS ciblé classique et HPOS.** Reçu final `wp/tests/licensed-a01/evidence/e49f54c5e931/result.json`, sortie **0**, **104 checks PASS et 4 observations**, zéro échec ; ce ne sont pas 104 tests métier indépendants. Classique : 48 PASS + 2 observations ; HPOS : 50 PASS + 2 observations ; six PASS d'isolation interne. Journal hôte : quatre PASS, dont suppression relue du conteneur exact. Résultat SHA-256 `c5da74dabc717773098edb08603d8695cbdd0c297183821a5f70ef858c5efc56`.

**Pas d'import réel, pas de déploiement, pas de `PRET`.** La fidélité des fichiers de l'importeur opérateur reste non démontrée : l'import reste **NON PRÊT**, indépendamment du succès des données/extensions. La baseline non commerciale `f36c72f4d187` n'a pas été rejouée ; les onze sources sujets sont identiques à son manifest. Le nouveau banc est séparé dans `wp/tests/licensed-a01/`, sans modification des scripts de production ni du banc précédent.

## Résultats réels par cas

| Cas | Classique | HPOS |
|---|---|---|
| Memberships **1.30.3** puis Subscriptions **9.4.1**, activations indépendantes | PASS / PASS | PASS / PASS |
| Article protégé réellement reconnu ; témoin public non restreint | PASS | PASS |
| Membre actif : accès `wc_memberships_user_can` et présence du contenu `wcm_restrict`, avant/après nettoyage | autorisé / autorisé | autorisé / autorisé |
| Invité : mêmes contrôles avant/après | refusé / refusé | refusé / refusé |
| Non-membre : mêmes contrôles avant/après | refusé / refusé | refusé / refusé |
| Membre expiré : mêmes contrôles avant/après | refusé / refusé | refusé / refusé |
| Membre annulé : mêmes contrôles avant/après | refusé / refusé | refusé / refusé |
| Membre en pause : mêmes contrôles avant/après | refusé / refusé | refusé / refusé |
| Adhésions : IDs, liens utilisateur/plan, statuts, dates ; règles de restriction | égalité exacte avant/après | égalité exacte avant/après |
| Six abonnements, états actif/suspendu/en attente d'annulation, créés par vraies API | six lignes `wp_posts` | six lignes `wp_wc_orders` |
| Identifiants/clients, états, début/prochain paiement/fin, période/intervalle, EUR/montants, produits/quantités/taxes, pays, paiement | égalité exacte avant/après | égalité exacte avant/après |
| Email, prénom, adresse et téléphone fictifs des six abonnements | nettoyés | nettoyés ; 12 coordonnées billing/shipping/pays inchangées par SQL direct |
| Email externe réinjecté par API dans un vrai abonnement | refus CLI 1 `EMAIL_EXTERNE` | refus CLI 1 `EMAIL_EXTERNE` |
| Chaîne `neutraliser → anonymiser → verifier` | 0 → 0 → 0 après décision fictive nommée | idem |
| Table inconnue personnelle `wp_wc_email_unsubscribes` sans décision | refus 1 `TABLE_PERSONNELLE_A_TRANCHER` | idem |
| Même table après `garder` explicite uniquement dans le contexte fictif | acceptée, aucun défaut de production changé | idem |
| Mode réel `WCS_Staging::is_duplicate_site()` après traitement | true | true |
| Mutation non-staging, MU sujet intact ; probe réel, moteur et CLI complète | false ; refus 1 `SUBSCRIPTIONS_NON_STAGING` | idem |
| Actions natives de Subscriptions | 14 pending + 16 canceled → 30 canceled | idem |
| Témoin AS avant verrou, un seul vrai hook de renouvellement, sans passerelle ni email réel | complete, 1 appel, 1 commande de renouvellement manuel | idem |
| Même type d'action AS sous verrou | failed, 0 appel, 0 renouvellement ; cron/runner/async coupés | idem |
| Runtime réel après nettoyage | mail/HTTP/cron/AS/passerelles coupés ; staging confirmé | idem |
| Dernier vérificateur après purge explicite des journaux de tests | sortie 0 | sortie 0 |

Le témoin positif de renouvellement est annulé par restauration du SQL produit **dans ce même conteneur**, avant le traitement sujet ; égalité du snapshot métier relue. Les contrôles des emails sont sensibles avant nettoyage et à la réinjection. Aucune preuve commerciale n'est remplacée par une doublure.

## Runtime et limites de cette recette

- WordPress **7.0.9**, WooCommerce **11.1.1**, PHP **8.2.36**, MariaDB **10.11.19**, WP-CLI **2.12.0** ; versions épinglées compatibles, pas annoncées comme les plus récentes. L'ancien blocage 6.9/10.4.3 est levé **dans cette image distincte**, pas par modification de la baseline. Dépendances publiques préparées séparément avant création/import ; URLs/SHA-256/image exacte dans `wp/tests/licensed-a01/compatible.lock.json`. Image finale : `sha256:2fa44089da3ca9aeaba5da0b74bbb3e9e1592b14c07d114c6a635b5c814208f2`.
- Paquets commerciaux opérateur lus hors dépôt, empreintes attendues vérifiées lors de l'extraction, copiés uniquement dans le conteneur neuf. Aucun paquet commercial dans le dépôt ou l'image publique, aucun téléchargement commercial, achat, activation de licence ou connexion WooCommerce.com.
- Droits d'adhésions **autonomes** : pas de liaison automatique Memberships↔achat/abonnement, pas de dripping, expiration simulée par attente ou renouvellement d'adhésion. API et shortcode réels sous CLI ; **pas une recette HTTP/thème/cache/REST ni une preuve d'étanchéité complète du paywall**.
- Renouvellement **manuel sans paiement** : création native de commande vérifiée, pas de débit, passerelle réelle, retry, remboursement ni échéancier réel de production. Les trois protections cron/runner/async et le garde avant exécution AS sont réellement actifs après nettoyage.
- Woo 11.1.1 introduit `wp_wc_email_unsubscribes` avec `email_hash`/`email_kind` : inventaire et refus prouvés ; décision `garder` exclusivement fictive, **pas un arbitrage de Ced**.
- Des journaux Woo `wcs-batch-processing` régénérés masquaient le tag non-staging dans des tentatives intermédiaires par un refus fichiers 78 ; les reçus sont conservés. Le reçu final obtient **bien le refus 1 et le tag précis par la CLI complète**, ainsi que par le moteur avec probe réel.
- Une exécution AS forcée sous verrou produit un journal `failed-scheduled-actions`. La purge fichiers réelle du sujet est donc rejouée **explicitement** après les manipulations avant le dernier contrôle. Ce n'est pas la preuve d'une absence perpétuelle de journaux après démarrage. Aucun garde n'est retiré, aucune donnée métier n'est supprimée pour blanchir la recette.
- Isolation inspectée avant/après : `network=none`, aucun port/montage/volume, capacités retirées, no-new-privileges, loopback seule, aucun listener TCP/IPv6 ; MariaDB sur socket Unix. Conteneur exact supprimé et absence relue. Aucun vrai site/compte/archive, Novamira, service partagé modifié, Git, installation hôte, déploiement ou ouverture web.
- La conservation des fichiers production, l'importeur complet, l'orchestration opérateur/API/MCP, la bascule et le réseau autorisé après vérification restent **non qualifiés**. Les succès commerciaux ne lèvent pas ces réserves.

## Preuves et rejeu commercial ciblé

- Sources et reçu : `wp/tests/licensed-a01/evidence/e49f54c5e931/{result,journal,driver-source,subject-source}.json`, `execution.log`, `packages.tsv`. Sources finales relues par empreinte après exécution ; onze sujets toujours identiques à `f36c72f4d187`.
- Cas complets recopiés depuis le vrai reçu : `files/rapports/2026-11-20-A-01-commercial-cases.json` ; rapport lisible : `files/rapports/2026-11-20-15h35-A-01-commercial.md`.
- Commande **synthétique seulement**, depuis `C:/Users/Ced/imagine` : `python wp/tests/licensed-a01/run.py`. Image locale exacte requise ; aucun pull/téléchargement runtime. Voir `wp/tests/licensed-a01/REPLAY.md`. Ce n'est pas la commande d'import réel.
- Diagnostics intermédiaires conservés : oracle de contenu public inadéquat (`wc_memberships_user_can` exige déjà une adhésion active), transition pending→on-hold invalide (désormais pending→active→on-hold), bridge absent puis chemins fictifs non conformes au bridge, table personnelle à trancher, et garde fichiers prioritaire. Corrections limitées au nouveau banc ; aucune source sujet changée.

---

## Baseline non commerciale stabilisée — point antérieur conservé


**20 novembre 2026 — PASS classique et HPOS sur données inventées.** Reçu exact : `wp/tests/staging-e2e/evidence/f36c72f4d187/result.json`, sortie **0**, **131 checks PASS, 2 NOT_TESTED**. Le journal du même répertoire confirme isolation avant/après et suppression relue du conteneur exact. Ces checks ne sont pas autant de tests métier indépendants.

**Aucun GO pour l'import réel.** Aucun vrai site, archive réelle, connexion Novamira, service partagé, téléchargement, installation hôte, Git, déploiement ou ouverture web utilisé dans ce sous-lot. Aucun `PRET` ajouté : l'intégration complète reste hors qualification de cette reprise ciblée.

## Causes isolées depuis `6cb3c90a73b0`

Les onze sources sujets étaient identiques au manifest du reçu de départ avant correction.

1. **Classique : décision manquante.** `wp_yoast_primary_term`, vide, comporte `taxonomy`, qui contient le motif conservateur `nom`. Le vérificateur exige `TABLE_PERSONNELLE_A_TRANCHER`, même sans ligne. Le classificateur n'a pas été assoupli. Le banc prouve le refus puis ajoute `garder` pour cette table **uniquement dans son contexte fictif**, marqué `decision_is_synthetic_not_Ced_approval`. Aucun choix de production ni arbitrage de Ced n'est créé.
2. **HPOS : collision de clé structurelle.** Le diagnostic `evidence/ff179a0b7caf/result.json` isole `PDOException`, SQLSTATE **23000**, errno **1062**, lors du remplacement de `wp_wc_order_addresses`, avec `address_type` parmi les colonnes modifiées. Le motif `address_…` vidait les discriminateurs billing/shipping : collision sur la clé unique d'une commande. La correction de `lib.php` exclut **seulement `wc_order_addresses.address_type`** de ce vidage personnel. Le nettoyage des valeurs dangereuses s'applique toujours auparavant. Aucun contrôle du vérificateur retiré.
3. **Oracle historique de note erroné.** `9ab62bc07a81` passe ensuite les traitements, la fidélité et les onze premiers résidus, mais attend à tort un avertissement pour une note liée à une commande. Le sujet et son test unitaire la classent déjà dans le périmètre transactionnel. Le banc teste désormais les **deux** branches : note de commande avec email externe refusée ; commentaire sans lien transactionnel accepté avec avertissement. Aucun affaiblissement du sujet pour obtenir du vert.

Les diagnostics exportent uniquement tags, codes SQLSTATE/errno, classes/fonctions et noms de tables/colonnes ; ni SQL, ni message PDO brut, ni valeurs de ligne. Sorties des sujets empreintées.

## Preuves dans les deux stockages

- **30 comptes et 30 commandes fictifs chacun**, créés par API WordPress/Woo ; exports/réimports SQL générés dans le même conteneur neuf. Chaîne `neutraliser → anonymiser → verifier` réussie, puis répétée.
- **Fidélité après nettoyage** : nouveau bootstrap réel de WordPress/Woo et des extensions Contact Form 7 **6.1.4**, Yoast SEO **26.5**, Meta Box **5.10.7** ; extensions actives, formulaire rendu, champs simples/clonés lus. Empreintes exactes inchangées des réglages, article et MU de champs.
- PDO indépendant : statuts, dates, montants, devise, produits, quantités, taxes, pays et moyens de paiement conservés ; mots de passe des 30 comptes remplacés et compte test ajouté. Les **60 adresses HPOS** gardent id/order_id/address_type/pays ; identités connues nettoyées. Sessions, jetons, tâches sortantes, cron et webhooks de fixture neutralisés.
- **Douze résidus par stockage** réinsérés indépendamment, détectés avant vérification, puis refusés avec le tag attendu : clé secrète/publique/restreinte/webhook/Brevo, clé en table inconnue, identifiant Stripe compte/commande, PayPal, email compte/commande/note liée. Refus de données `1` + tag exigé, pas un simple échec quelconque.
- Mail bloqué à l'exécution. Retrait du seul MU de sécurité : espion PHPMailer mémoire sensible et refus du sujet ; **aucun envoi réel**. Oracles également sensibles avant blocage.
- Table inconnue non personnelle conservée/rapportée. Table personnelle non tranchée refusée. Décisions fictives `garder`/`vider`/`anonymiser` exercées avec email externe et téléphone inventés : empreinte intégrale conservée, lignes vidées, ou seules colonnes désignées anonymisées ; présentation préservée.
- Réseau `none`, aucun port/montage/volume, capacités retirées, `no-new-privileges`, loopback seule, aucun listener TCP/IPv6, MariaDB sur socket Unix. Suppression ciblée et absence relue de chaque conteneur créé ; aucun prune.

Runtime épinglé, pas annoncé comme le plus récent : WordPress **6.9**, WooCommerce **10.4.3**, WP-CLI **2.12.0**, PHP **8.2.36**, MariaDB **10.11.19**. Image locale sans pull : `sha256:b2ffa6ad01ffacc6d31b176232c8d0779c0320daba381e05cbbd80f56d5327a0`.

## Reçus conservés

Chemins relatifs à `wp/tests/staging-e2e/`. Historiques non écrasés.

| Reçu | Résultat |
|---|---|
| `evidence/7011e26f91ee/` | reproduction des deux blocages de départ |
| `evidence/ff179a0b7caf/` | diagnostic des colonnes HPOS, sans valeurs |
| `evidence/9ab62bc07a81/` | oracle erroné de note liée isolé après fidélité réussie |
| `evidence/a45dd77b707c/` | premier vert : sortie 0, 129 PASS / 2 NOT_TESTED |
| **`evidence/f36c72f4d187/`** | **stabilisé renforcé : sortie 0, 131 PASS / 2 NOT_TESTED** |
| `evidence/c1186257ca0c/` | fixture-selftest : sortie 0, 75 PASS / 2 NOT_TESTED |
| `evidence/safety-22eece7f2ddf/result.json` | 17 tests de sécurité du banc réussis |
| `evidence/bb87e0db2ac4/data-result.json` | échec Linux conservé : `-n` masquait PDO partagé |
| `evidence/2ea8c8781c6c/data-result.json` | 9 cas data/MU/runtime/CLI, 337 assertions et lint réussis |
| `evidence/2ea8c8781c6c/journal.json` | régression billing/shipping verte sur correction, rouge sur ancien `lib.php` empreinté ; conteneur supprimé |

Les tests data/MU sont des doubles unitaires, distincts du vrai WordPress/MariaDB et des paquets payants. Le seul contrat PDO charge maintenant l'ini normal nécessaire à son module partagé Linux, au lieu de `-n` : aucune assertion supprimée, aucun module installé. Pilote ponctuel isolé conservé avec son reçu : `data-regression-driver.py`.

## Rejeu synthétique et limites

Depuis **`C:/Users/Ced/imagine`**, Python et Docker existants :

```sh
python wp/tests/staging-e2e/harness.py acceptance
```

Journal JSON et nouveau `evidence/<run_id>/` avec résultat, manifests des sources et contrôle de suppression. Code 0 seulement si les deux stockages et contrôles requis passent. Image locale manquante : refus, pas de `prepare` sous consigne sans téléchargement. Compléments : `python wp/tests/staging-e2e/test_harness.py` puis `python wp/tests/staging-e2e/harness.py fixture-selftest`.

- **Limite historique de cette baseline 6.9/10.4.3, levée uniquement par la recette commerciale distincte ci-dessus.** `results/reprise-licensed-acceptance.json` : Subscriptions **9.4.1** exige WordPress **7.0** et WooCommerce **11.1**, incompatibles avec **6.9 / 10.4.3**. Pas de contournement/licence/achat/téléchargement. Mode staging réel, son piège inverse, abonnements et renouvellements non qualifiés. Memberships **1.30.3** avait été activé ; droits non qualifiés.
- Les deux `NOT_TESTED` du reçu vert sont `paid_plugins_scope` et `real_staging_and_start_gate`. Aucun booléen de substitution crédité comme preuve commerciale.
- Bootstrap CLI, pas de serveur web exposé. Importeur d'archive complet/fidélité des fichiers production, service partagé/API/MCP, Novamira, bascule, réseau après vérification et mises à jour externes non exercés.
- Emails/IP éditoriaux hors transaction restent signalés, pas effacés globalement. Inconnues/formats opaques rapportés. La fixture verte ne qualifie pas toutes les extensions de production. Un avertissement conservateur d'identité sur `address_type` subsiste dans le vérificateur, sans blocage.
- Intégration opérateur non modifiée. Son ancien blocage data dans `OPERATEUR-A01.md` est dépassé par ces reçus ; ses autres réserves (importeur fichiers, Novamira, réseau) subsistent. Sa commande ne devient pas autorisée pour une archive réelle par ce résultat.
- Les anciens arrêts et révocations évoqués ci-dessous n'ont pas été revérifiés. **Ne pas réactiver l'ancien staging.** La réussite actuelle porte exclusivement sur la chaîne synthétique demandée.

## Notes antérieures — historiques, remplacées par le point ci-dessus

### Profil « site à abonnements » : ancien point de recette

**Décision de recette : ne pas lancer l’import réel.** L’outil partagé n’a pas été modifié. L’ancien site a été arrêté sans suppression ; la liaison agent est désactivée dans l’outil, mais la révocation du mot de passe applicatif dans WordPress n’est pas attestée. Ne pas redémarrer cette copie.

**Fait.** Les trois traitements hors ligne, les protections persistantes, le lanceur de bascule et le banc de test existent. Sur deux sites jetables (classique et HPOS), chacun avec 30 comptes et 30 commandes inventés, le banc a contrôlé l’absence de réseau et de port ouvert. Les tests propres au banc ne valent pas validation de la chaîne.

**Échec initial à conserver.** Dans les deux stockages, la neutralisation s’est arrêtée avant nettoyage sur quatre tables WooCommerce non reconnues. Les scripts n’ont donc pas encore démontré, ensemble, la réussite sur une copie propre puis le refus d’une copie contenant un résidu. L’intégration opérateur doit aussi être reliée aux scripts réels et exercée sans doublure Docker avant qualification. Voir `wp/tests/staging-e2e/REPORT.md` et `wp/tests/staging-e2e/results/acceptance.json`.

**Reprise du 20 novembre 2026.** Les quatre tables ne bloquent plus le précontrôle. Après correction de la prise en charge du type `shop_order_placehold` (champs texte anonymisés comme les commandes), la recette `wp/tests/staging-e2e/evidence/4bfcf5ac22d1/` passe la neutralisation dans les deux stockages. En classique, l’anonymiseur termine mais le vérificateur signale `SECRET_OU_IDENTIFIANT` ; en HPOS, l’anonymiseur refuse (78), cause exacte à isoler. Les 16 tests du banc passent ; conteneur jetable supprimé. Le paquet d’intégration et les sources du worker sont présents dans le dépôt, sans qualification bout en bout. Prochain diagnostic : localiser la table et la colonne sans afficher les valeurs ; identifier l’opération refusée en HPOS. Aucun import réel.

**À arbitrer par Ced :** des paquets de test autorisés pour Subscriptions et Memberships sont-ils disponibles pour le site jetable (oui/non) ? À défaut, les contrôles de ces extensions restent non validés ; pas de contournement du contrôle Subscriptions, ni d’achat.
