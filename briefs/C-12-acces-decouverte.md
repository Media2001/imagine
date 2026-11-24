# Lot C-12 — L'accès découverte, branché

**Voie** : 2. **Chantier** : C. **Délai** : une demi-journée. **Dépend de** : C-08, C-06 (clos), C-10.
**Cahier des charges** : les paragraphes de §3.9 sur la découverte. Relis-les avant de commencer.

## Pourquoi

La règle de l'accès découverte existe dans la bibliothèque de C-06 (durée, nombre d'articles, périmètre), mais rien ne l'ouvre ni ne la décompte. Les profils V-DEC et V-DEC-FIN restent « partiels » pour cette raison.

## Ce qu'on veut

- **Ouverture** : pour un compte vérifié qui n'a jamais eu de découverte, selon le cahier des charges. Si le déclencheur exact est une question ouverte pour Imagine, c'est un réglage, à défaut prudent.
- **Décompte** côté serveur, attaché au compte : un article déjà ouvert en découverte ne recompte pas ; pas de décompte pour un robot, un aperçu, une requête REST ou un flux.
- **Épuisement** : la décision renvoie « découverte épuisée » et le bloc correspondant.
- **Réglages** : durée, nombre d'articles et périmètre apparaissent dans l'écran de C-10 (section Accès), avec leur mention « à confirmer par Imagine ».
- **Pas de contournement simple** : recréer une session, vider ses cookies ou appeler l'adresse en boucle ne rend pas de crédit. (Recréer un compte avec une autre adresse : hors périmètre, signale-le.)
- La vérification de l'adresse email : s'il n'existe pas de parcours de vérification sur la démonstration, un drapeau posé par le script des profils suffit ; dis-le.

## Livrables

Code, tests (ouverture, décompte, relecture du même article, épuisement, tentative de contournement), mise à jour des profils V-DEC et V-DEC-FIN dans le script de C-09, `production/C-12/A-VOIR.md` (se connecter en `v-dec`, lire, voir le compteur s'épuiser), `PRET`.
