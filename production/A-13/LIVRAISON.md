# A-13 — Paquet de contrôle CSV hors ligne, corrigé le 26 novembre 2026

**B1** : sonde IBAN NFKC par cellule, ponctuation/espaces/format invisible retirés de la seule sonde, jamais de la source ; aucun assemblage des colonnes. Points, points médians, caractère sans chasse, espace fin insécable et caractères pleine chasse sont éprouvés en colonne non mappée, dernière ligne.

**I1** : nom + adresse suffit par défaut même si les prénoms diffèrent. Option explicite `doublon_prenom_identique=false` (aussi par défaut quand absente) ; `true` ajoute volontairement le prénom. **I3** : consoles cp1252 et ASCII éprouvées sans exception après les sorties UTF-8 ; remplacement explicite des caractères non encodables. L'échec initial reproduit sur ce code était ASCII, pas cp1252 sur le cas nominal.

## Résultat vérifié localement

Outil Python pur livré dans `wp/outils/bascule/controler-export`, sans WordPress,
sans import, sans compte et sans réseau. Correspondance dédiée :
`wp/outils/bascule/a13/correspondance.exemple.json`.
Mode d'emploi : `wp/outils/bascule/controler-export.md`.

Preuves : `verification.json` (chiffres et empreintes des sorties fictives),
`verification.tests.txt` (transcription intégrale du dernier passage de la suite).
`manifeste.json` lie les fichiers livrés à leurs octets SHA-256 ; il ne se contient
pas lui-même et ne couvre pas un futur marqueur de validation.

- Suite A-13 : 40 tests exécutés, 0 échec, 0 erreur, 0 ignoré, Python 3.11.15 Windows.
- Trois fixtures de 30 lignes, exclusivement fictives ; copies de travail en scratch.
- Propre : code 0, 30 lignes sans défaut, 0 rejet.
- Défauts : code 1, 5 lignes sans défaut, 25 lignes rejetées / 25 motifs,
  6 lignes en doublon, 1 ligne sans email (non rejetée pour son absence d'email).
- IBAN fictif : code 2, colonne 14, aucune sortie créée, aucune valeur recopiée.
- Les 25 diagnostics attendus sont vérifiés sur leur ligne physique exacte.
- Préflight intégral avant analyse métier : tests de dernière ligne, colonne non
  mappée, en-tête suspect même vide, contenu seul, CSV cassé et champ entre guillemets.
- Encodage/séparateur ambigus, sortie dans un dépôt synthétique de scratch,
  sortie existante et correspondance invalide : refus explicites testés.

## Rejouer

```text
python -m unittest discover -s wp/tests/a13 -v
python wp/tests/a13/verifier_livraison.py --preuve production/A-13/verification.json
```

Le vérificateur lance toute la suite puis trois commandes CLI séparées, vérifie
les codes, les quantités, l'absence de recopie et l'intégrité des sources. Les
sorties de contrôle sont nettoyées avec leur répertoire temporaire, pas stockées
dans le dépôt. Le JSON ne conserve que les résumés sans données et les empreintes.
Après un rejeu qui change les preuves, régénérer le manifeste de livraison.

## Décisions prises à défaut

CDC §2.3, §3.13, §4.3 et brief A-13 : aucun import ni décision d'éligibilité.
L'échéance passée est signalée, pas une décision de migration. Les obligations,
les codes de paiement et les modes demandant un mandat sont déclarés. Aucun
mappage de produit ni interprétation du statut de coopérateur. Le filtre facultatif
de types est désactivé par défaut et testé activé/désactivé. La casse, les accents
et les espaces sont neutralisés pour les comparaisons, jamais pour réécrire la source.
Le défaut nom/adresse n'exige pas le prénom. La syntaxe email est
contrôlée sans réseau, pas la délivrabilité. Les outils WordPress ne sont pas
appelés : le besoin est précisément un contrôle préalable autonome, pas un importeur.

## Intégration reçue

Le writer délégué a exécuté `wp/tests/preparer-image.ps1`, code **0**, après ajout des tests. Journal courant : `preparer-image-corrections-26nov.log`. `reception.json` porte cette intégration acquise ; la mention générique d'attente parent du vérificateur autonome n'est pas réécrite dans ses preuves.

Un seul jeu courant : `verification.json` et `verification.tests.txt`, suite de **40 tests** puis trois CLI fictives, codes **0, 1 et 2**. Les fichiers d'entrée source/test/fixture A-13 sont empreintés avant/après le rejeu. Les anciennes preuves ont été conservées intactes hors dépôt dans le scratch Hermes. Le manifeste est borné au lot, sans empreinte d'orchestration, de document partagé ou de lot frère.

Contrôle courant : `python production/A-13/verifier_manifeste.py`. Rejeu réel : `python wp/tests/a13/verifier_livraison.py --preuve <scratch>/verification.json`, puis rescellage. L'ancien contrôle consolidé A-10/A-13 est historique ; le PRET courant ne le désigne plus. Aucun test PHP global, accès à un export réel, import ou GO de migration n'est revendiqué.
