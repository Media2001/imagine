# B-10 — points de vente

## Standard natif (cinq lignes)
1. Quelques centaines de commerces tiennent dans un type de contenu WordPress `imagine_vente`, sans table supplémentaire.
2. Le titre et une métadonnée structurée conservent uniquement les champs expressément mappés ; aucun compte ni raccord C-21.
3. Le type est privé, sans REST ni recherche générale ; une page native restitue la seule liste active.
4. Une option non autoloadée désigne les IDs actifs : un nouvel import est préparé puis basculé, un rejeu identique garde les IDs.
5. Administration, capacité `manage_options`, nonces et formulaires natifs ; CSV PHP, sans bibliothèque ni fournisseur distant.

Sources officielles consultées : https://developer.wordpress.org/reference/functions/register_post_type/ ; https://developer.wordpress.org/reference/functions/register_post_meta/ ; https://developer.wordpress.org/apis/settings/ ; https://www.php.net/manual/en/function.fgetcsv.php (échappement propriétaire désactivé explicitement).

## Décisions prises à défaut
- Recherche exacte après suppression des accents, passage en minuscules Unicode et trim ; pas de préfixe postal ni rayon. Tri localité puis nom, mêmes règles.
- CSV UTF-8 avec en-tête, BOM permis, séparateur configurable `;`, `,` ou tabulation ; guillemets doubles standard. Plafond technique 2 Mio, 2 000 lignes acceptées, champs de 500 caractères.
- Correspondance JSON : clés fermées `nom`, `adresse`, `localite`, `postal`, facultativement `personne` et `telephone`. Ces deux dernières exigent une ligne explicite ; aucune colonne inconnue n'est conservée. Les quatre champs requis ne peuvent pas être vides.
- En-tête/mapping invalide ou zéro commerce accepté : l'ancienne liste reste active. Refus de ligne : numéro physique initial et motif fixe, jamais la donnée. Doublon exact refusé. Un import valide remplace toute la liste, sans fusion.
- La carte est un réglage fermé `0|1`, défaut `0` et valeur inconnue ramenée à `0`. À `1`, emplacement seulement, sans script/image/iframe.
- Page de réglages dédiée Réglages → Points de vente ; aucun changement de l'écran C-10 clos. Pas de style nouveau.

## Corrections de la fusion du 27 novembre 2026, 10 h 41
- Désaccentuation : `Normalizer::FORM_D` si **intl** est disponible ; puis suppression des marques combinantes. `œ→oe` et `æ→ae` sont explicites, car ces ligatures ne se décomposent pas. Sans intl : repli latin étendu (dont `ḉ`, `ǵ`, `ǘ`), plus retrait des marques NFD. **Ce repli borné n'est pas une promesse de translittération de tout Unicode.** Pour une décomposition Unicode générale, intl est la dépendance à garantir sur l'hébergement cible, encore inconnu. La démo native dispose de Normalizer ; l'image PHPUnit ne l'a pas. Les deux chemins ont réellement été exercés, sur NFC/NFD hors de l'ancienne table et sur les deux ligatures.
- Reprise : l'option non autoloadée `imagine_vente_nettoyage` conserve les IDs avant bascule. Un refus de suppression laisse la nouvelle liste active et un message « Liste remplacée ; nettoyage incomplet », pas un import refusé. Le même CSV retente, y compris en no-op, sans changer ses IDs ; un nouveau processus/requête relit cet état. Un ID encore actif n'est jamais supprimé, un type étranger reste en attente plutôt qu'être détruit, un ID déjà absent est retiré de la reprise. La reprise doit être persistée et relue avant bascule ; une panne à cette étape refuse la bascule. Pas de tâche planifiée ajoutée ; arrêt brutal/verrou d'import : diagnostic manuel toujours requis.
- Une méta active illisible ne bloque plus le remplacement réparateur. Les motifs restent des codes dans les résultats/tests ; l'interface affiche seulement des chaînes françaises littérales traduisibles, jamais une cellule CSV. La configuration est lue une seule fois par rendu.
- **Défaut C2 conservé : l'ordre des clés du JSON de correspondance compte pour le no-op strict.** Même fichier + mêmes clés dans le même ordre : IDs conservés. Réordonner des clés équivalentes peut réinsérer la liste et changer ses IDs. Limite documentée, pas de normalisation du mapping ajoutée sans demande.
- **Vraie bascule, hors lot :** remplacer la liaison page↔extension du seed de démonstration par un script de bascule versionné et rejouable avant toute mise en ligne réelle. Aucun script de production créé ici.

## Preuves actuelles (pas les décomptes historiques de relecture)
`corrections-reception-V2.json` lie les sources et reçus courants. PHPUnit : **14 tests, 80 assertions**, repli sans intl réellement exécuté ; natif WordPress : **13 contrôles**, Normalizer présent ; navigateur : **31 contrôles**, dont refus natif de suppression, reprise du même CSV entre requêtes, disparition du post et de sa méta personnelle fictive, réparation de liste illisible et recherche Unicode.

Image reconstruite : `corrections-preparation-V2.log`. Rejeu général frais : **1 187 tests, 36 494 assertions**, aucun échec/erreur ; **584 contrôles outils** verts. B11 stabilisé et inchangé. A32 / `A32_PARTIAL_EVIDENCE` reste signalé hors périmètre, sans modification.

Le premier reçu `corrections-recette-V2.json` reste rouge : l'ancien oracle comparait les empreintes des posts B10 alors que le test venait volontairement de les remplacer. Diagnostic : seules les empreintes posts/postmeta avaient changé. Le reçu final contrôle exactement tous les objets hors du seul CPT B10, et séparément les 30 lignes B10, carte OFF, reprise vide, sessions exactes et navigation. Aucun état tiers réinitialisé pour obtenir le vert. Les rouges PHPUnit et les reçus initiaux sont conservés, pas réécrits.

## Carte ultérieure (trois lignes)
Il faudra choisir un fournisseur, son coût et les conditions de chargement, sans présumer de ce choix ici.
Il faudra disposer des coordonnées dans le fichier ou faire approuver un géocodage séparé ; aucun n'est tenté par B-10.
Tout fond de carte tiers devra attendre le consentement approprié et rester déchargé avant celui-ci (§4.4).

## Questions laissées ouvertes
Imagine attend-il une recherche par rayon ou préfixe postal ? Le défaut de ce lot reste strictement exact.
Validation visuelle de Ced attendue ; données et adresses entièrement fictives.
