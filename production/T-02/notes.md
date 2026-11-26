# T-02 — corrections R1, R2 et M1, sans PRET

La commande habituelle `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\wp\tests\rejouer.ps1`, sans argument, rejoue aussi les banques PHP pures des outils. Aucun changement des options Docker, de l’image, de la préparation ni de la dernière ligne `REJEU` ; aucune nouvelle autorisation nécessaire aux relecteurs. L’ancien `PRET` a été retiré ; la préparation et le prochain marqueur sont réservés au parent.

## Résultat vérifié

- PHPUnit : **1 123 tests, 34 569 assertions, 0 échec, 0 erreur, 0 ignoré**, nombre strictement identique au rejeu avant raccord.
- Outils : **14 banques, 279 contrôles, 0 échec** : A-02/a02-audit **17**, A-03/a03-non-regression **10**, A-10 **10**, A-11 **19**, A-12 **15**, A-14 **8**, A-15 **14**, A-16 **23**, A-17 **42**, A-18 **37**, A-19 **9**, A-20 **23**, A-21 **18**, A-23 **34**. **Hors rejeu : aucun `unit.php` actuel**. A-23, déjà présent pendant cette passe, a été découvert automatiquement sans modification de ses fichiers. Les anciens 11/204 et 13/242 sont des photos dépassées. Les suites Python et les matrices natives classique/HPOS/commerciales restent hors de cette commande.
- Contrats T-02 : **24/24 PHP réels**, **7/7 sorties PowerShell** (doubles de frontière, identifiés comme tels). Non-régression ciblée T-01 : **32/32 PHP réels**, **18/18 contrats de frontière**. Les suites séparées de découverte, d’isolation synthétique et d’interruption n’ont pas été relancées dans cette correction ; les commandes PHP ont contrôlé leur isolation Docker réelle.
- Une assertion existante d’A-10 a été inversée **uniquement dans un miroir jetable sous scratch** : vraie commande, vrai PHPUnit vert, 1 contrôle outil rouge, dernière ligne `FAIL`, code 1 ; restauration exacte, vraie commande à nouveau `PASS`, code 0. Original inchangé ; miroir supprimé ; aucun conteneur T01 restant.
- Même matrice ciblée sous **Windows / CPython 3.14.6 (`C:/Python314/python.exe`)**, PowerShell **5.1**, console **UTF-8 (`PYTHONUTF8=1`) puis cp1252 (`PYTHONUTF8=0`)** ; stdout, stderr et locale mesurés dans chaque `verification.json`. L’orchestrateur fixe `PYTHONIOENCODING=utf-8` pour ses sous-processus. PHP **8.2.33**, exclusivement dans les conteneurs jetables.

## Corrections de la fusion

- **R1, TDD réel :** le contrat exact de la fusion échoue avant correction (**19 tests, 1 échec**), puis passe après la garde (**19 tests, 0 échec**). `tests` et `checks` simultanés sont désormais refusés par `T02_UNIT_RECEIPT_INVALID`, même si une famille vaut `null` ou si les deux sont vertes. Variantes ajoutées : ordre inversé, deux familles vertes, familles nulles et reçu scalaire ; suite finale **24/24**.
- **Mutation témoin, uniquement dans un miroir scratch :** le reçu mixte exact donne dernière ligne `FAIL`, code 1, `0 controls ; 1 failures ; exit=0`. Retirer seulement la nouvelle garde rend le même reçu indûment `PASS`, code 0 ; les contrats détectent la régression (**24 tests, 5 échecs**, code 1). Garde et unité restaurées octet pour octet, vraie commande à nouveau `PASS` ; originaux intacts, miroirs supprimés.
- **R2 :** les `commands.*.output_sha256` sont recalculés sur les octets des journaux finaux livrés, dans les deux contextes. `verifier.py` vérifie les empreintes internes en plus du manifeste externe ; le test Python refuse une empreinte interne périmée même après rescellement externe.
- **M1 :** le décompte ci-dessus vient du dernier rejeu, et non du miroir initial. **R3 :** maintien de l’espace global du harnais T-01, défaut technique de la fusion ; pas de namespacing T-02 isolé.

## Raccord et décisions prises à défaut

