# Vérification A-16 — second et dernier tour

Vérificateur indépendant. Base : `corrections/A-16.md` (5 instructions), brief `briefs/A-16-dix-derniers-numeros.md`, doctrine.
Méthode : `git diff` de la version relue (commit `3b429159`, 06h48) à HEAD sur `wp/` et `production/A-16`, puis rejeu des tests accessibles en local. Pas de relecture complète refaite.

## 1. Instructions de `corrections/A-16.md`, une par une

**Instruction 1 (R4, important) — fuite de chemin / nom sur stderr. PARTIELLEMENT APPLIQUÉE.**
- Fait, et bien fait : le filtrage a été porté à la source, dans `wp/outils/bascule/a11/Runtime.php:21-30`. `refusalMessage()` ne renvoie plus que le code, sauf pour `A11_DROPIN_UNSUPPORTED` dont le `file` est comparé à une **liste fermée** (`DROPINS`, `Runtime.php:19`). `A11_SYMLINK_UNSUPPORTED` et `A11_CONFIG_OVERRIDE_UNSUPPORTED` sont levés sans détails (`Runtime.php:71`, `Runtime.php:39,53`). Le nom de constante n'est plus recopié. Le point de sortie `inventorier-numeros:38-40` est inchangé, ce qui est cohérent : le tri se fait en amont.
- Banc : le lien symbolique canari exigé est présent dans le test commun `wp/tests/a17/refusal-common.py:28-35` (`...uploads/IDENTITE_CONFIDENTIELLE_CANARY`, cas `symlink-file` et `symlink-directory`), qui vérifie `stderr == "A11_SYMLINK_UNSUPPORTED\n"` et l'**absence du canari dans tous les artefacts** (stdout, stderr, fichiers). Preuve livrée verte : `production/A-16/refus-commun-A17.json` (exit_code 0, `canary_absent_all_artifacts: true` sur les 10 cas), Runtime lié par SHA256.
- **Réserve (voir §3) :** l'instruction autorisait explicitement à **laisser passer** « la clé de correspondance absente ». Or le correctif supprime aussi ce détail : `A16_MAPPING_KEY_ABSENT` ne nomme plus la clé. Sur-correction par rapport à la consigne.

**Instruction 2 (R1, important) — « emplacement public » sans branche négative. APPLIQUÉE.**
`Inventory.php:67-79` calcule désormais `public` séparément de la présence du fichier ; `pdf_public` peut valoir `false` (`Inventory.php:79`, reporté `Inventory.php:216`). Plus d'avortement : un PDF privé n'est plus un crash. Racine privée déclarable dans la correspondance (`racine_privee`), contrôlée strictement (`Inventory.php:85-93`, `A16_PRIVATE_ROOT_UNSAFE` : absolue, canonique, sans lien, disjointe du site). Cas banc classic/HPOS ajoutés : `private_pdf_present` (`pdf=oui, pdf_public=false`) et `private_pdf_absent` (`declare_mais_fichier_absent, pdf_public=false`), plus `private_root_paths_never_output` et `private_files_unchanged`. Tous verts (voir §2).

**Instruction 3 (R2, mineur) — correspondance sensible à l'ordre des clés JSON. APPLIQUÉE.**
`Mapping.php:27-28,32` trie les clés de `liaison` (`sort($linkKeys)`) et compare à `['cle', 'source']`, indépendamment de l'ordre, comme les clés de premier niveau. Clé absente ou en trop toujours refusées. Tests unitaires ajoutés : `liaison_keys_order_independent`, `liaison_exact_keys:missing`, `liaison_exact_keys:extra` (`wp/tests/a16/unit.php`).

**Instruction 4 (R3, mineur) — cas limites annoncés mais non éprouvés. APPLIQUÉE.**
`wp/tests/a16/seed.php` ajoute deux numéros de **même date** (`2025-12-01`) et un article publié rattaché au numéro de janvier, **exclu** de `--limit=2`, tout en gardant un vrai orphelin 2025. `inside.py` ajoute `equal_dates_id_descending` (départage par ID décroissant, mêmes dates) et `excluded_number_article_not_orphan` (l'article d'un numéro hors-N ne devient pas orphelin). Les deux sont dans la liste obligatoire de `verify.py`. Mutation-testée côté Hermès (HANDOFF §TDD) : deux mutants réellement attrapés.

