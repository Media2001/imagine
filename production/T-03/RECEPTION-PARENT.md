# T-03 — reception par le parent (pas de PRET)

**Candidat non natif.** Aucun Docker/WSL ni PHP Windows lance par ce worker ; aucun paquet externe, import ou gardien modifie par lui. **Surveillance : `wp/outils/staging/lib.php` a change concurremment depuis le snapshot d'entree ; les fichiers du gardien commun n'ont pas change.** Ce delta observe est conserve dans le recu local, sans l'attribuer a une execution T-03 ni le resceller. La chaine reelle attend le proprietaire Docker A-28 puis l'integration du parent. Les tests locaux sont uniquement des contrats Python, parseurs PowerShell et doubles explicites de frontiere, **jamais** des recus natifs.

## Ce qui est livre

- Decouverte `production/<lot>/verify.py` avec declaration fermee `rejeu.json` (contrat complet : `CONVENTION.md`). Processus Python sans argument dans le meme conteneur, stdout/stderr du verificateur retenus, premiere erreur declaree nommee, journal declare absent = hors rejeu.
- Une ligne `PAQUETS` independante, avant `OUTILS` ; derniere ligne `REJEU`, compteurs PHP/outils et code retour non modifies par un rouge de paquet. L'ancien montage `/repo/wp:ro` est conserve ; ajout strictement inspecte de la racine du depot a `/packet-repo:ro`. Tous les autres drapeaux et le nettoyage de proprietaire sont conserves.
- Python standard ajoute **uniquement** au Dockerfile deja utilise par `preparer-image.ps1` ; sonde hors reseau dans `verifier-image.php`. Le preparateur lui-meme est inchange. Bornes : 90 s par verificateur, budget collectif 120 s, enveloppe du collecteur 150 s ; timeout global T-01 de 600 s inchange.
- Exactement trois lignes ajoutees au vrai mode d'emploi T-01, `production/T-01/notes.md` (c'est le fichier prescrit au brief T-01 ; pas de README racine modifie). Contrat sur ces trois lignes seulement, dans `readme-ajout.txt`.
- `wp/tests/t01/test-paquets-native.ps1` prepare la vraie preuve : copie scratch complete des arbres wp/production/files, rejeu vert avec A-22 ET A-28, changement d'un seul octet de `production/A-28/preuves/final/before/native.json`, second rejeu exigeant uniquement A-28 PACKAGE_DRIFT et une derniere ligne REJEU PASS identique, lecture des deux nettoyages verifies, destruction de la copie et empreinte du recu original inchangee. **Ce script n'a pas ete execute ici.**

Les matrices natives classique/HPOS et commerciales restent hors du rejeu T-01 : verifier leurs recus ne les relance pas.

## Integrer d'abord les lots 20–29, sans rescellement artificiel

Le worker n'a ecrit ni entree ni declaration dans un autre lot. Au premier examen, seuls `production/A-26/verify.py`, `A-27/verify.py` et `A-28/verify.py` existaient ; aucune declaration `rejeu.json` n'etait presente. Les verificateurs A-21/A-22 lus sont `wp/tests/a21/verify.py` et `wp/tests/a22/verify.py`, avec argument de paquet obligatoire. Les wrappers de production 21/22 annonces dans le contexte ne se trouvaient donc pas a l'emplacement de decouverte lors de cet examen ; le parent doit confirmer leur emplacement/arrivee avant le gel, pas supposer leur presence.

