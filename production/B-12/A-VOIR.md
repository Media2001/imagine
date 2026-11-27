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
```

Rejouer la preuve native en créant/supprimant seulement les deux essais fictifs, sous transaction (utiliser des labels **neufs**, les reçus existants ne sont jamais remplacés) :

```powershell
python -B wp/outils/demo/b12.py mutant parent-mutation-NEUF-V2
python -B wp/outils/demo/b12.py runtime parent-natif-NEUF-V2
python -B wp/outils/demo/b12-corrections.py routes parent-routes-NEUF-V2
python -B wp/outils/demo/b12-corrections.py mutant parent-mutation-casse-NEUF-V2
python -B wp/outils/demo/b12-corrections.py bootstrap parent-complement-C29-NEUF-V2
```

Image et rejeu standard, commandes inchangées :

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Résultats **frais après correction** : mutation du verrou **6 tentatives / 0 transport** ; matrice générale **56 contrôles / 0 tentative** ; routes canonique/MAJ/mixed × cache absent/ancien **52 contrôles / 6 cas / 0 tentative**, liens seuls, ni iframe ni vignette, permissions refusées sans `edit_posts`. Rouge avant correction et mutation de la vraie source sensible à la casse : 2 tentatives B00 et anciens iframe/vignette détectés ; source et essais restaurés. B12 PHPUnit **6 tests / 47 assertions** ; lecteurs **6 historiques + 11 nouveaux tests** ; rejeu frais **1 204 tests / 36 667 assertions**, 22 outils / 720 contrôles, zéro échec/erreur/ignoré de suite. Paquets A31/A32 rouges hors lot, codes exacts dans `NOTE.md` et réception.

**Bootstrap partagé inchangé pendant cette correction :** `imagine-site.php`. Le complément initial B12 `reception-complement-voisins-V2.json/.log` reste historique. Le complément C29 est réutilisé, après contrôle de son sceau et de la portion ajoutée exacte, dans `correction-bootstrap-C29-V2.json` : retirer seulement C29 retrouve le bootstrap historique B12 ; branchement B12 intact, autres octets exacts, sources/preuves C29 et voisins conservés. `SOURCES` n'est pas neutralisé.

**Historique C29 :** son lecteur brut fige l'ancien PRET B12. Le nouveau PRET B12 périme ce seul contrôle `HISTORICAL_PACKETS` ; ancien PRET archivé octet pour octet dans `PRET-avant-corrections-V2` et relu contre le sceau C29 par le nouveau vérificateur. Les reçus/PRET/sources C29 restent intacts ; pas de resceau silencieux. B11/C28 gardent aussi leurs refus bruts historiques documentés. Détail et limites dans `NOTE.md`.

**À chaque montée de version du cœur WordPress**, rejouer les deux matrices natives et leurs mutations avant clôture. La suite scellée utilise des doublures et ne prouve pas le pipeline réel. Preuve native actuelle via WP-CLI/REST en processus, pas de capture UI ou de requête HTTP authentifiée depuis un navigateur ; B11 `UI_save_verified=false` inchangé, compteurs AUTO_INCREMENT non restaurables par rollback.

`PRET` = prêt technique à relire sur `reception-corrections-V2.json`, pas validation visuelle, clôture ou accord sur le réel. Aucun nouveau réglage, compte, donnée réelle, email ou transfert de paiement.
