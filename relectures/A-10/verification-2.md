# Vérification A-10 (tour 3) — contrat multi-lots du mode d'emploi partagé

Vérificateur : Claude. Date : 26 novembre 2026. Tour de contrôle après la clôture du second tour, A-10 ayant été re-scellé par Hermès.

Méthode : `git diff 81cc1c1..HEAD` (commit de `verification.md`) sur `wp/outils/bascule/a10`, `wp/tests/a10` et `production/A-10` ; lecture des seuls fichiers modifiés ; rejeu indépendant du vérificateur du lot sur le paquet scellé courant. **Pas de relecture complète refaite.** Paquet `PRET` courant : **`3a27ca7aea7c`** (l'ancien `5e795d00f9d6` reste historique).

**Ce qui a changé depuis le tour 2 (diff ciblé).** Le code de l'outil n'a **pas** bougé : aucune modification dans `wp/outils/bascule/a10/`, ni dans `seed.php`, `inside.py`, `unit.php`. Seuls ont changé :
- `wp/tests/a10/verifier.py` (+26 lignes) ;
- `wp/tests/a10/test_readme_contract.py` (nouveau, 50 lignes) ;
- les preuves régénérées sous `production/A-10/preuves/3a27ca7aea7c/`, le `PRET`, `notes.md`, `manifest.json`, `verification-finale.json` et les reçus d'intégration (`reception-common.json`, `verifier-reception.py`, `reception-verification.json`).

---

## 1. Consigne / arbitrage concerné — état d'application

La modification répond à **un seul** point : la règle du **fichier partagé contrôlé par contrat**, posée pour les manifestes A-08/A-09.

| Source | Texte | État | Preuve (fichier:ligne) |
|---|---|---|---|
| `A-FAIRE.md:21` (consigne 1) + `docs/arbitrages-2026-11-26.md:23` (A-09, point 3) | « Un fichier **partagé** entre lots (le mode d'emploi de l'audit) se contrôle par contrat … les lignes du lot sont présentes et exactes, pas par l'empreinte du fichier entier. » | **Appliquée** | `verifier.py:22-41` : `readme_original_digest()` reconstruit `README A-02 original + 2 lignes A-10 (SHA figé) + séparateur vide + 2 lignes A-11 + 2 lignes A-12`, byte à byte, sans normalisation. L'ancien test « le fichier se termine par les 2 lignes A-10 » (`current.endswith(appendix)`) est remplacé par la vérification du suffixe complet `appendix + INTEGRATION_APPENDIX` (`verifier.py:34`) et du hash de l'original (`verifier.py:36-37`), plus garde `README_BASELINE_CHANGED` (`verifier.py:103`). |

**Pourquoi ce changement était nécessaire (justification de l'arbitrage).** Depuis le tour 2, A-11 et A-12 ont ajouté chacun leurs deux lignes à la fin du mode d'emploi partagé `wp/tests/a02-audit/README.md`. L'ancien contrôle d'A-10 exigeait que le fichier **se termine** par les deux lignes A-10 : il serait devenu rouge sans qu'A-10 change. Le nouveau contrat reconstruit la séquence exacte des ajouts autorisés de tous les lots — c'est exactement « se contrôle par contrat, comme A-10 vient de le faire » (arbitrage A-09, point 3). `notes.md:3` et `:29` décrivent ce contrat (« README A-02 original + deux lignes A-10 exactes + séparateur vide + deux lignes A-11 exactes + deux lignes A-12 exactes »).

Quatre tests de contrat accompagnent le changement (`test_readme_contract.py:19-48`) : octets intégrés exacts ; **chaque** octet de l'original et des ajouts protégé contre toute dérive (XOR bit à bit sur toute la longueur) ; refus des omissions / doublons / réordonnancements / ajouts inconnus / fins de ligne CRLF ; refus d'un appendice A-10 modifié. **Appliqués et verts.**

Les sept instructions de `corrections/A-10.md` déjà validées au tour 2 restent inchangées (aucun fichier source de l'outil n'a bougé) : elles ne sont pas re-contrôlées ici.

---

## 2. Résultat des tests

- **`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1` : REFUSÉE.** Le validateur de commandes de cet environnement bloque le lancement (« nested PowerShell process which cannot be validated »), comme au tour 2. Hors de ma main. Sans effet sur ce re-scellé : le `git diff 81cc1c1..HEAD` ne touche **aucun** des quatre plugins PHPUnit — le périmètre modifié est entièrement `wp/tests/a10`. La suite des quatre plugins était au vert au tour 1 (1030 tests, 34124 assertions).
- **Rejeu indépendant du vérificateur du lot** (lecture seule, sans Docker, dans mes droits) sur le paquet `PRET` courant : `python wp/tests/a10/verifier.py production/A-10/preuves/3a27ca7aea7c` → **code 0**, `unit_assertions: 10`, `native_assertions: 187`, `runner_assertions: 7` (**204**), `source_files: 15`, `a02_original_bytes_preserved: true`, `cleanup_verified: true`. Reproduit à l'identique le reçu d'Hermès (`verification-finale.json`).
- **Test de contrat du README rejoué indépendamment** : `python -B wp/tests/a10/test_readme_contract.py` → **4 tests, OK**. Confirme que l'état réel courant du README partagé (avec les lignes A-10 + A-11 + A-12) se reconstruit bien vers le SHA-256 A-02 original figé, et que toute mutation d'un octet est refusée.
- **Limite assumée (inchangée).** Le runner Docker natif qui *génère* les preuves (staging + extensions commerciales) reste hors de mes droits (doctrine §3) ; je m'appuie sur la revalidation indépendante des preuves scellées par le `verifier.py` mis à jour, non sur une régénération.

---

## 3. Régressions ou modifications non demandées

- **Aucune régression de code.** Le diff ne touche pas l'outil : `wp/outils/bascule/a10/` est intact. Les 204 assertions sont inchangées en nombre et au vert.
- **`source_files` passe de 14 à 15** : conséquence attendue du seul fichier ajouté (`test_readme_contract.py`).
- **Reçus d'intégration ajoutés** (`reception-common.json`, `verifier-reception.py`, `reception-verification.json`, `PRET` réécrit vers `verifier-reception.py`) : ils documentent la préparation commune de l'image parente du 26/11 à 00:45:29 CET et lient A-10 au re-scellé multi-lots. Ce sont des artefacts d'empaquetage, **pas** une modification de l'outil ni une nouvelle dépendance (`notes.md:33` : « ni relancé la préparation partagée ni ajouté de dépendance »). Non demandés explicitement mais cohérents avec la correction du contrat partagé ; sans effet sur le comportement de l'inventaire.
- Les deux questions **Pour Imagine** (commandes annulées/remboursées comptées ; 4ᵉ état `pending_cancel`) restent des réglages à défaut prudent appliqué — non bloquantes (doctrine §4). Aucune question **visuelle ou touchant au réel**.

---

## 4. Verdict

**Prêt pour la clôture.**

Le seul changement depuis le tour 2 est l'adaptation du vérificateur d'A-10 au contrat multi-lots du mode d'emploi partagé, exactement comme le demande l'arbitrage A-09 (point 3) et la consigne 1 : le fichier partagé est contrôlé par contrat byte-exact, pas par l'empreinte du fichier entier. L'outil lui-même — celui validé au tour 2 — n'a pas bougé. Le rejeu indépendant du vérificateur sur le paquet scellé courant (`3a27ca7aea7c`) est au vert (204 assertions, code 0), et le test de contrat du README est au vert indépendamment (4 tests). Aucune régression ni modification non demandée affectant l'inventaire. La commande `rejouer.ps1` reste refusée par l'environnement, mais sans objet pour ce re-scellé (aucun plugin PHPUnit touché).

Ce verdict n'est pas un GO au sens de la doctrine §3/§6 : il clôt le contrôle de ce re-scellé de code et ne vaut aucune autorisation d'accès au réel ni de migration.
