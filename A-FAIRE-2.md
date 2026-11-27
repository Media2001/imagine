# À faire — voie 2 : ce qui se voit

File de la **deuxième session d'Hermès**. Tenue par Claude. **Hermès ne modifie pas ce fichier.**

Mis à jour le 27 novembre 2026, 22 h 30 (passage automatique).

Consigne permanente : `prompts/consigne-permanente.md` (section « Les deux voies »). Doctrine : `doctrine/doctrine.md`.

La voie 1 (`A-FAIRE.md`) s'occupe de l'existant : import, audit, mise à jour. La voie 2 construit, sur un site **entièrement fictif**, ce que Ced peut ouvrir dans un navigateur. Elle ne dépend ni de l'import d'Imagine, ni des maquettes.

## Consignes actives, par ordre de priorité

File du 27/11, 22 h 30. Tes rapports de 21 h 18, 21 h 36, 21 h 59 et 22 h 17 sont lus, merci : la reprise, les corrections de C-29, B-13 et B-14 rendus avec leur `PRET`. Aucun des trois n'est encore vérifié ou relu : tu continues sans les attendre, et leurs corrections passeront avant le lot en cours si elles arrivent. Arbitrages : `docs/arbitrages-2026-11-27.md`, passage de 22 h.

Les paquets de la voie 1 que ton rejeu trouve rouges (A-32, A-33 ce soir) ne sont pas à toi : continue à les signaler sans y toucher. **Ils ne bloquent pas la clôture de tes lots** : un lot se clôt sur la ligne `REJEU … PASS`, la ligne `OUTILS` sans échec et son propre vérificateur ; un paquet rouge ne bloque que s'il appartient au lot, ou à un lot clos ou porteur d'un `PRET`.

**Règle du contrat (16 h 30), qui reste : le fichier d'amorçage partagé se contrôle par contrat, jamais par son empreinte entière.** Le vérificateur d'un lot contrôle l'empreinte de **ses** fichiers, la présence dans `imagine-site.php` de **son** bloc d'enregistrement, tel que livré, une seule fois, et **sa** section du README. Tu ne rouvres aucun lot code clos pour cela, et tu ne refais plus de réception complémentaire des voisins pour une simple ligne d'amorçage. Le petit socle commun que tu as écrit pour cela (`lot_reception_contract.py`) est bien : les lots suivants s'en servent, sans l'étendre. La règle « un fichier partagé changé pour un lot se rejoue avant de rendre » reste pour tout le reste (un appel ajouté dans le fichier d'un autre lot, un bouchon commun).

**À savoir sur tes trois lots rendus.**
   - **C-29** : corrections lues ; borner son lecteur à ses propres fichiers pendant B-13 est conforme à la règle du contrat. Vérification attendue ;
   - **B-13** : « Connexion » comme libellé pour un lecteur connecté est une question de présentation, notée pour Ced ; n'y touche pas. La sélection manuelle des articles reste une question pour Imagine, non construite : c'est bien ;
   - **B-14** : le retrait de « Derniers articles » suit le §3.2. B-05, clos, n'est pas modifié ; la relecture dira si son contrôle de l'accueil doit être déclaré sans objet.

**1. `briefs/B-15-pied-de-page.md`** — §3.2 : cinq zones identiques sur toutes les pages (abonnement, newsletter, numéro en cours, point de vente, mentions). **Aucune géolocalisation** : un lien vers la recherche de B-10. Deux à trois heures. Si tu l'as déjà rendu, passe à la suite.

**2. `briefs/B-16-la-page-article.md`** — §3.3 : ce qui entoure le texte d'un article. Résumé et mots-clés en tête, signature, numéro d'origine, appel à l'abonnement en fin d'article pour qui a lu le texte complet sans être abonné. Structure seule ; le rendu du texte par C-08 et le mode lecture de B-03 ne changent pas. Trois heures.

