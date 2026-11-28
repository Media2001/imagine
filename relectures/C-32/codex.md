# Relecture indépendante Codex — C-32

Date : 28 novembre 2026. Références : brief C-32, cahier des charges §3.14 et §4.4, doctrine et décision « Cookies » de `docs/decisions.md`. Rapport Claude non consulté. Aucun accès à un site, une base ou un compte ; seul ce rapport est écrit.

## 1. Conformité

L’inventaire fermé contient quatorze noms/motifs et les cinq renseignements demandés. Le rendu est alimenté directement par cette liste, sous le contenu de la page B-09. Aucun bandeau, outil de consentement ou script n’est ajouté par le code livré. Le choix d’un filtre `the_content`, plutôt qu’un bloc ou code court, est annoncé dans le README et satisfait l’objectif de non-recopie.

Les sept cookies d’attribution en lecture sont explicitement signalés, avec le réglage natif `woocommerce_feature_order_attribution_enabled=no`. Leur maintien respecte le brief ; leur présence n’est pas, à elle seule, une correction à imposer à C-32.

**R1 — important — `wp/outils/demo/c32-browser.py:18` — Parcours C-26 incomplet.** La liste d’URL est reconstruite à partir des articles, numéros, pages B-09 et de l’archive agenda. Elle omet les dix pages publiques et les quatre fiches événement de l’extension C-26 : notamment `/notre-cooperative/`, `/soutenir/`, `/proposer-un-sujet/` et `/evenements/demo-events-1/`, présentes dans `production/C-26/mutations-livraison-inventaire.json`, rubrique `extension`. Les cinquante observations déposées confirment leur absence. Un cookie propre à ces pages échappe donc au contrôle demandé sur les mêmes pages publiques que C-26. **Correction proposée :** dériver les parcours publics concernés de l’inventaire C-26 existant, sans modifier sa matrice, et vérifier leur couverture par identité d’URL plutôt que par le seul total de 44 pages.

## 2. Exactitude métier

Cas déroulés à partir du code et des relevés déposés, sans nouvelle observation distante :

- **Lecture anonyme de l’accueil :** aucun nom dans les en-têtes, sept `sbjs_…` après JavaScript. Les sept entrées existent dans la liste ; six expirations valent `-1`, celle de `sbjs_session` est persistante. L’écart avec zéro cookie est documenté.
- **Arrivée avec `fictif-affiche`, puis cas indépendant d’ajout au panier :** le premier relevé ajoute `wp_woocommerce_session_[hash]` ; le second ajoute aussi `woocommerce_items_in_cart` et `woocommerce_cart_hash`. Les noms correspondent aux motifs fermés et aux gestes déclarés.
- **Connexion sans mémorisation :** les cookies WordPress d’authentification sont présents, avec expiration navigateur `-1`. Le relevé ne contient aucune session WooCommerce.

**R2 — mineur — `wp/plugins/imagine-site/Cookies.php:17` — Geste déclaré sans observation correspondante.** La session WooCommerce est annoncée pour « Code suivi connu (C-30), panier ou connexion », alors que la ligne `connexion` du relevé final ne comporte ce cookie ni dans les en-têtes ni dans le navigateur. Le brief impose uniquement ce qui est observé. **Correction proposée :** retirer « ou connexion » de cette entrée, ou déposer un parcours précis et reproductible démontrant cette émission avant de la déclarer.

Les frontières calendaires et échéances ne sont pas pertinentes ici ; les limites utiles sont l’anonymat, le geste déclencheur, les cookies inattendus et la restauration des sessions.

## 3. Tests

Exécutions effectuées :

