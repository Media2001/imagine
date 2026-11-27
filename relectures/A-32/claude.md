# Relecture A-32 — La tournée des inventaires (Claude, relecteur indépendant)

Date : 2026-11-27. Brief : `briefs/A-32-la-tournee-des-inventaires.md`. Cahier des charges : §4.3, §4.4.
Code relu : `wp/outils/bascule/tournee/` et `wp/tests/a32/`. Preuves : `production/A-32/`.
`relectures/A-32/codex.md` **non ouvert**. Fusion **non faite** (voir fin).

## 1. Conformité

Globalement conforme au brief. Points vérifiés, favorables :

- Ordre fixe des quinze outils clos, liste fermée dans un fichier du lot : `tournee/outils.jsonl` (A-10, A-11, A-12, A-15 à A-21, A-23 à A-27). `entries()` interdit les doublons de lot et exige que chaque commande figure mot pour mot dans le mode d'emploi de l'outil (`tournee.py:29-38`). Ajouter un outil = une ligne. Conforme.
- Commande exacte de chaque mode d'emploi : `command()` ne change que l'absolu de l'entrée et les chemins opérateur (`--wp-path/--audit/--correspondance/--output`), et préserve les littéraux (`--limit=10` d'A-16, `--as-of` d'A-19) (`tournee.py:41-48`). Conforme.
- Exclusions nommées avec raison fermée : `tournee/exclusions.json` + `tournee/README.md:34` (A-02/A-03 prérequis, A-04/A-05/A-08 mutantes, A-09 plan, A-13/A-14/A-30 fichier Imagine, A-22 gardien, A-28 import, A-29/A-31 non clos). Conforme.
- Continue après refus/échec, sort en erreur au moindre incident : `run()` capture chaque outil, poursuit, puis `return int(failed)` (`tournee.py:141-151`). Conforme.
- Bilan hors dépôt, statuts/codes fermés, aucun nombre ni nom tiré du site : `classify()` et `publish()` ne recopient que lot, statut, code de refus ou entier de sortie et chemin opérateur (`tournee.py:58-67, 130-139`). Vérifié sur les preuves (voir §2). Conforme.
- Bilan partiel jamais présenté comme complet : `publish(False)` est écrit avant la boucle et après chaque outil ; seul le dernier `publish(not failed)` peut écrire « complète » (`tournee.py:140-150`). Conforme.
- Standard d'abord : argumentaire présent (la tournée ne rejoue aucune étape d'A-08, lecture seule uniquement) — `tournee/README.md:3-7`. Conforme.

