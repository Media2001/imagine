# Relecture indépendante Codex — C-07

Date : 22 novembre 2026. Périmètre : brief C-07, exigences héritées de C-01, production C-07, sources et tests Envoi, dépendances Numeros et protection CSV du connecteur. Références : doctrine, grille, cahier des charges §3.4, §3.5, §3.8 et §3.13, profils de recette, décisions et arbitrages du 21 novembre.

Relecture statique et contrôle des preuves livrées. Le rejeu PHP indépendant a été tenté, mais bloqué par WSL ; détail en section 3. Les contre-exemples ci-dessous sont déroulés à la lecture du code, sans prétendre à une reproduction exécutée. Le rapport de l'autre relecteur n'a pas été consulté. Seul ce fichier est écrit.

## 1. Conformité

Le périmètre demandé est respecté : moteur PHP pur, entrées explicites, aucun recalcul des numéros dus, destinataires des cadeaux et groupes, exclusion des achats unitaires, projection historique, anomalies séparées et CSV utilisant la protection commune de C-04. L'absence d'email ne conditionne pas l'envoi. Le branchement WooCommerce, l'écran administratif et l'archivage persistant sont explicitement différés.

Les références métier figurent dans les notes ; les trois questions fermées imposées par le brief sont présentes : grâce, doubles abonnements, format du routeur. La borne strictement antérieure à la clôture est cohérente avec l'interprétation C-01. Le contrat des photographies complètes et les limites de l'historique de confiance sont documentés.

La règle 8 du brief n'est toutefois pas entièrement satisfaite : les trois cas C07-CX-01 à C07-CX-03 peuvent produire une liste sans anomalie alors qu'une intervention administrative est nécessaire. Les restrictions documentées sur la casse ASCII ne suffisent pas à satisfaire la détection du même destinataire à la même adresse.

## 2. Exactitude métier

### Cas du cahier des charges déroulés à la main

Calendrier fictif existant : sorties régulières le 5 du trimestre, clôtures le 20 du mois précédent ; hors-série le 15 juillet, clôture le 25 juin. Pour les cas suivants, les situations sont actives, payées, connues avant clôture, avec une adresse complète et sans fin atteinte.

| Cas | Attendu métier | Résultat déduit du code |
|---|---|---|
| §3.5 : commande du 8 octobre 2026 | Papier 171, 172, 173, 174 et HS-2027 ; pas 170 ni 175 au titre de cette année | C-01 fournit ces cinq identifiants. Le filtrage strict de C-07 conserve une ligne pour chacun, aucune pour les autres. Conforme, y compris le passage de 2026 à 2027. |
| §3.5 : renouvellement en octobre 2027 | Papier 175, 176, 177, 178 et HS-2028 | C-01 rattache le renouvellement après 174. Avec ces droits injectés dans la situation du renouvellement, C-07 conserve exactement ces cinq numéros. Conforme ; aucune attribution du hors-série précédent. |
| §3.4 : groupe de cinq places, trois attribuées | Trois exemplaires aux bénéficiaires ; aucun aux deux places libres | Trois destinataires injectés donnent trois lignes. Un remplacement effectif et enregistré avant clôture est retenu ; un remplacement après clôture est ignoré. Conforme au contrat d'entrée. |

Bornes examinées : paiement à 23 h 59 min 59 s avant la clôture du 20 décembre retenu ; paiement à minuit ou une seconde après exclu. Une correction enregistrée après clôture est ignorée même si son effet est antérieur. Une fin effective égale à la clôture exclut l'abonnement. Un numéro absent du calendrier est refusé ; un calendrier partiel contenant le numéro demandé n'entraîne aucune invention de droits. L'ordre des entrées n'affecte pas le tri des lignes et anomalies. Le rejeu reste conditionné à la conservation des photographies historiques, limite annoncée et acceptable pour ce lot pur.

### C07-CX-01 — Important — Disparition silencieuse d'un abonnement individuel sans destinataire

**Localisation :** `wp/plugins/imagine-pilotage/src/Envoi/ListeEnvoi.php:64`.

