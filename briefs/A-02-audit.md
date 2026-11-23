# Lot A-02 — Audit de l'existant

**Chantier** : A. **Nature** : script en lecture seule et son rapport. **Délai** : une demi-journée.

## Pourquoi

Dès que le staging d'Imagine existe, la première chose à savoir est : qu'est-ce qui tourne là-dedans, et qu'est-ce que la mise à niveau risque de casser ? Ce lot prépare l'outil **à l'avance**, sur un site fictif, pour que l'audit du vrai staging prenne quelques minutes le jour venu.

## Ce qu'on veut

Un script `wp/outils/bascule/audit` (lecture seule, aucun changement sur le site) qui produit un rapport `audit.md` et `audit.json`. Il ne contient **aucune donnée personnelle ni aucune valeur de réglage sensible** : des noms, des versions, des comptes.

1. **Versions** : WordPress, PHP, base de données, et pour chaque extension et chaque thème : version installée, active ou non, dernière version disponible si elle est connue sans réseau, version de WordPress et de PHP exigée.
2. **Commerce** : stockage des commandes (classique ou HPOS) ; passerelles de paiement présentes ; nombre d'abonnements par état et par périodicité ; nombre d'adhésions par plan et par état ; nombre de commandes par année ; produits d'abonnement et leurs réglages non sensibles (périodicité, synchronisation, essai, frais).
3. **Memberships** : plans, règles de restriction de contenu (quels types de contenu, quelles taxonomies), contenus distribués au goutte-à-goutte, pour comprendre comment le site actuel protège ses articles.
4. **Contenu** : types de contenu et taxonomies avec leur nombre d'entrées ; nombre d'articles par année ; champs personnalisés les plus fréquents (noms seulement) ; constructeur de pages utilisé, le cas échéant.
5. **Base** : tables avec leur taille et leur nombre de lignes ; tables n'appartenant ni à WordPress ni à une extension active (candidates au nettoyage) ; options chargées automatiquement les plus lourdes (noms et tailles).
6. **Planification** : actions planifiées par crochet et par état ; tâches planifiées de WordPress.
7. **Ce que la mise à niveau risque de casser** : pour chaque extension, l'écart entre la version installée et la dernière ; les extensions sans mise à jour depuis plus de deux ans ; les gabarits de WooCommerce surchargés par le thème et périmés ; les fonctions dépréciées signalées dans le journal de débogage, s'il existe.

Le rapport se termine par une synthèse d'une demi-page : les cinq points à regarder en premier.

## Preuve

Exécution sur un site fictif avec WooCommerce, Subscriptions et Memberships, contenant quelques abonnements, adhésions et règles de restriction. Vérifier que le script ne modifie rien (empreinte de la base avant et après).

## Limites

Lecture seule. Aucun accès à un staging d'Imagine : il n'en existe pas encore. `production/A-02/PRET` porte sur le script, pas sur l'audit d'Imagine, qui sera lancé après l'import.
