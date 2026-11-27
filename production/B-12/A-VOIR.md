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
```

Rejouer la preuve native en créant/supprimant seulement les deux essais fictifs, sous transaction (utiliser des labels **neufs**, les reçus existants ne sont jamais remplacés) :

```powershell
python -B wp/outils/demo/b12.py mutant parent-mutation-NEUF-V2
python -B wp/outils/demo/b12.py runtime parent-natif-NEUF-V2
python -B wp/outils/demo/b12-neighbors.py parent-voisins-NEUF-V2
```

Image et rejeu standard, commandes inchangées :

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Résultats reçus : mutation **6 tentatives / 0 transport**, verrou **56 contrôles / 0 tentative** ; B12 PHPUnit **5 tests / 37 assertions** ; lecteur de preuves **6 tests** ; rejeu **1 200 tests / 36 610 assertions**, 22 outils / 720 contrôles, zéro échec/erreur de suite. Paquets A31/A32 rouges hors lot, codes exacts dans `NOTE.md` et réception.

**Fichier partagé changé :** bootstrap `imagine-site.php`. Complément voisin dans `reception-complement-voisins-V2.json/.log` : B11 32/35, C28 31/37, C27 628 ; natifs B11 23 et C28 25. Historiques intacts, empreinte historique de la portion hors ajout B12 contrôlée ; les vérificateurs bruts B11/C28 gardent leur refus de l'empreinte entière changée.

`PRET` = prêt technique à relire sur `reception-V2.json`, pas validation visuelle, clôture ou accord sur le réel. Aucun nouveau réglage, compte, donnée réelle, email ou transfert de paiement.
