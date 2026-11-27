# C-26 — À voir et à relire

**Cible unique : `imagine-test-demo`, entièrement fictive.** Les dix instructions du 27 novembre sont appliquées après B-08 corrigé. Aucun changement durable du plugin, paywall, thème, réglage de découverte ni bibliothèque close. Deux sources de test C23 sont adaptées minimalement, pas ses preuves historiques. PRET n'est ni clôture Claude ni validation visuelle Ced.

## Adresses à ouvrir sur la seule démonstration

Base : `http://192.168.129.32:8085`. Ouvrir `/notre-cooperative/`, `/soutenir/`, `/proposer-un-sujet/` et `/evenements/` : pages publiques fictives, aucun texte d'article réservé ni donnée de témoin. L'archive exige titre Agenda, deux groupes natifs, chaque ID et lien événement inventorié. Ouvrir `/espace-cooperateurs/` sans statut : refus ; avec P-COOP : espace autorisé. Le compte natif est `/my-account/`. Les fixtures C26 temporaires ont été retirées : les demandes/propositions témoins ne doivent pas rester visibles dans l'administration. Les 132 adresses exactes et les 35 B06 sont dans `INVENTAIRE.md`.

## Commandes de réception

Depuis `C:/Users/Ced/imagine`, bash Windows. Interpréteur exact vérifié : **Python 3.11.15**. `py -3.11` n'est pas enregistré sur ce poste. Commandes sans argument applicatif, sans `TMPDIR` nécessaire :

```bash
env -u TMPDIR PYTHONIOENCODING=utf-8 'C:/Users/Ced/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe' -B wp/tests/demo/c26-tests.py
env -u TMPDIR PYTHONIOENCODING=cp1252 PYTHONUTF8=0 'C:/Users/Ced/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe' -B wp/tests/demo/c26-tests.py
env -u TMPDIR PYTHONIOENCODING=utf-8 'C:/Users/Ced/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe' -B wp/tests/demo/c26-verifier.py
env -u TMPDIR PYTHONIOENCODING=utf-8 'C:/Users/Ced/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe' -B wp/tests/demo/c26-paquet-tests.py
```

Rejeu réel, avec **un nom de reçu neuf** :

```bash
TMPDIR='C:/Users/Ced/AppData/Local/hermes/cache/scratch' PYTHONIOENCODING=utf-8 'C:/Users/Ced/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe' -B wp/outils/demo/c26-preparer.py --label livraison-nouvelle
TMPDIR='C:/Users/Ced/AppData/Local/hermes/cache/scratch' PYTHONIOENCODING=utf-8 'C:/Users/Ced/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe' -B wp/outils/demo/c26-preparer.py --label mutations-nouvelles --mutations
```

Le lanceur garde la cible, photographie durablement l'état dans le scratch privé Hermes **avant toute fixture ou session**, prépare les données fictives puis les sessions natives et lance `c26.py <label>` avec le contexte secret en mémoire sur stdin. `c26.py` réemploie la commande GET C-23 (extraction minimale de l'oracle historique dans `reserved_witnesses()`), puis son catalogue supplémentaire. Il ne crée aucune session et ne fait aucun POST, export HTTP, envoi ou appel extérieur. Les exports privacy passent séparément par les callbacks natifs enregistrés, en lecture seule et pour des emails `@example.org` seulement ; aucune demande privacy/email n'est créée.

## Gates du paquet courant

- `correction-livraison-V2-c23.json` : **1 922 contrôles verts**, 136 voies × 14 publics plus **18 identités/inverses/faux Bing**, les cinq pages B06 comprises.
- `correction-livraison-V2.json` et `.md` : **1 980 contrôles verts**, 132 voies nouvelles ou communes réinspectées × 15 publics. L'abonné actif est aussi un tiers pour les données du propriétaire témoin.
- `correction-livraison-V2-privacy.json` : **64 contrôles verts**, quatre callbacks × (15 tiers + le propriétaire positif). Les données privées existent vraiment et sortent pour leur propriétaire, jamais pour les tiers. Total : **3 966 contrôles par passage**.
- `correction-mutations-V2-mutation-*.json` : **huit familles rouges détectées**, puis restauration. Même passage complet ensuite vert ; rejeu normal `correction-livraison-V2` exécuté après restauration. Anciens labels historiques seulement, non rescellés.
- `tests.json`, `tests-{utf8,cp1252}.log` : **52 tests** (42 antérieurs conservés + 10 régressions), dont les 31 tests C23, dans chaque encodage ; Python réel **3.11.15**, `TMPDIR` absent, réseau interdit dans la suite.
- `image.json`, `image.log` : `wp/tests/preparer-image.ps1` exécuté après les nouveaux tests, code **0**, `T01 IMAGE READY`.
- `manifest.json` : sources C26 et dépendances C23 minimales, seuls documents/reçus courants. `verification-finale.json` : **77/77 contrôles, code 0** ; `qualification-finale.json` : **20/20 falsifications refusées** (19 reçus rescellés + source déclarée fausse), réseau bloqué et aucune écriture production. Totaux, cases, **toutes les lignes C23, identités et inverses exacts et uniques**, SHA et restaurations recalculés ; attente privacy déduite du public, jamais du champ `positive` déclaré. La qualification inclut suppression des contrôles supplémentaires, inverse vide redéclaré faux, faux tiers positif, identité dupliquée, échec caché hors grille et mutations blanchies. Préparation d'image distincte : dépendances publiques seules dans Docker.

