# A-23 — corrections du réveil du 26 novembre 2026

- **Fait** : les quatre instructions de `corrections/A-23.md` sont appliquées dans le périmètre A-23 ; consigne permanente, doctrine et brief relus en entier.
- **Prêt à relire** : code et tests livrés ; **pas de PRET**, pas de réception native revendiquée.
- **À arbitrer par Ced/Imagine** : i-1, collision d'un lecteur avec l'administration ; défaut conservé : oui. Aucune donnée réelle consultée.
- **Bloqué pour la preuve PHP/native** : aucun PHP Windows trouvé ; Docker, WSL, matrice native, préparation et rejeu global laissés au parent sérialisateur.
- **Ensuite** : matrice parent fraîche, sélection explicite, rescellage et portes communes ; ne pas réutiliser les anciennes preuves comme preuve de cette correction.

## Corrections et décisions prises à défaut

1. `Inventory.php` construit les rôles de gestion depuis `wp_roles()->roles` et le prédicat A-17 sur les **définitions**, plus `administrator`, `editor`, `shop_manager`. L'intersection avec tous les rôles du compte est unie à la détection `allcaps` existante : une surcharge négative ne masque plus la gestion par rôle.
2. Même expression régulière que A-17 pour les identifiants. Un rôle invalide portant une capacité de gestion provoque `A23_ROLE_IDENTIFIER_UNSAFE`, ajouté à la liste fermée locale ; aucun identifiant n'est recopié. Un rôle invalide non gestionnaire reste ignoré, comme en A-17.
3. Le seed partagé entre classique/HPOS ajoute cinq titulaires de rôle de gestion avec `edit_users=false`, et un multirôle customer + gestion également masqué. Il prouve les conditions de fixture par deux booléens fermés. Certains ont un abonnement pending, d'autres aucun commerce. Les assertions natives exigent toujours **32 lecteurs, 20 vivants, 3 sans historique**, les mêmes groupes d'empreintes, et l'absence des canaris. Un rôle de gestion invalide est aussi injecté en mémoire dans le véritable bootstrap confiné, avec refus fermé et absence de publication attendus.
4. i-1 et t-1 inchangés : collisions contre tous les comptes, administration comprise ; neutralisation détectée sur présence de `imagine_staging_disabled_plugins`. La dépendance à cette marque d'import est documentée ; import et logique d'analyse non modifiés.

`role-probe.php` teste le vrai adaptateur PHP et le vrai prédicat A-17 avec **doubles de frontières WordPress/SQL**, dans son propre processus. Il couvre surcharge négative, multirôle, capacités directes, rôles fixes sans définition, seuil de publication et limites d'identifiants, dans les deux chemins de stockage. Ce n'est pas WordPress natif. Le runner produit `role-definitions.json` ; le vérificateur exige ses cas nommés et les nouvelles assertions natives. Ce banc est livré mais **n'a pas été exécuté ici**, faute d'interpréteur PHP autorisé disponible.

## Tests réellement exécutés

Python mesuré : **`C:/Python314/python.exe`, 3.14.6**, Windows ; le Python du PATH est 3.11.15 et n'est pas utilisé pour les suites.

- RED contrats source : **5 tests, 5 échecs attendus, code 1**, avant correction. Ces tests sont explicitement structurels, pas une exécution PHP.
- RED vérificateur : **8 tests, 1 échec attendu, code 1** ; un reçu vert sans cas de rôle était accepté par le validateur générique.
- GREEN final : **30 tests Python, 0 échec, 0 erreur, 0 ignoré, code 0**, dans **chacun** des deux contextes complets : UTF-8 / mode UTF-8 1 ; cp1252 / mode UTF-8 0. Les tests de reçus utilisent des doubles explicitement identifiés, pas des preuves natives inventées.
- Syntaxe Python : analyse AST de tous les scripts du lot réussie. Aucune ligne des trois fichiers PHP changés ne dépasse 120 caractères ; cela **ne remplace pas** PHP lint ou PSR-12.
- Vérificateur contre le paquet historique, UTF-8 et cp1252 : **code 1 `A23_PACKET_INVALID`**, attendu. Il manque notamment le nouveau reçu de rôles et les sources ne correspondent plus. Aucun rescellage destiné à cacher ce résultat.
- PHP pur, lint PHP, PSR-12, WordPress classique/HPOS, matrice native et portes communes : **non exécutés**. Aucune commande Docker ou WSL lancée.

Reçus et logs réels :
`C:/Users/Ced/AppData/Local/hermes/cache/scratch/a23-corrections-reveil/`
(`red-role-contracts.*`, `red-role-receipt.*`, `utf8-python-tests.log`,
`cp1252-python-tests.log`, `python-only-results.json`, `historical-verify-results.json`).
Le wrapper `python-only.py` de ce dossier rejoue uniquement Python ; il ne lance aucun runner.

