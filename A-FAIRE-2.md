# À faire — voie 2 : ce qui se voit

File de la **deuxième session d'Hermès**. Tenue par Claude. **Hermès ne modifie pas ce fichier.**

Mis à jour le 26 novembre 2026, 1 h 30 (passage automatique).

Consigne permanente : `prompts/consigne-permanente.md` (section « Les deux voies »). Doctrine : `doctrine/doctrine.md`.

La voie 1 (`A-FAIRE.md`) s'occupe de l'existant : import, audit, mise à jour. La voie 2 construit, sur un site **entièrement fictif**, ce que Ced peut ouvrir dans un navigateur. Elle ne dépend ni de l'import d'Imagine, ni des maquettes.

## Consignes actives, par ordre de priorité

Tes rapports de 0 h 00, 0 h 29 et 0 h 45 sont lus, merci pour eux : six corrections de B-04, C-16 rendu, suite complète revenue au vert (1 040 tests). **B-02, B-04 et C-15 sont vérifiés : code clos.** C-16 attend sa relecture. Arbitrages : `docs/arbitrages-2026-11-26.md`.

**0. Corrections et relecture de C-16** : si elle revient « à corriger » (`corrections/C-16.md` plus récent que ton `PRET`), elle passe avant tout le reste. Tes décisions à défaut sont confirmées : création différée à la confirmation, brouillon privé d'une heure, un seul marqueur « sans email » pour tout le site (celui de C-13, désormais posé par le jeu de profils), correctif du chemin du jeu de test de B-04. **Kiosque de B-04** : l'étiquette d'accès reste telle quelle, c'est une question visuelle posée à Ced ; ne la retire pas de toi-même.

**1. Profil A-PAPIER : remets son action planifiée.** Tu as bien fait de ne pas inventer d'échéance. Tranché : rejoue le jeu de profils de C-09 pour ce profil (son calendrier est le sien, rien n'est inventé, le site est fictif), relis l'abonnement et son action, et la lecture native de C-09 doit revenir entièrement verte. S'il faut rejouer tout le jeu, fais-le quand aucune recette ne tourne, et dis-le. **Règle pour la suite** : un lot qui fait changer d'état un profil de C-09 le remet dans son état de départ, action planifiée comprise, et le relit avant de rendre. Un quart d'heure, à faire avant de reprendre C-17 si tu y es encore, sinon tout de suite.

**2. `briefs/C-17-justificatifs-tarif-solidaire.md`** — en cours chez toi. Le dépôt du justificatif dans « Mon compte », la file de validation côté administration, le fichier hors racine publique et supprimé à la décision (§3.13, §4.4). Ne touche ni au prix ni à l'accès. Une demi-journée.

**3. `briefs/C-18-extractions.md`** — l'écran des extractions au format tableur, quatre extractions de départ, lecture seule (§3.13). Une demi-journée.

**4. `briefs/C-19-tableau-de-bord.md`** — l'écran du tableau de bord : quatre indicateurs que les données permettent aujourd'hui, chacun avec la phrase qui dit comment il est compté ; les autres grisés, aucune formule inventée (§3.13). Une demi-journée.

**5. `briefs/C-20-ne-pas-renouveler.md`** — « Ne pas renouveler » dans « Mon compte », avec la date de fin et les numéros encore dus (§3.7). Le standard d'abord. Aucun email, pas de rétractation. Une demi-journée.

**6. `briefs/C-21-export-et-effacement.md`** — l'export et l'effacement des données d'un compte par les outils natifs de WordPress, étendus à ce que nos lots ont ajouté (§4.4). Aucun réglage de conservation modifié. Une demi-journée.

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
| C-16 Commande pour un client | 26/11 | Rendu ; relecture attendue (consigne 0) |
