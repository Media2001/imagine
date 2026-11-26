# A-16 — relais instructions 2 à 5 (en cours)

Ne pas sceller le manifeste ni PRET sur cette note : le parent finalise après les refus communs.

## Conflit d'intégration refus constaté

Le rejeu natif `a16-r1-green-20261126` a prouvé les PDF privés présent/absent en classic/HPOS, puis échoué sur `absent_mapping_key_named` : l'attente historique d'`inside.py` exige encore le détail `{"key":"absent_key"}` alors que le nouveau Runtime concurrent ne le rend plus. Le même fichier contient aussi une attente historique pour le détail drop-in. Ces assertions de refus ne sont pas modifiées par cet enfant ; parent/enfant refus doivent les aligner sur la règle fermée actuelle avant matrice finale et scellement. Aucun Runtime.php ni CLI ni test commun de refus touché ici.

La suite finale complète et ses empreintes restent à rejouer après intégration ; les essais restent en scratch.
