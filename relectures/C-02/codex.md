# Relecture indépendante Codex — C-02

Date : 20 novembre 2026. Périmètre : brief C-02, production C-02, sources et tests Entreprise dans `wp/`, configuration partagée et lanceur associé. Références : doctrine, grille, exigences du brief C-01, cahier des charges §3.4, décision 8 et recette R-06. Le rapport de Claude n’a pas été lu. Aucune correction de production effectuée.

## 1. Conformité

Le code respecte le périmètre fonctionnel : normalisation belge, ajout du zéro pour neuf chiffres, contrôle du premier chiffre et de la clé, motifs français, interface de recherche et implémentation indisponible sans réseau. Les renvois au §3.4 sont présents. Les restrictions sur les espaces et les préfixes, l’ordre des motifs et l’acceptation mathématique d’une base nulle sont explicités dans les notes. La recherche réelle et le parcours complet R-06 restent correctement distingués de cette bibliothèque ; la décision 8 n’est pas tranchée implicitement.

**C02-01 — important — `production/C-02/notes.md:62`.** Les sources BCE/VIES sont qualifiées de « pistes documentaires indicatives non consultées et non vérifiées dans ce lot ». Le tableau fournit des questions à vérifier, mais aucune condition d’accès établie. Or le brief demande les sources officielles possibles, leurs conditions d’accès et leurs limites, avec leur documentation. L’absence de recherche réelle dans le code ne dispense pas de ce livrable documentaire. **Correction proposée :** compléter les notes avec des conditions et limites étayées par des documents officiels datés et des références précises, ou faire acter explicitement le report de cette partie du brief. Ne pas présenter la liste de vérifications futures comme l’exécution de cette exigence. Cette relecture, soumise à l’interdiction d’accéder à un site, ne vérifie pas ces adresses.

## 2. Exactitude métier

Déroulé manuel des branches « accepté » et « refusé » de R-06, sur des numéros construits par calcul, comparé au code de `wp/plugins/imagine-pilotage/src/Entreprise/NumeroEntreprise.php:14` :

| Saisie fictive | Calcul et résultat attendu | Résultat déduit du code |
|---|---|---|
| `BE 0123.456.749` | 1 234 567 = 97 × 12 727 + 48 ; clé = 49 | Valide, `0123456749`, affichage `0123.456.749` |
| `123456749` | Neuf chiffres : ajout d’un zéro, même base et même clé | Même résultat valide |
| `1234567894` | 12 345 678 = 97 × 127 275 + 3 ; clé = 94 ; premier chiffre 1 | Valide, affichage `1234.567.894` |
| `0123456700` | Clé attendue 49, clé reçue 00 | Refus `cle_incorrecte`, numéro normalisé et affichage nuls |

Ces comparaisons sont une analyse statique, pas une nouvelle exécution PHP. Aucun défaut métier identifié sur ces cas. Le calcul reste dans la capacité d’un entier PHP, y compris sur 32 bits. Les lettres, les préfixes étrangers et les caractères de contrôle ne sont pas effacés pour fabriquer un numéro valide. L’indisponibilité de la recherche n’est pas assimilée à l’inexistence d’une entreprise. Les limites calendaires de la grille ne s’appliquent pas à ce lot.

## 3. Tests

**Relance tentée :** `python -B wp/tests/entreprise-runner/run.py run --name codex-relecture --filter NumeroEntrepriseTest`, depuis la racine. Sortie 1 : `FileNotFoundError` sur `production/C-02/tests/runner-state.json`, avant PHPUnit. Le reçu `cleanup.json` indique que le conteneur avait été supprimé. PHP et Composer ne sont pas disponibles directement, et le dossier `vendor` est absent.

**Les tests PHP n’ont donc pas été réexécutés par Codex.** La préparation du lanceur écrit des fichiers hors du rapport et télécharge des dépendances ; elle n’a pas été exécutée compte tenu des restrictions de cette relecture. Cet obstacle d’environnement n’est pas un échec d’une assertion métier.

Contrôles indépendants réalisés en lecture seule :

- Les 41 fichiers de l’inventaire courant de la bibliothèque correspondent exactement aux empreintes de `production/C-02/tests/final.json`.
- Le JUnit livré contient 41 tests Entreprise et 19 560 assertions, sans échec, erreur ou test ignoré. La suite pilotage complète annonce 169 tests et 19 860 assertions, également sans anomalie. Ce sont des preuves de l’exécution de production, pas une relance indépendante.
- Les 85 fichiers du manifeste de livraison sont présents et leurs empreintes concordent.

Les tests couvrent toutes les entrées minimales du brief, les anciens formats, Unicode et UTF-8 invalide, les motifs et l’absence de valeur exploitable après refus. L’oracle de clé utilise des divisions par soustractions successives, indépendamment du modulo de production, et confronte 194 bases aux 100 clés possibles. Les messages, la traduction injectée et l’implémentation vide sont exercés. Aucun manque de test justifiant une correction bloquante identifié. Le parcours WooCommerce → Odoo reste hors de cette preuve, comme annoncé.

## 4. Sécurité et données

Aucun secret ni donnée personnelle réelle identifié dans les fichiers du lot examinés. Les numéros de test sont calculés ; cela ne garantit pas qu’aucune combinaison ne soit attribuée, mais aucune entreprise réelle n’est prise comme fixture. Le code Entreprise ne contient ni transport réseau, ni stockage, ni journalisation de la saisie.

Les objets de résultat sont immuables et une saisie rejetée ne fournit pas de numéro normalisé. Droits WordPress, nonces, SQL, échappement HTML et paywall ne s’appliquent pas à cette bibliothèque sans point d’entrée web. La responsabilité d’échapper les messages au futur affichage est documentée.

## 5. Doctrine

PHP 8.2, types stricts et espace de noms conformes. La lecture ne révèle pas d’écart PSR-12 ; le reçu livré annonce un contrôle réussi, non rejoué ici. Les textes sont français et le résultat accepte une fonction de traduction injectée ; le catalogue et le branchement WordPress sont explicitement différés. Le README expose l’API, les limites et les commandes de test. La logique demeure indépendante de WordPress.

**C02-02 — mineur — `production/C-02/notes.md:83`.** La section « Standard d’abord » reporte la vérification de la couverture des extensions à l’intégration, sans fournir la comparaison documentaire préalable demandée par la doctrine §4. L’étude A-00 consultée ne démontre pas non plus la couverture de ce contrôle belge précis. Cela ne prouve pas qu’un composant existant soit dupliqué, mais laisse cette exigence sans preuve. **Correction proposée :** ajouter une comparaison ciblée et sourcée des fonctions des extensions retenues avec les besoins C-02, en marquant les absences de preuve comme « doute », puis préciser la justification du périmètre sur mesure.

## 6. Études (lots sans code)

Sans objet comme catégorie principale : C-02 est un lot de code. Pour son annexe documentaire, les adresses et conditions BCE/VIES restent en **doute**, explicitement annoncé par la production ; l’écart au livrable demandé est C02-01. Aucune disponibilité, gratuité ou autorisation d’accès n’est certifiée par cette relecture.

## Verdict

**À corriger.** Aucun défaut fonctionnel identifié dans le contrôle local examiné ; la documentation demandée reste incomplète et la relance indépendante des tests est empêchée par l’environnement disponible.

- **Bloquant :** aucun point identifié.
- **Important :** C02-01 — conditions d’accès et limites des sources officielles non établies.
- **Mineur :** C02-02 — comparaison préalable avec le standard non documentée.

Ce verdict n’est pas un GO.
