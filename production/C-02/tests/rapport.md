# C-02 — recette de la bibliothèque PHP

Exécution réelle le 20 novembre 2026, PHP **8.2.36**, PHPUnit **11.5.58**,
dans le runner jetable C-02 sans réseau pendant les suites.

## Résultats finaux

| Suite | Tests | Assertions | Résultat |
|---|---:|---:|---|
| Entreprise (C-02) | 41 | 19 560 | réussie |
| Numeros (C-01) | 39 | 101 | réussie, sources originales inchangées |
| Robots (C-03) | 89 | 199 | réussie, sources originales inchangées |
| Connecteur (C-04, copie distincte) | 22 | 161 | réussie, sources originales inchangées |
| **Total** | **191** | **20 021** | **aucun échec, erreur ou ignoré** |

`composer test` pilotage : 169 tests, 19 860 assertions, code 0.
`composer test` connecteur : 22 tests, 161 assertions, code 0.
`composer lint` (PSR-12), `php -l` et `composer validate --strict --no-check-publish` :
codes 0 pour les deux bibliothèques. Pas d’adaptation du code existant pour obtenir ce résultat.

## Couverture du brief / apport à R-06

| Règle | Preuve automatisée |
|---|---|
| Dix chiffres, premier chiffre 0 ou 1 | `testAccepteDixChiffresEtExposeAffichage`, données `formes` et oracle de clé |
| BE / be, espaces, points, tirets, mélange | `testNormaliseLesFormesDeSaisie`, dix formes valides |
| Neuf chiffres complétés, puis clé obligatoire | données `neuf chiffres`, `ancien format préfixé`, `ancien format cle fausse` |
| Onze / huit chiffres, lettres, vide, premier chiffre 2 | `testRefuseAvecMotifFrancais`, 21 entrées et cinq motifs avec messages exacts |
| Clés 01–97, zéros conservés, rejet des clés 00/98/99 | `testCouvreTousLesRestesEtToutesLesCles` : **19 400** comparaisons, 97 restes × 2 familles de premier chiffre × 100 clés ; oracle de divisions/soustractions, pas appel du code de production |
| Aucun effacement de lettre/pays ou caractère de contrôle | préfixes coupé/répété/étranger, tabulation, saut de ligne, NUL, chiffres Unicode, UTF-8 mal formé |
| Pas de valeur normalisée exploitable après refus | `normalise` et `affichage()` null vérifiés pour chaque rejet |
| Français et traduction injectable | messages exacts et callback exercé pour valide, vide, clé fausse, recherche indisponible et nom fictif |
| Interface et implémentation vide | `RechercheDenominationTest` ; null est indisponible, jamais inexistant |
| Résultats immuables / dénomination non vide | réflexion readonly, constructeur de numéro privé, quatre rejets de noms vides/mal encodés |
| Exemple de documentation réellement exécutable | `exemple.py`, `exemple.{json,log}` : sortie lue du PHP du README final |

Les numéros sont construits par calcul de clé sur des bases fictives. Aucune
entreprise n’est consultée, aucun numéro réel n’est repris d’un registre. Cela
n’affirme pas que ces combinaisons sont réservées ou non attribuées dans la réalité.

**R-06 complet non exécuté** : pas de commande WooCommerce, écran, confirmation
client ni transmission Odoo. Le catalogue de recette n’est ni changé ni automatisé.
La décision 8 reste ouverte ; la disponibilité d’une recherche n’est pas simulée
comme une réponse d’un registre. Le seul nom de test est « Organisation fictive C-02 ».

## Traçabilité RED → GREEN

- `red-canonique` : classe absente, PHPUnit 2 ; premier test nouveau.
- `green-canonique` : 1 test / 5 assertions, puis normalisation testée en échec
  (`red-normalisation`, dix échecs), `green-normalisation` réussi.
- `red-controles` : 21 refus attendus non implémentés, puis `green-controles` réussi.
- `red-traduction` : callback ignoré, puis `green-traduction` réussi.
- `red-recherche` : interface/classes absentes, puis `green-recherche` réussi.
- `final` inclut les compléments négatifs de dénomination et toutes les suites.

Des avertissements PSR-12 de lignes trop longues sont conservés dans certains
passages RED ; ils ont été corrigés, sans suppression des preuves. Tous les
passages GREEN et le final ont les quatre codes de contrôle à zéro. L’erreur
« classe absente » est le RED d’une API nouvelle, pas une erreur de syntaxe.
Le JUnit précédent est retiré avant chaque exécution pour éviter sa réutilisation.

## Conservation et nettoyage

L’inventaire SHA-256 avant travaux contient **377** fichiers existants des lots
C-01/C-03/C-04, de leurs runners et des références locales. Les **375** fichiers
non partagés restent identiques ; pour les deux partagés, retrait du seul appendice
C-02 et de la seule suite Entreprise reconstitue exactement les octets initiaux.
Le contrôle compare aussi l’appartenance des inventaires (pas seulement les hashes).
Aucun fichier vendor ou bytecode n’est ajouté chez les autres lots.

Le runner `imagine-c02-0f9ca8b50f35` a été supprimé, puis son absence relue
(`cleanup.json`). Pas de montage, port, base, site ou processus applicatif ; seul
`sleep` existait avant la suite. Aucun réseau pendant tests/lint/exemple. La
préparation seule a téléchargé Composer et les dépendances publiques verrouillées
dans le runner ; aucune installation hôte ni consultation BCE/VIES.

`check_artifacts.py` est une **vérification déterministe locale** après les
dernières écritures : JUnit, sources testées, documentation, rapports, marqueur,
empreintes et absence du runner. Ce n’est ni une relecture indépendante, ni un GO,
ni une recette en staging ou une autorisation de déploiement. Les conditions d’accès
BCE/VIES ne sont pas attestées : voir `../notes.md` pour les pistes non consultées
et les confirmations requises.
