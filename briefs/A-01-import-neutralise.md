# Lot A-01 — Import neutralisé et anonymisé de la production

**Chantier** : A · l'existant.
**Nature** : scripts et tests. **Tu ne touches jamais à la sauvegarde réelle** : tu écris l'outil, Ced le lance.
**Emplacement** : `wp/outils/existant/`.
**Livrables** : les scripts, leur test sur une base fictive, `wp/outils/existant/README.md`, `production/A-01/notes.md`, puis `production/A-01/PRET`.

## Pourquoi

Décision de Ced (11/11) : on repart de la production. Le site actuel est copié dans le staging Docker, mis à niveau, puis reçoit le nouveau thème et le code sur mesure. Cette copie contient de vrais abonnés, de vrais mandats Stripe et de vraies clés. Avant qu'un agent ou un test y touche, elle doit être rendue inoffensive : aucun paiement, aucun email, aucune synchronisation ne doit pouvoir partir vers une vraie personne, et les données personnelles doivent être remplacées.

L'import sera rejoué plusieurs fois, et une dernière fois le jour de la bascule : il doit être **rejouable à l'identique en une commande**.

## Ce que Ced fournira (hors dépôt)

Un dossier sur le NUC, **en dehors du dépôt Git**, dont le chemin est passé en paramètre : une exportation SQL de la base et le dossier `wp-content` de la production. Tu n'y as pas accès et tu n'en as pas besoin.

## Ce que l'outil doit faire, dans cet ordre

1. **Monter le site** dans Docker à partir du dossier fourni : base importée, `wp-content` de la production, WordPress dans la version de la production. Proposer un fichier `docker-compose.existant.yml` dans `wp/outils/existant/`, qui complète celui de la racine sans le modifier.
2. **Neutraliser, avant le premier démarrage de WordPress** (donc par SQL ou par un `mu-plugin` déposé avant le lancement) :
   - envoi d'emails bloqué pour tout le site (filtre `pre_wp_mail`), y compris ceux de WooCommerce ;
   - passerelles de paiement : clés réelles supprimées de la base ; Stripe et PayPal désactivés ou basculés en mode test sans clé ;
   - identifiants de client et de moyen de paiement Stripe et PayPal retirés des comptes, commandes et abonnements, pour qu'aucun prélèvement réel ne soit techniquement possible ;
   - renouvellements automatiques : vérifier que WooCommerce Subscriptions passe bien en mode « staging » au changement d'adresse du site, et le forcer si ce n'est pas le cas ;
   - clés et jetons de tous les services tiers supprimés (Brevo, SMTP, sauvegarde, sécurité, statistiques, webhooks sortants) ;
   - actions planifiées en attente qui appellent l'extérieur annulées ;
   - `WP_ENVIRONMENT_TYPE` à `local`, indexation par les moteurs découragée, adresse du site réécrite vers `http://localhost:8080`.
3. **Anonymiser** les données personnelles :
   - comptes : identifiant, email (`abonne-<id>@example.org`), nom, prénom, nom affiché ; mots de passe remplacés ; sessions supprimées ;
   - adresses de facturation et de livraison, téléphone, numéro d'entreprise : dans les métadonnées des comptes, les commandes, les abonnements (tables classiques et tables HPOS si elles existent) ;
   - commentaires, notes de commande, formulaires enregistrés, journaux qui contiennent des emails ou des adresses IP ;
   - garder ce qui sert aux tests : le pays, le code postal remplacé par un code valide du même pays, les statuts, les dates, les montants, les produits, le moyen de paiement utilisé.
   - un compte administrateur de test créé, avec un mot de passe passé en paramètre (jamais écrit dans le dépôt).
4. **Vérifier** et produire un rapport : aucun email hors `@example.org`, aucune clé de service restante (recherche de motifs `sk_live`, `pk_live`, `rk_live`, `xkeysib-` et équivalents), aucun identifiant Stripe (`cus_`, `pm_`, `src_`, `seti_`) restant, envoi d'email effectivement bloqué. **Si une vérification échoue, le site n'est pas démarré** et le rapport dit pourquoi.

## Comment tu le testes sans données réelles

Construis dans Docker une base fictive : WordPress et WooCommerce (gratuits) installés par WP-CLI, une trentaine de comptes, de commandes et de métadonnées inventés, dont des lignes piégées (une fausse clé `sk_live_…` dans une option, un faux `cus_…` dans une métadonnée, un email dans une note de commande). Les tests prouvent que l'outil les neutralise et que la vérification échoue quand on en laisse une.

Subscriptions et Memberships sont payants et ne sont pas disponibles pour ce test : écris les traitements qui les concernent d'après leur documentation officielle, cite les tables et métadonnées visées avec leur source, et liste dans `notes.md` ce qui n'a pas pu être testé.

## Exigences

- Une seule commande pour Ced, documentée dans le `README.md`, lancée depuis PowerShell, qui s'exécute dans Docker.
- Rejouable : relancer l'outil repart d'une base propre et donne le même résultat.
- Aucune requête vers l'extérieur pendant l'import.
- Aucun chemin, nom ou identifiant réel dans le dépôt.

## Ce que tu ne décides pas

Liste dans `notes.md`, sous « À arbitrer par Ced » :

- toute table ou extension que tu soupçonnes de contenir des données personnelles sans pouvoir le vérifier ;
- le sort des fichiers déposés par les utilisateurs dans `wp-content/uploads` (factures, justificatifs éventuels).
