# B-11 — à ouvrir et à rejouer

1. **Ouvrir** l'article `http://192.168.129.32:8085/wp-admin/post.php?post=3454&action=edit` puis le numéro `http://192.168.129.32:8085/wp-admin/post.php?post=11&action=edit` ; déplier « Boîtes méta » puis « Vidéo et podcast ».
2. **Saisir** `https://video-fictive.example.invalid/TEST_CED` et `https://podcast-fictif.example.invalid/TEST_CED`, puis **Enregistrer** dans chaque éditeur.
3. **Recharger**, vérifier les deux champs, puis rétablir la vidéo `https://video-fictive.example.invalid/B11_VIDEO_FICTIVE?a=1&b=2` et le podcast `https://podcast-fictif.example.invalid/B11_PODCAST_FICTIF`, enregistrer et recharger.

## Réception courante du 27 novembre 2026 — politique 13h30, PRET technique

**Preuve courante : `reception-politique1330-V2.json`.** Limite admise : aucun parcours de saisie/enregistrement/rechargement UI automatisé n'est prétendu ; les trois lignes ci-dessus sont pour Ced. La boîte est réellement proposée par le code de l'éditeur blocs livré pour les deux objets : déclaration `advanced/default`, compatibilité blocs native par défaut, registre filtré et champs rendus. **Pas de défaut de déclaration : aucun code fonctionnel corrigé.** La preuve de persistance est backend, pas UI.

Depuis `C:\Users\Ced\imagine`, commandes exactes du parent :
```powershell
python -B wp/tests/demo/b11-verifier.py
python -B wp/tests/demo/b11-verifier.py --live
```
**Sortie attendue : `PASS`, code 0.** La seconde commande ajoute uniquement des lectures du site fictif. Les sources actuelles, preuves neuves et reçus historiques sont contrôlés. Ne pas relancer les deux anciens outils `b11-finaliser.py` / `b11-receive-corrections.py` : leurs réceptions sont historiques.

### Résultats réels et limites
- Atteignabilité par lecture du code WordPress installé et rendu natif des deux champs : **11/11**, `politique1330-editeurs-final-V2.json`. Aucun filtre d'éditeur ni correction de la boîte.
- Vrai formulaire `options.php`, **16 options**, observateur passif : OFF → ON → OFF. Valeurs effectives strictement conservées pour les autres options ; les cinq absentes devenues explicites à leur défaut exact sont nommées et détaillées dans `NOTE.md`, le reçu et `politique1330-final-V2-details.json`. Aucun préremplissage, aucune différence réelle masquée.
- Recette adaptée **102/102** ; changement/effacement et refus d'hôte par vrai hook serveur `save_post` avec nonce/capacité, non par l'éditeur navigateur. Backend transactionnel distinct après code final **8/8**, deux mutations no-persist détectées, état restauré : `politique1330-ecritures-V2.json`.
- **32 sorties étanches non vides**, 32 témoins C26 inchangés ; deux mutations réelles des gardes et 36 injections de réponse détectées (nombres distincts). Gravatar public réellement déclenché et bloqué avant transport, contrôle rouge ; jamais excepté au titre de l'admin.
- Aucun tiers public dans OFF/ON, aucun HTTP/oEmbed/mail B11. Tentatives ambiantes bloquées : 54 Novamira, 2 dispatchs locaux Action Scheduler identifiés par chemin et pile, 6 autres observations HTTP ; 9 Gravatar admin bloqués. Le GIF tiers des anciens essais éditeur reste un tiers, pas une exception nouvelle. Reçus rouges de qualification réseau conservés sous `avant-qualification-*`.
- **16 restaurations relues** : lignes, métas, options et absences SQL, sessions/préférences, styles, sources, état métier ; sondes absentes. Pas de nouveau compte/profil/droit/achat permanent.
- PHPUnit B11 **4/34**, natif **23/23**, preuves **9 tests**. `politique1330-image-V2.*` sortie 0 ; `politique1330-rejeu-V2.*` : **1 195 tests / 36 573 assertions**, **22 outils / 720 contrôles**, verts. Bilan distinct : 12 paquets, 2 rouges hors B11 (`A31_PARTIAL_EVIDENCE`, `A32_PACKAGE_DRIFT`), non réparés ni rescellés.
- Complément sur voisins non clos C27/C28 après actualisation de la seule section B11 du README partagé : `politique1330-voisins-V2.json`. Historiques `reception.json`, `reception-corrections-V2.json` et documents bloqués de 12h58 conservés. B12 non implémenté, `catch` Paywall intact ; limite URL collée dans le corps reportée selon la nouvelle file.

Rejeux indépendants (étiquettes réellement neuves, jamais en parallèle d'une autre recette du site fictif) :
```powershell
python -B wp/outils/demo/b11-local.py parent-B11-unitaire-NEUF
python -B wp/outils/demo/b11.py runtime parent-B11-natif-NEUF
python -B wp/outils/demo/b11-write-witness.py parent-B11-ecritures-NEUF
python -B wp/outils/demo/b11-recette.py parent-B11-recette-NEUF --policy-1330
python -B wp/tests/demo/b11-proof-tests.py
```
La recette est temporairement mutante sur **imagine-test-demo seulement**, garde B00 conservée, préimage privée durable et restauration/readback dans `finally`. Elle ne visite pas les éditeurs, ne touche ni droits ni paiements. Ne pas employer le mode historique sans `--policy-1330` comme critère actuel. `b11-receive1330.py` a servi une fois à produire la réception neuve et PRET, refuse de les écraser ; les deux commandes du début vérifient sans réécriture.

<details>
<summary>Dossier historique avant corrections — résultats et commandes non actuels, ne fondent plus PRET</summary>

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

Les résultats de cette section sont ceux de la réception historique `reception.json`, conservée, et non la réception courante. La recette classique historique ne prouve pas les éditeurs livrés. Pas de consentement réel ni fournisseur intégré, aucune validation visuelle donnée par Ced.
</details>
