# Cohérence — lecture seule

Comptes uniquement ; aucune valeur ni decision de suppression.

```json
{
    "schema": "imagine-a19-coherence-v1",
    "read_only": true,
    "storage": "hpos",
    "as_of_utc": "2026-11-26T09:58:38Z",
    "counts": {
        "cross": [
            {
                "plan": 24,
                "subscription_status": "active",
                "membership_status": "active",
                "count": 1
            }
        ],
        "subscriptions_without_membership": [
            {
                "status": "active",
                "count": 2
            },
            {
                "status": "on-hold",
                "count": 1
            }
        ],
        "memberships_without_subscription": [
            {
                "plan": 24,
                "status": "active",
                "count": 2
            }
        ],
        "memberships_missing_subscription": [
            {
                "plan": 24,
                "status": "active",
                "count": 1
            }
        ],
        "multiple_active_membership_accounts_by_plan": [
            {
                "plan": 24,
                "count": 1
            }
        ],
        "automatic_without_saved_payment": [
            {
                "gateway": "a19_fixture",
                "count": 1
            }
        ],
        "automatic_payment_reference_unknown": [],
        "manual_by_gateway": [
            {
                "gateway": "bacs",
                "count": 1
            },
            {
                "gateway": "cheque",
                "count": 1
            }
        ],
        "multiple_active_subscription_accounts": 1,
        "multiple_active_membership_accounts": 1,
        "active_past_next_payment": 1,
        "active_without_paid_order": 1,
        "definitions": {
            "cross": "Chaque adhesion explicitement liee compte une fois, par plan et couple detats.",
            "subscriptions_without_membership": "Abonnements sans aucune adhesion portant leur lien, par etat.",
            "memberships_without_subscription": "Adhesions sans lien numerique positif, par plan et etat.",
            "memberships_missing_subscription": "Adhesions au lien positif vers un abonnement absent du magasin.",
            "multiple_active_subscription_accounts": "Comptes non invites portant plusieurs abonnements actifs.",
            "multiple_active_membership_accounts": "Comptes distincts avec plusieurs adhesions actives au meme plan.",
            "multiple_active_membership_accounts_by_plan": "Comptes distincts par plan, pas adhesions en trop.",
            "automatic_without_saved_payment": "Actifs automatiques declares sans passerelle ou reference requise.",
            "automatic_payment_reference_unknown": "Actifs declares automatiques sans adaptateur de reference connu.",
            "active_past_next_payment": "Actifs avec prochain paiement UTC positif strictement avant la reference.",
            "active_without_paid_order": "Actifs sans commande liee avec date payee ou statut natif paye.",
            "manual_by_gateway": "Tous etats non supprimes ; renouvellement manuel declare, par passerelle."
        }
    },
    "payment_reference_basis": "Reference Woo liee ou champs du schema natif de passerelle ; sinon inconnu.",
    "mode_basis": "Drapeau manuel enregistre, pas bascule manuelle effective du staging.",
    "scope": "Magasin natif faisant autorite ; liens explicites ; aucun rapprochement par identite.",
    "audit_sha256": "9690776a09dc6a0b5c71d3a78622f4b118f444c9f854c74b523c7ea7d47f81af"
}
```
