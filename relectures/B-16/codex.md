# Relecture indépendante Codex — B-16

Date : 28 novembre 2026. Références : `relecteurs/AGENTS.md`, doctrine, brief B-16, cahier des charges §3.3 et décision « Page article » de `docs/decisions.md:106`. Relecture du code, des tests et des preuves locales ; aucun accès à un site, à une base ou à un compte. Le rapport de Claude n'a pas été lu.

## 1. Conformité

La structure demandée est présente : titre, résumé éditorial, étiquettes, thématiques liées, signature sans lien, numéro publié lié, temps de lecture, corps C-08 puis appel conditionnel. Le résumé vient de `post_excerpt` brut ; aucun résumé automatique n'est produit. Les champs vides sont omis. Le gabarit porte une balise `article` et un seul `h1` propre à l'en-tête.

Le README explique le choix du champ de signature distinct de l'auteur technique et le traitement de l'en-tête en mode lecture : il disparaît entièrement, temps estimé compris, avec le marqueur B-03 existant. L'appel final disparaît également ; le corps et le paywall restent dans leur flux. Aucun style ajouté. Aucun remplacement des descriptions ou du balisage payant de C-08 identifié dans le raccord B-16.

Les livrables README, A-VOIR, capture et PRET sont présents. La capture locale a été examinée ; elle montre le squelette annoncé, sans validation de maquette. La conformité de l'appel final reste affectée par R1.

## 2. Exactitude métier

Cas déroulés à la lecture du code, conformément au §3.3 et à la décision précitée :

| Situation | Résultat du raccord B-16 | Appréciation |
|---|---|---|
| Anonyme, article réservé | Métadonnées publiques, extrait/bloc C-08 ; `complet=false` interdit l'appel final | Conforme |
| A-PAPIER actif, article couvert | Corps complet ; adhésion reconnue, appel final masqué | Conforme au cas nominal |
| Acheteur du numéro, sans abonnement | Corps complet ; appel final vers `Navigation::abonnementUrl()` | Conforme |
| Anonyme, article libre | Corps complet et appel final | Cohérent avec la condition « texte complet sans être abonné » ; interprétation annoncée dans A-VOIR |
| Résumé, signature et relation numéro absents | Aucun paragraphe correspondant ; C-08 conserve sa propre décision | Conforme |

**R1 — important — `wp/plugins/imagine-site/PageArticle.php:67` : la reconnaissance de l'abonné diverge des droits existants.** La requête retient uniquement le statut Memberships `active`, puis impose encore ce statut ligne 69. Un abonné en résiliation à échéance, avec adhésion `pending` liée à une souscription `pending-cancel` et une fin future, est donc déclaré non abonné. Or le raccord existant le classe explicitement `actif` jusqu'à la borne native (`Paywall.php:249`), cas documenté et testé dans `tests/C20PaywallAdapterTest.php:18`. Lorsqu'il lit un article complet, B-16 lui affiche à tort « Abonnez-vous ». Le statut `complimentary`, également reconnu actif par C-08, est lui aussi exclu. **Correction proposée :** aligner la projection d'abonnement utilisée pour l'affichage sur les états et bornes natifs déjà retenus par le raccord, sans modifier les droits C-08 ; tester B-16 avant, à et après la fin d'une résiliation à échéance, ainsi qu'une adhésion offerte reconnue active. Il s'agit d'une correction technique d'une règle déjà arrêtée, sans arbitrage métier supplémentaire.

## 3. Tests

Exécutions locales effectuées sans écriture de résultats dans le dépôt :

