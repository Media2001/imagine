# A-27 — Corrections du passage de 1 h 30

**Périmètre : uniquement `wp/outils/bascule/a27/`, `wp/tests/a27/` et ce rapport. Aucun fichier commun modifié.**

- **Fait :** R2 et R3 corrigés dans le code ; tests PHP purs, témoins rouges ciblés et intégrations classique/HPOS préparés.
- **Vérifié ici :** 41 tests Python réussis en UTF-8 et 41 en console cp1252 réelle, Windows, `C:/Python314/python.exe` **3.14.6**. Vérificateur de la matrice **Python seule** : code 0, 13 contrôles PASS.
- **Non exécuté ici :** PHP, lint PHP, PSR-12 et intégrations natives. Docker/WSL sont réservés à l'agent A-28 ; PHP Windows est interdit. Aucun résultat PHP/natif vert n'est revendiqué.
- **R1 reste au parent :** attendre le gel final de l'import A-28, rejouer réellement les matrices, puis seulement refaire le paquet et son sceau. Aucun `PRET` créé, aucun sceau modifié.
- **Ancêtre préservé :** tous les fichiers préexistants de `production/A-27/`, notamment `preuves/final/`, `manifest.json`, `FINALISATION.md` et les reçus, sont inchangés. Ils ne qualifient pas le code corrigé.

## Lectures et décisions appliquées

Lecture intégrale de `corrections/A-27.md`, du brief A-27, de la doctrine, de la consigne permanente et de la file du 27 novembre à 1 h 30. La délégation parent, propriétaire du verrou, limite cette intervention au code A-27 et diffère explicitement R1. Aucun Git, site, compte, donnée réelle, import, gardien, A-19 ou voie 2 touché.

### R2 — Opaque n'est jamais absent

`Inventory.php` conserve l'appel au **véritable** `SubscriptionCoherence\Inventory::paymentReference()` d'A-19. Un observateur temporaire, non transformant, voit le schéma de la passerelle pendant **cette même évaluation** de `woocommerce_subscription_payment_meta`, sans rejouer le filtre. Un champ déclaré non scalaire, nul ou de structure non interprétable interdit de réutiliser `absent` : le résultat est `unknown`. Un champ scalaire réellement vide reste `absent`. L'observateur est retiré dans un `finally`, même si une extension lève une exception. A-19 n'est pas modifié.

`adapter-unit.php` utilise le fichier A-19 réel, une coque de hooks/abonnement fictive sans WordPress ni base, puis Analysis : cinq références opaques `ppcp-gateway`, aucun jeton → cinq `automatic/illisible` et cinq `subscriptions_link_unknown`. Il distingue aussi vide, scalaire, nul, évaluation unique et retrait de l'observateur sur exception. Ce n'est pas la preuve native : elle est préparée séparément.

Le banc natif dispose de `seed-corrections.php` : cinq abonnements vivants, automatiques, `ppcp-gateway`, aucun jeton ; la valeur opaque est enregistrée via le magasin Woo/WCS, puis exposée par le filtre natif. Le seed relit le magasin et constate le verdict A-19 `absent` avant l'adaptation A-27 ; il vérifie exactement cinq abonnements et zéro jeton. `inside.py` traverse ensuite le lanceur normal/Inventory/A-19 et exige les deux groupes exacts de cinq, zéro carte, absence du canari et immutabilité DB/fichiers. Même parcours préparé en classique et HPOS, pas d'injection directe dans Analysis pour cette preuve.

### R3 — Contradiction avant repli

`Analysis::reference()` refuse un lien explicite dont la référence ne résout pas vers un jeton lié **avant** le repli par passerelle : `type=illisible`, `link=unknown`, aucune expiration ni instrument choisi. Cela couvre lien B/référence A et référence sans correspondance avec lien explicite.

Tests PHP séparés sous SEPA et PayPal : contradiction, absence de correspondance, référence seule et correspondance unique. Le repli sans lien reste `mandat_sepa`/`accord_paypal`. Le banc natif prépare aussi trois jeux SEPA distincts de cinq abonnements : contradiction, référence seule et correspondance unique, dans chacun des deux magasins. Les sorties exactes et l'immutabilité de chaque jeu sont vérifiées par le banc et relues par le vérificateur du paquet.

### RED/GREEN — état exact

