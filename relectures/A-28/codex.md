# Relecture indépendante Codex — A-28

Date : 27 novembre 2026. Périmètre : brief A-28, production A-28, import et tests concernés dans `wp/`. Doctrine et §4.4 du cahier des charges lus. Le rapport de l’autre relecteur n’a pas été consulté. Aucun code ni paquet de preuves modifié.

## 1. Conformité

La réalisation suit l’essentiel du brief : liste fermée partagée entre Python et PHP, purge obligatoire de six tables Fluent Forms et de deux types Flamingo, refus de `garder` et d’`anonymiser`, compteur et code de refus, archives fictives, comparaison avant/après et témoins de mutation. Le paquet unique, le marqueur `PRET` et les trois lignes du mode d’emploi sont présents. Le vérificateur contrôle les blocs de commandes de Ced et les trouve inchangés.

L’inclusion des contacts Flamingo et des révisions est explicitée. Les tables et types inconnus conservent leur traitement antérieur ; aucune suppression générale du magazine n’a été introduite. Les limites sur les pièces jointes et autres stockages sont annoncées.

Le contrôle indépendant des résidus ne couvre toutefois pas entièrement les métadonnées incluses dans ce périmètre : point I1 ci-dessous.

## 2. Exactitude métier

Cas déroulés à la lecture du code, puis comparés aux reçus du paquet :

- **Table connue avec canari, politique par défaut** : `Policy.resolve()` impose `vider`, le SQL normalisé écarte ses données, puis les phases PHP appliquent la même obligation. Les oracles des imports classique et HPOS indiquent zéro ligne et zéro canari dans chacune des six tables.
- **Même table avec `garder`** : refus Python `sql_preflight / FORM_MESSAGES_DECISION_REFUSED`, suffixe fermé de table, avant import SQL. L’appel natif refuse également à la construction du moteur, avant purge des fichiers, avec sortie 78. Les reçus comparent base et fichiers avant/après.
- **Message Flamingo avec révision et métadonnées** : les identifiants sont calculés avant les suppressions ; le parcours nominal supprime parent, révision et métadonnées. Les contenus `fiction_magazine` et `wpcf7_contact_form` restent préservés. Le test pur couvre aussi une révision de révision et le rejeu de neutralisation.
- **Table inconnue** : vidée par défaut, conservable par la décision historique lorsque celle-ci est admissible. Le type inconnu et ses métadonnées restent présents ; ce comportement est conforme à l’interdiction de décider pour eux dans A-28.

Les dates de clôture et changements d’année ne concernent pas ce lot. Les cas pertinents sont ici le rejeu, les révisions, les vues, les décisions incompatibles et les résidus introduits après nettoyage.

## 3. Tests

Exécutions indépendantes réalisées avec Python Windows `C:/Python314/python.exe`, option `-B` :

| Vérification | Résultat constaté |
|---|---|
| `production/A-28/verify.py` | **PASS**, sortie 0 ; 16 cas natifs, 6 cas historiques et 32 témoins de mutation reconnus dans les preuves |
| `unittest discover -s wp/tests/a28 -p test_*.py -v` ; UTF-8/mode 1 et cp1252/mode 0 | Dans chaque contexte : 17 tests, 10 réussites, 7 erreurs `PermissionError`, aucune assertion en échec |
| Suite `wp/tests/a01-court`, mêmes deux contextes, `TMPDIR` dirigé vers le temporaire Windows | Dans chaque contexte : 109 tests, 63 réussites, 38 erreurs `PermissionError`, 8 ignorés, aucune assertion en échec |
| `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1` | Sortie 1 avant tout test : `Wsl/Service/E_ACCESSDENIED` ; Docker inaccessible |

Les suites Python ont aussi été lancées par découverte `unittest` avec un rapport capturé en mémoire pour condenser leurs erreurs, sans changer leurs tests. Un premier lancement A-01 sans `TMPDIR` rencontrait également le chemin Linux `/opt/court/test-scratch` absent sous Windows ; les résultats du tableau sont ceux après configuration du temporaire.

Les erreurs ci-dessus sont des limites de l’environnement de relecture, pas des défauts fonctionnels démontrés d’A-28. Aucun contournement des permissions n’a été tenté. La matrice native Docker/PHP n’a donc pas pu être rejouée indépendamment. Le **PASS du vérificateur de paquet ne constitue pas un nouveau passage des imports ni du rejeu global**.

