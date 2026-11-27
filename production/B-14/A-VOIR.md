# B14 — à ouvrir sur imagine-test-demo seulement

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