Inventaire **une ligne par sortie** : `INVENTAIRE.md`. Catalogue machine et observations : `correction-livraison-V2.json`, `correction-livraison-V2-inventaire.json`, `correction-livraison-V2-privacy.json`. Oracle complet CONTENU_FICTIF_RESERVE, phrases C08/C10/C12 et B06 ; chaque corps réservé sans témoin reconnu est refusé même pour un lecteur autorisé. Droits C14 et B06 séparés : abonnement/achat ne donne pas B06, P-COOP ne donne pas les articles. Aucun cas synthétique n'est crédité comme parcours réel.

## Mutations : ce qui est réellement joué

| Famille | Mutation et chemin réel | Preuve |
|---|---|---|
| Agenda B07 | Mauvais titulaire au callback natif enregistré ; vraie inscription `Agenda::inscrire()`, 15 tiers rouges | `correction-mutations-V2-mutation-agenda.json` |
| Personnalisation C24 | Même faute de raccord ; vraie réponse `Personnalisation::enregistrer()`, sentinelle dédiée persistée | `correction-mutations-V2-mutation-personnalisation.json` |
| Rétractation C25 | Même faute de raccord ; vraie demande/note/journal Woo fictifs ; aucun remboursement ni annulation | `correction-mutations-V2-mutation-retractation.json` |
| Sujet B08 | Même faute de raccord ; vraie proposition `Sujet::enregistrer()` | `correction-mutations-V2-mutation-sujet.json` |
| Soutenir B08 | **Phrase C08 ET témoin B06** persistés ensemble ; vrai GET anonyme, deux familles détectées, contenu restauré après comparaison préalable | `correction-mutations-V2-mutation-cooperative.json` |
| Coopérateurs B06 HTTP | Statut temporaire V-INSCRIT ; vrai GET rouge puis métadonnée restaurée | `correction-mutations-V2-mutation-cooperateurs.json` |
| Archive événements | Phrase C10 dans le **vrai template d'archive**, GET `/evenements/` rouge, structure valide et source restaurée | `correction-mutations-V2-mutation-archive.json` |
| Décision B06 | **`Cooperateurs::autorise()` muté avant inventaire**, V-INSCRIT ouvert ; oracle indépendant refuse ; réglages/acteurs inchangés, source relue/restaurée | `correction-mutations-V2-mutation-autorisation-b06.json` |

Les quatre premières mutent le raccord du titulaire ; les deux dernières une source distante temporaire gardée par empreintes et refus de dérive concurrente. Aucun corps HTTP ni résultat n'est falsifié en mémoire pour ces huit preuves. Les anciennes 35 mutations B06 de corps en mémoire restent des tests de détecteur, pas des parcours applicatifs. `C26_PERSONNALISATION_FICTIF` et `C26_ACCUSE_FICTIF` remplacent les témoins datés : les champs temporels des deux seules fixtures temporaires portent ces sentinelles pour traverser les vrais rendus/exporteurs, sans prétendre qualifier la validation des dates métier.

## B06 : périmètre à relire comme code neuf

Cette extension est restée en place dans C23 mais n'a pas encore ses deux relectures. C26 la soumet explicitement, sans la déclarer close de lui-même :

