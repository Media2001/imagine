# T-02 — candidat livré, sans PRET

La commande habituelle `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\wp\tests\rejouer.ps1`, sans argument, rejoue aussi les banques PHP pures des outils. Aucun changement des options Docker, de l’image, de la préparation ni de la dernière ligne `REJEU` ; aucune nouvelle autorisation nécessaire aux relecteurs.

## Résultat vérifié

- PHPUnit : **1 123 tests, 34 569 assertions, 0 échec, 0 erreur, 0 ignoré**, nombre strictement identique au rejeu avant raccord.
- Outils : **11 banques, 204 contrôles, 0 échec** : A-02/a02-audit **17**, A-03/a03-non-regression **10**, A-10 **10**, A-11 **19**, A-12 **15**, A-14 **8**, A-15 **14**, A-16 **23**, A-17 **42**, A-18 **37**, A-19 **9**. **Hors rejeu : aucun `unit.php` actuel**. Les suites Python et les matrices natives classique/HPOS/commerciales restent hors de cette commande.
- Contrats T-02 : **18/18 PHP réels**, **7/7 sorties PowerShell** (doubles de frontière, identifiés comme tels). Non-régression T-01 : **32/32 PHP réels**, **18/18 contrats de frontière**, **2/2 découverte de préparation**, isolation réelle et interruption/récupération réelles vertes.
- Une assertion existante d’A-10 a été inversée **uniquement dans un miroir jetable sous scratch** : vraie commande, vrai PHPUnit vert, 1 contrôle outil rouge, dernière ligne `FAIL`, code 1 ; restauration exacte, vraie commande à nouveau `PASS`, code 0. Original inchangé ; miroir supprimé ; aucun conteneur T01 restant.
- Même matrice complète sous **Windows / CPython 3.14.6**, PowerShell **5.1**, console **UTF-8 puis cp1252 avec `PYTHONUTF8=0`** ; sortie et locale mesurées dans chaque `verification.json`. L’orchestrateur fixe `PYTHONIOENCODING=utf-8` pour ses sous-processus. PHP **8.2.33**, exclusivement dans les conteneurs jetables.

## Raccord et décisions prises à défaut

Découverte automatique des seuls sous-dossiers immédiats `wp/tests/<lot>/unit.php`, triés, avec exclusion explicite `unit.hors-rejeu` et raison courte. Chaque banque garde ses assertions et son format : un sous-processus séparé produit un reçu neuf, validé strictement (`checks` PASS/FAIL ou ancien dictionnaire `tests` booléens). Assertion rouge, code non nul, avertissement PHP, reçu absent/invalide/vide ou lien symbolique font échouer le rejeu.

Les anciens chemins absolus étaient des chemins de banc, non des dépendances WordPress : seuls leurs **littéraux de chemin dans les copies temporaires** sont relocalisés sous `/tmp`, par tokenisation PHP (`/subject`, `/checkout`, `/report`, `/unit-origin-fixture`). Les sources métier et les banques du dépôt ne sont pas réécrites. Les bibliothèques pures requises par leur chemin canonique restent accessibles par alias vers le montage déjà en lecture seule. Rien n’est écrit hors du tmpfs.

**A-19 instruction 3 : intégration portée par T-02.** Réutilisation inchangée du fichier déjà présent `wp/plugins/imagine-pilotage/tests/Administration/A19SubscriptionCoherenceTest.php` et de l’adaptation `wp/tests/a19/unit.php` ; **9 cas nommés présents dans le JUnit**. Aucun second adaptateur PHPUnit créé. Les 9 cas PHPUnit et les 9 contrôles de la banque autonome sont deux compteurs de rejeu, pas une prétention à 18 règles distinctes.

Deux anciennes attentes T-01 photographiaient les deux seuls paquets de novembre 23 : elles sont désormais contractuelles sur les racines courantes ; leurs refus de configurations partielles et de contexte de préparation trop large restent couverts. Les fixtures du rejeu relocalisé embarquent désormais aussi `tools.php`.

## Fichiers et preuves

Modifiés : `wp/tests/rejouer.ps1`, `wp/tests/t01/executer.php`, `wp/tests/t01/corrections-php.php`, `wp/tests/t01/mock-wsl.ps1` ; ajout strict de **trois lignes** à `production/T-01/notes.md`, contrôlé par contrat et non par empreinte globale.

Créés : `wp/tests/t01/tools.php`, `wp/tests/t01/tools-contract.php`, `wp/tests/t01/test-tools.ps1`, `wp/tests/t01/test-tools-summary.ps1`, cette note et le paquet unique **`production/T-02/preuves/final/`**. Chaque contexte contient la sortie complète, la mutation rouge/restaurée, les commandes, les compteurs et les empreintes des seuls fichiers T-02. A-16 est contrôlé par contrat, sans empreinte instable. Les étapes TDD intermédiaires restent hors dépôt, sous `C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-t02/`.

**Gate restant au parent :** relancer `wp/tests/preparer-image.ps1` après tous les ajouts de tests, puis le rejeu global et le scellement final. **Aucun PRET déposé.** Ni modification d’A-16/A-18/A-19, ni paquet de preuve clos régénéré, ni Git, archive d’Imagine, donnée réelle, compte, staging, déploiement ou verrou touché.
