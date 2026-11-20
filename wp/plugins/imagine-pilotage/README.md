# Imagine — pilotage (lot C-01)

Bibliothèque métier PHP 8.2, sans WordPress, WooCommerce, base de données,
réseau ni lecture de l'horloge dans le moteur. Ce lot n'est **pas** une extension
WordPress installable : le branchement et le chargement WordPress viendront dans
un autre lot. Aucune activation ni installation sur un site n'est nécessaire.

## Dépendances et tests

Dans un **conteneur jetable autorisé**, depuis ce répertoire :

```sh
composer install --no-interaction --prefer-dist --no-plugins --no-scripts
composer test
composer lint
composer validate --strict --no-check-publish
```

PHP doit fournir notamment dom, mbstring, xml et xmlwriter ; Composer a besoin
d'un extracteur ZIP. `composer.lock` fixe les dépendances de développement
(PHPUnit et PHP_CodeSniffer). `vendor/` reste dans le conteneur, jamais dans ce
lot. Rien à installer sur Windows ou sur l'hôte WSL.

Le lanceur local autorisé est documenté dans `wp/tests/numeros-runner/README.md`
(depuis la racine du dépôt). Il copie seulement cette bibliothèque dans un
conteneur dédié ; il coupe son réseau **avant** les tests et ne monte aucun
dossier, volume, site ou socket Docker. Il ne démarre ni WordPress ni base.

## Utilisation

Toutes les dates d'entrée sont des `DateTimeImmutable`. Le moteur les compare
comme des instants ; ses objets exposent des dates en `Europe/Brussels`.
Les dates éditoriales de clôture et de sortie sont ramenées à minuit Bruxelles.
Le calendrier doit être la liste chronologique exhaustive des parutions connues
jusqu'à son horizon (les identifiants ne sont jamais incrémentés ni inventés).

```php
use Imagine\Pilotage\Numeros\Activation;
use Imagine\Pilotage\Numeros\Calendrier;
use Imagine\Pilotage\Numeros\Moteur;

require __DIR__ . '/vendor/autoload.php';
$zone = new DateTimeZone('Europe/Brussels');
// Fixture fictive uniquement ; le futur adaptateur fournira le vrai calendrier.
$calendrier = new Calendrier(require __DIR__ . '/tests/Numeros/fixtures/calendrier.php');
$moteur = new Moteur($calendrier);
$commande = new DateTimeImmutable('2026-10-08 12:00', $zone);
$annee = $moteur->ouvrir($commande);
// À appeler seulement après confirmation réelle du paiement OU du mandat.
$annee = $annee->activer($commande, Activation::Paiement);
$papier = $moteur->numeros($annee); // 171, 172, 173, 174
$hs = $moteur->horsSerie($annee);  // HS-2027
$echeances = $moteur->echeances($annee, 7); // marge d'exemple, non validée
```

## API et limites

- `ouvrir(dateCommande)` crée un contrat non activé ; `activer(date, motif)`
  produit un nouvel objet. `Activation::Paiement` et `Activation::Mandat` sont les
  seuls événements d'ouverture, pas des preuves de paiement fournies par ce lot.
- `numeros`, `premier`, `dernier`, `horsSerie` projettent le contrat sur le
  calendrier. Ce ne sont pas des autorisations d'expédition sans activation.
- `nonResolus` indique combien des **quatre réguliers** restent inconnus.
  `dernier` est `null` tant que les quatre ne sont pas connus ; `premier` est
  `null` si aucun n'est connu. `horsSerie === null` reste une dette de hors-série,
  distincte des quatre réguliers. Aucun identifiant supposé n'est retourné.
- `renouveler(anneePrecedente, dateDebut)` lie les deux années. Si la fin précédente
  est inconnue, les quatre suivants restent inconnus. Un nouveau `Moteur` avec
  un calendrier complété résout la même chaîne, sans changer les objets contrats.
  L'activation du renouvellement reste explicite, indépendante de la précédente.
- `suspendre(date)` et `reactiver(date)` conservent un historique immuable.
  `accesNumerique(annee, date)` applique ouverture, suspension et anniversaire
  de fin exclusif ; la réactivation ne repousse pas cet anniversaire.
- `aDroit(annee, identifiant, dateObservation)` répond pour la liste d'envoi :
  avant clôture, projection à la date passée ; après clôture, état historique
  juste **avant** minuit de clôture. Une activation/réactivation ce jour-là
  arrive trop tard. Une suspension ultérieure ne retire pas un ancien envoi.
  Les réguliers exclus pendant suspension ne sont pas remplacés automatiquement.
- `restants(annee, date)` renvoie les numéros connus encore éligibles et non
  sortis, hors-série compris. Ajouter séparément `nonResolus` et l'éventuelle
  dette de hors-série à l'affichage. Il n'existe ici aucun suivi postal : la
  sortie est le repère de réception théorique, pas une preuve de livraison.
- `echeances(annee, margeJours)` ne produit que les dates théoriques des réguliers
  connus, même pendant une suspension. Marge obligatoire, strictement positive,
  en jours civils. `Echeance::estPassee(date)` permet de repérer une date déjà
  dépassée ; aucun débit, report, montant, rattrapage ou annulation n'est décidé.
