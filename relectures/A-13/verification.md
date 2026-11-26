# Vérification A-13 — second et dernier tour (Claude)

Lot : A-13. Base : `corrections/A-13.md` (fusion), code corrigé par Hermès.
Méthode : `git diff 20cf7e3..HEAD` sur `wp/outils/bascule/`, `wp/tests/a13/`,
`production/A-13/` ; relance de la suite Python sur ce poste.
Poste de contrôle : **Windows, Python 3.14.6, locale cp1252** (identique à celui de Ced).

Ce n'est pas une relecture complète : je vérifie seulement l'application des six
instructions, je relance les tests, je note les régressions.

## 1. Instructions de `corrections/A-13.md`

**1 — (Bloquant) Ajouter le dict `env={… PYTHONIOENCODING: utf-8 …}` à l'appel
`test_controler_export.py:89-90`. « Aucune modification de l'outil. »
→ NON APPLIQUÉE.**
L'appel visé est toujours là (`test_controler_export.py:90-91`,
`test_repository_output_refused_without_touching_fixture`) et **n'a toujours pas**
le dict `env=`. Hermès a choisi une autre voie : il a **modifié l'outil**
(`controler-export:287-290`, `stream.reconfigure(errors='backslashreplace')`) et
ajouté un test `test_console_cp1252_or_ascii_does_not_fail_after_outputs`
(`test_controler_export.py:352-369`). Mais ce nouveau test ne couvre que le chemin
de **succès** (code 0, `stderr` vide) ; il ne couvre pas le chemin de **refus**, où
`stderr` accentué (« REFUS : … dépôt … ») est relu en UTF-8 par le parent. Or c'est
exactement ce cas qui casse. Sur cp1252, l'enfant écrit « é » en 0xE9 (parfaitement
encodable, donc `backslashreplace` ne se déclenche jamais), et le parent décode ce
0xE9 en UTF-8 → plantage. **Le bloquant est intact** (voir § 2).

**2 — (Important) Durcir le précontrôle IBAN sur une représentation normalisée, sans
concaténer les colonnes ni restituer de valeur ; tests pour `ZZ00.0000…` et U+200B.
→ APPLIQUÉE.**
`controler-export:27-31` : sonde par cellule via `NFKC`, retrait des espaces, de la
ponctuation (`P*`) et des caractères de format (`Cf`), sans toucher la source et sans
joindre les colonnes. Tests ajoutés et au vert :
`test_iban_typographic_variants_in_one_unmapped_cell` (points, U+200B, U+202F, point
médian, pleine chasse) et `test_iban_scan_never_joins_two_columns`
(`test_controler_export.py:313-334`). Doc mise à jour `controler-export.md:32`.

**3 — (Important) Rapprocher les doublons « nom + adresse » par défaut sans le prénom ;
option « prénom identique » désactivée par défaut ; tests ; mettre à jour le .md.
→ APPLIQUÉE.**
`controler-export:238-239` : clé = `('nom',)` par défaut, `('nom','prenom')` seulement
si l'option est vraie. `lire_config:80-82` pose le défaut `False` (y compris si la clé
est absente d'une ancienne config) et refuse une valeur non booléenne. Exemple mis à
jour (`a13/correspondance.exemple.json:24`). Doc mise à jour (`controler-export.md:65`).
Tests au vert : `test_same_name_address_different_firstname_duplicate_by_default` et
`test_explicit_firstname_duplicate_option_is_off_by_default`
(`test_controler_export.py:343-351`). Réserve mineure : l'instruction demandait aussi
un test « prénom absent » ; il n'y en a pas de distinct, mais le défaut ignore le
prénom, donc le cas est couvert par construction. Le défaut conforme au brief est bien
livré ; la question métier (§ 5 de la fusion) reste ouverte pour Ced, comme prévu.

**4 — (Mineur) Refuser une correspondance où `types_abonnement_autorises` est non vide
alors que `type_abonnement` n'est pas mappé ; message français ; test.
→ NON APPLIQUÉE.**
Aucun contrôle de ce genre dans `lire_config` : `type_abonnement` n'est pas ajouté à la
liste des colonnes nécessaires (`controler-export:107`) et aucune condition ne rejette
la combinaison contradictoire. Aucun test ajouté pour ce cas. Le filtre reste donc
silencieusement inopérant si la colonne n'est pas mappée (`controler-export:248`,
`fields['type_abonnement']` vaut `''`).

