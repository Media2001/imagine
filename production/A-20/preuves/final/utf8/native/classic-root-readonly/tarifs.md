# Récurrences enregistrées — lecture seule

Comptes uniquement ; aucune correspondance ni decision de tarif.

```json
{
    "schema": "imagine-a20-recurring-prices-v1",
    "read_only": true,
    "storage": "classic",
    "counts": {
        "live_subscriptions": 8,
        "products": [
            {
                "product": 24,
                "variation": 0,
                "count": 7,
                "states": {
                    "active": 5,
                    "pending": 1,
                    "on-hold": 0,
                    "pending-cancel": 1
                },
                "schedules": [
                    {
                        "interval": 1,
                        "period": "month",
                        "count": 1
                    },
                    {
                        "interval": 1,
                        "period": "year",
                        "count": 6
                    }
                ],
                "non_annual": 1,
                "amounts": [
                    {
                        "currency": "EUR",
                        "amount": "100.00",
                        "count": 5
                    }
                ],
                "other_amounts": 2
            },
            {
                "product": 25,
                "variation": 26,
                "count": 2,
                "states": {
                    "active": 0,
                    "pending": 0,
                    "on-hold": 1,
                    "pending-cancel": 1
                },
                "schedules": [
                    {
                        "interval": 1,
                        "period": "year",
                        "count": 2
                    }
                ],
                "non_annual": 0,
                "amounts": [],
                "other_amounts": 2
            }
        ],
        "countries": [
            {
                "country": "BE",
                "count": 5,
                "with_shipping": 0
            }
        ],
        "other_countries": {
            "count": 2,
            "with_shipping": 2
        },
        "unknown_country": {
            "count": 1,
            "with_shipping": 0
        },
        "multiple_product_lines": 1,
        "without_product_line": 0,
        "with_fee_line": 1,
        "with_shipping_line": 2,
        "foreign_currency": 1,
        "zero_recurring_total": 1,
        "definitions": {
            "live_subscriptions": "Un abonnement natif actif, en attente, suspendu ou en annulation a terme ; pas un compte ni un paiement constate.",
            "products": "Une fois par abonnement et couple produit/variation ; variation 0 sans variation, produit 0 reference absente. Les groupes peuvent se recouper.",
            "states": "Etat natif enregistre ; aucune qualification en anomalie.",
            "schedules": "Intervalle/periode enregistres sur l abonnement, jamais le rythme du catalogue.",
            "non_annual": "Autre que 1 year ou 12 month ; week/day ne sont pas convertis. Pas une duree d engagement.",
            "amounts": "Total recurrent enregistre sur l abonnement : taxes/frais/port/remises inclus selon Woo. Pas un paiement constate ni un prix catalogue. Pour plusieurs produits, total entier dans chaque groupe, sans repartition. Visible par couple devise/montant porte par au moins cinq abonnements du groupe produit.",
            "other_amounts": "Autres montants : somme des effectifs des couples devise/montant portes par moins de cinq abonnements du groupe produit ; aucune valeur.",
            "countries": "Pays de livraison enregistre sur l abonnement, pas le pays de facturation ou du compte. Codes visibles a partir de cinq abonnements, tous produits reunis ; with_shipping compte ceux avec une ligne de port.",
            "other_countries": "Autres pays : effectif des pays a moins de cinq abonnements et nombre avec ligne de port ; aucun code rare.",
            "unknown_country": "Pays absent ou non reconnu par la liste ISO fermee : effectif et nombre avec ligne de port, sans valeur source.",
            "multiple_product_lines": "Au moins deux lignes produit, independamment des quantites et du nombre de produits distincts.",
            "without_product_line": "Aucune ligne produit ; inclus dans les comptes globaux et pays, sans produit invente.",
            "with_fee_line": "Au moins une ligne de frais, meme de montant nul.",
            "with_shipping_line": "Au moins une ligne de port, meme de montant nul ; pas une preuve de livraison.",
            "foreign_currency": "Devise enregistree differente de la devise enregistree du site ; aucune conversion.",
            "zero_recurring_total": "Total recurrent exactement nul, toutes devises confondues."
        }
    },
    "scope": "Magasin natif faisant autorite ; totaux recurrents enregistres, pas prelevements garantis ; aucune correspondance de tarif.",
    "audit_sha256": "5829de966f7dd35d97d7d05ad93cfec901ce21fdcf14a7d2953e755fd1764bae"
}
```
