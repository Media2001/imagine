# Relecture indépendante Codex — A-30

Date : 27 novembre 2026. Périmètre : brief A-30, `production/A-30/`, outil et tests A-30 dans `wp/`, dépendances A-13/A-22 et lecteurs réemployés. Doctrine, décisions et cahier des charges §2.3, §3.7, §3.13 et §4.3 lus. Le rapport Claude n’a pas été consulté. Aucun code ni paquet de preuves modifié.

## 1. Conformité

Le périmètre fonctionnel est respecté : simulation sans création de compte, abonnement, mot de passe, invitation ou transmission Odoo ; correspondance fictive des types ; réemploi direct du lecteur A-13 ; sorties limitées aux nombres et numéros de ligne. Les deux lignes destinées au mode d’emploi de l’audit sont présentes et contrôlées par le vérificateur.

Les choix sont explicités dans le README : priorité du refus A-13, puis absence d’email, puis type inconnu, puis rapprochement ; comptage des lignes et non des comptes ; refus d’un rapprochement ambigu. Sur copie neutralisée, les deux issues de compte deviennent inconnues et les lignes concernées sont conservées séparément. Cette adaptation annoncée concilie la liste des cinq issues avec l’interdiction de présenter un rapprochement inconnu comme zéro.

Les trois options métier réservées restent désactivées et leur activation est refusée. Le lot ne prétend donc pas implémenter une politique d’import des échus, de résolution des doublons ou de calcul d’échéance.

## 2. Exactitude métier

Déroulement manuel confronté au code et aux résultats conservés du banc :

- **Abonné sans email (§3.13 et §4.3)** : une ligne admissible A-13 sans adresse aboutit à `sans_email`, sans recherche de compte ni adresse inventée. Dans la fixture étendue, ce sont les lignes 12 à 16, correctement présentes dans les résultats classique et HPOS.
- **Abonné déjà connu (§3.7 et §4.3)** : pour une adresse unique existante et un produit reconnu, l’issue est `compte_existant`. Les lignes 7 à 11 du banc correspondent à ce cas. Après neutralisation, ces lignes rejoignent les lignes 2 à 6 dans `rapprochement_inconnu` ; elles ne deviennent pas des comptes à créer.
- **Type hors table** : les lignes 17 à 21 sont `type_a_decider`, sans produit deviné. Les lignes 22 à 26 restent refusées par A-13, même si leur produit est connu.

Contrôles complémentaires exécutés en mémoire, sans fichier de résultat : échéance égale au 25 novembre acceptée par A-13 ; échéance au 24 novembre refusée ; 1er janvier 2027 accepté au 31 décembre 2026 ; 31 décembre 2026 refusé au 1er janvier 2027. Aucun calcul de prochaine échéance ajouté. Les seuils d’agrégation 0/4/5 donnent les résultats attendus. Le rejeu identique et le refus d’écraser des sorties existantes figurent dans les preuves natives vérifiées.

## 3. Tests

**A30-C01 — important — dépendance non déclarée à `TMPDIR`.**

- **Localisation :** `wp/tests/a30/test_core.py:32`, `dir=os.environ['TMPDIR']`.
- **Problème :** les tests exigent une variable absente de cette session Windows, alors que `TEMP` et `TMP` sont définies. La même dépendance est utilisée par les autres classes créant un répertoire temporaire. Ni la commande documentée ni la matrice ne l’initialise. La suite annoncée rejouable sous Windows dépend ainsi d’un environnement préparé implicitement.
- **Reproduction :** `C:/Python314/python.exe -B -m unittest discover -s wp/tests/a30 -p 'test_*.py' -q`, avec `PYTHONIOENCODING=utf-8` et `PYTHONUTF8=1`, puis avec `PYTHONIOENCODING=cp1252` et `PYTHONUTF8=0` : **25 tests, 22 erreurs `KeyError: 'TMPDIR'` dans chaque contexte**. Les trois tests sans cette dépendance passent.
- **Correction proposée :** conserver la possibilité d’imposer un répertoire extérieur au dépôt, mais prévoir le répertoire temporaire standard de Python lorsque `TMPDIR` est absente, ou initialiser explicitement ce prérequis dans un lanceur commun documenté. Ajouter un rejeu avec `TMPDIR` absente, `TEMP`/`TMP` définies, dans les deux encodages. Le répertoire choisi doit rester hors dépôt pour le test de publication.

