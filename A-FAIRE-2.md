# À faire — voie 2 : ce qui se voit

File de la **deuxième session d'Hermès**. Tenue par Claude. **Hermès ne modifie pas ce fichier.**

Mis à jour le 25 novembre 2026, 19 h 30 (passage automatique).

Consigne permanente : `prompts/consigne-permanente.md` (section « Les deux voies »). Doctrine : `doctrine/doctrine.md`.

La voie 1 (`A-FAIRE.md`) s'occupe de l'existant : import, audit, mise à jour. La voie 2 construit, sur un site **entièrement fictif**, ce que Ced peut ouvrir dans un navigateur. Elle ne dépend ni de l'import d'Imagine, ni des maquettes.

## Consignes actives, par ordre de priorité

**Pas de rapport de ta part depuis 16 h 25**, mais ton travail est lu dans `production/` : complément de C-09 rendu (`PRET` de 19 h 13), B-03 rendu à 18 h 03, relu, corrections en cours. C-14 : vérifié, code clos. Arbitrages : `docs/arbitrages-2026-11-25.md`, section « Passage automatique de 19 h 30 ».

**0. Corrections de B-03 : `corrections/B-03.md`.** Tu les as commencées, termine-les. Le défaut de la fusion est confirmé : **les couleurs posées dans le contenu sont neutralisées dans les trois fonds**, sans toucher au contenu enregistré ni aux images. Instruction 4 : retire le bloc redondant. Instruction 5 (rejouer la part que les relecteurs n'ont pas pu exécuter) : **elle ne te concerne pas et ne bloque pas** ; rejoue toi-même tes tests PHP et HTTP après correction et dépose les reçus. Puis redépose `production/B-03/PRET`.

**1. B-02 : dépose `production/B-02/PRET`.** Il manque toujours, donc le lot n'a jamais été relu. `PRET` veut dire « prêt à relire », pas « recette complète » : dépose-le maintenant, avec tes réserves telles qu'elles sont écrites (seconde échéance payée non lue par le tableau, marge, historique, documents). La relecture dira ce qui est à corriger ; n'attends pas d'avoir tout raccordé. Deux minutes.

**2. `briefs/B-04-page-numero.md`** — la page numéro, le kiosque et la page thématique, avec le statut d'accès visible, le bouton d'achat (C-14) et le PDF (C-11). Une demi-journée.

**3. `briefs/C-15-ecran-des-echeances.md`** — l'écran des échéances du référent administratif (§3.13), sur les paiements fictifs du complément de C-09. Une demi-journée.

Les corrections d'un lot relu (B-03, B-02, C-09) passent avant le lot en cours, sans attendre que cette file les cite. Preuves proportionnées, rapports courts. **Un rapport dans `files/rapports/` à chaque fin de réveil**, même de cinq lignes : c'est ce que le passage automatique lit en premier.

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
| B-02 Mon compte | 25/11 | Rendu sans `PRET` ; à déposer (consigne 1) |
| C-09 Complément paiements fictifs | 25/11 | Rendu (9 profils créés, 20 partiels, 1 impossible) ; vérification attendue |
| B-03 Mode lecture | 25/11 | Relu : **à corriger** (contraste quand le contenu porte ses propres couleurs), consigne 0 |
