# C-26 — À voir et à relire

**Cible unique : `imagine-test-demo`, entièrement fictive.** Extension de tests uniquement : aucun plugin, paywall, thème, réglage de découverte ni bibliothèque close modifié. Les preuves C-23 scellées ne sont pas réécrites.

## Adresses à ouvrir sur la seule démonstration

Base : `http://192.168.129.32:8085`. Ouvrir `/notre-cooperative/`, `/soutenir/`, `/proposer-un-sujet/` et `/evenements/` : pages publiques fictives, aucun texte d'article réservé ni donnée de témoin. Ouvrir `/espace-cooperateurs/` sans statut : refus ; avec P-COOP : espace autorisé. Le compte natif est `/my-account/`, et non `/mon-compte/`. Les fixtures C26 temporaires ont été retirées : les demandes/propositions témoins ne doivent pas rester visibles dans l'administration. Les 131 adresses exactes et les 35 B06 sont dans `INVENTAIRE.md`.

## Commandes de réception

Depuis `C:/Users/Ced/imagine`, bash Windows, sans `TMPDIR` nécessaire :

```bash
env -u TMPDIR PYTHONIOENCODING=utf-8 python -B wp/tests/demo/c26-tests.py
env -u TMPDIR PYTHONIOENCODING=cp1252 PYTHONUTF8=0 python -B wp/tests/demo/c26-tests.py
PYTHONIOENCODING=utf-8 python -B wp/tests/demo/c26-verifier.py
PYTHONIOENCODING=utf-8 python -B wp/tests/demo/c26-paquet-tests.py
```

Rejeu réel, avec **un nom de reçu neuf** :

```bash
PYTHONIOENCODING=utf-8 python -B wp/outils/demo/c26-preparer.py --label livraison-nouvelle
PYTHONIOENCODING=utf-8 python -B wp/outils/demo/c26-preparer.py --label mutations-nouvelles --mutations
```

Le lanceur garde la cible, photographie durablement l'état dans le scratch privé Hermes **avant toute fixture ou session**, prépare les données fictives puis les sessions natives et lance `c26.py <label>` avec le contexte secret en mémoire sur stdin. `c26.py` réemploie **la commande GET C-23 inchangée**, puis son catalogue supplémentaire. Il ne crée aucune session et ne fait aucun POST, export HTTP, envoi ou appel extérieur. Les exports privacy passent séparément par les callbacks natifs enregistrés, en lecture seule et pour des emails `@example.org` seulement ; aucune demande privacy/email n'est créée.

## Gates du paquet courant

- `livraison-finale-c23.json` : **1 922 contrôles verts**, 136 voies × 14 publics plus identités/inverses, les cinq pages B06 comprises.
- `livraison-finale.json` et `.md` : **1 965 contrôles verts**, 131 voies nouvelles ou communes réinspectées × 15 publics. L'abonné actif est aussi un tiers pour les données du propriétaire témoin.
- `livraison-finale-privacy.json` : **64 contrôles verts**, quatre callbacks × (15 tiers + le propriétaire positif). Les données privées existent vraiment et sortent pour leur propriétaire, jamais pour les tiers.
- `mutations-livraison-mutation-*.json` : **six familles rouges détectées**, puis restauration. Le même passage complet est ensuite vert ; le rejeu normal `livraison-finale` a encore été fait après sa restauration.
- `tests.json`, `tests-{utf8,cp1252}.log` : **42 tests**, dont les 31 tests C23, dans chaque encodage ; Python réel **3.11.15**, `TMPDIR` absent, réseau interdit dans la suite.
- `image.json`, `image.log` : `wp/tests/preparer-image.ps1` exécuté après les nouveaux tests, code **0**, `T01 IMAGE READY`.
- `manifest.json` : sources C26, correctif C23 autorisé et seuls documents/reçus C26 courants. **`verification-finale.json` : 46/46 contrôles, code 0.** Le vérificateur recalcule les totaux, cases, inverses, SHA, restaurations et résultats de mutation ; JSON stdout seulement. **`qualification-finale.json` : aucune écriture dans production, réseau bloqué, 9/9 falsifications refusées**, dont huit reçus rescellés avant contrôle (la neuvième altère la source déclarée). `c26-paquet-tests.py` exerce réellement ces garde-fous sur des copies scratch. La préparation d'image autorisée est distincte de ces commandes offline et peut consulter les seules dépendances publiques dans Docker.

Inventaire **une ligne par sortie** : `INVENTAIRE.md`. Catalogue machine et toutes les observations élémentaires : `livraison-finale.json`, `livraison-finale-inventaire.json`, `livraison-finale-privacy.json`. Aucun total de cas synthétiques n'est crédité comme parcours réel.

## Mutations : ce qui est réellement joué

| Famille | Mutation et chemin réel | Preuve |
|---|---|---|
| Agenda B07 | Mauvais titulaire transmis au **callback d'export natif enregistré**, qui lit la vraie inscription privée créée par `Agenda::inscrire()` | `mutations-livraison-mutation-agenda.json` : les 15 tiers rougissent |
| Personnalisation C24 | Même faute de raccord, vrai callback, vraie réponse persistée par `Personnalisation::enregistrer()` ; date ISO distinctive de fixture | `mutations-livraison-mutation-personnalisation.json` |
| Rétractation C25 | Même faute de raccord, vrai callback, vraie demande/note/journal sur commande fictive temporaire créée par Woo ; aucun remboursement ni annulation | `mutations-livraison-mutation-retractation.json` |
| Sujet B08 | Même faute de raccord, vrai callback, proposition privée créée par `Sujet::enregistrer()` | `mutations-livraison-mutation-sujet.json` |
| Pages publiques / Soutenir B08 | Texte témoin réservé temporairement persisté dans le contenu de Soutenir ; véritable GET anonyme rouge, puis ligne exacte restaurée | `mutations-livraison-mutation-cooperative.json` |
| Pages coopérateurs B06 | Statut coopérateur temporairement persisté pour `V-INSCRIT` ; vrai GET de la page B06 laissant passer son témoin, attendu rouge pour ce public, puis métadonnée exacte restaurée | `mutations-livraison-mutation-cooperateurs.json` |