**3. `briefs/C-30-offre-de-bienvenue-et-code-suivi.md`** — §3.7, §3.14 : la page « Bienvenue » atteinte par un QR code, et son code suivi rangé sur la commande payée, compté par code. **L'offre n'offre rien** : aucun prix modifié, aucun code de réduction. Aucun traceur. Trois heures.

**4. `briefs/C-31-adresses-jetables-a-l-inscription.md`** — §3.9 : une liste de domaines refusés à l'inscription, en réglage, vide par défaut. Aucune liste téléchargée, aucun service tiers. Deux heures.

Pour les réglages de C-30 et de C-31 : la règle de l'écran de C-10 plus bas vaut toujours (comme les quatre sections existantes, ou un écran à soi comme B-10).

**Le test d'étanchéité vivant est celui de C-26.** Les lots de cette file ne l'étendent pas ; ils prouvent leur étanchéité avec les témoins de C-26. La matrice sera étendue une fois, plus tard, par un lot.

**Règle venue de C-28 et de B-11 : un fichier partagé changé pour un lot se rejoue avant de rendre.** L'appel ajouté dans `AchatsNumeros.php` a fait échouer un test de B-04 et périmé la réception de B-11, qui n'avait pas bougé. Quand un lot touche un fichier qu'un autre lot non clos a scellé, tu le dis en tête du rapport et tu refais la réception du voisin dans le même réveil, historiques conservés. **Exception depuis 16 h 30 : la ligne d'enregistrement d'un lot dans l'amorçage et sa section du README**, contrôlées par contrat (règle en tête).

**Les messages de visiteurs et l'import** : continue à écrire, pour tout nouveau contenu saisi par un visiteur, où il est rangé. L'import de la voie 1 est gelé et n'est pas rouvert pour cela.

**Règle nouvelle, venue de C-25 puis de B-08 : un bouchon reproduit le déséchappement de WordPress.** Deux lots de suite ont perdu un antislash parce que le bouchon de test rangeait les valeurs telles quelles, là où WordPress les déséchappe à l'écriture. Tout bouchon d'une fonction d'écriture (`wp_insert_post`, `add_*_meta`, `update_option` quand il y a lieu) reproduit ce comportement, et tout champ de texte libre a un cas d'essai avec un antislash, du formulaire jusqu'à l'export.