- **Exécuté :** deux contrats Python de source rouges avant R2/R3, puis verts ; contrat du vérificateur rouge avant son extension, puis vert. Logs intermédiaires uniquement en scratch.
- **Préparé, non exécuté :** `corrections-red.py`, appelé par `run.py`, retire séparément chaque correction dans la seule copie conteneur jetable. R2 doit rendre rouges `opaque_adapted_presence`, `opaque_five_automatic_illisible` et `opaque_five_relation_unknown` ; R3 doit rendre rouge `explicit_contradiction_stripe_sepa`. Restauration des octets en `finally`, puis suites PHP vertes attendues. Les mutations ne ciblent jamais le dépôt.
- Le vérificateur exige ces deux reçus rouges, la suite d'adaptateur verte, les assertions R3 distinctes et les quatre nouveaux jeux natifs. Un ancien paquet ne peut pas satisfaire ces nouvelles exigences.

### Mineurs, métier et écart

- **M-1 conservé :** `cards` conserve `later` et `illisible`, sans fusionner les deux comptes demandés. Aucun élargissement supplémentaire.
- **M-2 conservé :** `eCheck` n'est SEPA que pour `stripe_sepa`. Note du README conservée ; aucun identifiant réel de passerelle supposé.
- **Six mois inchangé :** borne au jour/heure de l'audit, six mois calendaires, dernier jour borné ; ni réglage ni modification du décompte dans cette intervention. Les tests existants restent présents.
- **Écart à reporter par Claude dans `docs/ecarts.md` :** après neutralisation, aucun compte de moyens de paiement utile ; tous les nombres sont `inconnu après neutralisation`, jamais zéro reconstruit. `docs/` n'est pas modifié. Aucun comptage réel ni choix de source sans GO écrit de Ced.

## Commandes exécutées et résultats

Depuis `C:/Users/Ced/imagine`, sans PHP ni Docker :

```sh
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 C:/Python314/python.exe -B wp/tests/a27/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a27-corrections-1h30/python-final
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 C:/Python314/python.exe -B wp/tests/a27/verify.py --python-only --evidence=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a27-corrections-1h30/python-final
```

Résultats : `python_only`, `readiness_claimed=false`, `sources_stable=true`, code 0 ; 41 tests par console. En UTF-8 : stdout/stderr UTF-8, mode UTF-8=1, locale cp1252. En cp1252 : stdout/stderr/locale/encodage préféré cp1252, mode UTF-8=0. Les sous-processus des tests imposent leur encodage explicitement. Les journaux et environnements exacts restent dans le scratch nommé ci-dessus, pas dans un nouveau paquet de production.

Contrôles complémentaires exécutés : parsing AST des fichiers Python A-27 ; comparaison SHA-256 de l'ancêtre et d'A-19 ; absence de `PRET`. Les deux vérificateurs historiques restent volontairement rouges sur l'arbre corrigé : `production/A-27/verify.py` → code 1 `SEALED_VERIFICATION_FAILED` ; `wp/tests/a27/verify.py` sans argument → code 1 `A27_PACKET_INVALID` (les nouveaux reçus n'existent pas dans l'ancêtre). Aucun de leurs fichiers n'a été réécrit pour masquer cet état.

## Commandes préparées — parent seulement, après A-28

**Non exécutées par ce worker.** Répertoires de sortie neufs, hors dépôt ; aucune simple actualisation d'empreintes d'anciens reçus.

```sh
C:/Python314/python.exe -B wp/tests/a27/run.py --parent-serialized --unit-only --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a27-corrections-parent-pure-neuf
C:/Python314/python.exe -B wp/tests/a27/matrix.py --include-native --parent-serialized --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a27-corrections-parent-matrice-neuve
C:/Python314/python.exe -B wp/tests/a27/verify.py --evidence=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a27-corrections-parent-matrice-neuve
```

Le runner natif inclut lint des sources PHP, RED/GREEN ciblé R2/R3, PHP pur, classique/HPOS, contrôle du code installé, canaris, refus, immutabilité et neutralisation réelle par l'import courant ; la matrice inclut le contrôle PSR-12. Préparation d'image et portes communes, qualification du gel final, régénération du paquet unique, vérificateurs courants et éventuel `PRET` restent au parent. Ni ce rapport ni la matrice Python seule ne clôturent R1.

## Fichiers livrés

- Outil : `Analysis.php`, `Inventory.php`, `README.md` dans `wp/outils/bascule/a27/`.
- Tests créés : `adapter-unit.php`, `corrections-red.py`, `seed-corrections.php`, `test_corrections.py` dans `wp/tests/a27/`.
- Tests ajustés : `inside.py`, `run.py`, `unit.php`, `verify.py` dans ce même dossier.
- Production : uniquement ce nouveau `corrections-1h30.md`. Sources, hashes de comparaison, logs RED et matrice Python conservés en scratch Hermes.
