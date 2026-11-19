# Prompt — déclinaison complète du design à partir de la page d'accueil validée

À donner à Claude Design, par le designer, **une fois la maquette de la page d'accueil validée par Imagine**. Joindre la maquette validée.

But : obtenir en une passe tous les écrans, tous leurs états et un système de design chiffré, pour que l'intégration n'ait rien à deviner (espacements, tailles, états).

---

La maquette jointe est la page d'accueil validée du nouveau site d'Imagine, magazine belge vendu par abonnement (papier et numérique). Elle fixe la direction : ne la remets pas en question. À partir d'elle, produis le reste du design du site, en deux livrables.

## Livrable 1 — Le système de design

Extrais-le de la page d'accueil, complète ce qui manque, et **donne toutes les valeurs en chiffres**. Rien ne doit dépendre d'une mesure faite à l'œil sur une image.

- **Couleurs** : palette nommée par rôle (fond, texte, texte secondaire, accent, bordure, succès, alerte, erreur), avec les valeurs hexadécimales. Chaque couple texte/fond utilisé respecte un contraste de 4,5:1 (3:1 pour les grands titres) : indique le ratio.
- **Typographie** : deux familles au maximum, de préférence des polices variables. Pour chaque style (titres 1 à 4, chapô, corps, légende, bouton, étiquette) : famille, graisse, taille, interlignage, en mobile et en bureau.
- **Espacements** : une seule échelle (par exemple 4, 8, 12, 16, 24, 32, 48, 64, 96). Tout espacement des maquettes est une valeur de cette échelle. Aucune valeur intermédiaire.
- **Grille** : largeurs de référence 390, 768 et 1440 px ; nombre de colonnes, gouttières, marges extérieures et largeur maximale du contenu à chacune ; largeur de la colonne de lecture d'un article.
- **Formes** : rayons, épaisseurs de bordure, ombres (s'il y en a), en valeurs.
- **Composants**, chacun avec ses dimensions, ses espacements internes et **tous ses états** :
  - bouton principal, secondaire, lien : repos, survol, focus clavier visible, enfoncé, désactivé, en chargement ;
  - champ de formulaire, liste déroulante, case à cocher, bouton radio, dépôt de fichier : vide, rempli, focus, erreur avec message, désactivé ;
  - messages : information, succès, alerte, erreur ;
  - carte d'article, carte de numéro, carte d'événement ;
  - bloc d'abonnement (celui qui suit l'extrait d'un article réservé) ;
  - choix du tarif et du mode de paiement ;
  - en-tête et navigation (bureau, mobile ouvert, mobile fermé ; visiteur anonyme, abonné connecté), pied de page ;
  - bandeau d'état de l'abonné (paiement échoué, échéance proche, justificatif en attente) ;
  - fil d'Ariane, pagination, étiquette de thématique, tableau, fenêtre de confirmation.
- **Jetons** : termine ce livrable par la liste complète des valeurs sous forme de variables CSS (`--couleur-accent`, `--espace-4`, `--texte-corps-taille`…), prête à être copiée.

## Livrable 2 — Les écrans

Chaque écran en **trois largeurs** (390, 768, 1440 px), construit uniquement avec les composants et les valeurs du livrable 1.

### Éditorial
1. Page d'un numéro (couverture, sommaire, achat du numéro).
2. Article — vue normale, dans cinq états : anonyme (extrait puis bloc d'abonnement) ; abonné (texte complet) ; accès découverte en cours ; accès découverte épuisé ; acheteur du numéro.
3. Article — mode lecture (vue épurée, réglages de taille et de thème).
4. Archive des articles et page d'une thématique.
5. Résultats de recherche (avec et sans résultat).
6. Page de contenu statique (texte long, FAQ).
7. Agenda et page d'un événement (billets disponibles, complet, tarif abonné).
8. Page 404.

### S'abonner
9. Page des offres (trois tarifs, paiement en une ou en quatre fois).
10. Tunnel d'abonnement, **sur une seule page** : choix du tarif et du mode de paiement, coordonnées, paiement (carte, Bancontact, domiciliation avec IBAN et acceptation du mandat, PayPal), **encadré de reconduction tacite en gras avant le paiement**. Variantes : visiteur sans compte ; lecteur déjà connecté (champs préremplis) ; professionnel (numéro d'entreprise) ; abonnement offert (coordonnées du destinataire, choix du renouvellement) ; tarif solidaire (catégorie et dépôt du justificatif) ; erreur de paiement.
11. Confirmation de commande, avec la question « Comment nous avez-vous connus ? » et l'invitation au formulaire de personnalisation.
12. Page « Abonnement sur facture » (virement).
13. Achat d'un numéro à l'unité, panier, achat d'un billet.

### Compte
14. Connexion, création de compte, vérification de l'adresse, mot de passe oublié.
15. Tableau de bord du compte : statut de l'abonnement, numéros restant à recevoir, échéance, tarif, mode de paiement. États : actif ; paiement échoué (délai de grâce) ; suspendu ; arrivé à terme ; renouvellement désactivé ; sans abonnement.
16. Moyen de paiement (modification, passage à la domiciliation en ligne).
17. Adresses (avec l'effet d'un changement de pays sur le port).
18. Renouvellement : désactivation en un clic et sa confirmation.
19. Rétractation, en deux étapes.
20. Abonnements offerts.
21. Gestion d'un abonnement groupé : liste des bénéficiaires, attribution, remplacement.
22. Tarif solidaire : statut, date de fin, nouveau justificatif.
23. Factures.
24. Préférences de newsletter et formulaire de personnalisation.
25. Espace coopérateurs (page d'entrée).

### Emails
26. Un gabarit d'email, décliné pour : confirmation d'abonnement, avis de prélèvement, rappel de reconduction, échec de paiement, non-renouvellement. Largeur 600 px et version mobile.

## Contraintes à respecter partout

- **Mobile d'abord** : conçois chaque écran en 390 px, puis élargis. Aucun défilement horizontal.
- **Accessibilité WCAG 2.1 AA** : contrastes, focus clavier toujours visible, zones tactiles d'au moins 44 px, libellés au-dessus des champs (pas de texte d'exemple servant de libellé), erreurs décrites en texte et pas seulement par la couleur.
- **Performance** : le site doit atteindre 90 en performance sur Lighthouse mobile. Pas de carrousel automatique, pas de vidéo d'arrière-plan, pas d'animation au défilement, pas d'effet qui exige une bibliothèque. Une seule grande image au-dessus de la ligne de flottaison. Aucun filtre de couleur sur les images ; recadrage par point focal.
- **Contenus** : textes réalistes en français (titres de longueurs variées, dont un très long ; noms composés ; adresse sur trois lignes), pas de faux texte latin. Montre ce qui se passe quand un contenu est absent (pas d'image, pas de chapô, liste vide).
- **Cohérence** : n'invente aucune valeur hors du système. Si un écran a besoin d'un composant qui n'existe pas, ajoute-le au livrable 1 avec ses états, puis utilise-le.

## Ce que tu ne fais pas

- Le back-office de l'administration : il garde l'apparence de WordPress.
- Les textes définitifs, les prix et le nom des tarifs : mets des valeurs d'exemple clairement signalées.

## Pour finir

Donne la liste des écrans et des états produits, et signale ceux pour lesquels tu as dû faire une hypothèse faute d'information, avec la question à poser à Imagine.
