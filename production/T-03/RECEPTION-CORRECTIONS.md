# Réception des corrections T-03 — 27 novembre 2026

**Candidat de corrections seulement. Aucun PRET, aucun GO.** Le parent reprend les dernières gates, les gels dépendants et la preuve nominale/un octet après A-30. Aucun paquet voisin n'est rescellé par cette intervention.

## 1. Six instructions appliquées

1. **C1, échéance commune** — `executer.php` établit l'échéance monotone de 600 s immédiatement après `declare`, avant découverte, copie, PHPUnit et outils. `paquets.php` reçoit ce même instant et utilise `min(150 s, temps restant - 5 s de publication - 1 s de grâce TERM/KILL)`. S'il n'y a plus de budget, il ne lance rien ; si la phase expire, seul `T-03 RUNNER_TIMEOUT` devient rouge. Le marqueur unique `T01_RESULT` reste émis après la phase et son `pass`/ses compteurs ne dépendent pas des paquets. **`wp/tests/rejouer.ps1` n'a pas été modifié** : timeout extérieur 600, montages et limites inchangés.
2. **C1, intégration réelle** — `test-corrections.py` lance le vrai PowerShell, le vrai conteneur et un vrai PHPUnit : un test dort 2 s, un outil pur dort 2,5 s et produit son vrai reçu, puis un vérificateur dort 10 s. Dans la seule copie jetable, le contrat énuméré remplace exactement `600.0` par `7.0` et la marge `5.0` par `1.0` dans les deux affectations PHP nommées. Aucun faux temps/tick, aucune variable de mutation de production, aucun changement du lanceur extérieur ou des assertions. Le paquet rouge borné conserve **REJEU : 1 tests, 1 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS**, et l'absence du vrai runner est relue. La consommation antérieure réelle et la marge/grâce laissent moins d'une seconde au vérificateur lent.
3. **S1, flux et descendants** — `paquets.py` utilise `Popen`, une session privée et des lectures concurrentes par sélecteur. Chaque canal est plafonné à 1 Mio pendant la lecture ; le bloc excédentaire n'est pas ajouté. Dès dépassement, SIGKILL vise le groupe, le fils direct est attendu et les pipes sont fermés ; seul `VERIFIER_OUTPUT` est rendu, jamais les flux privés. Le groupe est aussi supprimé sur sortie normale, délai individuel et TERM de la phase. Le handler TERM pose un drapeau, sans lever une exception asynchrone au milieu de `Popen` ; la boucle EOF/attente vérifie aussi ce drapeau. Deux producteurs **finis** de 2 Mio, l'un stdout et l'autre stderr, chacun avec un vrai fils et petit-fils, ont un observateur suivant qui vérifie leurs vrais PID dans `/proc` avant la fin du conteneur. Un test natif supplémentaire couvre les deux flux simultanés. Aucun stress OOM de l'hôte.
4. **A-20** — déclaration toujours absente, raison `declaration absente` explicitement conservée sur PAQUETS. Aucun fichier A-20 n'est modifié. La convention programme sa requalification sans argument dans un lot ultérieur, sans changer ses contrôles ni ses reçus natifs ; ce n'est pas une requalification A-20 ici.
5. **OUTILS** — une nouvelle exécution du vrai `wp/tests/rejouer.ps1` est conservée, avec le nombre réellement observé : **22 outils, 584 contrôles, 0 échecs**. Ce n'est pas une valeur imposée : le collecteur n'a aucun compteur modifié. Le REJEU observé est désormais **1159 tests, 36263 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS**. L'ancien 1153/36075 et les anciens 582/584 restent de l'historique, pas des preuves courantes.
6. **Opt-in** — phrase ajoutée à `CONVENTION.md` : seuls les lots déclarés opt-in figurent parmi les vérifiés ; un lot absent de la ligne n'est ni vérifié ni compté hors rejeu. Les diagnostics explicites `verify.py` sans déclaration restent nommés `declaration absente`, notamment A-20. A-29 n'a pas été déclaré ni diagnostiqué.

