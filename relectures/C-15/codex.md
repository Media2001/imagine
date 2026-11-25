# Relecture indépendante Codex — C-15

Date : 25 novembre 2026. Références : `relecteurs/AGENTS.md`, doctrine, grille, brief C-15, cahier des charges §3.13 et passage relatif aux mandats papier du §3.6, décisions du dépôt. Production C-15, code, tests et raccords C09/C13 examinés. La relecture Claude n'a pas été consultée. Aucun accès au site, à une base ou à un compte.

## 1. Conformité

Les cinq vues, les périodes 30/90/180 jours, l'export CSV et l'action unique sur un virement sont présents. Le code utilise les objets WooCommerce/Subscriptions, sans registre parallèle des paiements. La convention fictive A-VIR/A-PAPIER est explicitée et contrôlée par environnement, URL, marqueurs, propriétaire et manifeste. Aucun nouveau délai de retard n'est introduit. Les livrables `A-VOIR.md`, rapport et `PRET` sont présents.

La couverture fonctionnelle reste incomplète pour les mandats déjà exigibles (R1). La preuve de refus d'une seconde validation couvre seulement deux requêtes successives (R2).

## 2. Exactitude métier

Cas déroulés à la main sur les branches du code, sans les présenter comme des tests exécutés :

| Cas | Résultat du code et appréciation |
|---|---|
| §3.13, virement `bacs`, commande `on-hold`, sans date de paiement, reliée à une souscription du même client | Présent dans « attente » et « virements ». Après paiement natif, statut payé ou date payée l'excluent ; une nouvelle validation séquentielle est refusée. Conforme au parcours nominal. |
| §3.13, renouvellements `failed` A-GRACE et A-SUSP, non payés | Présents dans « échecs » ; aucune ancienneté ni fermeture d'accès supplémentaire n'est calculée. Conforme à la séparation avec C06/C10. |
| §3.13, fin au 1er janvier 2027 à 12 h UTC, horloge au 25 novembre 2026 à 12 h UTC, aucune prochaine échéance | Exclue à 30 jours, incluse à 90 et 180 jours. Le changement d'année ne modifie pas le calcul. Une date égale à l'instant courant est incluse. |
| §3.6/§3.13, mandat papier dû et impayé, souscription `on-hold`, référence renseignée | Exclu du fichier des mandats, même si sa date est connue et déjà due : R1. |

**R1 — Important — `wp/plugins/imagine-site/EcheancesRegles.php:17`.** Le filtre exige une souscription `active` et une `next_payment` non nulle. Il exclut donc un mandat exigible dont la souscription est en attente de règlement (`on-hold`). La branche native des mandats ne consulte pas les commandes de renouvellement : une échéance impayée n'est pas récupérée si la prochaine date a été effacée ou avancée. L'affirmation « un mandat dont la prochaine date native est déjà due reste à lancer » ne vaut ainsi que tant que le statut reste actif. Or la liste doit permettre de préparer les prélèvements à l'échéance, y compris les sommes encore à traiter ; une ligne dans « paiements en attente » ne remplace pas l'export avec référence du mandat.

Correction proposée : rapprocher les échéances papier des commandes de renouvellement natives impayées pour conserver les sommes effectivement dues, avec leur montant et leur date, sans doublonner la prochaine échéance. Distinguer une attente de règlement d'une suspension pour un autre motif ; ne pas simplement autoriser tous les `on-hold`. Ajouter les cas « avant échéance », « renouvellement exigible non payé » et « renouvellement payé ». Le catalogue ne démontre actuellement que le premier état : signaler cette limite sans créer de nouveau profil hors C09.

**R2 — Important — `wp/plugins/imagine-site/EcheancesAdmin.php:132`.** La validation de l'impayé précède l'écriture sans exclusion mutuelle par commande. Deux confirmations peuvent donc toutes deux obtenir un objet encore impayé. Après `payment_complete()`, le contrôleur vérifie seulement que la commande est désormais payée, puis ajoute sa note d'opérateur ; il ne distingue pas un paiement réalisé par cette requête d'un paiement réalisé entre-temps. Même un refus natif retourné par `payment_complete()` n'est pas examiné. Deux requêtes concurrentes peuvent ainsi attribuer la réception du même virement à deux opérateurs et annoncer toutes deux un succès. Le test de double validation attend la fin de la première requête avant d'envoyer la seconde.

Correction proposée : protéger l'ensemble « relecture de l'impayé, paiement, note » par une exclusion mutuelle par commande, relire après acquisition et libérer systématiquement. Employer un mécanisme natif approprié s'il existe, sans registre parallèle. Tester deux confirmations simultanées : un seul succès et une seule note C15 ; la seconde doit être refusée. Aucun double débit bancaire n'est allégué ici.

## 3. Tests

