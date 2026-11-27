# Conservation — lecture seule

Comptes uniquement ; aucune valeur ni decision de suppression.

```json
{
    "schema": "imagine-a18-retention-v1",
    "read_only": true,
    "storage": "classic",
    "database": {
        "status": "observe",
        "groups": []
    },
    "payment_tokens": [],
    "media": [
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
    "count_basis": "Valeurs physiquement conservees dans les deux magasins presents, actif ou inactif ; une ligne compte au plus une fois par forme, separee par portee, magasin et cle. storage indique seulement le magasin actif ; store=commun pour comptes et options.",
    "server_rules": "Presence observee par nom technique ferme ; lecture effectivement interdite inconnue sans ouvrir les fichiers ni lire la configuration serveur.",
    "token_basis": "References par passerelle et type ; jamais des numeros de carte ou IBAN.",
    "audit_sha256": "b0febe082fd145d45dbf535800a2edacfecc06319be8d8df65adac4158c9d420"
}
```
