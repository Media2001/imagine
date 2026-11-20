# Contrat `staging-offline-v1`

Ce contrat est l'interface entre l'orchestrateur, les adaptateurs image et les scripts natifs. **La reprise A-01 n'est pas qualifiée pour un import réel** : le prototype ne conserve pas tous les fichiers du site et l'étape Novamira reste refusée. Voir `OPERATEUR-A01.md`. Aucun repli vers `wp ai1wm restore`.

## Frontière de confiance

- Trois images **déjà disponibles localement**, sélectionnées par Ced par ID `sha256:<64 hex>` : worker approuvé, MariaDB compatible `healthcheck.sh`, nginx compatible `/etc/nginx/conf.d/default.conf`. Aucun tag mutable, pull, build, installation ou activation de licence réseau pendant le parcours.
- L'image worker contient ses dépendances PHP/PDO/MySQL, ses éventuels outils CLI WordPress propres, un importeur indépendant de WordPress, les archives Novamira neuves approuvées et le serveur PHP-FPM décrit ci-dessous. Un ID immuable n'établit pas à lui seul la confiance : Ced doit approuver la provenance et le contenu.
- L'entrypoint habituel de l'image est toujours contourné avant publication. Seuls des exécutables de confiance sont exécutés ; aucun serveur PHP-FPM/Apache/nginx ni bootstrap du WordPress importé pendant import/neutralisation/anonymisation.
- Le worker et MariaDB utilisent `network_mode: none` dès leur création. La base écoute uniquement sur son socket Unix. Aucun réseau bridge, réseau partagé, port publié, socket Docker, socket hôte général ou montage du répertoire complet d'un site existant.
- L'archive d'origine est un montage **fichier unique, lecture seule**, uniquement pour l'importeur. Les étapes suivantes ne la voient pas. Le dépôt complet n'est jamais monté : seulement `wp/outils/staging/` et `wp/outils/bascule/`, approuvés et en lecture seule. Les dépendances applicatives de ces scripts doivent se trouver dans ces dossiers ou dans l'image de confiance.
- Le code importé est une donnée. Ne jamais inclure son `wp-config.php`, `.user.ini`, core, MU-plugins, drop-ins, thèmes, plugins ou hooks pour réaliser les trois premières opérations. Un simple `wp --skip-plugins --skip-themes` n'est pas une isolation suffisante. Les interrogations SQL et transformations PHP doivent être réalisées par du code de confiance ; un éventuel test des hooks utilise un harness/core/plugins de confiance, pas un bootstrap aveugle du site importé.

## Invocation

Un processus CLI isolé neuf par étape, arrêté à la première erreur :

| Étape | Exécutable absolu dans le worker |
|---|---|
| import | `/opt/staging/importer --request-stdin` |
| neutralisation | `/opt/staging/neutraliser --request-stdin` |
| anonymisation | `/opt/staging/anonymiser --request-stdin` |
| vérification | `/opt/staging/verifier --request-stdin` |
| bascule | `/opt/staging/bascule --request-stdin` |
| Novamira neuf | `/opt/staging/novamira --request-stdin` |

Les adaptateurs appartiennent à l'image de confiance. Pour les trois scripts de données, ils appellent PHP sur `/workflow/wp/outils/staging/<phase> --worker-bridge /opt/staging/worker-bridge.php` : les lanceurs PHP natifs ne prennent pas `--request-stdin`. La requête passe par pipe anonyme ; seul le mot de passe administrateur utilise stdin de `anonymiser`. Aucun bootstrap du WordPress importé avant nettoyage. La bascule reste indépendante de Novamira.

Chaque invocation reçoit **un objet JSON sur stdin**, aucune commande shell construite, aucune donnée sensible dans les arguments ou l'environnement :

