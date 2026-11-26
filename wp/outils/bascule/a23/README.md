# A-23 — Comptes des lecteurs (lecture seule)

## Le standard WordPress, en dix lignes

1. WordPress conserve l'empreinte dans `users.user_pass`, pas le mot de passe en clair [S1, code installé].
2. Le standard historique de WordPress 2.5 à 6.7 utilise phpass ; son préfixe usuel est `$P$` [S2].
3. Depuis WordPress 6.8, le choix par défaut est bcrypt, avec un prétraitement SHA-384 et le préfixe `$wp` [S2, S3].
4. Le code installé du banc 7.0.9 contient ces branches ; son empreinte de source et les tests statiques sont dans `standard.json` [code installé].
5. `wp_check_password` garde une branche historique MD5 pour les empreintes d'au plus 32 caractères [S1].
6. Il distingue ensuite un hasher substitué, les formes préfixées `$wp`, phpass `$P$`, puis `password_verify` [S1].
7. La documentation décrit le maintien des anciennes empreintes et leur re-hachage lors d'une connexion réussie [S2].
8. Les fonctions sont remplaçables par une extension, et le choix d'algorithme comporte des filtres [S1, S3].
9. A-23 ne lance aucune de ces vérifications : il reconnaît seulement une liste fermée de préfixes ; MD5 sans préfixe reste `autre`.
10. Une famille reconnue ne prouve ni la validité de l'empreinte ni la reconnexion d'un compte ; aucun verdict de reprise n'est rendu.

Sources officielles consultées le 26 novembre 2026 (pas un engagement sur une extension du site réel) :

- S1 : https://developer.wordpress.org/reference/functions/wp_check_password/
- S2 : https://make.wordpress.org/core/2025/02/17/wordpress-6-8-will-use-bcrypt-for-password-hashing/
- S3 : https://developer.wordpress.org/reference/functions/wp_hash_password/
- Code installé : `wp-includes/pluggable.php`, `wp-includes/class-phpass.php`, `wp-includes/version.php` dans le seul banc fictif ; contrôle statique, sans tentative de mot de passe.

## Parcours opérateur

Ne lancer qu'après A-22 clos, sur une copie **vérifiée et anonymisée**, dans un
conteneur Linux déjà confiné et sans réseau. Jamais sur la source ou une archive.
Les chemins ci-dessous sont des emplacements fictifs à remplacer. `/hors-web`
existe, est privé et est disjoint de la copie et du dépôt dans les deux sens.
L'audit A-02 a déjà été produit dans le même parent. Un nouveau dossier de sortie
est exigé ; ni réutilisation ni écrasement. Le PHP brut est refusé.

```sh
python3 wp/outils/bascule/a23/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/comptes-date
```

Seuls arguments : `--wp-path`, `--audit`, `--output`, tous obligatoires. Succès :
`A23_OK comptes.json comptes.md`. Les deux fichiers contiennent uniquement des
nombres, des étiquettes fermées et l'empreinte de l'audit. En refus, seulement un
code fixe et, pour un fichier de remplacement, son nom technique fermé. Rien
n'est publié avant la fin du processus **et** des deux flux et la validation
stricte du rapport. Les fichiers temporaires sont privés et retirés au refus.
Aucun flux PHP brut n'est persisté. Le gardien est celui d'A-22
(`wp/outils/bascule/stream_guard.py`), pas une copie dans ce lot.

## Définitions et limites

- Lecteur : compte hors des rôles `administrator`, `editor`, `shop_manager`, sans
  capacité de gestion reconnue par la règle inclusive A-17 (capacités directes
  comprises). Un compte ayant plusieurs rôles est exclu dès qu'un est de gestion.
- Abonné vivant : lecteur avec au moins un abonnement `active`, `pending`,
  `on-hold` ou `pending-cancel`. Le compte est dédupliqué. Ce n'est pas un droit
  d'accès ni une prédiction de paiement. Les statuts expiré/annulé n'en font pas
  partie, mais comptent comme historique commercial.
- La lecture des liens passe par le magasin natif faisant autorité :
  `posts/postmeta._customer_user` en classique, `wc_orders.customer_id` en HPOS.
  Commandes, remboursements et abonnements de **tout statut**, corbeille comprise,
  comptent comme historique. Aucun rapprochement par email. Le magasin inactif
  n'est pas une seconde vérité. Un lien client mal formé ou contradictoire est
  refusé, jamais interprété comme « aucun historique ».
- Familles, préfixes uniquement : `phpass` (`$P$`), `phpass_h` (`$H$`),
  `wordpress_bcrypt` (`$wp$2y$`), `bcrypt` (`$2a$`, `$2b$`, `$2y$`), `argon2i`,
  `argon2id`, `autre`, `vide`. La reconnaissance de `$H$` n'affirme pas qu'il suit
  la branche phpass standard de WordPress. Aucun fragment n'est rendu.
- Email vide : chaîne vide ; sinon mal formé si `is_email` de WordPress dit non.
  Ce n'est ni une vérification de boîte ni une requête réseau. Les doublons
  ignorent la casse ASCII, sans rogner ni corriger ; tous les membres d'un groupe
  non vide comptent, y compris une adresse mal formée.
- Login égal à l'email : égalité exacte et email non vide. Collision de casse :
  au moins deux graphies différentes sous la même forme ASCII minuscule ; tous
  leurs membres comptent. Une répétition strictement identique ne suffit pas.
- Les collisions des lecteurs sont cherchées contre **tous les comptes**,
  administration et lecteurs non vivants compris, pour les deux populations.
- Groupe de moins de cinq : fondu dans `autres` de son tableau, y compris `autre`
  et `vide`. Les groupes à zéro sont absents. `families` partitionne la population ;
  les anomalies d'email/login se recoupent. Leurs colonnes et leurs `autres` ne
  s'additionnent pas en personnes distinctes. `without_commerce` compte les lecteurs
  sans aucune commande/remboursement/abonnement ; un petit nombre est aussi fondu.
- Après neutralisation, les six blocs `families`, `emails`, `logins` disent
  **« inconnu après neutralisation »**, jamais zéro : l'import remplace ces trois
  champs. La marque existante peut être posée dès la neutralisation seule : on
  reste prudent. Restent utiles le nombre de lecteurs, de lecteurs avec abonnement
  vivant et de lecteurs sans historique commercial. L'import n'a pas été modifié.
- Les caches/fichiers de remplacement ou liens symboliques sont refusés avant
  exécution ; ils se traitent sur la copie par l'opérateur, jamais sur la source.
  Les erreurs d'extension ne sont jamais recopiées. Aucune activation, correction,
  fusion, réactivation, notification ou connexion n'est réalisée.

## Tests et reprise

Depuis la racine du dépôt sous Windows ; le Python réellement exécuté, la locale
et les encodages sont enregistrés par la matrice. Docker est appelé via WSL
Ubuntu ; image déjà locale, aucun téléchargement. PHP ne tourne que dans les
conteneurs jetables A-23, sans montage, réseau, port ou privilège. Nettoyage par
nom exact, vérification du label puis de l'absence.

```sh
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 python -B wp/tests/a23/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a23-reprise
python -B wp/tests/a23/verify.py
```

Le dossier de reprise doit être nouveau. Un rejeu ne remplace pas implicitement
le paquet livré : le parent choisit explicitement le dernier paquet vert.
`verify.py` vérifie le paquet livré ; `--require-shared-doc` ajoute le contrat des
deux lignes du README partagé après leur intégration par le parent.
Aucun PRET ni préparation de l'image globale n'est fait par le présent enfant.
