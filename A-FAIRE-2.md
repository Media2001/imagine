# À faire — voie 2 : ce qui se voit

File de la **deuxième session d'Hermès**. Tenue par Claude. **Hermès ne modifie pas ce fichier.**

Mis à jour le 26 novembre 2026, 16 h 30 (passage automatique).

Consigne permanente : `prompts/consigne-permanente.md` (section « Les deux voies »). Doctrine : `doctrine/doctrine.md`.

La voie 1 (`A-FAIRE.md`) s'occupe de l'existant : import, audit, mise à jour. La voie 2 construit, sur un site **entièrement fictif**, ce que Ced peut ouvrir dans un navigateur. Elle ne dépend ni de l'import d'Imagine, ni des maquettes.

## Consignes actives, par ordre de priorité

File du 26/11, 16 h 30. Tes rapports de 14 h 43, 15 h 20 et 16 h 19 sont lus, merci pour eux. **B-05 et C-22 sont code clos** (vérifications de 15 h 33 et 15 h 38 : sept et trois corrections appliquées). **C-23 est rendu**, en relecture : 1 432 contrôles, aucune fuite, la mutation fait rougir. Arbitrages : `docs/arbitrages-2026-11-26.md`, passage de 16 h.

**0. `briefs/B-06-espace-cooperateurs.md`** — en cours chez toi. L'attribut « coopérateur » posé par l'administration, avec sa source, et l'espace réservé qu'il ouvre (§3.9, §3.12). Il n'ouvre pas les articles. Rien de CoopHub. Quand il est rendu, **ajoute ses pages à la matrice de C-23** (le contenu de l'espace, pour un non-coopérateur) : le test de livraison suit ce qu'on construit.

**1. `briefs/C-24-formulaire-de-personnalisation.md`** — « Personnalisez ce que vous recevez » dans Mon compte : des questions qui sont un réglage, des réponses qui deviennent des étiquettes sur le compte, un consentement distinct (§3.7, §3.10, §4.4). Rien ne part vers Brevo. Une demi-journée.

**2. `briefs/B-07-agenda.md`** — l'agenda : trois types d'événements, inscription simple aux rencontres gratuites, lien externe pour les événements partenaires, balisage minimal (§3.11). Pas de billetterie. Une demi-journée.

**Sur C-23, en attendant sa relecture** : ton choix de ne pas corriger le paywall dans ce lot est le bon ; le script de récupération reste hors du rejeu courant, comme tu l'as écrit. Les plans de site sont fermés sur la démonstration : le jour où ils s'ouvrent, ces quatre lignes de la matrice changent de sens, et le test devra y chercher les témoins. **Rangement** : un relecteur signale `production/B-05/correction-preparation-V2.log` ; si ce n'est pas une preuve du paquet, sors-le.

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
| B-05 Partenaires | 26/11, corrigé le 26/11 | **Code clos le 26/11** : sept corrections vérifiées (un lien dont on ne sait pas dire s'il sort du site est déclaré commercial ; le contrôle de l'accueil trouve d'abord des liens). Validation visuelle de Ced attendue ; la distinction graphique de l'étiquette « Partenariat » relève du designer |
| C-22 Préférences des newsletters | 26/11, corrigé le 26/11 | **Code clos le 26/11** : trois corrections vérifiées (un identifiant déjà employé est réservé et refusé, même après effacement du compte ; longueurs en caractères). Validation visuelle de Ced attendue, avec une question : la section sous le bouton « Enregistrer » |
| C-23 Test d'étanchéité de livraison | 26/11 | Rendu, en relecture : 101 voies, 14 publics, aucune fuite. Limites : cache d'hébergement et robots réellement vérifiés hors de portée de la démonstration ; plans de site fermés |
