# Lot C-02 — Contrôle du numéro d'entreprise

**Chantier** : C · code sur mesure. **Nature** : PHP pur et tests, sans WordPress.
**Emplacement** : `wp/plugins/imagine-pilotage/src/Entreprise/` et `tests/Entreprise/`.
**Livrables** : code, tests, `production/C-02/notes.md`, puis `production/C-02/PRET`.
**Cas d'acceptance concerné** : R-06 (`docs/recette/cas.md`).

## Pourquoi

À la commande d'un professionnel, le site demande le numéro d'entreprise et en vérifie la cohérence (§3.4), pour qu'Odoo reçoive des données exploitables pour la facturation électronique.

## À implémenter

1. **Normalisation** d'un numéro d'entreprise belge saisi librement : avec ou sans `BE`, espaces, points, tirets ; ancien format à neuf chiffres complété par un zéro initial. Forme de sortie : dix chiffres, et forme d'affichage `0123.456.789`.
2. **Contrôle de cohérence** : dix chiffres, premier chiffre 0 ou 1, et les deux derniers chiffres égaux à 97 moins le reste de la division par 97 des huit premiers.
3. **Résultat explicite** : valide, ou invalide avec un motif (vide, mauvaise longueur, caractères interdits, clé de contrôle fausse), chaque motif ayant un message en français destiné au client.
4. **Recherche de la dénomination** : uniquement une **interface** (`RechercheDenomination`) et une implémentation vide qui répond « non disponible ». Aucun appel réseau dans ce lot.

## Ce que tu ne décides pas

Le cahier des charges demande d'« afficher la dénomination trouvée », ce qui suppose une recherche en ligne ; une décision antérieure prévoyait le seul contrôle de format. L'arbitrage est ouvert (`docs/decisions.md`, point 8). N'implémente aucune recherche réelle. Dans `notes.md`, indique les sources officielles possibles (registre belge des entreprises, service européen de validation de TVA), leurs conditions d'accès et leurs limites, avec les adresses de leur documentation.

Les numéros étrangers : hors de ce lot. Signale simplement ce qu'il faudrait pour les accepter.

## Tests

Au moins : numéros valides dans chaque forme de saisie ; clé fausse ; neuf chiffres ; onze chiffres ; lettres ; chaîne vide ; premier chiffre 2. Construis les numéros de test par calcul de la clé, sans utiliser le numéro d'une entreprise réelle.

## Exigences

Celles du lot C-01 (PHP 8.2, types stricts, PSR-12, espace de noms `Imagine\Pilotage\Entreprise`, PHPUnit par `composer test`).
