# Registre des écarts

Toute demande hors cahier des charges, toute contradiction interne au cahier des charges, tout blocage dû à un tiers. Une ligne par écart, datée. Tenu par Claude à partir des rapports.

| Date | Origine | Écart | Effet | Suite |
|---|---|---|---|---|
| 11/11/2026 | Cahier des charges §3.4 | Le numéro d'entreprise doit « afficher la dénomination trouvée », alors que la décision d'octobre prévoyait un simple contrôle de format. | Une recherche en ligne à développer. | À trancher (`decisions.md`, point 8). |
| 11/11/2026 | Cahier des charges §5 | « Dépôt de code chez UPARTNER, aucune dépendance à un compte personnel », alors que le dépôt est chez Media2001. | Copie ou transfert à prévoir à la réception. | Dépôt maintenu chez Media2001 (Ced, 11/11). |
| 11/11/2026 | Imagine | Décisions 3, 4 et 5 du chapitre 7 ouvertes à la date de démarrage de la production. | Tunnel et emails non finalisables. | En attente d'Imagine. |
| 11/11/2026 | Cahier des charges §4.3 | Le cahier des charges décrit une migration des abonnés en ligne vers un nouveau site. Décision : on repart de la production et on la met à niveau. | Moins de migration, mais une mise à jour de l'existant à sécuriser et à rejouer à la bascule. | Tranché (`decisions.md`). À faire savoir au pilote du projet. |
| 20/11/2026 | Étude A-00, besoin 3 · brief vs §3.6 | Le brief de l'étude supposait un prélèvement SEPA après une première carte. Le cahier des charges ne prévoit le passage au SEPA que pour Bancontact ; la carte se renouvelle par carte. | Parcours et mandat différents selon la réponse. | Ouvert : question A de `corrections/A-00.md`, pour le pilote du projet. |
| 20/11/2026 | Étude A-00, besoin 7 · §3.8 | Le cahier des charges demande que les emails de Stripe soient désactivés. Avec l'identifiant créancier de Stripe, la prénotification SEPA envoyée par Stripe est obligatoire. | « Aucun email de Stripe » ne peut pas être promis en l'état. | Ouvert : question 4 de l'étude, pour Imagine. |
| 20/11/2026 | Étude A-00, besoin 2 · §3.5 | La synchronisation native de Subscriptions ne garantit pas des dates d'échéance communes à tous les abonnés, calées sur les trimestres civils. | Un raccord sur mesure est nécessaire pour le paiement en quatre fois. | Acté. Mécanisme à soumettre (arbitrage du 21/11). |
| 20/11/2026 | Lot C-04 | Les cas de recette R-39, R-40 et R-41 ne sont couverts qu'au niveau du cœur de file. Le parcours complet est dû au lot de branchement. | La recette du connecteur ne peut pas être prononcée sur C-04 seul. | À reprendre au lot de branchement. |
| 20/11/2026 | Lot C-04 | Les messages destinés à l'administration ne passent pas encore par les fonctions de traduction (code hors WordPress). | À ré-emballer au branchement. | À reprendre au lot de branchement. |
| 20/11/2026 | Lot C-04 · Step | Le champ `payment_reference` de l'événement n'est pas confirmé par Step. | Format de l'événement provisoire. | À poser à Step avec les champs attendus par Odoo. |
| 22/11/2026 | Relecture C-07 | `docs/recette/profils.md` disait A-SANSMAIL « exclu des envois », ce qui contredisait la règle 5 du brief C-07 (il figure dans la liste postale). | Ambiguïté de rédaction, sans effet sur le code. | Corrigé le 22/11 : exclu des envois par email seulement. |
| 22/11/2026 | Lot C-05 | Le brief C-05 et l'arbitrage du 21/11 demandaient « jamais cinq » paiements par année de date à date, ce qui est incompatible avec des échéances communes à tous les abonnés. | Règle impossible à tenir pour une commande passée entre la date commune et la clôture. | Tranché le 22/11 : quatre échéances par bloc de quatre numéros ; une fenêtre de date à date peut en contenir cinq. |

## 23 novembre 2026 — voie 2

- L'extension `imagine-site` réunit le modèle de contenu provisoire (B-00) et le branchement du paywall (C-08) : B-00 ne se relit plus isolément. Accepté pour la démonstration ; à séparer quand le vrai modèle éditorial sera défini.
- Modèle de contenu de la démonstration (numéro, rattachement des articles) : provisoire, sans ACF, à remplacer après l'audit de l'existant.
