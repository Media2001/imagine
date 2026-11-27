# T03 — réception native achevée

Fait : communs T01/T03 intégrés (second montage RO, collecteur Python) ; image préparée réellement, wrappers20–25 et déclarations20–28 ajoutés, aucun contrôle import/gardien modifié.
Prêt à relire : T03 ; 9 paquets vérifiés, 0 échec ; hors rejeu : aucun.
À arbitrer : A22 toujours NON CLOS ; ce rejeu auteur permet la relecture indépendante mais ne la remplace pas. Aucun GO réel.
Bloqué : aucun pour T03 ; mutant +1 octet A28 donne uniquement PACKAGE_DRIFT, REJEU PASS et compteurs inchangés ; copie et runners supprimés, absences prouvées.
Ensuite : parent verify ; REJEU : 1153 tests, 36074 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS ; reçus exacts dans production/T-03/preuves/final ; verrou conservé.

Commandes réellement exécutées depuis `C:/Users/Ced/imagine`, sorties/exits complets dans `preuves/final/native/` :

```text
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/t01/test-paquets-native.ps1 -Output C:\Users\Ced\AppData\Local\hermes\cache\scratch\requal2127-t03-20261127\t03-native-copy-proof-02
```

Toutes exit0. La préparation contient `T03 IMAGE PYTHON : offline standard-library probe PASS`. Deux montages bind exactement, `/repo/wp:ro` et `/packet-repo:ro`, racine vérifiée ; réseau none, rootfs RO, 65534, cap-drop ALL, no-new-privileges, limites inchangées et tmpfs seul. Les inspections avant/après sont obligatoires dans le vrai runner ; la preuve ne les remplace pas par une simulation. La copie jetable altère exactement un octet de before/native.json ; les deux sorties complètes green.log/one-byte.log prouvent le même REJEU, la seule erreur A28 PACKAGE_DRIFT et deux nettoyages vérifiés.

Entrées sans argument ajoutées : A20/A21/A22 appellent leurs `wp/tests/aNN/verify.py production/A-NN/preuves/final` ; A23/A25 appellent le vérificateur existant avec `--require-shared-doc`, A24 avec `--require-shared`. Aucun contrôle réécrit. A26/A27 gardent leur enveloppe scellée actuelle, A28 son vérificateur actuel. `rejeu.json` liste les contrôles fermés et tous les journaux requis dérivés des inventaires/références, y compris les gates externes26/27 ; l’absence d’un journal reste hors rejeu, jamais reconstituée. Détail relu par lot dans integration-readback.json. Les trois lignes exactes T01 sont conservées uniques, `scripts/relire.ps1` inchangé.

Contrats locaux réellement rejoués : 15 collecteur + 9 intégration, chacun UTF-8 et cp1252 sous Windows Python3.14.6 ; deux scripts historiques de doubles PowerShell verts. Ces doubles ne sont pas les preuves natives. Les matrices natives classique/HPOS/commerciales restent hors de T01 : vérifier leurs reçus ne les rejoue pas. Aucun paquet A29/A30 intégré de force ; A29 reste bloqué neutral_success exit255/refus, pas de PRET29. La liste hors rejeu ci-dessus est celle réellement mesurée, pas un inventaire de tous les lots sans entrée.

Évolution observée hors gel de propriétaires : le premier rejeu réel avait 1151 tests / 36062 assertions PASS ; la première copie a exécuté 1152 tests avec un échec SujetAdapterTest::testAntislashDuPostAuDetailAdminEtExport (paquet imagine-site, hors périmètre). Cet essai a été conservé intact en scratch, copie détruite ; il ne prouve pas la mutation un octet. Un seul rejeu de contrôle réel a ensuite mesuré 1153 tests / 36074 assertions PASS. La nouvelle preuve utilise cette référence actuelle : ses deux passages ont exactement cette même dernière ligne PASS. Aucun inventaire d’empreintes, gel ou changement de source de la voie2 par cette phase ; les sources des propriétaires A21–27/T03 restent exactement les 397 empreintes gelées. Les gates communes de qualification à 1151 restent leurs vrais résultats antérieurs, jamais réécrits comme 1153. Les anciens logs restent hors dépôt, aucune ancienne course rouge renommée verte.

Ancien candidat T03 et ses reçus locaux intacts : `C:/Users/Ced/AppData/Local/hermes/cache/scratch/requal2127-t03-20261127/T03-ancestor`. Sept lots requalifiés : `files/rapports/2026-11-27-05h03-qualification-A21-A27` ; leurs PRET relus verts après ce T03. Source gelée par propriétaires explicites, jamais inventaire voie2. A28 : seul ajout rejeu.json et metadata manifest actualisée, verify28 vert avant/après ; tous les reçus natifs inchangés. Gardien, import, Git, réel, compte/site/Novamira, voie2, cron, scripts/relire intacts. Verrou rafraîchi, non libéré.