**5 — (Mineur) Lever l'ambiguïté « Champ obligatoire absent » / « Adresse postale
incomplète » quand un champ postal est obligatoire : dédoublonner ou documenter.
→ NON APPLIQUÉE.**
`analyser` émet toujours les deux motifs indépendamment (`controler-export:207-209` et
`:228-229`). `controler-export.md` ne documente nulle part ce double libellé possible.
Ni dédoublonnage, ni mention.

**6 — (Rappel) Mentionner dans `LIVRAISON.md` que `rejouer.ps1` (PHP) ne couvre pas
A-13, validé à part par sa suite Python une fois le point 1 corrigé.
→ PARTIELLEMENT.**
`LIVRAISON.md` indique bien « Aucun test PHP global … n'est revendiqué » et renvoie à
`wp/tests/a13/verifier_livraison.py`. Mais la formulation explicite « rejouer.ps1 ne
couvre pas A-13 » n'y est pas, et le rappel est de toute façon privé d'objet puisque le
point 1 n'est pas corrigé.

## 2. Résultat des tests

Suite Python du lot, sur le poste de contrôle (cp1252, Python 3.14.6) :

```text
python -m unittest discover -s wp/tests/a13 -v
→ Ran 40 tests … FAILED (errors=1)
```

Le test en échec est `test_repository_output_refused_without_touching_fixture`
(`:90-91`), avec **exactement** la cause annoncée par la fusion :

```text
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 25
  (thread lecteur de subprocess)
→ result.stderr devient None
→ assert_refused : TypeError: can only concatenate str (not "NoneType") to str
```

La preuve livrée par Hermès (`production/A-13/verification.tests.txt`) affiche
« Ran 40 tests … OK » : c'est son environnement (Python 3.11.15), pas le poste de
contrôle. **La non-reproductibilité selon la locale — l'objet même du bloquant — est
toujours là.** La clôture ne peut pas s'appuyer sur « tests au vert » (doctrine §4, §6).

Je n'ai pas relancé la suite PHP `rejouer.ps1` : elle ne couvre pas A-13 et la fusion
ne la mettait pas en cause.

## 3. Régressions et modifications non demandées

- **Modification de l'outil non demandée, et inefficace sur la cible.** L'instruction 1
  disait « aucune modification de l'outil » ; Hermès a ajouté
  `reconfigure(errors='backslashreplace')` dans `main` (`controler-export:287-290`).
  Sur ASCII elle évite un plantage à l'écriture, mais sur **cp1252** (le poste de Ced)
  elle ne change rien : le bloquant persiste. Ce n'est pas une régression du contrôle
  métier, mais un correctif qui ne traite pas le cas visé.
- **`LIVRAISON.md` affirme « 40 tests exécutés, 0 échec ».** Faux sur le poste de
  contrôle (1 erreur). L'affirmation de reproductibilité est donc inexacte.
- **Section « Intégration reçue » de `LIVRAISON.md` réécrite ; `reception-verification.json`
  et `.tests.txt` supprimés.** Hors du périmètre des corrections demandées. Sans effet
  sur le code, mais à signaler : les anciennes preuves de réception ne sont plus dans le
  dépôt.
- Aucune régression dans la logique de contrôle elle-même : les 39 autres tests passent,
  les changements IBAN (instr. 2) et doublon (instr. 3) sont corrects et testés.

## 4. Verdict : **Remonte à Ced**

Problème de fond restant : **le bloquant de la fusion n'est pas résolu**. Instruction 1
mal appliquée (l'outil a été modifié au lieu du test, et la modification ne corrige pas
le cas cp1252) ; la suite A-13 échoue sur le poste de contrôle avec l'erreur même que la
fusion avait décrite. S'y ajoutent deux mineurs non appliqués (instr. 4 et 5) et un
rappel seulement partiel (instr. 6).

Ce n'est pas « prêt pour la validation de Ced ». La correction est à mes yeux simple
(ajouter le dict `env=` à l'appel `:90-91`, comme demandé à l'origine), mais c'est à
Ced de décider : renvoyer à Hermès pour un correctif ciblé, ou accepter en connaissance
de cause. Instructions 2 et 3 : conformes et testées.

---

*Rappel doctrine §6 : ce verdict n'est pas un GO. Le marqueur `production/A-13/PRET` et
le déploiement relèvent de Ced.*
