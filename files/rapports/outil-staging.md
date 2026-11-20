# Outil staging WordPress — fiche technique

**Inspection : 19 novembre 2026, vers 19 h UTC.** Source réelle : `/home/ced/staging-wp`, WSL Ubuntu. Audit en lecture seule : lecture du code, inspections Docker, versions et `GET /api/health` ; aucune création, restauration, modification de site, connexion administrateur ou réparation exécutée. Seule cette fiche est créée hors staging. Aucun secret, identifiant client, domaine privé ou contenu de base n’est reproduit.

## Architecture et dépendances

Le dashboard associe **React 18 / Vite 5 / Tailwind 3**, une API **FastAPI**, SQLite et un orchestrateur Docker. Son build utilise Node 20 puis Python 3.12 ; Node n’est pas nécessaire dans l’image finale. Le dashboard monte le socket Docker, les dossiers `sites` et `data` en écriture, `api`, `plugins` et `wp-image` en lecture seule. `HOST_PROJECT_DIR` doit désigner le chemin réel côté daemon ; sa valeur effective correspond ici au dépôt WSL, contrairement aux exemples NAS du README.

**Constaté :** dashboard actif, `/api/health` répond HTTP 200 ; publication du port 7000 sur toutes les interfaces IPv4/IPv6. WSL fournit Docker **29.6.2**, Compose **5.3.1**, Python **3.14.4** et OpenSSH **10.2p1**. Les dépendances Python installées dans le dashboard correspondent à `api/requirements.txt` : FastAPI 0.115.12, MCP 2.1.1, Uvicorn 0.32.0, Jinja2 3.1.4, Pydantic 2.12.5, HTTPX 0.27.2, aiofiles 24.1.0, python-multipart 0.0.12. Les imports MCP attendus fonctionnent.

## Création, import et clonage

- **Création** — `POST /api/sites` valide template et PHP, réserve un slug/port dans SQLite, puis provisionne en tâche de fond. L’image WordPress est construite à la demande ; chaque site reçoit PHP-FPM, nginx 1.27 Alpine et MariaDB 11. WP-CLI installe le cœur, le thème et les extensions du template ; les ZIP premium sont partagés en lecture seule. Le catalogue contient six templates : minimal, Crocoblock, Novamira/ACF, Elementor, stack complet, WooCommerce. Des installations premium utilisent `check=False` : le statut « running » ne garantit pas leur réussite intégrale.
- **Import** — `POST /api/sites/import-wpress` reçoit l’archive par blocs de 1 Mio dans `data/uploads`, crée une cible distincte, installe All-in-One WP Migration et Unlimited Extension, valide le ZIP Unlimited et sa compatibilité, puis exécute `wp ai1wm restore … --yes`. `home` et `siteurl` sont réassignées ; l’upload temporaire est supprimé, la copie dans `ai1wm-backups` reste. La route ne fixe pas de quota applicatif explicite. Les limites nginx/PHP du site ne constituent pas la limite de cet upload au dashboard.
- **Clone** — export SQL temporaire dans le `wp-content` source, copie des fichiers, import dans une nouvelle base et remplacement de l’URL hors colonne `guid`. **Ce parcours écrit temporairement sur la source** ; il ne convient pas à une référence strictement immuable. La route accepte une source arrêtée mais ne la redémarre pas avant le dump.

## Isolation et accès agent

Chaque site possède réseau `site-net-{slug}`, base, `wp-content` et volume de cœur distincts ; seul nginx publie son port, choisi dans la plage configurée **8081–8200**. nginx rejoint aussi le réseau commun `staging-net`. **Ce n’est pas un bac à sable de sécurité** : sortie réseau non bloquée, réseau frontal partagé, socket Docker privilégié et permissions initiales de certains dossiers en `0777`. Aucun verrouillage global des mails, paiements/webhooks, accès Internet ou indexation n’apparaît dans le provisioning ; les intégrations importées doivent être contrôlées séparément.

Le serveur **MCP `/mcp`** route explicitement par `site_slug` : inventaire, découverte/contrat/exécution d’abilities Novamira, pages et fichiers du thème. Les écritures de pages/fichiers requièrent `confirmed=True` ; l’exécution d’abilities n’a pas ce garde générique. Les mots de passe applicatifs restent côté serveur. La création sur template provisionne Novamira ; **import et clone ne provisionnent pas automatiquement leur MCP** dans les fonctions inspectées. L’adoption MCP est une action mutante distincte. Même la lecture de thème utilise un wrapper qui journalise en SQLite : ne pas l’invoquer pour un audit strict sans écriture.

**Sécurité :** aucune authentification du dashboard/API/MCP n’est définie dans les fichiers inspectés ; un éventuel contrôle externe n’a pas été vérifié. Les liaisons WordPress utilisent HTTP. L’API peut générer un accès administrateur à usage unique valable cinq minutes : réserver le dashboard à un périmètre de confiance. Le verrou `MutationGuard` sérialise les mutations `/api/`, mais ne couvre pas génériquement `/mcp`.

## SSH, WP-CLI, Composer et PHP

**SSH** n’est pas utilisé par l’orchestrateur : administration locale via `wsl.exe` puis Docker. Le client existe dans Ubuntu, le service `ssh` est inactif ; aucun client SSH n’est présent dans le dashboard. Le push différentiel SSH apparaît seulement comme projet futur dans le README.

**WP-CLI** est téléchargé en PHAR dans l’image WordPress, puis lancé par `docker exec --user www-data wp-{slug} wp …`. Version observée : **2.12.0**. **Composer** n’est ni installé par les Dockerfiles ni utilisé par le provisioning ; aucun exécutable trouvé dans WSL, le dashboard ou les conteneurs PHP échantillonnés. PHP/WP-CLI ne sont pas requis sur l’hôte.

**PHP** : catalogue applicatif 7.3 à 8.5, défaut 8.3 ; disponibilité catalogue ≠ compatibilité du site. Échantillons réellement interrogés : **8.2.32, 8.3.32, 8.4.23, 8.5.10**. Le changement de version recrée seulement le service WP, conserve les données et attend la disponibilité ; aucun rollback automatique n’apparaît. Le template génère PHP upload/post 64M et mémoire 256M, nginx accepte 256M ; les réglages existants peuvent différer. Les tags d’images et le téléchargement WP-CLI ne sont pas figés par digest/version.

**Limite :** aucun parcours de création/import/swap ni test de contenu n’a été exécuté. L’environnement évoluait pendant le relevé ; les versions sont des observations ponctuelles, pas un inventaire figé. Réparations et validations fonctionnelles restent au parent.

**Preuves locales :** `Dockerfile`, `docker-compose.yml`, `wp-image/Dockerfile` ; `api/{config,main,models,orchestrator,mcp_proxy,mcp_client,site_management,unlimited_extension}.py` ; `api/requirements.txt` ; `api/templates/{docker-compose.wp.yml.j2,nginx.conf.j2,templates.json,php_versions.json}` ; `ui/package.json`. Références de parcours : `orchestrator.py:493–623` (création), `735–893` (clone/import), `660–685` (PHP), `main.py:16–30` et `mcp_proxy.py` (accès agent). Le README est historique et ne fait pas foi sur les versions ni l’architecture nginx actuelle.
