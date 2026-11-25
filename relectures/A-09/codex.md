# Relecture indépendante Codex — A-09

Date : 25 novembre 2026. Périmètre : brief A-09, production A-09 et fichiers concernés dans `wp/`. Références : doctrine, décisions, grille et cahier des charges §4.3, lignes 1104–1105 (« plan de redirections validé avant la bascule, test automatisé après »).

Le rapport de Claude n'a pas été consulté. Aucun site, compte ou service externe n'a été interrogé. Seul ce rapport a été écrit.

## 1. Conformité

Les livrables sont présents : commande, module, tests, mode d'emploi, exemple de trois enregistrements fictifs et `PRET`. L'outil ne décide ni n'installe de redirections. Les contrôles d'origine, de statut déclaré, de cadence et les trois sorties correspondent au périmètre. Les choix de cibles relatives, de marqueur complémentaire et de plafond de diagnostic sont explicités.

**R1 — Important — Paramètres encodés valides exclus du plan.**

- **Fichier et ligne :** `wp/outils/bascule/a09/check.py:37`.
- **Problème :** l'interdiction des séparateurs et espaces encodés porte sur toute l'URI, donc aussi sur les valeurs de paramètres. Les entrées relatives `/ancien?retour=%2Fpage` et `/ancien?q=deux%20mots` lèvent toutes deux `A09_PLAN_URL`. Un seul de ces paramètres empêche de vérifier tout le plan. La restriction est annoncée dans le mode d'emploi, mais elle réduit la capacité demandée par le brief sans nécessité démontrée pour les paramètres : ces séquences encodées ne changent pas l'origine HTTP.
- **Correction proposée :** séparer les contrôles du chemin de ceux des paramètres ; conserver les valeurs encodées dans la requête, sans les décoder en séparateurs. Ajouter les deux cas ci-dessus à la validation et aux tests HTTP, en maintenant les refus d'origine externe et de caractères de contrôle.

## 2. Exactitude métier

Le §4.3 ne fournit pas de scénarios détaillés de redirection. Deux cas du contrat du brief ont donc été déroulés avec `check_row`, en mémoire, avec réponses simulées :

| Cas | Résultat attendu | Résultat observé |
|---|---|---|
| `/ancien` → 301 `/nouveau` → 200 | Conforme, un saut | Aucune anomalie, un saut, HTTP final 200 |
| `/ancien` → 301 `/milieu` → 302 `/nouveau` → 200, cible attendue `/nouveau` | Chaîne non conforme | `mauvaise_cible`, `chaine`, deux sauts, HTTP final 200 |

**R2 — Important — URI validée différente de l'URI interrogée.**

- **Fichier et ligne :** `wp/outils/bascule/a09/check.py:114`.
- **Problème :** la reconstruction de la requête supprime le délimiteur `?` lorsque les paramètres sont vides. `relative('/a?')` conserve pourtant `/a?`. Reproduction sans réseau : `Client.get('http://fictif.test/a?')`, avec connexion HTTP remplacée par un collecteur, transmet `/a`. De plus, le plan `/a?,/b,301` puis `/a,/c,302` est accepté : deux anciennes adresses distinguées par la validation deviennent la même requête, avec des attentes contradictoires. Le diagnostic peut donc porter sur une autre URI que celle fournie.
- **Correction proposée :** utiliser une représentation cohérente pour la validation, la détection des doublons, les comparaisons et le transport, en conservant notamment la présence d'une requête vide. À défaut de prise en charge, refuser explicitement ce cas avant tout appel plutôt que le modifier silencieusement. Tester les URI avec et sans `?` vide ensemble.

Les dates, échéances et calendriers de la grille ne concernent pas ce lot. Les boucles, chaînes, répétitions d'adresse et limites de parcours sont les cas limites pertinents.

## 3. Tests

Exécutions effectuées avec `python -B`, sans fichier de test ajouté ni accès réseau :

