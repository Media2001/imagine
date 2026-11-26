# Vérification B-05 — second et dernier tour

Base relue : état du dépôt au moment de la fusion (`corrections/B-05.md`, 10:06).
Diff examiné : `git diff 0b8e0613 HEAD` sur `wp/` et `production/B-05`.
Je ne refais pas une relecture complète : je vérifie les sept instructions, les tests,
et les écarts.

## Limites d'exécution (honnêteté)

- Le moteur HTML isolé (`b05-unit.py` → Docker/WSL, réseau `none`) et les sondes de la
  démo live (`b05-http.py`, `b05-admin.py` contre `http://192.168.129.32:8085`) sont **hors
  de mes droits** en session non interactive : WSL/Docker exige une approbation que je ne
  peux pas donner ici, et la démo live est interdite au relecteur.
- J'ai donc relancé le **vérificateur rejouable V2** (`wp/tests/demo/b05-verifier.py`, qui
  délègue à `b05-verifier-v2.py`) : pur Python, sans réseau, sans Docker. Il contrôle
  l'intégrité des reçus (tous verts), les **SHA-256 des sources** (ils correspondent à
  l'arbre de travail) et les contrats partagés. **Sortie : `B05 VERIFIE_V2`, code 0.**
- Conséquence : le code que j'ai relu sur le disque est **exactement** celui scellé dans
  `final-V2.json`. Les gates live/Docker sont validés via l'intégrité des reçus scellés,
  pas réexécutés par moi.

## 1. Les sept instructions de corrections/B-05.md

| # | Instruction | État | Fichier : ligne |
|---|---|---|---|
| 1 | R2 — réparer le contrôle accueil (vraie section, présence>0, puis absence `sponsored`, aucun permalien partenaire, + mutation témoin) | **Appliquée** | `wp/tests/demo/b05-http.py:13-36` (`home_article_checks`, `home_mutations`), `:90-94` ; témoin : `wp/tests/demo/b05-browser-unit.py:20-23` |
| 2 | R1 — fermer la faille des liens sortants (rogner espaces/contrôles ASCII, antislashes, autorités à slashes surnuméraires, doute → commercial, `array_unique`) | **Appliquée** | `wp/themes/imagine/functions.php:162-181` ; canari enrichi `wp/tests/demo/b05-http.py:59` (espace initial + `https:////`) |
| 3 | Couvrir B-05 hors live (validation `id`, filtre `imagine_partner_content`, formes malformées) | **Appliquée** | `wp/tests/demo/b05-offline.php:43-109` (64 contrôles, exécuté en conteneur isolé par `wp/outils/demo/b05-unit.py`) ; + `b05-browser-unit.py` |
| 4 | Tracer la rupture d'injection C10 (log/avertissement admin si ancre introuvable) | **Appliquée** | `wp/plugins/imagine-site/Partenaires.php:74-78` (avertissement `notice-error imagine-partenaire-injection-erreur`) |
| 5 | Reformuler le texte de l'archive | **Appliquée** | `wp/themes/imagine/archive-imagine_partenaire.php:10` (« Les fiches ci-dessous sont des liens internes… ») |
| 6 | Mettre à jour les reçus (total périmé + écart de hash `imagine-site.php`) | **Appliquée** | Jeu de reçus V2 ; `PRET`, `A-VOIR.md:28`, `CORRECTIONS-V2.md:14` affichent 1123/34569 ; hash partagé **expliqué** (contrat B05, `shared_bootstrap_pinned:false`), non plus épinglé |
| 7 | Lever l'ambiguïté de `imagine_list` (documenter ou retirer la branche `sponsored`) | **Appliquée** | `wp/themes/imagine/functions.php:130-131` (branche morte **retirée**, commentaire explicite) |

Précisions de contrôle, à la lecture :

