# Synthèse du cahier des charges v3.1

Lecture du 11/11/2026. Le cahier des charges fait foi ; cette page sert à s'y retrouver.

## Principe

Le site est la seule source de vérité pour l'abonné, son statut et ses droits. Il vend, gère les abonnés et leur écrit (par Brevo). Odoo facture. Les données vont du site vers Odoo, sauf deux retours conditionnés à Step : statut des virements et factures consultables dans le compte (§2).

## Composants imposés (§4.1)

Thème sur mesure sans constructeur de pages · WooCommerce · Subscriptions · Memberships · ACF Pro · Rank Math Pro · Event Tickets Plus · Stripe · PayPal · Brevo · extension « pilotage » sur mesure · connecteur vers Odoo (n8n ou intégré, à arrêter).

## Les blocs à construire

| Bloc | Références | Nature |
|---|---|---|
| Modèle éditorial : numéro, article, thématique, événement, partenaire | §3.3, §4.2 | Standard + ACF |
| Thème, gabarits, mode lecture | §3.1 à §3.3 | Sur mesure, après maquettes |
| Offre : un abonnement annuel, 3 tarifs, 1 ou 4 paiements | §3.4 | Standard à vérifier |
| Règle des numéros, calendrier de parution | §3.5 | Sur mesure |
| Paiements : carte, Bancontact, SEPA, PayPal, virement, mandat papier | §3.6 | Standard à vérifier |
| Tunnel une page, compte client, rétractation | §3.7 | Mixte |
| Abonnements offerts et groupés, professionnels, codes de réduction | §3.4 | À vérifier |
| Emails du cycle de vie, impayés, délai de grâce | §3.8 | Mixte |
| Paywall côté serveur, robots vérifiés, étanchéité | §3.9, §4.4 | Sur mesure |
| Brevo : contacts, statuts, étiquettes de persona | §3.10 | Sur mesure |
| Agenda et billetterie | §3.11 | Standard |
| CoopHub : attribut coopérateur | §3.12 | Selon documentation |
| Back-office : échéances, justificatifs, liste d'envoi, extractions, tableau de bord | §3.13 | Sur mesure |
| Connecteur Odoo : file, rejeu, quarantaine, export de secours | §2.2 à §2.5 | Sur mesure |
| Migration : contenus, abonnés en ligne, base Access, codes | §4.3 | Sur mesure |
| Tests de réception | §5 | Sur mesure |

## Points durs

1. **Échéances calées sur les parutions** (§3.5) : les prélèvements en quatre fois suivent les dates de clôture des listes d'envoi, qui ne sont pas régulières.
2. **Robots vérifiés et cache** (§4.4) : deux versions d'une même page pour des visiteurs anonymes ; le cache doit les distinguer. Conditionne l'hébergeur.
3. **Étanchéité** (§3.9) : REST, flux, oEmbed, recherche, aperçus de partage.
4. **Seuils contractuels** (§5) : Lighthouse mobile ≥ 90 en performance sur le tunnel, WCAG 2.1 AA.
5. **Renouvellements PayPal et Bancontact vers SEPA** (§3.6) : à vérifier avant tout développement.
6. **Garantie** (§11) : trois mois de correctifs sans limite d'heures.
7. **Planning** (§10) : mise en ligne estimée fin janvier 2027 ; décisions 3 à 5 du chapitre 7 encore ouvertes.

## Écarts avec les décisions antérieures

| Sujet | Avant | Cahier des charges v3.1 |
|---|---|---|
| Retours d'Odoo | Aucun | Statut des virements et factures, si Step fournit les données |
| Numéro d'entreprise | Contrôle de format (modulo 97) | « Affiche la dénomination trouvée » : suppose une recherche en ligne |
| Redirections, hébergement | Hors périmètre | Mise en place et test dans le périmètre |
| Moyens de paiement | Carte, SEPA, virement | + PayPal, Bancontact, mandat papier |
| Accès newsletter par lien signé, article offert | Prévus | Remplacés par l'accès découverte |
| Dépôt de code | — | « Chez UPARTNER » ; voir `decisions.md` |
