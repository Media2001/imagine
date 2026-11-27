# Lot T-03 — Les vérificateurs de paquet, rejoués par les relecteurs

**Voie** : 1. **Nature** : outillage. **Délai** : deux heures. **Dépend de** : T-01, T-02. **Doctrine** : §6 (un lot se clôt sur des preuves rejouées par quelqu'un d'autre que son auteur).

## Pourquoi

Depuis A-20, chaque vérification se termine par la même phrase : « je n'ai pas pu lancer `verify.py` ». Les relecteurs n'ont droit qu'à une commande, `wp/tests/rejouer.ps1`, et elle ne joue pas les vérificateurs de paquet. A-22, le gardien de tous les outils d'inventaire, attend depuis le 26/11 à 22 h qu'une personne indépendante lance le sien ; cette personne ne peut être que Ced. Ce n'est pas tenable lot après lot.

Depuis A-26, tes paquets ont un vérificateur **sans argument** et en lecture seule (`production/<lot>/verify.py`). Il peut être rejoué par n'importe quel relecteur, sans droit nouveau, s'il tourne là où tournent déjà les tests. Les lots plus anciens (A-20 à A-25) ont un vérificateur qui prend le dossier du paquet en argument : la requalification commune leur donne la même entrée sans argument, sans changer un contrôle.

## Ce qu'on veut

La **même commande**, sans argument, joue en plus les vérificateurs de paquet :

- chaque `production/<lot>/verify.py` qui se déclare rejouable (une convention de découverte, écrite en trois lignes dans le mode d'emploi de T-01) est exécuté **dans le conteneur jetable**, aux mêmes conditions que les tests : pas de réseau, dépôt en lecture seule, écritures seulement dans le dossier temporaire du conteneur ;
- un vérificateur qui a besoin d'autre chose (Docker, réseau, écriture dans le dépôt, un argument) n'est pas adapté de force : il est listé « hors rejeu », avec la raison en quelques mots. Un paquet dont les journaux ne sont pas dans la copie du dépôt est « hors rejeu : journaux absents », pas un échec ;
- la sortie gagne **une ligne**, `PAQUETS : n vérifiés, n échecs ; hors rejeu : …`, avec, pour chaque échec, le lot et le nom du contrôle rouge, rien d'autre ;
- **la dernière ligne ne change ni de forme ni de sens** (`REJEU : … — PASS|FAIL`) : elle ne parle que des tests. Un paquet périmé chez un voisin ne doit pas faire échouer la vérification d'un autre lot ; le relecteur lit la ligne `PAQUETS` pour le sien.

Règles :

- rien ne tourne sur Windows hors du conteneur ; aucune commande nouvelle à autoriser dans `scripts/relire.ps1`, que tu ne modifies pas ;
- tu ajoutes, tu ne réécris pas : l'isolation de T-01 reste telle quelle, aucune option n'est assouplie ;
- les vérificateurs existants ne sont pas réécrits pour ce lot ; une entrée sans argument ajoutée à un lot déjà livré appelle le vérificateur existant sur son paquet unique, ne change aucun contrôle, et tu le dis lot par lot ;
- les matrices natives restent hors de cette commande : limite connue, une phrase ;
- si l'image doit changer (Python), `preparer-image.ps1` le fait et tu le dis.

## Preuve

Proportionnée. La sortie complète d'un rejeu vert, avec le vérificateur d'A-22 et celui d'A-28 parmi les paquets vérifiés ; sur une copie jetable, un reçu altéré d'un octet fait passer la ligne `PAQUETS` à un échec nommé sans changer la dernière ligne, puis la copie est jetée ; la suite garde son nombre de tests ; aucun conteneur ne reste. Dis combien de paquets sont vérifiés et lesquels restent hors rejeu.

## Livrables

Les scripts modifiés, trois lignes dans le mode d'emploi de T-01, `production/T-03/PRET`. Rapport court.
