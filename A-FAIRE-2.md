# À faire — voie 2 : ce qui se voit

File de la **deuxième session d'Hermès**. Tenue par Claude. **Hermès ne modifie pas ce fichier.**

Mis à jour le 26 novembre 2026, 19 h 30 (passage automatique).

Consigne permanente : `prompts/consigne-permanente.md` (section « Les deux voies »). Doctrine : `doctrine/doctrine.md`.

La voie 1 (`A-FAIRE.md`) s'occupe de l'existant : import, audit, mise à jour. La voie 2 construit, sur un site **entièrement fictif**, ce que Ced peut ouvrir dans un navigateur. Elle ne dépend ni de l'import d'Imagine, ni des maquettes.

## Consignes actives, par ordre de priorité

File du 26/11, 19 h 30. Tes rapports de 17 h 33, 18 h 18 et 19 h sont lus, merci pour eux. **B-06 est relu « à corriger »** (cinq instructions, aucun bloquant). **C-23 est corrigé** et bloqué sur la découverte fermée : je lève le blocage ci-dessous. **C-24 est construit** et bloqué sur une restauration non prouvable octet pour octet : je le lève aussi. Arbitrages : `docs/arbitrages-2026-11-26.md`, passage de 19 h.

**0. Corrections de B-06** (`corrections/B-06.md`), les cinq, telles quelles :
   - les deux règles de rôle (qui pose le statut, qui lit l'espace sans l'avoir) deviennent **deux réglages** dans l'écran de C-10, défaut « Administrateur seul », chaque valeur testée, aucune n'ouvre un article ;
   - une lecture du journal en échec n'est pas un journal vide : dans le doute, l'export et l'effacement se déclarent **incomplets**, jamais complets ;
   - la règle pure du lot entre dans la suite que les relecteurs rejouent (`rejouer.ps1`) ;
   - la source et la date ne s'affichent que si le statut est posé ; un contrôle rejouable sur la collection REST, avec sa mutation ;
   - la présentation de la date (brute, en temps universel) est une question visuelle pour Ced : n'y touche pas.

**1. Finir C-23** (`production/C-23/BLOQUE-V2.md`). **Une découverte fermée n'est pas un prérequis manquant : c'est l'état livré, et il se teste tel quel.**
   - quand le réglage livré est fermé, la ligne « découverte épuisée » devient « découverte fermée à la livraison » : `V-DEC-FIN` est contrôlé comme un compte sans droit, voie par voie, et le reçu dit en une ligne que le cas « épuisé » n'a pas été joué et pourquoi. Le test normal tourne sans rien forcer ;
   - le test lit le réglage, il ne le suppose pas : le jour où la découverte est livrée ouverte, la ligne reprend son sens premier, et un personnage qu'on ne peut alors pas préparer redevient un refus ;
   - le cas « découverte ouverte puis épuisée » se prouve **à part**, dans une recette nommée qui ouvre la découverte, joue le cas et remet le réglage exactement, comme la mutation témoin. Elle n'est pas dans la commande jouée à chaque livraison ; son reçu accompagne le paquet ;
   - rejeu normal vert sous un nom de reçu neuf, puis `PRET`.

**2. Finir C-24** (`production/C-24/TRANSMISSION.md`). **Sur la démonstration, « remis en état » veut dire l'état métier** : rôles, commandes, abonnements, adhésions, profils, réglages, actions métier. Les sessions, données temporaires, caches et verrous du planificateur n'en font pas partie. L'écart de ton premier parcours s'écrit une fois dans tes notes, et le lot se rend : rejoue le harnais corrigé une fois sous un nom de reçu neuf, qualifie les deux mutations en attente, `A-VOIR.md` à jour, `PRET`. La localité reste en choix fermés ; la question est rangée pour Imagine. La section sous le bouton « Enregistrer » reste où elle est : même question visuelle que C-22, posée à Ced.

**3. `briefs/B-07-agenda.md`** — l'agenda : trois types d'événements, inscription simple aux rencontres gratuites, lien externe pour les événements partenaires, balisage minimal (§3.11). Pas de billetterie. Une demi-journée.

**4. `briefs/C-25-retractation-en-ligne.md`** — « Me rétracter » dans Mon compte, en deux étapes, pendant le délai (§3.7) : une demande datée, visible de l'administration, **aucun remboursement, aucune annulation, aucun accès fermé**. Délai et point de départ en réglages. Une demi-journée.

**5. `briefs/B-08-soutenir-et-notre-cooperative.md`** — les deux entrées du menu qui n'ont rien derrière : « Notre coopérative » et ses sous-pages aux intitulés du §3.12, « Soutenir » (don éteint par réglage, prise de parts par lien), formulaire « Proposer un sujet ». Rien de CoopHub, aucun paiement. Une demi-journée.

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
| C-23 Test d'étanchéité de livraison | 26/11, corrigé le 26/11 | Relu « à corriger » (un bloquant du détecteur : témoin non cherché dans les attributs et les commentaires ; aucune fuite constatée sur le site). Six corrections faites, `PRET` retiré : reste le rejeu normal sur la découverte fermée (consigne 1) |
| B-06 Espace coopérateurs | 26/11 | Relu « à corriger », aucun bloquant : cinq instructions (consigne 0) |
| C-24 Formulaire de personnalisation | 26/11 | Construit, sans `PRET` : à finir (consigne 2) |
