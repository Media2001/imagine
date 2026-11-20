# Intégration « site à abonnements » dans l'outil de staging

**Livraison : patch applicable, testé en copie isolée. Non déployé. Aucun staging réel créé.**

## Constat préalable sur les seuls sources de l'outil

- `api/orchestrator.py::_do_import_wpress` démarre l'ensemble Compose (WordPress/FPM + nginx et port web), installe un WordPress vide et ai1wm, puis restaure l'archive dans cette pile déjà démarrée. Il réécrit ensuite `home` et `siteurl` avec des erreurs tolérées. Ce chemin n'est pas utilisable pour une copie à abonnements non nettoyée.
- `api/templates/docker-compose.wp.yml.j2` désactive WP-Cron, l'updater automatique et l'édition de fichiers ; l'environnement est `local`. Le réseau de site n'est pas isolé de la sortie réseau et nginx rejoint le réseau partagé.
- `--skip-email` concerne seulement l'installation initiale : aucun blocage global de l'email n'est posé par cet importeur. Pas de suppression des clés, moyens de paiement, identifiants tiers ou actions planifiées ; pas d'anonymisation, de contrôle Subscriptions, d'étape de vérification ou de verrou agent propre à ce profil. Pas de découragement explicite de l'indexation dans ce parcours.
- Novamira est ajouté aux créations par template ; l'import `.wpress` ne comporte pas le nouveau parcours vérifié/Novamira neuf demandé.

Constat par lecture de code seulement : aucun conteneur, site, log, base, secret ou sauvegarde réelle n'a été inspecté.

## Contenu du patch

- Profil `subscriptions` / template import-only `import-subscriptions` ; l'ancienne création par template refuse ce profil.
- Colonne persistante `verification_state`, indépendante du statut runtime : `quarantined` avant réussite de l'import, `imported` après, `verified` uniquement à l'issue complète. Un simple changement de `status` en `running` ou `verified` n'ouvre rien.
- Base neuve et workers sans réseau dès leur création ; aucun service web dans le manifeste pré-vérification, aucune utilisation des entrypoints WordPress historiques ni du réseau partagé. Images locales par ID immuable et `pull=never`.
- Ordre : importeur de confiance → neutraliser → anonymiser → vérifier → seuil WP 6.9 → bascule → revérifier → Novamira neuf → revérifier. Le manifeste web n'est écrit qu'à la fin ; son démarrage exige ensuite l'état vérifié et une demande explicite.
- Gardes API/ASGI, fonctions d'orchestration, client MCP et REST, accès aux thèmes/admins, magic login, exports/downloads, mutation PHP/clone, adoption MCP et maintenance Unlimited. Une fonction recevant un dictionnaire périmé relit aussi l'état persistant.
- En quarantaine, metadata et rapport filtré restent visibles ; URLs web/admin et indicateurs MCP sont masqués. Les routes autres que la metadata, même futures, sont fermées. Clone, changement PHP, destruction et import historique sont refusés pour ce profil même vérifié : il faut une nouvelle copie fraîche et le parcours hors ligne.
- Les autres profils gardent leurs templates et leur parcours historique. Ajouts de schéma/réponse rétrocompatibles ; test de parité du transport `_wp` pour un autre profil. Pas de prétention à une non-régression E2E de tous les profils.

Voir `CONTRAT-HORS-LIGNE.md` pour stdin JSON, réponses attendues, montages, responsabilités des scripts et devoirs précis du worker.

## Appliquer et tester sans toucher au service partagé

Les variables ci-dessous sont des chemins/opérandes fournis par Ced. Aucun chemin réel ou secret n'est livré.

```sh
# Vérifier le patch sur une copie SOURCE de l'outil (aucune donnée de site).
python3 "$INTEGRATION/apply.py" "$COPIE_OUTIL"
python3 "$INTEGRATION/apply.py" "$COPIE_OUTIL" --apply

# Reproduction complète : lit seulement une whitelist des sources, crée sa copie,
# applique le patch et lance UNIQUEMENT les tests synthétiques livrés.
python3 "$INTEGRATION/test_isolated.py" \
  --tool-source "$OUTIL_SOURCE" --scratch "$DOSSIER_JETABLE"
```

`apply.py` vérifie toutes les préimages avant écriture, refuse une cible déjà patchée et sauvegarde les sources modifiées en `.pre-subscriptions`. Pas de Git, migration de la base réelle, Compose, téléchargement, installation ou redémarrage. Ne pas lancer `unittest discover` sur l'outil d'origine : sa suite contient des tests qui ciblent des sites réels.

**Avant une adoption opérationnelle**, Ced doit faire charger le patch par tous les processus API/MCP qui ont accès à la base du tableau de bord. Modifier les fichiers sans mettre à jour les processus existants ne protège pas leurs anciennes routes. Aucun redémarrage partagé n'a été effectué ou automatisé dans cette livraison.

