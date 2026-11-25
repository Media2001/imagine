# B-02 — Rejeu des corrections, 25 novembre 2026, 21 h 58 CET

Depuis `C:/Users/Ced/imagine`, bash Windows :

```bash
PYTHONDONTWRITEBYTECODE=1 'C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-b03-tests/Scripts/python.exe' wp/tests/demo/test_b02_runner.py
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
PYTHONDONTWRITEBYTECODE=1 'C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-b03-tests/Scripts/python.exe' wp/outils/demo/b02.py --require-complete
```

Résultats réellement obtenus : runner **2/2** ; préparation **exit 0** ; T01 **1023 tests/34094 assertions, PASS** ; strict natif/HTTP **138/138, exit 2** pour cinq réserves observées. Installation initiale des corrections faite avec `--deploy --require-complete`, seulement MonCompteRegles.php, MonCompte.php, parts/mon-compte.php puis relecture exacte ; ne réinstalle ni bootstrap partagé ni functions.php. Ne pas lancer de seed/reset C09.

Le test HTTP conserve son parcours positif d’adresse dans `verify(allow_address_edit=True)` mais le défaut des corrections est sans édition positive. Isolation GET/POST et refus de nonce toujours exécutés. Aucun passage à True n’a été effectué ici. Les logs FAIL initiaux et les reçus antérieurs sont conservés ; le rapport distingue le premier snapshot pris pendant des mutations concurrentes et le rejeu stable.

TDD ciblé réel : PHPUnit de l’image préparée, conteneur `--rm --pull never --network none --read-only --tmpfs /tmp:rw,nosuid,nodev,size=128m,mode=1777 --cap-drop ALL --security-opt no-new-privileges --user 65534:65534`, source wp montée readonly ; fichiers MonCompteReglesTest.php et MonCompteAdapterTest.php, **9 tests/73 assertions**. Les tests séparés ont besoin du tmpfs PHPUnit ; aucun outil installé sur Windows.

---

# Historique des commandes avant fusion B02

**Les nombres et descriptions ci-dessous sont historiques, pas les attentes actuelles. En particulier : le hook postal limité au formulaire, l’absence de second règlement et le profil a-4x-j45 sont périmés. Aucun ancien reçu JSON/log n’a été réécrit.**

Répertoire : `C:/Users/Ced/imagine` ; shell bash Windows, `python`, jamais python3. Aucun Git, reset, seed C09 ou reconstruction globale.

## Rouge avant implémentation

```bash
PYTHONDONTWRITEBYTECODE=1 python -c 'import sys,json;from pathlib import Path;sys.path.insert(0,"wp/outils/demo");import c14;c14.c10.guard(); c14.upload("imagine-demo-build/b02-runtime.php",Path("wp/tests/demo/b02-runtime.php"));r=c14.wp("require WP_CONTENT_DIR . \"/imagine-demo-build/b02-runtime.php\";"); p=Path("production/B-02");p.mkdir(exist_ok=True);(p/"red-runtime.json").write_text(json.dumps(r,indent=2));print(r);sys.exit(0 if all(r.values()) else 1)'
```

Exit **1** : `raccord_mon_compte_present=false` (reçu conservé). Pas un succès préfabriqué ni une erreur de syntaxe.

## Itérations réellement lancées

```bash
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/b02.py --deploy --native-only
PYTHONDONTWRITEBYTECODE=1 python wp/tests/demo/b02-http.py
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/b02.py --deploy
```

Premier natif 75/80 (préfixe réel DEMO des codes, intervalle WCS retourné en chaîne). Après correction : 80/80. Premier HTTP **51/54**, rouge sur navigation et observation postale : la vraie sauvegarde WCS émet `after_subscription_object_save`, pas le hook order de C13. Raccord B02 corrigé sans changer C13 ; HTTP **54/54**. Le premier runner complet a ensuite détecté les nouvelles observations append-only comme changement de « policies » dans l'ancien snapshot C14 : garde séparée pour leur append-only, autres options conservées. Aucune ancienne observation supprimée.

## Dernière recette complète

```bash
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/b02.py --deploy --require-complete
```

Exit **2**, volontairement non vert en acceptation complète : **144/144 contrôles techniques**, aucune panne technique, mais profil nominatif A-4x-J45 absent et limites décrites dans `rapport.md`. Décomposition : 75 PHP natifs + 8 états/gardes natifs + 54 HTTP + 4 readbacks/syntaxes + 3 gardes de préservation. Quatre fichiers applicatifs seulement installés, plus les recettes PHP dans `imagine-demo-build` ; aucun reset de profil ni état de paiement changé. Les derniers rouges ciblés (`red-nonaddress.json`, `red-gel.json`) ont précédé respectivement le bornage du hook postal au formulaire natif et la suppression de la promesse de gel C13 ; dernier rejeu complet vert technique, strict 2.

Rejeu indépendant sans réinstallation :

```bash
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/b02.py --require-complete
```

La recette effectue un véritable aller-retour d'adresse synthétique, conserve deux observations postales supplémentaires et les notes natives, puis restaure adresse/date de modification. Ce n'est pas un reset ni un effacement du journal. Le mode `--native-only` évite ce parcours HTTP mais ne prouve pas l'édition.

## Image de test obligatoire

```bash
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
```

Exit **0** ; PHP de l'image 8.2.33, trois paquets publics verrouillés, vérification hors ligne réussie. Image : `sha256:6fa287e70ce269aa0e0bb9dd93d15bbe9629b8280a731df3d11c88c386150572`. Avertissements explicites : imagine-site et le thème ne sont pas découverts par T01 ; les 83 assertions PHP B02 sont exécutées par la recette native ci-dessus, pas prétendues dans T01.

Complément C14 pur exécuté via `c14.pure()` : **21/21**, sans paiement ni mutation de profil. Le runner C14 complet (qui modifie temporairement des états financiers synthétiques) n'a pas été relancé par ce lot. Les 536 + 193 contrôles antérieurs appartiennent au parent, pas aux totaux B02.
