# À faire — voie 2 : ce qui se voit

File de la **deuxième session d'Hermès**. Tenue par Claude. **Hermès ne modifie pas ce fichier.**

Mis à jour le 23 novembre 2026, 13 h 45.

Consigne permanente : `prompts/consigne-permanente.md` (section « Les deux voies »). Doctrine : `doctrine/doctrine.md`.

La voie 1 (`A-FAIRE.md`) s'occupe de l'existant : import, audit, mise à jour. La voie 2 construit, sur un site **entièrement fictif**, ce que Ced peut ouvrir dans un navigateur. Elle ne dépend ni de l'import d'Imagine, ni des maquettes.

## Consignes actives, par ordre de priorité

**Réponse à ton rapport de 12 h 53 : oui, débloqué.** Tu as bien fait de t'arrêter ; l'interdiction venait de mon brief, pas d'une règle de fond. Pour `imagine-test-demo`, **la création normale par l'outil est autorisée telle quelle**, avec ce qu'elle installe d'office (Novamira, sa licence, la préparation MCP), comme pour les sites de test de la voie 1 (accord de Ced du 22/11). Le site est entièrement fictif : tu peux y utiliser Novamira si cela te sert, `wp-cli` sinon. La règle « Novamira seulement sur un staging vérifié » protège les données réelles ; elle ne s'applique pas à un site qui n'en contient aucune. Ce qui reste interdit : connecter le site à WooCommerce.com, activer une licence d'extension commerciale, une passerelle réelle, un email sortant.

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
