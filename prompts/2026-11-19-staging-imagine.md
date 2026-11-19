# Prompt — staging d'Imagine dans l'outil de staging (19/11/2026)

À donner à Claude Code, sur la machine où tourne l'outil de staging de Ced.

---

Tu travailles sur mon outil de staging WordPress. Je démarre un projet client, Imagine : un magazine vendu par abonnement (WooCommerce, WooCommerce Subscriptions, WooCommerce Memberships, Stripe, PayPal, Brevo). On repart d'une copie du site de production, qu'on met à niveau, et on rejouera la même opération sur la vraie base le jour de la mise en ligne.

Le dépôt du projet est `Media2001/imagine` (cloné dans `C:\Users\Ced\imagine`). Lis d'abord `README.md`, `doctrine/doctrine.md` et `docs/decisions.md`.

## Ce que je te demande

Ajouter à l'outil de staging une étape « site à abonnements », qui s'exécute **après l'import de la base et des fichiers, et avant le premier démarrage de WordPress**. Elle enchaîne trois scripts, puis installe Novamira si tout est bon.

Les scripts vivent dans le dépôt Imagine, pas dans l'outil, pour être versionnés et relus :

- `wp/outils/staging/` : ce qui ne tourne **que** sur une copie de travail.
- `wp/outils/bascule/` : ce qui sera rejoué sur la vraie production le jour J.

### 1. `wp/outils/staging/neutraliser` — obligatoire

Après ce script, la copie ne peut plus rien déclencher chez une vraie personne :

- envoi d'emails bloqué pour tout le site (filtre `pre_wp_mail` dans un `mu-plugin`), WooCommerce compris ;
- clés réelles de Stripe et de PayPal supprimées de la base ; passerelles désactivées ou en mode test sans clé ;
- identifiants de client et de moyen de paiement (Stripe : `cus_`, `pm_`, `src_`, `seti_` ; PayPal : jetons de facturation) retirés des comptes, des commandes et des abonnements, pour qu'aucun prélèvement réel ne soit techniquement possible ;
- WooCommerce Subscriptions en mode « staging » (renouvellements automatiques coupés), forcé si le changement d'adresse ne le déclenche pas ;
- clés et jetons de tous les services tiers supprimés : Brevo, SMTP, sauvegarde, sécurité, statistiques, webhooks sortants ;
- actions planifiées en attente qui appellent l'extérieur annulées ;
- `WP_ENVIRONMENT_TYPE` à `staging`, indexation découragée, adresse du site réécrite.

### 2. `wp/outils/staging/anonymiser`

- comptes : identifiant, email (`abonne-<id>@example.org`), nom, prénom, nom affiché ; mots de passe remplacés ; sessions supprimées ;
- adresses de facturation et de livraison, téléphone, numéro d'entreprise : métadonnées des comptes, commandes et abonnements (tables classiques et tables HPOS si elles existent) ;
- commentaires, notes de commande, formulaires enregistrés, journaux contenant des emails ou des adresses IP ;
- à conserver, parce que les tests en ont besoin : pays, statuts, dates, montants, produits, moyen de paiement utilisé ;
- un compte administrateur de test, dont le mot de passe est passé en paramètre et n'est écrit nulle part.

### 3. `wp/outils/staging/verifier`

Produit un rapport et renvoie un code d'erreur si l'un de ces points échoue :

- aucun email hors `@example.org` dans les comptes, commandes et abonnements ;
- aucune clé de service restante (motifs `sk_live`, `pk_live`, `rk_live`, `whsec_`, `xkeysib-` et équivalents), dans toute la base ;
- aucun identifiant Stripe ou PayPal restant ;
- envoi d'email effectivement bloqué ;
- mode staging de Subscriptions actif.

**Si la vérification échoue, le site ne démarre pas** et l'outil affiche le rapport.

### 4. Novamira

Installé et activé **seulement si la vérification a réussi**. Novamira demande WordPress 6.9 ou plus : si la copie est en dessous, ne l'installe pas, dis-le dans le rapport et arrête-toi là.

### 5. `wp/outils/bascule/`

Pour l'instant : un `README.md` qui explique le principe, et un lanceur qui exécute dans l'ordre les scripts numérotés du dossier (`010-…`, `020-…`), s'arrête à la première erreur et écrit un journal. Chaque script doit pouvoir être relancé sans dégât. L'outil de staging appelle ce lanceur après l'étape 3. Le dossier est vide aujourd'hui : les scripts arriveront lot par lot.

## Règles

- **Tu n'ouvres jamais la sauvegarde réelle d'Imagine** : ni la base, ni les exports, ni les journaux qui en sortent. Tu écris les scripts à l'aveugle et tu les testes sur un site jetable que tu construis toi-même (WordPress + WooCommerce, une trentaine de comptes et de commandes inventés, avec des lignes piégées : une fausse clé `sk_live_…` dans une option, un faux `cus_…` dans une métadonnée, un email dans une note de commande). Le test doit prouver que les pièges sont neutralisés, et que la vérification échoue quand on en laisse un.
- Subscriptions et Memberships sont payants : si tu n'as pas de licence sur le site jetable, écris leurs traitements d'après la documentation officielle, cite les tables et métadonnées visées, et liste ce qui n'a pas pu être testé.
- Aucun secret, aucun chemin réel, aucune donnée réelle dans le dépôt.
- Aucune requête vers l'extérieur pendant l'import.
- Tout est rejouable : relancer l'étape sur une copie fraîche donne le même résultat.
- Les scripts de `staging/` ne doivent jamais pouvoir tourner sur la production : ils refusent de s'exécuter si l'adresse du site est celle de la production ou si `WP_ENVIRONMENT_TYPE` vaut `production`.
- Novamira ne figure dans aucun script de `bascule/`.

## Ce que tu me rends

1. Avant de coder : ce que l'outil de staging fait déjà à l'import (emails, clés, tâches planifiées, indexation), et ce qui manque par rapport à la liste ci-dessus.
2. Les scripts, leurs tests, et la commande unique pour créer le staging d'Imagine.
3. Un rapport d'une page dans `production/A-01/notes.md` : ce qui est fait, ce qui n'a pas pu être testé, et les questions à arbitrer, sous forme fermée.

Ne crée pas le staging d'Imagine toi-même : c'est moi qui lance la commande.
