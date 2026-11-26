# B-06 — Relecture indépendante Codex

Date : 26 novembre 2026. Périmètre : brief B-06, cahier des charges §3.9, §3.12 et §4.2, production V2 et raccords dans `wp/`. Rapport Claude non consulté. Aucun accès au site, à une base ou à un compte ; aucun autre fichier modifié.

## 1. Conformité

L’essentiel du brief est présent : attribut distinct des abonnements, source et date, fiche native avec nonce, journal, compte WooCommerce, cinq pages et intitulés attendus, export/effacement, accroche sans écouteur. Le choix administratif fermé est explicite. L’exception de conservation de l’attribut P-COOP et la restauration des autres profils sont documentées dans `production/B-06/A-VOIR.md` ; leur état actuel n’a pas été vérifié sur le site.

- **C1 — Important — `wp/plugins/imagine-site/CooperateursRegles.php:12`.** Le rôle `administrator` est codé en dur ; la lecture sans statut réutilise ce même choix. Les deux règles restent pourtant ouvertes dans A-VOIR. Cela ne respecte pas la doctrine §4 : une règle métier ouverte doit devenir un réglage modifiable dans l’administration, avec défaut prudent et valeurs testées. **Correction proposée :** exposer séparément les rôles autorisés à modifier l’attribut et ceux autorisés à lire sans statut, conserver Administrateur seul dans les deux défauts, contrôler leur modification et tester chaque configuration sans accorder de droit d’article.

### Pour Imagine

- **Métier —** Garder Administrateur comme seul rôle pouvant poser/retirer l’attribut : oui/non ? **Défaut prudent : oui**, à porter dans le réglage correspondant.
- **Métier —** Garder Administrateur comme seul rôle pouvant lire sans statut coopérateur : oui/non ? **Défaut prudent : oui**, dans un réglage distinct. Les autres rôles restent refusés sans statut.

Ces réponses ne sont pas nécessaires pour appliquer les défauts et terminer la correction.

## 2. Exactitude métier

Cas déroulés par lecture du code, sans exécution WordPress :

1. **Coopérateur connecté, non abonné (§3.9)** : avec booléen vrai, source administration et date au format attendu, `lecture()` ouvre l’espace. Aucun raccord B06 ne fournit de droit à `Paywall` ; le statut seul n’ouvre donc pas les articles. Le reçu HTTP comporte aussi un témoin positif pour l’abonné et un extrait pour P-COOP.
2. **Abonné actif non coopérateur (§3.9 et §3.12)** : le rôle subscriber et l’absence d’attribut ferment l’espace ; les réponses de contenu et REST sont refusées, les collections sont filtrées. L’abonnement n’intervient pas dans cette décision.
3. **Retrait puis sauvegarde identique** : le retrait écrit un état faux et un événement ; l’accès se ferme. La sauvegarde suivante quitte avant écriture et ne redouble pas le journal. Pas de date d’expiration ni de calendrier de numéros propre à cet attribut.

## 3. Tests

- **Exécuté, réussi :** partie strictement locale du vérificateur fourni (`wp/tests/demo/b06-verifier.py:11`, jusqu’avant l’appel à `b06.guard()`). Exécution en mémoire sous `python -B`, sans importer le lanceur distant ni écrire de reçu. Les assertions d’intégrité des 11 sources, de cohérence des reçus, du bootstrap, de qualité et de régression passent.
- **Tenté, non exécuté :** `b06-rules.php`, via l’image existante `imagine-tests-t01:1`, réseau désactivé et dépôt monté en lecture seule. WSL refuse le lancement : `Wsl/Service/E_ACCESSDENIED`, code 1. Aucun PHP natif trouvé dans le PATH.
- **Non rejoués :** recette native/HTTP et vérificateur complet, qui accèdent au site et, pour la recette, modifient ses données. `relecteurs/AGENTS.md` interdit ces accès au relecteur.

Les **165 contrôles, 11 mutations, 1 123 tests de régression et 34 569 assertions** sont donc des résultats consignés par la production, dont la cohérence locale a été vérifiée, pas des tests fonctionnels indépendamment rejoués. La couverture inclut nonce, retrait, absence de doublon, échec d’écriture du journal et témoins positifs des surfaces. Il manque notamment l’échec de **lecture** du journal décrit en S1 et les configurations demandées en C1.

## 4. Sécurité et données

Les contrôles de rôle, droit natif d’édition et nonce lié au titulaire sont présents. Sorties échappées, requêtes paramétrées pour les valeurs variables, objets clonés avant filtrage, et aucun transport CoopHub ajouté. Les cinq voies demandées disposent de protections et de preuves enregistrées ; leur comportement réel n’est pas certifié par cette relecture locale.

- **S1 — Important — `wp/plugins/imagine-site/Cooperateurs.php:157`.** `audits()` ne vérifie pas l’échec du SELECT ni `$wpdb->last_error` et peut retourner un tableau vide après une erreur SQL. Si cette lecture échoue pendant l’export, l’historique est omis avec `done=true`. Pendant l’effacement, l’attribut peut être supprimé mais les événements conservés, puis l’opération déclarée terminée sans données retenues si les lectures du journal échouent. **Correction proposée :** distinguer explicitement journal vide et lecture impossible ; propager un échec contrôlé à l’exporteur et signaler l’effacement incomplet. Ajouter une injection d’échec du SELECT avec événements existants, vérifier qu’aucun succès complet n’est annoncé, puis vérifier la reprise.

## 5. Doctrine

Le choix documenté réutilise les fiches, métadonnées, pages et outils de confidentialité WordPress, sans créer d’adhésion Memberships ni modifier C06/C21. Règles pures séparées, namespace Imagine, typage strict et textes traduisibles présents. L’écart de réglages est décrit en C1. Aucun style ajouté dans le lot.

## 6. Études (lots sans code)

Sans objet : lot avec code. La note « standard d’abord » contient les dix lignes et des liens officiels ; ces pages externes n’ont pas été consultées dans ce rôle.

## Verdict

**À corriger.**

- **Bloquant :** aucun établi par cette relecture.
- **Important :** C1 — règles ouvertes non réglables ; S1 — erreur de lecture du journal assimilée à une absence d’historique.
- **Mineur :** aucun retenu.

Les tests fonctionnels restent à rejouer après correction dans un environnement autorisé. Ce verdict n’est pas un GO.
