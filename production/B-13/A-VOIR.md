# B13 — à ouvrir sur la seule démonstration fictive

## Réception corrigée après la relecture de 22h30

Référence courante : `reception-corrections-V2.json`. Capture : `browser-corrections-final-V2.png`. **34 contrôles natifs, 123 navigateur**, dont chaque image des neuf articles sélectionnés sur chacune des six surfaces. Séquence B08 → B13 → B08 → B13 réellement jouée dans une transaction annulée, lien S'abonner réparé sans nouvel item. Retrait direct d'une relation couvert, et identifiants exacts comparés pour les limites 1, 3 et 10 sur deux thématiques temporaires de douze articles. Données, profils et sessions rendus à leur départ, copies de seeds retirées.

Défaut technique appliqué : hors préparation de la démonstration, un récent sans image reste sélectionné sans image, jamais remplacé, exclu ou habillé d'un placeholder. La démonstration courante a bien neuf images synthétiques, une par article sélectionné. Alphabet conservé, sur-invalidation save_post laissée (sans risque), dépendance à la classe `imagine-nav-thematiques` documentée au README. Connexion inchangé. Les paragraphes ci-dessous décrivent la première livraison et ses preuves historiques ; les commandes natives/navigateur courantes sont celles de corrections.

- Accueil : http://192.168.129.32:8085/
- Article réservé : http://192.168.129.32:8085/demo-2026-t4-reserve-1/
- Numéro : http://192.168.129.32:8085/numeros/demo-2026-t4/
- Attente abonnement : http://192.168.129.32:8085/abonnement-en-attente/
- Réglage administrateur : Réglages → Menu principal (3 articles par thématique par défaut).

Les huit entrées sont conservées dans l'ordre ; trois thématiques ont chacune une sélection titre/image/lien, sans extrait ni corps. Tout reste visible sans JavaScript, aucun habillage ajouté. Connexion reste Connexion, même connecté, et ouvre le compte. Les anciennes sous-pages de Notre coopérative restent présentes. La grande hauteur du menu est volontairement non maquettée.

Capture : `browser-final-V2.png`, navigateur réel sans JavaScript, anonyme ; les six surfaces anonymes/A-PAPIER sont dans `browser-final-V2.json`. Les publications/dépublications et thématique vide sont éprouvées nativement dans une transaction annulée et comparée ; aucun menu ni profil laissé altéré par les essais. Trois illustrations réservées B13 et une page d'attente sont les seules nouvelles données fictives permanentes.

```text
python -B production/B-13/verifier.py
python -B production/B-13/verifier.py --live
python -B production/B-13/qualifier.py
python -B wp/outils/demo/b13-corrections.py native ETIQUETTE_NEUVE
python -B wp/outils/demo/b13-corrections.py browser ETIQUETTE_NEUVE
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Réception `reception-V2.json`. La matrice C26 n'est pas étendue : ses témoins historiques sont relus, complétés par les corps réservés natifs courants. Le premier inventaire sans fixture temporaire C26 n'avait pas ses marqueurs coopérateurs ; correction du banc seulement, source C26 inchangée. Sonde zéro HTTP/mail et mutations de détection positives. Sessions A-PAPIER restaurées, sonde retirée. Aucune donnée de visiteur saisie ou exportée. Choix manuel des articles et forme du menu : questions pour Imagine/le designer, non construits.

PRET technique seulement, validation visuelle attendue. Aucun compte réel, envoi, paiement ni déploiement.
