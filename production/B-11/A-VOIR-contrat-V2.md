# B11 — réception courante au contrat, parcours Ced inchangé

1. **Ouvrir** l’article `http://192.168.129.32:8085/wp-admin/post.php?post=3454&action=edit` puis le numéro `http://192.168.129.32:8085/wp-admin/post.php?post=11&action=edit` ; déplier « Boîtes méta » puis « Vidéo et podcast ».
2. **Saisir** `https://video-fictive.example.invalid/TEST_CED` et `https://podcast-fictif.example.invalid/TEST_CED`, puis **Enregistrer** dans chaque éditeur.
3. **Recharger**, vérifier les deux champs, puis rétablir la vidéo `https://video-fictive.example.invalid/B11_VIDEO_FICTIVE?a=1&b=2` et le podcast `https://podcast-fictif.example.invalid/B11_PODCAST_FICTIF`, enregistrer et recharger.

Politique 13h30 conservée : **UI_save_verified=false**, 16 options effectives et témoin backend 8/8. Les trois lignes ci-dessus sont pour Ced, pas une validation UI déjà acquise. `A-VOIR.md` et `NOTE.md` demeurent les documents historiques exacts de cette preuve.

Depuis `C:\Users\Ced\imagine` :
```text
python -B wp/tests/demo/b11-verifier.py
python -B wp/tests/demo/b11-verifier.py --live
python -B wp/tests/demo/b11-c29-contract-tests.py B11
python -B wp/tests/demo/b11-proof-tests.py
```
Les lecteurs doivent sortir PASS/code 0 ; la qualification compte 12 tests, les assertions historiques 9. Sans `--live`, aucun réseau ; avec, seulement lectures de `imagine-test-demo` sous la garde existante. Réception neuve `reception-contrat-V2.json`, finaliseur à usage unique `wp/outils/demo/b11-c29-contract.py` (ne pas relancer : refus d’écrasement). Aucun code fonctionnel/bootstrap changé ; anciens reçus et compléments conservés, aucun PRET voisin requis. Ni clôture, validation visuelle ou GO réel.
