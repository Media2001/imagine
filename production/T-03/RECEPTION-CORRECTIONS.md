# Réception des corrections T-03 — historique du 27 novembre 2026

**Le reste de ce document est historique, pas le statut courant.** Pour la clôture du 28 novembre, lire `FINALISATION.md` : liste scellée de 13 paquets A-20…A-28/A-30/A-31/A-32/A-33, lecteur final borné à ses fichiers et à ses dépendances nommées. Les voisins ne sont contrôlés qu'une fois dans le reçu daté du sceau. Réception actuelle hors paquet : `C:/Users/Ced/AppData/Local/hermes/cache/scratch/t03-cloture-20261128/postpret/reception.json`. Le statut courant est exclusivement celui du marqueur exact et de `verify-final.py`, pas les nombres ni les présents de l'historique ci-dessous.

**État final : PRET posé après les gates de clôture, aucun GO.** Les blocages A-31/A-32 de 18 h 42 ont été levés par la réception conjointe parent à 19 h 30, sans modification de ces paquets ici. L'ancien PRET de 8 h 14 et son paquet restent historiques dans `C:/Users/Ced/AppData/Local/hermes/cache/scratch/t03-cloture-20261127-1829/historique-T03/`. Un seul paquet courant reste dans `preuves/final/` ; aucun paquet voisin rescellé.

**`verify-corrections.py` reste avant PRET seulement** : après PRET, son refus est intentionnel. **`verify-final.py` est le lecteur final read-only** ; il réutilise toutes les assertions d'évidence du candidat, puis vérifie gates nominale/un octet, gel exact, sources et logs de clôture et marqueur. `sceller-candidat.py` puis `finaliser.py` calculent les empreintes, vérifient leurs propres contrôles et restaurent le manifeste précédent en cas d'erreur ; aucun hash manuel. Toute nouvelle écriture source/notice exige une qualification neuve.

## 1. Six instructions appliquées

1. **C1, échéance commune** — `executer.php` établit l'échéance monotone de 600 s immédiatement après `declare`, avant découverte, copie, PHPUnit et outils. `paquets.php` reçoit ce même instant et utilise `min(150 s, temps restant - 5 s de publication - 1 s de grâce TERM/KILL)`. S'il n'y a plus de budget, il ne lance rien ; si la phase expire, seul `T-03 RUNNER_TIMEOUT` devient rouge. Le marqueur unique `T01_RESULT` reste émis après la phase et son `pass`/ses compteurs ne dépendent pas des paquets. **`wp/tests/rejouer.ps1` n'a pas été modifié** : timeout extérieur 600, montages et limites inchangés.
2. **C1, intégration réelle** — `test-corrections.py` lance le vrai PowerShell, le vrai conteneur et un vrai PHPUnit : un test dort 2 s, un outil pur dort 2,5 s et produit son vrai reçu, puis un vérificateur dort 10 s. Dans la seule copie jetable, le contrat énuméré remplace exactement `600.0` par `7.0` et la marge `5.0` par `1.0` dans les deux affectations PHP nommées. Aucun faux temps/tick, aucune variable de mutation de production, aucun changement du lanceur extérieur ou des assertions. Le paquet rouge borné conserve **REJEU : 1 tests, 1 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS**, et l'absence du vrai runner est relue. La consommation antérieure réelle et la marge/grâce laissent moins d'une seconde au vérificateur lent.
3. **S1, flux et descendants** — `paquets.py` utilise `Popen`, une session privée et des lectures concurrentes par sélecteur. Chaque canal est plafonné à 1 Mio pendant la lecture ; le bloc excédentaire n'est pas ajouté. Dès dépassement, SIGKILL vise le groupe, le fils direct est attendu et les pipes sont fermés ; seul `VERIFIER_OUTPUT` est rendu, jamais les flux privés. Le groupe est aussi supprimé sur sortie normale, délai individuel et TERM de la phase. Le handler TERM pose un drapeau, sans lever une exception asynchrone au milieu de `Popen` ; la boucle EOF/attente vérifie aussi ce drapeau. Deux producteurs **finis** de 2 Mio, l'un stdout et l'autre stderr, chacun avec un vrai fils et petit-fils, ont un observateur suivant qui vérifie leurs vrais PID dans `/proc` avant la fin du conteneur. Un test natif supplémentaire couvre les deux flux simultanés. Aucun stress OOM de l'hôte.
4. **A-20, consigne postérieure** — A-20 est **dans le rejeu** par consigne de **7 h 30 le 27 novembre 2026**, postérieure à la fusion et confirmée par la consigne 1 à 13 h 30. Ce n'est pas une divergence à arbitrer. L'ancien défaut hors rejeu est remplacé ; aucun fichier, contrôle ni reçu natif A-20 n'est modifié par cette passe. Le banc propriétaire exige les douze lots réellement observés, A-20 et A-32 compris.
5. **OUTILS** — première observation réelle de cette reprise : **22 outils, 791 contrôles, 0 échecs** ; **REJEU : 1204 tests, 36667 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS**. Aucun compteur n'est forcé. Les 584/1166 de 8 h 14 et les 582/1153 antérieurs sont historiques, pas des preuves des sources courantes. Les logs courants conservent les nombres réellement observés.
6. **Opt-in** — seuls les lots déclarés figurent parmi les vérifiés ; un lot absent de la ligne n'est ni vérifié ni compté hors rejeu. Les entrées sans déclaration restent nommées `declaration absente` ; A-20, déclaré, n'est plus dans ce cas. A-29 n'a pas été déclaré ni diagnostiqué.

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