**L'écran de réglages de C-10** : quatre lots y insèrent leur section sous le bouton « Enregistrer » (C-22, C-24, C-25, C-27). On n'y touche pas pour l'instant, ni pour déplacer, ni pour ouvrir un point d'accroche : la place est une question posée à Ced, et les deux se feront en une fois après sa réponse. Un lot nouveau qui a un réglage fait comme ces quatre-là, ou prend un écran à lui comme B-10.

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
| C-23 Test d'étanchéité de livraison | 26/11, corrigé le 26/11 | **Code clos le 26/11** : six corrections vérifiées (témoins cherchés dans la réponse brute, redirections inspectées, aucun réglage forcé ; découverte fermée contrôlée telle quelle, cas « épuisé » prouvé à part). La couverture des pages coopérateurs a eu ses relectures avec C-26 le 27/11 : réserve levée. Paquet devenu historique, le test à jour est celui de C-26 |
| B-06 Espace coopérateurs | 26/11, corrigé le 26/11 | **Code clos le 26/11** : cinq corrections vérifiées (deux réglages de rôle, défaut « Administrateur seul » ; un journal illisible rend l'export et l'effacement incomplets). Validation visuelle de Ced attendue, avec une question : la présentation de la date du statut |
| C-24 Formulaire de personnalisation | 26/11, corrigé le 26/11 | **Code clos le 27/11** : cinq corrections vérifiées (la restauration après un échec du journal restaure vraiment ; seule une inscription choisie par le lecteur ouvre la transmission). Validation visuelle de Ced attendue, avec la question de la section sous le bouton « Enregistrer » |
| B-07 Agenda | 26/11, corrigé le 26/11 | **Code clos le 27/11** : huit corrections vérifiées (lien d'un événement partenaire déclaré commercial, export qui échoue au lieu de rendre une page vide, adaptateur dans la suite rejouable). Validation visuelle de Ced attendue |
| C-25 Rétractation en ligne | 26/11, corrigé le 27/11 | **Code clos le 27/11** : quatre corrections vérifiées (réglages journalisés avec retour à l'ancienne valeur si le journal échoue ; un motif avec antislash est gardé). Une demande, aucun effet automatique. Validation visuelle de Ced attendue ; délai et effets à faire valider par Imagine et son conseil |
| B-08 « Soutenir » et « Notre coopérative » | 26/11, corrigé le 27/11 | **Code clos le 27/11** : six corrections vérifiées (une proposition avec antislash est gardée jusqu'à l'export ; le menu se reprend après une interruption ; lien de prise de parts en `https` seulement) ; colonne de liste, facultative, non faite. Validation visuelle de Ced attendue |
| C-26 Étanchéité des sorties nouvelles | 27/11, corrigé le 27/11 | **Code clos le 27/11** : dix corrections vérifiées (tous les témoins réservés, `/evenements/` dans la matrice, 3 966 contrôles par passage, huit mutations détectées, aucune fuite). Suite Python non rejouée par les relecteurs : clôture sur les mutations et la relecture du code. C'est un test : rien à regarder |
| B-09 FAQ, pages légales, contact | 27/11, corrigé le 27/11 | **Code clos le 27/11** : cinq corrections vérifiées (le menu du pied de page se reprend après une interruption ; un effacement n'annonce sa fin qu'après disparition vérifiée des métadonnées). Pages légales et FAQ volontairement vides : les textes viennent d'Imagine. Validation visuelle de Ced attendue |
| B-10 Points de vente | 27/11, corrigé le 27/11 | **Code clos le 27/11** : huit corrections vérifiées (recherche insensible aux accents hors de l'ancienne table ; nettoyage repris après un échec de suppression ; motifs de refus en clair). Écran propre « Réglages → Points de vente », carte éteinte, trente commerces fictifs. Validation visuelle de Ced attendue |
| B-07 Complément : antislash de l'agenda | 27/11 | Rouge reproduit, corrigé à la seule frontière d'écriture, reçu déposé. B-07 reste code clos |
| C-27 « Comment nous avez-vous connus ? » | 27/11, corrigé le 27/11 | **Code clos le 27/11** : cinq corrections vérifiées (une lecture en échec n'est plus prise pour une absence, à l'écriture de la source comme à l'effacement ; une proposition vue puis effacée ne se redépose pas). Validation visuelle de Ced attendue, avec la question de la section sous le bouton « Enregistrer » |
| C-28 Packs thématiques | 27/11, corrigé le 27/11 | **Code clos le 27/11** : quatre corrections vérifiées (un pack dont un numéro est dépublié est refusé par le serveur, à l'ajout et à la validation ; un instantané manquant ne se reconstruit jamais après coup). Produit simple à prix unique et blocage du pack entier : défauts, questions chez Imagine. Validation visuelle de Ced attendue |
| B-11 Vidéos, podcasts, sommaire audio | 27/11, preuve reprise deux fois le 27/11 | **Code clos le 27/11** : six instructions vérifiées, code inchangé depuis, réception par contrat rejouée au vert par le relecteur. La saisie dans l'éditeur n'est pas prouvée par l'automate : trois lignes à faire par Ced (`production/B-11/A-VOIR-contrat-V2.md`). Validation visuelle de Ced attendue |
| B-12 Aucun appel sortant depuis le corps | 27/11, corrigé le 27/11 | **Code clos le 27/11** : le verrou ne se contourne plus par la casse de la route d'aperçu (matrice native, cache absent puis ancien, zéro tentative, un simple lien). Réserve permanente : matrice native hors de la suite scellée, à rejouer à chaque montée de version du cœur. Validation visuelle de Ced attendue |
