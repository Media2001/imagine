# A-13 — Paquet de contrôle CSV hors ligne

## Résultat vérifié localement

Outil Python pur livré dans `wp/outils/bascule/controler-export`, sans WordPress,
sans import, sans compte et sans réseau. Correspondance dédiée :
`wp/outils/bascule/a13/correspondance.exemple.json`.
Mode d'emploi : `wp/outils/bascule/controler-export.md`.

Preuves : `verification.json` (chiffres et empreintes des sorties fictives),
`verification.tests.txt` (transcription intégrale du dernier passage de la suite).
`manifeste.json` lie les fichiers livrés à leurs octets SHA-256 ; il ne se contient
pas lui-même et ne couvre pas un futur marqueur de validation.

- Suite A-13 : 35 tests exécutés, 0 échec, 0 erreur, 0 ignoré, Python 3.11.15 Windows.
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
Le nom complet comprend le prénom s'il est configuré. La syntaxe email est
contrôlée sans réseau, pas la délivrabilité. Les outils WordPress ne sont pas
appelés : le besoin est précisément un contrôle préalable autonome, pas un importeur.

## Intégration reçue

Le parent a exécuté `wp/tests/preparer-image.ps1`, code **0**, le **26 novembre
2026 à 00:45:29 CET** ; reçu et journal `production/A-11/preparer-image-parent.json`
et `.log`, image T01 vérifiée. Cette exigence est acquise avant le marqueur PRET.
La réception a rejoué les **35 tests**, sans échec/erreur/ignoré, puis les trois
commandes CLI fictives (codes **0, 1 et 2**) : preuves fraîches
`reception-verification.json` et `reception-verification.tests.txt`.

Les anciennes preuves `verification.json` et `.tests.txt` restent historiques,
sans réécriture de leur mention d'attente parent. `reception.json` porte l'état
courant ; `manifeste.json` scelle l'ensemble. Vérification consolidée en lecture
seule : `python -B production/A-10/verifier-reception.py`. Aucun test PHP global,
accès à un export réel, import ou GO de migration n'est revendiqué.
