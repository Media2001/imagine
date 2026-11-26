# Portes vers l’extérieur — lecture seule

Comptes seulement ; aucune révocation ni décision.

```json
{
    "schema": "imagine-a21-external-doors-v1",
    "read_only": true,
    "storage": "hpos",
    "as_of_utc": "2026-11-26T17:28:26Z",
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
    "audit_sha256": "5bd0bad8cdd860d0054c796c0873a54511bcea0802fa01fd274ac383d1033ec0"
}
```