M2/M3 restent au défaut demandé : montage racine RO inchangé ; les tests T-03 ne sont pas ajoutés implicitement à la commande relecteur. Les trois lignes communes T-01 et leur fichier `readme-ajout.txt` n'ont pas changé.

## 2. RED réels avant correction, GREEN après

Historique intégral, hors dépôt :

`C:/Users/Ced/AppData/Local/hermes/cache/scratch/t03-corrections-20261127-0646/`

- `historique-T03/` contient le paquet et le PRET antérieurs ; le PRET a été retiré **avant** les modifications. `ancienne-preuve-final/` et `ancien-manifest.json` restent historiques, pas ré-étiquetés.
- `red-c1/` : vrai rejeu de la fixture avant le fix, 18,367 s ; le vérificateur lent n'est pas borné au budget PHP restant, contrôles `closed_packet_red_only` et `real_remaining_budget_bounded` rouges. Le test a donc échoué sur le défaut visé, pas sur une erreur de syntaxe ou un double de temps.
- `red-s1/` : stdout puis stderr réels avant le fix, deux contrôles rouges (`VERIFIER_OUTPUT` puis `DESCENDANTS_STOPPED`) ; les descendants survivent à l'ancien collecteur. L'observateur nettoie aussi ces essais RED rejetés.
- `green-c1/`, `green-c1-s1/` : échéance puis les trois cas réels passent après correction ; 7 tests natifs supplémentaires sont dans `native-streams/`.
- `qualification-01/` : première qualification honnêtement rouge. Les anciens bancs PHP/T02 copiaient `executer.php`, `discovery.php` et `tools.php`, mais pas les nouvelles dépendances `paquets.php`/`paquets.py` : inclusion manquante, donc 9/32 et 3/24 rouges. Correction **limitée aux listes de copie de ces deux fixtures**, sans drapeau de production, sans mutation de verdict ni d'assertion. `green-legacy-fixtures/` prouve ensuite 32/32 et 24/24 verts. Ces échecs ne sont ni effacés ni présentés comme verts.

Le paquet courant `preuves/final/qualification/` est la nouvelle qualification complète **après les dernières écritures des sources et notices** :

- Python Windows réellement détecté : `C:/Python314/python.exe`, **3.14.6** ; consoles UTF-8 / cp1252 et modes UTF-8 1 / 0 mesurés, pas supposés.
- Dans chaque console : **15 contrats collecteur + 9 contrats d'intégration/préservation + 3 intégrations Docker réelles**. Les doubles restent identifiés et distincts des intégrations réelles.
- **7 tests natifs de flux/groupes**, lint PHP dans le conteneur, **32 tests de corrections PHP** et **24 contrats T02**, deux scripts de doubles PowerShell et le nominal observé.
- Lint et PHP natif ne sont jamais exécutés sur Windows. Les producteurs natifs sont finis ; tous les conteneurs possédés sont supprimés avec absence relue. Les copies jetables sont absentes.

Le lecteur du candidat vérifie 14 commandes terminées, leur exit réel, leurs flux hachés, les trois cas par console, la mesure des consoles, l'inventaire et les sources courantes. Son succès signifie **tests des corrections PASS**, jamais gate globale ou PRET.

## 3. État nominal observé et dépendances à reprendre

Le premier rejeu nominal réellement observé (`qualification-01`, avant réception A-30) affichait **10 vérifiés**, A-21 à A-28, A-30 et A-31 ; **A-20 seul hors rejeu**, et honnêtement quatre rouges :

- A-26 `SEALED_VERIFICATION_FAILED` ;
- A-27 `SEALED_VERIFICATION_FAILED` ;
- A-30 `PACKAGE_DRIFT` (autre agent de tests actif ; ni qualification ni rescellage A-30 ici) ;
- A-31 `A31_PARENT_GATES_MISSING`.

