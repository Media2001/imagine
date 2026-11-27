# A-30 — corrections de la fusion 06h39 (27 novembre 2026)

**C01 corrigé et rejoué sous Windows ; M1/M2 documentés. Pas de PRET, pas de nouveau sceau, pas de qualification native revendiquée.** Sources A30 stabilisées pour le parent ; dernier rejeu Python à 06:56:11–06:56:16 CET. La fusion `corrections/A-30.md` reste inchangée : cette livraison applique ses instructions dans les seuls outils/tests/production A30.

## 1. Modifications livrées

- Nouveau `wp/tests/a30/temp_support.py` : point unique pour les quatre classes de fixtures (`test_core.py`, `test_cli.py`, `test_boundary.py`, `test_verify.py`). `os.environ.get('TMPDIR')` est une surcharge **optionnelle** ; valeur absente/vide → `tempfile.gettempdir()`, donc TEMP/TMP standards Python sous Windows. Garde résolue `assert_outside_repo` avant allocation et après création ; refus fermé `A30_TEST_TEMP_IN_REPOSITORY`, sans allocation dans le dépôt. Aucun accès obligatoire `os.environ['TMPDIR']`.
- `matrix.py` supprime explicitement TMPDIR des environnements fils, remplace TEMP/TMP par un répertoire privé sous le scratch Hermes autorisé, et sonde un **nouveau processus Windows**. Le parent du dernier essai portait volontairement `TMPDIR=a30-parent-value-must-not-be-inherited` : les deux fils ont bien constaté son absence. `--temp-root` permet de désigner un parent scratch autorisé hors dépôt ; défaut `C:/Users/Ced/AppData/Local/hermes/cache/scratch` sur ce poste. Le temporaire est nettoyé après exécution.
- Matrice : version/exécutable, stdout/stderr, locale/préférence, mode UTF-8, présence/valeur de TMPDIR, TEMP/TMP et `tempfile.gettempdir()`, compte découvert et compte exécuté réellement consignés. Résumés ambigus, compte discordant, erreurs, échecs et ignorés refusés. Les logs sont décodés avec l'encodage réel du fils, puis stockés en UTF-8 ; JSON également UTF-8. Empreintes du log et de la sonde liées à chaque ligne.
- `wp/tests/a30/verify.py` exige désormais ces preuves sémantiques (pas seulement un ancien compte >=17 et un hash). Les mutations de compte, d'encodage, de présence TMPDIR et d'environnement falsifié puis re-hashé sont testées. Ce lecteur ne fabrique jamais de preuve native.
- Nouveaux `test_temp_support.py` et `test_matrix.py` : **9 tests indépendants**, sans sous-classer les quatre classes métier. Les seuls héritages déjà présents dans les 25 tests historiques sont conservés. Refus de dépôt exercé sur un faux dépôt jetable sous scratch, pas sur le dépôt actif. Données fictives/public-safe ; aucune donnée de compte/site réel.
- `wp/outils/bascule/a30/README.md` : captures officielles datées et contrat du marqueur canonique `imagine_staging_disabled_plugins` (présence, pas contenu ; toute évolution impose adaptation/requalification A30). Absence de marqueur hors copie vérifiée : aucune certification d'anonymisation tierce. **Aucun changement de l'import, du staging, du gardien ou des six PHP A30. Axe produit `0` conservé.**

## 2. Résultats réellement exécutés

Interpréteur constaté : `C:/Python314/python.exe`, **3.14.6**, Windows `win32`. Aucun PHP Windows, Docker ou WSL exécuté par cette correction.

| Étape | UTF-8 réel | cp1252 réel | TMPDIR fils | Code |
|---|---|---|---|---|
| RED avant correction, 06:47:18 | `Ran 25 tests in 0.073s` ; `FAILED (errors=22)` | `Ran 25 tests in 0.071s` ; `FAILED (errors=22)` | absent | 1 / 1 |
| GREEN des quatre modules historiques | `Ran 25 tests in 1.561s` ; `OK` | `Ran 25 tests in 1.534s` ; `OK` | absent | 0 / 0 |
| GREEN final, découverte complète | **34 découverts, 34 exécutés ; OK** | **34 découverts, 34 exécutés ; OK** | absent, valeur JSON null | 0 / 0 |

Les deux RED contiennent **exactement 22 `KeyError: 'TMPDIR'`** chacun. Les RED des nouvelles régressions ont aussi été conservés avant implémentation : helper manquant/réemploi absent, fonctions de matrice manquantes, puis contrôle sémantique du lecteur manquant. Aucun reçu rouge remplacé par une sortie verte.

