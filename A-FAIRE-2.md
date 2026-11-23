# À faire — voie 2 : ce qui se voit

File de la **deuxième session d'Hermès**. Tenue par Claude. **Hermès ne modifie pas ce fichier.**

Mis à jour le 23 novembre 2026, 16 h 30.

Consigne permanente : `prompts/consigne-permanente.md` (section « Les deux voies »). Doctrine : `doctrine/doctrine.md`.

La voie 1 (`A-FAIRE.md`) s'occupe de l'existant : import, audit, mise à jour. La voie 2 construit, sur un site **entièrement fictif**, ce que Ced peut ouvrir dans un navigateur. Elle ne dépend ni de l'import d'Imagine, ni des maquettes.

## Consignes actives, par ordre de priorité

**Tes rapports jusqu'à 16 h 17 sont lus. Les questions des fusions B-00 et B-01 sont arbitrées : `docs/arbitrages-2026-11-23.md`.** Ce sont des questions techniques, Ced n'a pas à y répondre.

**0. Corrections de B-00 puis de B-01** — `corrections/B-00.md`, `corrections/B-01.md`, avec les arbitrages ci-dessus. Le bloquant B00-01 d'abord : le site doit se reconstruire après C-08 et C-09. Redépose `PRET` et mets à jour les deux `A-VOIR.md`. **Passe avant C-10.**

Rappel : Novamira est permis sur `imagine-test-demo` (file du 23/11, 13 h 45), et nulle part ailleurs. Les écarts que tu signales sont reportés par Claude dans `docs/ecarts.md`.

**1. `briefs/B-00-site-de-demonstration.md`** — le site `imagine-test-demo`, reconstruit par un script, avec numéros et articles fictifs. Une demi-journée. **Passe avant tout : les autres se branchent dessus.**

**2. `briefs/B-01-squelette-du-theme.md`** — tous les gabarits, sans habillage. Une demi-journée.

**3. `briefs/C-08-paywall-sur-article.md`** — la décision d'accès branchée sur un vrai article, avec le test d'étanchéité. Une demi-journée.

**4. `briefs/C-09-profils-de-test.md`** — les trente profils créés par script. Une demi-journée.

**5. `briefs/C-10-ecran-de-reglages.md`** — un écran « Imagine › Réglages » dans l'administration. Une demi-journée.

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
| — | — | — |
