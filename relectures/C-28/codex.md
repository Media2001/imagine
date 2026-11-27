# C-28 — Relecture indépendante Codex

Date : 27 novembre 2026. Références : brief C-28, doctrine, cahier des charges §3.1 et §3.3, décision C-28 dans `docs/decisions.md:93`. Rapport Claude non consulté. Aucun accès à un site, une base ou un compte ; aucune modification hors de ce rapport.

## 1. Conformité

Le parcours nominal répond au brief : produit simple à prix global, sélection administrative de numéros, fiche avec couvertures/titres/dates, expansion vers la décision C14, compte et remboursement existants. Les cinq lignes « standard d'abord », le README, les données fictives déclarées, la capture et `PRET` sont présents. La décision enregistrée confirme la composition au paiement sans nouveau réglage ; son application ne nécessite pas de question métier supplémentaire.

**C28-01 — important — `wp/themes/imagine/single-product.php:36` : l'indisponibilité du pack ne bloque que son bouton.** Si un numéro inclus est dépublié après la création du pack, `PacksThematiques::numeros()` renvoie une liste vide pour tout le pack. La fiche masque alors l'achat, mais le produit simple conserve son prix et son statut publié : aucun raccord ne rend ce pack non achetable ni ne valide sa composition au panier/à la commande. Un panier constitué avant la dépublication, ou un ajout direct natif, peut donc aboutir à un paiement dont l'instantané est vide : aucun des numéros, même ceux encore publiés, n'est acquis. **Correction proposée :** faire respecter l'indisponibilité côté serveur dans les parcours natifs d'achat, y compris pour un panier déjà constitué, et refuser la commande tant que la composition est invalide. Ajouter un test de dépublication d'un numéro entre ajout au panier et validation, ainsi qu'un ajout direct. Constat statique, non rejoué sur Woo dans cette relecture.

## 2. Exactitude métier

Cas déroulés à la lecture du code et comparés aux preuves livrées :

- **Paiement puis évolution éditoriale :** `[11,18,25]` ne donne aucun droit avant paiement ; une fois l'instantané enregistré, C14 produit trois achats. Remplacer ensuite la liste par `[18,25,32]` conserve 11 et n'accorde pas 32. Le propriétaire est contrôlé par C14 et le compte utilise la décision PDF existante. Conforme dans ce parcours nominal.
- **Remboursement :** un partiel non ventilé ferme les trois droits en mode `commande`, les conserve en mode `ligne` ; rembourser la ligne pack ferme ses trois droits. Un remboursement total ferme les deux modes. Le code réutilise bien `AchatNumero::remboursement()`.
- **Rejeu normal :** une ligne ayant déjà `_imagine_pack_paye` n'est pas recalculée. Le cas d'un numéro déjà possédé ne déclenche aucune remise ; une ancienne ligne sans marque candidat n'acquiert pas rétroactivement un pack.

**C28-02 — important — `wp/plugins/imagine-site/PacksThematiques.php:53` : un instantané manquant peut être reconstruit après le paiement avec la mauvaise composition.** `payer()` est appelé à chaque sauvegarde de commande. Il exige seulement une commande payée/datée, une ligne candidate et l'absence d'instantané. Si le paiement est persisté mais que l'écriture de l'instantané échoue ou est interrompue, puis que la rédaction remplace `[11,18,25]` par `[18,25,32]`, une sauvegarde ultérieure relit cette dernière liste et l'enregistre avec l'ancienne date de paiement. L'acheteur reçoit alors 32 et perd 11, contrairement à la règle « au moment du paiement ». La limite de crash déclarée dans la note est recevable comme absence de récupération automatique, mais le défaut annoncé « fermé » ne reste pas fermé lors d'une sauvegarde ultérieure. **Correction proposée :** réserver la capture à la première persistance du paiement ; pour une commande déjà payée sans instantané fiable, conserver la fermeture et signaler l'anomalie sans reconstruire depuis le produit courant. Tester une panne après persistance du paiement, puis modification du pack et sauvegarde d'un objet commande rechargé. Constat statique ; aucune panne injectée pendant cette relecture.

## 3. Tests

- **Exécuté :** `python -B wp/tests/demo/c28-verifier.py` → code 0, `PASS`, **27 contrôles réussis**. Ce résultat vérifie les reçus, les empreintes des sources et les preuves ; il ne réexécute pas les parcours Woo.
- **Tenté :** commande Docker/WSL de `c28-local.py`, directement vers `c28-horslive.php`, sans le lanceur qui écrit un journal dans `production/C-28`. Échec avant démarrage : **`Wsl/Service/E_ACCESSDENIED`**, code 1. Aucun PHP/Docker disponible dans le PATH Windows. Les tests PHPUnit n'ont donc pas été exécutés indépendamment.
- **Preuves livrées vérifiées hors réseau :** PHPUnit 2 tests/18 assertions, natif 25 contrôles, complément C14 45 contrôles, recette 200 contrôles ; rejeu général annoncé de 1 189 tests/36 512 assertions. Ces résultats restent ceux du producteur. La limite A-32 est explicitement conservée.
- Les tests couvrent plusieurs cas limites utiles, mais pas C28-01 ni C28-02. Le témoin de panne existant intervient **avant** persistance du paiement ; il ne vérifie pas le second scénario. Les recettes `--live` et les scripts mutants n'ont pas été lancés, conformément aux droits du relecteur.

## 4. Sécurité et données

Pas de secret ni de donnée réelle repéré dans les fichiers examinés. Le champ administratif s'appuie sur le nonce Woo et vérifie `edit_post` ; les IDs sont validés strictement et les sorties publiques échappées. La fiche n'extrait aucun corps d'article réservé. Les reçus attestent sept surfaces et 32 témoins C26, avec contrôle positif du détecteur ; leur étanchéité n'a pas été rééprouvée sur site. C28-02 concerne néanmoins l'exactitude des droits accordés après incident.

## 5. Doctrine

Le choix produit simple + liste est proportionné et documenté par des liens officiels ; aucune extension commerciale ajoutée. Validation pure séparée du raccord Woo, décision de droit C14 réutilisée, textes français traduisibles, squelette B01 sans nouveau CSS/JS. Les pages documentaires externes n'ont pas été ouvertes, conformément à l'interdiction d'accès à un site.

### Décisions techniques, défaut proposé

Les deux corrections sont techniques : refuser un achat dont le pack est invalide ; garder fermé un achat payé dont l'instantané ne peut être établi avec certitude. Aucun arbitrage supplémentaire demandé à Ced ou Imagine.

## 6. Études (lots sans code)

Sans objet : lot avec code. La justification du standard est examinée au §5.

## Verdict

**À corriger.**

- **Bloquant :** aucun point classé ainsi.
- **Important :** C28-01, achat possible d'un pack invalide ; C28-02, reconstruction tardive donnant des droits différents de ceux du paiement.
- **Mineur :** aucun point retenu.

Ce verdict n'est pas un GO. Le rejeu PHPUnit indépendant reste non obtenu à cause du refus d'accès WSL.
