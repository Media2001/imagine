# B-12 — un lien, pas de lecteur

Site **imagine-test-demo uniquement** : `http://192.168.129.32:8085/`.

## Ce que Ced verra

- Dans un article, une adresse de vidéo seule sur une ligne, un bloc natif **Contenu embarqué** ou `[embed]URL[/embed]` affiche **un lien ordinaire**, sans lecteur, vignette ou script tiers. Le réglage d'intégration B11 ne change pas ce résultat.
- L'aperçu de l'éditeur reçoit seulement ce lien ; la route conserve ses permissions natives. Le texte saisi est conservé tel quel, y compris commentaires du bloc et antislash.
- Les intégrations du site lui-même restent natives ; B11 et le paywall ne sont pas modifiés. Ce lot n'est pas un filtre général des iframes HTML ajoutées à la main.

Les deux articles d'essai ont été **retirés** et l'état métier restauré : aucune adresse d'essai morte n'est proposée. Pour voir le résultat sans toucher un contenu existant : ouvrir `http://192.168.129.32:8085/wp-admin/post-new.php`, créer son propre brouillon fictif avec une URL seule, prévisualiser ; refaire avec le bloc « Contenu embarqué », puis retirer ses propres brouillons. L'automate ne revendique pas ce parcours UI : il exerce les mêmes chemins natifs sur deux articles temporaires. B11 `UI_save_verified=false` reste la limite acceptée à 13h30.

## Réception parent — commandes à la racine du dépôt

Lecture seule, sans argument puis lecture du site gardé :

```powershell
python -B wp/tests/demo/b12-verifier.py
python -B wp/tests/demo/b12-verifier.py --live
python -B wp/tests/demo/b12-proof-tests.py
python -B wp/tests/demo/b12-correction-proof-tests.py
python -B wp/tests/demo/b12-contract-proof-tests.py
```

Rejouer la preuve native en créant/supprimant seulement les deux essais fictifs, sous transaction (utiliser des labels **neufs**, les reçus existants ne sont jamais remplacés) :

```powershell
python -B wp/outils/demo/b12.py mutant parent-mutation-NEUF-V2
python -B wp/outils/demo/b12.py runtime parent-natif-NEUF-V2
python -B wp/outils/demo/b12-corrections.py routes parent-routes-NEUF-V2
python -B wp/outils/demo/b12-corrections.py mutant parent-mutation-casse-NEUF-V2
```

Image et rejeu standard, commandes inchangées :

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Résultats **frais après correction** : mutation du verrou **6 tentatives / 0 transport** ; matrice générale **56 contrôles / 0 tentative** ; routes canonique/MAJ/mixed × cache absent/ancien **52 contrôles / 6 cas / 0 tentative**, liens seuls, ni iframe ni vignette, permissions refusées sans `edit_posts`. Rouge avant correction et mutation de la vraie source sensible à la casse : 2 tentatives B00 et anciens iframe/vignette détectés ; source et essais restaurés. B12 PHPUnit **6 tests / 47 assertions** ; lecteurs **6 historiques + 11 nouveaux tests** ; rejeu frais **1 204 tests / 36 667 assertions**, 22 outils / 720 contrôles, zéro échec/erreur/ignoré de suite. Paquets A31/A32 rouges hors lot, codes exacts dans `NOTE.md` et réception.

**Réception courante par contrat, arbitrage de 16h30 : `reception-contrat-V2.json`.** Le vérificateur contrôle exactement les fichiers propres B12, l'unique bloc d'enregistrement B12 dans le bootstrap et la seule section README B12 (bornée avant le lot suivant). Ajout d'un futur lot dans l'amorçage accepté ; bloc B12 absent/modifié/dupliqué et source B12 modifiée refusés. Aucun sceau entier du bootstrap, ni PRET voisin, n'est une dépendance de cette réception. Tests de lecteurs : 6 historiques + 11 corrections + **7 tests de contrat**.

Les compléments B12/C29 et `reception-corrections-V2.json` sont désormais **historiques**, conservés bruts : l'arbitrage remplace l'instruction 3 de la fusion, il n'exige plus de réception complémentaire pour une simple ligne d'amorçage. Les anciens PRET B12 sont archivés dans `PRET-avant-corrections-V2` et `PRET-avant-contrat-V2`. Les lecteurs historiques B11/C28/C29 peuvent rester rouges, sans resceau silencieux ; migration par contrat de B11 et C29 à reprendre par le parent. Leur code/dossier de production et le bootstrap C29 n'ont pas été modifiés ici.

**À chaque montée de version du cœur WordPress**, rejouer les deux matrices natives et leurs mutations avant clôture. La suite scellée utilise des doublures et ne prouve pas le pipeline réel. Preuve native actuelle via WP-CLI/REST en processus, pas de capture UI ou de requête HTTP authentifiée depuis un navigateur ; B11 `UI_save_verified=false` inchangé, compteurs AUTO_INCREMENT non restaurables par rollback.

`PRET` = prêt technique à relire sur `reception-contrat-V2.json`, pas validation visuelle, clôture ou accord sur le réel. Aucun nouveau réglage, compte, donnée réelle, email ou transfert de paiement.
