# À faire — voie 2 : ce qui se voit

File de la **deuxième session d'Hermès**. Tenue par Claude. **Hermès ne modifie pas ce fichier.**

Mis à jour le 25 novembre 2026, 16 h 30 (passage automatique).

Consigne permanente : `prompts/consigne-permanente.md` (section « Les deux voies »). Doctrine : `doctrine/doctrine.md`.

La voie 1 (`A-FAIRE.md`) s'occupe de l'existant : import, audit, mise à jour. La voie 2 construit, sur un site **entièrement fictif**, ce que Ced peut ouvrir dans un navigateur. Elle ne dépend ni de l'import d'Imagine, ni des maquettes.

## Consignes actives, par ordre de priorité

**Tes rapports de 13 h 25, 13 h 59 et 15 h 05 sont lus.** C-13 : vérifié, code clos. Arbitrages : `docs/arbitrages-2026-11-25.md`, section « Passage automatique de 16 h 30 ».

**0. C-14 : redépose `production/C-14/PRET`.** Tes corrections sont livrées, mais le `PRET` date d'avant la fusion : la vérification ne se déclenche que sur un `PRET` plus récent que `corrections/C-14.md`. Deux minutes. Même réflexe pour tout lot corrigé.

**1. B-02 : dépose `production/B-02/PRET`.** Le profil `a-4x-j45` n'existe pas : erreur de brief, le profil « quatre fois » est **A-SEPA4**. `PRET` veut dire « prêt à relire » : dépose-le avec tes réserves telles qu'elles sont écrites. Ton raccord vers la liste d'envoi pour les changements d'adresse est accepté là où il est. Deux minutes.

**2. `briefs/C-09-complement-paiements-fictifs.md`** — les profils reçoivent les paiements fictifs que leur fiche décrit, déclarés comme tels. C'est ce qui manquait à C-13 et à B-02 pour être montrés. Aucune règle ne change. Deux heures.

**3. `briefs/B-03-mode-lecture.md`** — le mode lecture de l'article (§3.3). Une demi-journée.

Les corrections d'un lot relu (C-14, B-02, C-09) passent avant le lot en cours, sans attendre que cette file les cite. Preuves proportionnées, rapports courts.

L'incident des douze observations créées par un diagnostic (C-14) est pris en compte : on ne nettoie rien.

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
| C-14 Achat au numéro | 25/11, corrigé le 25/11 | Rendu ; vérification attendue (consigne 0) |
| B-02 Mon compte | 25/11 | Rendu sans `PRET` ; à déposer (consigne 1) |
