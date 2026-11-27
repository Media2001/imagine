# A-32 — Finalisation après corrections du 27 novembre

**État courant : A-31 est scellé avec PRET ; ne pas le déplacer ni le resceller. A-33 est construit, sa matrice locale est verte et ses gates de paquet sont rouges.** La séquence A-31/A-32 ci-dessous est historique, autorisée une fois : elle n'autorise pas de déplacement d'A-33. Aucun lecteur, import, gardien ou lanceur n'est assoupli pour résoudre ce cycle.

## Contrôles actuels, lecture seule

Depuis `C:/Users/Ced/imagine` :

```sh
C:/Python314/python.exe -B wp/tests/a32/verify.py --evidence=production/A-32/preuves/final
C:/Python314/python.exe -B production/A-32/verify.py
C:/Python314/python.exe -B production/A-31/verify.py
C:/Python314/python.exe -B production/A-33/verify.py
```

Le premier contrôle ne qualifie que la matrice complète ; le lecteur de production exige toujours de vraies gates vertes. RAPPORT.md précise les sorties effectivement observées, sans transformer le candidat en PRET.

Après résolution autorisée du blocage par le parent, les seules commandes A-32 nécessaires sont :

```sh
C:/Python314/python.exe -B wp/tests/a32/gates.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a32-gates-apres-parent-NEUF
C:/Python314/python.exe -B wp/tests/a32/seal.py --gates=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a32-gates-apres-parent-NEUF
C:/Python314/python.exe -B production/A-32/verify.py
```

**Ne lancer le sceau que si le collecteur rend vraiment 0.** Les gates photographient récursivement tout `wp/outils/bascule/`, A-33 inclus. Aucun paquet rouge n'est ignoré ; `T01_RESULT.pass=true` ne suffit jamais si `packets.failures` n'est pas vide. `seal.py` ne crée jamais PRET et refuse les gates rouges. Une réinstallation locale utilise `--evidence=<matrice-verifiee> --archive-existing=<scratch-neuf>`, sans empreinte remplacée à la main.

Après les sceaux A-32/A-33 : rejeu indépendant dans les deux consoles, TMPDIR retiré, reçus hors paquets ; exiger zéro échec et A-31/A-32/A-33 réellement dans `packets.lots`, aucun exclu, puis relire les lecteurs sans argument. Alors seulement les PRET pertinents et T-03 par ses propres contrôles. Tant que le cycle reste rouge : candidat vérifié, aucun PRET, retour au parent ; ne pas exclure discrètement A-33 ni effacer ses gates.

---

## Historique — ancienne finalisation conjointe, ne pas rejouer

Les états et commandes qui suivent décrivent la réception antérieure aux corrections et à A-33, pas la situation actuelle.

# A-32 — Finalisation conjointe réservée au parent

Ce document ne déclare aucun `PRET`. La matrice locale complète est indépendante des paquets A-31/T-03. Le vérificateur de production exige toujours les gates réellement vertes ; `A31_PARTIAL_EVIDENCE` n'est ni ignoré, ni remplacé, ni assoupli. Le contrôle local A-31 (324 PASS dans la réception du parent) n'est pas sa réception de production.

## Commandes propres A-32

Depuis `C:/Users/Ced/imagine`, avec le vrai Python Windows :

```sh
C:/Python314/python.exe -B wp/tests/a32/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a32-matrice-neuve
C:/Python314/python.exe -B wp/tests/a32/verify.py --evidence=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a32-matrice-neuve
C:/Python314/python.exe -B wp/tests/a32/gates.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a32-gates-neuves
```

La dernière commande lance réellement `preparer-image.ps1`, les deux rejeux canoniques puis les vérificateurs A-20/A-21/A-22/A-28. Un `T01_RESULT.pass=true` ne suffit pas : elle exige aussi zéro échec dans `packets.failures`. Les tests Python et les runners natifs ôtent TMPDIR aux fils ; les deux consoles sont mesurées, pas supposées.