**Problème :** un abonnement individuel ou offert actif, payé et ayant droit à 171 peut contenir une situation avec `destinataires = []`. Les constructeurs l'acceptent : seul le cas de plusieurs destinataires individuels est refusé. La boucle ne produit alors aucune ligne ; la recherche d'anomalies, qui parcourt uniquement les lignes produites, ne signale rien. Avec ce seul abonnement, le résultat est `lignes = []`, `anomalies = []`, et l'export accepte un simple en-tête. Un abonné ayant droit disparaît donc sans alerte. L'exception prévue pour les places non attribuées concerne les groupes.

**Correction proposée :** détecter l'absence du destinataire d'un abonnement individuel/offert éligible avant la génération des lignes et la remonter dans les anomalies avec l'identifiant de l'abonnement, afin de bloquer l'export non revu. Conserver l'absence de ligne et d'anomalie pour un groupe sans place attribuée. Ajouter les trois cas en tests.

### C07-CX-02 — Important — Doubles exemplaires non signalés avec une casse accentuée différente

**Localisation :** `wp/plugins/imagine-pilotage/src/Envoi/ListeEnvoi.php:95`.

**Problème :** la clé de doublon utilise le nom transformé par `strtolower`, qui ne normalise pas la casse UTF-8 des lettres accentuées. Deux abonnements pour le même `destinataire_id`, à l'adresse strictement identique, portant les noms fictifs `ÉLODIE FICTIVE` et `élodie fictive`, donnent deux clés différentes. L'identifiant du destinataire n'intervient pas dans le rapprochement. Les deux exemplaires sont conservés sans anomalie et peuvent être exportés sans revue. Il s'agit du même destinataire connu, pas d'un rapprochement postal flou.

**Correction proposée :** rendre la comparaison des noms compatible avec la casse Unicode et exploiter l'identité stable du destinataire lorsqu'elle est commune aux abonnements. Conserver les deux exemplaires, mais signaler chacun en doublon. Ajouter ce contre-exemple avec identité et adresse identiques ; vérifier que deux destinataires distincts ne sont pas fusionnés automatiquement.

### C07-CX-03 — Important — Champs postaux visuellement vides acceptés

**Localisation :** `wp/plugins/imagine-pilotage/src/Envoi/ListeEnvoi.php:85`.

**Problème :** les vérifications de présence utilisent `trim`, qui ne retire pas les espaces insécables UTF-8. Un destinataire dont la rue est uniquement U+00A0 et dont les autres champs sont complets ne reçoit pas l'anomalie `adresse_incomplete`. Le même défaut concerne un pays composé uniquement d'espaces insécables, testé à la ligne 90. Le contrôle des doublons ne corrige pas cette absence de contenu. Un exemplaire sans adresse exploitable passe donc l'export par défaut, contrairement à la règle 8.

**Correction proposée :** appliquer une vérification commune du contenu postal après suppression des espaces Unicode aux extrémités, puis considérer les champs ainsi vides comme manquants. Tester séparément rue, nom, code postal, ville et pays avec espaces ordinaires, U+00A0 et U+202F, ainsi qu'une vraie valeur entourée d'espaces.

## 3. Tests

**Rejeu indépendant non réalisé jusqu'à PHPUnit.** La commande suivante a été tentée sans écriture de cache ni de rapport annexe :

```text
wsl.exe -d Ubuntu -- docker exec -w /work imagine-c03-d60863809aab php vendor/bin/phpunit --do-not-cache-result --fail-on-warning --fail-on-risky --fail-on-deprecation --testsuite Envoi
```

Résultat : code 1, `Wsl/Service/E_ACCESSDENIED`, avant toute exécution Docker/PHP. Aucun PHP ou Composer n'est disponible dans le PATH Windows ; aucune installation n'a été faite. Le conteneur historique est par ailleurs annoncé supprimé dans `cleanup.json`. Le lanceur complet n'a pas été utilisé, car il réécrit des sources dans son conteneur et crée des preuves hors de l'unique fichier autorisé. Cette limitation d'environnement ne constitue pas un échec des tests du lot.

Les XML et le reçu `production/C-07/replays/reveil-22nov-0340/final.json` ont été lus et confrontés aux fichiers actuels : **97 empreintes concordantes**, hors README, incluant les sources, tests, configurations et fichiers Composer enregistrés dans ce reçu.

