# A-09 — vérifier un plan de redirections (lecture seule)

**Aucune redirection n'est choisie, créée ou modifiée. Aucune production autorisée.**
Python 3.11+ standard, sans dépendance. Garder `a09/`, `a04/update.py` et le fichier
de sécurité `wp/outils/staging/mu-plugins/000-imagine-staging-safety.php` dans le dépôt.

## Préparer les entrées, sans appeler le site

Le plan CSV UTF-8 appartient au dépôt : en-tête exact `ancienne,cible,code`, puis
une ancienne URI relative à la racine, une cible relative, un code parmi
301/302/303/307/308. `plan-redirections.exemple.csv` contient **trois lignes de données
entièrement fictives**, en plus de l'en-tête. Les paramètres d'URL sont significatifs.
Encoder les caractères non ASCII (y compris au-delà de U+FFFF) ; aucun fragment,
espace, antislash ou contrôle littéral. Dans le chemin : aucun segment `.`/`..`,
espace, contrôle ou séparateur encodé. La requête conserve exactement ses encodages
licites (`u=%2Fpage`, `q=deux%20mots`, casse comprise), sans décodage ; les contrôles
encodés restent interdits. Une requête vide (`/a?` ou cible `/b?`) refuse **tout le
plan**, code 2 `A09_PLAN_EMPTY_QUERY`, zéro GET : jamais de normalisation silencieuse.
Une `Location` à requête vide est invalide et non suivie. Pas d'URL HTTP absolue, `//hôte`, doublon même
identique, ligne contradictoire ou ancienne=cible (y compris caractères non réservés
encodés dans le chemin). Maximum 1 000 lignes et 1 Mio pour le plan, 2 048 caractères par URI.
**Tout le plan est validé avant la première requête**, sans traitement partiel.

Le répertoire `--wp-path` doit déjà porter le marqueur natif
`.imagine-staging-verified.json` avec `status=verified`, `offline_verified=true`,
`runtime_probe_passed=true`, et les octets exacts du MU de sécurité, comme A-04/A-05.
L'opérateur autorisé doit en plus y avoir déclaré l'origine HTTP exacte dans
`.imagine-a09-http.json` :

```json
{"schema":"imagine-a09-http-v1","kind":"test","base_url":"http://site-fictif.test"}
```

`kind` accepte seulement `test` ou `staging`. Schéma, hôte et port sont liés à
`--base-url`, qui ne contient ni identifiants, ni chemin de sous-répertoire, ni
paramètres. Ne jamais fabriquer un marqueur natif sur un site non vérifié ; cette
déclaration n'est ni une vérification de staging ni un GO de Ced.

## Lancer puis lire

Depuis le dépôt, dans l'environnement autorisé (exemple fictif, ne pas exécuter tel quel) :

```bash
python3 -B wp/outils/bascule/tester-redirections --wp-path=/srv/site-fictif --base-url=http://site-fictif.test --plan=wp/outils/bascule/plan-redirections.exemple.csv --output=/srv/rapports/controle-fictif --interval=0.5 --timeout=5
```

La sortie doit être nouvelle, hors du site, dans un parent existant. Aucun lien
symbolique accepté dans les entrées ou la sortie. Codes : **0** tout conforme ;
**1** au moins une non-conformité ; **2** refus/erreur d'exécution (ne pas conclure).
Lire `rapport.md` et `nonconformes.csv` (UTF-8 BOM, cellules protégées des formules) ;
`rapport.json` donne les traces et les comptes. Le rapport est aussi affiché.

GET uniquement, sans cookies, authentification, proxy d'environnement, nouvelle
tentative automatique ni téléchargement des corps. Toutes les requêtes, y compris
les sauts et les lignes suivantes, sont espacées : 0,5 s par défaut, minimum 0,1 s,
maximum 60 s. Délai réseau par opération socket : 5 s, réglable de 0,05 à 30 s
(résolution DNS selon l'OS ; aucun test de contenu). HTTPS vérifie normalement TLS.
Jamais de suivi automatique : chaque `Location` est contrôlée avant le prochain GET,
même dans une chaîne. Une autre origine (schéma/hôte/port) est signalée sans visite.
Conforme = code et première cible exacts, un saut, HTTP 200 ; sinon code/cible,
chaîne, boucle, cible non-200, externe, délai ou erreur sont détaillés. Diagnostic
borné à 9 requêtes par ligne ; la limite n'est jamais une conformité.
`mauvaise_cible` compare la **première** cible au plan ; une chaîne peut donc avoir
ce diagnostic même si sa destination finale est la cible attendue.

**Rejouer la preuve fictive Windows/WSL :** `python -B wp/tests/a09/run.py`.
Banc Docker propre à A09, réseau `none`, HTTP loopback réel, aucun site de démonstration.
Vérification livrable et rejeu parent : `python -B production/A-09/verifier.py --replay`.
Ce paquet Python a sa commande dédiée ; aucun succès global `rejouer.ps1` n'est revendiqué.
