# Portes vers l’extérieur — lecture seule

Comptes seulement ; aucune révocation ni décision.

```json
{
    "schema": "imagine-a21-external-doors-v1",
    "read_only": true,
    "storage": "hpos",
    "as_of_utc": "2026-11-28T02:14:35Z",
    "api_keys": {
        "status": "connu",
        "counts": {
            "total": 0,
            "by_permission": {
                "read": 0,
                "write": 0,
                "read_write": 0,
                "unknown": 0
            },
            "never_used": 0,
            "unused_twelve_months": 0,
            "last_access_unknown": 0
        }
    },
    "webhooks": {
        "status": "connu",
        "counts": {
            "total": 0,
            "by_status": {
                "active": 0,
                "paused": 0,
                "disabled": 0,
                "unknown": 0
            },
            "by_topic": [],
            "active_destination": {
                "same_domain": 0,
                "external_domain": 0,
                "unknown": 0
            }
        }
    },
    "extension_store": {
        "status": "connu",
        "connected": false
    },
    "outbound_attempts": {
        "http": 0,
        "mail": 0,
        "scheduled": 0
    },
    "basis": {
        "keys": "Droits déclarés ; accès local au fuseau WordPress ; jamais et plus de douze mois disjoints.",
        "destinations": "Nom d’hôte exact sans DNS ; casse et point final neutralisés ; seuls les actifs.",
        "topics": "Identifiants standard fermés ; sujets libres et actions personnalisées regroupés sous unknown.",
        "store": "Déclaration locale auth.access_token ; aucune vérification distante."
    },
    "audit_sha256": "947bbf5da0f2d6ebf40d95053568618c5e962b9b66e22c710e47e2ce8301f742"
}
```
