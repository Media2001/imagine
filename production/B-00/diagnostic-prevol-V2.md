# B-00 — prévol refusé, voie 2

Contrôle du 23 novembre 2026, entre 12 h 50 et 12 h 53 CET. Aucun site créé ; aucun appel de création lancé.

## Blocage vérifié

Le brief B-00 interdit Novamira sur `imagine-test-demo` (§ règles propres, ligne 27), toute licence activée et toute connexion extérieure (ligne 14). L'usage normal de l'outil ajoute pourtant Novamira même au modèle « WP minimal » :

- `/app/api/orchestrator.py:94` : `_MCP_PLATFORM_ZIPS = ("novamira.zip", "novamira-pro.zip")`.
- `:607-615` : union systématique des extensions du modèle avec cette liste ; installation et activation.
- `:618-623` : appel à l'activation de licence si configurée, puis `provision_mcp(site)`.
- `/app/api/main.py:37-42,150-165` : la création n'accepte que `name`, `template_slug`, `php_version`, `client_name`, `target_domain` ; pas d'option pour désactiver ces opérations.
- `/app/api/templates/templates.json:5-13` : le modèle `sandbox-wp-minimal` a bien une liste premium vide ; cela n'empêche pas l'ajout global ci-dessus.

Ces fichiers ont été lus depuis le montage en lecture seule du conteneur existant `staging-wp-dashboard`. La configuration a été contrôlée uniquement sous forme booléenne : une licence Novamira est configurée ; sa valeur n'a été ni affichée ni copiée.

La décision générale du 22 novembre (`docs/decisions.md:31`) autorise l'usage normal des sites de test avec activation Novamira. Le brief particulier B-00 demande explicitement l'inverse pour ce site : je n'ai ni ignoré cette restriction, ni modifié l'outil, ni écrit directement dans sa base pour contourner son API.

## Résultats réellement retournés

Lecture SQLite de la seule cible, connexion `mode=ro`, `PRAGMA query_only=ON` :

```json
{"scope":"imagine-test-demo","site":null,"db_mode":"read-only/query-only","api_create_fields":["name","template_slug","php_version","client_name","target_domain"],"provision_references":{"platform_zips":true,"novamira_license":true,"mcp":true},"novamira_license_configured":true,"commercial_packages":["woocommerce-memberships.zip","woocommerce-product-addons.zip","woocommerce-subscriptions.zip"]}
```

La présence des ZIP est un inventaire de fichiers, pas une preuve d'activation ni de compatibilité. Aucun ZIP commercial n'a été installé ou exécuté.

Empreintes SHA-256 des sources effectivement montées :

| Fichier | SHA-256 |
|---|---|
| `main.py` | `fae065a3d75eabb98266bbe6a47a4446ff8bb3477df6e2a176e3fc86872b9b32` |
| `orchestrator.py` | `1d73b3d4c4c2825cc4ba68a8aefa2731c401767db8f63916891d70cec49694d1` |
| `models.py` | `44dc74dce43076787910a496091b8b54f19004b26df03678666ada2620584c77` |

## Suite nécessaire

**Question fermée : faut-il lever, pour B-00 seulement, l'interdiction de Novamira et de son activation automatique de licence lors de la création normale du site (oui/non) ?** Cela implique l'exception à l'absence de connexion extérieure pour cette activation. Si non : l'outil doit proposer une voie normale de création sans Novamira, sans activation de licence et sans configuration MCP, fournie par son mainteneur ; le worker ne la modifie pas.

B-00 n'est pas `PRET`. Aucun script de construction incomplet n'est présenté comme livré. Aucun `A-VOIR.md` ni URL de démonstration ne sont inventés. Les tests de construction, d'idempotence et HTTP n'ont pas été exécutés, faute de création conforme. B-01, C-08, C-09 et C-10 restent bloqués par leurs dépendances explicites à B-00/B-01.
