# Portes vers l’extérieur — lecture seule

Comptes seulement ; aucune révocation ni décision.

```json
{
    "schema": "imagine-a21-external-doors-v1",
    "read_only": true,
    "storage": "classic",
    "as_of_utc": "2026-11-26T23:59:41Z",
    "api_keys": {
        "status": "connu",
        "counts": {
            "total": 2,
            "by_permission": {
                "read": 1,
                "write": 0,
                "read_write": 1,
                "unknown": 0
            },
            "never_used": 1,
            "unused_twelve_months": 1,
            "last_access_unknown": 0
        }
    },
    "webhooks": {
        "status": "connu",
        "counts": {
            "total": 4,
            "by_status": {
                "active": 2,
                "paused": 1,
                "disabled": 1,
                "unknown": 0
            },
            "by_topic": {
                "order.created": 1,
                "order.updated": 1,
                "product.updated": 1,
                "unknown": 1
            },
            "active_destination": {
                "same_domain": 1,
                "external_domain": 1,
                "unknown": 0
            }
        }
    },
    "extension_store": {
        "status": "connu",
        "connected": true
    },
    "outbound_attempts": {
        "http": 1,
        "mail": 1,
        "scheduled": 5
    },
    "basis": {
        "keys": "Droits déclarés ; accès local au fuseau WordPress ; jamais et plus de douze mois disjoints.",
        "destinations": "Nom d’hôte exact sans DNS ; casse et point final neutralisés ; seuls les actifs.",
        "topics": "Identifiants standard fermés ; sujets libres et actions personnalisées regroupés sous unknown.",
        "store": "Déclaration locale auth.access_token ; aucune vérification distante."
    },
    "audit_sha256": "a0417fd9ffe759e14be74f88852aa0d2f8ab6a6117de475346d8a13c4d7d68f9"
}
```
