# Relecture indépendante Codex — C-08

Date : 23 novembre 2026. Périmètre : `briefs/C-08-paywall-sur-article.md`, `production/C-08/`, adaptateur, branchement du thème, fixtures et tests associés dans `wp/`. Références : doctrine, décisions, cahier des charges §3.8, §3.9, §4.4 et chapitre 5, cas R-25 à R-31. Le rapport de Claude n'a pas été consulté. Aucun accès au site, à une base ou à un compte ; aucune modification de la production.

## 1. Conformité

L'adaptateur appelle bien le moteur C-06 et le vérificateur C-03. Le thème dispose du point de sortie et des quatre gabarits demandés. Les gardes couvrent contenu, REST, flux, extraits et partage ; les en-têtes interdisent le stockage partagé. `A-VOIR.md` et `PRET` sont présents. Les limites concernant PDF, découverte complète, cycle des impayés et robots Internet sont explicitement déclarées ; elles ne sont pas assimilées ici à des preuves obtenues.

**C08-03 — Mineur — Type de balisage différent de celui demandé.**

- **Localisation :** `wp/plugins/imagine-site/Paywall.php:235`.
- **Problème :** le JSON-LD utilise `@type: Article`, alors que le §3.9 demande expressément `NewsArticle` (`docs/cahier-des-charges-v3.1.txt:831`). Ce choix différent n'est pas signalé. `isAccessibleForFree`, `hasPart` et le sélecteur sont présents ; il s'agit d'un écart au contrat, pas d'une affirmation d'invalidité générale du type `Article`.
- **Correction proposée :** employer le type demandé et ajouter son contrôle à la recette de partage, qui ne vérifie actuellement pas ce champ.

## 2. Exactitude métier

Cas déroulés à la lecture de l'adaptateur et du moteur, sans exécution WordPress :

| Cas | Chemin et résultat constatés | Attendu |
|---|---|---|
| R-26, anonyme sur un article réservé déjà paru | Aucun droit ; robot non vérifié ; décision `complet=false`, bloc `connexion` ; extrait puis liens de connexion et d'abonnement | Conforme au brief |
| R-25, adhésion active et abonnement actif, dates 2026–2030 des fixtures | Intersection des dates natives ; droit `abonnement/actif` ; texte complet sans bloc | Conforme pour l'article |
| §3.8, adhésion `paused`, abonnement `on-hold`, fenêtre de grâce couvrant l'instant | Droit `grace` ; texte complet et bandeau `regularisation` | Conforme à la situation de démonstration demandée |
| Fin exacte de la grâce | La condition `now < graceEnd` devient fausse ; état suspendu, extrait et régularisation | Fermeture effective à la borne |
| Fin exacte du droit natif actif | Le moteur refuse dès `instant >= fin` | Fermeture effective à la borne |
| Numéro absent ou date éditoriale invalide | Exception capturée ; extrait | Conforme à la fermeture par défaut |

Le changement d'année ne déclenche pas de calcul particulier dans cet adaptateur : les comparaisons portent sur des dates complètes. Le rejeu des fixtures dispose d'une preuve archivée, non rejouée ici. Les parcours complets R-29/R-30 et le véritable robot de R-27 ne sont pas présentés comme validés.

**C08-01 — Important — Un article explicitement ouvert par le champ booléen natif est refermé.**

- **Localisation :** `wp/plugins/imagine-site/Paywall.php:31`.
- **Problème :** seules les chaînes `'0'` et `'1'` sont acceptées. Or `imagine_reserve` est déclaré comme métadonnée REST de type `boolean`. Une écriture native de `false` peut être stockée puis relue comme chaîne vide, représentation normale d'un booléen faux dans les métadonnées WordPress. L'adaptateur la traite comme une panne et renvoie `adaptateur_indisponible`, même avec un numéro valide déjà paru. Le contrôle positif existant utilise la chaîne `'0'` injectée par le seed B-00 et ne couvre donc pas cette écriture native. Constat par analyse du contrat de données ; reproduction WordPress non exécutée dans cette relecture.
- **Correction proposée :** distinguer explicitement l'absence de métadonnée d'une valeur fausse enregistrée, normaliser les représentations natives valides et continuer à fermer les valeurs absentes ou invalides. Ajouter un test passant par l'écriture REST de `false`, puis vérifier la lecture complète anonyme ; conserver les tests de fermeture lorsque la clé manque.

