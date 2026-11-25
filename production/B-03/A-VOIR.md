# B-03 — Mode lecture, à ouvrir

**Corrections du 25/11/2026, y compris suppression CSS de 19h30, appliquées ; recette B03 réconciliée après clôture C15. Prêt à relire techniquement si le reçu courant lié par `reconciliation-c15-current.json` est `VERIFIED`, sans validation visuelle.**

Site fictif uniquement : `http://192.168.129.32:8085`.
Article de recette : `http://192.168.129.32:8085/c08-article-reserve-article/`.
Aucun compte, article ou paiement n’a été créé, renommé ou réensemencé par B-03.

## En `a-carte`, puis en anonyme

Se connecter par `/wp-login.php` avec le compte fictif **A-CARTE / a-carte** déjà présent. Les identifiants restent hors dépôt, dans `C:\Users\Ced\.imagine-demo\identifiants.json`, clé `c09_accounts` : aucun secret n’est à recopier dans un rapport. Pour la seconde recette, utiliser une fenêtre privée sans connexion.

Rejouer les points suivants à **390 × 844** puis **1440 × 900** (ou un écran étroit et un large) :

1. À l’ouverture ordinaire : titre, chapeau, signature existante, numéro/thématiques éventuels, durée estimée et texte ; menu habituel visible. Cliquer sur **« Lire l’article »**, aussi activable par Tab puis Entrée/Espace.
2. La racine reçoit `imagine-reading`. Menu, pied de page et leurs appels à l’abonnement disparaissent ; une seule colonne, au maximum **70ch**, agrandie et limitée par l’écran. Titre et métadonnées éditoriales restent dans `article` ; commandes hors du flux éditorial. Le bouton annonce son état pressé et devient **« Quitter le mode lecture »**.
3. Choisir **Confort / Grand / Très grand**, puis **Clair / Sépia / Sombre**. Le texte et les contrôles restent lisibles, les liens et le focus clavier identifiables. Aucun défilement horizontal à 390 px dans la recette. Les valeurs ne prétendent pas remplacer les maquettes.
4. Descendre dans le texte : barre native fixée en haut de l’écran, pourcentage dans les réglages. La progression porte sur le **texte accessible**, pas sur le menu ni le bloc de droits. Cet article fictif est court : **100 % lorsque tout son texte est dans la fenêtre** est normal. La logique d’un long texte et ses positions intermédiaires est exercée par les tests JS sans ajouter une fixture.
5. **Recharger réellement la page**, y compris juste après un défilement : mode actif, taille, fond et position proportionnelle sont repris. Au départ ou au masquage, la position est recalculée synchroniquement même si la rAF du scroll n’a pas encore tourné ; le test JS exerce cette fenêtre exacte. Hors mode lecture, le défilement ordinaire ne remplace pas la fraction mémorisée. Ces valeurs sont locales au navigateur/origine, sans compte ni transmission au serveur. Une reprise n’est pas réutilisée entre article complet et extrait de longueur différente. Le refus du stockage peut empêcher la mémorisation : la lecture continue néanmoins.
6. **Échap** quitte le mode et rend le focus au bouton. Le bouton permet aussi de sortir ; menu et pied de page reviennent. Après cette sortie, recharger : le mode ne se réactive plus, mais les préférences seront reprises à la prochaine entrée.

### Différence de droit, inchangée

- **a-carte** : texte complet, dont le témoin fictif des lucioles C08. La décision reste celle de C08 ; B03 ne crée aucun droit.
- **Anonyme** : chapeau/extrait public puis bloc de connexion/abonnement. Le bloc de droits **reste visible en mode lecture**, contrairement aux appels périphériques. Aucun texte réservé n’apparaît dans la réponse HTML, les données de page, le REST, le flux ou la recherche sondés.
- Le chapeau et l’extrait peuvent répéter le même texte : c’est le gabarit B01/C08 conservé, pas du contenu éditorial inventé par B03. La signature dépend des données fictives existantes ; elles n’ont pas été corrigées ici.

## Sans JavaScript et mouvement réduit

