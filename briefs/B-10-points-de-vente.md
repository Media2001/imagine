# Lot B-10 — Les points de vente

**Voie** : 2. **Chantier** : B. **Délai** : une demi-journée. **Dépend de** : B-00, B-01. **Cahier des charges** : §3.14 (« Carte des points de vente avec recherche par localité, à partir de la base fournie par Imagine ou ses diffuseurs »). Relis-le.

## Pourquoi

Un lecteur qui n'est pas abonné achète le magazine en librairie ou en kiosque, et cherche où. La base des points de vente viendra d'Imagine ou de ses diffuseurs, dans un format inconnu. La page, la recherche et le chargement d'un fichier peuvent exister avant elle.

## Ce qu'on veut

**Le standard d'abord.** Dis en cinq lignes ce qui range le mieux quelques centaines de points de vente dans WordPress (un type de contenu, une table) et pourquoi.

- Une page « Points de vente » : une recherche par localité ou par code postal, une liste de résultats (nom, adresse, localité). Sans recherche, la liste par localité.
- **Le chargement d'un fichier** par l'administration : un CSV et une correspondance des colonnes en configuration, comme A-13, parce que le format de la base n'est pas connu. Un chargement remplace la liste, dit combien de lignes il a prises et refusées (numéro de ligne et motif, sans recopier la ligne), et se rejoue sans doublon.
- **Pas de fond de carte par défaut.** Une carte charge des images chez un tiers, donc un consentement (§4.4, cookies). Un réglage fermé « afficher une carte », éteint ; allumé sur la démonstration, il n'appelle rien et affiche un emplacement vide. Le choix du fournisseur de carte n'est pas fait : dis en trois lignes ce qu'il faudra le jour venu (coordonnées dans le fichier ou géocodage, consentement).
- Aucun géocodage, aucun appel sortant.

Règles :

- un fichier d'essai entièrement fictif (commerces et adresses manifestement inventés), une trentaine de lignes ;
- la recherche est simple : localité ou code postal exacts, sans tenir compte de la casse ni des accents. Si le lecteur attend autre chose (rayon, début de code postal), c'est une question que tu notes, pas une règle que tu inventes ;
- un point de vente est un commerce, pas une personne : pas de raccord à C-21. Si le fichier porte un nom de personne ou un téléphone, la colonne n'est pas affichée sans une ligne explicite dans la correspondance ;
- aucun style inventé : le squelette de B-01. L'emplacement dans la navigation suit le pied de page de B-09 s'il existe, sinon une page seule.

## Preuve

Proportionnée. Le fichier d'essai se charge, se recharge sans doublon, refuse une ligne mal formée en la nommant par son numéro ; la recherche trouve par localité et par code postal, avec et sans accents ; le réglage de carte éteint n'ajoute rien à la page, allumé il n'appelle aucun tiers (zéro requête sortante observée) ; données d'essai laissées en place pour que Ced les voie, déclarées fictives dans `A-VOIR.md`.

## Livrables

Le code, ses tests, la correspondance d'exemple, la section du README de l'extension, `production/B-10/A-VOIR.md`, `PRET`. Rapport court.