Découverte automatique des seuls sous-dossiers immédiats `wp/tests/<lot>/unit.php`, triés, avec exclusion explicite `unit.hors-rejeu` et raison courte. Chaque banque garde ses assertions et son format : un sous-processus séparé produit un reçu neuf, validé strictement (`checks` PASS/FAIL ou ancien dictionnaire `tests` booléens). Assertion rouge, code non nul, avertissement PHP, reçu absent/invalide/vide ou lien symbolique font échouer le rejeu.

Les anciens chemins absolus étaient des chemins de banc, non des dépendances WordPress : seuls leurs **littéraux de chemin dans les copies temporaires** sont relocalisés sous `/tmp`, par tokenisation PHP (`/subject`, `/checkout`, `/report`, `/unit-origin-fixture`). Les sources métier et les banques du dépôt ne sont pas réécrites. Les bibliothèques pures requises par leur chemin canonique restent accessibles par alias vers le montage déjà en lecture seule. Rien n’est écrit hors du tmpfs.

**A-19 instruction 3 : intégration portée par T-02.** Réutilisation inchangée du fichier déjà présent `wp/plugins/imagine-pilotage/tests/Administration/A19SubscriptionCoherenceTest.php` et de l’adaptation `wp/tests/a19/unit.php` ; **9 cas nommés présents dans le JUnit**. Aucun second adaptateur PHPUnit créé. Les 9 cas PHPUnit et les 9 contrôles de la banque autonome sont deux compteurs de rejeu, pas une prétention à 18 règles distinctes.

Deux anciennes attentes T-01 photographiaient les deux seuls paquets de novembre 23 : elles sont désormais contractuelles sur les racines courantes ; leurs refus de configurations partielles et de contexte de préparation trop large restent couverts. Les fixtures du rejeu relocalisé embarquent désormais aussi `tools.php`.

## Fichiers et preuves

Modifiés dans cette correction : `wp/tests/t01/tools.php`, `tools-contract.php`, notes et sceaux T-02. Ajoutés : `wp/tests/t01/test-t02-package.py`, `production/T-02/verifier.py`. `rejouer.ps1` et `preparer-image.ps1` ne changent pas ; les trois lignes T-02 de `production/T-01/notes.md` sont contrôlées par contrat, jamais par hash global. Aucun fichier A-22, A-23 ou autre lot modifié.

Paquet courant unique **`production/T-02/preuves/final/`** ; ancienne livraison déplacée sous scratch, pas de second paquet dans le dépôt. Chaque contexte contient la sortie complète, les mutations/restaurations, les commandes exactes et leurs répertoires de travail, les compteurs et les empreintes. Les étapes TDD intermédiaires et le collecteur de cette passe restent hors dépôt sous `C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-t02-correction/`. Le vérificateur fonctionne avant et après le futur `PRET` parent sans déduire ses gates ; un faux marqueur est testé uniquement dans une copie jetable.

Commandes rejouées depuis `C:/Users/Ced/imagine`, dans les deux environnements ci-dessus :

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\wp\tests\t01\test-tools.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\wp\tests\t01\test-tools-summary.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\wp\tests\t01\test-rejeu.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\wp\tests\t01\test-php-corrections.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\wp\tests\rejouer.ps1
C:/Python314/python.exe .\wp\tests\t01\test-t02-package.py
C:/Python314/python.exe .\production\T-02\verifier.py
```

Collecteur lancé sous Bash : `T02_MATRIX=utf8 PYTHONIOENCODING=utf-8 PYTHONUTF8=1 C:/Python314/python.exe C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-t02-correction/collect.py`, puis la même commande avec `T02_MATRIX=cp1252 PYTHONIOENCODING=cp1252 PYTHONUTF8=0`. Les répertoires de résultats existants sont refusés pour éviter le recyclage d’une preuve.

**Gate restant au parent :** relancer `wp/tests/preparer-image.ps1` après tous les ajouts de tests, puis le rejeu global et le scellement final. **Aucun PRET déposé.** Ni modification d’A-16/A-18/A-19, ni paquet de preuve clos régénéré, ni Git, archive d’Imagine, donnée réelle, compte, staging, déploiement ou verrou touché.
