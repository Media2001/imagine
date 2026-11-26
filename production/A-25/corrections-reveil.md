# A-25 — Corrections du réveil du 26 novembre 2026

**Alerte pour l'import : des messages de formulaires peuvent rester en clair après neutralisation/anonymisation.** C'est un avertissement éditorial permanent ; ce passage ne mesure aucune copie et ne modifie pas l'import.

- **Fait :** les quatre instructions de `corrections/A-25.md` sont implémentées dans le périmètre attribué.
- **Vérifié ici :** 33 tests Python verts en UTF-8 et 33 en cp1252, sur Windows avec `C:/Python314/python.exe`, version mesurée **3.14.6**. Reçus frais dans `corrections-python/` ; il ne s'agit pas d'un rejeu PHP/SQL.
- **Prêt : non.** Ancien `PRET` copié puis retiré avant toute mutation ; aucun nouveau `PRET` posé. Parent détenteur du verrou, verrou inchangé.
- **Réservé au parent :** préparation, matrice native classique/HPOS, PHP pur, PSR-12, rejeu global et rescellement après leurs résultats réels. Aucun Docker, WSL ou runner natif lancé ici.
- **Aucune question Ced :** décisions techniques prudentes appliquées. Aucun Git, réel, archive de site, compte, autre voie ou fichier commun modifié.

## Corrections et décisions prises à défaut

