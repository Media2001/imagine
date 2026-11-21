# C-05 — proposition d’échéancier (21 novembre 2026)

**Statut : BLOQUÉ pour l’acceptance intégrale ; proposition et prototype vérifiés, sans PRET.** Aucun branchement sur un site existant, aucune décision financière, aucun encaissement. Voir le contre-exemple ci-dessous avant toute utilisation.

## 1. Le point qui empêche de promettre « tous les jours de commande »

Les règles suivantes ne sont pas simultanément satisfaisables pour toutes les commandes : premier numéro encore ouvert selon C-01 ; initial à la commande ; quatre paiements dans chaque année de date à date ; premier numéro de reconduction suivant le quatrième ; échéances reconduites toutes communes à clôture moins une marge positive.

**Contre-exemple entièrement fictif, issu du calendrier de test de C-01 :** clôtures régulières les 10 janvier, avril, juillet et octobre, sorties les 20 ; marge de démonstration 7 jours civils, donc dates communes les 3.

- Commande le **9 avril 2027 à 12 h Bruxelles** : C-01 attribue avril, juillet, octobre 2027 et janvier 2028.
- Année initiale : 9 avril 2027, 3 juillet 2027, 3 octobre 2027, 3 janvier 2028. Le premier numéro est payé à la commande ; on ne rajoute pas le 3 avril passé.
- Reconduction anniversaire le **9 avril 2028 à 12 h** : C-01 attribue ensuite avril, juillet, octobre 2028 et janvier 2029.
- La date commune du premier de ces numéros est le **3 avril 2028**, soit **avant** cet anniversaire. L’appliquer donne un cinquième paiement dans la première fenêtre de date à date. La supprimer laisse le premier numéro reconduit impayé. La déplacer ne respecte plus la date commune et la marge.

Ce n’est ni une limitation de WooCommerce ni une raison de modifier C-01. Pour toute marge positive, une commande entre la date commune du premier numéro et sa clôture peut produire ce conflit au cycle suivant. Le balayage quotidien fictif de 2027 détecte **28 dates à midi sur 365**, refusées à la reconduction ; ce nombre dépend du calendrier et de la marge, pas des tarifs.

**Position du prototype : refus explicite `HORS_ENGAGEMENT`, avant toute écriture Woo.** Aucun numéro n’est supprimé ou substitué, aucune date n’est reportée et aucune cinquième position n’est créée. Ce garde-fou est testé ; il ne résout pas le besoin « quel que soit le jour ». Arbitrage fermé en §6.

## 2. Standard examiné avant le sur-mesure

La référence Woo permet des périodes en jours, semaines, mois et années.[3] Mais l’alignement natif du premier renouvellement ignore l’intervalle supérieur à une unité : l’exemple officiel d’une inscription le 6 avril, tous les trois mois, donne le 1er mai, non le 1er juillet.[5] Il ne suffit donc pas de cocher « trimestriel synchronisé ».

Les fonctions documentées `update_dates`, `can_date_be_updated` et les relations de commandes permettent un raccord fin plutôt qu’un nouvel encaisseur.[1] Une action de renouvellement peut être déclenchée sur calendrier ou explicitement hors calendrier ; l’action spécifique de passerelle est distincte.[4]

### Deux voies possibles — comparaison de conception, pas promesse de couverture native

