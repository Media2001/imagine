# Relecture indépendante Codex — B-04

Date : 25 novembre 2026. Références : `relecteurs/AGENTS.md`, doctrine, grille, brief B-04, cahier des charges §3.3 et §3.9, décisions du dépôt. Examen de `production/B-04`, des cinq fichiers livrés du thème, des adaptateurs appelés et des tests. Le rapport Claude n’a pas été consulté. Aucun site, compte ou base n’a été accédé ; aucune source n’a été modifiée.

## 1. Conformité

Les éléments structurels demandés sont présents : kiosque trié par date éditoriale avec pagination native, présentation publique du numéro, sommaire détaillé, article libre mis en avant, emplacement audio sans lecteur, liens conditionnels d’achat et de PDF, thématiques transversales. Le helper de statut est commun aux trois gabarits. `A-VOIR.md`, besoins du designer et `PRET` sont livrés.

Les interprétations « présentation = extrait enregistré », « titre du dossier = titre natif » et « pas de bouton sans produit public achetable » sont signalées dans le rapport de production. Les mesures archivées pour vingt articles donnent respectivement **93/32**, **183/110** et **182/113** requêtes SQL, page entière/depuis le gabarit, pour anonyme, a-carte et p-numero. Ces mesures n’ont pas été rejouées ici.

**I1 — Important — Le statut Découverte n’est jamais obtenu dans les listes.**

- **Localisation :** `wp/themes/imagine/single-imagine_numero.php:20`.
- **Problème :** le sommaire appelle `Paywall::decision()` hors lecture d’un article. Or cette méthode ne passe par C-12 que si `Decouverte::concerne()` est vrai (`wp/plugins/imagine-site/Paywall.php:84`). Ce contexte est activé uniquement pour une requête singulière d’article (`wp/plugins/imagine-site/Decouverte.php:43`). Hors de ce contexte, les droits découverte ne sont pas ajoutés et le moteur est appelé sans règle découverte. Un compte vérifié disposant d’une découverte valide voit donc « Réservé », alors que le clic ouvre effectivement l’article en découverte. La page thématique subit le même défaut via `wp/themes/imagine/inc/catalogue.php:75`. Le simple mapping des motifs découverte ne suffit pas à rendre ce statut atteignable.
- **Correction proposée :** fournir dans l’adaptateur commun une évaluation de la découverte sans consommation, fondée sur les mêmes règles et le même état que la lecture. L’utiliser pour les listes en conservant la logique métier hors du thème. Ne pas activer artificiellement le contexte de lecture, ce qui consommerait les crédits à l’affichage du sommaire. Ajouter un parcours catalogue → article pour les deux formes de découverte, avec contrôle de l’absence de consommation sur les listes.

## 2. Exactitude métier

Cas déroulés à la main dans le code, sans exécution WordPress :

| Cas | Résultat du code | Appréciation |
|---|---|---|
| Anonyme, numéro paru, article libre et article réservé, produit C-14 public disponible | Libre/Réservé ; bouton d’achat ; aucune recherche du fichier PDF | Cohérent avec le brief et §3.3/§3.9 |
| Acheteur du numéro paru, acquisition valide, PDF disponible | Articles réservés « Ouvert pour vous » ; PDF ; aucun bouton d’achat | Cohérent avec §3.9 |
| Compte vérifié sans abonnement, découverte valide, article éligible | Liste « Réservé » ; lecture effective en découverte | Écart I1 |
| Acheteur d’un numéro publié dont la date éditoriale est encore future | PDF fermé ; bouton d’achat réaffiché si produit disponible | Écart I2 |

**I2 — Important — La fermeture temporaire du PDF est assimilée à l’absence de possession.**

- **Localisation :** `wp/themes/imagine/single-imagine_numero.php:27`.
- **Problème :** `$covered` est exclusivement la décision de lecture du PDF. Pour un numéro publié avec une date éditoriale future, le moteur ferme le contenu avant d’examiner l’achat (`wp/plugins/imagine-pilotage/src/Acces/Moteur.php:67`). Ce cas est admis par la garde de publication, qui exige une date valide sans interdire une date future (`wp/plugins/imagine-site/NumeroPublication.php:36`). Un acheteur possédant déjà ce numéro reçoit donc « Acheter ce numéro », contrairement à la règle explicite du brief. À l’instant exact de sortie, cette même décision devient positive et le bouton disparaît sans changement de possession.
- **Correction proposée :** distinguer dans l’adaptateur métier la possession/couverture du numéro et l’autorisation actuelle de lire son PDF ; piloter le bouton avec la première et conserver C-11 pour le second. Tester un achat valide avant la date de sortie et à cette date : bouton absent dans les deux cas, PDF fermé puis ouvert selon C-06. Ne pas ouvrir le PDF pour résoudre le problème d’affichage.

La différence documentée entre articles accessibles et PDF antérieur fermé pour a-carte est bien identifiée par la production ; I2 porte sur un numéro effectivement acheté, sans arbitrage de cette différence de périmètre.

## 3. Tests

