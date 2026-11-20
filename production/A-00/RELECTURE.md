# A-00 — Transmission pour relecture

**Périmètre : étude documentaire uniquement, 20 novembre 2026.** Aucun GO demandé pour une installation, un achat, une connexion de compte ou une bascule. `PRET` signale la remise de l'étude ; il ne signifie pas que les parcours de paiement ou le paywall sont validés.

## Dossier à relire

1. `couverture-extensions.md` : synthèse et dix-neuf besoins, capacités natives, compléments, adaptations, doutes et questions fermées à Ced.
2. `sources-officielles.json` : sources retenues, URL demandées/finales, horodatage, courts extraits anglais exacts.
3. `registre-citations.json` : correspondance des appels de source avec leurs URL et preuves littérales.
4. `sources-collectees.json` : journal des tentatives HTTP, redirections et indisponibilités ; pas de copie intégrale de documentation dans la remise.
5. `verification.json` : contrôles documentaires, empreintes du dossier, décomptes des exemples et concordance du reçu A-01 préexistant. Ce fichier est produit après les dernières modifications du texte.

## Points prioritaires

- **Besoin 2** : le premier alignement trimestriel ignore l'intervalle long et prend le prochain jour mensuel. Le contre-exemple officiel 6 avril → 1er mai interdit de conclure que ce seul réglage aligne tous les abonnés sur les trimestres civils. Le premier paiement entier, lui, est documenté.
- **Besoin 2** : expiration après quatre paiements ≠ engagement annuel reconduit. Le contre-exemple fictif de cinq charges avant anniversaire doit conduire à une règle explicite, pas à un choix financier du worker.
- **Besoins 3–4** : Bancontact → SEPA est documenté ; carte → SEPA systématique, case exacte et ouverture dès acceptation ne sont pas une recette acquise.
- **Besoin 5** : PayPal Payments distingue plan fixe et Vaulting. L'approbation Reference Transactions du compte n'est pas connue ; le plan fixe n'est pas un repli équivalent au calendrier piloté.
- **Besoin 7** : « aucun email Stripe » ne peut pas être garanti avec les notifications liées à l'identifiant créancier Stripe. Les pages d'aide PayPal ont été bloquées : leur contenu n'est pas traité comme vérifié.
- **Besoin 8** : l'ancien Gifting est retiré et la fonction intégrée au cœur dans la documentation actuelle. Ne pas prévoir un achat séparé ; le parcours surprise/coordonnées/reconduction exige encore une adaptation.
- **Besoins 13–15** : avertissement officiel de reconstruction possible via la recherche ; URL PDF non protégées par Memberships ; retry natif avec défaut `on-hold` non équivalent à la grâce Imagine.
- **Besoin 18** : la décision de conservation de l'existant prévaut. Aucun import en ligne ou transfert de compte Stripe n'est entrepris.

## Frontière avec A-01

Les fichiers A-01 ont été lus en lecture seule. Le reçu `e49f54c5e931` décrit des API/shortcodes réels, la conservation de champs fictifs en stockage classique/HPOS et un renouvellement manuel sans paiement. Ni A-00 ni ce reçu n'attestent une recette passerelle, HTTP/cache/REST, quatre fois, cadeau, groupe, coupon, billetterie ou migration de tokens. A-01 ne déclare pas l'import opérateur prêt.

## Relecture attendue

Appliquer `doctrine/grille-relecture.md`, puis consigner les éventuelles corrections selon le circuit projet. Vérifier surtout les conclusions conditionnelles et l'exhaustivité des doutes, pas seulement la présence des citations. Les questions « À arbitrer par Ced » ne sont pas résolues par le dépôt de `PRET`. Un verdict de relecture n'est pas un GO.

**Emplacement utilisé :** `C:/Users/Ced/imagine`, checkout nommé dans le contexte et contenant le brief. Le répertoire de session `C:/- Claude Project -/imagine` ne contient pas ce checkout ; il n'a pas été modifié. Aucun autre lot ni fichier de pilotage n'a été modifié par ce worker.