- Test livré `test_check.OriginStrictTest.test_port_zero_and_even_empty_userinfo_are_not_repaired` : **réussi**.
- Vérification de l'exemple : **réussie**, trois enregistrements.
- Quatre méthodes de contrôle supplémentaires exécutées depuis l'entrée standard : l'exemple passe ; les trois autres reproduisent R1, R2 et R3. Résultat `unittest` : deux échecs d'assertion et deux erreurs correspondant aux deux sous-cas de paramètres encodés.
- `python -B production/A-09/verifier.py` : **code 1**, `hash drift: wp/tests/a02-audit/README.md`. Vérification séparée : les 10 empreintes de sources du manifeste, les 132 empreintes de preuves et les 33 empreintes des sources du paquet final correspondent. Parmi les 80 empreintes de référence, seule celle de ce README partagé diverge. Cette divergence n'est pas attribuée à A-09 faute d'élément permettant de le faire.
- Appel en lecture seule de `verify_packet` sur `production/A-09/preuves/6fd5c1c30990` : **réussi**, 21 tests archivés, 13 rapports HTTP et 63 requêtes consignées. Il s'agit d'une vérification des preuves existantes, pas d'un nouveau rejeu HTTP.

**Limite de rejeu :** la suite complète de 21 tests n'a pas été relancée. `wp/tests/a09/run.py:26` crée systématiquement un répertoire de preuves et y écrit plusieurs fichiers ; les tests eux-mêmes créent des fixtures et des rapports. Cela contredit la consigne de cette relecture limitant toute écriture à `relectures/A-09/codex.md`. Le mode `--replay` présente la même incompatibilité. Aucun succès de rejeu complet indépendant n'est revendiqué.

La suite livrée couvre substantiellement les cas demandés : codes de redirection, mauvaises cibles, 404/503, chaînes, boucles, plafond, cibles externes immédiates et tardives, délai, plans invalides, cadence, refus d'exécution et protection CSV. Les assertions sur les GET effectivement reçus et le piège d'autre origine sont utiles. Elle ne couvre pas les trois écarts relevés ici.

## 4. Sécurité et données

**R3 — Mineur — Le contrôle ASCII ne couvre pas tout Unicode.**

- **Fichier et ligne :** `wp/outils/bascule/a09/check.py:34`.
- **Problème :** la plage interdite s'arrête à `\uffff`. Une ancienne adresse contenant U+1F600 est acceptée par `relative` et par `load_plan`, contrairement au contrat ASCII annoncé. Placée après une ligne valide, cette ligne ne provoque donc pas le refus préalable du plan ; son encodage échoue ensuite dans le client HTTP, après que les lignes précédentes ont pu être interrogées.
- **Correction proposée :** vérifier explicitement le caractère ASCII de l'intégralité de l'entrée avant son analyse, puis appliquer les autres restrictions. Tester un caractère au-delà de U+FFFF en fin de plan et vérifier le refus global avec zéro requête.

Pas de secret ni de donnée métier réelle identifié dans les fichiers A-09 examinés. Les réponses ne sont pas suivies automatiquement ; chaque origine est contrôlée avant visite. Les prédicats du marqueur natif et l'empreinte du MU de sécurité sont repris d'A-04. Les appels utilisent GET sans authentification ni cookies, avec cadence bornée. Les cellules CSV à préfixe de formule sont protégées. Aucun comportement WordPress, accès à la base ou paywall n'est modifié par ce lot.

## 5. Doctrine

L'outil reste une vérification autonome, hors logique métier WordPress. Il réutilise le garde-fou existant et ne modifie pas d'extension tierce. Les conventions PHP ne s'appliquent pas directement à ces scripts Python. Le mode d'emploi expose les limites du délai par opération socket et du diagnostic borné ; aucune autorisation de production n'est revendiquée.

La documentation de remise ne fournit pas de comparaison sourcée avec les fonctions des extensions retenues pour le principe « standard d'abord ». Aucune duplication précise n'a cependant été établie pendant cette relecture ; les corrections demandées portent sur les comportements reproduits ci-dessus.

## 6. Études (lots sans code)

Sans objet : lot de code. Aucune recherche externe n'a été effectuée, conformément au périmètre d'accès du relecteur.

## Verdict

**À corriger.**

- **Bloquant :** aucun défaut classé à ce niveau.
- **Important :** R1, refus de paramètres encodés valides ; R2, incohérence entre l'URI validée et la requête émise.
- **Mineur :** R3, contrôle ASCII incomplet.

Ces corrections sont techniques ; aucune question métier, visuelle ou touchant au réel n'est ouverte pour Ced. La suite complète reste à rejouer après correction dans le cadre autorisé pour produire ses preuves.

Ce verdict n'est pas un GO.
