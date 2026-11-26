# Vérification B-04 — 3e tour (après modifications d'Hermès post-vérification)

Rôle : vérificateur. Base de comparaison : l'état `59faebd` (synchro 00:28) lu par
`verification.md`. Diff relu sur `wp/` et `production/B-04` jusqu'à `HEAD` (`fd29679`).
Pas de nouvelle relecture complète : contrôle des seules modifications intervenues
depuis, des tests et des régressions.

Consignes/arbitrages qui justifiaient ces modifications :
`A-FAIRE-2.md:15` (consigne 0) et `docs/arbitrages-2026-11-26.md:37-41` (§B-04).

## 1. Consignes / arbitrages, un par un

**C0a — « correctif du chemin du jeu de test de B-04 » (`A-FAIRE-2.md:15`) ;
arbitrage « il cherchait le thème à un chemin absent du banc… le test est inchangé »
(`arbitrages-2026-11-26.md:41`). → Appliqué.**
- Seule la fixture `imagine-site/tests/b04-status-fixture.php:8-18` change : le chemin
  `dirname(__DIR__, 3)/themes/imagine/inc/catalogue.php` (checkout local) reçoit un
  repli vers le montage source en lecture seule `/repo/wp/themes/imagine/inc/catalogue.php`
  (`:11-14`), et une `RuntimeException` si aucun des deux n'existe (`:15-17`).
- Le test reste inchangé sur le fond : il charge **le vrai** helper livré, jamais une
  copie de test, sans mapping alternatif (`:5`, `:10`). Aucune assertion sautée.
- C'est exactement le besoin du banc canonique T01, qui ne copie que les paquets
  Composer : le thème `imagine` n'est pas copié dans `/tmp/t01`, d'où le repli sur le
  montage `/repo/wp:ro`. Vérifié : la suite passe par ce chemin (voir §2).

**C0b — « Kiosque de B-04 : l'étiquette d'accès reste telle quelle… ne la retire pas
de toi-même » (`A-FAIRE-2.md:15`) ; point 7 conditionnel réservé à Ced, visuel
(`arbitrages-2026-11-26.md:37-39`). → Appliqué (conservé à juste titre).**
- `archive-imagine_numero.php` **inchangé** depuis la vérification précédente (le statut
  d'accès par numéro, `:24`, est conservé).
- `production/B-04/A-VOIR.md:4` confirme : statut kiosque « conservé à l'identique », en
  attente du oui/non de Ced. Conforme à la consigne.

**C0c — sceau/preuve du delta (arbitrage « suite complète verte »,
`arbitrages-2026-11-26.md:41`). → Appliqué.**
- Nouveau sceau du seul delta : `production/B-04/verification-portabilite-c16.json`,
  `sceller-portabilite.py`, `junit-*-portabilite-c16.xml`, `unit-portabilite-c16.json`.
- `A-VOIR.md:7` (addendum) et `PRET` mis à jour : qualification initiale conservée
  (matrices non annoncées rejouées), complément de portabilité ajouté sans redater
  l'ancien sceau. Honnête : le `PRET` dit que seule la fixture de chemin a changé.

**Corrections 1 à 6 de `corrections/B-04.md` — déjà vérifiées au 2e tour. → Toujours
appliquées, code inchangé.**
- Aucun des fichiers cœur B-04 n'a bougé depuis `59faebd` : `Paywall.php`,
  `Decouverte.php`, `inc/catalogue.php`, `single-imagine_numero.php`,
  `archive-imagine_numero.php`, `taxonomy-imagine_thematique.php`, `functions.php`,
  `tests/CatalogueTest.php`, `tests/CatalogueStatusTest.php`, `phpunit.b04.xml`
  (`git diff 59faebd..HEAD` vide sur ces fichiers). Les constats de `verification.md`
  tiennent trait pour trait.

## 2. Résultat des tests

Rejeu lancé exactement comme demandé :
`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`.
**Non refusé, exécuté.** Banc canonique T01 isolé (réseau=none, rootfs=ro, montage
`/repo/wp:ro`, cap-drop=ALL). Dernière ligne :

```
REJEU : 1062 tests, 34271 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

- `imagine-site` (qui porte le paquet rejouable B-04 `CatalogueTest` +
  `CatalogueStatusTest` via la fixture corrigée) : vert dans l'agrégat, 0 échec.
- Le compte (1062 / 34271) est supérieur aux 1040 cités par l'arbitrage de 0 h 45 :
  dérive attendue, due aux tests ajoutés depuis par d'autres lots (C-17/C-18), pas à
  B-04. Toujours 0 échec, 0 erreur, 0 ignoré.

## 3. Régressions / modifications non demandées

- **Aucune régression fonctionnelle** dans le périmètre B-04. Le cœur du calcul de
  droit et du mapping de statut est inchangé.
- **`PdfNumero::privateHeaders()` passée de `private` à `public`**
  (`imagine-site/PdfNumero.php:185`, synchro `60936c7`). Ce fichier est un **contrat
  lu par B-04**, mais ce changement **n'est pas une consigne B-04** : il est imputable
  à **C-17** (`Justificatifs.php:160` et `:238` appellent la méthode ;
  `README.md:227` documente « seule visibilité de cette méthode passée à public »).
  Élargissement de visibilité seul, **aucun changement de comportement** du flux PDF
  (le corps de la méthode est identique, `self::privateHeaders()` toujours appelée aux
  mêmes points `:200`/`:206`). Signalé, sans impact sur B-04, sans réserve.
- Les autres fichiers du diff (`ExtractionsAdmin/Natives/Regles`, `Justificatifs*`,
  `c16/c17/c18`, `parts/mon-compte.php`) relèvent d'**autres lots** menés en parallèle,
  hors B-04 ; non imputables ici. La suite reste verte.

## 4. Verdict

**Prêt pour la clôture.**

Depuis la vérification précédente, seule la fixture de chemin du jeu de test a changé
(C0a) — test inchangé sur le fond, justifié par la consigne 0 et l'arbitrage §B-04 — et
les preuves de portabilité ont été rescellées sans redater l'existant (C0c). Le statut
du kiosque est conservé comme demandé (C0b). Le cœur B-04 et les six corrections déjà
vérifiées sont intacts. Le rejeu T01 passe (1062 tests, 0 échec).

Aucun **problème de fond restant** : le seul point ouvert — l'étiquette d'accès sur le
kiosque — est l'arbitrage **visuel** explicitement réservé à Ced (fusion §7,
`arbitrages-2026-11-26.md:37-39`), déjà tracé et non bloquant ; la consigne 0 ordonne
de le conserver tel quel. Rien à renvoyer à Ced au titre d'un défaut technique.

**Rappel doctrine :** ce verdict n'est pas un GO (§3/§6). La clôture du code appartient
à Claude sur preuves ; la validation visuelle (dont la question kiosque) reste à Ced.