Sondes finales :

| Contexte | stdout / stderr | locale | preferred | utf8_mode | TEMP = TMP = gettempdir |
|---|---|---|---|---|---|
| UTF-8 | utf-8 / utf-8 | cp1252 | utf-8 | 1 | scratch Hermes `a30-clean-windows-raznsat9` |
| cp1252 | cp1252 / cp1252 | cp1252 | cp1252 | 0 | même scratch privé hors dépôt |

Zéro échec, erreur ou ignoré dans chacun des deux GREEN finaux. **25 historiques + 9 nouveaux = 34**, pas un ancien compte recopié. Les régressions du lecteur utilisent des fixtures de frontière explicitement étiquetées, pas des reçus PHP/natifs inventés.

### Emplacement des sorties brutes et empreintes

Tout le paquet de travail est **hors dépôt** :
`C:/Users/Ced/AppData/Local/hermes/cache/scratch/a30-corrections-0639-20261127/`.

- `red.json`, `red-utf8.log`, `red-cp1252.log` ; `red-temp-support.log`, `red-matrix-contracts.log`, `red-verifier-contract.log`.
- `green-original25.json` et ses deux logs : commandes, cwd, codes, résumés et hashes réels.
- `matrix-final/windows-matrix.json`, `utf8/environment.json`, `cp1252/environment.json` et les deux `python-tests.log` ; `matrix-final.stdout.log`, stderr vide.
- `final-verification.json` : commandes exactes, heures, codes, hashes des flux, inventaire/hash des sources finales, stabilité avant/après, conservation des pièces historiques et dépendances.

| Pièce finale | SHA-256 |
|---|---|
| Log Python UTF-8 | `aed23c3c647f26a1091aab923dfe59047bb1567ca19e6235f21d7062bfe49b1c` |
| Log Python cp1252 | `789c5628e7ff8d7ac172618271c76d28a341bacfd1987219cb643096d211d4a4` |
| Sonde UTF-8 | `ad1a5061bfc6fb3c188657ea77a1b4383e4d04be9655fdd0e2ab14ee634d4867` |
| Sonde cp1252 | `42bdeba3c8bb12c9d1d3f31d8b47bebf8e099ef3c9597bae2cd88011be0065b3` |

Commande finale réellement exécutée depuis `C:/Users/Ced/imagine` (parent volontairement empoisonné, fils nettoyés par la matrice) :

```sh
TMPDIR=a30-parent-value-must-not-be-inherited PYTHONIOENCODING=utf-8 C:/Python314/python.exe -B wp/tests/a30/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a30-corrections-0639-20261127/matrix-final --temp-root=C:/Users/Ced/AppData/Local/hermes/cache/scratch
```

## 3. M1 — deux captures officielles hors dépôt

HTTP **200**, URL finale identique à l'URL demandée ; octets HTML, en-têtes HTTP et date de collecte conservés dans `official-sources/captures.json`, avec les deux HTML et leurs extractions texte lisibles à côté. Captures du **27 novembre 2026 à 05:49:56 UTC / 06:49:56 CET**.

| Page officielle | Taille HTML | SHA-256 des octets capturés |
|---|---:|---|
| `https://woocommerce.com/document/product-csv-importer-exporter/` | 325127 octets | `a747cf7017ebbb95e957413285f64bbb2e3ffad00be957ec55f35e451435093a` |
| `https://woocommerce.com/document/subscriptions/migrating-subscribers-woocommerce-subscriptions/` | 263301 octets | `00982fa8a641500b5c1918741fe3406d6c8f45ab1b5bbb484c25912828ad4bb2` |

Lecture effectuée : import de produits ; ajout manuel d'une souscription liée à un client ; CSV Importer gratuit en bêta publique et ses limites de migration/support. Aucune extension téléchargée/installée. **Doute maintenu explicitement** sur les deux anciennes URL supposées 404 : non recapturées, ni nécessaires au choix sur-mesure en lecture seule. La capture prouve le contenu reçu à cette date, pas sa pérennité distante.

## 4. Préservation, réserve de concurrence et statut des sceaux

