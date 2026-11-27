# B15 — pied de page de la démonstration fictive

À ouvrir :
- http://192.168.129.32:8085/
- http://192.168.129.32:8085/demo-2026-t4-reserve-1/
- http://192.168.129.32:8085/numeros/demo-2026-t4/
- http://192.168.129.32:8085/my-account/ (Mon compte, adresse native relue dans la preuve)
- http://192.168.129.32:8085/faq-service-client/ (contrôle complémentaire du contexte du menu).

Les cinq zones, toujours dans cet ordre : Abonnement vers la page d'attente B13 ; Newsletter par lien, sans saisie ; même numéro que l'accueil, couverture miniature ; Trouver un point de vente vers B10 ; Mentions, menu existant conservé. Les cinq liens B09 sont présents chacun une fois ; le lien Points de vente ajouté antérieurement au menu par B10 reste également présent. Aucun menu recréé, aucun indicateur de page courante conservé dans ce seul menu de pied pour que le rendu reste identique. Le menu principal n'est pas modifié.

Capture : `browser-final-V2.png`. Le navigateur compare **le HTML brut entier du footer, sans normalisation**, sur cinq pages × anonyme/A-PAPIER : dix réponses identiques. Le mode lecture B03 masque déjà le footer ; vérifié par la feuille de style réelle, aucun changement de B03. Quatre contrôles purs, 15 natifs, 155 navigateur ; sonde retirée, sessions et métier restaurés. Publication d'un numéro fictif plus récent puis dépublication, états natifs relus : cache renouvelé puis retour exact au fragment initial, tout dans une transaction annulée.

Limites de banc documentées : deux rendus de `wp_nav_menu` dans une même requête PHP dédupliquent les IDs ; le contrôle natif neutralise uniquement ces IDs connus, pas le contrôle HTTP. Le premier HTTP FAQ a réellement trouvé les classes natives `page_item/page-item-ID` encore variables : RED pur conservé, correction du seul rendu footer, puis dix réponses HTTP strictement identiques. Aucun état utilisateur, droit ou menu stocké changé. Aucune géolocalisation navigateur/IP, ni carte/service tiers ; zéro HTTP/mail et mutations témoins de saisie/script/geo et des témoins C26.

```text
python -B production/B-15/verifier.py
python -B production/B-15/verifier.py --live
python -B production/B-13/qualifier.py B-15
python -B wp/outils/demo/b15.py pure ETIQUETTE_NEUVE
python -B wp/outils/demo/b15.py native ETIQUETTE_NEUVE
python -B wp/outils/demo/b15-browser.py ETIQUETTE_NEUVE
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Réception `reception-V2.json`. Image préparée et vérifiée ; dernier REJEU **1208 tests / 36685 assertions PASS**, OUTILS **23 / 852 / zéro échec**, **12 paquets vérifiés / zéro échec**. Les rouges étrangers des passages précédents sont conservés dans leurs journaux historiques, sans correction de notre part. Aucun nouveau contenu de visiteur saisi, aucun email ni paiement. Structure seule, validation visuelle attendue ; aucun GO sur le réel. Socle et matrice C26 inchangés.
