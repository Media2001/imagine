# Conservation — lecture seule

Comptes uniquement ; aucune valeur ni decision de suppression.

```json
{
    "schema": "imagine-a18-retention-v1",
    "read_only": true,
    "storage": "hpos",
    "database": {
        "status": "inconnu apr\u00e8s neutralisation",
        "groups": null
    },
    "payment_tokens": [
        {
            "gateway": "a18_fixture",
            "type": "CC",
            "count": 1
        }
    ],
    "media": [
        {
            "folder": "autre",
            "directories": 2,
            "files": {
                "txt": 1
            },
            "bytes": 4,
            "server_rule_file_present": false,
            "reading_denied": null
        },
        {
            "folder": "exports",
            "directories": 1,
            "files": {
                "csv": 2,
                "log": 1
            },
            "bytes": 12,
            "server_rule_file_present": false,
            "reading_denied": null
        },
        {
            "folder": "woocommerce_uploads",
            "directories": 1,
            "files": {
                "html": 1,
                "regles": 1
            },
            "bytes": 13,
            "server_rule_file_present": true,
            "reading_denied": null
        }
    ],
    "count_basis": "Une valeur stockee compte au plus une fois par forme ; une cle est separee par portee.",
    "server_rules": "Presence observee par nom technique ferme ; lecture effectivement interdite inconnue sans ouvrir les fichiers ni lire la configuration serveur.",
    "token_basis": "References par passerelle et type ; jamais des numeros de carte ou IBAN.",
    "audit_sha256": "fc41fe28952ccf6ef1639b57e33bc7c8a490954245b3abdfeb973c9239a043ab"
}
```