- `python -B production/B-16/verifier.py` : **PASS**, code de sortie 0. Ce vérificateur contrôle les empreintes et les résultats archivés : 10 contrôles natifs, 79 contrôles navigateur sur 9 réponses, rejeu enregistré de 1 211 tests et 36 700 assertions. Ce n'est pas une nouvelle exécution de ces scénarios.
- `python -B production/B-13/qualifier.py B-16` : **PASS**, 9 contre-exemples du vérificateur, code de sortie 0 ; mutations en mémoire uniquement.
- Tentative du test `PageArticleB16Test.php` par PHPUnit dans l'image locale `imagine-tests-t01:1`, avec montage en lecture seule, réseau désactivé et cache PHPUnit désactivé : **non exécuté**, WSL refuse l'accès (`Wsl/Service/E_ACCESSDENIED`, sortie 1). PHP/PHPUnit ne sont pas disponibles directement dans le PATH. Aucun contournement ni installation effectué.

Les commandes natives et navigateur, ainsi que `verifier.py --live`, n'ont pas été lancées : elles accèdent à la démo et certaines en modifient temporairement les données, ce que le rôle de relecteur interdit. Les preuves archivées annoncent une restauration ; celle-ci n'a pas été vérifiée sur une base pendant cette relecture.

Les tests purs B-16 vérifient seulement le prédicat `appel()` avec un booléen d'abonnement fourni. Les profils natifs testés ne couvrent pas la divergence R1.

**R2 — important — `wp/outils/demo/b16-browser.py:48` : le contrôle d'étanchéité perd une partie de la fin d'article.** L'en-tête est inspecté en HTML, mais l'appel final est réduit à `all_inner_texts()`. Un témoin réservé présent dans un attribut, une URL ou un commentaire de ce bloc ne serait donc pas soumis au contrôleur C-26. La mutation ligne 50 ajoute le témoin après cette extraction : elle prouve la détection dans la chaîne obtenue, sans vérifier que l'extraction conserve une fuite réelle. **Correction proposée :** contrôler le HTML complet des zones visées, attributs compris, et placer la mutation témoin dans cette entrée avant extraction, notamment dans un commentaire ou un attribut de l'appel final d'un article libre vu anonymement. Conserver les profils et la matrice bornée du brief. Ce constat porte sur la preuve, pas sur une fuite observée dans le PHP livré.

## 4. Sécurité et données

Les sorties textuelles de B-16 sont échappées, les liens passent par `esc_url`, les liens de thématique par `wp_kses_post`. La sauvegarde de signature vérifie capacité, nonce, révision et autosauvegarde, puis nettoie la saisie. Aucun accès direct au corps réservé dans `PageArticle` ; la décision et le rendu C-08 restent utilisés. Aucun secret ni donnée personnelle réelle identifié dans les éléments B-16 examinés.

La preuve d'étanchéité doit être renforcée selon R2. Aucun défaut observé ici n'accorde un droit de lecture supplémentaire.

## 5. Doctrine

Le recours aux champs et taxonomies natifs est pertinent. Le PHP du lot utilise le typage strict, l'espace de noms `Imagine`, des métadonnées préfixées et des textes d'interface traduisibles. R1 illustre toutefois le risque de réinterpréter les états métier dans une projection d'affichage distincte du raccord existant.

**R3 — mineur — `wp/plugins/imagine-site/README.md:5` : le « standard d'abord » n'est pas sourcé.** Les cinq lignes de choix sont présentes, mais cette section ne cite aucune documentation officielle pour l'extrait, les étiquettes ou l'auteur natifs, contrairement au §4 de la doctrine. **Correction proposée :** ajouter les références officielles qui justifient ces choix, notamment la lecture de l'extrait saisi sans génération et la distinction auteur du compte/signature. Aucune consultation externe effectuée dans cette relecture.

## 6. Études (lots sans code)

Sans objet : lot avec code. Le défaut documentaire applicable est relevé en R3.

## Verdict

**À corriger.** Ce verdict n'est pas un GO.

- **Bloquant :** aucun identifié.
- **Important :** R1, appel à l'abonnement affiché à des abonnés encore actifs ; R2, contrôle d'étanchéité incomplet sur le HTML de fin d'article.
- **Mineur :** R3, références officielles absentes du « standard d'abord ».

Aucune question ouverte pour Ced ou Imagine. La validation visuelle reste distincte de cette relecture technique.
