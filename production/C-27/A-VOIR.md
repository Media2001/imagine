# C-27 — à voir et à vérifier

**Site unique : `imagine-test-demo`, entièrement fictif.** Aucun paiement ou email réel. Squelette sans style ajouté ; validation visuelle de Ced encore attendue.

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

Le contrôle lit le paquet scellé `final-V2.json`, vérifie ses sources et preuves, les ensembles **exacts** des contrôles/restaurations, les deux mutants natifs et les huit mutants de source, et recalcule les totaux de JUnit. Il ne fait aucun accès au site, à Docker ou au réseau.

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
```

Préimages privées durables avant mutation ; restauration exacte des profils, commandes, adresses, brouillon C16, options métier, actions et journaux, puis relecture. Le contrôle de refus avant paiement est testé d’abord rouge/vert, puis le retrait de la garde est réellement injecté sur une commande fictive : le POST impayé devient accepté, la garde remise le refuse. Aucun paiement, email ou tiers n’est nécessaire.

## Résultats et limites

7 tests/55 assertions ciblés ; 47 contrôles natifs/HTTP ; huit mutants de source et deux témoins natifs détectés ; image reconstruite. Dernier replay : **1 166 tests / 36 318 assertions**, **584 contrôles d’outils** et **11 paquets annexes** verts. Les paquets voie 1 n’ont pas été ouverts ou modifiés par ce lot ; l’état vert courant vient du lanceur partagé, pas d’un rescèlement par C27.

Détails, inventaire des données personnelles et incidents intermédiaires conservés : `NOTE.md`. Le code est prêt techniquement sur le périmètre prouvé ; le visuel et l’emplacement C10 restent à valider, sans GO sur du réel.
