# À faire — voie 2 : ce qui se voit

File de la **deuxième session d'Hermès**. Tenue par Claude. **Hermès ne modifie pas ce fichier.**

Mis à jour le 26 novembre 2026, 13 h 30 (passage automatique).

Consigne permanente : `prompts/consigne-permanente.md` (section « Les deux voies »). Doctrine : `doctrine/doctrine.md`.

La voie 1 (`A-FAIRE.md`) s'occupe de l'existant : import, audit, mise à jour. La voie 2 construit, sur un site **entièrement fictif**, ce que Ced peut ouvrir dans un navigateur. Elle ne dépend ni de l'import d'Imagine, ni des maquettes.

## Consignes actives, par ordre de priorité

File du 26/11, 13 h 30. Aucun rapport de ta part depuis 10 h 05 : si tu lis ceci, la file ci-dessous a du travail, et **un rapport court à la fin de ce réveil**, même pour dire ce qui t'a arrêté. **C-21 est code clos** (vérification de 10 h 18 : sept corrections, les tiers préservés). C-22 est relu « à corriger » : sa fusion est arrivée à 10 h 33. Arbitrages : `docs/arbitrages-2026-11-26.md`, passages de 10 h et de 13 h.

**0. Corrections de B-05** (`corrections/B-05.md`) : deux importants, les sept instructions comme la fusion les écrit. Dans le contenu d'un partenaire, un lien dont on ne sait pas dire s'il sort du site est déclaré commercial plutôt qu'oublié. Les liens internes vers la fiche d'un partenaire ne le sont pas : confirmé. Le contrôle de l'accueil doit d'abord trouver des liens d'articles (plus de zéro) avant de dire qu'aucun n'est déclaré commercial.

**1. Corrections de C-22** (`corrections/C-22.md`) : deux importants, un mineur, les trois instructions comme la fusion les écrit.
   - un identifiant de lettre déjà employé, même retiré, est réservé et refusé : c'est une donnée de consentement, l'avertissement d'écran ne suffit pas ;
   - ton vérificateur échoue sur l'arbre livré parce qu'il contrôle l'écriture d'un fichier partagé (que C-21 a légitimement changée) : il contrôle le résultat, la préférence qui sort à l'export et disparaît à l'effacement ;
   - longueurs comptées en caractères ;
   - l'injection dans l'écran de C-10 reste comme elle est, avec un test de présence de la section ;
   - **la place de la section sous le bouton « Enregistrer » ne bouge pas** : c'est une question visuelle posée à Ced.

**2. `briefs/C-23-test-d-etancheite-de-livraison.md`** — une seule commande qui rejoue l'étanchéité de tout ce qui a été construit depuis C-08 : toutes les voies, tous les publics sans droit, le contrôle inverse (§3.9, §4.4). Lecture seule ; ce lot ne modifie pas le paywall, il rapporte. Une demi-journée.

**3. `briefs/B-06-espace-cooperateurs.md`** — l'attribut « coopérateur » posé par l'administration, avec sa source, et l'espace réservé qu'il ouvre (§3.9, §3.12). Il n'ouvre pas les articles. Rien de CoopHub. Une demi-journée.

**Règle rappelée par B-05 et C-21 : un contrôle qui ne peut pas échouer ne prouve rien.** Un contrôle d'absence vérifie d'abord que ce qu'il inspecte existe (la liste n'est pas vide, la page est bien celle attendue) ; un jeu d'essai traverse le vrai chemin (un vrai brouillon de C-16, pas une forme écrite à la main). Une mutation témoin pour chaque contrôle d'absence nouveau.

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
| C-20 Ne pas renouveler | 26/11, corrigé le 26/11 | **Code clos le 26/11**, périmètre réduit : raccord corrigé et couvert sur le vrai adaptateur, écrans sans bouton. §3.4 n'est pas tenu : le bouton passe au branchement sur le staging vérifié. Validation visuelle de Ced attendue |
| C-21 Export et effacement | 26/11, corrigé le 26/11 | **Code clos le 26/11** : sept corrections vérifiées (l'export d'un opérateur ne contient plus rien de son client ; l'effacement préserve les tiers). Validation visuelle de Ced attendue |
| B-05 Partenaires | 26/11 | Relu « à corriger » : deux importants (consigne 0) |
| C-22 Préférences des newsletters | 26/11 | Relu « à corriger » : deux importants (consigne 1). Une question visuelle pour Ced : la section sous le bouton « Enregistrer » |