Les quatre premières sont **des mutations du raccord de sélection du titulaire dans la fixture applicative**, pas des modifications des callbacks métier et pas des falsifications de leur résultat. Les deux dernières traversent HTTP sur une fixture persistée. Aucun corps HTTP ni tableau retourné n'est réécrit en mémoire pour ces six preuves. Les anciennes 35 mutations B06 de corps en mémoire restent des tests de détecteur, **pas 35 parcours applicatifs mutés**.

## B06 : périmètre à relire comme code neuf

Cette extension est restée en place dans C23 mais n'a pas encore ses deux relectures. C26 la soumet explicitement, sans la déclarer close de lui-même :

- `wp/outils/demo/c23.py` : **`cooperator_routes()` (139–161), `assess_cooperator()` (164–193)** ; intégration dans `build_routes()` et `matrix()` (publics autorisés, témoins B06 ajoutés aux interdits, contrôles inverses). Cinq pages × HTML, REST unitaire, alias, collection, oEmbed, embed et recherche.
- `wp/outils/demo/c23-inventaire.php` : **bloc `$out['cooperator_pages']` (74–83)**, inventaire des cinq vrais IDs ; **bloc `$out['cooperator_publics']` (84–91)**, décision native. Les pages sont 2867 Espace coopérateurs, 2868 Appels à bénévolat, 2869 Lettre de missions, 2870 Cadastre des compétences, 2871 Relais des événements.
- `wp/outils/demo/c23-preparer.py` : **`cooperator_snapshot()` (125–127), `seed_cooperator_witness()` (130–135), `restore_cooperator()` (138–143)** ; `private_snapshot()` et ordre dans `run()` (146–237). Cinq corps initialement vides exigés ; pose CAS des témoins ; restauration qui refuse une dérive concurrente.
- `wp/tests/demo/c23-tests.py` : **`CooperatorsTest` (195–270), `PreparationSafetyTest` (272–315), `LiveMutationHarnessTest` (317–332)**. Le seul changement C26 dans ce fichier est **`test_scratch()`** et ses deux appels : plus d'accès obligatoire à `os.environ['TMPDIR']`, plus de repli implicite vers le temporaire système.
- `wp/tests/demo/c23-mutations.py` : **`inject()` (22–33), `run()` (36–87)** : recette historique de mutations **en mémoire**, explicitement limitée à cette portée. `wp/tests/demo/c23-verifier.py` : `matrix_checks()` et inverses B06, à lire avec ces tests, sans réécrire les reçus historiques.
- Extension nouvelle : `wp/outils/demo/c26.py`, `wp/outils/demo/c26-preparer.py`, `wp/tests/demo/c26-fixture.php`, `wp/tests/demo/c26-tests.py`, `wp/tests/demo/c26-verifier.py`, `wp/tests/demo/c26-paquet-tests.py`.

Les oEmbed coopérateurs autorisés prouvent l'objet riche et le bon titre ; les six autres sorties prouvent aussi la présence du témoin. Un flux `post_type=page` ne vaut pas preuve des pages B06 ; aucun faux flux B06 n'est ajouté.

## Restauration et limites

`livraison-finale-restauration.json` et `mutations-livraison-restauration.json` : utilisateurs, **toutes les métadonnées utilisateur**, pages/contenus/métadonnées, commentaires/notes, commandes Woo, adresses/opérations/lignes de commandes, navigation, options métier et calendrier relus et identiques. Les empreintes métier avant/après sont identiques ; les actions planifiées métier restent identiques. Les fixtures privées et commandes temporaires sont supprimées, les cinq pages B06 remises vides. Les sources live, bootstrap actuel compris, sont identiques à leur état avant essai.

La découverte livrée reste **fermée, sans numéro**. `V-DEC-FIN` est contrôlé sans droit ; aucun cas épuisé ouvert n'est prétendu rejoué par C26. La recette C23 séparée reste historique. Les exceptions de l'arbitrage métier restent celles prévues : caches, sessions recréables et verrous du planificateur ne sont pas des règles métier ; C26 prouve en plus l'égalité exacte des lignes utilisateur capturées. Les compteurs auto-incrément ne sont pas un état métier.

Les URL de flux demandant les types privés sont réellement interrogées et inspectées ; WordPress les projette ici sur des articles publics : **ce n'est pas un flux privé non vide**. L'existence des données privées est prouvée par les callbacks natifs positifs, pas inventée depuis ce repli. Les droits C14 du numéro effectivement acheté sont respectés ; un texte légitimement lu n'est pas classé fuite. Les plans de site restent fermés comme dans C23 ; ni cache d'hébergement partagé ni vrais robots vérifiés ne sont prouvés.

Les diagnostics rouges conservés sont des **erreurs du nouveau test**, corrigées et couvertes : chemin compte natif `/my-account/` au lieu d'un chemin présumé, apostrophe typographique dans un titre, droit C14 sur un repli de flux et réflexion native d'une date dans le titre du lien RSS. Ils ne sont pas présentés comme fuites du site ni comme reçus finaux. Aucun rapport parent, verrou, file, autre site ou autre lot de production n'a été touché.
