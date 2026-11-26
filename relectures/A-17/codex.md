# Relecture indépendante Codex — A-17

Date : 26 novembre 2026. Références : `relecteurs/AGENTS.md`, doctrine, grille, brief A-17, décisions et cahier des charges §4.4. Examen de la production A-17, du code et de ses dépendances A-02/A-11/A-12. La relecture Claude n'a pas été consultée.

## 1. Conformité

Les livrables sont présents : commande confinée, tests, documentation, deux lignes dans le mode d'emploi partagé, paquet unique et marqueur `PRET`. L'outil inventorie sans activer de protection ni choisir les titulaires des droits. Les limitations des adaptateurs et le décompte multi-rôles sont documentés.

- **R1 — Important — `wp/outils/bascule/a17/Inventory.php:85` : le compteur des mots de passe d'application ne conserve pas le sens attendu après l'import anonymisé.** L'outil compte les entrées encore présentes dans la copie. Or `wp/outils/staging/lib.php:270` classe `_application_passwords` comme secret et la transformation supprime la ligne à la ligne 346 ; le parcours d'import appelle cette transformation. Un compte qui portait un mot de passe d'application donne donc zéro après neutralisation. Le brief promet des nombres justes sur le site anonymisé afin d'établir l'état des comptes hérités. Le banc crée au contraire le mot de passe directement dans sa fixture (`wp/tests/a17/seed.php:13`) sans traverser cet import. **Correction proposée :** établir un contrat avec l'import permettant de conserver uniquement l'information non secrète nécessaire au décompte, avec sa provenance, puis la lire dans A-17 ; en son absence, afficher « inconnu après neutralisation » au lieu d'un zéro interprétable comme l'état initial. Ajouter un parcours fictif avant/après anonymisation. Ne conserver ni empreinte ni secret utilisable. Cette incompatibilité entre lots doit être tracée comme écart.

- **R2 — Important — `wp/outils/bascule/a17/Inventory.php:12` : des rôles de gestion sont omis.** La liste reconnaît `create_users`, `delete_users` et `promote_users`, mais pas `edit_users` ; elle omet aussi notamment `update_plugins` et `switch_themes`. Un rôle sur mesure `gestion_comptes` portant seulement `read` et `edit_users` accordées retourne `false` dans `management()` et disparaît entièrement des agrégats. Cela contredit « tout rôle sur mesure portant une capacité de gestion » et sous-estime les comptes à examiner. **Correction proposée :** compléter et documenter la liste des capacités natives de gestion, avec tests séparés pour les capacités isolées et refusées ; ne pas se limiter aux préfixes actuellement reconnus.

## 2. Exactitude métier

Déroulés manuels des règles du brief qui déclinent le §4.4 :

1. Au 26 novembre 2026 à 12 h UTC, deux administrateurs, dont un doté d'un mot de passe d'application et d'une 2FA reconnue : le code produit `accounts=2`, `application_password_accounts=1`, `two_factor_active=1`. Une connexion du 1er janvier 2025 est ancienne ; celle du 1er novembre 2026 ne l'est pas. Les rapports classic et HPOS livrés portent ces résultats. Ce cas est correct avant les réserves R1 et R3.
2. Sans API 2FA reconnue, `two_factor_active=null` et adaptateur `inconnu` : les rapports `classic-unknown` et `hpos-unknown` le confirment. Sans journal reconnu, le chemin de code rend également un compteur ancien `null`, sans déduire une inactivité. Avec journal reconnu et date absente, le compte rejoint `unknown_accounts`.
3. À la borne exacte du 26 novembre 2025 à 12 h UTC, la comparaison stricte `$last < $cutoff` n'incrémente pas le compteur ancien ; une seconde avant, elle l'incrémente. Cela concorde avec l'interprétation explicitée dans le README, mais ce cas n'est pas exécuté par les tests livrés.

- **R3 — Important — `wp/outils/bascule/a17/Inventory.php:50` : la présence de Two-Factor transforme un inventaire partiel en total certain.** Dès que son API est disponible, tous les compteurs 2FA deviennent numériques. Si une autre extension de 2FA active protège certains comptes, les réponses négatives de Two-Factor restent comptées comme des absences, même lorsque l'autre fournisseur apparaît dans `protections`. Exemple : deux administrateurs protégés par deux fournisseurs différents, dont un seul pris en charge, donnent `two_factor_active=1` au lieu d'un total inconnu ou explicitement partiel. Le test « fournisseur inconnu » retire seulement l'API connue et ne teste pas cette coexistence. **Correction proposée :** exposer la couverture par fournisseur ; ne publier un total certain que lorsque la couverture est établie, sinon indiquer « inconnu » ou un minimum observé clairement distinct du total. Ajouter le cas de coexistence en classic et HPOS.

- **R4 — Important — `wp/outils/bascule/a17/Inventory.php:149` : l'analyse des conditions PHP peut déclarer à tort l'édition des fichiers interdite.** Le parseur ne suit que la profondeur des accolades et le token précédent. Pour `<?php if (false): ; define('DISALLOW_FILE_EDIT', true); endif;`, la profondeur vaut zéro et le token précédent est `;` : il retient `true`, alors que cette définition n'est jamais exécutée. Le rapport affiche alors `admin_file_editing=false`. Le README promet « inconnu » pour une expression non résolue. **Correction proposée :** identifier aussi les structures conditionnelles à syntaxe alternative ou refuser prudemment de conclure lorsque la définition n'est pas démontrée inconditionnelle. Ajouter ce cas au test des définitions conditionnelles, sans exécuter le fichier de configuration. Constat par lecture des tokens et du code ; reproduction PHP empêchée par WSL, comme indiqué ci-dessous.

