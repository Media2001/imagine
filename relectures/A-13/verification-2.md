# Vérification A-13 — correctif ciblé (Claude, second passage)

Lot : A-13. Base : `relectures/A-13/verification.md` (premier tour, « Remonte à Ced »),
consigne 0 d'`A-FAIRE.md` du 26/11 4 h 30, arbitrage « A-13 — retour à Hermès »
(`docs/arbitrages-2026-11-26.md`, passage de 4 h).
Méthode : `git diff 7e620640..HEAD` sur `wp/outils/bascule/controler-export(.md)` et
`wp/tests/a13/` ; relance de la suite Python ; relance de la suite PHP.
Poste de contrôle : **Windows, Python 3.14.6, console cp1252** (`preferred`, `stdout`
et `stderr` = `cp1252`, mesuré). Ce n'est pas une relecture complète.

## 1. Consignes et arbitrages concernés

**Instruction 1 (bloquant) — le test fixe lui-même l'encodage de son sous-processus,
pas l'outil. → APPLIQUÉE.**
L'appel `subprocess.run` de `test_repository_output_refused_without_touching_fixture`
reçoit désormais le dict `env={**os.environ, 'PYTHONIOENCODING': 'utf-8', …}`
(`wp/tests/a13/test_controler_export.py:92`), comme les autres appels (`:36`). C'est
exactement le correctif demandé à l'origine. La cause annoncée au premier tour
(enfant en cp1252, parent décodant en UTF-8 → `UnicodeDecodeError`) ne se reproduit
plus.

**Arbitrage « modification non demandée : retirée si inutile, sinon justifiée par un
test, et dire lequel ». → APPLIQUÉE (garde conservé et justifié).**
Le garde-fou `stream.reconfigure(errors='backslashreplace')` est conservé
(`controler-export:293-294`). Hermès dit lequel le justifie
(`production/A-13/LIVRAISON.md:11-17`, `PRET`) : le chemin **succès** sur console
ASCII par `test_console_cp1252_or_ascii_does_not_fail_after_outputs`
(`test_controler_export.py:417`), et le chemin **refus** — le trou signalé au premier
tour — désormais couvert par
`test_console_cp1252_or_ascii_refusal_without_traceback_or_outputs` (`:430`, teste
cp1252 **et** ascii : code 2, stderr échappé, pas de traceback, pas de sortie
écrite). Le garde n'est plus présenté comme le correctif du cas cp1252 : il est
distinct, et prouvé.

**Instruction 4 (mineur) — refuser `types_abonnement_autorises` non vide quand
`type_abonnement` n'est pas mappé ; message français ; test. → APPLIQUÉE.**
`controler-export:101-102` : `Refus('Correspondance : types_abonnement_autorises
exige une colonne type_abonnement mappée.')`. Deux tests :
`test_subscription_type_filter_without_mapped_column_is_refused` (`:259`, refus + pas
de traceback) et `test_empty_subscription_type_filter_allows_unmapped_optional_column`
(liste vide ⇒ champ facultatif non mappé toujours accepté). Doc alignée
(`controler-export.md:62-64`). Aucun mapping vers un produit ajouté.

**Instruction 5 (mineur) — lever le double libellé « Champ obligatoire absent » /
« Adresse postale incomplète ». → APPLIQUÉE (dédoublonné et documenté).**
`controler-export:232` : `if any(not fields[key] and key not in config['obligatoires']
for key in postal_fields)`. Un champ postal obligatoire absent ne porte plus que son
motif précis ; « Adresse postale incomplète » ne subsiste que pour un autre champ
postal manquant **non** obligatoire. Tests : `test_missing_mandatory_postal_field_
has_only_specific_reason` (`:293`, les quatre champs) et `test_other_missing_postal_
field_keeps_generic_reason` (cas mixte : les deux motifs désignent deux absences
distinctes). Doc : `controler-export.md:73-77`.

**Instruction 6 (rappel) — `LIVRAISON.md` dit que `rejouer.ps1` ne couvre pas A-13, et
avec quel Python et quel encodage la suite a tourné. → APPLIQUÉE.**
`LIVRAISON.md:65` : « `wp/tests/rejouer.ps1` ne couvre pas A-13 : c'est la
non-régression PHP. A-13 est validé séparément par sa suite Python. » Le tableau des
cinq contextes (`:36-42`) donne les versions (3.11.15, 3.14.7, 3.14.6) et les
encodages (utf-8 / cp1252, `PYTHONUTF8` 1 et 0). `controler-export.md:96-99` reprend
la séparation.

**Arbitrage question métier (prénom) rangé dans `docs/decisions.md` — défaut : deux
personnes de même nom à la même adresse sont un doublon, signalées toutes deux. →
CONFORME au défaut.** Le défaut ignore le prénom (`doublon_prenom_identique=false`),
et le cas « prénom absent », en réserve au premier tour, a maintenant son test :
`test_same_name_address_missing_firstname_duplicate_by_default` (`:401`).

**Instructions 2 et 3 (IBAN, doublons) — acquises, inchangées.** Conformes au premier
tour ; aucun changement dans leur logique depuis.

## 2. Résultat des tests

Suite Python du lot, sur le poste de contrôle (console cp1252 mesurée, Python 3.14.6) :

```text
python -B -m unittest discover -s wp/tests/a13
→ Ran 46 tests … OK
```

C'est le contexte même qui échouait au premier tour (`UnicodeDecodeError` byte 0xe9).
Il passe maintenant intégralement. La non-reproductibilité selon la locale — l'objet
du bloquant — est levée.

Suite PHP (non-régression globale), commande demandée :

```text
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1
```

Dernière ligne :

```text
REJEU : 1084 tests, 34363 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Réserve inchangée : cette suite est en PHP et ne couvre pas A-13 (en Python) ; elle
prouve la non-régression du reste du dépôt. La preuve d'A-13 est sa suite Python
ci-dessus.

## 3. Régressions et modifications non demandées

- **Dans le périmètre A-13 : aucune.** Les seules modifications de l'outil sont les
  deux demandées (instr. 4 et 5), chacune testée ; les 46 tests passent, y compris
  l'IBAN et les doublons.
- Le `git diff` depuis le premier tour touche aussi d'autres lots (a10, a12, a14,
  a15, a16, `wp/outils/demo/`, `wp/plugins/imagine-site/`, `wp/tests/demo/`) : hors
  périmètre de ce correctif, non examinés ici.
- `LIVRAISON.md` annonce désormais « 46 tests, 0 échec » dans cinq contextes dont
  cp1252 : conforme à ce que je rejoue (46 OK sur console cp1252). L'affirmation de
  reproductibilité, fausse au premier tour, est maintenant exacte.

## 4. Verdict : **Prêt pour la clôture**

Le bloquant du premier tour est résolu : le test fixe lui-même l'encodage de son
sous-processus ; la suite A-13 passe sur le poste de contrôle (cp1252). Les deux
mineurs (instr. 4 et 5) et le rappel (instr. 6) sont appliqués, testés et documentés.
La modification non demandée de l'outil est conservée **avec** le test qui la
justifie, chemins succès et refus, et dite comme telle. IBAN et doublons restent
conformes.

---

*Rappel doctrine §6 : ce verdict n'est pas un GO. Le marqueur `production/A-13/PRET`
et le déploiement relèvent de Ced. Rien de réel n'a été touché.*