```json
{
  "protocol": "staging-offline-v1",
  "stage": "anonymiser",
  "slug": "fixture-synthetique",
  "environment": "staging",
  "production_url": "https://production.invalid",
  "production_hosts": ["production.invalid"],
  "table_decisions": {},
  "staging_url": "http://staging.invalid:8099",
  "wordpress_path": "/var/www/html",
  "archive": "/input/source.wpress",
  "database": {
    "host": "localhost",
    "socket": "/run/mysqld/mysqld.sock",
    "name": "wordpress_staging",
    "user": "wp",
    "password": "<fourni-en-memoire>"
  },
  "admin": {"login": "imagine-test-admin", "password": "<fourni-en-memoire>"}
}
```

`admin` n'est transmis **qu'à anonymiser**. Le mot de passe administrateur n'est pas enregistré dans le modèle du tableau de bord, le manifeste Compose, le rapport ou un journal. Les identifiants techniques de la base jetable sont stockés comme les autres profils dans la base privée du tableau de bord et le manifeste privé hors dépôt ; ce ne sont jamais des identifiants de production. Ne pas enregistrer stdin, exceptions PDO complètes ou sorties SQL.

Les chemins d'archive et de dépôt doivent être visibles **au même emplacement absolu depuis le processus opérateur et le daemon Docker**. `SITES_DIR` désigne le chemin vu par le processus, `HOST_SITES_DIR` dérive de `HOST_PROJECT_DIR` et désigne le chemin vu par Docker. Le patch n'essaie pas de deviner ces correspondances. Ne pas utiliser un dépôt contenant des secrets dans les deux dossiers de scripts montés.

## Devoirs de l'importeur de confiance

- Attendre la base propre et importer hors ligne sans appeler WordPress, ses extensions ou `wp ai1wm restore`.
- Décoder `.wpress` avec un outil approuvé, borné et testé ; refuser traversées de chemins, symlinks/hardlinks, fichiers spéciaux et volumes expansés déraisonnables. Ne jamais exécuter un fichier contenu dans l'archive.
- Déduire/valider le préfixe SQL depuis les données, pas par inclusion de configuration importée. La requête ne suppose pas `wp_`.
- Écrire la copie uniquement dans `/var/www/html` et la nouvelle base. Ne pas recopier l'archive brute, dumps SQL, sauvegardes embarquées ou fichiers de configuration avec secrets dans une zone ultérieurement exposée au web/agent. Les logs et sauvegardes de la source ne deviennent jamais des fichiers publics.
- Générer une configuration de staging propre, sans configuration PHP importée ni identifiants externes ; `WP_ENVIRONMENT_TYPE=staging`, cron/updater désactivés. Avant de passer aux scripts qui refusent une URL de production, réécrire `home`/`siteurl` par SQL de confiance vers la destination de staging, sans bootstrap du site. Conserver l'URL de production uniquement pour les contrôles en mémoire nécessaires aux scripts.
- Aucun repli réseau si un format, une dépendance, une licence ou un plugin manque.

## Devoirs des scripts de données

Ils doivent vérifier simultanément le marqueur staging de confiance, la destination effective et la configuration/URL en base. Refuser une adresse de production ou un environnement `production`, même avec les arguments staging. Ne pas se contenter de croire l'objet JSON. Prendre en charge toutes les tables/préfixes réels sans les connaître à l'avance. Aucune donnée personnelle dans stdout/stderr/rapport.

L'orchestrateur exige la séquence :

```text
importer → neutraliser → anonymiser → verifier
→ [WP >= 6.9 obligatoire] → bascule/lancer → verifier
→ Novamira neuf/actif → verifier → état verified
```

Le premier `verifier` autorise le lancement de la bascule et l'étape Novamira, **pas encore l'accès web/agent**. Toute régression de bascule ou de l'installation ferme la publication. L'absence de scripts numérotés dans la bascule est un succès valide du lanceur, pas une raison de le sauter.

## Réponse, erreurs et rapports

Succès : code de sortie zéro, stdout = **un objet JSON uniquement**, au plus 16 Kio, sans texte PHP/notice avant ou après :

```json
{"protocol":"staging-offline-v1","stage":"neutraliser","ok":true}
```