| Preuve livrée, PHP 8.2.36 | Tests | Assertions | Erreurs / échecs / ignorés |
|---|---:|---:|---|
| Suite standard | 270 | 29 594 | 0 / 0 / 0 |
| Envoi ciblé | 36 | 78 | 0 / 0 / 0 |
| Régression connecteur C-04 | 37 | 224 | 0 / 0 / 0 |

Ces résultats sont ceux de la production, pas d'une exécution indépendante. Le reçu annonce également syntaxe et validation Composer à zéro, mais lint global à **1** ; les six avertissements C-05 sont explicitement réservés dans le rapport de production. Aucun lint global vert n'est déduit de ces pièces.

La suite couvre les profils, les paiements autour de la clôture, les changements d'adresse et de bénéficiaire, le rejeu, le filtrage C-01 et le CSV. Elle ne couvre pas les trois anomalies ci-dessus. Le test d'intégration C-01 écarte les clôtures antérieures au 1er novembre 2026 : il ne vérifie donc pas effectivement 170, juste avant le premier numéro de l'exemple. Le renouvellement, une fin exactement à la clôture et une grâce avec fin effective méritent également des assertions explicites.

### C07-CX-04 — Mineur — Oracle CSV calqué sur l'implémentation

**Localisation :** `wp/plugins/imagine-pilotage/tests/Envoi/ExportCsvTest.php:34`.

**Problème :** le résultat attendu est calculé avec la même expression régulière et la même construction que `CsvProtection::cellule`. Une erreur commune aux deux expressions, ou leur modification conjointe, peut laisser ce test vert. Le test de roundtrip ne fixe indépendamment que le cas `=1`.

**Correction proposée :** remplacer le calcul de l'attendu par une table de couples entrée/sortie littéraux, couvrant les quatre préfixes de formule, les contrôles initiaux et les chaînes inchangées. Vérifier ces résultats dans les cellules du CSV exporté, sans reprendre le prédicat de production.

## 4. Sécurité et données

Aucun secret ni donnée réelle identifié dans les sources, fixtures et exemples examinés. Les noms sont fictifs. Aucun accès réseau, WordPress ou base dans le moteur ; droits administratifs, nonces et requêtes SQL relèvent du branchement futur. Le lot ne restitue aucun contenu réservé : pas de voie de fuite du paywall identifiée dans ce périmètre.

La protection CSV est réellement partagée avec C-04 et appliquée à toutes les colonnes de données. Le CSV utilise l'échappement explicite sans antislash. `ExportCsv::liste` refuse les anomalies non revues ; les cas C07-CX-01 à C07-CX-03 contournent ce garde-fou en empêchant leur détection. Le booléen de revue et le sérialiseur bas niveau sont documentés comme nécessitant un parcours administratif ultérieur, sans être présentés comme une autorisation.

## 5. Doctrine

Logique métier séparée de WordPress, objets immuables, dates immuables, horloge injectée, namespace attendu et typage strict respectés. Le sur-mesure correspond au calcul explicitement demandé par le brief ; la réutilisation de C-01 et de la protection C-04 évite de les réimplémenter. Le README décrit les contrats, dépendances et commandes de tests.

Les dates sont comparées comme des instants et la clôture est normalisée par `Numero` en Europe/Brussels. Les notes exigent ce fuseau pour les entrées Envoi. La réserve sur le lint global est transparente. Aucune correction ni modification hors du présent rapport n'a été effectuée.

## 6. Études (lots sans code)

Sans objet : lot de code. Aucun comportement d'extension tierce n'est affirmé ici sur la base d'une documentation externe non consultée.

## Verdict

**À corriger.** Ce verdict n'est pas un GO.

- **Bloquant :** aucun défaut classé à ce niveau dans le périmètre examiné.
- **Important — C07-CX-01 :** abonnement individuel/offert sans destinataire supprimé silencieusement de la liste.
- **Important — C07-CX-02 :** doublons du même destinataire non signalés avec une variation de casse accentuée.
- **Important — C07-CX-03 :** adresse ou pays composés uniquement d'espaces Unicode acceptés sans anomalie.
- **Mineur — C07-CX-04 :** oracle de protection CSV reproduisant l'implémentation.

Après correction, rejouer Envoi et les régressions C-04 dans le banc autorisé. Le présent examen ne remplace pas ce rejeu, qui reste non exécuté du fait du refus WSL. Les trois arbitrages explicitement demandés par le brief restent ouverts dans les notes de production.