- `python -B production/C-32/verifier.py` : **réussi**, code retour 0 ; `PASS_INVENTAIRE` et `FAIL_CONSTATE_NON_CORRIGE` pour la lecture. Ce programme contrôle les empreintes et les reçus archivés ; il ne réexécute pas le navigateur ni PHPUnit.
- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1` : **empêché avant les tests**, code retour 1, `Wsl/Service/E_ACCESSDENIED`, Docker indisponible ; zéro test exécuté. Aucun téléchargement ni installation tenté. PHP et PHPUnit ne sont pas disponibles directement dans le PATH et le paquet n’a pas de `vendor/bin/phpunit` local.

Les preuves contrôlées annoncent 21 contrôles natifs, 151 contrôles navigateur et un rejeu de 1 220 tests / 36 756 assertions. Ce sont des résultats de production vérifiés sur pièces, pas des résultats reproduits pendant cette relecture. Les recettes natives, navigateur et `--live` accèdent à la démonstration et à sa base : non exécutées conformément à `relecteurs/AGENTS.md`.

Les deux mutations HTTP/JavaScript font bien lever le refus des noms hors liste, intercepté par le test témoin. Le test PHP vérifie aussi les préfixes/suffixes indus et le saut de ligne terminal.

**R3 — important — `wp/outils/demo/c32-browser.py:100` — L’attendu zéro cookie n’est pas un test exécutable en échec.** `zero_cookie_pass` est enregistré mais n’entre pas dans `checks` ni dans l’assertion finale. La recette réussit donc avec les sept cookies actuels, et réussirait aussi avec un cookie de panier déjà autorisé apparaissant indûment en lecture. Le fichier strict est ensuite fabriqué avec un statut `FAIL` constant ; le vérificateur exige même que cet échec subsiste. Cela conserve un constat historique, sans fournir le test réutilisable de l’attendu demandé. **Correction proposée :** exposer un contrôle strict calculé sur les observations qui échoue réellement dès qu’une lecture reçoit un cookie et réussit lorsque la lecture n’en reçoit plus. Garder séparément le bilan d’inventaire et l’écart natif autorisé ; si cet écart est toléré dans le bilan général, borner cette tolérance aux sept noms `sbjs_…` observés. Ne désactiver aucun cookie dans ce lot.

## 4. Sécurité et données

La liste et les relevés de cookies examinés ne publient pas leurs valeurs. Le compte de recette utilise une adresse fictive `@example.org`. Les sorties HTML sont échappées, et le rendu ne lit aucun contenu réservé. Aucun défaut de paywall ajouté par `Cookies.php` n’a été identifié ; cela ne constitue pas une nouvelle recette d’étanchéité complète.

**R4 — important — `wp/outils/demo/c32-browser.py:90` — Nettoyage susceptible de supprimer une session étrangère.** La condition autorise la suppression de toute nouvelle session à clé non numérique, même absente de `knownkeys`. Une session invitée créée par une autre visite pendant la recette est ainsi supprimée. La comparaison finale peut ensuite déclarer la restauration réussie, puisque cette session ne figurait pas dans l’état initial. **Correction proposée :** limiter les suppressions aux clés attribuées avec certitude au navigateur de recette et à son compte temporaire ; conserver toute session non attribuée et signaler la concurrence. Couvrir ce cas par un test avec une session étrangère apparue après le snapshot.

Les reçus indiquent une restauration exacte et le retrait des sondes pour l’exécution déposée ; ils ne couvrent pas ce cas concurrent.

## 5. Doctrine

Le code s’appuie sur les mécanismes natifs et se limite à l’inventaire et à son affichage. `strict_types`, espace de noms `Imagine\Site`, échappement et domaine de traduction sont présents. La qualification juridique du consentement reste chez Imagine et son conseil, conformément à la décision existante. Aucune nouvelle question métier ni autorisation de déploiement n’est proposée.

## 6. Études (lots sans code)

Lot avec code ; contrôle du volet documentaire « standard d’abord » néanmoins effectué.

**R5 — mineur — `wp/plugins/imagine-site/README.md:730` — Sources sans phrase justificative conservée.** Les cinq lignes renvoient à des URL officielles, mais aucune citation précise ne permet de rattacher les affirmations à leur source. `standard-V2.json` conserve des empreintes et des présences de mots ; cela ne prouve pas les phrases annoncées. **Correction proposée :** ajouter pour chaque affirmation native un bref extrait officiel pertinent et son URL, ou marquer « doute » les points non établis. Les sources en ligne n’ont pas été consultées pendant cette relecture, l’accès à un site étant interdit au relecteur.

## Verdict

**À corriger.** Ce verdict n’est pas un GO.

- **Bloquant :** aucun défaut classé à ce niveau.
- **Important :** R1, couverture des pages C-26 ; R3, véritable test de zéro cookie ; R4, isolation du nettoyage des sessions.
- **Mineur :** R2, geste de connexion non observé pour la session WooCommerce ; R5, traçabilité documentaire.

Le rejeu PHPUnit reste à reproduire dans un environnement local où WSL/Docker est accessible. Cette limite d’environnement est distincte des défauts du lot.
