# Relecture indépendante Codex — A-16

Date : 26 novembre 2026. Références : `relecteurs/AGENTS.md`, doctrine, grille, brief A-16, cahier des charges §4.3 et décisions du dépôt. Examen de `wp/outils/bascule/a16/`, de ses dépendances A-11/A-12, de `wp/tests/a16/` et de `production/A-16/`. La relecture Claude n'a pas été consultée. Aucun autre fichier n'a été modifié.

## 1. Conformité

Le script, la correspondance fictive, les tests, les deux lignes du mode d'emploi, le rapport court et `PRET` sont présents. Le paquet de preuves est unique. L'outil réutilise le confinement A-12 et le démarrage en lecture seule A-11, impose une correspondance et ne rattache aucun article. Les conventions de dates, d'états et de médias sont explicitées dans la livraison. Le brief renvoie bien au §4.3.

**R1 — Important — `wp/outils/bascule/a16/Inventory.php:67` — Les PDF hors du dossier public ne peuvent pas être inventoriés.** Tout fichier extérieur à la base uploads est refusé ; la base elle-même doit rester sous la racine du site. Un PDF local existant dont la pièce jointe indique un chemin absolu vers un dossier privé provoque donc `A16_ATTACHMENT_PATH_UNSAFE`, au lieu de produire `pdf=oui` et `pdf_public=false`. Pour les fichiers acceptés, `public` vaut systématiquement `true` : le renseignement demandé par le brief n'a jamais de branche négative. **Correction proposée :** permettre à l'opérateur de déclarer explicitement une racine locale privée dans la correspondance, vérifier les chemins dans les seules racines autorisées et calculer séparément présence et emplacement public, sans accès HTTP ni chemin dans les sorties. Ajouter les cas PDF privé présent et absent au banc classique/HPOS.

## 2. Exactitude métier

Deux cas du §4.3, déclinés par le brief et déroulés à partir du jeu fictif :

- Numéro 26, daté du 1er mars 2026 : deux articles, dont un publié et un brouillon ; un sans thématique, un avec deux thématiques ; un sans image principale ; deux médias attachés dont un absent ; PDF présent dans uploads. Le parcours du code donne respectivement `2, 1, 1, 1, 1, 1, 2, 1`, puis `oui/true`. Les sorties classique et HPOS conservées correspondent exactement.
- Numéro 25, daté du 1er février 2026 : un article publié, une thématique, aucune image principale ni média attaché ; pièce jointe PDF déclarée mais fichier absent. Le code et les deux sorties donnent un article, zéro anomalie de thématique, une image manquante, zéro média, puis `declare_mais_fichier_absent/true`.

Le numéro 24 sans article ni PDF donne les zéros attendus et `non/null`. L'article publié sans rattachement est compté une fois en 2025. La lecture du code confirme que les orphelins sont recherchés sur tous les numéros avant la limitation à N, et que les égalités de date sont départagées par ID décroissant. Ces comparaisons reposent sur le code et les preuves livrées, pas sur un rejeu PHP indépendant réussi.

**R2 — Mineur — `wp/outils/bascule/a16/Mapping.php:20` — L'ordre des propriétés JSON change la validité de la correspondance.** `{"cle":"_a16_numero_id","source":"postmeta"}` est rejeté alors qu'il exprime exactement la liaison acceptée avec les propriétés inversées. La comparaison stricte de `array_keys()` impose un ordre qui n'a pas de signification pour un objet JSON. **Correction proposée :** comparer l'ensemble des clés attendues indépendamment de leur ordre, tout en refusant les clés absentes ou supplémentaires ; tester les deux ordres.

## 3. Tests

Exécutions indépendantes réalisées, sans génération de fichiers dans le dépôt :

- `python -B wp/tests/a16/test_launcher.py` : **3 tests réussis**, code 0.
- `python -B wp/tests/a16/verify.py production/A-16/preuves/final` : **20 contrôles réussis**, code 0. Le vérificateur confirme les empreintes des sources propres au lot, le manifeste du paquet et les reçus livrés : 7 assertions unitaires, 54 assertions natives et 7 contrôles du runner. Il vérifie aussi les instantanés de base conservés et la matrice Windows UTF-8/cp1252.
- Prérequis du rejeu natif, exécuté via le même appel du runner à `wsl.exe -d Ubuntu -- docker image inspect` sur son image épinglée : **échec `Wsl/Service/E_ACCESSDENIED`**, code 4294967295. Le banc PHP classique/HPOS n'a donc pas pu être relancé ici. Les résultats natifs mentionnés ci-dessus restent ceux du paquet livré ; leur vérification ne remplace pas leur réexécution.

