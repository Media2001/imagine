# Lot C-18 — Les extractions

**Voie** : 2. **Chantier** : C. **Délai** : une demi-journée. **Dépend de** : C-10, C-13, C-15. **Cahier des charges** : §3.13 (« Extractions »). Relis-le.

## Pourquoi

La direction d'Imagine demande aujourd'hui ses listes à la personne qui tient Access. Le cahier des charges promet un outil d'extraction dans le back-office, au format tableur. La liste définitive des rapports sera arrêtée avec Imagine ; ce lot pose l'outil et quelques extractions de départ, pour qu'Imagine réagisse sur quelque chose de visible.

## Ce qu'on veut

Dans l'administration de `imagine-test-demo`, sous le menu Imagine existant, en compte `e-abo` : un écran « Extractions » où l'on choisit une extraction, ses filtres, puis où l'on voit le **nombre de lignes** avant de télécharger le fichier.

Extractions de départ, celles que le cahier des charges cite et que les données du site permettent **aujourd'hui** :

1. abonnés par localité (code postal, pays) ;
2. abonnés par mode de paiement ;
3. abonnés par date d'échéance (période choisie) ;
4. abonnés par état (actif, en délai de grâce, suspendu, expiré).

Les extractions par tranche d'âge et par étiquette dépendent du formulaire de personnalisation, qui n'existe pas encore : elles figurent dans la liste, grisées, avec la mention « à venir ». Ne fabrique pas ces données.

Règles :

- **Lecture seule.** L'écran lit l'état natif (comptes, abonnements, commandes) ; il n'écrit rien d'autre qu'une ligne de journal : qui a extrait quoi, quand, combien de lignes. Pas le contenu.
- Une extraction se décrit en un seul endroit du code (ses colonnes, ses filtres, sa requête), pour qu'en ajouter une soit l'affaire d'un fichier. Les règles de filtrage en code pur, testables sans WordPress.
- Colonnes : identité, adresse de livraison, formule, mode de paiement, état, échéance. **Jamais** de mot de passe, de jeton, de référence de moyen de paiement, d'IBAN, ni de note interne.
- Les comptes « sans email » sortent avec la colonne adresse électronique **vide**, pas avec leur adresse technique.
- Mêmes précautions que l'export de la liste d'envoi (C-13) : droit dédié, jeton, fichier produit à la volée et jamais laissé dans un dossier public, protection contre les formules de tableur. Réemploie ce code.
- Aucun email, aucun appel sortant.

## Preuve

Proportionnée. Sur le site, avec les profils de C-09 : chaque extraction rend les profils attendus et pas les autres (A-ETRANGER seul hors de Belgique, A-PAPIER et A-VIR dans leur mode de paiement, A-ECHEANCE dans les trente jours, A-GRACE et A-SUSP dans leur état) ; A-SANSMAIL sort sans adresse électronique ; un compte sans le droit reçoit un refus ; le fichier s'ouvre ; la ligne de journal existe et ne contient aucune donnée d'abonné.

## Livrables

Le code, ses tests, `production/C-18/A-VOIR.md`, `PRET`. Rapport court dans `files/rapports/`.