Le parent integre, **lot par lot**, une entree sans argument pour les anciens paquets A-20 a A-25 (reutiliser un wrapper deja livre s'il existe). Cette entree selectionne le paquet unique explicitement et appelle le verificateur existant sans changer un controle. A-26/A-27/A-28 et A-29 s'il livre une entree utilisent leur contrat courant ; aucune adaptation forcee d'un besoin Docker/reseau/ecriture/argument. Documenter pour chaque ancien lot quel fichier existant est appele et quel paquet unique est choisi.

Chaque lot rejouable recoit sa declaration avant le gel/rescellement du parent :

1. `schema:1`, `entrypoint:"verify.py"`, `requires:[]` pour une entree effectivement pure et sans argument ; sinon exigence fermee et hors rejeu.
2. `controls` = liste fermee de **tous** les codes/noms de controles possibles du verificateur courant (verts et rouges). Les sorties candidates A-21/A-22 ne deviennent pas pour autant une preuve des gates parent.
3. `logs` = liste exhaustive des journaux requis, tiree des manifestes et references, **meme absents**. Inclure ceux de `files/rapports/` pour les enveloppes A-26/A-27. Ne pas construire cette liste par le seul glob des fichiers presents : les `.log` absents d'une copie Git sont hors rejeu, pas echec ni faux fichier reconstitue.

**Risque d'integration :** les inventaires A-26/A-27/A-28 couvrent leur dossier production ; ajouter `rejeu.json`/un wrapper APRES un gel peut perimer le paquet. Integrer ces entrees avant les nouvelles matrices et sceaux, selon la file 1 h 30 et la fusion A-28. Ne rien changer aux controles des verificateurs, au gardien ou a l'import pour rendre la ligne verte. T-02 scelle l'ancien runner : ses empreintes peuvent devenir historiques avec T-03 ; cela n'est pas une autorisation de resceller T-02 ou les autres lots par ce worker.

## Gates exactes — depuis C:\Users\Ced\imagine

Contrats locaux autorises, sans Docker/WSL reel :

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONIOENCODING='utf-8'; $env:PYTHONUTF8='1'
C:/Python314/python.exe -B -m unittest discover -s wp/tests/t01 -p test_paquets.py -v
C:/Python314/python.exe -B -m unittest discover -s wp/tests/t01 -p test_t03_integration.py -v
$env:PYTHONIOENCODING='cp1252'; $env:PYTHONUTF8='0'
C:/Python314/python.exe -B -m unittest discover -s wp/tests/t01 -p test_paquets.py -v
C:/Python314/python.exe -B -m unittest discover -s wp/tests/t01 -p test_t03_integration.py -v
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/t01/test-rejeu.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/t01/test-tools-summary.ps1
```

Les deux derniers scripts n'appellent que leur double fonctionnel de la frontiere WSL/Docker ; ils ne sont pas des preuves PHP. Leurs donnees synthetiques sont identifiees dans les scripts et sorties.

**Uniquement apres liberation Docker par A-28 et integration des paquets/declarations finaux :**

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
$N = 'C:/Users/Ced/AppData/Local/hermes/cache/scratch/t03-native-final-' + [guid]::NewGuid().ToString('N')
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/t01/test-paquets-native.ps1 -Output $N
```

Preparation : exiger le vrai `T03 IMAGE PYTHON ... PASS`, le succes de la preparation et la nouvelle image. Rejeu : conserver stdout complet, dernier REJEU PASS, meme nombre de tests PHP que le rejeu du parent avant T-03 sur les memes autres sources. La preuve sur copie doit produire `$N/result.json` status PASS, native_executed=true, quatre controles PASS, copy_absent=true, original_receipt_unchanged=true, A-22/A-28 dans les deux listes `lots` et une seule erreur nommee A-28 PACKAGE_DRIFT au mutant. Les journaux `green.log` et `one-byte.log` contiennent les sorties completes et les absences de conteneurs relues par le runner. Les autres paquets perimes doivent etre regles par leur proprietaire avant cette preuve strictement verte ; ils ne changent cependant jamais le REJEU d'un voisin.

Copier ensuite seulement cette preuve native finale et les contrats locaux finaux dans le paquet T-03, annoncer le nombre **mesure** de paquets verifies et la liste hors rejeu, puis le parent decide de PRET. Ici : aucun nombre de paquets natifs verifies n'est revendique, aucun conteneur cree, aucun PRET. Les preuves locales finales sont `preuves/local/result.json` et leurs fichiers `.txt` ; les RED restent exclusivement dans le scratch Hermes.