Résultats et limites de cette relecture :

| Vérification | Résultat |
|---|---|
| `C:/Python314/python.exe -B production/A-30/verify.py`, sans argument | Code 0, `package: PASS`, `native_packet: PASS` |
| `C:/Python314/python.exe -B wp/tests/a30/verify.py`, sans argument | Code 0, tous les contrôles PASS |
| Suite Python indépendante UTF-8 / cp1252, sans `TMPDIR` | Échec reproductible décrit dans A30-C01 |
| Première tentative UTF-8 avec `TMPDIR=TEMP` | Refus d’accès Windows aux répertoires temporaires ; rejeu non validé dans ce contexte restreint |
| Contrôles complémentaires en mémoire | Fixture propre : 30 lignes admissibles ; quatre bornes de date ; seuils 0/4/5 ; refus IBAN : PASS |

Le paquet scellé correspond aux sources actuelles et conserve les résultats de 25 tests Python par encodage, sept contrôles PHP purs et 122 contrôles natifs par contexte, avec classique et HPOS. Les vérificateurs contrôlent notamment les empreintes de base et de fichiers, les canaris, les issues exactes et la neutralisation. **Cela constitue une vérification des preuves livrées, pas un nouveau rejeu natif indépendant.** Le banc Docker, le style et la commande opérateur Linux n’ont pas été réexécutés pendant cette relecture. Les refus d’accès temporaires de la première tentative sont une limite d’environnement, distincte du défaut reproductible A30-C01.

## 4. Sécurité et données

Aucune donnée réelle ni secret repéré dans le périmètre examiné. Les données d’essai sont fictives. Les adresses passent en mémoire/stdin ; les sorties finales sont reconstruites suivant un schéma fermé. Les recherches de comptes utilisent des requêtes préparées et refusent deux comptes pour une adresse.

Le lancement réemploie le gardien commun, le confinement et la base en lecture seule. La liaison du succès au condensat du résultat et la validation après terminaison couvrent les modifications tardives examinées. Les sorties adjacentes au CSV refusent le dépôt et l’écrasement. La liste privée de numéros de ligne est explicitement distinguée du résumé agrégé. Aucun accès à un site, compte ou service réel effectué ; aucune voie de paywall ajoutée par ce lot.

## 5. Doctrine

Logique de classement isolée dans `Analysis.php`, branchement natif limité, PHP strict et espaces de noms conformes. Le contrôle PSR-12 livré est vérifié avec zéro erreur et zéro avertissement. Le réemploi d’A-13 et d’A-22 évite une seconde implémentation du contrôle ou du gardien.

Le défaut A30-C01 empêche de considérer la rejouabilité Windows comme acquise sans prérequis supplémentaire. Il est technique et ne demande aucun arbitrage métier ni intervention sur le réel.

### Décisions techniques, défaut proposé

Pour A30-C01, défaut proposé : utiliser le mécanisme temporaire standard de Python en l’absence de surcharge explicite, tout en conservant l’exclusion du dépôt. Hermès peut appliquer cette correction sans attendre Ced.

## 6. Études (lots sans code)

Sans objet : lot avec code. Les cinq lignes « standard d’abord » et les deux liens officiels WooCommerce sont présents. Leur contenu distant n’a pas été vérifié pendant cette relecture, conformément à l’interdiction d’accéder à un site ; les affirmations documentaires externes restent donc non vérifiées ici.

## Verdict

**À corriger.**

- **Bloquant :** aucun défaut bloquant établi.
- **Important :** A30-C01 — rendre la suite Windows rejouable sans variable `TMPDIR` implicite, puis produire le rejeu UTF-8/cp1252 correspondant.
- **Mineur :** aucun point supplémentaire retenu.

Le classement métier et les protections examinées ne présentent pas d’autre défaut établi. Les limites du rejeu indépendant sont détaillées en section 3. Ce verdict n’est pas un GO d’import, d’accès au réel ou de déploiement.