## 3. Tests

Exécutés pendant cette relecture, sans création de fichiers de test ni de bytecode :

| Commande / contrôle | Résultat |
|---|---|
| `python -B wp/tests/a17/test_launcher.py` | 3 tests réussis, code 0 |
| `python -B wp/tests/a17/verify.py production/A-17/preuves/final` | 20 contrôles réussis, code 0 |
| Comparaison en mémoire des SHA-256 de `dependency-snapshot.json` avec les fichiers actuels | 26 dépendances identiques |

Le vérificateur confirme les sources, manifestes, reçus et empreintes livrés. Il lit **10 assertions PHP, 50 contrôles natifs et 7 contrôles du runner** annoncés verts ; ce n'est pas leur réexécution. Les reçus classic/HPOS attestent les empreintes de toutes les tables avant/après et la stabilité des fichiers, ainsi que les gardes d'écriture, de mail, de réseau et de planification.

**Limite du rejeu :** une tentative de tests PHP sans écriture, par entrée standard vers `wsl.exe -d Ubuntu -- php`, a échoué avant PHP avec `Wsl/Service/E_ACCESSDENIED`. PHP n'est pas disponible directement sous Windows. La suite native `run.py`, qui dépend du même WSL, n'a donc pas été rejouée. Elle impose en outre un répertoire de résultats hors dépôt (`wp/tests/a17/run.py:28`) ; je n'ai pas créé ces fichiers supplémentaires compte tenu de l'écriture limitée au présent rapport. Aucun environnement ni aucune base n'a été ouvert.

Lacunes pertinentes pour les corrections : rôles à capacité isolée, coexistence des fournisseurs 2FA, passage par l'anonymisation et confidentialité des refus. Les tests de date ne couvrent ni l'égalité à la borne, ni une date future, ni une année bissextile ; les comptes multi-rôles ne sont pas exercés. L'API Two-Factor est remplacée par une lecture de métadonnée fictive (`wp/tests/a17/inside.py:24`) : cela valide l'agrégation, pas le contrat effectif de l'extension. Cette limite est honnêtement documentée et doit rester explicite dans les preuves.

## 4. Sécurité et données

Les sorties nominales examinées sont agrégées ; aucun secret ni aucune donnée réelle n'y a été identifié. Les canaris sont fictifs. La commande reprend les barrières A-11/A-12 avant le chargement de WordPress et contrôle ses arguments et chemins de sortie. Elle n'ajoute aucune interface web : nonces, formulaires et paywall sont hors du périmètre modifié.

- **R5 — Bloquant — `wp/outils/bascule/a17/inventorier-securite:38` : un refus peut divulguer un chemin contenant une identité.** Le gestionnaire d'erreur recopie sans filtrage les détails de `Runtime::refusalMessage()`. En présence d'un lien symbolique, A-11 y place le chemin relatif du fichier (`wp/outils/bascule/a11/Runtime.php:61`). Un lien nommé `wp-content/uploads/A17_LOGIN_PRIVATE_CANARY.pdf` entraîne donc la sortie de ce canari sur stderr, malgré le refus d'exécution. Les noms de fichiers peuvent contenir un nom ou une adresse : la garantie « absent de toutes les sorties » ne tient pas. Le test actuel contrôle les sorties du succès et un drop-in au nom fixe, pas ce refus. **Correction proposée :** filtrer les détails au niveau de la sortie A-17, garder un code de refus fixe pour les chemins arbitraires et ne nommer que les fichiers techniques issus d'une liste fermée. Ajouter un canari dans un chemin refusé et vérifier stdout, stderr et les éventuels artefacts. Constat établi par le chemin de code, sans création de lien ni accès à un site.

## 5. Doctrine

Le recours aux API natives pour rôles, mots de passe d'application et extensions est cohérent avec « standard d'abord ». Le PHP de production examiné utilise `strict_types` et l'espace de noms `Imagine`. Le reçu PSR-12 indique zéro erreur et zéro avertissement sur les sources livrées ; il n'a pas été rejoué ici.

Les corrections proposées sont techniques et ne nécessitent aucun choix de titulaire de droits. Défaut prudent : information non démontrable = « inconnu », aucun secret conservé, aucun détail personnel dans les refus. Aucun arbitrage visuel, métier ou touchant au réel n'est demandé à Ced. Les changements inter-lots nécessaires à R1 devront être instruits et tracés sans accéder à une sauvegarde réelle.

## 6. Études (lots sans code)

Sans objet : ce lot contient du code. `production/A-17/sources-officielles.json` fournit des adresses officielles, dates et empreintes, mais pas le contenu ni les citations des pages. Ces références ont été lues dans le dépôt ; leur contenu distant n'a pas été vérifié pendant cette relecture, conformément à l'interdiction d'accéder à un site. Le contrat réel des adaptateurs reste donc une limite de preuve, et non une validation indépendante de leur documentation.

## Verdict

**À corriger.**

- **Bloquant : R5**, confidentialité des sorties de refus.
- **Importants : R1**, perte du sens du compteur après anonymisation ; **R2**, rôles de gestion omis ; **R3**, total 2FA présenté comme certain malgré une couverture partielle ; **R4**, faux diagnostic sur une définition conditionnelle.
- **Mineur :** aucun point distinct retenu.

Ce verdict n'est pas un GO. Seul `relectures/A-17/codex.md` a été écrit ; aucun correctif n'a été appliqué.
