# T-03 — convention fermee de rejeu

La commande relecteur reste `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\wp\tests\rejouer.ps1`, sans argument. La decouverte examine uniquement les dossiers immediats `production/<lot>` dont le nom est `[A-Z]-[0-9]{2}`, avec `verify.py` ou `rejeu.json` ; aucun glob de banc natif, aucune adaptation implicite d'arguments.

## Declaration `production/<lot>/rejeu.json`

Exemple de **format**, pas une preuve ni une declaration deja installee pour A-28 :

```json
{
  "schema": 1,
  "entrypoint": "verify.py",
  "requires": [],
  "logs": ["production/A-28/preuves/final/before/native.stdout.log"],
  "controls": ["PACKAGE_DRIFT", "PACKET_REFUSED"]
}
```

- Ces cinq cles exactement, pas de doublon JSON, entier `1` (pas booleen), listes de chaines uniques. `entrypoint` est exactement `verify.py` ; la commande est `/usr/bin/python3 -B /packet-repo/production/<lot>/verify.py`, **sans argument**. Aucun import du verificateur dans le processus collecteur.
- `requires` est une liste fermee parmi `docker`, `network`, `repository-write`, `arguments`. Toute exigence listee rend le paquet hors rejeu (respectivement `Docker requis`, `reseau requis`, `ecriture depot requise`, `argument requis`) sans le lancer ; la premiere exigence donne la raison. Une valeur inconnue ou declaration invalide donne `DECLARATION_INVALID`, sans execution.
- `logs` liste **tous** les journaux requis par le paquet, meme ceux absents de la copie. Chemins POSIX relatifs sous `production/<lot>/` ou `files/rapports/`, finissant par `.log`, sans `..`, lien symbolique ou segment non ASCII `[A-Za-z0-9_.-]+`. La liste vide ne convient qu'a un verificateur sans journaux. Le parent derive cette liste des manifestes/references du paquet scelle, **pas uniquement des fichiers presents** : les `.log` ignores dans une copie Git doivent rester declares. Un seul manque suffit a `hors rejeu : <lot> (journaux absents)` ; aucun faux echec, aucune reconstruction des journaux.
- `controls` est la liste **fermee de tous les noms de controles** que l'entree peut publier : codes `code` et noms `checks[].check`, rouges comme verts. Grammaire `[A-Za-z][A-Za-z0-9_:.-]{0,159}` ; pas de chemin ni valeur du site. On derive cette liste du code et du contrat connu, jamais d'une sortie non fiable du site. Aucun controle d'un autre lot n'est reecrit.

Declaration absente : hors rejeu `declaration absente`. Une entree declaree mais absente donne `VERIFIER_START`. Les liens de lot, d'entree, de declaration et de journaux sont refuses. Le contrat des trois lignes communes est `readme-ajout.txt`, dans le vrai mode d'emploi T-01 `production/T-01/notes.md` (c'est le fichier nomme par le brief T-01 ; aucun README racine n'est modifie).

## Sortie et confinement

Le verificateur conserve son JSON existant : un seul objet sur stdout, stderr vide, entier `exit_code` ou `exit` egal a 0/1 (si les deux sont presents ils doivent etre egaux), code processus coherent. `checks`, lorsqu'il existe, est une liste non vide de controles uniques avec `status` PASS/FAIL ; si `status` global existe au vert, il vaut PASS ou CANDIDAT_GATE_PARENT. Les sorties A-21/A-22 candidates sont ainsi acceptables sans les transformer en preuve de gates parent. Une sortie rouge ne publie que son premier controle declare ; erreur de protocole ou nom inconnu = `VERIFIER_OUTPUT`, delai depasse = `VERIFIER_TIMEOUT`, lancement impossible = `VERIFIER_START`. Jamais de stdout/stderr brut du verificateur sur la sortie relecteur.

Le JSON interne `T03_PACKETS` porte `verified` (entrees tentees, rouges comprises), `lots` (ces lots dans l'ordre), `failures` (premier controle rouge de chaque paquet) et `excluded` (lot et raison fermee). Les declarations invalides peuvent etre rouges sans entree tentee. La seule nouvelle ligne de bilan est :

```text
PAQUETS : n verifies, n echecs ; hors rejeu : ... ; A-28 PACKAGE_DRIFT
```

Les accents de la sortie reelle sont preserves. `PAQUETS` precede `OUTILS`, puis l'ancien `REJEU` final **inchange octet pour octet**. Ni compteur PHPUnit/outils, ni `pass`, ni exit du rejeu ne depend des paquets ; marqueur absent/malforme = T-03 RUNNER_OUTPUT sur cette seule ligne. `lots` permet la preuve explicite qu'A-22 et A-28 ont bien ete lances, sans ajouter une ligne de bilan par paquet.

Le montage T-01 `/repo/wp:ro` et tous les drapeaux existants sont conserves. Un second montage de la **meme racine de depot**, `/packet-repo:ro`, rend disponibles les preuves et fichiers de sources dont les anciens verificateurs calculent les empreintes. L'inspection exige exactement ces deux montages, leur source attendue et RW=false avant/apres. Le conteneur reste `network=none`, rootfs ro, utilisateur 65534, cap-drop ALL, no-new-privileges, limites identiques, tmpfs `/tmp` seulement. Python recoit HOME/TMPDIR/XDG_CACHE_HOME=/tmp et PYTHONDONTWRITEBYTECODE=1, sans shell, delai 90 s par entree. L'enveloppe globale T-01 reste 600 s : les paquets attendus doivent tenir dans ce budget ; le parent le mesure sur la chaine reelle.

Python standard est ajoute **seulement dans le Dockerfile existant**, par la preparation d'image existante. `verifier-image.php` en sonde les imports hors reseau. Aucun Python/PHP n'est installe sur Windows ; aucun changement de `preparer-image.ps1` n'a ete necessaire. Les matrices natives classique/HPOS/commerciales restent hors de cette commande : lire leurs recus scelles ne les rejoue pas.
