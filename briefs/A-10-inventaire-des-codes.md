# Lot A-10 — L'inventaire des codes de réduction

**Voie** : 1. **Chantier** : A. **Délai** : trois heures. **Cahier des charges** : §4.3 (« inventaire complet des codes actifs et des abonnés rattachés avant la migration. Chaque code est reclassé ou supprimé »).

## Pourquoi

Le site actuel porte des années de codes de réduction. Certains sont attachés à des abonnements en cours et jouent à chaque renouvellement. Avant de toucher à l'offre, Imagine doit voir la liste. Le reclassement est sa décision : ce lot ne produit que l'inventaire.

## Ce qu'on veut

Un complément du script d'audit (A-02), en **lecture seule**, qui produit pour un site :

- chaque code : type, montant ou pourcentage, dates, limites d'usage, nombre d'utilisations, restrictions (produits, adresses autorisées **comptées, jamais listées**), s'il est récurrent sur les renouvellements ;
- pour chaque code : le nombre d'abonnements actifs, suspendus ou en attente qui le portent encore, et le nombre de commandes des douze derniers mois ;
- les codes expirés ou jamais utilisés, à part.

Le rapport contient les **noms des codes** (ce sont des réglages du site, pas des données personnelles) mais **aucun nom, email ou identifiant de client** : des nombres seulement. Il s'écrit hors de la racine web, au même endroit que le rapport d'audit, et ne rejoint jamais le dépôt quand il vient d'un site réel.

Classique et HPOS. Aucun écrit en base, aucune tâche planifiée, aucun envoi.

## Preuve

Sur le banc fictif d'A-02 : quelques codes de chaque sorte, dont un récurrent porté par un abonnement actif et un expiré. Les comptes du rapport sont exacts ; l'empreinte de la base est identique avant et après ; aucun identifiant de client dans la sortie. Preuves proportionnées.

## Livrables

Le script, ses tests, deux lignes dans le mode d'emploi de l'audit, `production/A-10/PRET`. Rapport court.