Désactiver JavaScript puis recharger : **aucun bouton ni réglage**, article et bloc de droits lisibles, menu normal. Réactiver ensuite JavaScript. Avec la préférence système « réduire les animations », aucun déplacement animé : les reprises sont instantanées dans tous les cas. Le même HTML sémantique est fourni aux modes lecture intégrés des navigateurs ; aucune certification multi-navigateurs n’est revendiquée.

## Ce qui est prouvé

### Couleurs éditoriales corrigées

Dans les **trois** palettes, la lecture neutralise les couleurs inline et les classes couleur des blocs, sans modifier le HTML enregistré ni les images. À la sortie, les couleurs d’auteur reviennent. Le contrôle rejouable `b03-colors.py` ajoute uniquement dans le DOM client un paragraphe explicitement noir, un bloc à fond rouge et une sonde inline, puis les supprime : ne rien enregistrer dans l’éditeur WordPress. Contrastes réellement calculés dans Chromium, sur ces sondes à 390 et 1440 px : **clair 21:1, sépia 14,255:1, sombre 16,157:1** (tous ≥ 4,5:1). L’image sonde, ses couleurs propres et le DOM restent intacts. Le bloc de droits reste visible.

- `reconciliation-c15-current.json` : pointeur et SHA-256 du **nouveau** reçu final sous `reconciliation-c15/<horodatage>/`. L'ancien `verification-finale.json` racine reste `FAILED`, historique intact, pas le verdict courant.
- Dans ce nouveau dossier : `http-corrections.json`, 43 contrôles, vraie connexion A-CARTE, anonyme, vitesse lue dans la constante serveur, HTML5, octets des assets et absence sur l’accueil ; corps C08 comparés à l'historique.
- Même dossier : `php-corrections.json`, `js-corrections-green.txt`, `local-regression.json`, `t01-release.txt` : 10 assertions PHP B03, 8 tests JS, 15 tests locaux, 1 012 tests T01 / 34 006 assertions. `c09-native-readback.json` : 149 contrôles natifs frais, sans seed ni paiement.
- `browser-colors-corrections.json` : **77 contrôles réels anonymes**, couleurs et images, trois tailles, rechargement/Échap, zéro requête lors des réglages, JavaScript désactivé et mouvement réduit. Les anciens reçus navigateur sont historiques. Le parcours connecté est prouvé en HTTP, pas présenté comme une inspection visuelle connectée.
- `preservation-reconciliation.json` et `current-before.json` / `current-after.json` du nouveau dossier : **égalité exacte pendant le rejeu B03 courant**, sur les quatre tables non-utilisateur de la photographie existante et les fichiers plugins/thème. Aucune exception C15 dans cette garde courante. Les seuls deltas historiques de sources sont les deux assets B03 et les quatre chemins C15, dont les octets finaux doivent correspondre aux reçus C15 locaux et distants.
- Un document **local seulement** s'ajoute aux quatre sources C15 : `plugins/imagine-site/README.md`, qualifié exactement par le SHA-256 de `C-15/livraison.json`, absent des snapshots distants, jamais déployé ici.
- **Limite historique conservée** : `wp_posts`, `wp_postmeta`, `wp_wc_orders`, `wp_wc_orders_meta` diffèrent de `corrections-before.json`. Les paires d'empreintes restent explicites ; l'action/reset C15 est documentée et sémantiquement restaurée selon ses reçus, mais une empreinte ne permet pas d'attribuer exhaustivement chaque ligne changée. B03 ne prétend ni identité des tables historiques ni attribution exclusive de tous leurs deltas. Les notes d'audit légitimes ne sont pas supprimées. La référence et les anciens reçus restent intacts.

Vitesse fixe : **200 mots/minute**, une seule constante dans `wp/themes/imagine/inc/reading.php`. Minimum affiché : une minute ; HTML autorisé uniquement, bloc de droits exclu du compte. Script sans dépendance : **6 045 octets UTF-8**, **1 956 octets gzip déterministe** (poids mesuré, pas promesse de compression HTTP).

Le designer doit fixer les variables listées dans `besoins-designer.md`. **Après son choix**, Ced doit revalider le contraste et le rendu sur un article réel ; aucune approbation visuelle n’est déduite des sondes. Le défaut technique est la neutralisation dans les trois modes. Rejeu avec les deux interpréteurs exacts : `REJOUER.md`. `PRET` signifie prêt à relire, sans GO de production.
