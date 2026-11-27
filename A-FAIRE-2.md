# À faire — voie 2 : ce qui se voit

File de la **deuxième session d'Hermès**. Tenue par Claude. **Hermès ne modifie pas ce fichier.**

Mis à jour le 27 novembre 2026, 1 h 30 (passage automatique).

Consigne permanente : `prompts/consigne-permanente.md` (section « Les deux voies »). Doctrine : `doctrine/doctrine.md`.

La voie 1 (`A-FAIRE.md`) s'occupe de l'existant : import, audit, mise à jour. La voie 2 construit, sur un site **entièrement fictif**, ce que Ced peut ouvrir dans un navigateur. Elle ne dépend ni de l'import d'Imagine, ni des maquettes.

## Consignes actives, par ordre de priorité

File du 27/11, 1 h 30. Tes quatre rapports de 22 h 33 à 0 h 31 sont lus, merci : toute la file de 22 h 30 est rendue. **B-07, C-24 et C-25 sont code clos** (vérifications « prêt »). **C-26** : rendu, en relecture, rien à faire. **B-08** : relu « à corriger », deux importants. Arbitrages : `docs/arbitrages-2026-11-27.md`, passage de 1 h.

**0. Corrections de B-08** (`corrections/B-08.md`), les sept :
   - une proposition contenant un antislash est aujourd'hui refusée et perdue : écris les métadonnées selon la convention de WordPress (valeurs échappées à l'écriture, valeurs propres pour la relecture) ; **corrige d'abord le bouchon** qui masquait le défaut, puis un cas d'essai du formulaire jusqu'au détail de l'administration et à l'export ;
   - la création du menu se reprend après une interruption : un témoin posé dès la création, pas une option écrite à la fin ; un menu ou un élément étranger reste refusé ;
   - le lien de prise de parts n'accepte que `https` : confirmé ;
   - une entrée de menu ne reçoit une adresse que si sa cible existe ;
   - la section B-08 du README de l'extension ; B-06 et B-07 aussi si c'est au même coût ;
   - la colonne de liste de l'administration est facultative.

**1. `briefs/B-09-autres-pages.md`** — FAQ du service client (quatre rubriques du §3.14, vides), pages légales (la page de confidentialité native, CGV, cookies ; pas de bandeau), formulaire de contact sur la mécanique corrigée de B-08, le tout dans un menu de pied de page reprenable. Rien ne part. Une demi-journée.

**2. `briefs/C-27-comment-nous-avez-vous-connus.md`** — la question du §3.7, **après** le paiement, facultative, à réponses fermées en réglage ; une réponse par commande ; des nombres par réponse pour l'administration ; export et effacement. Trois heures.

**3. `briefs/B-10-points-de-vente.md`** — la page du §3.14 : recherche par localité ou code postal, liste, chargement d'un fichier par correspondance de colonnes (fichier d'essai fictif). **Pas de fond de carte par défaut**, aucun appel à un tiers. Une demi-journée.

**Règle nouvelle, venue de C-25 puis de B-08 : un bouchon reproduit le déséchappement de WordPress.** Deux lots de suite ont perdu un antislash parce que le bouchon de test rangeait les valeurs telles quelles, là où WordPress les déséchappe à l'écriture. Tout bouchon d'une fonction d'écriture (`wp_insert_post`, `add_*_meta`, `update_option` quand il y a lieu) reproduit ce comportement, et tout champ de texte libre a un cas d'essai avec un antislash, du formulaire jusqu'à l'export.

**L'écran de réglages de C-10** : trois lots y insèrent leur section sous le bouton « Enregistrer » (C-22, C-24, C-25). On n'y touche pas pour l'instant, ni pour déplacer, ni pour ouvrir un point d'accroche : la place est une question posée à Ced, et les deux se feront en une fois après sa réponse. Un lot nouveau qui a un réglage fait comme ces trois-là.

**Une correction ne fait pas entrer de fonction nouvelle.** Dans C-23, la couverture des pages coopérateurs est arrivée pendant le tour de correction : elle était utile, mais elle a échappé aux deux relectures. Une idée de ce genre se note dans le rapport ; elle devient un lot.

**Style PSR-12** : la règle de la doctrine reste, mais on ne reformate ni lot par lot, ni maintenant (cela périmerait les reçus des lots code clos). Un seul passage d'ensemble viendra au gel du code. Écris le code neuf au plus près de PSR-12, sans retoucher l'existant pour cela.

**Règle de proportion, rappelée par C-24** : une restauration se prouve sur l'état métier. Si une preuve plus fine t'échappe sur le site fictif, écris l'écart et continue ; ne multiplie pas les rejeux pour elle.

**Rangement** : un relecteur signalait `production/B-05/correction-preparation-V2.log` ; si ce n'est pas une preuve du paquet, sors-le.

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
| C-23 Test d'étanchéité de livraison | 26/11, corrigé le 26/11 | **Code clos le 26/11** : six corrections vérifiées (témoins cherchés dans la réponse brute, redirections inspectées, aucun réglage forcé ; découverte fermée contrôlée telle quelle, cas « épuisé » prouvé à part). La couverture des pages coopérateurs n'a pas eu ses deux relectures : elle les aura avec C-26 |
| B-06 Espace coopérateurs | 26/11, corrigé le 26/11 | **Code clos le 26/11** : cinq corrections vérifiées (deux réglages de rôle, défaut « Administrateur seul » ; un journal illisible rend l'export et l'effacement incomplets). Validation visuelle de Ced attendue, avec une question : la présentation de la date du statut |
| C-24 Formulaire de personnalisation | 26/11, corrigé le 26/11 | **Code clos le 27/11** : cinq corrections vérifiées (la restauration après un échec du journal restaure vraiment ; seule une inscription choisie par le lecteur ouvre la transmission). Validation visuelle de Ced attendue, avec la question de la section sous le bouton « Enregistrer » |
| B-07 Agenda | 26/11, corrigé le 26/11 | **Code clos le 27/11** : huit corrections vérifiées (lien d'un événement partenaire déclaré commercial, export qui échoue au lieu de rendre une page vide, adaptateur dans la suite rejouable). Validation visuelle de Ced attendue |
| C-25 Rétractation en ligne | 26/11, corrigé le 27/11 | **Code clos le 27/11** : quatre corrections vérifiées (réglages journalisés avec retour à l'ancienne valeur si le journal échoue ; un motif avec antislash est gardé). Une demande, aucun effet automatique. Validation visuelle de Ced attendue ; délai et effets à faire valider par Imagine et son conseil |
| B-08 « Soutenir » et « Notre coopérative » | 26/11 | Relu « à corriger » le 27/11, deux importants, aucun bloquant : sept instructions (consigne 0) |
| C-26 Étanchéité des sorties nouvelles | 27/11 | Rendu à 0 h 33, en relecture |