- Pour modifier une date future : `Calendrier::modifier(numero, dateOperation)`
  retourne un nouveau calendrier, puis créer un nouveau moteur. Les clôtures
  passées, les dates rétroactives, les changements de type et les déplacements
  qui changeraient le rang d'un numéro clôturé sont refusés. Le constructeur
  sert à hydrater un calendrier de confiance ; il ne remplace pas cette méthode
  de modification et ne constitue pas un stockage persistant.

Les arbitrages du brief et les limites d'intégration figurent dans
`production/C-01/notes.md`. En particulier, l'anniversaire du 29 février refuse
un résultat arbitraire et demande un arbitrage. Pas de validation juridique,
pas de recouvrement, pas d'adaptateur WooCommerce dans ce lot.

## C-03 — identité des robots, indépendante du paywall

`src/Robots/` vérifie une identité candidate à partir d'un UA et d'une IP explicite :
DNS inverse + domaine autorisé + directe concordante, **ou** appartenance CIDR
IPv4/IPv6, au choix pour chaque robot. `config/robots.php` propose Googlebot et
Bingbot en DNS et cite les pages et sources de plages officielles. Aucun robot
supplémentaire n'est activé et aucun appel réseau n'est fourni par ce lot.

`Verificateur` reçoit `Configuration`, `Dns`, `Cache`, `HorlogeMonotone` ; sa méthode
`verifier(agent, ip, DateTimeImmutable)` rend une `Decision` avec `estVerifie()`,
`robot` (null au refus) et `motif`. Le DNS et le temps sont simulés dans
`tests/Robots/`. Aucun en-tête IP n'est lu et aucun contenu n'est servi.

```sh
# Depuis ce répertoire, uniquement dans le conteneur jetable autorisé :
composer test                         # suites Numeros et Robots
composer test -- --testsuite Robots
composer lint
vendor/bin/phpcs --standard=PSR12 config
php -l config/robots.php
```

Le lanceur réutilisable propre à C-03 et ses commandes sont documentés dans
`wp/tests/robots-runner/README.md`, depuis la racine du dépôt. Les runners et les
preuves C-01/C-04 sont conservés. Rien ne s'installe sur l'hôte.

Les durées proposées sont 3 600 s (positif), 60 s (négatif), 200 ms (séquence DNS).
Le cache est séparé par IP canonique, robot et configuration. Un instantané CIDR
exige une expiration et son cache positif ne la dépasse pas. Le cache mémoire
livré est un exemple local, pas une persistance serveur.

Le futur adaptateur DNS devra garantir un **délai dur** : le moteur refuse une
réponse tardive mais ne peut pas interrompre une implémentation qui ne revient
jamais. Les DNS natifs PHP ne sont volontairement pas branchés. Voir
`production/C-03/notes.md` pour les sources, limites, proxies de confiance et
arbitrages ; `production/C-03/tests/rapport.md` pour les exécutions réelles.

## C-02 — numéro d’entreprise belge, contrôle local uniquement

`Entreprise\NumeroEntreprise::depuisSaisie(string)` retourne un objet immuable :
`estValide()`, `normalise` (dix chiffres ou null), `affichage()` (`0123.456.749`
pour l’exemple calculé ci-dessous, ou null), `motif` (enum ou null) et
`message(?callable $traduire = null)` en français. La clé et le premier chiffre
sont contrôlés après normalisation ; aucune preuve d’existence ou de TVA.

```php
use Imagine\Pilotage\Entreprise\NumeroEntreprise;
use Imagine\Pilotage\Entreprise\RechercheDenominationIndisponible;

// Fixture calculée, sans entreprise interrogée ni numéro réel repris.
$base = '01234567';
$saisie = 'BE ' . $base . sprintf('%02d', 97 - ((int) $base % 97));
$numero = NumeroEntreprise::depuisSaisie($saisie);
if ($numero->estValide()) {
    $recherche = new RechercheDenominationIndisponible();
    $denomination = $recherche->rechercher($numero); // indisponible, jamais « inexistante »
}
```

Pas de réglage, stockage, hooks, écran de commande ou transport réseau. Le
futur adaptateur d’interface doit injecter sa fonction de traduction dans
`message()`, fournir les entrées du catalogue et échapper la sortie. Dans
WordPress : `fn (string $texte): string => __($texte, 'imagine-pilotage')`.
Les motifs sont des identifiants stables, pas des messages techniques à afficher.

```sh
# Dans le conteneur PHP jetable autorisé, depuis ce répertoire :
composer test                       # Numeros, Robots et Entreprise
composer test -- --testsuite Entreprise
composer lint
```

Le lanceur propre à C-02 est décrit dans `wp/tests/entreprise-runner/README.md`.
`production/C-02/notes.md` précise les saisies acceptées, limites et pistes
documentaires non consultées ; la décision 8 reste ouverte. R-06 n’est couvert
qu’au niveau de la bibliothèque, pas du parcours WooCommerce/Odoo.

