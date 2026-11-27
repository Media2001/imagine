# Relecture indépendante — B-15

Date : 27 novembre 2026. Références : brief B-15, cahier des charges §3.2, décision « Pied de page » de `docs/decisions.md`, doctrine et grille de relecture. Périmètre : `production/B-15/` et code concerné dans `wp/`. Aucun accès au site ou à une base ; `relectures/B-15/claude.md` non lu.

## 1. Conformité

Les cinq zones sont rendues une fois et dans l'ordre demandé. Abonnement utilise `Navigation::abonnementUrl()`, comme l'accueil ; newsletter et points de vente restent de simples liens. Le menu `imagine-footer` est réutilisé, sans écriture ni duplication des entrées B-09. La conservation du lien Points de vente ajouté par B-10 est explicitée.

Tous les gabarits publics examinés appellent le pied commun. La neutralisation des classes de contexte et de `aria-current` est limitée à ce menu. Le mode lecture masque déjà le pied via `wp/themes/imagine/assets/reading.css:31`. Aucun style ou JavaScript ajouté par B-15.

README, trois lignes sur le standard, capture, A-VOIR et PRET présents. Capture examinée : structure et cinq zones visibles. La validation visuelle reste distincte de cette relecture.

## 2. Exactitude métier

Cas déroulés à la lecture du code, conformément au §3.2 :

- **Publication puis retrait.** Deux numéros publiés, datés du 15 octobre 2026 et du 15 janvier 2027 : `Accueil::numero()` sélectionne le second par `imagine_sortie DESC`, puis `ID DESC`. La sauvegarde invalide le fragment. Après passage du second en brouillon, le prochain rendu reprend le premier. Le changement d'année est correctement ordonné par les dates ISO.
- **Dates égales.** Deux numéros publiés de même date : celui d'identifiant supérieur est sélectionné à l'accueil et au pied, qui appelle exactement le même sélecteur. Aucun second critère métier divergent n'est introduit.
- **Aucun numéro publié.** Le fragment vide est conservé comme chaîne en cache ; la section demeure sans lien vers un brouillon. Une publication invalide ce résultat vide.

La décision consignée pour « le plus proche » est respectée : lien vers la recherche, sans géolocalisation. Aucun défaut fonctionnel établi dans ces parcours.

## 3. Tests

Exécutés localement pendant cette relecture :

- `python -B production/B-15/verifier.py` : **PASS**. Vérification des empreintes et des résultats archivés : 4 contrôles purs, 15 natifs, 155 navigateur sur 10 réponses, 2 tests PHPUnit ; rejeu archivé de 1 208 tests et 36 685 assertions.
- `python -B production/B-13/qualifier.py B-15` : **PASS**, 9 contre-épreuves en mémoire, sans modification des fichiers.

Tentatives de réexécution PHP : `php wp/tests/demo/b15-pure.php` échoue avant lancement, PHP étant absent du PATH ; lancement du même test dans le conteneur local prévu par le lot refusé par WSL (`Wsl/Service/E_ACCESSDENIED`). Les résultats PHP ci-dessus sont donc **archivés et vérifiés, pas reproduits** pendant cette relecture. Les recettes natives/navigateur et `--live` accèdent au site : non lancées conformément aux droits du relecteur. Aucune image reconstruite ni preuve réécrite.

**M1 — mineur — `wp/tests/demo/b15-runtime.php:22`.** `numero_cache_reutilise` compare seulement le HTML de deux appels. Une reconstruction intégrale à chaque appel produirait le même HTML et satisferait cette assertion : elle ne prouve pas l'exigence « construite une fois et gardée en cache ». La lecture du code montre bien le retour anticipé actuel, mais le test ne protège pas ce comportement. **Correction proposée :** compter les passages dans la construction du fragment ou la sélection du numéro ; vérifier une construction au premier appel, aucune au second, puis une nouvelle après invalidation. Vérifier également qu'un mutant supprimant le retour du cache fait échouer cette assertion.

## 4. Sécurité et données

Le composant ne lit ni corps, ni extrait, ni PDF : seulement identifiant, titre, couverture et liens. Les URL, titres et attributs construits sont échappés ; aucun formulaire, traitement de données personnelles ou appel réseau ajouté. Aucun secret ou contenu réel identifié dans les éléments examinés.

Les preuves archivées attestent l'absence des témoins C-26 dans le pied, le rejet d'un témoin injecté, l'absence de sorties HTTP/mail et la restauration des états. Leur intégrité est vérifiée localement ; leur exécution distante n'est pas réitérée.

## 5. Doctrine

Le lot utilise le menu, le gabarit et les transients WordPress. Le choix de ne pas ouvrir une zone de widgets est motivé par le contenu et l'ordre imposés. Les sources officielles sont consignées ; elles n'ont pas été consultées en ligne dans cette relecture.

Code de production sous `Imagine\`, typage strict, textes traduisibles, préfixes cohérents. Pas de nouvelle règle d'accès ni de duplication du sélecteur de numéro. M1 concerne la solidité de la preuve automatisée, sans nécessiter de réécriture du composant.

## 6. Études (lots sans code)

Sans objet : lot avec code.

## Verdict

**À corriger**, pour la preuve de réutilisation du cache uniquement.

- **Bloquant :** aucun constaté.
- **Important :** aucun constaté.
- **Mineur :** M1 — renforcer le test de réutilisation du fragment.

Ce verdict n'est pas un GO. Les limites de réexécution PHP sont indiquées ci-dessus ; aucune question à arbitrer par Ced.