Le banc contrôle réellement plusieurs interdictions d'écriture et d'effets externes, les trois états de PDF, les variantes de liaison, les comptes, le canari nominal et le rejeu identique.

**R3 — Mineur — `wp/tests/a16/inside.py:53` — Le test annoncé comme déterministe ne couvre ni une égalité de dates ni l'orphelin hors sélection.** Les trois dates sont différentes ; le numéro exclu par `--limit=2` ne contient aucun article ; l'assertion ne compare que `issues`. Une régression du départage ou un calcul des orphelins limité à N pourrait donc rester verte. **Correction proposée :** ajouter deux numéros de même date et vérifier l'ordre par ID, puis rattacher un article publié à un numéro exclu de N et vérifier qu'il reste absent des orphelins. Conserver un véritable orphelin pour distinguer les deux cas.

## 4. Sécurité et données

Les requêtes variables sont préparées ; le démarrage utilise la connexion en lecture seule et les gardes héritées ; les permissions de sortie sont contrôlées. Les sorties nominales examinées ne contiennent ni titre, ni texte, ni auteur, ni chemin source. Aucune voie HTTP ou de paywall n'est ajoutée par ce lot. Aucun site, compte ou service réel n'a été consulté pendant cette relecture.

**R4 — Important — `wp/outils/bascule/a16/inventorier-numeros:39` — Les erreurs héritées divulguent des chemins source sur stderr.** L'appel à `Runtime::refusalMessage()` transmet sans filtrage les détails des refus A-11. En présence d'un lien symbolique sous le site, le démarrage construit `A11_SYMLINK_UNSUPPORTED` avec le chemin relatif réel du lien dans `file` ; ce chemin peut contenir un titre ou un nom de personne. Il ressort alors sur stderr malgré l'interdiction du brief portant sur toutes les sorties. Le test de canari nominal ne couvre pas cette branche. **Correction proposée :** filtrer les détails au point de sortie A-16, ne conserver que les codes et les identifiants explicitement autorisés, notamment la clé de correspondance absente, et supprimer les chemins source. Tester un lien symbolique dont le nom porte un canari, en vérifiant stdout, stderr et les éventuels fichiers produits.

## 5. Doctrine

Le code PHP propre au lot déclare les types stricts et utilise l'espace de noms `Imagine\IssueInventory`. Le paquet contient un contrôle PSR-12 sans erreur ni avertissement, lié aux empreintes vérifiées. Le README décrit la commande, les limites et le rejeu. Le périmètre reste un audit complémentaire, sans transformation du contenu ni modification d'une extension tierce.

La livraison fournit des références officielles sur les métadonnées et les taxonomies. Leur contenu distant n'a pas été consulté, conformément à l'interdiction d'accès à un site donnée au relecteur ; la justification de l'absence d'un rapport standard équivalent n'a donc pas été vérifiée indépendamment.

### Décisions techniques, défaut proposé

R1 à R4 sont des corrections techniques. Défauts proposés : racines de fichiers explicitement autorisées, emplacement public distinct de la présence, propriétés JSON sans ordre imposé, sorties d'erreur limitées à une liste de détails autorisés et cas limites vérifiés sur le banc fictif. Aucun arbitrage visuel ou touchant au réel n'est demandé à Ced.

## 6. Études (lots sans code)

Sans objet : lot de code.

## Verdict

**À corriger.** Ce verdict n'est pas un GO.

- **Bloquant :** aucun point classé à ce niveau.
- **Important :** R1, PDF privés impossibles à inventorier ; R4, divulgation de chemins dans les erreurs.
- **Mineur :** R2, correspondance sensible à l'ordre des propriétés ; R3, cas limites insuffisamment éprouvés.

Limite de validation : rejeu natif empêché par le refus d'accès WSL ; tests Python et vérification du paquet réussis.
