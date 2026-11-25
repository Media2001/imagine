# A-10 — complément autonome de l'audit

Commande opérateur (PHP CLI 8.2+, `pdo_mysql`, après GO sur une copie vérifiée) :

```text
php wp/outils/bascule/inventorier-codes --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/codes-date
```

L'audit A-02 doit déjà exister. Le nouveau dossier de sortie est **frère** du dossier du rapport A-02 : même parent externe au site **et au dépôt**, jamais un dossier existant. Le garde vérifie schéma A-02, lecture seule, présence des sections et même magasin faisant autorité ; il lie le rapport par SHA-256. Ce n'est ni une preuve cryptographique d'identité du site ni un permis d'accès au réel : l'opérateur choisit explicitement la bonne photographie récente. Les gardes ne recherchent aucun autre site.

`codes.json` et `codes.md` (0600, dossier 0700) inventorient les coupons stockés, tous statuts : nom du code, type, montant et unité, dates UTC, limites et usages, produits/catégories inclus et exclus par leurs **identifiants de réglage**, montants minimum/maximum, vente seule, livraison gratuite, articles soldés et **nombre** de restrictions email. Aucun titre de produit, description de coupon, auteur, nom/email ou identifiant de client n'est projeté. Les noms des codes sont l'exception expressément autorisée.

`recurring_on_renewals` décrit le type standard Subscriptions configuré, pas la remise effective à venir. `payment_limit_including_initial` inclut le paiement initial éligible ; zéro = illimité. Aucun historique personnel, solde par abonné ou décision de facturation n'est calculé. Type tiers inconnu : `null`, jamais récurrent inventé.

Défauts techniques déclarés :

- Porteurs **distincts** par code : `active`, `on_hold`, `pending`, `pending_cancel` séparés ; les abonnements terminés/annulés sont exclus.
- Commandes **distinctes**, renouvellements inclus, créées entre la même seconde UTC d'il y a douze mois calendaires et maintenant, bornes incluses ; tous statuts sauf corbeille/auto-draft. Futur et objets `shop_order_refund` exclus. Les commandes annulées/remboursées restent des commandes : pas un chiffre de ventes nettes.
- Les lignes coupon dupliquées ne multiplient pas les comptes ; noms comparés sans casse, sans comparaison insensible aux accents.
- `expired` et `never_used` sont des listes séparées de noms de codes et peuvent se recouper. Jamais utilisé signifie compteur Woo enregistré égal à zéro, pas absence de commande historique reconstruite. Aucun code n'est reclassé ou supprimé.
- Lecture directe du stockage natif : le bootstrap Woo exécute des hooks et peut écrire des caches/tâches, donc n'est pas appelé. Les API officielles servent d'oracle dans la fixture, pas de lecteur en production. Parseur de configuration et normalisation d'identifiants A-02 réutilisés sans modifier cet outil.
- Configuration littérale, site simple, toutes tables InnoDB ; métadonnées coupon dupliquées, dates illisibles et formats structurés invalides refusés. Une seule transaction REPEATABLE READ / READ ONLY. Le compte SELECT est recommandé ; la transaction bloque également une écriture avec root (prouvé sur le banc).
- Contrat standard qualifié : WooCommerce 11.1.1 / Subscriptions 9.4.1 sur le banc A-02. Pas de preuve sur Imagine, ses versions/plugins historiques ou les restrictions ajoutées par des extensions tierces (y compris filtres de code/types, marques ajoutées dans d'autres versions). Pas d'évaluation dynamique des droits ou d'une future remise.

## Tests et preuves

```text
python wp/tests/a10/run.py
python wp/tests/a10/verifier.py production/A-10/preuves/IDENTIFIANT
```

Le runner ne prend aucun chemin de site, archive ou compte. Il importe les fonctions du banc A-02 sans bytecode, utilise un label A-10 distinct, crée ses propres fixtures dans le conteneur jetable hors réseau (aucun port/montage/privilège), et supprime seulement ce nom après vérification du label. Aucun nettoyage global.

Dix coupons, les sept types natifs standard dont les deux types récurrents et les deux types de frais initiaux ; expirés et jamais utilisés. Vrai renouvellement Subscriptions, doublons de lignes coupon, commandes récentes/anciennes/futures/en corbeille, statuts porteurs et terminés. Oracle : getters Woo natifs, empreinte logique complète de toutes tables et fichiers identique avant/après, compte SELECT, piège de bootstrap. Les appels de préparation de fixtures sont distincts du passage de l'auditeur : seule la préparation crée des objets. Les reçus sont des assertions nommées, pas un décompte PHPUnit. La préparation d'image T-01 est réellement relancée et son reçu est conservé séparément.

Le paquet final désigné par `production/A-10/PRET` est seul courant ; les essais RED et essais intermédiaires sont historiques. La documentation officielle et les hashes des sources natives sont tracés sans embarquer les extensions commerciales. Aucun rapport issu d'un site réel ne doit rejoindre le dépôt.
