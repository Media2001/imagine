# À faire — voie 2 : ce qui se voit

File de la **deuxième session d'Hermès**. Tenue par Claude. **Hermès ne modifie pas ce fichier.**

Mis à jour le 26 novembre 2026, 4 h 30 (passage automatique).

Consigne permanente : `prompts/consigne-permanente.md` (section « Les deux voies »). Doctrine : `doctrine/doctrine.md`.

La voie 1 (`A-FAIRE.md`) s'occupe de l'existant : import, audit, mise à jour. La voie 2 construit, sur un site **entièrement fictif**, ce que Ced peut ouvrir dans un navigateur. Elle ne dépend ni de l'import d'Imagine, ni des maquettes.

## Consignes actives, par ordre de priorité

Tes rapports de 1 h 26 à 4 h 11 sont lus, merci pour eux : C-17, C-18 et C-19 rendus, huit corrections de C-16, profil A-PAPIER remis en état (C-09 : 382 sur 382), arrêt sur C-20. Ton arrêt sur C-20 était le bon. Arbitrages : `docs/arbitrages-2026-11-26.md`, passage de 4 h.

**0. Corrections de C-17** (`corrections/C-17.md`, fusion de 4 h 08) : les quatre instructions, dans l'ordre. Plus une cinquième, tranchée ici : **ce que le site conserve après la décision.** Mon brief disait cinq champs ; le cahier des charges (§4.4) dit « la catégorie et la date de fin », et c'est lui la référence. Le dossier de l'abonné ne garde donc que **la catégorie, la date de fin et l'état** (l'état sert au statut affiché dans Mon compte, §3.7). La date de la décision et le nom de l'opérateur vont dans le journal de l'administration de C-10, pas dans la fiche de la personne ; l'écran du référent les relit depuis le journal s'il en a besoin. Un test relit le dossier après validation et après refus : trois champs, pas un de plus. La capacité « traiter les justificatifs » reste donnée par le seul jeu de démonstration.

**1. Corrections de C-18** (`corrections/C-18.md`, fusion de 4 h 18) : le filtre par état s'appuie sur la clé d'état, pas sur le libellé traduit (important) ; pagination native éprouvée avec une correspondance en deuxième page ; `A-VOIR.md` mis à jour ; les autres mineurs comme la fusion les écrit. Une ligne par abonnement et filtre de localité exact : confirmés, les deux questions sont rangées pour Imagine.

**2. Relectures de C-16 (corrigé à 3 h 57) et de C-19** : si l'une revient « à corriger », elle passe avant la suite. Adresse enregistrée sur le seul compte créé, réglage oui ou non : confirmé, question rangée pour Imagine.

**3. `briefs/C-20-ne-pas-renouveler-2.md`** — deuxième passe. L'accès qui se fermait venait de notre raccord, qui lit mal un état de Memberships : l'interdiction de toucher au raccord est levée, pas celle de toucher à la bibliothèque C-06 ni aux règles de C-13. Le quatre-fois passe par la date de fin native de l'abonnement, à prouver d'abord par ta sonde. Une demi-journée.

**4. `briefs/C-21-export-et-effacement.md`** — l'export et l'effacement des données d'un compte par les outils natifs de WordPress, étendus à ce que nos lots ont ajouté (§4.4). Aucun réglage de conservation modifié. Inclut le justificatif de C-17 (son nettoyage à la suppression du compte est l'instruction 3 de la fusion) ; dis dans l'inventaire ce que le journal de l'administration garde d'une personne. Une demi-journée.

**5. `briefs/B-05-partenaires.md`** — le bloc « partenaire du mois », la page « Nos partenaires », l'étiquette « Partenariat », les liens déclarés commerciaux (§3.12). Une demi-journée.

**6. `briefs/C-22-preferences-newsletters.md`** — le centre de préférences des newsletters dans Mon compte et la page « Nos newsletters » (§3.10). Les choix restent sur le site : aucun appel à Brevo, aucun email. Une demi-journée.

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
| C-16 Commande pour un client | 26/11, corrigé le 26/11 | Huit corrections rendues à 3 h 57 ; vérification attendue |
| C-17 Justificatifs du tarif solidaire | 26/11 | Relu « à corriger » : trois importants, et les champs conservés alignés sur §4.4 (consigne 0) |
| C-18 Extractions | 26/11 | Relu « à corriger » : un important, trois mineurs (consigne 1) |
| C-19 Tableau de bord | 26/11 | Rendu ; relecture attendue |
| C-20 Ne pas renouveler | — | Arrêté à 4 h 11 sur un blocage démontré ; deuxième passe en file (consigne 3) |
