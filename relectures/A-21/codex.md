# Relecture indépendante Codex — A-21

Date : 26 novembre 2026. Périmètre : brief A-21, production A-21, outil et tests dans `wp/`, dépendances de confinement et neutralisation. Doctrine, décisions et §2.5/§4.4 du cahier des charges lus. Aucun accès à un site, une base ou un compte. Aucun autre fichier modifié ; relecture Claude non consultée.

## 1. Conformité

Les livrables demandés sont présents : script, moteur pur, tests, dix lignes sur le standard, deux lignes dans le mode d'emploi de l'audit, paquet de preuves unique et `PRET`. La finalisation parent distingue correctement « prêt à relire » et clôture ; les anciens reçus candidats sont explicitement historiques.

Le périmètre reste un inventaire : aucune révocation, désactivation ou décision de conservation dans l'outil. Les interprétations sont annoncées : sujets personnalisés regroupés sous `unknown`, comparaison des hôtes exacts, comptes d'inactivité disjoints, anniversaire strict et fuseau WordPress. Le regroupement des sujets libres protège la confidentialité exigée par le brief.

La garantie « aucune sortie, sortie d'erreur comprise » n'est cependant pas assurée pour toutes les sorties du processus PHP : point **R1** ci-dessous.

## 2. Exactitude métier

Déroulés manuels des cas du brief, en application du périmètre de sécurité des §2.5 et §4.4 ; ces paragraphes ne spécifient pas eux-mêmes les seuils de l'inventaire :

- **Clés, cas nominal** — `wp/tests/a21/seed.php:9` : une clé `read` sans accès et une `read_write` utilisée le 1er janvier 2024. Au 26 novembre 2026 : total 2, lecture 1, écriture 0, lecture/écriture 1, jamais utilisée 1, ancienne 1. Le déroulé de `Analysis::keys()` et les rapports classique/HPOS livrés donnent exactement ces nombres.
- **Webhooks, cas nominal** — `wp/tests/a21/seed.php:26` : deux actifs, un en pause et un désactivé ; un actif interne et un externe. Attendu : total 4, états 2/1/1, destinations actives 1 interne et 1 externe. Le sujet libre substitué dans la fixture compte sous `unknown`. Le moteur et les deux rapports correspondent ; le jeton du magasin produit seulement `connected: true`.
- **Copie neutralisée** — `wp/outils/bascule/a21/Analysis.php:18` : la marque entraîne trois rubriques inconnues, avec valeurs `null`, indépendamment des compteurs désormais vides. La lecture de l'import confirme suppression des clés, neutralisation des destinations/secrets et effacement des jetons sensibles. Les reçus de neutralisation et les rapports livrés concordent ; aucun zéro historique n'est inventé.

Limites examinées : accès égal au seuil exclu des anciens, seconde précédente incluse ; accès futur/invalide inconnu ; NULL et date zéro jamais utilisés ; anniversaire du 29 février rabattu au 28 février. Ces cas sont présents dans les assertions pures. Le fuseau local est pris en compte. Le rejeu figé livré est identique. Les calendriers de parution et événements Odoo sont hors périmètre.

## 3. Tests

Exécutés pendant cette relecture, sans produire de fichiers supplémentaires :

- `C:/Python314/python.exe -B -m unittest discover -s wp/tests/a21 -p 'test_*.py'` : **7 tests réussis**, une fois avec `PYTHONIOENCODING=cp1252`, `PYTHONUTF8=0`, puis avec `PYTHONIOENCODING=utf-8`, `PYTHONUTF8=1`.
- `C:/Python314/python.exe -B wp/tests/a21/verify.py production/A-21/preuves/final` : **code 0**, tous les contrôles acceptés. Son statut `CANDIDAT_GATE_PARENT` est cohérent avec son périmètre documentaire.
- Comparaison supplémentaire en lecture seule des deux `dependency-snapshot.json` aux fichiers courants : **48 fichiers par instantané, aucune différence**.

**Limite de rejeu :** le prérequis Docker du banc, interrogé par le helper existant, échoue avec le code `4294967295` ; le diagnostic WSL est `Wsl/Service/E_ACCESSDENIED`. Aucun PHP hôte n'est disponible dans le PATH. Les assertions PHP et matrices natives n'ont donc pas été réexécutées ici. Les résultats livrés — 15 assertions pures, 98 contrôles natifs et 7 contrôles runner par encodage, puis les tests globaux du parent — sont des preuves examinées, pas des succès d'exécution revendiqués par cette relecture.

