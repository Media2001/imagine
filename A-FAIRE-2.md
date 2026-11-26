# À faire — voie 2 : ce qui se voit

File de la **deuxième session d'Hermès**. Tenue par Claude. **Hermès ne modifie pas ce fichier.**

Mis à jour le 26 novembre 2026, 7 h 30 (passage automatique).

Consigne permanente : `prompts/consigne-permanente.md` (section « Les deux voies »). Doctrine : `doctrine/doctrine.md`.

La voie 1 (`A-FAIRE.md`) s'occupe de l'existant : import, audit, mise à jour. La voie 2 construit, sur un site **entièrement fictif**, ce que Ced peut ouvrir dans un navigateur. Elle ne dépend ni de l'import d'Imagine, ni des maquettes.

## Consignes actives, par ordre de priorité

Tes rapports de 4 h 45 à 6 h 46 sont lus, merci pour eux. **C-16, C-17, C-18 et C-19 sont code clos** ; il ne leur manque que l'œil de Ced. Ton second arrêt sur C-20 était encore le bon : tu n'as forcé ni un droit postal ni une marge. Arbitrages : `docs/arbitrages-2026-11-26.md`, passage de 7 h.

**0. C-20 : dépose `PRET` sur l'état actuel, sans rien y ajouter.** Un quart d'heure. Le périmètre du lot est réduit par arbitrage :
   - le raccord corrigé (adhésion « en attente d'annulation » liée à un abonnement en annulation à terme : active jusqu'à la date de fin) est le livrable principal ;
   - **mon critère sur la liste d'envoi était faux** : quand le terme payé tombe avant la clôture du prochain numéro, l'abonné qui ne renouvelle pas sort de la liste, et c'est ce que disent les règles de C-13. Ta réception « rouge » sur ce point devient le comportement attendu : renomme-la ou retourne son assertion, sans toucher aux règles ;
   - quatre-fois : pas de bouton, la phrase « faites la demande auprès d'Imagine ». On ne donne pas de valeur à la marge de C-05 pour les besoins d'une preuve ;
   - reprise : pas de bouton, les produits de la démonstration sont privés ;
   - le bouton « ne pas renouveler », sa confirmation et l'émission de `imagine_non_renouvellement_confirme` **ne sont pas dans ce lot** : aucun profil de la démonstration n'est en renouvellement automatique, et on ne fabrique pas de passerelle. Ils passent au branchement sur le staging vérifié.
   `A-VOIR.md` dit en tête, en trois lignes, ce que Ced voit et ce qui est reporté. Les relecteurs jugeront ce périmètre-là, pas le brief d'origine.

**1. Relectures de C-20, puis de C-21** : si l'une revient « à corriger », elle passe avant la suite.

**2. `briefs/C-21-export-et-effacement.md`** — en cours chez toi. L'export et l'effacement des données d'un compte par les outils natifs de WordPress, étendus à ce que nos lots ont ajouté (§4.4). Aucun réglage de conservation modifié. Depuis C-17, la date d'une décision sur un justificatif et son opérateur vivent dans le journal de l'administration : dis dans l'inventaire ce que ce journal garde d'une personne et ce que l'effacement en fait. Une demi-journée.

**3. `briefs/B-05-partenaires.md`** — le bloc « partenaire du mois », la page « Nos partenaires », l'étiquette « Partenariat », les liens déclarés commerciaux (§3.12). Une demi-journée.

**4. `briefs/C-22-preferences-newsletters.md`** — le centre de préférences des newsletters dans Mon compte et la page « Nos newsletters » (§3.10). Les choix restent sur le site : aucun appel à Brevo, aucun email. Une demi-journée.

**C-19, pour mémoire.** Q-1 est tranchée au plus fermé : la composition actuelle des deux droits reste, aucun rôle n'est modifié ; la question est rangée pour Imagine. Q-2 : la ligne grisée « Par moyen de paiement » reste. Tu n'as rien à faire.

**Kiosque de B-04** : l'étiquette d'accès reste telle quelle, c'est une question visuelle posée à Ced ; ne la retire pas de toi-même. **Profils de C-09** : un lot qui fait changer d'état un profil le remet dans son état de départ, action planifiée comprise, et le relit avant de rendre.

Les corrections d'un lot relu passent avant le lot en cours, sans attendre que cette file les cite. Preuves proportionnées, rapports courts. **Un rapport dans `files/rapports/` à chaque fin de réveil**, même de cinq lignes : c'est ce que le passage automatique lit en premier.

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
| B-02 Mon compte | 25/11, corrigé le 25/11 | **Code clos le 26/11** : dix corrections vérifiées, règles isolées en code pur. Recette partielle assumée : marge, historique, documents. Validation visuelle de Ced attendue |
| C-09 Complément paiements fictifs | 25/11 | **Code clos le 25/11** : 9 profils créés, 20 partiels, 1 impossible ; paiements fictifs déclarés comme tels. Liens « offert » et « groupé » non fabriqués |
| B-03 Mode lecture | 25/11, corrigé le 25/11 | **Code clos le 25/11** : couleurs du contenu neutralisées sur les trois fonds, position de lecture conservée. Validation visuelle de Ced attendue, contraste à revoir après le choix des couleurs par le designer |
| B-04 Page numéro, kiosque, thématiques | 25/11, corrigé le 26/11 | **Code clos le 26/11** : six corrections vérifiées (découverte lisible dans les listes sans être consommée, possession séparée de la lecture du PDF). Validation visuelle de Ced attendue, avec une question : étiquette d'accès sur le kiosque, oui ou non |
| C-15 Écran des échéances | 25/11, corrigé le 25/11 | **Code clos le 26/11** : huit corrections vérifiées. Validation visuelle de Ced attendue |
| C-16 Commande pour un client | 26/11, corrigé le 26/11 | **Code clos le 26/11** : huit corrections vérifiées, double création sous concurrence fermée. Validation visuelle de Ced attendue |
| C-17 Justificatifs du tarif solidaire | 26/11, corrigé le 26/11 | **Code clos le 26/11** : cinq corrections vérifiées ; le dossier ne garde que catégorie, date de fin et état (§4.4), à défaire si Ced préfère. Validation visuelle de Ced attendue |
| C-18 Extractions | 26/11, corrigé le 26/11 | **Code clos le 26/11** : trois corrections vérifiées, filtre sur la clé d'état. Validation visuelle de Ced attendue |
| C-19 Tableau de bord | 26/11, corrigé le 26/11 | **Code clos le 26/11** : quatre corrections vérifiées ; droit d'accès laissé tel quel (les deux droits), « par moyen de paiement » grisé. Validation visuelle de Ced attendue |
| C-20 Ne pas renouveler | 26/11, en partie | Raccord corrigé, écrans sans bouton ; `PRET` à déposer tel quel (consigne 0). Le bouton passe au branchement sur le staging vérifié |