| Aspect | A — Cadence courte, prochaine date pilotée | B — Support annuel et trois appels complémentaires |
|---|---|---|
| Support Woo | Abonnement sans expiration automatique, période technique de trois mois ; chaque prochain paiement est remplacé par la date du plan C-01, via l’API de dates. La cadence n’est pas la durée d’engagement.[1][3] | Abonnement de période annuelle ; trois actions supplémentaires doivent créer des commandes reliées, ou appeler explicitement le cycle de renouvellement. Ces actions hors calendrier sont possibles, mais leur combinaison n’est pas un fractionnement annuel natif documenté.[3][4] |
| Ce que verrait l’abonné | Prochaine date et commandes natives ; le libellé technique trimestriel ne doit pas laisser croire à une résiliation trimestrielle. Un récapitulatif des quatre positions et de l’anniversaire reste à raccorder. Le compte rendu visuel n’est pas implémenté ici.[2] | L’annuel est plus proche du contrat affiché, mais les trois sommes complémentaires et leur lien à la dette annuelle exigent aussi un récapitulatif spécifique. Ne pas afficher une charge annuelle entière en plus de trois fractions. |
| Paiement échoué | Une position reste la même créance ; pas de rang supplémentaire sur un échec ou une reprise. Le comportement natif peut laisser l’abonnement en attente ; droits, grâce et maintien de l’engagement ne sont pas décidés ici.[2][6] | Même prudence pour la position concernée ; les commandes complémentaires doivent être incluses dans le traitement des échecs, faute de quoi elles divergent du support annuel. Ce raccord n’a pas été exercé. |
| Reconduction | Anniversaire = changement de bloc d’engagement, **pas** un débit supplémentaire. Les quatre positions suivantes viennent de C-01 ; la première commune doit encore appartenir à la nouvelle fenêtre contractuelle. Le conflit du §1 reste bloquant. | Le renouvellement annuel natif ne coïncide généralement pas avec la première date commune. Il faut donc le déplacer, ou séparer renouvellement du contrat et première fraction ; cela retire l’avantage de simplicité. Même conflit du §1. |
| Comptage d’engagement | Quatre identités `(abonnement, cycle, rang)` attachées à quatre numéros, dont l’initial au cycle 1. Anniversaire et opposition à reconduction sont indépendants de l’intervalle technique. | Même compteur nécessaire ; le nombre de commandes de renouvellement ne suffit pas à distinguer appel annuel et fraction. |
| Côté Odoo | Proposition : chaque commande porte cycle, rang, numéro et date théorique ; paiement validé et engagement annuel sont des événements distincts, à passer ensuite par la file C-04. Aucun événement Odoo n’est émis ici ; champs, facturation et étalement restent à confirmer par Step. | Même données, avec en plus une distinction stricte entre support annuel et appels complémentaires pour éviter de compter cinq créances ou de facturer deux fois la somme annuelle. Aucun connecteur n’est ajouté. |

**Recommandation conditionnelle : voie A.** Elle conserve un seul flux natif de commandes de renouvellement et une seule prochaine action. B ajoute trois circuits sans résoudre le conflit contractuel. La recommandation reste une proposition à relire et ne vaut ni arbitrage financier ni GO.

## 3. Mécanisme limité et exercice réel

`Planificateur` reçoit un `Numeros\Moteur`, une `Annee`, la borne exclusive de l’engagement et une marge explicitement fournie. Il ne lit ni horloge ni WordPress. Il appelle **uniquement C-01** pour sélectionner les quatre numéros et calculer leurs dates communes. Il remplace la première date du premier cycle par la commande. Il refuse calendrier incomplet, dates non croissantes et date hors fenêtre. La borne est fournie séparément : la validité numérique après activation n’est pas assimilée silencieusement à l’engagement après commande. Dans la fixture, activation immédiate et anniversaire proviennent de C-01, y compris le 29 février.

`RaccordManuel` ne contient aucune logique de calendrier et ne s’enregistre sur aucun hook. Il utilise l’API officielle de dates en UTC, après vérification de modifiabilité.[1] Il refuse tout abonnement sans marqueur fictif C05, sans drapeau explicite de renouvellement manuel ou avec identifiant de passerelle non vide. Aucun booléen de mode staging n’est employé pour autoriser un paiement.

Le pilote de la fixture applique le raccord après chaque validation locale réussie, puis ne traite **que** l’action native de l’abonnement fictif concerné. L’absence de validation n’est jamais comptée comme paiement. Une deuxième application de la même date conserve une seule action en attente. Le dernier appel est stoppé à la fin de l’horizon démontré, sans annuler l’abonnement ni effacer de dette.

Un futur raccord autonome devra conserver durablement le curseur, verrouiller les concurrences, gérer échec/reprise/opposition à reconduction et empêcher une avance anticipée. Il ne suffit pas de brancher aveuglément `woocommerce_subscription_payment_complete` : la documentation signale le traitement particulier des renouvellements anticipés.[4] **Ce branchement complet n’est pas livré ni déclaré prouvé.** Le prototype exerce l’API et les vraies créations manuelles demandées, pas un moteur de production.