## 3. Tests

Exécutions locales, sans installation de dépendance ni écriture de cache Python :

| Commande | Résultat |
|---|---|
| `python -B -m unittest discover -s wp/tests/demo -p test_c08_scope.py -v` | 5 tests réussis |
| `python -B -m unittest discover -s wp/tests/demo -p 'test_b0*.py' -v` | 7 tests réussis, 1 erreur d'import : `ModuleNotFoundError: No module named 'bs4'` |

Deux contrôles supplémentaires exécutés en mémoire réussissent : correspondance des **16 empreintes source** de `verification-finale.json` avec les fichiers présents, et absence des **deux phrases témoins dans les 20 réponses anonymes archivées**. Ces contrôles vérifient les pièces livrées, pas le fonctionnement actuel du site.

Les recettes HTTP, runtime WordPress, pannes et idempotence n'ont pas été exécutées : elles accèdent au site ou à la base et plusieurs réécrivent des preuves ou des fixtures, contrairement aux droits de `relecteurs/AGENTS.md` et à la restriction d'écriture de cette demande. Aucun exécutable `php` n'est disponible dans le PATH. Les **425 contrôles annoncés** restent donc des résultats de livraison, non un résultat indépendant reproduit intégralement.

Les tests fournis ne se limitent pas au nominal : configuration invalide, exception, numéro invalide, `on-hold` sans grâce, faux robots, requêtes conditionnelles et retour anonyme après abonné sont couverts. En revanche, les bornes temporelles natives de l'adaptateur et l'écriture booléenne de C08-01 ne sont pas exercées par la recette runtime.

**C08-02 — Important — Dépendance manquante pour rejouer la non-régression livrée.**

- **Localisation :** `wp/tests/demo/c08-regression.py:12`.
- **Problème :** l'import de `b01_html` dépend de `bs4`, absent de l'environnement et des roues fournies dans `production/B-01/validation/`. Le test local de ce validateur échoue à l'import ; le même import empêche la recette C-08 de démarrer. Les commandes de rejeu C-08 ne précisent pas cette préparation. L'erreur constatée ne démontre pas un défaut du rendu HTML, mais empêche de reproduire la preuve avec les prérequis livrés.
- **Correction proposée :** déclarer les dépendances complètes et leurs versions, fournir une procédure de préparation isolée compatible avec les contraintes du projet, puis rejouer les 13 tests locaux et la non-régression. Aucune installation n'a été tentée par le relecteur.

## 4. Sécurité et données

Aucune fuite du corps réservé établie dans les fichiers examinés ou les réponses anonymes archivées. La fermeture sur exception, la suppression des champs REST brut/mot de passe, les clones évitant de contaminer le cache objet, l'ignorance des IP de proxy et les en-têtes privés sont des protections effectives à la lecture du code. Les sorties ajoutées sont échappées ; le JSON-LD n'inclut pas le corps.

Les fixtures utilisent des identités fictives en `@example.org` ; les documents indiquent seulement le chemin des identifiants hors dépôt. Aucun fichier d'identifiants privé n'a été ouvert. Cette inspection et les captures historiques ne constituent pas une certification exhaustive des voies de sortie sur une installation en fonctionnement.

## 5. Doctrine

La logique de décision reste dans les bibliothèques et le branchement utilise les objets Memberships/Subscriptions. Les sources officielles et des extraits sont consignés dans les livrables ; aucun site documentaire n'a été consulté pendant cette relecture. Les fichiers examinés utilisent les espaces de noms Imagine, le typage strict et des textes d'interface traduisibles. Les choix prudents propres à la démonstration sont documentés. Le point C08-02 reste à résoudre pour satisfaire la preuve rejouable.

## 6. Études (lots sans code)

Sans objet : lot de code et de branchement WordPress.

## Verdict

**À corriger.** Ce verdict n'est pas un GO.

- **Bloquant :** aucun défaut classé bloquant établi dans le périmètre vérifié.
- **Important :** C08-01 — ouverture booléenne native mal interprétée ; C08-02 — dépendance manquante pour le rejeu de la non-régression.
- **Mineur :** C08-03 — type JSON-LD différent du cahier des charges.
