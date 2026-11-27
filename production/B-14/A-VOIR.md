# B14 — à ouvrir sur imagine-test-demo seulement

## Réception corrigée de la fusion B14

Référence courante : `reception-corrections-V2.json`, capture `browser-corrections-final-V2.png`. **22 contrôles natifs, 52 navigateur**, clic réel depuis le paywall vers `/#imagine-abonnement`, cible unique avec S'abonner. Helper unique de sélection du libre partagé par B04/B14 ; deux libres d'ordres distincts puis égaux testés avec comparaison d'IDs. Nouveau vrai rendu `Accueil::rendre` sous bouchons minimaux en processus PHPUnit séparé : garde-fou structurel rejouable, découvert dans le JUnit (2 tests B14).

**Partage modifié explicitement :** `single-imagine_numero.php` et `inc/catalogue.php`. Complément B11 de 23 contrôles natifs et diff strict limité à l'extraction du libre dans `complement-B11-corrections-V2*.json`. Aucun rendu média/audio changé ; anciens reçus B11 conservés, leur empreinte historique du gabarit n'est pas prétendue courante.

**Limite honnête B01 :** les deux recettes demandées ont été exécutées, mais restent rouges sur contrats historiques (token PDF et absence de JS, inventaire limité à B00/C08). Voir `legacy-B01-corrections-V2.json`, pas un succès fabriqué ni une réécriture de B01. L'ancre courante est prouvée par le vrai chemin HTTP. Première tentative bloquée par html5lib absent, reçue en log ; dépendances ajoutées uniquement dans scratch privé, puis vrais essais. La dérive 1206→1208 vient exactement des deux tests B15 / cinq assertions, **pas** d'A32/A33 : `derive-comptage-V2.json`.

Dernier rejeu corrigé : **1209 tests / 36693 assertions PASS**, 23 outils / 852 contrôles / 0 échec, 13 paquets / 0 échec. Les paragraphes suivants restent l'historique de la première livraison. Question de repli si pages absentes conservée non bloquante, aucune règle visuelle nouvelle inventée.

Accueil : http://192.168.129.32:8085/

Sous le menu B13, regarder dans l'ordre : numéro en cours (couverture fixe, titre, date, résumé), conversion, reportage en accès libre, newsletter par lien, thématiques, événements futurs (maximum trois), Soutenir, coopérative, partenaire du mois avec **Partenariat**. Les Derniers articles de B01 sont retirés. Aucun habillage, vidéo, iframe ni animation ajouté. L'ancre Thématiques du menu reste valide.

Le numéro est le plus récent publié selon B04. Le reportage est celui que la page numéro désigne déjà ; son illustration est uniquement la couverture synthétique existante, assignée si l'image à la une manquait. Pas de nouvelle règle métier ni de second réglage. Le numéro courant n'est pas en vente : Acheter ce numéro est absent dans cette démo. Un produit de test fictif créé et retiré uniquement dans une transaction annulée prouve le cas positif, puis la disparition du lien après dépublication avec état natif relu. Aucun achat effectué.

Capture : `browser-final-V2.png` ; vraie navigation sans JavaScript, anonyme et A-PAPIER, contrôle identique des neuf sections. 17 contrôles natifs, 45 contrôles navigateur ; refus des mutations vidéo, iframe, saisie newsletter, Derniers articles, bouton hors vente et témoin réservé. Restauration des données/sessions relue et sonde retirée. Images secondaires lazy/low, une seule eager/high avec dimensions. Zéro tentative HTTP/mail dans le rendu, témoins positifs bloqués avant transport.

```text
python -B production/B-14/verifier.py
python -B production/B-14/verifier.py --live
python -B production/B-13/qualifier.py B-14
python -B wp/outils/demo/b14.py native ETIQUETTE_NEUVE
python -B wp/outils/demo/b14-browser.py ETIQUETTE_NEUVE
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Réception `reception-V2.json`. Image réellement préparée ; REJEU 1206 tests / 36680 assertions PASS, OUTILS 23 / 852 / aucun échec. A32_PACKAGE_DRIFT connu, A33_GATES_INVALID en cours sans PRET ; aucun contenu V1 modifié. Socle, banc B13 et matrice C26 inchangés. Le vieux contrôle B05 de la liste Derniers articles devient historique parce que B14 supprime explicitement cette section ; son contrôle d'étiquette du partenaire est conservé, avec le même sélecteur et le même composant B05. Aucun nouveau message de visiteur collecté. PRET technique, visuel à valider, aucun GO réel.
