# Non-régression A-03 — paquet pur

Bibliothèque PHP 8.2+, sans bootstrap WordPress, base, réseau ni réglage métier.
Elle expose `Imagine\NonRegression\Report::compare()` et les méthodes existantes
`Policy::dsn()`, `verified()` et `renewalAllowed()` ; le comportement de Policy est inchangé.
Les fichiers `wp/outils/bascule/a03/{Report,Policy}.php` sont des wrappers `require_once`.
Aucune activation WordPress n'est nécessaire.

## Contrat des rapports

- `schema = imagine-a03-v1` est obligatoire. Une photo est le format historique **sans champ mode**,
  avec toutes les sections de `Site::collect()` : timestamp chaîne, cinq versions chaînes,
  stockage `classic|hpos`, états, échantillons, adhésions, accès, abonnements/comptages,
  actions/comptages journaliers, douze mois, commandes, pages et renouvellement désactivé.
- `sample_states.membership` et `.subscription` sont des dictionnaires `état => true`,
  non des listes. Les inventaires peuvent être vides ; leurs lignes présentes doivent être complètes
  et typées. Les champs inconnus sont refusés, y compris dans les lignes.
- Une sonde a exactement `schema`, `mode = renewal_probe`, `renewal` ; ce dernier contient
  six booléens : `enabled` (vrai), `manual_only`, `created`, `linked`, `pending`, `cleaned`.
  Les indicateurs faux restent comparables, sans les convertir en preuves de réussite.
- Les deux modes ne sont jamais comparables entre eux. Schéma, structure ou mode invalides
  lèvent uniquement un code technique constant (`A03_REPORT_SCHEMA|STRUCTURE|MODE`).
  La commande existante `comparer` traduit ces exceptions en code de sortie 1.
- Les sept clés de pages sont fixes. Une page supprimée devient **anormale** ; si une même page
  manque dans les deux photos, la comparaison est refusée (pas de faux « inchangé »).
- Le timestamp, une fois son type validé, n'entre pas dans les différences. Les classements
  versions = attendu, accès/actions = anormal, pages/sonde = à regarder hors santé dégradée
  restent inchangés. Aucune liste de hooks attendus n'est introduite.

## Clés et confidentialité

Les sections à identifiants exigent des IDs décimaux positifs ; les accès exigent
`uid:post` (uid 0 permis pour l'anonyme). Les clés d'états/groupes, commandes et actions
journalières ont chacune une grammaire dédiée ; les pages et champs de ligne sont fermés.
Aucune valeur n'est émise. Un slug bien formé peut néanmoins être un nom personnel :
les chemins contenant des clés libres (`sample_states`, `samples`, `subscription_counts`,
`action_days`, `orders`) sont donc réduits à `section.[masque]` dans la sortie.
Plusieurs changements peuvent partager ce chemin masqué ; leur nombre et leur classe sont conservés.
Ce paquet valide la structure, pas l'exactitude des lectures SQL ni l'étanchéité du contenu servi.

## Tests et intégration

`phpunit.xml` à la racine, bootstrap `vendor/autoload.php`, tests réels `*Test.php` et
`composer.json`/`composer.lock` rendent le paquet découvrable par T01 sans modifier T01.
Le lock réutilise exactement les dépendances publiques déjà préparées pour imagine-pilotage ;
son empreinte de contenu est calculée par Composer pour le nouveau manifeste.
Dans le conteneur jetable autorisé uniquement : `composer install --no-scripts --no-plugins`,
`composer validate --strict --no-check-publish`, `composer test`, `composer lint`.
La commande de rejeu autorisée du projet reste `wp/tests/rejouer.ps1` ; son image préparée
ancienne doit être reconstruite par la procédure autorisée pour inclure ce nouveau manifeste.
Aucun `vendor/` n'est livré et aucun PHP Windows n'est requis.

PSR-4 : `Imagine\NonRegression\` → `src/` ; après installation Composer,
autoload = `wp/plugins/imagine-non-regression/vendor/autoload.php`.
Les wrappers CLI chargent directement les deux sources et n'exigent pas Composer à l'exécution.
Pour copier les outils dans un banc, préserver le rapport relatif
`wp/outils/bascule/a03/` → `wp/plugins/imagine-non-regression/src/`.
Avec les anciens chemins aplatis `/subject/a03/`, les wrappers résolvent
`/plugins/imagine-non-regression/src/{Report,Policy}.php` : copier ces sources à cet endroit
ou conserver l'arborescence `wp/` complète. Ne pas dupliquer les classes dans les wrappers.

Les arbitrages de `corrections/A-03.md` §5 restent ouverts ; ce paquet ne clôt ni A-03,
ni la vérification fonctionnelle WordPress, et n'autorise aucun accès au réel.