- **R1 (inst. 2)** : le défaut prudent de la fusion est respecté. Seuls les liens
  **internes certains** passent (`continue`) : hôte identique à `home_url`, ou relatif/ancre
  sans `:` ni `\`. Les formes HTTP malformées et toute destination ambiguë (`https:example`,
  `https:\…`) reçoivent `sponsored`. Les fixtures `b05-offline.php:44-55`
  (`leading_space`, `extra_slashes`, `ambiguous_http`, `backslash_authority` → commercial ;
  `internal`, `internal_case`, `relative`, `anchor` → non) couvrent exactement ces bords.
  Pas de sur-marquage des liens internes.
- **R2 (inst. 1)** : `front-page.php` portait déjà `aria-labelledby="imagine-latest-posts"`
  et `imagine_list` émet `<ul class="imagine-list">` ; la correction est donc dans le
  sélecteur de test, désormais `section[aria-labelledby=…] .imagine-list a`. La mutation
  témoin (`a.rel="sponsored"`) **fait bien échouer** le contrôle, et `b05-browser-unit.py`
  reproduit le faux positif de l'ancien sélecteur à côté du nouveau qui le refuse.

## 2. Résultat des tests

Relancé par moi (hors réseau, pur Python) :

```
python -B wp/tests/demo/b05-verifier.py
→ {"B05":"VERIFIE_V2", … "live_readback":false}  (code 0)
```

Totaux scellés et revalidés par ce vérificateur :

- T01 rejoué : **1123 tests / 34569 assertions**, 0 échec / 0 erreur / 0 ignoré ;
  outils purs 14 / 279 contrôles, 0 échec.
- B-05 hors live : PHP isolé **64/64** ; Chromium hors réseau **9/9** ; natif **15/15** ;
  pages HTTP **50/50** ; admin lecture/refus/captures **12/12** ; qualité **8/8** ;
  C09 **382/382**.

Le total 1123/34569 remplace le périmé 1097/34443 et l'intermédiaire 1114/34560 cité en
fusion : l'écart tient à des lots postérieurs, **pas** à B-05. Les gates Docker et live
n'ont pas été réexécutés par moi (droits), mais leur intégrité est confirmée : reçus verts,
hash des sources concordant avec l'arbre.

## 3. Régressions ou modifications non demandées

- **Aucune régression** repérée dans le périmètre B-05. Les seules modifications de source
  sont les instructions 2, 4, 5, 7 ; les tests portent 1 et 3 ; les reçus portent 6. La
  réduction de `NAMES` dans `b05.py` et la délégation de `b05-verifier.py` vers la V2 font
  partie de l'instruction 6 (bootstrap partagé contrôlé par contrat).
- **Hors B-05, dans la même fenêtre de diff** : des fichiers de **C-21** et **C-22**
  (`c21-fusion-verifier.py`, `c21-verifier.py`, `c22-*.py/php`) ont changé. Ils relèvent
  d'autres lots traités en parallèle, **ne sont pas** des corrections B-05 et ne sont pas
  évalués ici. Signalé pour que la clôture B-05 ne les absorbe pas.
- **Écart de hash `imagine-site.php`** (constat Codex) : non « réparé » mais **requalifié** —
  fichier partagé, B-05 n'épingle que son propre bloc d'amorçage (contrat vérifié :
  présent une seule fois). Choix cohérent avec la doctrine (pas de réécriture d'un fichier
  tiers hors hook). Reçu conserve hash observé et historique.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les sept instructions sont appliquées et citées ; les tests rejouables sont au vert ;
aucun problème de fond ne subsiste ; aucune question ouverte technique ou métier n'est
laissée pour Ced dans le lot. Restent, hors verdict technique, les deux points qui relèvent
par nature de Ced et du designer : la **validation visuelle** (`accueil-partenaire-V2.png`,
`fiche-partenaire-V2.png`) et la **distinction graphique** de l'étiquette « Partenariat ».

Rappel doctrine : ce verdict n'est pas un GO. Il ne vaut que pour la clôture du lot de
code ; aucune mise en ligne ni bascule n'est autorisée.