## Commande opérateur unique — après adoption et qualification des prérequis

Dans l'environnement de l'outil, les valeurs `DB_PATH`, `SITES_DIR`, `HOST_PROJECT_DIR`, `NAS_HOST` et les chemins du dépôt/archive doivent déjà correspondre à la bonne instance. Le code ne les devine pas. L'URL cible est `http://NAS_HOST:PORT`; la production doit avoir un autre hôte. Le port doit être réservé par Ced ; l'outil refuse un port déjà enregistré et Docker refusera une collision externe lors de la publication.

```sh
cd "$OUTIL_ADOPTE"
python3 -m api.subscription_operator \
  --name imagine \
  --archive "$ARCHIVE_APPROUVEE" \
  --workflow "$DEPOT_SCRIPTS_APPROUVE" \
  --production-url "$URL_PRODUCTION" \
  --port "$PORT_STAGING" \
  --worker-image "$IMAGE_WORKER_SHA256" \
  --db-image "$IMAGE_MARIADB_SHA256" \
  --nginx-image "$IMAGE_NGINX_SHA256" \
  --start
```

Le mot de passe administrateur est demandé dans le terminal privé, jamais dans argv ou le journal. Pour une automatisation maîtrisée, `--password-fd N` lit une ligne d'un descripteur privé fourni par Ced. Sans `--start`, la commande s'arrête après vérification complète, sans publication web. Un échec ne lance jamais le parcours historique en secours ; la copie et ses rapports restent pour diagnostic, sans destruction. Une relance utilise un **nouveau nom/copie fraîche** : jamais de réimport en place d'un site déjà exposé.

Le provisionnement d'identifiants MCP neufs reste une opération post-vérification (`mcp-adopt`), après validation du serveur runtime de confiance. Il n'est pas présenté comme déjà effectué.

## Vérifications réellement exécutées

Résultat versionné : `test-results.json`. Suite `api.test_subscriptions` appliquée sur une copie isolée des sources : **22 tests, 0 échec, 0 erreur, 0 ignoré**. Hashes des fichiers sources sélectionnés inchangés après le test.

Tests : séquence complète, rapport incomplet refusé, WP 6.8 refusé, échec import/vérification/bascule et régression de la vérification finale, état persistant, absence de web dans tous les appels pré-vérification, arguments réseau/ports du worker, absence de secret admin dans argv et sortie opérateur, montages restreints et archive visible au seul importeur, gardes API et entrées directes (dont kwargs et dictionnaire périmé), URLs masquées, parité de transport d'un autre profil.

## Limites exactes / bloquants avant tout import réel

1. **Pas d'image worker approuvée fournie ici.** Ses exécutables `/opt/staging/importer`, `/opt/staging/novamira`, `/opt/staging/serve`, ses dépendances et archives Novamira doivent être réalisés/qualifiés selon le contrat. Le patch est fonctionnel au niveau orchestration, mais ce n'est pas un importeur `.wpress` autonome prêt pour une sauvegarde réelle.
2. Les scripts de données aux quatre coordonnées convenues sont des dépendances, pas réécrits dans ce lot. Leur interface doit implémenter ce contrat ou être adaptée par des wrappers de confiance. Aucun de leurs effets métier n'a été validé par ces tests.
3. Le transport Docker est **doublé dans les tests**. Aucun conteneur réel, socket MariaDB, PHP-FPM/nginx, plugin Novamira, WordPress/WooCommerce, Subscriptions/Memberships payants ou traitement réel d'archive n'a été exercé. Les rapports positifs des fixtures ne sont pas des attestations de ces produits. Une recette Docker/WP synthétique est obligatoire avant GO.
4. FastAPI/httpx/MCP ne sont pas installés dans l'environnement Python WSL disponible. Le middleware ASGI est exécuté directement et la vraie fonction de sérialisation API est extraite/compilée pour son test ; ce n'est pas un test HTTP complet du serveur FastAPI. Aucun paquet n'a été installé pour contourner cette limite.
5. La garantie s'applique aux lignes explicitement créées avec le profil `subscriptions`. Pour ne pas modifier les autres profils, l'importeur historique `imported` demeure disponible pour eux : il n'est pas possible de reconnaître une archive à abonnements sans la lire. **Ne jamais importer Imagine sous un autre profil**. La classification est une obligation opérateur, non une détection magique.
6. Les sorties brutes d'erreur sont volontairement abandonnées pour éviter toute fuite ; seuls les rapports filtrés et raisons fixes sont accessibles. Timeout : un arrêt ciblé du CID worker est tenté ; si Docker est indisponible, un worker peut subsister, toujours sans réseau/port web. Il n'est pas détruit par un nettoyage global.
7. Le patch n'est **pas actif sur l'instance partagée**. Aucun site réel n'a été créé, consulté ou modifié ; aucun secret lu, aucune opération Git, aucune installation hôte, aucun redémarrage partagé ou destruction effectué.