**Point important 1 — garde de tournée vs « les outils refusent ».** `tournee.py:70-107` ajoute `verified_site()` : la tournée refuse globalement (`A32_NOT_VERIFIED`, stdout vide, aucun outil lancé, aucun bilan) si le marqueur `.imagine-staging-verified.json` ou `WP_ENVIRONMENT_TYPE=staging` ne convient pas. Or le brief dit : « n'ajoute et ne retire aucun contrôle d'accès : ce sont les outils qui refusent un site non vérifié, la tournée rapporte leur refus ». Ici, sur un site non vérifié, **aucun bilan n'est produit et aucun outil n'est nommé**, au lieu que chaque outil refuse et soit listé. Le choix est défendable (doctrine §3 « dans le doute sur un droit d'accès, fermé » ; éviter de lancer quinze sous-processus contre un site possiblement réel), et le marqueur recopie fidèlement la règle A-05 (`a05/clean.py:210-211` : `status=verified`, `offline_verified is True`, `runtime_probe_passed is True`). Mais c'est une **interprétation qui s'écarte du texte du brief sans être signalée comme telle** (grille §1). Le RAPPORT la présente comme un acquis (« garde initiale A-05 recopiée ») sans noter la tension. Voir question technique ci-dessous.

**Point important 2 — README commun obsolète.** `wp/outils/bascule/README.md:18` affirme « La tournée inclut A-10, A-11, A-12, A-15 à A-21, A-23 à A-25 » et « A-26/A-27/A-29/A-31 ne sont pas clos ». C'est **faux aujourd'hui** : `outils.jsonl` inclut A-26 et A-27, et les preuves les exécutent (réussis). Le RAPPORT (`RAPPORT.md:19`) reconnaît la phrase « historiquement obsolète » mais la laisse en place, au motif du périmètre d'écriture. L'argument est faible : la section §A-32 de ce même fichier est bien éditée par le lot (lignes de contrat A32-CONTRAT/A32-BILAN présentes). Un opérateur qui suit le README commun exclura A-26/A-27 à tort. Correction : mettre à jour (ou retirer) cette phrase pour refléter la liste courante.

## 2. Exactitude métier (déroulé à la main)

Déroulé du code confronté aux preuves committées.

- **Cas nominal (tournée complète).** `run()` → `verified_site` OK → 15 entrées → boucle, chaque outil réussi → `failed=False` → `publish(True)` → `return 0` → `main` imprime `A32_COMPLETE bilan.json bilan.md`. Confirmé par `preuves/final/utf8/native/classic-complete/bilan.json` : `tournee: "complète"`, 15 `réussi`, chemins opérateur seuls. Conforme.
- **Cas refus + échec (doubles nommés A-10/A-11).** A-10 → `refusé (A10_AUDIT_GUARD)` ; A-11 → `en échec (255)` ; 13 autres `réussi` ; `partielle` ; exit 1. Confirmé par `classic-named-doubles/bilan.md`. Les deux doubles sont déclarés comme tels (`classic-doubles.json`). Conforme.
- **Cas limite — site non vérifié.** Marqueur absent/invalide/champs faux ou `production` → `A32_NOT_VERIFIED`, 0 outil, 0 sortie, base et fichiers inchangés (preuves `*-unverified-*-proof.json`, audit Python du vrai exécuteur : `tools_launched: 0`). Comportement vérifié — mais voir point important 1 (absence de bilan).
- **Cas limite — interruption.** Le bilan reste « partielle » tant que la boucle n'est pas finie (publish systématique). Une interruption ne peut laisser une déclaration « complète ». Conforme.
- **Cas limite — événement rejoué / sortie existante.** `output.exists()`/symlink → `A32_OUTPUT_UNSAFE` ; sorties suffixées préexistantes → `A32_OUTPUT_EXISTS` (`tournee.py:114-121`). Pas d'écrasement : un rejeu exige un dossier neuf. Correct pour une preuve en lecture seule.
- **Classification des refus — pas de trou.** `allowed_messages()` = gardien commun (`stream_refusals.json`, qui couvre A-15 à A-19) ∪ `tournee/refusals.json` (A-10, A-12, A-20 à A-27) ∪ A-11 dans les deux. Couverture des quinze outils vérifiée à la main. Un refus légitime est donc bien classé « refusé » avec son code, pas « en échec ». Bon.

## 3. Tests

**Rejeu PHP autorisé** (commande sans argument) :

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1
```

Conteneur jetable, réseau coupé, dépôt en lecture seule. Dernière ligne :

```
REJEU : 1204 tests, 36667 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Ligne outils associée : `OUTILS : 22 outils, 829 contrôles, 0 échecs ; hors rejeu : aucun`.
Le `T01_RESULT` vérifie aussi les paquets : A-32 est dans `packets.lots` avec `failures: []` ; A-31 est **exclu** (`"reason":"journaux absents"`). Voir point important 3.

Portée : la suite PHP valide la chaîne d'outils PHP et la vérification du paquet A-32, mais **ne rejoue pas** les tests Python propres d'A-32 (`test_tournee.py`, `test_delivery.py`) ni la matrice native (Docker/Linux, lourde). Je ne les ai pas relancés — hors de l'unique commande autorisée. Je les ai **relus** : la matrice committée (`windows-matrix.json`) sort 0 sur les deux consoles, dix tests Python verts par console, bench natif classique/HPOS (immuabilité base/fichiers, sept canaux de fuite, zéro sous-processus sur site non vérifié, canaris absents) — les tests vérifient la règle, ils ne répètent pas le code. Couverture des cas limites satisfaisante.

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle : fixtures synthétiques, bilans ne contenant que statuts/codes/chemins opérateur. Canaris (`PRIVATE_CANARY`, numéros fictifs) absents du bilan et de chaque canal — vérifié par le bench (`clean`) et par lecture directe des bilans.
- Robustesse de lecture : `verified_site()` borne les fichiers à 16 Mio, refuse les liens symboliques, et lit `wp-config.php` sans exécuter PHP (purge des commentaires sans toucher aux chaînes). Bon.
- Paywall : sans objet (outil de bascule en lecture seule, hors web, pas de rendu d'article).

## 5. Doctrine

- Standard d'abord : respecté (tournée distincte d'A-08, aucun outil/gardien/lanceur modifié). `scope-readback.json` atteste 239 fichiers protégés identiques ; gel des outils respecté.
- Conventions : A-32 est en Python (hors du périmètre PHP 8.2/`strict_types`) ; code PEP cohérent, préfixes `A32_` pour les codes globaux. Textes en français. Conforme à l'esprit du §5.
- Rejouable / non-régression : la tournée ne mute rien ; bench prouve base et fichiers inchangés avant/après. Conforme.

**Point important 3 — écart PRET A-32 vs A-31 (vérification).** `production/A-32/PRET` existe (déposé 19:30) et affirme « A-31/A-32 effectivement vérifiés, aucun échec de paquet », s'appuyant sur une réception hors dépôt. Or le rejeu indépendant **actuel** exclut A-31 (« journaux absents ») : A-31 a un `manifest.json` mais pas de `PRET`, et n'est pas vérifié par la suite. La condition posée par le propre `FINALISATION.md` du lot (« rejeu indépendant où A-31 et A-32 sont effectivement vérifiés, non exclus, exigé avant PRET ») **n'est donc pas reproductible maintenant**. Cela touche la réception d'A-31 et le dépôt du PRET, qui sont du ressort du parent et hors de mon périmètre d'écriture : je le signale, je n'y touche pas.

## 6. Études

Sans objet (lot de code).

## Verdict

**À corriger** — le cœur du code et les preuves sont solides ; les réserves portent sur la signalisation d'une interprétation, une doc commune obsolète, et un écart d'état PRET/A-31.

- **Bloquant** : aucun.
- **Important** :
  1. Garde de tournée `verified_site()` qui s'écarte du « les outils refusent un site non vérifié » du brief, sans être signalée comme interprétation (`tournee.py:70-107`).
  2. `wp/outils/bascule/README.md:18` obsolète : exclut A-26/A-27 alors que la tournée les inclut.
  3. Écart : `production/A-32/PRET` présent alors que le rejeu indépendant actuel exclut A-31, contre la précondition de `FINALISATION.md`.
- **Mineur** :
  - La commande documentée d'A-16 porte `--limit=10`, copiée telle quelle (correct vis-à-vis du brief) ; confirmer seulement qu'un inventaire plafonné est bien l'intention en migration (concerne A-16, pas A-32).
  - `tournee/README.md:40` déclare la phrase d'exclusion A-26/A-27 « remplacée » alors qu'elle subsiste dans le README commun — hygiène documentaire.

Ce verdict n'est pas un GO (doctrine §6).

## Décisions techniques, défaut proposé (Hermès applique, Claude arbitre après coup)

1. **Garde de tournée.** Défaut : conserver `verified_site()` (plus sûre), mais ajouter une ligne au RAPPORT signalant qu'elle s'écarte du texte du brief (refus global vs refus outil par outil) et que, sur site non vérifié, aucun bilan n'est produit — comportement assumé.
2. **README commun.** Défaut : corriger `wp/outils/bascule/README.md:18` pour que la liste incluse mentionne A-26/A-27 et retire « A-26/A-27 … ne sont pas clos » (une phrase).

## À arbitrer par Ced (touche à la réception)

1. Le PRET d'A-32 doit-il être suspendu tant que le rejeu indépendant n'affiche pas **A-31 et A-32 tous deux vérifiés, sans exclusion** ? — Défaut prudent proposé : **oui** (suspendre le PRET jusqu'à un rejeu conjoint vert), conformément à `FINALISATION.md`.

---

`codex.md` n'a pas été ouvert ; la fusion (`corrections/A-32.md`) n'est pas écrite, comme demandé. Je m'arrête ici.
