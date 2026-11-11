# Décisions

Ce qui est tranché par Ced, daté. Ce fichier précise ou corrige le cahier des charges. Tenu par Claude.

## Tranché

| Date | Décision |
|---|---|
| 11/11/2026 | Le cahier des charges v3.1 est la référence du projet. |
| 11/11/2026 | Ced réalise toute la production technique. |
| 11/11/2026 | Le design et le référencement sont fournis : hors du périmètre de Ced. |
| 11/11/2026 | Le dépôt de code est `Media2001/imagine`. |
| 11/11/2026 | On commence par le socle, sans attendre les maquettes. |
| 11/11/2026 | Le développement et les tests se font dans un staging Docker sur le NUC, décrit dans le dépôt. Rien ne s'installe sur la machine. |
| 11/11/2026 | **On repart de la production.** Le site actuel est copié, mis à niveau (Memberships et ce qui en dépend), puis reçoit le nouveau thème et le code sur mesure. Les abonnés en ligne, leurs mots de passe et leurs moyens de paiement ne sont donc pas migrés : ils restent en place. Seuls les abonnés hors ligne (base Access) sont importés. |
| 11/11/2026 | Trois chantiers indépendants : A l'existant, B le thème, C le code sur mesure. |
| 11/11/2026 | Toute transformation de l'existant est un script rejouable : elle sera refaite sur une copie fraîche le jour de la bascule. |
| 11/11/2026 | Architecture de production : Claude (briefs, arbitrages), Hermès (production), Codex et Claude Code (relecture), Git comme file de travail. |

## Ouvert — à trancher par Ced

1. **Frontière du référencement.** Hypothèse de travail : le référenceur spécifie (balisage, redirections), Ced implémente dans le thème et le serveur. À confirmer.
2. **Pilotage.** La gestion de projet, le document d'interface avec Odoo et les deux sessions de formation sont-ils chez Ced ?
3. **Données réelles.** Appliqué par défaut : la copie de production vit sur le NUC hors du dépôt ; Ced lance lui-même l'import, qui la neutralise et l'anonymise (lot A-01) ; les agents ne travaillent que sur la copie anonymisée. À confirmer, et à préciser pour l'export Access : où et par qui est-il traité ?
4. **Environnements.** Hébergeur et préproduction (le staging local Docker est tranché).
5. **Licences.** Subscriptions, Memberships, ACF Pro, Rank Math Pro, Event Tickets Plus : disponibles pour le développement ?
6. **Site actuel.** Sauvegarde complète (export SQL et `wp-content`) à récupérer chez l'hébergeur actuel.
7. **Connecteur.** n8n hébergé à part ou intégré au site (§4.1).
8. **Numéro d'entreprise.** Recherche de la dénomination en ligne (cahier des charges) ou simple contrôle de format (décision d'octobre) ?
9. **Rythme d'Hermès sur ce dépôt.** Mêmes passages que TUM, ou un passage de nuit seulement ?

## Ouvert — chez Imagine (chapitre 7 du cahier des charges)

Prioritaires : grille tarifaire (3), tarif solidaire (4), accès découverte (5). Tant qu'elles sont ouvertes, le tunnel ne peut pas être finalisé.

## Ouvert — chez Step (chapitre 8)

Points 1 à 4 : champs attendus par Odoo, liste d'envoi, email de facture. Ils conditionnent le document d'interface.
