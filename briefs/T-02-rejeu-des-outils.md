# Lot T-02 — Le rejeu des tests purs des outils de la voie 1

**Voie** : 1. **Nature** : outillage. **Délai** : deux heures. **Dépend de** : T-01.

## Pourquoi

Depuis A-10, chaque relecture d'un outil de la voie 1 se termine par la même réserve : la commande de rejeu autorisée (`wp/tests/rejouer.ps1`) ne joue que les extensions sur mesure, aucune ligne des outils de `wp/outils/bascule/`. Les relecteurs contrôlent donc tes reçus, ils ne rejouent rien. Or ces outils ont presque tous leur logique en PHP pur, avec un `unit.php` qui ne demande ni WordPress, ni base, ni réseau. Cette partie-là peut être rejouée par n'importe quel relecteur, sans droit nouveau.

## Ce qu'on veut

La **même commande**, sans argument, joue en plus les tests purs des outils :

- chaque `wp/tests/<lot>/unit.php` qui ne dépend que de PHP est exécuté dans le même conteneur jetable, aux mêmes conditions (pas de réseau, dépôt en lecture seule, écritures seulement dans le dossier temporaire du conteneur) ;
- un `unit.php` qui a besoin d'autre chose (WordPress, base, extension commerciale) n'est pas adapté de force : il est listé comme « hors rejeu », avec la raison en quelques mots ;
- la sortie gagne **une ligne** avant la dernière : le nombre d'outils joués, de contrôles, d'échecs, et la liste des lots hors rejeu ;
- **la dernière ligne ne change pas de forme** (`REJEU : … — PASS|FAIL`) : des reçus et le script de relecture la lisent. Elle dit `FAIL` si un test d'outil échoue ;
- ajouter un outil ne demande pas de modifier la commande : une convention de découverte, écrite en trois lignes dans le mode d'emploi de T-01.

Règles :

- tu ajoutes, tu ne réécris pas : l'isolation du conteneur de T-01 reste telle quelle, aucune option n'est assouplie, aucun nouveau script à autoriser ;
- les matrices natives (classique et HPOS, extensions commerciales) restent hors de cette commande : c'est une limite connue, dis-le en une phrase ;
- les lots clos le restent ; leurs paquets de preuves ne sont pas régénérés pour ce lot ;
- si l'image doit changer, `preparer-image.ps1` le fait, et tu le dis : Ced devra la relancer une fois.

## Preuve

Proportionnée. La sortie complète d'un rejeu vert ; un test d'outil rendu rouge à la main fait passer la dernière ligne à `FAIL`, puis est remis en état ; la suite PHPUnit garde son nombre de tests ; aucun conteneur ne reste. Dis combien d'outils sont joués et lesquels restent hors rejeu.

## Livrables

Les scripts modifiés, trois lignes dans le mode d'emploi de T-01, `production/T-02/PRET`. Rapport court.
