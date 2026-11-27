# B-11 — à ouvrir et à rejouer

**Site unique : `imagine-test-demo`. Toutes les données et adresses de médias sont fictives.** Aucun compte réel, aucun paiement, email, appel fournisseur ou ouverture de droit.

## Adresses
- Article réservé B11 : http://192.168.129.32:8085/b11-article-medias-fictifs/ — article 3454. Avec P-NUMERO ou A-CARTE : texte, « Voir la vidéo » et lien du podcast. Sans droit : extrait public seulement, ni lien ni adresse des deux médias, y compris dans le code de la réponse.
- Numéro acheté existant : http://192.168.129.32:8085/numeros/demo-2026-t1/ — numéro 11. Liens vidéo/podcast fictifs publics ; lecteur audio réservé à P-NUMERO. A-CARTE ne reçoit pas l'audio de cet ancien numéro : c'est le réglage C06 existant, pas un défaut B11.
- Numéro courant : http://192.168.129.32:8085/numeros/demo-2026-t4/ — numéro 39. A-CARTE dispose du même silence de trois secondes ; P-NUMERO n'a pas droit à ce numéro.
- Réglages : http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-reglages — section « Vidéos et podcasts », sous le bouton existant. Un seul hôte fictif `video-fictive.example.invalid`, intégration OFF. En ON : emplacement vide, aucun lecteur, vignette ou appel.
- Saisie article : http://192.168.129.32:8085/wp-admin/post.php?post=3454&action=edit ; numéro : http://192.168.129.32:8085/wp-admin/post.php?post=11&action=edit — boîte « Vidéo et podcast ». Un autre hôte est refusé, anciennes valeurs conservées.

Ne pas suivre les liens fictifs comme s'il s'agissait de services disponibles : `example.invalid` est volontairement inutilisable. Les identifiants de démonstration restent dans le rangement privé habituel ; aucun secret n'est dans ce paquet.

## Fixture laissée
- Article 3454, titre « B11 — Article médias entièrement fictif », extrait public explicite, corps `CONTENU_FICTIF_RESERVE_B11_VIDEO_PODCAST`, réservé, rattaché au numéro 11.
- Vidéo et podcast dans les champs séparés du numéro 11 et de l'article ; aucun collage dans le corps ou cache oEmbed créé par B11.
- Numéros 11 et 39 : même WAV fabriqué, trois secondes, 48 044 octets, stocké hors webroot dans le dossier privé de C11. Aucun fichier audio public ou attachment ajouté. Lecteur natif à la demande, sans autoplay.
- Option `imagine_b11_fixture` déclare les IDs et le silence fictif ; `_imagine_b11_fictif=1` sur l'article. Option `imagine_medias` : hôte unique fictif, OFF restauré. Les autres pages/numéros/profils/commandes restent ceux de la démonstration, sans nouvelle acquisition ni modification de droit.

## Commandes parent — à la racine `C:\Users\Ced\imagine`

Vérifications sans réécriture de preuve :
```powershell
python -B wp/tests/demo/b11-verifier.py
python -B wp/tests/demo/b11-verifier.py --live
```
La première est hors réseau ; la seconde relit uniquement le site fictif gardé, ses sources et sa fixture. `reception.json` contient les empreintes et résultats qui fondent PRET.

Rejeu indépendant si souhaité (LABEL-NEUF doit être réellement neuf) :
```powershell
python -B wp/outils/demo/b11-local.py parent-unitaire-NEUF
python -B wp/outils/demo/b11.py runtime parent-natif-NEUF
python -B wp/outils/demo/b11-recette.py parent-recette-NEUF
```
La recette est **mutante temporairement sur le seul site fictif** : formulaires HTTP, sessions, option B11, deux gardes de sources B11 ; préimage privée durable, restauration et readback obligatoires. Ne pas lancer en parallèle d'une autre recette de cette voie. Aucune matrice C26 étendue.

Commandes générales déjà exécutées avant PRET :
```powershell
.\wp\tests\preparer-image.ps1
.\wp\tests\rejouer.ps1
```
Leurs sorties et codes réels sont conservés dans `preparation-image.*` et `regression-finale.*` ; le paquet partiel A32 n'est pas dans le périmètre B11. La préparation de dépendances publiques ne lance pas le site.

Une réception neuve de ce même paquet se vérifie avec les deux premières commandes ; `b11-finaliser.py` a servi à produire une seule fois `reception.json` et `PRET` et refuse de les écraser.

## Résultats et limites
- PHPUnit B11 : **4 tests, 34 assertions**, zéro échec ; syntaxe PHP : **11 fichiers** analysés avec succès.
- WordPress natif transactionnel : **23 contrôles sur 23** ; recette HTTP/navigateur : **90 contrôles sur 90**, **32 sorties non vides** inspectées, zéro fuite hors des mutations voulues.
- **2 mutations réelles** de gardes B11 détectées puis restaurées ; **36 injections témoins** détectées sur réponse brute (dont les **32 témoins C26** livrés). Ces deux nombres ne sont pas confondus.
- Réseau : **0 appel B11**, **0 oEmbed B11**, **0 tiers public** dans OFF et ON. **27 tentatives Novamira ambiantes** sur les phases ciblées et **91 autres observations HTTP ambiantes**, toutes observées bloquées par B00 ; ce ne sont pas des appels B11 et elles ne sont pas cachées.
- Préparation d'image : sortie **0**, image `sha256:e50d691d9782faf3d7fed68d8d243f07df0663cc24d63af3cc8b0cb1b492d7cc`.
- Rejeu général : **1 179 tests, 36 441 assertions, 0 échec, 0 erreur, 0 ignoré — PASS** ; outils : **22 outils, 584 contrôles, 0 échec**. Paquets : **12 vérifiés, 1 échec connu `A-32 A32_PARTIAL_EVIDENCE`**, hors périmètre, inchangé.
- Vérificateur B11 : **17 contrôles offline**, **22 avec readback live**, tous verts.

Les résultats définitifs sont ceux des reçus `unitaire-final.log`, `natif-final.json`, `recette-finale.json` et `regression-finale.log`, lus par le vérificateur. La section « Limites explicites » de `NOTE.md` fait partie de la réception : tentatives ambiantes Novamira bloquées distinctes du zéro B11, premier essai avec empreinte usermeta résiduelle non reconstruite, recette de boîte classique seulement. Pas de consentement réel ni fournisseur intégré, aucune validation visuelle encore donnée par Ced.
