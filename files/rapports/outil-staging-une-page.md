# Staging WordPress — fiche pratique Imagine

**Où ?** L’outil tourne dans Docker sous WSL Ubuntu, dans `/home/ced/staging-wp`. Dashboard : `http://192.168.129.32:7000/`. Imagine : `http://192.168.129.32:8081/` ; administration : `/wp-admin/`. Les fichiers du site sont accessibles depuis Windows dans `\\wsl.localhost\Ubuntu\home\ced\staging-wp\sites\imagine`. Ce n’est pas le dépôt Git.

**Créer une copie de production.** Exporter le site source en `.wpress` avec All-in-One WP Migration, puis utiliser l’import `.wpress` du dashboard. L’outil crée une cible distincte et restaure la base et les fichiers inclus dans l’archive (extensions, thèmes, médias selon les exclusions de l’export). Le site a sa propre base MariaDB, son dossier `wp-content` et son volume de cœur WordPress. Le tableau de bord réassigne `home` et `siteurl` à la cible. Vérifier la version du cœur : l’import Imagine a laissé un cœur 6.1.1 pour une sauvegarde en 6.9.1. Ne pas confondre l’import avec le clonage d’un staging existant.

**Commandes agent depuis Windows.** Pas besoin de SSH : utiliser WSL puis Docker. Le service SSH Ubuntu était inactif au contrôle. WP-CLI et PHP sont dans le conteneur ; Composer n’a pas été trouvé dans les environnements inspectés.

    wsl -d Ubuntu -- docker exec -u www-data wp-imagine wp core version
    wsl -d Ubuntu -- docker exec wp-imagine php -v

**Que neutralise l’import ?** Ne pas confondre copie locale et coupure des services réels. Aucune neutralisation générale constatée des adresses email, des envois, des clés d’API, des passerelles de paiement ou des webhooks. La sortie réseau n’est pas bloquée. Sur Imagine, `DISABLE_WP_CRON=1` empêche le déclenchement automatique de WP-Cron par les visites, sans supprimer les tâches importées ni exclure un déclenchement externe. `blog_public=1` : WordPress ne demande pas aux moteurs de décourager l’indexation. Avant tout test de commande ou d’abonnement, vérifier les destinataires, les clés, le mode test des paiements et les tâches différées.

**Contrôle du 19 novembre 2026.** WordPress 6.9.1, PHP-FPM 8.5.10, formulaire de connexion accessible. Le contrôle automatique du changement de PHP n’accorde que trois secondes à chaque tentative HTTP : en cas de délai dépassé, vérifier séparément le moteur PHP, la connexion WordPress et l’état du dashboard.