PRET a été copié octet pour octet dans ce scratch, puis retiré **avant modification**.
Les **112 fichiers historiques contrôlés** (109 fichiers du paquet final, manifeste,
reçu candidat et FINALISATION) restent inchangés. Les anciens chiffres de
`notes.md`/`FINALISATION.md` sont historiques et ne certifient pas cette correction.
Le manifeste et le reçu candidat existants sont volontairement périmés en attente du parent.

## Fichiers livrés

- Modifiés : `wp/outils/bascule/a23/{Inventory.php,refusals.json,README.md}`.
- Modifiés : `wp/tests/a23/{seed.php,inside.py,run.py,verify.py,test_verify.py}`.
- Créés : `wp/tests/a23/{role-probe.php,test_role_corrections.py}`.
- Notes : `production/A-23/notes.md` et le présent fichier.
- Retiré : `production/A-23/PRET`, sauvegardé en scratch, **non redéposé**.

Aucun Git, accès réel, archive, site, compte externe, voie 2, verrou ou fichier commun modifié.

## Commandes exactes réservées au parent — NE PAS exécuter en parallèle

Depuis **`C:/Users/Ced/imagine`**, Bash Windows. Les noms de dossiers doivent rester
nouveaux ; si déjà utilisés, choisir une nouvelle suffixation partout. Ces commandes
sont **préparées, non exécutées par cet enfant**. La préparation commune et le rejeu
global restent au parent ; nouvelle préparation requise avant tout futur PRET.

```sh
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR=C:/Users/Ced/AppData/Local/hermes/cache/scratch
export TEMP="$TMPDIR" TMP="$TMPDIR"
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 C:/Python314/python.exe -B wp/tests/a23/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a23-corrections-matrix-20261126
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 C:/Python314/python.exe -B wp/tests/a23/verify.py --evidence=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a23-corrections-matrix-20261126 --unsealed --require-shared-doc
```

La matrice exécute les deux suites Python, les deux runners natifs
(classique et HPOS chacun, avec les bancs purs et le nouveau banc de rôles), puis
PSR-12. Si PSR-12 exige une correction, conserver ce passage rouge, corriger dans
le périmètre A-23 et rejouer la **matrice complète sous un nouveau nom** après le
dernier changement de source. Ne pas appeler `style.py --fix` puis recycler un
ancien paquet vert.

### Sélection et rescellage A-23 seulement, après deux codes 0 et sources figées

Le premier bloc revérifie le candidat avant de déplacer l'ancien paquet. Il
sauvegarde aussi les anciens manifeste/reçu candidat sans les réécrire. Le second
scelle le paquet courant après les dernières notes parent. Aucun de ces blocs ne
dépose PRET. Les contrôles finaux doivent réussir dans les deux consoles avant
que le parent remplace explicitement son reçu candidat ou dépose PRET.

```sh
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 C:/Python314/python.exe -B -c "import hashlib,json,shutil,subprocess,sys; from pathlib import Path; new=Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch/a23-corrections-matrix-20261126'); prod=Path('production/A-23'); old=prod/'preuves/final'; hist=Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch/a23-historique-avant-correction-20261126'); assert not (prod/'PRET').exists() and not hist.exists(); subprocess.run([sys.executable,'-B','wp/tests/a23/verify.py','--evidence='+str(new),'--unsealed','--require-shared-doc'],check=True); hist.mkdir(); [shutil.copy2(prod/n,hist/n) for n in ('manifest.json','candidate-verification.json')]; shutil.move(str(old),str(hist/'final')); shutil.copytree(new,old); hashes=lambda root:{p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}; assert hashes(new)==hashes(old); print('A23_SELECTION_COPIE_EXACTE')"
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 C:/Python314/python.exe -B -c "import importlib.util,json; from pathlib import Path; s=importlib.util.spec_from_file_location('a23_verify','wp/tests/a23/verify.py'); v=importlib.util.module_from_spec(s); s.loader.exec_module(v); Path('production/A-23/manifest.json').write_text(json.dumps(v.inventory(v.PACKAGE),indent=2)+'\n',encoding='utf-8')"
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 C:/Python314/python.exe -B wp/tests/a23/verify.py --require-shared-doc
PYTHONIOENCODING=cp1252 PYTHONUTF8=0 C:/Python314/python.exe -B wp/tests/a23/verify.py --require-shared-doc
```

Si le parent veut un RED PHP additionnel : le prédécesseur exact est sauvegardé
en scratch sous `Inventory-before.php`, et `role-probe.php` accepte son chemin
comme unique argument optionnel. Le faire uniquement dans un runner A-23
positivement identifié par le parent, avec le vrai A-17 copié au chemin
canonique et sans site ; attendu : code 1 avec contrôles métier rouges. Le GREEN
courant est intégré à `run.py`. Aucun RED PHP n'est revendiqué dans ce rapport.
