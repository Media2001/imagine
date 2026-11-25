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
- Les sept clés de pages sont fixes et obligatoires dans la référence. Une page supprimée dans
  la seconde photo devient **anormale** ; une référence incomplète est refusée, même si la page apparaît ensuite.
- Le timestamp, une fois son type validé, n'entre pas dans les différences. Les classements
  versions = attendu, accès/actions = anormal, pages/sonde = à regarder hors santé dégradée.
  Exception fermée : `woocommerce_run_on_woocommerce_admin_updated` et son compteur de jour
  deviennent attendus seulement si la version Woo diffère ; les deux côtés d’un ID existant
  doivent porter ce hook. Ce seul travail administratif natif différé a été constaté dans
  les mises à jour A04 classique/HPOS (`production/A-04/COORDINATION.md`). Aucune exception
  pour migrations, paiements, entretien ou préfixe ; tout autre écart reste anormal.
- La photo exige aussi `php_log` : `checked=true`, `from_utc`, `until_utc` (UTC ISO seconde,
  fenêtre ordonnée ≤24 h), `errors` entier positif ou nul. Anciennes photos sans contrôle
  du journal : refus, les régénérer, ne pas ajouter de preuve synthétique à un historique.
  Les dates de fenêtre ne créent pas de diff ; toute nouvelle fenêtre avec diagnostics
  est anormale, même quand le compteur est identique à celui de la référence.

## Journal PHP complémentaire

`PhpLog::read(path, from, until)` lit un journal PHP natif UTC entre deux bornes inclusives.
`PhpLog::during(path, callable)` encadre les GET par ces dates, vérifie identité et préfixe
avant/après, et renvoie `[résultat, bilan]`. Il ne configure ni n’active la journalisation.
Le vrai serveur HTTP doit déjà écrire dans le fichier indiqué par `php_error_log` dans la
configuration de collecte. Vérifier `log_errors=On` et `date.timezone=UTC` côté serveur.
Un fichier vide lisible est valide ; chemin non canonique, lien, permission manquante,
fichier absent, rotation, troncature/réécriture, lecture incomplète ou >16 Mio bloquent
la collecte. Formats inconnus, dates invalides, lignes >64 Kio ou fin tronquée sont refusés,
jamais ignorés. Format reconnu : `[25-Nov-2026 12:00:00 UTC] diagnostic`, avec suites de
trace PHP natives ; chaque enregistrement horodaté dans la fenêtre est un diagnostic,
y compris `error_log()` personnalisé. Ce compteur conservateur n’est pas un nombre
d’exceptions distinctes. Les messages, traces, chemins et valeurs ne sont jamais exportés.
Le contrôle couvre la fenêtre des GET (pas toute une mise à jour antérieure) ; HTTP/display
restent contrôlés en plus. Connexion HTTP impossible ou corps trop grand = refus technique.
Le choix du bon fichier et son activation côté serveur restent des prérequis opérateur.

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
`python wp/tests/a03-non-regression/phpunit.py --name nom-nouveau` rejoue ce paquet seul,
avec découverte et contrôle exhaustif de couverture T01 sur sa copie, sans modifier le banc partagé.
Les dépendances déjà préparées de `imagine-tests-t01:1` sont réutilisées hors réseau ;
aucun `vendor/` n'est livré et aucun PHP Windows n'est requis. Sorties : scratch Hermes.
La commande globale reste `wp/tests/rejouer.ps1` ; si son image ne connaît pas encore ce
manifeste, son propriétaire doit la préparer par la procédure autorisée. Le runner A03 ne
reconstruit pas cette image et ne prétend pas avoir rejoué les autres lots.

PSR-4 : `Imagine\NonRegression\` → `src/` ; après installation Composer,
autoload = `wp/plugins/imagine-non-regression/vendor/autoload.php`.
Les wrappers CLI chargent directement ces sources et n'exigent pas Composer à l'exécution.
Pour copier les outils dans un banc, préserver le rapport relatif
`wp/outils/bascule/a03/` → `wp/plugins/imagine-non-regression/src/`.
Avec les anciens chemins aplatis `/subject/a03/`, les wrappers résolvent
`/plugins/imagine-non-regression/src/{Report,Policy,PhpLog}.php` : copier ces sources à cet endroit
ou conserver l'arborescence `wp/` complète. Ne pas dupliquer les classes dans les wrappers.

Les arbitrages du 25/11 sont appliqués ; ce paquet ne prononce pas la clôture A03
et n’autorise aucun accès au réel. Le banc HTTP fictif utilise un écrivain SQL natif en
transaction annulée, car un serveur HTTP SELECT seul génère des erreurs sur les transients.
Seule la séquence AUTO_INCREMENT synthétique de `wp_options` est restaurée explicitement
après la sortie du collecteur (les lignes et schémas sont contrôlés indépendamment).
Cet adaptateur de banc n’est ni installé par le sujet ni une promesse de HTTP sans écritures
sur un staging réel. Les photos hooks du banc utilisent des lignes AS natives et un oracle
de version antérieure synthétique ; la vraie mise à jour appartient au rejeu A04 du parent.