- Python Windows réellement détecté : version et exécutable dans `result.json` et les sondes, sans recopier une ancienne version ; consoles UTF-8/cp1252, modes UTF-8 1/0 et **TMPDIR absent** mesurés. Le qualificateur retire TMPDIR à tous les processus fils ; les temporaires natifs restent explicitement sous Scratch. Le lecteur refuse une mesure absente ou TMPDIR présent.
- Dans chaque console : **15 contrats collecteur + 9 contrats d'intégration/préservation + 3 intégrations Docker réelles**. Les doubles restent identifiés et distincts des intégrations réelles.
- **7 tests natifs de flux/groupes**, lint PHP dans le conteneur, **32 tests de corrections PHP** et **24 contrats T02**, deux scripts de doubles PowerShell et le nominal observé.
- Lint et PHP natif ne sont jamais exécutés sur Windows. Les producteurs natifs sont finis ; tous les conteneurs possédés sont supprimés avec absence relue. Les copies jetables sont absentes.

Le lecteur du candidat vérifie 14 commandes terminées, leur exit réel, leurs flux hachés, les trois cas par console, la mesure des consoles, l'inventaire et les sources courantes. Son succès signifie **tests des corrections PASS**, jamais gate globale ou PRET.

## 3. Historique nominal et résolution finale

Le premier rejeu nominal réellement observé (`qualification-01`, avant réception A-30) affichait **10 vérifiés**, A-21 à A-28, A-30 et A-31 ; **A-20 seul hors rejeu**, et honnêtement quatre rouges :

- A-26 `SEALED_VERIFICATION_FAILED` ;
- A-27 `SEALED_VERIFICATION_FAILED` ;
- A-30 `PACKAGE_DRIFT` (autre agent de tests actif ; ni qualification ni rescellage A-30 ici) ;
- A-31 `A31_PARENT_GATES_MISSING`.

**Historique avant réception de 8 h 14, pas diagnostic courant** : ces dépendances communes avaient nécessité une vraie requalification, jamais un remplacement manuel d'empreintes. Ces étapes et leurs journaux ne sont pas ré-étiquetés comme preuves des sources actuelles.

**Historique de reprise à 18 h 42** : 12 lots tentés, aucune exclusion ; rouges A-31 `A31_PARTIAL_EVIDENCE` et A-32 `A32_PACKAGE_DRIFT`, REJEU PASS. Aucun contournement ou faux PRET n'a été posé sur cette base. **État final après réception conjointe parent** : 12 lots A-20…A-28/A-30/A-31/A-32, zéro échec/exclusion. La preuve native courante est nominale verte puis un octet A-28, A-28 PACKAGE_DRIFT seul, REJEU identique ; copie/conteneurs absents et original intact. Gates et gel exact dans `preuves/final/cloture/`, preuve un octet dans `preuves/final/native/`. Aucun changement A-31/A-32.

## 4. Commandes de réception/finalisation parent

La procédure finale courante est **`FINALISATION.md`**. Depuis `C:/Users/Ced/imagine`, séquentiellement, avec le même Python Windows :

```text
C:/Python314/python.exe -B production/T-03/verify-final.py
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Le premier est sans écriture, sans Docker et sans argument ; il valide l'état final avec PRET. Le lecteur `verify-corrections.py` reste avant PRET seulement, et refuse donc volontairement l'état final. La qualification, la preuve native et les gates de clôture ont leur unique preuve courante dans `preuves/final/`. `sceller-candidat.py` et `finaliser.py` ont calculé et contrôlé le sceau, jamais des empreintes remplacées à la main.

Exiger le lecteur PASS ; **PAQUETS : 12 vérifiés, 0 échecs ; hors rejeu : aucun**, A-20/A-31/A-32 présents ; OUTILS 22/791 vert ; REJEU 1204 tests/36667 assertions PASS ; marqueur T01_RESULT unique et nettoyage relu. Aucun runner concurrent. La preuve un octet n'a que A-28 PACKAGE_DRIFT en rouge, mêmes tests et REJEU, copie et deux conteneurs absents, original intact.

Le manifeste porte `status:PRET`, `readiness_claimed:true`, `parent_final_gates_pending:false` et l'empreinte du marqueur exact. Le reçu du rejeu séparé postPRET est **hors paquet** : `C:/Users/Ced/AppData/Local/hermes/cache/scratch/t03-final-20261127-postPRET/reception.json`. Il lie les fichiers exacts avant/après et deux rejeux UTF-8/cp1252 sans TMPDIR. Le parent peut rejouer sa propre réception read-only.

## 5. Limites et état conservé

Aucun Git, compte, site, réel, cron, montage ou limite modifié ; aucun A-29/A-33 repris. Aucun fichier t01/rejouer/import/gardien/outil clos/A-31/A-32/voie 2 modifié ; gel exact relu. Anciennes preuves hors dépôt ; aucun manifeste voisin rescellé. Verrou parent intact et non libéré. Les matrices métier natives restent hors rejeu. PRET technique n'est ni clôture par Claude ni GO réel.
