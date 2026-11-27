# A-31 — Retouche du regroupement, file du 27 novembre 2026 à 19 h 30

## Contrat courant

K=5 porte sur `years`, `statuses`, **`natures` et les années de `refunds`**. Une cellule de 1 à 4 perd son libellé et rejoint `autres`. Les quatre liens cassés (`orphan_renewals`, `living_without_parent`, `orders_missing_account`, `orders_link_unknown`) restent distincts et exacts, y compris 0 à 4 ; `refunds.total` reste exact et vaut `autres` plus la somme des groupes annuels visibles. La lecture précédente « années/années-états seulement » est remplacée, pas conservée comme contrat courant.

Les cinq autres corrections restent : liens séparés testés seuls/mêlés ; rendu fermé JSON et Markdown avec liaison après fin du processus ; abonnement à la corbeille compté à l'existence, jamais vivant ; deux frontières UTC et ancienneté ; import, gardien et lanceur inchangés. Vivant = exactement `active`, comme A-19. Après le vrai neutraliser/anonymiser sur bases fictives, seul `natures` est inconnu après neutralisation, jamais zéro. L'outil ne répare, rattache ni supprime rien.

Le témoin d'altération cohérente JSON+Markdown modifie désormais `orphan_renewals` : les groupes rares de natures sont justement vides. La mutation reste un rapport valide refusé par la liaison finale, pas seulement un schéma invalide.

## Qualification réellement exécutée

- Une matrice complète classique/HPOS × UTF-8/cp1252, Windows `C:/Python314/python.exe` 3.14.6 ; stdout/stderr et mode UTF8 mesurés, TMPDIR retiré des enfants et mesuré `null`, TEMP/TMP sous le scratch Hermes.
- Par console : 42 tests Python, 276 assertions PHP pures, 19 de frontière, 552 contrôles natifs, 15 runner et 19 du standard installé dans chacun des deux magasins. Les 48 scénarios de liens par magasin/console restent présents, soit 192 exécutions natives ; empreintes DB/fichiers identiques avant/après. Canaris sur tous les canaux et rapports ; PHP uniquement dans les conteneurs jetables déconnectés, nettoyés et absence contrôlée.
- K5 des six natures et des remboursements/année testé à 0/1/2/3/4/5 ; cas mêlant rare/visible et total exact. Le RED préalable a réellement rendu 32 assertions PHP rouges et deux tests Python rouges ; reçus hors dépôt. Les témoins RED K5 et liens scalaires restent dans la matrice.
- Lecteur candidat : 324 contrôles PASS, exit 0. PSR-12 strict : 0 erreur et 0 avertissement. Les deux lignes communes A-31 sont contrôlées par contrat exact et unique ; le mode d'emploi commun n'est pas réécrit.
- Sept gates propres A-31 : préparation réelle de l'image, deux rejeux généraux et lecteurs A-20/A-21/A-22/A-28, tous exit 0, sources stables. Chaque rejeu : 1 204 tests, 36 667 assertions, 22 outils/829 contrôles, zéro échec ; `PAQUETS : 11 vérifiés, 0 échecs ; hors rejeu : A-31 (journaux absents)`. **Seul A-31 est exclu pendant cette préparation ; A-32 est effectivement vérifié et n'est pas retiré.** Aucune nouvelle séquence conjointe, aucun portail assoupli.

## Paquet unique et réception post-sceau

Scratch : `C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-retouche-20261127-2003/`.

- `avant-retouche/` conserve les préimages intégrales A-31 ; `ancien-paquet/` conserve manifeste, preuves et anciens reçus retirés sans perte. `PRET-avant-retouche` a été retiré par le parent avant les écritures.
- `matrix-final/` est l'unique matrice neuve complète ; `gates-final/` ses seules gates courantes. Après installation, l'unique paquet publié est `production/A-31/preuves/final/`, avec les gates sous `gates/`.
- Le sceau est calculé par `reseal.py`, sans substitution manuelle d'empreintes. Il ne crée pas PRET. Le lecteur de production sans argument doit ensuite être vert.
- Réception post-sceau hors paquet : `post-seal/reception.json` et journaux des deux consoles. Elle exige les 12 paquets dont A-31/A-32, zéro échec/exclusion, 1 204 tests/36 667 assertions, 22 outils/829 contrôles, sources et paquets inchangés. PRET A-31 n'est restauré qu'après ces contrôles. A-32 et son PRET ne sont pas écrits.
- T-03 n'est pas modifié. Sa photographie intégrale des voisins incluait l'ancien paquet A-31 : elle devient obsolète malgré ses propres source_hashes inchangés. Le verdict relu est retourné au parent dans `post-seal/t03-impact.json`, sans réactualiser son sceau.

## Commandes

Depuis `C:/Users/Ced/imagine`, étapes sérialisées sur répertoires scratch neufs :

```sh
C:/Python314/python.exe -B wp/tests/a31/matrix.py --include-native --parent-serialized --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-retouche-20261127-2003/matrix-final
C:/Python314/python.exe -B wp/tests/a31/verify.py --evidence=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-retouche-20261127-2003/matrix-final
C:/Python314/python.exe -B wp/tests/a31/gates.py --parent-serialized --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-retouche-20261127-2003/gates-final
C:/Python314/python.exe -B wp/tests/a31/reseal.py --parent-serialized --evidence=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-retouche-20261127-2003/matrix-final --gates=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-retouche-20261127-2003/gates-final
C:/Python314/python.exe -B production/A-31/verify.py
```

Puis deux exécutions réelles de `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1`, enfants Python en UTF-8 puis cp1252, TMPDIR absent. Le pilote scratch `postseal-a31.py` conserve les sorties complètes, mesure les consoles et ne restaure que PRET A-31 après vérification. Le rapport de réveil donne le résultat obtenu, pas une promesse de cette procédure.

Aucun Git, compte réel, archive Imagine, déploiement, voie 2, verrou, A-33 ni fichier gelé modifié. Aucun changement demandé dans le périmètre A-32. Ceci n'est ni une clôture éditoriale ni un GO réel.
