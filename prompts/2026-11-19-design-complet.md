# Ce dont l'intégration a besoin côté design

Note pour Mike, à lui transmettre quand la page d'accueil sera validée. Le design est son domaine : cette note ne dit pas comment dessiner, seulement ce qu'il faut recevoir pour intégrer sans deviner. Il l'adapte librement dans son prompt pour Claude Design.

## 1. Le système de design, avec ses valeurs

- Couleurs, avec leur code.
- Styles de texte (titres, corps, légendes, boutons) : police, graisse, taille, interlignage, en mobile et en bureau.
- Échelle d'espacements utilisée dans les maquettes.
- Grille : colonnes, gouttières, marges, largeur maximale, aux largeurs dessinées.
- Composants récurrents (boutons, champs de formulaire, messages, cartes, navigation, bloc d'abonnement) avec leurs états : repos, survol, focus, erreur, désactivé.

L'idéal : les valeurs sous forme de liste ou de variables, en plus des images. C'est ce qui évite les écarts d'espacement à l'intégration.

## 2. Une page par point du cahier des charges

En mobile et en bureau.

- **Éditorial** : page d'un numéro ; article (vu par un anonyme avec le bloc d'abonnement, et vu par un abonné) ; mode lecture ; archive et thématique ; page de contenu ; agenda et événement.
- **S'abonner** : page des offres ; tunnel d'abonnement sur une page ; confirmation ; achat d'un numéro et d'un billet.
- **Compte** : connexion et création de compte ; tableau de bord de l'abonné ; les pages du compte (paiement, adresses, renouvellement, abonnements offerts et groupés, tarif solidaire, factures, préférences).
- **Emails** : un gabarit.

Pour les écrans qui changent selon la situation (article, tunnel, compte), une variante par cas suffit là où la mise en page diffère vraiment ; pour le reste, les composants et leurs états font foi.

## 3. À avoir en tête

Le cahier des charges fixe des seuils mesurés à la réception (chapitre 5) : Lighthouse mobile à 90 en performance et 95 en accessibilité, WCAG 2.1 AA, aucun défilement horizontal sur mobile. Si un choix de design risque de les mettre en difficulté, on en parle avant de le figer.

Le back-office de l'administration garde l'apparence de WordPress : rien à dessiner.
