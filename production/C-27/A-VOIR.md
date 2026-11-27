# C-27 — à voir et à vérifier

**Site unique : `imagine-test-demo`, entièrement fictif.** Aucun paiement ou email réel. Squelette sans style ajouté ; validation visuelle de Ced encore attendue.

**Réception corrective du 27 novembre :** les cinq instructions sont couvertes par `correction-final-V2.json`, lié au reçu initial `final-V2.json` désormais historique. Pas de clôture ni GO réel. Les paquets annexes A-31 (`A31_PARTIAL_EVIDENCE`) et A-32 (`A32_PACKAGE_DRIFT`) restent rouges dans le rejeu général ; ils ne sont ni ouverts ni réparés ici.

**Lanceurs non rejoués en première relecture :** recettes mutantes Python non rejouées par Claude **et** Codex ; PHPUnit non rejoué par Codex (`Wsl/Service/E_ACCESSDENIED`). La livraison corrective les a exécutés réellement ; aucun nouveau rejeu des relecteurs n’est revendiqué.

## Adresses

Avec le personnage administrateur fictif déjà fourni par B00/C09 (aucun identifiant dans ce paquet) :

- Réglage C10 : <http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-reglages>. Section **Comment nous avez-vous connus ?**, dans le formulaire existant **sous « Enregistrer »** ; deux réponses fictives, dont un antislash. Aucune autre section déplacée. Une ligne `identifiant|libellé`, liste vide = aucune question ; les changements apparaissent dans le journal C10. L’emplacement reste la question visuelle déjà posée à Ced.
- Nombres : <http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-acquisition&du=2026-11-01&au=2026-11-30>. Tableau **Acquisition déclarée**, libellés et nombres seulement, bornes UTC inclusives. Après restauration : aucune déclaration conservée, donc pas de faux chiffre de démonstration. Modifier la période ne modifie rien.
- Tunnel : <http://192.168.129.32:8085/checkout/>. Aucun champ C27 avant paiement.
- Compte : <http://192.168.129.32:8085/my-account/>. Aucun rappel en boucle de la question.
- Commande opérateur C16 : <http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-commandes>. Aucun champ de source, l’opérateur ne répond pas pour le client.
- Outils natifs : <http://192.168.129.32:8085/wp-admin/export-personal-data.php> et <http://192.168.129.32:8085/wp-admin/erase-personal-data.php>. Le callback **Source d’acquisition déclarée** est enregistré ; ne pas envoyer de demande email. Les callbacks ont été exécutés réellement dans la recette fictive puis les profils restaurés.

### Confirmation payée : limite de prévisualisation, explicite

WooCommerce laisse cette boutique en mode **« À venir »** pour les lecteurs ordinaires. C27 n’ouvre pas la boutique et ne change pas ce réglage. La recette accède au vrai rendu Woo à blocs avec le **filtre natif de prévisualisation**, seulement dans son observateur temporaire pour ses requêtes marquées ; tout est retiré ensuite.

Sur une confirmation payée autorisée, le titulaire voit « Comment nous avez-vous connus ? », un select facultatif, « Je préfère ne pas répondre » et « Continuer sans répondre ». Rafraîchir ne repropose pas la question. Impayé, invité, tiers, clé incorrecte, liste vide ou commande C16 : rien. Une réponse enregistrée est datée et ne peut plus être changée. La recette fabrique sept commandes fictives et les supprime ; **aucune adresse morte de commande jetable n’est présentée comme visite permanente**. Pour une visite manuelle client, employer l’accès natif de prévisualisation de la boutique Woo ; ne pas ouvrir la boutique réelle ni modifier les profils.

## Vérificateur parent — sans argument, hors réseau, sans site

Depuis `C:\Users\Ced\imagine` :

```text
python -B production/C-27/verifier.py
```

Interpréteur effectivement utilisé ici (Python **3.11.15**) si `python` ne désigne pas Python 3.11 dans la session du relecteur :

```text
C:/Users/Ced/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -B production/C-27/verifier.py
```

Le contrôle lit `correction-final-V2.json`, vérifie sources et preuves, les ensembles **exacts** de contrôles/restaurations, cinq témoins mutants réels et onze mutants de source, les trois rouges TDD et les cinq nouvelles régressions découvertes dans le JUnit global. Il exige les véritables contre-exemples I1/I2/M1, pas seulement un drapeau de réussite. Aucun accès au site, à Docker ou au réseau. L’ancien paquet et `verifier-historique-avant-fusion.py` ne sont pas une réception des sources actuelles.

Contre-exemples du vérificateur (copies jetables dans le scratch Hermes) :

```text
python -B wp/tests/demo/c27-verifier-tests.py
```

## Rejouer les preuves exécutables

Les étiquettes de preuve sont immuables : remplacer `NOM-NEUF` par une étiquette jamais utilisée.

```text
python -B wp/outils/demo/c27.py local parent-unitaires-NOM-NEUF
python -B wp/outils/demo/c27-mutations.py parent-mutants-NOM-NEUF
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

**Mutations sur le seul site fictif gardé**, jamais un site réel :

```text
python -B wp/outils/demo/c27-native.py parent-natif-NOM-NEUF
python -B wp/outils/demo/c27-recette.py parent-HTTP-NOM-NEUF
python -B wp/outils/demo/c27-corrections.py parent-fusion-NOM-NEUF
```

Préimages privées durables avant mutation ; restauration exacte des profils, commandes, adresses, brouillon C16, options métier, actions et journaux, puis relecture. Le dernier lanceur fabrique huit commandes fictives puis les supprime. I1/I2 injectent une seule vraie erreur SQL SOURCE sous verrou ; le mutant I1 écrase réellement la source antérieure, le mutant I2 annonce réellement terminé avec SOURCE encore en base. Le vieux POST d’une proposition effacée sans réponse reçoit 403 ; sans sa garde, il recrée effectivement réponse/source (200). Cache empoisonné/suppression refusée et panne de relecture finale refusent `done`. Aucun paiement, email ou tiers nécessaire. Ce n’est pas un nouveau test d’entrelacement simultané effacement/réponse : la symétrie du verrou et le cache périmé sont vérifiés ; les deux POST concurrents nominaux restent exercés.

## Résultats et limites

**12 tests/80 assertions** ciblés ; **56 contrôles natifs/HTTP** ; **11 mutants de source**, **5 témoins mutants réels** détectés ; image reconstruite (`correction-image.*`). Dernier rejeu : **1 195 tests / 36 573 assertions**, 0 échec/erreur/ignoré ; **720 contrôles d’outils**, 0 échec. **12 paquets annexes, 2 échecs** A-31/A-32 signalés en tête, pas masqués. Les paquets voie 1 n’ont pas été ouverts, modifiés ou rescellés par ce lot. PSR-12 : zéro erreur, 32 avertissements de longueur conservés, pas de reformatage global.

Détails, inventaire des données personnelles et incidents intermédiaires conservés : `NOTE.md`. Le code est prêt techniquement sur le périmètre prouvé ; le visuel et l’emplacement C10 restent à valider, sans GO sur du réel.