1. **PK et référence.** `Inventory.php` lit désormais `COLUMN_NAME,COLUMN_KEY`. La méthode pure `formStructure()` distingue clé primaire simple `submission_id` (entrée), clé primaire simple `id` avec `submission_id` non primaire (détail exclu), et structure ambiguë. Les composites, absences de clé et rôles non qualifiés deviennent indéterminés. Le contenu n'est jamais sélectionné par l'inventaire.
2. **Couverture fermée.** `forms.coverage` vaut uniquement `heuristique bornée` ou `couverture indéterminée`. Au moindre candidat ambigu, `counts.forms` est la chaîne fermée `couverture indéterminée`, pas un total partiel présenté comme complet ni un zéro silencieux. Après neutralisation, `inconnu après neutralisation` reste prioritaire. `other_tables` dénombre seulement les entrées structurellement qualifiées, jamais toutes les tables possibles. La projection vérifie cette cohérence et refuse les valeurs libres.
3. **Banc préparé, non exécuté ici.** `seed.php` ajoute cinq messages en 2022 à PK `submission_id`, et une vraie table-fille à PK `id` avec dix détails (deux par message). Le nominal doit publier uniquement cinq messages sous `autre`. Les phases `pk-only` (aucun magasin connu ni autre table d'entrées) et `ambiguous` doivent prouver respectivement absence de double compte/zéro silencieux et couverture indéterminée, avec empreintes avant/après. Les décisions de conservation du clone de neutralisation incluent explicitement ces deux tables ; aucun import partagé modifié. Dix assertions PHP pures nouvelles couvrent les rôles ; `verify.py` exige leurs noms, les nouveaux contrôles natifs et les observations exactes des sept variantes, pas seulement des étiquettes PASS.
4. **Étiquette et source.** `clear_messages_after_import=true` demeure inchangé, accompagné dans les deux sorties de `clear_messages_after_import_label` exactement égal à « avertissement éditorial permanent, non mesuré sur la copie inspectée ». `SOURCES.md` donne la phrase officielle exacte et la ligne `created_at` de la section `fluentform_submissions`, vérifiées dans le navigateur officiel ; provenance/extrait dans `fluentforms-source.json`. Extraction indisponible, HTTP simple 403, lecture navigateur réussie.

## RED / GREEN réellement observés

Scratch : `C:/Users/Ced/AppData/Local/hermes/cache/scratch/a25-corrections-20261126-212918/`.

- `red-wiring.log` : trois échecs attendus sur l'absence du rôle SQL, des fixtures et des assertions PHP. Ce sont des contrats statiques de câblage, **pas une exécution de PHP**.
- `red-projection.log` : deux échecs attendus sur les nouveaux rapports fermés (étiquette et couverture ambiguë).
- `red-verifier.log` : un échec attendu sur l'absence du validateur d'observation corrigée.
- GREEN final : `corrections-python/python-matrix.json`, environnements réellement mesurés, logs liés par SHA-256, sources finales dans `corrections-python/sources.json` ; 33 tests, zéro échec dans chacun des deux contextes. Aucun résultat natif simulé.
- L'ancien paquet vérifié en lecture seule est correctement refusé avec code 1 `A25_PACKET_INVALID` ; reçu `historical-packet-refusal.json` en scratch. **Les 185 fichiers préexistants de `preuves/` sont intacts**, comparés à l'inventaire SHA-256 d'avant correction. Les anciens manifestes/réceptions ne qualifient pas ces nouvelles sources et n'ont pas été rescellés.
- Copie privée de l'ancien marqueur : scratch `PRET.before`, SHA-256 `f1e3afb4c0d1c8d381bff38ab1ad89ca7a7770128ae29f9114247ae76de1b77f`.

### Rejouer Python seulement, sans Docker/WSL

Depuis `C:/Users/Ced/imagine`, shell bash du poste ; ces commandes ne lancent que la suite Python :

```sh
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=C:/Users/Ced/AppData/Local/hermes/cache/scratch C:/Python314/python.exe -B -m unittest discover -s wp/tests/a25 -p 'test_*.py' -v
PYTHONIOENCODING=cp1252 PYTHONUTF8=0 PYTHONDONTWRITEBYTECODE=1 TMPDIR=C:/Users/Ced/AppData/Local/hermes/cache/scratch C:/Python314/python.exe -B -m unittest discover -s wp/tests/a25 -p 'test_*.py' -v
```

## Commandes exactes réservées au parent — non lancées ici

À sérialiser avec les autres lots ; aucune source A-25 ne doit changer entre la matrice et le sceau. L'image locale et les dépendances fictives autorisées doivent être disponibles. Le chemin scratch et le chemin du nouveau paquet doivent être absents ; sinon choisir un nouveau suffixe pour **toutes** les commandes, jamais écraser un reçu.

```sh
C:/Python314/python.exe -B wp/tests/a25/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a25-corrections-reveil-native-01
C:/Python314/python.exe -B wp/tests/a25/verify.py --unsealed --require-shared-doc --evidence=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a25-corrections-reveil-native-01
```

Arrêter si une commande est rouge. La matrice exécute les deux contextes Windows, PHP natif classique/HPOS et PSR-12. Elle ne remplace pas les portes globales du parent (`preparer-image.ps1` puis `rejouer.ps1`). Mettre à jour les seules notes de finalisation autorisées **avant** de resceller. Après les vrais résultats verts, conserver le nouveau paquet de manière additive, sans retoucher `preuves/final/` :

```sh
C:/Python314/python.exe -B -c "import shutil; shutil.copytree('C:/Users/Ced/AppData/Local/hermes/cache/scratch/a25-corrections-reveil-native-01','production/A-25/preuves/reveil-20261126-01')"
```

Puis ce rescellement strict : il vérifie le paquet réel et le contrat partagé avant toute écriture, écrit le seul manifeste A-25, revérifie le sceau et écrit sa réception exclue du manifeste. **Aucun PRET n'est créé.**

```sh
C:/Python314/python.exe -B - <<'PY'
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('a25_verify', 'wp/tests/a25/verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
packet = Path('production/A-25/preuves/reveil-20261126-01').resolve()
receipt = io.StringIO()
with contextlib.redirect_stdout(receipt):
    code = v.verify(packet, sealed=False, require_shared=True)
if code != 0:
    print(receipt.getvalue(), end='')
    sys.exit(code)
manifest = v.ROOT / 'production/A-25/manifest.json'
manifest.write_text(json.dumps(v.inventory(v.PACKAGE), indent=2) + '\n', encoding='utf-8', newline='\n')
receipt = io.StringIO()
with contextlib.redirect_stdout(receipt):
    code = v.verify(packet, sealed=True, require_shared=True)
if code != 0:
    print(receipt.getvalue(), end='')
    sys.exit(code)
result = json.loads(receipt.getvalue())
(v.ROOT / 'production/A-25/candidate-verification.json').write_text(
    json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
print(receipt.getvalue(), end='')
PY
C:/Python314/python.exe -B wp/tests/a25/verify.py --require-shared-doc --evidence=production/A-25/preuves/reveil-20261126-01
```

Le `verify.py` sans `--evidence` vise encore le paquet historique ; employer explicitement le nouveau chemin ci-dessus. Un changement de source après matrice exige un nouveau rejeu ; un changement de note après sceau exige un nouveau sceau. Les portes globales, la décision finale et un éventuel futur `PRET` appartiennent exclusivement au parent.