Une vérification doit aussi renvoyer une version stable WordPress strictement numérique et **tous** ces booléens vrais :

```json
{
  "protocol":"staging-offline-v1", "stage":"verifier", "ok":true,
  "wordpress_version":"6.9.1",
  "checks": {
    "emails":true, "service_keys":true, "payment_ids":true,
    "mail_blocked":true, "subscriptions_staging":true, "unknown_tables_resolved":true,
    "production_refused":true, "imported_code_not_loaded":true
  }
}
```

`imported_code_not_loaded` atteste que le contrôle lui-même n'a pas exécuté le bootstrap non approuvé de la copie. `mail_blocked` nécessite un test effectif. Le vérificateur natif décide si Subscriptions est présent ; son absence n'est pas un échec de mode staging, ni une preuve d'acceptance du produit payant. S'il est présent, un contrôle effectif du mode est obligatoire. Les tables personnelles inconnues doivent être tranchées. Une version WordPress inférieure à 6.9, inconnue ou pré-release bloque la suite ; les minima effectifs des plugins sont également requis, sans mise à niveau implicite. Le ZIP Subscriptions 9.4.1 fourni exige WP 7.0 et WooCommerce 11.1.

L'installateur Novamira doit supprimer/remplacer, **dans la seule copie**, tout code Novamira/Pro importé par les archives neuves approuvées de l'image, puis activer et contrôler ces nouvelles copies, sans réutiliser l'identité MCP ni un mot de passe applicatif importé. Il renvoie :

```json
{"protocol":"staging-offline-v1","stage":"novamira","ok":true,"fresh":true,"active":true}
```

Ces attestations doivent être implémentées et testées par le worker ; ce ne sont pas des résultats réels que l'orchestrateur prétend avoir produits. Le script `verifier` doit couvrir aussi les identités MCP héritées s'il veut garantir leur suppression. Un échec : code non nul ou `ok:false`. Le wrapper natif peut recueillir le JSON négatif d'un vérificateur non nul ; il le traduit en réponse de protocole `ok:false`, sans créditer la phase. Seuls les booléens, tags et métadonnées de schéma validées sont exposés. stderr et messages SQL bruts sont abandonnés. Aucun `ok:false` ne devient un succès parce que l'adaptateur a pu fournir un objet JSON valide.

L'orchestrateur conserve des rapports **filtrés**, hors dépôt, et `failure.json` : étape, raison fixe, booléens, tags et métadonnées de schéma sans valeurs. La liste des tables contient nom, colonnes, nombre de lignes, colonnes personnelles et décision ; elle n'est pas tronquée silencieusement. Les autres données restent exclues. Le GET metadata et le CLI incluent `verification_report`, même lors d'un échec après création de leur propre copie ; logs/export/admin et routes futures restent verrouillés avant `verified`. Le transport refuse au-delà de 16 Kio, sans transformer ce refus en succès.

## Serveur post-vérification

`/opt/staging/serve` n'est utilisé qu'après succès complet. Il doit lancer PHP-FPM sur `/run/staging-fpm/php.sock`, accessible à nginx ; le docroot est `/var/www/html`, la base reste accessible par socket Unix. Il ne doit pas changer le contenu vérifié ni télécharger de dépendance. Le processus WordPress reste sans réseau. nginx est seul sur un réseau interne nouvellement créé, et seul son port web est publié **après vérification et demande explicite `--start`**. Pas de redémarrage automatique (`restart: no`).

L'accès Novamira reste soumis à `verification_state=verified` dans l'API, le client MCP, le REST et les commandes WordPress. Le provisionnement d'une identité MCP neuve est une opération post-vérification ; l'installation seule ne crée pas d'identifiants MCP dans le tableau de bord. Les personnes qui disposent de root, du socket Docker ou d'un shell arbitraire sur l'hôte peuvent évidemment contourner l'outil : cette interface n'est pas un confinement de l'administrateur de la machine.
