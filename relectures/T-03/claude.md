# Relecture T-03 — Rejeu des vérificateurs de paquet

Relecteur : Claude, indépendant. Date : 2026-11-27.
Je n'ai pas lu `codex.md`. Pas de fusion à ce stade.

## Rejeu de la commande autorisée

Commande (sans argument, exactement) :

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Lignes de bilan de ma propre exécution :

```
PAQUETS : 9 vérifiés, 0 échecs ; hors rejeu : A-20 (declaration absente), A-31 (journaux absents)
OUTILS : 22 outils, 584 contrôles, 0 échecs ; hors rejeu : aucun
REJEU : 1153 tests, 36075 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

- 9 paquets vérifiés : A-21, A-22, A-23, A-24, A-25, A-26, A-27, **A-28**, A-30. A-22 **et** A-28 sont bien dedans (preuve demandée par le brief).
- Hors rejeu : A-20 (plus de `rejeu.json`), A-31 (dossier `preuves/` absent du dépôt).
- Isolation affichée : `network=none ; rootfs=ro ; mount=…/wp:/repo/wp:ro ; ports=none ; cap-drop=ALL ; no-new-privileges`.
- Nettoyage : `T01 CLEANUP : absence verifiee de imagine-t01-…` ; balayage d'orphelins au départ. Aucun conteneur ne reste.
- La ligne `REJEU` est identique à celle du rapport d'Hermès.

## 1. Conformité

- Conforme. La commande gagne **une seule** ligne `PAQUETS`, placée avant `OUTILS`, puis `REJEU` en dernier, inchangée. `scripts/` n'est pas modifié (git propre) ; aucune commande nouvelle à autoriser ; `rejouer.ps1` ne contient pas `python` (le Python ne tourne que dans le conteneur).
- Découverte conforme au brief et à `CONVENTION.md` : seuls les dossiers immédiats `production/<lot>` au nom `[A-Z]-[0-9]{2}` avec `verify.py` ou `rejeu.json` sont examinés ; déclenchement opt-in par `rejeu.json` fermé (`schema:1`, `entrypoint:"verify.py"`, `requires`, `logs`, `controls`). Le second montant `/packet-repo:ro` est ajouté sans assouplir aucun drapeau T-01 ; les deux montages sont vérifiés RW=false avant/après.
- Interprétation signalée (opt-in) : les lots sans déclaration (A-00→A-19, **A-29**, tous les B-xx/C-xx) sont hors périmètre et **n'apparaissent pas** sur la ligne `PAQUETS`, ni vérifiés ni hors rejeu. C'est le comportement voulu par le brief (« qui se déclare rejouable »), mais il reste invisible dans la sortie (voir point mineur 1).
- Écart vs brief sur A-20 : le brief prévoit que « A-20 à A-25 » soient tous requalifiés en entrée sans argument. Hermès a requalifié A-21→A-25 mais a **retiré la déclaration d'A-20** (son `verify.py` existe, son `rejeu.json` a été supprimé → hors rejeu « declaration absente »). C'est disclosé par le `RAPPORT`/`PRET` (« déclaration A20 retirée, métadonnées vérifiées sans changer ses contrôles »). Le brief tolère explicitement des lots hors rejeu nommés, donc le mécanisme reste conforme ; mais la requalification d'A-20 prévue par le brief n'est pas faite (voir point important).

## 2. Exactitude métier (déroulé à la main)

Déroulé des cas du cahier des charges / brief, code lu (`wp/tests/t01/paquets.py`, `paquets.php`, `paquets.ps1`, `commun.ps1`) et preuves croisées.

- **Cas sain déclaré (A-28)** : `rejeu.json` avec `requires:[]`, journaux présents, `controls` incluant `PACKAGE_DRIFT`. `verify.py` lancé en `/usr/bin/python3 -B …` sans argument ; verdict vert → compté. Confirmé : A-28 figure dans `lots` de ma sortie verte.
- **Reçu altéré d'un octet** (`preuve/final/native/copy-proof/result.json`, banc propriétaire `native-copy-proof.ps1`, copie jetable hors dépôt) : le dernier octet de `production/A-28/preuves/final/before/native.json` est inversé → `PAQUETS : 9 vérifiés, 1 échecs ; … ; A-28 PACKAGE_DRIFT`, tandis que la ligne `REJEU` reste **identique** (mêmes 1153 tests, PASS). Copie supprimée (`copy_absent=true`), reçu d'origine inchangé (`original_receipt_unchanged=true`). Conforme à l'exigence centrale du brief : un paquet rouge chez un voisin ne touche ni `REJEU` ni le code de sortie.
- **Cas limite — journaux absents (A-31)** : `preuves/` absent du dépôt → « journaux absents », **pas** un échec. Le parent dérive la liste `logs` du paquet scellé, pas seulement des fichiers présents : un seul manque suffit à sortir le lot sans faux échec. Confirmé.
- **Cas limite — déclaration absente (A-20)** : `verify.py` présent mais pas de `rejeu.json` → « declaration absente ». Confirmé.
- **Cas limite — exigence Docker/réseau/écriture/argument** : `requires` non vide → hors rejeu avec la raison fermée de la première exigence, verificateur jamais lancé (code `replay`, couvert par test).
- **Cas limite — déclaration invalide / clé en double / lien symbolique** : `DECLARATION_INVALID` sans exécution (lu dans `declaration()` et `no_links()`, couvert par test).
- **Cas limite — marqueur `T01_RESULT` absent/malformé** : `Get-T03PacketSummary` retombe sur `PAQUETS : 0 vérifiés, 1 échecs ; hors rejeu : aucun ; T-03 RUNNER_OUTPUT`, sur cette seule ligne ; `REJEU` intact. Conforme.
- **Étanchéité de la sortie** : `parse_verdict` ne publie **que** le nom du premier contrôle rouge déclaré ; jamais le stdout/stderr brut du vérificateur. Les tests injectent un `PRIVATE_CANARY_PATH` et vérifient qu'il ne fuit pas. Bien.

Je confirme que, côté PHP, le statut des paquets n'entre pas dans `$pass` (`executer.php` l.201, `$pass = $pass && … && $toolTotals['failures'] === 0`, sans `$packet`) et que le code de sortie ne dépend que des tests et des outils (`rejouer.ps1` l.63). Le mécanisme « le relecteur lit la ligne `PAQUETS` pour son lot » est donc réel.

## 3. Tests

- J'ai rejoué la **vraie** suite via la commande autorisée : `REJEU … — PASS` (voir ci-dessus), `PAQUETS` vert, `OUTILS` 22/584/0, conteneur supprimé.
- **Limite de droit** : les tests de contrat T-03 eux-mêmes (`wp/tests/t01/test_paquets.py`, `test_t03_integration.py`) ne sont **pas** joués par la commande relecteur — ce sont des fichiers `.py` ; la commande rejoue les bibliothèques PHPUnit, les outils de bascule et le rejeu **réel** des paquets. Je ne les ai pas exécutés (mon seul droit d'exécution est cette commande sans argument). Leur vert repose sur les preuves parent (`preuves/final/native/global-retry-*.log`).
- Revue statique de ces tests : la couverture est bonne et teste la **règle**, pas le code. Sont couverts : journaux absents → hors rejeu sans lancement ; `requires` → hors rejeu nommé ; déclaration invalide/doublon/symlink → `DECLARATION_INVALID` sans exécution ; rouge nommé + suppression du texte non fiable ; faux succès de process ne masquant pas un rouge ; `VERIFIER_TIMEOUT`/`VERIFIER_START` et continuation du lot suivant ; budget collectif 120 s borné ; refus du contexte hors conteneur ; parseur PowerShell gardant le rouge séparé et fermé ; un paquet rouge ne change jamais la ligne `REJEU` ni le code de sortie.

## 4. Sécurité et données

- Isolation T-01 préservée et vérifiée (ma sortie + assertions `Assert-T01Isolation` + test d'intégration) : `network=none`, rootfs ro, `cap-drop ALL`, `no-new-privileges`, user `65534`, limites pids/mémoire/cpus, `tmpfs /tmp` seul en écriture. Les deux montages (`/repo/wp`, `/packet-repo`) sont en lecture seule, source attendue, RW=false avant **et** après. Aucune option assouplie.
- Le second montage `/packet-repo` est la **racine du dépôt** en lecture seule : il expose aussi `relectures/`, `corrections/`, `briefs/`, `docs/` au sous-processus Python du vérificateur. Sans réseau et en lecture seule → pas d'exfiltration ni d'écriture possible. Conforme au brief (« dépôt en lecture seule ») ; surface plus large que les seules preuves nécessaires (point mineur 2).
- Pas de secret ni de donnée réelle lus : les `logs` déclarés sont des `.log` de preuves ; les chemins sont contraints (POSIX relatifs, sous `production/<lot>/` ou `files/rapports/`, sans `..` ni lien ni segment non ASCII).
- Python reçoit `HOME/TMPDIR/XDG_CACHE_HOME=/tmp`, `PYTHONDONTWRITEBYTECODE=1`, pas de shell, stdin `/dev/null`. Les écritures ne peuvent viser que `/tmp`.

## 5. Doctrine

- §3 Git : aucun script ne fait d'opération Git ; `native-copy-proof.ps1` copie sans Git et refuse un dossier de sortie dans le dépôt. Bon.
- Rejouable / idempotence : la commande sans argument redonne le même résultat ; le banc propriétaire jette sa copie et vérifie l'absence du conteneur. Conforme.
- §5 conventions : PHP `declare(strict_types=1)`, Python `sys.dont_write_bytecode` ; rien n'est installé sur Windows ; le Python est ajouté **seulement** au `Dockerfile` existant via `preparer-image.ps1` (l'image a bien tourné, donc Python présent). Matrices natives classique/HPOS/commerciales laissées hors de la commande, dit en une phrase (`CONVENTION.md`, `notes.md`). Conforme.
- Les trois lignes de T-03 sont bien dans le mode d'emploi T-01 `production/T-01/notes.md` (et reprises dans `readme-ajout.txt`, le contrat) ; le test vérifie « exactement trois lignes ». Conforme.

## 6. Études

Sans objet : lot de code/outillage.

## Verdict

**Conforme.** Le mécanisme fait ce que demande le brief, la ligne `REJEU` ne change ni de forme ni de sens, un paquet rouge n'affecte que `PAQUETS`, et les preuves (rejeu vert + mutant d'un octet) sont reproduites. Ce verdict **n'est pas un GO**.

Points classés :

- **Important** — A-20 n'est pas requalifié alors que le brief prévoyait la requalification commune d'A-20→A-25. Son `verify.py` existe mais son `rejeu.json` a été retiré ; il reste hors rejeu « declaration absente ». C'est disclosé et sûr, mais c'est un écart au périmètre attendu.
- **Mineur 1** — Les lots sans déclaration (ex. A-29) n'apparaissent nulle part dans la sortie (ni vérifiés, ni hors rejeu). Un relecteur pressé pourrait croire un lot couvert alors qu'il est simplement non déclaré.
- **Mineur 2** — `/packet-repo` monte toute la racine du dépôt (y compris `relectures/`, `corrections/`, `briefs/`) en lecture seule dans le conteneur, plus large que les preuves strictement nécessaires. Sans risque (ro + sans réseau).
- **Mineur 3** — Les tests de contrat T-03 (`test_paquets.py`, `test_t03_integration.py`) ne sont pas joués par la commande relecteur ; leur vert n'est pas re-prouvé par moi, seulement relu.

## Décisions techniques, défaut proposé

(Questions techniques : Hermès applique le défaut sans attendre, Claude arbitre après coup. Aucune question visuelle, métier ou touchant au réel pour Ced dans ce lot.)

1. **A-20 : requalifier maintenant ou plus tard ?** Défaut proposé : **laisser A-20 hors rejeu avec sa raison nommée** (sûr et visible) et planifier sa requalification sans argument dans un lot suivant, en confirmant qu'elle ne change aucun contrôle ni reçu natif. Ne bloque pas T-03.
2. **Visibilité des lots non déclarés** : défaut proposé : **garder le comportement opt-in tel quel** ; au plus, une phrase dans `CONVENTION.md` précisant que seuls les lots déclarés figurent sur `PAQUETS`.
3. **Largeur du montage `/packet-repo`** : défaut proposé : **laisser tel quel** ; la réduction de surface n'est pas exigée par le brief et le montage est en lecture seule, sans réseau.
