# Imagine — pilotage (bibliothèques métier C-01 à C-07, sans branchement WordPress)

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
`production/C-01/notes.md`. Ced a décidé le 21/11 que l'anniversaire d'une ouverture
le 29 février est le 28 février suivant, à l'heure d'ouverture, borne exclusive.
Pas de validation juridique,
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

Les durées décidées par Ced le 21/11 sont 3 600 s (positif), 60 s (refus négatif établi
seulement) et 1 000 ms (séquence DNS totale). Délai dépassé/panne de résolution : refus
sans cache, la requête suivante retente immédiatement. Domaine refusé, adresse directe
différente et IP hors plage seulement sont mis en cache négatif. La liste de départ
reste Googlebot/Bingbot seuls, confirmation référenceur attendue. La clé c03-v2 sérialise
le tuple complet version/configuration/identité/IP canonique ; calcul du TTL en UTC.
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

## C-06 — décision d'accès pure, sans restitution de contenu

Point d'entrée unique : `Acces\Moteur::decider($contenu, $visiteur, $robot,
$instant, $decouverte = null): Acces\Decision`. Aucun accès WordPress, base,
session, horloge ou réseau. Les entrées sont fournies par un futur adaptateur de
confiance ; ce moteur ne prouve pas l'étanchéité HTTP du paywall ou des PDF.

Les tableaux ont **exactement** les clés suivantes :

- Contenu : `reserve` (bool), `numero` (chaîne non vide, sans espace ASCII ni
  contrôle), `type` (`article` ou `pdf`), `sortie` (`DateTimeImmutable`),
  `decouverte` (bool).
- Visiteur : `identifie` (bool), `droits` (liste de tableaux). Un anonyme n'a
  aucun droit. Chaque droit suit l'une des formes ci-dessous.
- Robot : `Imagine\Pilotage\Robots\Decision`, calculée pour la même requête par
  C-03 ; un booléen d'UA ne suffit pas. L'identité vérifiée doit être `google`
  ou `bing`. La liste blanche de `src/Acces/Moteur.php` est synchronisée
  **manuellement** avec `config/robots.php` : tout nouveau robot approuvé impose
  de modifier **les deux fichiers**, sinon il reste fermé en extrait. Aucun
  nouveau robot n'est autorisé par cette livraison.
- Instant : `DateTimeImmutable`. Toutes les dates sont à la seconde entière,
  début inclus et fin exclue ; dates fractionnaires ou mutables refusées.
- Découverte : `null` si aucun droit découverte, sinon une des deux politiques
  réglées explicitement ci-dessous. Aucune variante commerciale n'est choisie.

Formes des droits (clés exactes) :

| Type | Autres clés et valeurs |
|---|---|
| `abonnement`, `offert`, `groupe` | `etat` : `actif`, `grace`, `suspendu`, `expire` ou `virement_non_valide` ; `debut`, `fin` : dates immuables, `debut < fin` |
| `achat` | `numero` : identifiant exact ; `acquis_le` : date immuable |
| `equipe` | `role` : `redaction` ou `administration` |
| `cooperateur` | aucune autre clé |
| `decouverte` | `debut` : date immuable ; `compte_verifie` : bool ; `consommes` : entier positif ou nul ; un seul droit de ce type |

Les identifiants sont opaques : `170` et `0170` restent distincts. Le résultat
readonly contient seulement `complet` (bool), `motif` (enum `Acces\Motif`) et
`bloc` (enum `Acces\Bloc` : `aucun`, `abonnement`, `connexion`,
`regularisation`, `decouverte_epuisee`). Il ne transporte jamais de texte,
d'HTML ou d'URL PDF. Entrée manquante, inconnue, incohérente ou exception :
`false / entree_invalide / abonnement`, avant tout cas favorable.

Les droits valides coexistent ; le plus favorable l'emporte, indépendamment
de leur ordre. La grâce utilise la borne effective `fin` fournie, sans durée
inventée. Un achat ouvre uniquement son numéro, article et PDF, sans expiration.

Réglages **tous obligatoires**, sans valeur par défaut :

```php
new Imagine\Pilotage\Acces\DureeDecouverte($secondesPositives, $numeros, $pdfAutorise);
new Imagine\Pilotage\Acces\NombreArticlesDecouverte($quotaPositif, $numeros, $pdfAutorise);
```

`$numeros` est une liste d'identifiants exacts ; vide, elle n'ouvre rien.
`$pdfAutorise` est un booléen explicite ; le contenu doit aussi avoir
`decouverte=true`. La durée compte les secondes écoulées depuis `debut` ;
le quota exige `consommes < quota`. Le moteur ne consomme ni ne persiste rien :
le futur adaptateur devra garantir vérification du compte et décompte atomique.

**Questions non tranchées :** PDF antérieur au début numérique, grâce au-delà du
bandeau, longueur d'extrait et choix commercial découverte ; la fusion ajoute
la prévisualisation avant parution et l'accès robot aux PDF. Aujourd'hui une
sortie future est refusée pour tous ; un robot vérifié ouvre aussi un PDF déjà
paru ; le PDF ancien reste refusé au seul titre de l'abonnement. Ces comportements
existants ne sont pas modifiés par les corrections techniques. Voir
`production/C-06/notes.md` et `corrections/C-06.md` ; aucun branchement autorisé.

### Tests C-06

Uniquement **dans le conteneur jetable autorisé**, depuis ce répertoire :

```sh
composer test                       # Numeros, Robots, Entreprise ET Acces, XML racine
composer test -- --testsuite Acces   # ciblage facultatif
composer lint
composer validate --strict --no-check-publish
```

Depuis Git Bash à la racine du dépôt, Python ne fait que piloter le conteneur ;
aucun PHP ni dépendance ne s'installe sur Windows. Choisir un nom de paquet neuf :

```bash
export IMAGINE_C06_PACKET=corrections-rejeu-unique
python -B wp/tests/acces-runner/run.py prepare
python -B wp/tests/acces-runner/run.py run --name final
python -B wp/tests/acces-runner/run.py close
python -B wp/tests/acces-runner/check-standard-suite.py production/C-06/replays/$IMAGINE_C06_PACKET/final.xml
python -B wp/tests/acces-runner/verify.py seal
python -B wp/tests/acces-runner/verify.py check
unset IMAGINE_C06_PACKET
```

Le lanceur n'injecte plus de configuration PHPUnit particulière : il exerce le
`composer test` standard et conserve le JUnit, les empreintes et les journaux.
Le contrôle `check-standard-suite.py` refuse une commande standard qui omet
Acces. Réseau détaché avant les tests, aucun montage, port, WordPress ou base ;
le nettoyage vérifie l'absence du seul conteneur possédé. Les anciens paquets
restent des preuves historiques de leurs sources, pas des preuves des corrections.

## C-07 — liste d'envoi, historique explicite et CSV

`Envoi\ListeEnvoi::etablir($numero, $calendrier, $abonnements, $cloture)` retourne
un objet readonly (`numero`, `cloture`, `lignes`, `anomalies`). Le numéro et sa
clôture doivent correspondre au calendrier ; aucun droit n'est recalculé.

- `Abonnement(id, origine, creation, situations)` : origine `abonnement`, `offert`,
  `groupe` ou `numero_unite` (cette dernière est toujours exclue).
- `Situation(effet, enregistre, etat, paiementValide, numerosDus, destinataires,
  fin = null)` est une photographie **complète**, pas un patch : état `actif`,
  `grace`, `suspendu`, `expire` ou `attente` ; IDs de numéros dus fournis par C-01 ;
  places attribuées uniquement. `fin` est la borne effective exclusive, y compris
  la fin du délai si l'état est `grace`. Aucune durée n'est inventée.
- `Destinataire(id, nom, rue, complement, codePostal, ville, pays)` ne contient
  pas d'email. Pour un cadeau, fournir le destinataire, jamais l'acheteur ; pour
  un groupe, chaque bénéficiaire, jamais le gestionnaire. Le lecteur de données
  WooCommerce viendra dans un autre lot.
- Les dates sont immuables ; fournir les dates métier en `Europe/Brussels`.
  L'historique doit être complet et append-only, avec un horodatage d'enregistrement
  fiable. Sont retenues les situations dont **effet et enregistrement précèdent
  strictement** la clôture, conformément à C-01. Une arrivée à minuit de clôture
  est trop tardive. Une correction enregistrée après clôture, même rétrodatée,
  ne change pas la liste. Deux situations au même instant d'effet sont refusées.
- Les lignes sont triées par IDs d'abonnement et de destinataire. Le résultat
  readonly n'est pas un stockage : le futur adaptateur devra archiver le résultat
  et les historiques de confiance, sans reconstruire une ancienne liste depuis
  les seules valeurs courantes. Une entrée réécrite rétroactivement n'est pas
  une archive historique et ce moteur pur ne peut pas en garantir l'intégrité.
- Les anomalies sont séparées et référencent l'index de ligne et l'exemplaire :
  `adresse_incomplete`, `pays_manquant`, `doublon_destinataire_adresse`. Les
  exemplaires restent dans la projection, y compris deux abonnements distincts
  au même nom/adresse. Détection des doublons : nom et adresse complète,
  espaces normalisés et casse ASCII ignorée ; pas de rapprochement flou postal.

`Envoi\ExportCsv::liste($liste)` rend les octets CSV et refuse toute anomalie
non revue. `anomaliesRevues: true` n'est à passer qu'après traitement explicite
par l'administration ; ce n'est ni une correction ni une autorisation métier.
`ExportCsv::lignes()` est le sérialiseur bas niveau, pas l'entrée d'expédition.
Le futur adaptateur écrit les octets dans un fichier privé, puis gère sa remise
au routeur ; aucun envoi réseau ni stockage de données réelles ici.

Colonnes provisoires : `abonnement_id`, `destinataire_id`, `destinataire`, `rue`,
`complement`, `code_postal`, `ville`, `pays`, `origine`. Virgule, UTF-8 sans BOM,
fin de ligne LF ; guillemets CSV standards, antislash sans rôle d'échappement.
La protection contre les formules est **la même fonction** que C-04 :
`Imagine\Connecteur\CsvProtection::cellule()`, extraite sans changer sa règle.
Pour un appel hors tests, charger les autoloaders **pilotage et connecteur**
(ou enregistrer leurs deux namespaces PSR-4). Les tests C-07 chargent le
connecteur frère ; aucun `require` de tests n'est à copier dans WordPress.

```sh
# Dans le conteneur uniquement, XML racine incluant la suite Envoi :
composer test
composer test -- --testsuite Envoi
```

Depuis la racine du dépôt, avec un nom de paquet neuf pour ne pas écraser les preuves :

```bash
export IMAGINE_C07_PACKET=rejeu-unique
python -B wp/tests/envoi-runner/run.py prepare
python -B wp/tests/envoi-runner/run.py run --name final
python -B wp/tests/envoi-runner/verify.py
python -B wp/tests/envoi-runner/run.py close
unset IMAGINE_C07_PACKET
```

Le `composer lint` global signale actuellement six avertissements préexistants
dans `tests/Echeancier/run.php` (C-05 en attente). Ils ne sont pas corrigés dans
C-07 ; `verify.py` contrôle séparément PSR-12 sur tous les fichiers PHP modifiés,
les tests C-07 et les régressions C-04. Voir `production/C-07/notes.md`.

