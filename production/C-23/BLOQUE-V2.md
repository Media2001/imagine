# C-23 — Blocage V2 après corrections, 26 novembre 2026

**Statut : NON PRÊT. L’ancien PRET est archivé, pas conservé comme promesse verte.**

## Fait et vérifié

- Corrections 1, 2, 4, 5, 6 : détecteur brut + normalisé ; attributs/commentaires ; inspection des redirections avant suivi ; régression non vacante ; vérificateur JSON stdout sans écriture ; SHA d’état dérivé des snapshots natifs.
- Correction 3 : retrait de tout forçage de politique dans la préparation normale ; refus explicite avant session ou autre écriture si le prérequis est incompatible.
- B06 : cinq pages, sept sorties chacune ; témoins temporaires hors commande GET, vrais inverses coopérateur. **503 contrôles, zéro fuite, code 0** dans `b06-livraison-finale-V2.*` ; cette matrice ne vaut que B06.
- **35/35 mutations** des réponses HTTP natives détectées, puis octets restaurés (`b06-reponses-mutations-post-redirection-V2.json`). Le témoin éditorial C23 réellement ouvert provoque **177 fuites sur 1 922 contrôles**, code détecteur 1, puis restauration (`mutation-finale-V2.*`).
- **28 tests × 2 contextes d’encodage**, UTF-8 et cp1252 réel, Python 3.11.15, deux codes 0. Image de tests préparée, code 0.
- Readback indépendant : même état natif avant/après les trois derniers rejeux ; cinq corps B06 remis vides ; attribut administratif P-COOP conservé ; métadonnées, sessions, options et actions planifiées restaurées exactement.

## Blocage restant : préparation durable du personnage découverte

Le réglage effectivement livré est :

```json
{"ouverture":"fermee","forme":"articles","jours":7,"nombre":2,"numeros":[]}
```

Aucune modification du seul personnage `V-DEC-FIN` ne peut faire fonctionner une découverte globalement fermée et sans numéro. Forcer l’ouverture pour obtenir le vert reproduirait précisément le défaut de l’instruction 3. Choisir un autre réglage métier ne relève pas de C23. **Aucun réglage métier n’a donc été changé durablement et aucun personnage compatible n’a été prétendu préparé.**

Commande finale réellement exécutée :

```bash
PYTHONIOENCODING=utf-8 python -B wp/outils/demo/c23-preparer.py --label livraison-finale-V2
```

Code **1**, avant toute session et avant plantation du témoin B06 :

```text
ETANCHEITE : 0 contrôles, 0 fuites — FAIL ; Prérequis découverte incompatible : politique livrée fermée ou sans numéro ; aucun réglage forcé
```

Le vérificateur de paquet retourne aussi **1** : 36/39 contrôles vrais, trois rouges attendus (`delivery_prerequisites`, `delivery_exit`, `delivery_nonempty`). Il ne promeut pas la matrice B06 ni la mutation en livraison complète.

## Décision prise à défaut

Conserver les réglages livrés et rendre ce refus opposable. Quand le lot propriétaire fournit une politique compatible, préparer durablement le seul personnage fictif selon cette politique et rejouer le test normal sous un nom de reçu neuf. Cette étape et le vert complet restent à faire avant redépôt de PRET.

Le changement temporaire de politique n’est utilisé que dans la recette séparée `--mutation`, explicitement autorisée par la correction ; il a été exactement restauré et n’est pas présenté comme l’état livré.

## Périmètre et preuves

Modifications uniquement dans `wp/outils/demo/c23*`, `wp/tests/demo/c23*` et `production/C-23/`. Aucun code fermé de paywall/plugin/thème, B05/C22/B06, verrou, file, site différent ou rapport parent modifié. Aucun Git, installation hôte, appel extérieur, paiement ou email réel. Les anciens reçus et les deux diagnostics rouges B06 sont conservés sans réécriture. Commandes complètes, limites et matrice : `A-VOIR.md`, `b06-livraison-finale-V2.md`, `INCIDENTS.md`.