Les gels antérieurs A-26/A-27 et les sources de gates A-31 diffèrent réellement sur les sources communes corrigées : `corrections-php.php`, `executer.php`, `paquets.php`, `paquets.py`, `test_paquets.py`, `tools-contract.php`. Ce sont des dépendances périmées à **requalifier réellement**, pas des hashes à remplacer pour verdir le collecteur. Malgré ces paquets rouges, le vrai REJEU reste PASS et ses nombres/tests/outils restent séparés. Les logs bruts contiennent la sélection et les codes exacts. Aucun engagement de dix paquets verts n'est fait ici.

## 4. Commandes de réception/finalisation parent

Depuis `C:/Users/Ced/imagine`, **séquentiellement**, avec le même Python Windows ; sorties toujours dans un **nouveau** répertoire Scratch. Ne pas lancer des runners T01 concurrents : leur balayage d'orphelins est exclusif.

Qualification des corrections, consoles et intégrations réelles, avec nouvelle observation nominale :

```text
C:/Python314/python.exe -B production/T-03/qualifier-corrections.py --output C:/Users/Ced/AppData/Local/hermes/cache/scratch/t03-parent-final-NEUF --nominal
```

Lecture seule du candidat livré (ne lance aucun Docker, n'écrit aucun fichier) :

```text
C:/Python314/python.exe -B production/T-03/verify-corrections.py
```

Après réception A-30, reprendre les qualifications/gates/gels réellement nécessaires des lots dépendants dans leurs périmètres autorisés, puis tous les lecteurs sans argument A-20, A-21…A-28, A-30, A-31 dans les deux consoles. Exemples de commandes exactes, sans retoucher les lecteurs :

```text
C:/Python314/python.exe -B production/A-26/verify.py
C:/Python314/python.exe -B production/A-27/verify.py
C:/Python314/python.exe -B production/A-31/verify.py
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Ne pas se contenter du code 0 global : exiger **PAQUETS : 10 vérifiés, 0 échecs**, A-31 présent, seul A-20 exclu, OUTILS réconcilié au nombre alors observé, REJEU PASS, une seule ligne T01_RESULT et nettoyage relu. Refaire les gates finales T01 exigées par les paquets voisins (corrections PHP, outils, découverte, isolation, interruption, consoles, image si leur contrat l'exige) ; ne pas modifier import/gardien pour satisfaire une gate.

Seulement ensuite, nouvelle preuve finale complète nominale + exactement un octet A-28 sur copie :

```text
powershell.exe -NoProfile -ExecutionPolicy Bypass -File production/T-03/native-copy-proof.ps1 -Output C:/Users/Ced/AppData/Local/hermes/cache/scratch/t03-parent-one-byte-NEUF
```

Le banc propriétaire attend maintenant explicitement les dix lots, A-31 compris ; le banc commun `wp/tests/t01/test-paquets-native.ps1` reste intact. Exiger baseline sans rouge, puis seul A-28 PACKAGE_DRIFT, même dernier REJEU et mêmes nombres, deux nettoyages, copie absente et reçu original inchangé. **Cette preuve finale n'est pas anticipée ou synthétisée dans le paquet candidat.**

À la réception finale, refaire inventaire/octet des sources import/gardien contre le gel parent antérieur, et contrôler que `rejouer.ps1`, `commun.ps1`, Dockerfile, les deux montages RO, timeout extérieur 600 et limites sont restés identiques. Les gels qui incluaient les anciens t01 doivent être repris après les vraies gates, sans simple actualisation des empreintes historiques. Aucun fichier ni inventaire de sources de voie 2 ne doit être ajouté à un sceau T-03.

## 5. Limites et état conservé

Aucun Git, compte, site, réel, cron, montage ou limite modifié ; aucun diagnostic A-29 repris. Import et gardien, style inclus, sont intacts. Les sources/gates A-30 restent à leur agent et au parent. Les anciennes preuves ne sont pas rescellées, et aucun manifeste voisin n'est modifié. `.hermes.lock` est rafraîchi et **non libéré**. La réception parent et les preuves finales sont volontairement restantes ; **ne pas poser PRET sur la seule base de ce candidat**.