La couverture livrée dépasse le nominal : droits inconnus, dates, sujets libres, refus de chemins/configurations, six fichiers de remplacement, exceptions, empreintes de toutes les tables et fichiers, rejouabilité et neutralisation réelle sur fixtures. Les exceptions testées ne couvrent toutefois pas les sorties directes et fins de processus décrites en R1.

**R2 — mineur — `wp/tests/a21/verify.py:30` (`source == inventory(OWN)`).** Le vérificateur compare les sources propres au lot, mais ne compare jamais les fichiers de dépendances courants aux `dependency-snapshot.json`. Le manifeste scelle les instantanés archivés, pas les fichiers A-11/A-12/A-02 ou de neutralisation qu'ils décrivent. Une modification ultérieure de ces dépendances peut donc laisser ce vérificateur au vert avec des preuves devenues anciennes. **Correction proposée :** vérifier également les dépendances exécutées contre les sources courantes, en conservant l'exception documentée du README partagé ; ajouter un cas de dérive d'une dépendance. Aucune dérive n'est constatée aujourd'hui par la comparaison supplémentaire ci-dessus.

## 4. Sécurité et données

**R1 — bloquant — `wp/outils/bascule/a21/confine.py:30` (`os.execvp('php', ...)`).** PHP hérite directement des sorties publiques du lanceur, alors que le bootstrap charge les extensions du site. Le tampon de `inventorier-portes` protège les `echo` suivis d'un retour normal ou d'une exception interceptée, mais pas tous les chemins de sortie : une extension qui fait `fwrite(STDERR, __FILE__)` écrit directement un chemin ; `exit('CANARI')` termine avant le nettoyage et laisse le tampon être vidé ; une fonction de fin de processus qui affiche un canari s'exécute après le nettoyage. Ces sorties atteignent l'opérateur sans passer par la liste fermée des erreurs. Ni Landlock ni `display_errors=0` ne filtrent ces écritures. Le contrat explicite de confidentialité du brief est donc contournable, sans avoir besoin d'une exception inconnue.

**Correction proposée :** faire superviser le processus PHP confiné par un lanceur qui capture ses deux flux jusqu'à sa terminaison et ne restitue que des messages reconstruits depuis une liste fermée ; refuser les sorties inattendues et les succès incomplets. Conserver le confinement du processus enfant. Ajouter des fixtures de bootstrap pour écriture directe sur stdout/stderr, `exit` anticipé et fonction de fin de processus, puis vérifier l'absence de canaris sur tous les flux et dans les rapports, y compris après l'annonce de succès. **Nature du constat : analyse statique du chemin d'exécution ; reproduction PHP non exécutée ici pour la limitation WSL indiquée plus haut.**

Pour le reste, les sélections SQL évitent descriptions, clés, fragments, identifiants et secrets de webhooks. Les champs nécessaires à la comparaison des destinations et à l'état du magasin ne sont pas projetés tels quels. Les sorties de données utilisent des catégories fermées. Les requêtes ne prennent aucun filtre utilisateur libre ; le préfixe passe par le parseur partagé. Les protections en lecture seule, contre les appels WordPress et contre les écritures de fichiers sont présentes et couvertes dans les preuves. Le répertoire et les rapports sont créés en 0700/0600. Aucun secret ni donnée réelle identifié dans le périmètre examiné. Nonces et contrôles d'accès web ne s'appliquent pas à cette commande CLI ; aucun nouveau point d'entrée paywall.

## 5. Doctrine

Le standard est décrit avant le complément spécifique. Le lot réutilise le confinement existant et laisse l'import inchangé. Le moteur de calcul est indépendant de WordPress ; les fichiers de production PHP déclarent les types stricts et l'espace de noms `Imagine`. Le reçu PSR-12 livré est vert et lié aux sources courantes. Le README explique emploi, limites et tests. Aucune modification d'extension tierce ni opération sur le réel dans le travail examiné.

## 6. Études (lots sans code)

Sans objet : lot de code. Les références officielles et chemins du code WooCommerce sont indiqués dans le README. Les pages externes et le code de l'image native n'ont pas été consultés pendant cette relecture ; l'accès à un site est interdit par la consigne du rôle et le banc est indisponible. Les affirmations sur la version installée sont donc corroborées ici par les reçus livrés, sans nouvelle vérification indépendante de cette image.

## Verdict

**À corriger.**

- **Bloquant : R1** — sorties du processus PHP non filtrées sur tous les chemins de terminaison.
- **Important :** aucun autre point retenu.
- **Mineur : R2** — vérificateur incomplet sur les dépendances courantes ; absence de dérive vérifiée manuellement pour cette relecture.

Les corrections proposées sont techniques et ne demandent pas d'arbitrage de Ced. Ce verdict n'est pas un GO.
