# Lot C-13 — L'écran de la liste d'envoi

**Voie** : 2. **Chantier** : C. **Délai** : une demi-journée. **Dépend de** : C-07 (clos), C-09, C-10.
**Cahier des charges** : §3.13, pour la liste d'envoi et les extractions.

## Pourquoi

À chaque parution, quelqu'un chez Imagine doit sortir la liste des abonnés à qui envoyer le magazine. La règle est écrite et testée (C-07). Il manque l'écran : c'est le premier outil de travail quotidien qu'Imagine verra.

## Ce qu'on veut

Dans le menu « Imagine », une page « Liste d'envoi », accessible au rôle Référent abonnements et aux administrateurs :

- choix du numéro (calendrier de parution), avec sa date de clôture ;
- un aperçu : nombre de destinataires, répartition Belgique / étranger, et la liste des **exclus avec leur motif** (suspendu, expiré, virement non validé…), parce que c'est la question qu'on posera au téléphone ;
- un bouton d'export CSV, au format réglé dans l'écran de C-10 ;
- chaque export est journalisé (qui, quand, quel numéro, combien de lignes).

Les données viennent des vrais abonnements du site de démonstration (profils de C-09), lus par un adaptateur qui alimente la bibliothèque de C-07. Les abonnés sans email y figurent : ils reçoivent le magazine.

Le CSV ne doit pas être atteignable sans les droits (pas de fichier déposé dans un dossier public ; généré à la demande, nonce, capacité). Protège les cellules contre l'injection de formules de tableur.

Sobre : composants natifs de l'administration WordPress.

## Livrables

Code, tests (droits, contenu de la liste pour les profils de C-09, exclus et motifs, injection de formules, journal), `production/C-13/A-VOIR.md` (se connecter en `e-abo`, choisir un numéro, exporter), `PRET`.
