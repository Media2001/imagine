# C-05 — notes et réception

**Fait :** proposition comparant deux voies officielles, moteur PHP pur, preuve sur vrai Subscriptions classique/HPOS, nettoyage vérifié.
**Prêt à relire :** code et preuves partielles ; **aucun PRET** car l’acceptance universelle échoue sur une contradiction métier reproductible.
**À arbitrer :** `proposition.md`, §6 : invariant à amender, marge, rejet/engagement, variation tarifaire.
**Bloqué :** commande dans la fenêtre entre date commune et clôture : première charge de reconduction commune avant anniversaire, donc cinq dates dans la première année ; le moteur refuse.
**Ensuite :** arbitrage explicite et nouveau test de la règle retenue ; aucun autre lot commencé.

## Textes lus et interprétation

Lecture intégrale de la consigne permanente, doctrine révisée le 21 novembre, A-FAIRE et brief C05 ; décisions et arbitrages du 21 novembre, étude A00 (notamment besoin 2), moteur/notes C01 et portions utiles du cahier §§3.4–3.6. C01 est clos selon la file et reste inchangé. Les cas de `docs/recette/` ne sont ni modifiés ni automatisés : les tests ici sont ceux du brief C05.

J’ai compris « année de date à date » comme une fenêtre `[début, anniversaire)` pour le comptage des paiements, et « quatre suivants » comme les numéros fournis par C01, non une sélection de dates civiles indépendante. Dans les jeux immédiats, la borne provient de C01 ; dans l’API pure elle est obligatoire et explicitement fournie par le domaine contractuel. L’activation numérique et la date de commande ne sont pas fusionnées implicitement. La marge n’a pas de défaut.

Le parent détient le verrou : il n’est ni repris ni réécrit. L’exception de délégation est l’instruction explicite du parent, non une nouvelle session autonome. Écritures du dépôt limitées aux quatre surfaces C05. Aucun rapport écrit dans `files/rapports/` ; cette note en tient lieu pour remontée au parent.

## Acceptance, sans équivoque

| Critère du brief | Résultat |
|---|---|
| Quatre positions, initial compris, numéros et dates C01 | PASS : 365 jours de commandes ; initial remplace seulement la première commune |
| Veille, jour et lendemain d’une clôture | PASS pour la détection : veille impossible à reconduire dans la fenêtre ; jour et lendemain changent de numéro conformément à C01 |
| Exactement quatre dans chaque année de date à date, **quel que soit le jour** | **BLOQUÉ : 28 commandes quotidiennes à midi sur 365 incompatibles dans le calendrier fictif avec marge 7** |
| Deux voies sourcées, recommandation | PASS documentaire, voie A conditionnelle ; 6 sources officielles vérifiées HTTP 200 |
| Trois dates de commande, année puis reconduction, vrai Subscriptions | PASS de prototype sur 3 dates compatibles, classique et HPOS ; pas une preuve pour les dates incompatibles |
| Toutes les dates reconduites communes et numéros suivants | PASS pour les 3 scénarios compatibles ; refus explicite des autres, pas de dérogation financière |
| Rejet, marge, tarifs sans choix arbitraire | Questions fermées seulement ; aucun automatisme financier ou de droits |
| Aucun réel / isolement / ressources propres supprimées | PASS : manifests d’isolation et `cleanup.json`, revérification par identifiants exacts |
| PRET seulement si acceptance complète | **Aucun PRET** |

## Résultats canoniques

- `preuves/final-unit-3-result.json` : **376 tests / 1 473 assertions / 0 échec**. Suite autonome PHP, pas PHPUnit.
- `preuves/final-unit-3.json` et `final-e2e-3.json` : sources réellement copiées et vérifiées, syntaxe PHP, commandes, isolation avant/après.
- `preuves/final-e2e-3-result.json` : **2 stockages × 3 scénarios**, **230 contrôles de scénario par stockage**, **42 commandes réelles de renouvellement + 6 initiales = 48 commandes**. Les contrôles d’enveloppe Python/isolation sont distincts et ne sont pas présentés comme des scénarios.
- `preuves/cleanup.json` : suppression du dernier conteneur possédé et diagnostic d’absence ; `verification.json` recontrôle l’absence de toutes les ressources C05 identifiées dans les reçus.
- `sources/ledger.json`, `sources/retrieval.json`, `sources/extrait-*.txt` : URLs finales, dates de consultation, empreintes des pages et extraits brefs littéraux. Le contrôle des citations est effectué après rédaction.
- `preuves/verification.json` : contrôle d’artefacts actuel, agrégation mécanique, C01 identique au premier RED, aucun PRET.

Les premières preuves RED/GREEN sont conservées (`red-initial`, `green-initial`, `red-date-a-date`, `green-date-a-date`, `red-validations`, `green-validations`, `red-raccord`). Les essais `raccord-first` et `raccord-customer-fix` ont exposé les préconditions réelles de création et l’horodatage des confirmations, puis ont été corrigés dans la fixture, sans contourner de garde d’activation. `final-e2e` a révélé que `is_manual()` peut être vrai sans drapeau manuel explicite lorsqu’aucune passerelle n’est disponible ; le raccord exige désormais le vrai drapeau et un identifiant de passerelle vide, vérifiés au vert dans les reçus finaux.

## Limites et incidents de collecte

- La preuve est un site **entièrement inventé**, pas le site Imagine neutralisé et pas un staging vérifié/public. Les versions exercées sont celles de l’image synthétique compatible déjà préparée, pas une affirmation sur la production.
- Les actions natives ont les bonnes dates futures mais sont traitées explicitement en accéléré ; les confirmations locales surviennent maintenant. Ni débits réels, ni passerelle sandbox, ni rejet bancaire, retry automatique, emails effectifs, compte abonné rendu, Odoo, taxes/port ou opposition à reconduction ne sont exercés.
- Aucun contrôle PHPCS/Composer nouveau : dépendances de test supplémentaires non installées. Syntaxe PHP et suite réelle exécutées dans Docker. Pas de prétention à une suite complète de non-régression du plugin ; l’inventaire et les 7 empreintes C01 sont comparés, et ses fonctions sont exercées directement par les tests C05.
- Le backend `web_extract` a répondu qu’il était search-only et ne pouvait pas extraire les pages. La lecture publique officielle a donc été faite par HTTP direct, avec une ouverture navigateur complémentaire. **Aucun appel `web.run` n’est revendiqué** dans ce sous-agent ; ce transport demandé n’était pas exposé parmi ses outils utilisables. Le parent peut revérifier les six URLs au moyen de `web.run`. Aucun changement de configuration/outillage pour contourner cette limite.
- Aucun défaut de Subscriptions supposé : le refus universel vient des règles de dates, démontré en PHP sans WordPress. Ne pas proposer d’achat d’extension pour résoudre une contradiction de calendrier.

## Revérifier

Depuis `C:/Users/Ced/imagine` :

```bash
python wp/tests/echeancier-runner/verify.py
```

Rejeu réel complet : commandes avec fermeture même sur erreur dans `wp/tests/echeancier-runner/README.md`. Le banc ne touche ni aux ressources des agents A01/C06 ni à la configuration de l’outil de staging. Après arbitrage, ajouter d’abord le test de la règle décidée ; ne pas transformer un refus en report automatique sans ce texte.
