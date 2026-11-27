# Resultats mesures A-28 apres fusion

2026-11-27T02:51:15.329249+00:00 ; Python Windows 3.14.6 ; UTF-8/mode 1 et cp1252/mode 0 mesures dans les recus.

| Contexte | Controles natifs | Cas import/refus | PHP A28 | A01 donnees | Lint PHP | Mutations tables/posts | Mutations postmeta orphelins |
|---|---:|---:|---:|---|---:|---:|---:|
| utf8 | 190, 0 echec | 10 | 82 | 9 cas / 337 assertions | 16 | 16 | 2 |
| cp1252 | 190, 0 echec | 10 | 82 | 9 cas / 337 assertions | 16 | 16 | 2 |

Les repetitions entre encodages ne sont pas des cas uniques supplementaires. Les nouveaux temoins omettent uniquement la purge postmeta lors du vrai import : parents/revisions connus absents, quatre lignes de meta et quatre identifiants de provenance, refus 1 / controle retire 0 / controle retabli 1. Aucun texte canari publie.

PSR-12 strict en conteneur : 7 fichiers, 0 erreur, 0 avertissement, aucune exclusion. Les declarations ont leurs fichiers distincts ; equivalence native des jetons de mise en forme dans `preuves/final/format-equivalence.json`.

## Portes

- `environment-utf8` : sortie 0 ; sources propres stables.
- `python-utf8` : sortie 0 ; 19 tests ; sources propres stables.
- `a01-windows-utf8` : sortie 0 ; 109 tests ; sources propres stables.
- `environment-cp1252` : sortie 0 ; sources propres stables.
- `python-cp1252` : sortie 0 ; 19 tests ; sources propres stables.
- `a01-windows-cp1252` : sortie 0 ; 109 tests ; sources propres stables.
- `psr12` : sortie 0 ; sources propres stables.
- `prepare-image` : sortie 0 ; sources propres stables.
- `global-utf8` : sortie 0 ; sources propres stables.
- `global-cp1252` : sortie 0 ; sources propres stables.

utf8 :

```text
PAQUETS : 0 vérifiés, 0 échecs ; hors rejeu : A-26 (declaration absente), A-27 (declaration absente), A-28 (declaration absente)
OUTILS : 21 outils, 553 contrôles, 0 échecs ; hors rejeu : aucun
REJEU : 1151 tests, 36062 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

cp1252 :

```text
PAQUETS : 0 vérifiés, 0 échecs ; hors rejeu : A-26 (declaration absente), A-27 (declaration absente), A-28 (declaration absente)
OUTILS : 21 outils, 553 contrôles, 0 échecs ; hors rejeu : aucun
REJEU : 1151 tests, 36062 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

A01 Python natif : 109 tests par encodage, le cas NTFS est ignore sous Linux mais joue dans chaque porte Windows. Les trois complements PHP A01 et le differentiel hors formulaires ont chacun leur vraie sortie 0. Le differentiel conserve toutes les tables et le rapport ancien, hors compteur zero ajoute par A28.

Gel identique des matrices et portes : 50 fichiers strictement import/A28/reference, pas un inventaire global concurrent. Sources comparees aux recus apres execution. Les communs T03 sont seulement observes avant chaque porte dans `*.common-observed.json` ; aucun lot voisin n'est requalifie ici.

Baseline anterieure A28 : 108 controles historiques, pas une qualification actuelle. Ancien paquet complet intact hors depot : `historical-preservation.json` verifie ses empreintes. Un seul nouveau paquet dans `preuves/final`.

Runners finaux supprimes, absence verifiee : `imagine-test-a28-56a6753730e3`, `imagine-test-a28-1fb6556bbc8d`, `imagine-test-a28-style-897c7ef6d1d4`. Aucun site ou archive reelle utilise.