Tentative de rejeu des tests PHP purs, avec dépôt monté en lecture seule et réseau désactivé :

```text
wsl.exe -d Ubuntu -- docker run --rm --pull never --network none --read-only --user 65534:65534 --cap-drop ALL --security-opt no-new-privileges --mount type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly --entrypoint php imagine-tests-t01:1 /repo/wp/tests/demo/c15-unit.php
```

Résultat : code de sortie 1, `Wsl/Service/E_ACCESSDENIED`, avant démarrage des tests. Aucun PHP disponible dans le PATH. **Aucun résultat vert indépendant n'est donc revendiqué.**

Le lanceur `c15-verifier.py` n'a pas été exécuté : il accède au site, déploie des fichiers et réécrit les preuves de production, ce que les droits du relecteur interdisent. Les recettes HTTP/natives ont été examinées dans leurs sources et leurs résultats enregistrés.

`production/C-15/verification.json` annonce 257 contrôles/tests : 18 purs C15, 21 natifs C15, 43 HTTP, 16 action/reset, 10 tests C13 et 149 contrôles C09. Les quatre empreintes SHA-256 enregistrées correspondent aux trois classes C15 et au bootstrap présents. Cela rattache les preuves aux sources examinées, sans remplacer leur rejeu.

**R3 — Mineur — `wp/tests/demo/c15-unit.php:20`.** Le test nommé `30_jours_inclus_tri_date_id` ne vérifie ni une échéance retenue exactement à J+30 ni un départage par ID : sa première ligne possède une prochaine date à J+29, prioritaire sur sa fin à J+30, et toutes les dates retenues sont différentes. Le test à 180 jours n'inclut aucune date située entre J+90 et J+180. Des erreurs sur ces bornes ou sur le second critère de tri resteraient vertes.

Correction proposée : ajouter des dates retenues exactement à J+30 et J+180, leurs voisines à une seconde, deux objets de même date présentés dans l'ordre inverse des IDs, et un objet sans prochaine date ni fin. Étendre aussi la couverture au parcours R1 et à la concurrence R2.

## 4. Sécurité et données

Contrôles satisfaisants à la lecture : capacité vérifiée indépendamment du nonce, POST obligatoire, nonce lié à la commande ou à la période, validation des paramètres scalaires, confirmation serveur, contrôle du propriétaire et refus des remboursements dans l'action. Les sorties HTML sont échappées. Le CSV possède des colonnes fermées, neutralise les préfixes de formule, sort directement dans la réponse privée et ne crée aucun fichier public. Aucun IBAN n'est lu dans les projections ; les données examinées sont fictives.

Les filtres de transport sont présents autour du paiement. La preuve native contrôle également la garde générale de la démonstration : elle ne constitue pas à elle seule une preuve d'absence d'envoi différé hors de cette garde. Aucun appel extérieur n'a été effectué pour cette relecture.

Le lot n'ajoute pas de voie de diffusion de contenu réservé ; pas de modification du paywall identifiée. L'intégrité de l'audit de paiement reste concernée par R2.

## 5. Doctrine

Séparation effective entre projections PHP pures, lecture des objets natifs et contrôleur WordPress ; `strict_types`, espace de noms `Imagine\Site`, préfixes WordPress et README présents. Le paiement utilise bien la fonction native. Les références officielles sont consignées dans `A-VOIR.md` ; elles n'ont pas été ouvertes, conformément au périmètre de lecture locale.

**R4 — Mineur — `wp/plugins/imagine-site/EcheancesAdmin.php:221`.** La colonne « État » affiche directement les identifiants `active`, `pending-cancel`, `on-hold`, `failed`, etc. Ces textes anglais ne passent pas par une traduction, contrairement à la doctrine §5.

Correction proposée : conserver les identifiants pour les filtres et afficher les libellés français des statuts natifs, adaptés au type commande/souscription, puis les échapper.

### Décisions techniques, défaut proposé

R2 relève de la technique : défaut proposé, une seule confirmation en cours par commande, sans attente d'arbitrage utilisateur. R3 et R4 relèvent également de corrections techniques. Aucun changement de droit d'accès ni de délai métier n'est proposé.

## 6. Études (lots sans code)

Sans objet : lot de code. Pas de nouvelle étude d'extension à valider.

## Verdict

**À corriger.** Ce verdict n'est pas un GO.

- **Bloquant :** aucun établi.
- **Important :** R1, mandats exigibles exclus de l'export ; R2, confirmations concurrentes et attribution de l'audit non protégées.
- **Mineur :** R3, bornes et départage insuffisamment testés ; R4, statuts affichés en anglais.

Limite de validation : rejeu local empêché par les permissions WSL ; preuves enregistrées examinées et empreintes concordantes, mais tests non exécutés jusqu'au bout par le relecteur. Validation visuelle laissée à Ced, comme prévu au brief.