**Instruction 5 (encodage mort, mineur) — `Command.php:72`. APPLIQUÉE.**
Le premier `json_encode($report, …)` a été retiré ; il ne reste qu'un encodage, **après** l'ajout des deux empreintes (`Command.php:71-73`). Test unitaire ajouté : `report_encoded_once_after_both_hashes`.

## 2. Résultat des tests

Exécutés en local (droits §3 : pas de rejeu du banc natif en conteneur ; je m'appuie sur le paquet livré pour les assertions natives, comme au premier tour).

- `python wp/tests/a16/verify.py production/A-16/preuves/final` → **20/20 PASS**, exit 0.
- `python wp/tests/a16/test_launcher.py` (contrôle sans PHP hôte) → **3/3 OK**.
- Paquet natif livré `preuves/final/result.json` → **68/68 PASS** classic+HPOS, exit 0 ; toutes les assertions neuves (R1/R3/R4) présentes et vertes dans les deux stockages.
- `production/A-16/refus-commun-A17.json` → exit 0, 10 cas, canari absent partout.
- Non rejoués faute de PHP hôte et de conteneur (droits §3) : les 23 unités PHP et le banc natif lui-même. Je constate leur verdict dans les preuves livrées, je ne les ai pas réexécutés indépendamment — même limite qu'au premier tour.

## 3. Régression / modification non demandée

**Un point de fond, introduit par le correctif R4 : `A16_MAPPING_KEY_ABSENT` ne nomme plus la clé.**

- Avant (version relue), l'outil refusait une correspondance pointant une clé absente en la **nommant** : `A16_MAPPING_KEY_ABSENT {"key":"absent_key"}`. Désormais `refusalMessage()` ne rend que le code (`Runtime.php:30`), et le test a été réécrit pour l'exiger : `inside.py` → `absent_mapping_key_code_only` attend `stderr == "A16_MAPPING_KEY_ABSENT\n"`.
- C'est contraire à **deux** références :
  1. Brief, ligne 31 (Preuve) : « Une correspondance qui désigne une clé absente du site est refusée **en la nommant**. » Cette preuve requise n'est plus produite ; le test livré atteste l'inverse.
  2. `corrections/A-16.md`, instruction 1 : elle autorise explicitement à laisser passer « **la clé de correspondance absente** ». Le correctif va donc au-delà de la consigne.
- La clé en cause est **fournie par l'opérateur** dans le fichier de correspondance (`Inventory.php:101,105,109,127` : `numero_type`, `thematique`, `pdf_cle`, `liaison.cle`). Ce n'est ni un titre, ni un texte, ni un nom d'auteur, ni une adresse de fichier (brief ligne 27) : la nommer ne viole aucune règle d'étanchéité. Ni `corrections/A-16.md`, ni `corrections/A-17.md` (R5, qui ne vise que le chemin du lien symbolique), ni `docs/decisions.md` ne demandent de la masquer.
- Justification invoquée par Hermès : « arbitrage plus récent » (`production/A-16/LIVRAISON.md`, `HANDOFF…:30` : « refus par code fixe »). Cet arbitrage n'est tracé nulle part dans le dépôt et prime, de fait, sur une exigence explicite du brief. Conséquence concrète : l'opérateur reçoit un refus sans savoir **laquelle** de ses clés est mauvaise — précisément l'aide que le brief imposait.

Aucune autre modification non demandée détectée sur le périmètre A-16 : les autres changements de `wp/` relèvent d'autres lots (a11 partagé, a17, a18, thèmes, plugin — hors de ce lot).

## 4. Verdict

**Remonte à Ced.**

Les cinq instructions sont techniquement appliquées et tous les tests accessibles sont verts. Mais le correctif R4 a supprimé un signal que **le brief exige** (« refusée en la nommant ») et que la fusion avait **explicitement autorisé** (« la clé de correspondance absente »). Le test de preuve correspondant a été retourné pour valider ce retrait. C'est un écart de conformité au brief, non couvert par un arbitrage tracé — donc un problème de fond non résolu, pas une simple finition.

Décision attendue, question fermée pour Ced : **faut-il rétablir le nom de la clé de correspondance absente dans `A16_MAPPING_KEY_ABSENT`** (conforme au brief ligne 31 et à l'instruction 1, sans fuite puisque la clé vient de l'opérateur) **— défaut proposé : oui** — ou acter le refus « code seul » en amendant le brief et `docs/decisions.md` ? Le reste du lot est prêt : une fois ce point tranché, aucune autre réserve.

---
*Rappel doctrine : ce verdict de vérification n'est pas un GO (§6). Il ne vaut que pour la clôture du lot de code.*
