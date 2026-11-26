# Lot C-23 — Le test d'étanchéité de livraison

**Voie** : 2. **Chantier** : C. **Délai** : une demi-journée. **Dépend de** : C-08, C-11, C-12, C-14, B-04. **Cahier des charges** : §3.9 (« Étanchéité »), §4.4 (« Un test automatisé vérifie, à chaque livraison, qu'un visiteur anonyme ne peut obtenir le texte réservé par aucune de ces voies »). Relis-les.

## Pourquoi

C-08 a prouvé l'étanchéité de l'article le jour où il a été rendu. Depuis, quinze lots ont ajouté des pages et des sorties : le PDF, l'accès découverte, l'achat au numéro, la page numéro et le kiosque, les partenaires, les newsletters, l'export des données. Chaque lot a testé sa part ; personne ne rejoue l'ensemble. Le cahier des charges demande **un** test, joué **à chaque livraison**. Ce lot l'écrit : une commande, une matrice, un oui ou un non.

## Ce qu'on veut

Une commande unique, rejouable sur `imagine-test-demo`, **en lecture seule** : elle ne fait que des requêtes, comme un visiteur.

- **Le témoin** : un article réservé de la démonstration porte une phrase témoin au milieu de son texte (celle de C-08 si elle existe encore ; sinon une seule, posée par le jeu de démonstration). Même principe pour le PDF d'un numéro.
- **Les voies**, au minimum : la page de l'article ; les listes où il apparaît (accueil, page numéro, kiosque, thématique, archives) ; l'interface REST du contenu, de la recherche et des révisions ; les flux ; l'oEmbed et la vue intégrée ; la recherche interne ; les balises de partage et l'extrait automatique ; le plan de site ; le PDF par son adresse de téléchargement, par son adresse directe dans les médias et par la page de pièce jointe. Fais l'inventaire des sorties ajoutées depuis C-08 et dis lesquelles tu as retenues et pourquoi.
- **Les publics**, sans droit sur ce texte : anonyme ; compte connecté sans abonnement ; accès découverte épuisé ; acheteur d'un **autre** numéro ; faux robot (agent utilisateur d'un moteur, adresse non vérifiée). Pour chacun et pour chaque voie : le témoin est **absent**.
- **Le contrôle inverse**, sans lequel le test ne prouve rien : un abonné actif reçoit le témoin dans la page et dans le PDF. Et une mutation témoin : sur une copie jetable ou par un réglage remis ensuite, une voie rendue fuyante **fait échouer** la commande.
- **La sortie** : une matrice voies × publics, une ligne finale `ETANCHEITE : <n> contrôles, <n> fuites — PASS|FAIL`, code 0 ou 1.

Règles :

- ce lot **ne modifie pas le paywall**. Si la matrice révèle une fuite, tu la rapportes en tête du rapport, avec la voie et le public ; la correction se fait dans le lot qui porte cette sortie, avec sa régression, et tu le dis ;
- le cache de pages et les robots **vérifiés** (résolution inverse) ne se prouvent pas sur la démonstration : note-le comme limite, ils viendront avec l'hébergement ;
- profils remis dans leur état de départ ; aucun email, aucun appel extérieur.

## Preuve

La matrice verte, la mutation témoin rouge puis remise en état, le contrôle inverse. Proportionnée : pas de captures, la matrice suffit.

## Livrables

La commande, ses tests, `production/C-23/A-VOIR.md` (la commande à lancer et la matrice du dernier rejeu), `PRET`. Rapport court.
