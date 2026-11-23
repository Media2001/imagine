# B-00 — précontrôle bloqué, voie 2

1. Aucun site créé : `imagine-test-demo` est absent du registre de l'outil au précontrôle du 23 novembre 2026.
2. L'usage normal de l'outil installe Novamira et Novamira Pro, même avec le modèle `sandbox-wp-minimal`.
3. Il active ensuite la licence configurée et provisionne le MCP ; la requête de création n'offre aucun paramètre de désactivation.
4. B-00 interdit Novamira et toute activation de licence ; l'agent ne modifie donc ni l'outil ni ses modèles et ne lance pas la création.
5. Preuve : `production/B-00/preflight-V2.json` ; script de reconstruction, adresses HTTP et `PRET` non livrés tant que ce préalable n'est pas résolu.