**Exécutés localement : 9 tests réussis, aucun échec.** Deux suites expressément reprises par `b04-regression.py` ont été lancées séparément, avec le Python QA existant et `-B` pour éviter toute écriture de bytecode :

```text
python.exe -B -m unittest discover -s wp/tests/demo -p test_b03_contract.py -v
4 tests : OK
python.exe -B -m unittest discover -s wp/tests/demo -p test_c08_scope.py -v
5 tests : OK
```

Ces tests vérifient des contrats de non-régression ; ils ne remplacent pas la recette HTTP B-04.

**Test PHP tenté, non exécuté :** aucun `php` n’est disponible dans le PATH Windows. La tentative de lancer `b04-runtime.php` via PHP sous WSL, avec seulement des substituts de traduction/enregistrement de filtre/JSON, s’est arrêtée avant PHP : `Wsl/Service/E_ACCESSDENIED`, sortie 1. Aucun succès PHP indépendant n’est revendiqué.

**HTTP non relancé :** les commandes fournies accèdent au site de démonstration, aux comptes ou à WordPress et écrivent des fichiers de preuve. `b04-work.py` téléverse également le test PHP. Cela contrevient aux droits du relecteur dans `relecteurs/AGENTS.md` (« accéder à un site, à une base ou à un compte » interdit) et à l’unique destination d’écriture autorisée. Aucun contournement n’a été tenté.

Les reçus de production annoncent 554 contrôles verts, plus 9 de préservation. Les empreintes SHA-256 des cinq sources actuelles du thème correspondent toutes à `verification-finale.json`. Il s’agit de preuves archivées examinées, pas de 554 contrôles rejoués par Codex.

Les tests HTTP suivent bien les liens d’articles et les routes PDF pour les trois visiteurs requis. Ils n’exercent toutefois aucun visiteur découverte. De plus, l’attendu du bouton reprend exactement `not expected['pdf']` (`wp/tests/demo/b04-http.py:80`) : il ne vérifie pas indépendamment la possession et laisserait passer I2. Les corrections I1/I2 doivent apporter les cas métier manquants.

**M1 — Mineur — Une preuve d’étanchéité peut réussir sans témoin privé.**

- **Localisation :** `wp/tests/demo/b04-http.py:70`.
- **Problème :** les assertions de destination et d’absence de corps utilisent `all(...)` sur les marqueurs extraits des paragraphes. Aucun contrôle n’impose que cette liste soit non vide. Si un article réservé n’a que des paragraphes courts ou tous repris dans l’extrait, les assertions réussissent même sans vérifier un seul fragment réservé, y compris pour la destination autorisée.
- **Correction proposée :** imposer un marqueur privé non vide pour chaque article témoin réservé, vérifier sa présence chez l’ayant droit et son absence chez l’anonyme et dans les listes. Faire échouer explicitement une fixture incapable de fournir ce témoin.

## 4. Sécurité et données

Aucune fuite supplémentaire démontrée dans les gabarits examinés. Ils n’impriment pas les corps d’articles, n’engendrent pas d’extraits à partir de ceux-ci et échappent les textes, attributs et liens. Le PDF n’est recherché qu’après une décision complète ; sa route est fournie par C-11. Les requêtes utilisent les API WordPress. Aucun formulaire de mutation n’est ajouté par B-04 ; aucun nonce supplémentaire n’est nécessaire sur ces liens de lecture.

Les données de démonstration examinées sont explicitement fictives. Aucun secret n’a été rencontré dans les fichiers lus. Les garanties HTTP de cache et d’étanchéité restent appuyées par les reçus archivés, avec la limite M1 sur les témoins.

## 5. Doctrine

Réutilisation de `WP_Query`, de la pagination WordPress, des produits WooCommerce, du moteur C-06 et de C-11/C-14 : conforme au principe du standard d’abord. Les fichiers livrés du thème utilisent `strict_types`, l’espace de noms `Imagine\Theme`, les préfixes et les fonctions de traduction. Les gabarits conservent les styles neutres existants ; aucune validation graphique n’est prononcée.

Les références officielles sont consignées dans `production/B-04/references.md` ; elles n’ont pas été consultées en ligne par le relecteur. I1 et I2 doivent être corrigés dans le contrat de l’adaptateur, sans créer un second calcul de droits dans le thème.

### Décisions techniques, défaut proposé

Catégorie **technique** : pour I1, retenir une évaluation de catalogue sans effet sur le quota ; pour I2, séparer possession et lecture du PDF. Défaut prudent : une erreur d’évaluation ne doit jamais ouvrir un article ou un PDF. Ces corrections ne nécessitent pas de décision visuelle ou d’accès au réel par Ced.

## 6. Études (lots sans code)

Sans objet : lot de code.

## Verdict

**À corriger.** Ce verdict n’est pas un GO.

- **Bloquant :** aucun défaut de cette gravité démontré.
- **Important :** I1 — découverte absente des statuts des listes ; I2 — rachat proposé pour un numéro déjà acquis avant sa sortie éditoriale.
- **Mineur :** M1 — assertions d’étanchéité acceptant une liste vide de marqueurs privés.
