# B-03 — Mode lecture, à ouvrir

**Prêt à relire techniquement ; valeurs graphiques provisoires, sans validation visuelle.**

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
5. Après un arrêt du défilement (150 ms), **recharger réellement la page** : mode actif, taille, fond et position proportionnelle sont repris. Ces valeurs sont locales au navigateur/origine, sans compte ni transmission au serveur. Une reprise n’est pas réutilisée entre article complet et extrait de longueur différente. Le navigateur privé ou le refus du stockage peuvent empêcher la mémorisation : la lecture continue néanmoins.
6. **Échap** quitte le mode et rend le focus au bouton. Le bouton permet aussi de sortir ; menu et pied de page reviennent. Après cette sortie, recharger : le mode ne se réactive plus, mais les préférences seront reprises à la prochaine entrée.

### Différence de droit, inchangée

- **a-carte** : texte complet, dont le témoin fictif des lucioles C08. La décision reste celle de C08 ; B03 ne crée aucun droit.
- **Anonyme** : chapeau/extrait public puis bloc de connexion/abonnement. Le bloc de droits **reste visible en mode lecture**, contrairement aux appels périphériques. Aucun texte réservé n’apparaît dans la réponse HTML, les données de page, le REST, le flux ou la recherche sondés.
- Le chapeau et l’extrait peuvent répéter le même texte : c’est le gabarit B01/C08 conservé, pas du contenu éditorial inventé par B03. La signature dépend des données fictives existantes ; elles n’ont pas été corrigées ici.

## Sans JavaScript et mouvement réduit

Désactiver JavaScript puis recharger : **aucun bouton ni réglage**, article et bloc de droits lisibles, menu normal. Réactiver ensuite JavaScript. Avec la préférence système « réduire les animations », aucun déplacement animé : les reprises sont instantanées dans tous les cas. Le même HTML sémantique est fourni aux modes lecture intégrés des navigateurs ; aucune certification multi-navigateurs n’est revendiquée.

## Ce qui est prouvé

- `verification-finale.json` : résultats et empreintes de la release, des sources, des documents et des fichiers relus sur le site.
- `http-release.json` : connexion WordPress réelle A-CARTE, anonyme, durée du seul texte servi, HTML5, assets différés exacts, absence des assets sur l’accueil ; comparaison du corps C08 avec l’avant-B03.
- `php-release.json`, `js-release.txt`, `local-regression.json`, `t01-release.txt` : tests natifs, logique/événements JS hors navigateur, non-régressions et bibliothèques hors ligne.
- `browser-narrow-final.json`, `browser-wide-final.json` : **contrôles réels anonymes** sur les deux largeurs, rechargement/Échap et JavaScript désactivé. Le parcours connecté est prouvé en HTTP, pas présenté comme une inspection visuelle connectée.

Vitesse fixe : **200 mots/minute**, une seule constante dans `wp/themes/imagine/inc/reading.php`. Minimum affiché : une minute ; HTML autorisé uniquement, bloc de droits exclu du compte. Script sans dépendance : **5 756 octets UTF-8**, **1 851 octets gzip déterministe** (poids mesuré, pas promesse de compression HTTP).

Le designer doit fixer les variables listées dans `besoins-designer.md`. Rejeu : `REJOUER.md`. `PRET` signifie prêt à relire, sans GO de production.
