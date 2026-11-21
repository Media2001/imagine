# Lot C-05 — Paiement en quatre fois : proposition de mécanisme et preuve

**Chantier** : C. **Nature** : note de conception, prototype sur site jetable, tests.
**Emplacement** : `wp/plugins/imagine-pilotage/src/Echeancier/`, `tests/Echeancier/`, et `production/C-05/`.
**Délai** : une demi-journée.
**Cas d'acceptance concernés** : R-02, R-16, R-17.

## Pourquoi

L'étude A-00 (besoin 2) conclut que la synchronisation native de Subscriptions ne garantit pas des échéances communes à tous, calées sur les trimestres civils. Ced a tranché le 21/11 : **exactement quatre paiements, initial compris, par année d'engagement de date à date**, et il t'autorise à **soumettre** un mécanisme. Ce lot est cette soumission : une proposition prouvée, pas une mise en production.

## La règle à mettre en œuvre

- Une échéance par numéro (§3.4, §3.5). Le paiement initial, à la commande, paie le premier numéro. Les trois suivants paient les trois numéros suivants.
- Chaque échéance postérieure à la commande est lancée avant la clôture de la liste d'envoi du numéro qu'elle paie, avec une marge en jours paramétrable. Ces dates sont donc **communes à tous les abonnés** d'un même numéro.
- Il y a toujours exactement quatre paiements par année d'engagement, quel que soit le jour de la commande : jamais trois, jamais cinq.
- À la reconduction, l'année suivante reprend au numéro qui suit ; ses quatre échéances tombent toutes à des dates communes.
- Les quatre échéances sont dues : ce n'est pas un abonnement trimestriel résiliable entre deux échéances.

Les dates viennent du moteur C-01 (calendrier de parution). Ne recalcule rien que C-01 calcule déjà.

## Ce qu'il faut produire

1. **L'échéancier en PHP pur** : à partir d'une date de commande et du calendrier, la liste des quatre échéances de l'année d'engagement (date, numéro payé, rang), puis celles de l'année de reconduction. Tests : commande à chaque moment du trimestre, dont la veille, le jour et le lendemain d'une clôture ; les contre-exemples de l'étude A-00 où une date commune « en trop » apparaîtrait.
2. **La note de conception** `production/C-05/proposition.md` : comment piloter WooCommerce Subscriptions pour qu'il suive cet échéancier. Compare au moins deux voies, avec leurs sources officielles (celles de l'étude A-00 suffisent) : par exemple un abonnement à période courte dont la date du prochain paiement est fixée par code après chaque paiement, ou un abonnement annuel accompagné de trois paiements planifiés. Pour chacune : ce que voit l'abonné dans son compte, ce que devient un paiement échoué, comment se fait la reconduction annuelle, comment se compte l'engagement, ce que ça donne côté Odoo. Recommande une voie.
3. **La preuve sur site jetable**, avec le vrai Subscriptions, hors ligne, sans passerelle réelle (renouvellement manuel, comme dans ton banc A-01) : la voie recommandée produit bien quatre paiements aux dates de l'échéancier sur une année, puis reconduit, pour trois dates de commande différentes.

## Ce que tu ne décides pas

Liste en questions fermées, sans y répondre : la marge avant clôture ; ce que devient l'engagement après un rejet en cours d'année (décisions 8 et 12 d'Imagine) ; le montant de chaque échéance si le tarif change en cours d'année.

Rien n'est branché sur le site. Aucun GO financier.