Le renouvellement manuel natif demande normalement une action du client ; il ne constitue pas un prélèvement automatique.[2] Les reprises automatiques ont leurs prérequis et ne sont pas démontrées par ce banc manuel.[6]

## 4. Preuve acquise, sans gonfler sa portée

- PHP pur : **376 tests, 1 473 assertions, 0 échec** ; 365 jours de commande, clôture veille/jour/lendemain, marges 1/3/7 et refus 0/-1, calendrier incomplet, fuseaux et 29 février, contre-exemple A-00 et refus de la cinquième charge.
- Vrais **Subscriptions 9.4.1**, WordPress **7.0.9**, WooCommerce **11.1.1**, PHP **8.2.36** ; trois commandes pour **chacun** des stockages classique et HPOS : 20 février, 10 avril et 11 octobre 2027.
- **6 abonnements, 6 commandes initiales et 42 vraies commandes de renouvellement** : quatre positions initial comprises puis quatre reconduites par scénario, **48 commandes au total**. **230 contrôles de scénario par stockage**, tous réussis. Ces contrôles ne sont pas 460 parcours financiers indépendants.
- Les dates enregistrées de `next_payment` et des actions natives correspondent exactement aux dates C-01, avec conversions hiver/été. Les actions futures sont exécutées explicitement en accéléré ; les confirmations locales ont l’heure réelle d’exécution. **Ce n’est pas une attente de deux ans, ni une preuve de débit bancaire à une date future.** Les reçus séparent date théorique, date native d’action et date de validation Woo.
- Les trois dates positives ne masquent pas les 28 contre-exemples de la suite pure. Elles ne prouvent donc pas l’acceptance universelle.

Reçus : `preuves/final-unit-3-result.json`, `preuves/final-e2e-3-result.json`, manifests et syntaxe associés ; RED/GREEN conservés. Commandes de reprise et limites dans `notes.md`.

## 5. Isolation et périmètre

Image synthétique A-01 existante réutilisée par identifiant immuable, aucun téléchargement dans le banc. Seul le ZIP Subscriptions autorisé est lu dans la bibliothèque de paquets, avec empreinte vérifiée ; ni ZIP ni licence ne sont copiés dans le dépôt. Memberships n’est pas utilisé. Nouveau conteneur possédé C05, réseau `none`, aucun montage/volume/port, capacités supprimées ; MariaDB uniquement sur socket Unix, aucun serveur web. Emails et HTTP bloqués dans la fixture. Aucune archive de site, aucun compte réel, aucun outil installé sur l’hôte, aucune opération Git ni modification de staging. Ressource C05 supprimée et absence vérifiée (`preuves/cleanup.json`). Le verrou du parent est laissé intact.

## 6. À arbitrer par Ced / Imagine — aucune réponse appliquée

1. **Conflit du §1 : quelle règle amender ?** A — compter quatre créances par bloc de numéros, en acceptant qu’une fenêtre anniversaire contienne cinq dates ; B — autoriser une exception à la date commune **et à la marge** pour la première position reconduite ; C — revoir le premier numéro attribué dans la fenêtre entre lancement commun et clôture. **Choisir A / B / C**, ou demander une nouvelle règle explicite ; aucune de ces dérogations n’est codée. C impliquerait un nouveau brief C-01, pas une correction furtive.
2. **Marge** : une valeur positive explicite fournie par l’administration, en jours civils, sans valeur par défaut : **oui / non** ? La valeur métier reste à fournir ; 7 n’est qu’une valeur de démonstration.
3. **Rejet en cours d’année** (décisions Imagine 8 et 12) : les quatre créances restent-elles intégralement dues malgré le rejet : **oui / non** ? Et la priorité d’accès est-elle **retrait immédiat / délai de grâce** ? Ni remise, ni report, ni abandon, ni règle de droits n’est ajouté.
4. **Changement de tarif** : **montants figés pour les quatre positions de l’année / nouveau tarif pour les seules positions non encore payées** ? Aucun calcul de montant ni taxe ni port dans le moteur ; les 10 EUR de la fixture ne sont pas un tarif Imagine.

## Sources