`seal.py --evidence=... --archive-existing=<scratch-neuf>` vérifie et installe une matrice complète en conservant l'ancien paquet hors dépôt. Sans gates vertes, il marque `complete=false` et retourne `A32_LOCAL_STAGED_GATES_PENDING`, **pas** `A32_PACKAGE_PASS`. `seal.py --gates=<scratch-neuf>` ne joint que des gates réellement vérifiées et recalcule le sceau par son propre inventaire ; il ne crée jamais PRET. Il refuse un PRET préexistant, les liens et les preuves partielles. Ne changer aucune empreinte à la main.

## Résoudre l'ordre d'installation, sans faux vert

Le parent a actuellement un candidat A-31 complet à son emplacement final, mais pas de manifeste A-31. Tant que ses journaux sont présents, le rejeu le lit et refuse `A31_PARTIAL_EVIDENCE`. A-32 ne peut pas toucher ce paquet. Le resealer A-31 exige lui-même un emplacement final absent : le déplacement de ce candidat vers scratch est donc une étape normale de sa commande propre, pas une modification du vérificateur.

Le parent seul peut effectuer la séquence minimale ci-dessous, sérialisée, après avoir relu les états réels. Le candidat A-32 doit déjà être installé localement, sans dossier `gates` et sans PRET. Le dossier scratch nommé ci-dessous doit être neuf.

1. Sortir le candidat A-31 de son emplacement d'installation, sans le détruire, et séparer ses anciennes gates rouges :

```sh
C:/Python314/python.exe -B -c "from pathlib import Path; import shutil; r=Path.cwd(); s=Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-a32-joint-final'); assert not s.exists(); assert not (r/'production/A-31/manifest.json').exists(); assert not (r/'production/A-31/PRET').exists(); assert not (r/'production/A-32/PRET').exists(); s.mkdir(); shutil.move(str(r/'production/A-31/preuves/final'),str(s/'a31-evidence')); shutil.move(str(s/'a31-evidence/gates'),str(s/'a31-gates-historiques'))"
C:/Python314/python.exe -B wp/tests/a31/verify.py --evidence=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-a32-joint-final/a31-evidence
```

2. Produire les deux gates avant de réinstaller l'un des paquets. Le rejeu doit alors nommer A-31 et A-32 dans les exclusions `journaux absents`, sans les présenter comme vérifiés ; A-22 et A-28 restent effectivement vérifiés, tous les autres paquets présents doivent être verts. Cette étape n'autorise aucun PRET.

```sh
C:/Python314/python.exe -B wp/tests/a31/gates.py --parent-serialized --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-a32-joint-final/a31-gates
C:/Python314/python.exe -B wp/tests/a32/gates.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-a32-joint-final/a32-gates
```

3. Réinstaller par les commandes propres, pas par réécriture d'empreintes :

```sh
C:/Python314/python.exe -B wp/tests/a31/reseal.py --parent-serialized --evidence=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-a32-joint-final/a31-evidence --gates=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-a32-joint-final/a31-gates
C:/Python314/python.exe -B wp/tests/a32/seal.py --gates=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-a32-joint-final/a32-gates
C:/Python314/python.exe -B production/A-31/verify.py
C:/Python314/python.exe -B production/A-32/verify.py
```

4. Rejouer indépendamment `wp/tests/rejouer.ps1` dans les deux consoles Windows (UTF-8 puis cp1252, TMPDIR retiré) et conserver les sorties réelles hors des paquets déjà scellés. Exiger `REJEU ... PASS`, `packets.failures=[]`, **A-31 et A-32 effectivement dans `packets.lots`, aucun des deux exclu**. Vérifier à nouveau les deux paquets sans argument. Alors seulement déposer les PRET et terminer T-03 par ses propres contrôles. Si une gate reste rouge : s'arrêter sans PRET, ne rien assouplir.

La procédure A-31 ci-dessus n'a pas été exécutée par le worker A-32 : elle dépasse son périmètre d'écriture. A-33 reste non commencé.
