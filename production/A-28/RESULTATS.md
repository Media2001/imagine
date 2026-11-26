# Résultats mesurés A-28

2026-11-26T23:52:30.346329+00:00 ; Python Windows 3.14.6 ; consoles UTF-8/mode 1 et cp1252/mode 0 effectivement mesurées.

| Contexte | Contrôles import | Cas complets/refus | Tests purs PHP A28 | A01 données | Lint PHP | Mutations réelles | Refus CLI garder | Commandes du runner |
|---|---:|---:|---:|---|---:|---:|---:|---:|
| utf8 | 172, 0 échec | 8 | 62 | 9 cas / 337 assertions | 12 | 16 | 12 | 9, toutes sortie 0 |
| cp1252 | 172, 0 échec | 8 | 62 | 9 cas / 337 assertions | 12 | 16 | 12 | 9, toutes sortie 0 |

Les décomptes répétés entre consoles ne sont pas des tests uniques supplémentaires. Chaque mutation est le triplet réel refus 1, contrôle retiré 0, contrôle restauré 1 ; chaque garder connu est refusé par le CLI PHP à 78. Les archives sont entièrement fabriquées dans les conteneurs ; le code de restauration, le SQL et les trois phases natives sont ceux de staging-court.

Avant correction : 108 contrôles du défaut sur six imports (défaut puis garder table connue/inconnue, classique/HPOS). Preuve et sources anciennes authentiques conservées, pas présentées comme la qualification actuelle.

## Portes Windows et globales

- `environment-utf8` : sortie réelle 0 ; sources stables.
- `python-utf8` : sortie réelle 0 ; 17 tests ; sources stables.
- `a01-windows-utf8` : sortie réelle 0 ; 109 tests ; sources stables.
- `environment-cp1252` : sortie réelle 0 ; sources stables.
- `python-cp1252` : sortie réelle 0 ; 17 tests ; sources stables.
- `a01-windows-cp1252` : sortie réelle 0 ; 109 tests ; sources stables.
- `prepare-image` : sortie réelle 0 ; sources stables.
- `global-utf8` : sortie réelle 0 ; sources stables.
- `global-cp1252` : sortie réelle 0 ; sources stables.

utf8 :

```text
OUTILS : 20 outils, 521 contrôles, 0 échecs ; hors rejeu : aucun
REJEU : 1151 tests, 36062 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

cp1252 :

```text
OUTILS : 20 outils, 521 contrôles, 0 échecs ; hors rejeu : aucun
REJEU : 1151 tests, 36062 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

La suite A01 Python complète est également exécutée dans chaque runner : 109 tests par contexte, avec le cas NTFS réservé à Windows déclaré ignoré dans Linux et réellement joué sous Windows. Les trois compléments PHP A01 (politique, diagnostic PDO sur une vraie contrainte unique, fichiers) sont chacun à sortie 0. Le différentiel hors formulaires est byte-identique entre les sources anciennes et actuelles, sauf le nouveau compteur zéro explicitement isolé.

Gel identique pour matrices et portes : 45 fichiers import/tests/vérificateur/référence, toutes les empreintes relues après exécution. Les logs bruts, véritables statuts et empreintes internes figurent dans `preuves/final/native`, `preuves/final/gates` ; aucun reçu ancien remplacé pour cacher une dépendance modifiée.

Runners finaux supprimés et absence relue : `imagine-test-a28-982fac8b70f1`, `imagine-test-a28-9314c96183a1`. La baseline et les essais rouges ont leur propre preuve de suppression. Aucun runner partagé, site ou archive réelle n’a été utilisé.
