# Lot A-03 — Les tests de non-régression de l'existant

**Voie** : 1. **Chantier** : A. **Délai** : une demi-journée. **Dépend de** : A-02 (clos).

## Pourquoi

Avant de mettre à jour quoi que ce soit sur le site d'Imagine, il faut une photo de ce qui marche, qu'on puisse reprendre après la mise à jour et comparer. Le script se prépare maintenant, sur site fictif, pour être lancé dès que le staging d'Imagine existe.

## Ce qu'on veut

`wp/outils/bascule/non-regression` (même forme que l'audit de A-02), lancé sur un site, en lecture seule sauf mention contraire, qui produit un rapport comparable d'une exécution à l'autre :

- **Accès** : pour un échantillon de comptes pris dans chaque état d'adhésion et d'abonnement présent sur le site (actif, en pause, expiré, annulé, en attente, sans adhésion), ce que Memberships répond sur un échantillon de contenus restreints. On compare la matrice avant et après.
- **Abonnements** : nombre par état, par moyen de paiement, par périodicité ; dates de prochain paiement ; actions planifiées en attente (par type, par jour). Rien ne doit disparaître ni changer de date.
- **Commandes** : totaux par état et par mois sur douze mois (nombre et montant), pour détecter une altération.
- **Pages clés** : accueil, un article ouvert, un article restreint, boutique, panier, commande, compte : code HTTP, absence d'erreur PHP, présence d'un marqueur attendu.
- **Renouvellement de test** : sur staging seulement, et seulement si le site est au statut vérifié (courrier et passerelles neutralisés) : déclencher un renouvellement manuel sur un abonnement de test créé pour l'occasion, vérifier la commande créée, puis nettoyer. C'est la seule partie qui écrit ; elle est désactivée par défaut.

Le rapport ne contient **aucune donnée personnelle** : des identifiants numériques internes, des états, des nombres. Pas de nom, pas d'email, pas d'adresse.

Une commande `comparer` prend deux rapports et dit ce qui a changé, classé : attendu (versions), à regarder, anormal.

## Preuve

Sur site fictif (classique et HPOS) : deux exécutions identiques → aucune différence ; une altération provoquée (une adhésion expirée à la main, une action planifiée supprimée) → détectée et classée anormale.

## Livrables

Le script, la commande de comparaison, les tests, le mode d'emploi en dix lignes, `production/A-03/PRET`. Rapport de dix lignes : pas de reçus d'empreintes ni d'archives de preuves.
