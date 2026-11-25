# Relecture Codex — B-03 : mode lecture

Date : 25 novembre 2026. Relecture indépendante du brief, du cahier des charges §3.3 (mode lecture et note technique), de la doctrine, du thème et des livrables B-03. Rapport Claude non consulté. Aucun accès à un site, une base ou un compte ; aucune modification hors du présent rapport.

## 1. Conformité

Le mécanisme demandé est présent : classe sur `html`, CSS dédiée, script autonome, bouton natif masqué sans JavaScript, trois tailles et trois fonds, stockage local, estimation serveur et progression. Les paramètres graphiques passent par les variables B-01. Les livrables de recette, besoins du designer et `PRET` sont présents. Les choix de reprise proportionnelle et d'isolation par article et longueur sont explicités.

**B03-C1 — important — `wp/themes/imagine/assets/reading.css:19`.** Le fond sombre modifie les variables héritées, mais ne neutralise pas les couleurs explicites du contenu autorisé. Un paragraphe `<p style="color:#000000">Texte</p>`, conservé dans le corps complet, reste noir sur `#171717` : contraste **1,17:1**, inférieur à 4,5:1. Les classes de couleur éditoriales posent le même problème. Les bons contrastes des variables seules ne garantissent donc pas l'exigence AA du brief. **Correction proposée :** en mode lecture uniquement, ramener les couleurs de texte et fonds des blocs éditoriaux à une palette compatible, y compris les styles explicites autorisés, sans altérer le contenu enregistré ni les images ; vérifier un paragraphe coloré et un bloc avec fond dans les trois modes. Constat par analyse statique de la cascade et du corps conservé, pas par observation du staging.

Poids vérifié sur les octets locaux : **5 756 octets**, **1 851 octets gzip**. Vitesse fixe : **200 mots/minute**, constante `IMAGINE_READING_WORDS_PER_MINUTE` dans `wp/themes/imagine/inc/reading.php:8`.

## 2. Exactitude métier

Deux cas du §3.3 déroulés dans le code :

- **Abonné autorisé :** l'unique appel à `imagine_article_body()` produit le corps complet ; le même résultat sert à l'affichage et au calcul de durée. La présentation change sans requête supplémentaire pour obtenir le texte.
- **Anonyme sans droit :** cette sortie produit l'extrait puis le bloc de droits. Le CSS masque les éléments périphériques, conserve le bloc de droits, et le script mesure seulement `.imagine-paywall-body`. L'estimation ne reçoit pas le corps réservé et exclut le bloc d'abonnement.

**B03-C2 — mineur — `wp/themes/imagine/assets/reading.js:114`.** `pagehide` appelle directement `save()`, qui enregistre la dernière fraction calculée, sans mesurer la position actuelle. Si un défilement attend encore son `requestAnimationFrame`, un départ ou rechargement conserve l'ancienne position ; `visibilitychange` utilise aussi cette sauvegarde. **Reproduction locale :** avec le simulateur DOM du lot, activation puis défilement à `scrollY=1200` (texte à 400, hauteur 2400, fenêtre 800), suivi de `pagehide` avant le rafraîchissement : position sauvegardée **0 au lieu de 0,5**, reprise à **0 au lieu de 1200**. **Correction proposée :** au départ ou masquage, actualiser synchroniquement la fraction si le mode est actif avant de sauvegarder, en préservant la position mémorisée lorsque le mode est inactif ; ajouter ce scénario d'événements au test.

## 3. Tests

Exécutés pendant cette relecture, sans écrire de preuves ni de caches :

- `node wp/tests/demo/b03-reading.test.cjs` : **5/5 réussis**. Le premier lancement avec `node --test` était empêché par `spawn EPERM` ; l'exécution directe du même fichier a permis de jouer les cinq tests.
- `python -B wp/tests/demo/test_b03_contract.py` : **3/3 réussis**.
- Régression `b03-regression.py`, avec son seul réceptacle de rapport remplacé en mémoire : **14/14 réussis**, dont les trois contrats ci-dessus. L'ancien B-01 échoue uniquement sur « aucun JS », puis passe avec l'adaptation B-03 déjà documentée ; aucune assertion supplémentaire modifiée.
- Scénario complémentaire C2 exécuté en mémoire avec le simulateur existant : défaut reproduit. Les tests livrés vident les rafraîchissements avant le départ et ne couvrent pas cette séquence. Pour C1, ils vérifient les couples de variables, sans contenu imposant ses propres couleurs.

Les **13 empreintes de sources**, **4 de documents** et **9 de preuves** du reçu final correspondent aux fichiers présents. Ce reçu annonce 10 assertions PHP B-03, 43 contrôles HTTP, 1 012 tests T01 / 34 006 assertions et 29 contrôles navigateur anonymes, sans échec ; ces nombres restent des **preuves fournies**, non des exécutions indépendantes de cette relecture.

PHP B-03, HTTP et T01 non rejoués : `php` est absent du PATH ; le parcours PHP B-03 et HTTP fourni accède au site et au compte de recette, interdits par `relecteurs/AGENTS.md`. Le lanceur final téléverse également un test et réécrit des livrables. Aucun lancement de ce parcours ni installation effectués. La recette manuelle couvre bien anonyme et `a-carte`, écrans étroit et large, rechargement et absence de JavaScript ; aucune validation visuelle indépendante revendiquée.

## 4. Sécurité et données

Aucune nouvelle voie de sortie du texte réservé identifiée dans B-03. La décision serveur reste au point de sortie B-01/C-08 ; aucun chargement réseau dans le script. Le stockage contient les préférences, l'identifiant d'article, la longueur du texte accessible et une fraction, sans texte ni identifiant de compte. Les libellés et attributs du nouveau gabarit sont échappés ; le HTML du corps réutilise la sortie existante autorisée. Aucun secret ni donnée personnelle réelle relevé dans les fichiers examinés.

## 5. Doctrine

Le sur-mesure correspond au mécanisme explicitement demandé ; pas de bibliothèque ni d'extension ajoutée. PHP strict, espace de noms, préfixes et traduction des nouveaux libellés respectés. Les références officielles sont consignées dans la production ; aucune consultation externe effectuée. Pas de question métier ou touchant au réel à soumettre : C1 et C2 sont des corrections techniques proposées.

## 6. Études (lots sans code)

Sans objet : lot de code.

## Verdict

**À corriger.**

- **Bloquant :** aucun identifié.
- **Important :** B03-C1 — contraste insuffisant en présence de couleurs éditoriales explicites.
- **Mineur :** B03-C2 — position périmée sauvegardée si le départ précède le rafraîchissement.

Ce verdict n'est pas un GO.
