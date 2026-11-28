# Lot C-32 — Les cookies qu'un visiteur reçoit

**Voie** : 2. **Chantier** : C. **Délai** : trois heures. **Dépend de** : B-09 (page « Gestion des cookies », vide), C-30 (code suivi), C-26 (parcours des pages publiques). **Cahier des charges** : §3.14 (« Pages légales, conditions générales de vente, politique de confidentialité, gestion des cookies ») et §4.4 (« gestion des cookies conforme »). Relis-les.

## Pourquoi

Personne ne sait aujourd'hui dire quels cookies le site pose à un visiteur, ni à quel moment. Or deux lots en posent sans l'avoir cherché : le code suivi de C-30 ouvre une session WooCommerce, et WooCommerce a sa propre attribution d'origine des commandes. Avant de parler de bandeau, il faut la liste, et un test qui la garde vraie.

## Ce qu'on veut

**Le standard d'abord.** Cinq lignes, sources officielles citées : quels cookies WordPress et WooCommerce posent d'eux-mêmes à un visiteur anonyme, à quel geste (simple lecture, panier, connexion, commentaire), et quels réglages natifs les éteignent (l'attribution d'origine des commandes en a un).

- **Une liste fermée, écrite dans le code** : pour chaque cookie que la démonstration peut poser, son nom ou son motif, qui le pose, à quel geste, sa durée, et s'il sert au fonctionnement (session, panier, connexion) ou à la mesure. Rien d'inventé : seulement ce que tu observes.
- **Un test** qui parcourt les pages publiques en anonyme (les mêmes que C-26, sans étendre sa matrice) et relève les cookies reçus, par l'en-tête de réponse et par le navigateur après exécution des scripts :
  - en simple lecture (accueil, numéro, article, thématique, agenda, pages légales), dis ce que tu trouves ; l'attendu est **aucun cookie** ;
  - à chaque geste qui en pose un (arrivée avec un code suivi connu, ajout au panier, connexion), le cookie reçu est dans la liste ;
  - **un cookie hors liste fait échouer le test.**
- **La page « Gestion des cookies » de B-09** affiche cette liste sous son texte, par un bloc ou un code court, sans que personne la recopie. Le texte de la page reste vide : il viendra d'Imagine et de son conseil.
- Si la simple lecture pose un cookie, **ne le supprime pas de toi-même** quand il vient d'un lot rendu : écris-le dans le rapport, avec le réglage natif qui l'éteindrait.

Règles :

- **aucun bandeau, aucun outil de consentement, aucun script ajouté** : le choix de l'outil n'est pas fait, et savoir si un de ces cookies demande un consentement est une question rangée pour Imagine et son conseil ;
- tu ne modifies ni C-30 ni un lot code clos ;
- la liste ne contient aucune valeur de cookie, seulement des noms et des motifs.

## Preuve

Proportionnée. Le relevé des cookies par page et par geste, en anonyme ; une mutation témoin : un cookie de plus, posé par une sonde, fait échouer le test, puis la sonde est retirée ; la page affiche la liste et rien d'autre. Sessions et paniers d'essai rendus dans leur état de départ.

## Livrables

Le code, ses tests, la section du README, `production/C-32/A-VOIR.md`, `PRET`. Rapport court.