- `wp/outils/demo/c23.py` : **`cooperator_routes()` (139–161), `assess_cooperator()` (164–193)** ; intégration dans `build_routes()` et `matrix()` (publics autorisés, témoins B06 ajoutés aux interdits, contrôles inverses). Cinq pages × HTML, REST unitaire, alias, collection, oEmbed, embed et recherche.
- `wp/outils/demo/c23-inventaire.php` : bloc `$out['cooperator_pages']`, cinq vrais IDs ; bloc `$out['cooperator_publics']`, décision native observée, **pas un attendu** ; ajouts minimaux `$out['cooperator_roles']` et `$out['cooperator_actors']` pour lecture des caractéristiques/réglages bruts. Pages : 2867 Espace coopérateurs, 2868 Appels à bénévolat, 2869 Lettre de missions, 2870 Cadastre des compétences, 2871 Relais des événements.
- `wp/outils/demo/c23-preparer.py` : **`cooperator_snapshot()` (125–127), `seed_cooperator_witness()` (130–135), `restore_cooperator()` (138–143)** ; `private_snapshot()` et ordre dans `run()` (146–237). Cinq corps initialement vides exigés ; pose CAS des témoins ; restauration qui refuse une dérive concurrente.
- `wp/tests/demo/c23-tests.py` : **`CooperatorsTest` (195–270), `PreparationSafetyTest` (272–315), `LiveMutationHarnessTest` (317–332)**. Le seul changement C26 dans ce fichier est **`test_scratch()`** et ses deux appels : plus d'accès obligatoire à `os.environ['TMPDIR']`, plus de repli implicite vers le temporaire système.
- `wp/tests/demo/c23-mutations.py` : **`inject()` (22–33), `run()` (36–87)** : recette historique de mutations **en mémoire**, explicitement limitée à cette portée. `wp/tests/demo/c23-verifier.py` : `matrix_checks()` et inverses B06, à lire avec ces tests, sans réécrire les reçus historiques.
- Extension nouvelle : `wp/outils/demo/c26.py`, `wp/outils/demo/c26-preparer.py`, `wp/tests/demo/c26-fixture.php`, `wp/tests/demo/c26-tests.py`, `wp/tests/demo/c26-verifier.py`, `wp/tests/demo/c26-paquet-tests.py`.

Fonctions corrigées à relire : `c23.reserved_witnesses()` (oracle historique extrait sans changement), `c26.cooperator_expected()` (P-COOP documenté + rôles/réglage livrés), `validate_cooperator()` (compare au natif), `denied_markers()` (droits séparés), `routes()`/`assess()` (archive). Dans le préparateur : `restoration()`/`finish_restoration()`, `mutate_source()` et les recettes. Dans le vérificateur : `privacy_checks()` et `c23_checks()` exigent les ensembles complets et leurs résultats positifs. Les dix nouveaux tests couvrent aussi pannes cleanup/B06, reçu même si relecture échoue, restauration de source sur erreur et refus de dérive. Ces pannes sont injectées offline, sans laisser le site sale.

Les oEmbed coopérateurs autorisés prouvent l'objet riche et le bon titre ; les six autres sorties prouvent aussi la présence du témoin. Un flux `post_type=page` ne vaut pas preuve des pages B06 ; aucun faux flux B06 n'est ajouté.

## Restauration et limites

`correction-livraison-V2-restauration.json` et `correction-mutations-V2-restauration.json` : 14 égalités exactes (utilisateurs, toutes métadonnées utilisateur, pages/métadonnées, commentaires/notes, commandes Woo, adresses/opérations/lignes, navigation, options métier/calendrier), empreintes métier/actions planifiées identiques. Fixtures privées/commandes supprimées, cinq pages B06 remises vides, sources live et bootstrap identiques. Cleanup, B06, usermeta sont tentés indépendamment ; les erreurs et relectures échouées n'empêchent pas l'écriture du bilan. La restauration B06 conserve son refus d'écraser une dérive.

La découverte livrée reste **fermée, sans numéro**. `V-DEC-FIN` est contrôlé sans droit ; aucun cas épuisé ouvert n'est prétendu rejoué par C26. La recette C23 séparée reste historique. Les exceptions de l'arbitrage métier restent celles prévues : caches, sessions recréables et verrous du planificateur ne sont pas des règles métier ; C26 prouve en plus l'égalité exacte des lignes utilisateur capturées. Les compteurs auto-incrément ne sont pas un état métier.

Les URL de flux demandant les types privés sont réellement interrogées et inspectées ; WordPress les projette ici sur des articles publics : **ce n'est pas un flux privé non vide**. L'existence des données privées est prouvée par les callbacks natifs positifs, pas inventée depuis ce repli. Les droits C14 du numéro effectivement acheté sont respectés ; un texte légitimement lu n'est pas classé fuite. Les plans de site restent fermés comme dans C23 ; ni cache d'hébergement partagé ni vrais robots vérifiés ne sont prouvés.

Les anciens diagnostics sont historiques ; `correction-*-red.log` garde les défauts des oracles/vérificateur/restauration vus avant correction, pas des fuites réelles du site. Aucune extension de B07, notamment sur l'antislash connu. Aucun rapport parent, verrou, file, autre site, bibliothèque close ou autre lot de production touché. Deux adaptations minimales C23 (`c23.py`, `c23-inventaire.php`) changent ses SHA historiques : ancien paquet ni modifié ni rescellé ; preuve C26 courante réexécutée et dépendances scellées. Aucun Git, réel, email, achat ni déploiement.

Commande exacte d'image exécutée, après ajout des tests :

```bash
TMPDIR='C:/Users/Ced/AppData/Local/hermes/cache/scratch' powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
```