- **144 fichiers historiques de production A30** vérifiés identiques octet pour octet à la sauvegarde initiale, hors retrait du seul PRET. `preuves/final/`, `manifest.json`, `rejeu.json`, `parent-gates.json`, `seal-order.json` et la réception historique n'ont pas été réécrits. **Six PHP A30 inchangés** ; **48 dépendances** identiques aux empreintes du reçu natif historique (import/staging/gardien compris). Aucun autre lot ni voie 2 retouché.
- Le PRET trouvé portait réellement `2026-11-27T05:45:37.484035+01:00` (et non une date reconstruite à partir du contexte). Ses octets sont sauvegardés sous `before/production/A-30/PRET` hors dépôt ; marqueur actif retiré. **Aucun nouveau PRET créé.**
- Les lecteurs ont été réellement relancés en lecture seule : `production/A-30/verify.py` → code **1**, `PACKAGE_DRIFT` ; `wp/tests/a30/verify.py` → code **1**, `native_proven=false`. C'est le refus attendu d'un paquet historique dont les sources ont évolué, **pas un succès natif actuel**. Logs réels conservés. Aucun hash de paquet n'a été changé pour masquer cet état.
- **« Arbre propre » reste une réserve de clôture**, pas une instruction exécutée : aucun Git, reset, suppression/restauration d'autres lots ou élargissement de gel à la voie 2. La fusion relève un écart historique global 1157/36234 contre 1153/36075, attribué à des sources concurrentes A31/demo ; ce n'est pas un nouveau résultat de cette correction. Le parent doit fixer les sources par owner, attendre leur stabilité, puis mesurer les comptes globaux réellement obtenus. Aucun compte PHP actuel n'est annoncé ici.

## 5. Remaining — commandes exactes réservées au parent après T03 stable

**Non exécutées ici.** Un seul propriétaire Docker/WSL : le parent/agent T03. Import et gardien restent gelés. Ne pas rejouer parallèlement une préparation/sweep et un runner utilisant le même label. Les chemins de sortie ci-dessous doivent être absents ; choisir un nouveau suffixe si une exécution antérieure les occupe.

Depuis `C:/Users/Ced/imagine`, dans le shell Bash de ce poste :

```sh
# 1. Parent seulement, une fois les sources owners stabilisées.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1

# 2. Matrice réelle Python + PHP natif classique/HPOS dans les deux encodages.
C:/Python314/python.exe -B wp/tests/a30/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a30-parent-apres-T03-0639 --temp-root=C:/Users/Ced/AppData/Local/hermes/cache/scratch --with-native

# 3. Style PHP strict, uniquement A30, en runner natif autorisé.
C:/Python314/python.exe -B wp/tests/a30/style.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a30-parent-apres-T03-0639/style
```

**Rendez-vous packaging parent entre 3 et 4 :** conserver le paquet natif historique intact hors dépôt avant remplacement éventuel ; installer uniquement les sorties réellement vertes du nouveau paquet, mettre à jour la déclaration de rejeu réelle et le manifeste selon la procédure parent. Les empreintes de sources de la matrice, du style et du paquet natif doivent coïncider. Ce rapport ne fournit ni ne simule ce rescellage. Sans ce rendez-vous, les lecteurs ci-dessous doivent rester rouges.

```sh
# 4. Lecteurs sans argument après véritable installation/scellage parent.
C:/Python314/python.exe -B wp/tests/a30/verify.py
C:/Python314/python.exe -B production/A-30/verify.py

# 5. Gates globales après stabilité de tous les owners et des paquets.
# TEMP/TMP standards Windows sous scratch ; aucun TMPDIR transmis.
env -u TMPDIR TEMP=C:/Users/Ced/AppData/Local/hermes/cache/scratch TMP=C:/Users/Ced/AppData/Local/hermes/cache/scratch PYTHONIOENCODING=utf-8 PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1

env -u TMPDIR TEMP=C:/Users/Ced/AppData/Local/hermes/cache/scratch TMP=C:/Users/Ced/AppData/Local/hermes/cache/scratch PYTHONIOENCODING=cp1252 PYTHONUTF8=0 PYTHONDONTWRITEBYTECODE=1 powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Conserver stdout/stderr et codes réels de chaque commande, les sondes, comptes PHP effectivement obtenus et traces de suppression des runners. `rejouer.ps1` produit sa sortie PowerShell canonique UTF-8 ; les encodages Python réels restent ceux attestés séparément par la matrice. Tout nouvel écart de source invalide les preuves correspondantes et impose un nouveau paquet, sans réécriture des échecs historiques. **Clôture, sceau et PRET restent au parent ; aucun GO d'import ni accès au réel, site, archive, compte ou voie 2.**