Les preuves livrées, dont les empreintes sont acceptées par ce vérificateur, consignent bien les passages UTF-8/cp1252, A-01 et globaux annoncés. Les tests examinent les vraies données restaurées et les refus natifs, et pas seulement les décisions de politique. En revanche, leurs mutations injectent des lignes de tables dédiées ou des parents Flamingo ; elles ne couvrent pas le résidu constitué uniquement de métadonnées décrit en I1.

## 4. Sécurité et données

**I1 — important — `wp/outils/staging/lib.php:663` : les métadonnées deviennent invisibles au contrôle après disparition du parent.** Le compteur initialise sa valeur avec `formPostIds()`, qui ne retrouve que les parents Flamingo encore présents et leurs révisions, puis ajoute les lignes des six tables dédiées. Il ne compte jamais les lignes de `postmeta`. Cas précis à ajouter au banc : retenir l’identifiant d’un message connu de la fixture, nettoyer ce message, puis laisser ou réinjecter sa seule métadonnée `_a28_message` contenant un texte canari ordinaire. Sans parent restant, le compteur vaut zéro ; les contrôles génériques ne bloquent pas ce texte libre. Le vérificateur peut donc accepter cette copie alors que subsiste une partie du message pourtant incluse dans le périmètre annoncé.

Constat établi par analyse statique ; ce cas supplémentaire n’a pas été exécuté en PHP, inaccessible ici. Il ne remet pas en cause la suppression nominale des métadonnées, observée dans les preuves livrées. **Correction proposée :** conserver jusqu’à la vérification une provenance technique fiable des identifiants de messages/révisions supprimés, ou une garantie équivalente permettant de vérifier leurs métadonnées après suppression des parents. Compter et refuser les résidus associés avec le code fermé existant. Ajouter un témoin où seule la purge des métadonnées est omise et vérifier que la copie est refusée. Ne pas étendre cette correction à une suppression générale des métadonnées ou types inconnus.

Les nouveaux diagnostics de refus exposent des codes et suffixes issus de la politique, sans valeur du message. Le refus de conservation intervient avant mutation. Les accès SQL concernés utilisent le magasin PDO et ses paramètres préparés. Les fixtures examinées sont manifestement fictives. Le paywall n’est pas modifié par ce lot.

## 5. Doctrine

L’ajout s’insère dans l’import existant, sans nouvelle extension ni commande opérateur. Le PHP concerné utilise `strict_types` et l’espace de noms `Imagine\Staging`. Les données métier des fixtures restent hors des rapports de refus. La séparation entre `PRET` technique et autorisation d’accès au réel est correctement rappelée.

Les invalidations des anciens paquets dépendants sont signalées dans `REJEUX-PARENT.md`, sans rescellement présenté comme un rejeu. Elles restent à traiter par leur propriétaire.

### Pour Imagine

Question métier reprise de `production/A-28/notes.md:33` : faut-il inclure certains types aujourd’hui inconnus dans une future politique de suppression des messages ? **Défaut proposé :** aucune suppression supplémentaire dans A-28 ; conserver le comportement actuel et qualifier les types individuellement avant tout élargissement. Cette question ne justifie ni la destruction globale des types inconnus ni un GO sur une copie réelle.

## 6. Études

Le lot contient du code, mais son état du standard reste soumis à l’exigence de citation du brief. Les premières entrées donnent des adresses officielles et des citations ou extraits de source. Aucun site externe n’a été consulté pendant cette relecture, conformément aux droits du relecteur.

**M1 — mineur — `production/A-28/standard.md:11` : justification documentaire incomplète pour deux tables.** L’entrée consacrée à `fluentform_draft_submissions` et `ff_scheduled_actions` ne fournit pas la phrase officielle citée demandée par le brief, ni de référence précise propre à cette affirmation. Les empreintes dans `official-sources.json` ne remplacent pas l’extrait documentaire absent. **Doute** sur cette justification en l’état du livrable, sans conclure que les noms seraient erronés. **Correction proposée :** ajouter pour chacune la citation exacte et l’adresse officielle qui établissent son stockage, en conservant la liste courte.

## Verdict

**À corriger.**

- **Bloquant :** aucun point classé à ce niveau.
- **Important :** I1 — contrôle incomplet des métadonnées résiduelles après suppression du parent connu.
- **Mineur :** M1 — deux tables sans la citation documentaire demandée.

La relecture indépendante des tests reste partielle à cause des refus d’accès locaux ; les preuves livrées sont intègres selon leur vérificateur. Ce verdict n’est pas un GO.
