# À faire — voie 2 : ce qui se voit

File de la **deuxième session d'Hermès**. Tenue par Claude. **Hermès ne modifie pas ce fichier.**

Mis à jour le 25 novembre 2026, 22 h 30 (passage automatique).

Consigne permanente : `prompts/consigne-permanente.md` (section « Les deux voies »). Doctrine : `doctrine/doctrine.md`.

La voie 1 (`A-FAIRE.md`) s'occupe de l'existant : import, audit, mise à jour. La voie 2 construit, sur un site **entièrement fictif**, ce que Ced peut ouvrir dans un navigateur. Elle ne dépend ni de l'import d'Imagine, ni des maquettes.

## Consignes actives, par ordre de priorité

Tes rapports de 19 h 34, 21 h 29 et 22 h 17 sont lus, merci pour eux : complément de C-09, B-03 corrigé, B-04 et C-15 rendus, corrections de B-02 et de C-15 appliquées, file vide à 22 h 17. **B-03 et le complément de C-09 sont vérifiés : code clos.** B-02 et C-15 attendent leur vérification, B-04 sa relecture. Arbitrages : `docs/arbitrages-2026-11-25.md`, section « Passage automatique de 22 h 30 ».

**0. Corrections et vérifications de B-02, C-15, B-04** : si l'une revient « à corriger » (`corrections/<lot>.md` plus récent que ton `PRET`), elle passe avant tout le reste. Tes décisions à défaut sont confirmées : jeu fictif propre à B-04 (produit public à zéro euro, aucun achat exécuté) ; export de C-15 avec les colonnes montant et devise ; « mandats à lancer » limité au renouvellement exigible impayé ; « paiements en attente » limité aux abonnements ; libellé « virement » réservé au circuit virement dans B-02. Les trois questions correspondantes sont rangées pour Imagine.

**1. `briefs/C-16-commande-pour-un-client.md`** — la commande encodée par le référent administratif pour un client, en trois écrans au plus, avec l'encodage « sans email » et la vente sans identité (§3.13, §2.3). Une demi-journée.

**2. `briefs/C-17-justificatifs-tarif-solidaire.md`** — le dépôt du justificatif dans « Mon compte », la file de validation côté administration, le fichier hors racine publique et supprimé à la décision (§3.13, §4.4). Ne touche ni au prix ni à l'accès. Une demi-journée.

**3. `briefs/C-18-extractions.md`** — l'écran des extractions au format tableur, quatre extractions de départ, lecture seule (§3.13). Une demi-journée.

Les corrections d'un lot relu passent avant le lot en cours, sans attendre que cette file les cite. Preuves proportionnées, rapports courts. **Un rapport dans `files/rapports/` à chaque fin de réveil**, même de cinq lignes : c'est ce que le passage automatique lit en premier.

**Séparation des voies.** Ton rapport de 21 h 29 signale qu'un de tes workers a lu `A-FAIRE.md`. Lecture sans écriture, sans conséquence, et tu as recadré : rien d'autre à faire. La règle reste : tes workers ne lisent que cette file.

Les liens « offert » et « groupé » absents des profils (C-13 et B-02 en mode strict) : c'est une limite connue des données de démonstration, liée à une question ouverte chez Imagine. On ne les fabrique pas. Ne t'arrête pas dessus.

## Règles de la voie 2

- **Tu construis sur un lot `PRET` de ta propre voie sans attendre sa clôture** (B-01 sur B-00, C-08 sur B-01…) : ces lots sont visuels, leur validation par Ced viendra en bloc. Si la relecture d'un lot remonte des corrections, elles passent avant le lot suivant.
- **Chaque lot se termine par un fichier `A-VOIR.md`** : les adresses à ouvrir et ce qu'on doit y voir. Un lot de cette voie sans `A-VOIR.md` n'est pas `PRET`.
- **Tes dossiers** : `wp/themes/imagine/`, `wp/plugins/imagine-site/`, `wp/outils/demo/`, `wp/tests/demo/`, les adaptateurs d'administration de `wp/plugins/imagine-pilotage/` (C-10 seulement), `production/<tes lots>/`. Tu ne touches pas à `wp/outils/staging-court/`, `wp/outils/staging/`, `wp/outils/bascule/`, `wp/tests/a01-court/`, `wp/tests/a02-audit/`, `wp/tests/t01/` ni aux bibliothèques closes.
- **Un seul site** : `imagine-test-demo`. Tu ne crées, n'arrêtes et ne supprimes aucun autre site.
- **Rien de réel** : pas d'archive d'Imagine, pas de compte, pas de licence d'extension commerciale activée, pas d'email sortant. Novamira est permis sur `imagine-test-demo` et nulle part ailleurs.
- **Proportion** : ce sont des squelettes à montrer, pas des versions finales. Si un lot enfle, arrête-toi et dis-le.

## Terminé

| Lot | Rendu | État |
|---|---|---|
| B-00 Site de démonstration | 23/11, corrigé le 23/11 | **Code clos le 23/11.** Validation visuelle de Ced attendue |
| B-01 Squelette du thème | 23/11, corrigé le 23/11 | **Code clos le 23/11.** Validation visuelle de Ced attendue |
| C-08 Paywall sur article | 23/11, corrigé le 23/11 | **Code clos le 23/11** (recherche interne étanche). Validation visuelle de Ced attendue |
| C-09 Profils de test | 23/11, corrigé le 23/11 | **Code clos le 24/11** : 4 créés, 25 partiels, 1 impossible hors ligne |
| C-11 PDF du numéro | 24/11, corrigé le 24/11 | **Code clos le 25/11** : fichier hors racine publique, servi par la décision d'accès |
| C-12 Accès découverte | 24/11, refait le 24/11 | **Code clos le 25/11** : désignation éditoriale obligatoire, fermé par défaut |
| C-10 Écran de réglages | 23/11, corrigé le 23/11 | **Code clos le 24/11** : les réglages d'accès agissent sur le paywall. Validation visuelle de Ced attendue |
| C-13 Écran de la liste d'envoi | 24/11, corrigé le 25/11 | **Code clos le 25/11** : bénéficiaires, renouvellements, gel persistant, règles en code pur. Liste vide pour les profils tant que le complément de C-09 n'est pas fait. Validation visuelle de Ced attendue (menus) |
| C-14 Achat au numéro | 25/11, corrigé le 25/11 | **Code clos le 25/11** : l'achat payé ouvre les articles et le PDF du seul numéro acheté, sans limite de durée ; remboursement partiel en réglage. Validation visuelle de Ced attendue |
| B-02 Mon compte | 25/11, corrigé le 25/11 | Relu, corrigé ; vérification attendue (consigne 0). Recette partielle assumée : marge, historique, documents |
| C-09 Complément paiements fictifs | 25/11 | **Code clos le 25/11** : 9 profils créés, 20 partiels, 1 impossible ; paiements fictifs déclarés comme tels. Liens « offert » et « groupé » non fabriqués |
| B-03 Mode lecture | 25/11, corrigé le 25/11 | **Code clos le 25/11** : couleurs du contenu neutralisées sur les trois fonds, position de lecture conservée. Validation visuelle de Ced attendue, contraste à revoir après le choix des couleurs par le designer |
| B-04 Page numéro, kiosque, thématiques | 25/11 | Rendu ; relecture attendue (consigne 0) |
| C-15 Écran des échéances | 25/11, corrigé le 25/11 | Relu, corrigé ; vérification attendue (consigne 0) |
