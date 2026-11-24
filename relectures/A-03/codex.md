# Relecture indépendante Codex — A-03

Date : 24 novembre 2026. Périmètre : brief A-03, production/A-03, scripts et tests correspondants dans wp/. Doctrine, décisions et passages pertinents du cahier des charges (§3.1, §4.1, §4.3, chapitre 5 et chapitre 11) lus. Le brief ne cite pas de paragraphes précis. Le rapport de l’autre relecteur n’a pas été consulté.

## 1. Conformité

Les livrables principaux existent : collecte, comparaison, tests fictifs classique/HPOS, mode d’emploi et PRET. La séparation de la sonde de renouvellement, le compte SQL SELECT, les douze mois UTC et les limites des contrôles HTTP sont explicités. Le renouvellement appelle les API natives, vérifie la commande et sa relation, puis prévoit nettoyage et annulation de transaction.

- **C1 — Important — `wp/outils/bascule/a03/Site.php:221` : l’échantillon peut représenter un client sans droits par un administrateur.** Le premier ID de chaque combinaison d’états est retenu sans distinguer les capacités administratives. La preuve livrée le montre : `samples["none:none"] = 1` et `access["1:10"] = true`, le compte 1 étant l’administrateur créé par le banc. Ajouter ensuite un client ordinaire sans adhésion ni abonnement ne l’inclurait pas dans ce profil. Une régression propre aux clients connectés sans droits pourrait donc rester invisible, même avec la sonde anonyme. **Correction proposée :** distinguer les comptes privilégiés et retenir un compte ordinaire pour chaque état lorsqu’il existe ; ajouter une fixture où administrateur et client partagent `none:none`, puis altérer uniquement le droit du client.

- **C2 — Mineur — `production/A-03/notes.md:4` : des archives de preuves sont livrées malgré l’exclusion explicite du brief.** La ligne renvoie à un ensemble de rapports et de reçus ; deux ensembles existent dans `preuve-finale/` et `relecture-parent-a03/`. Le brief demande « Rapport de dix lignes : pas de reçus d’empreintes ni d’archives de preuves ». **Correction proposée :** conserver le compte rendu synthétique demandé et faire produire les sorties détaillées dans un emplacement temporaire extérieur aux livrables du lot.

## 2. Exactitude métier

Déroulés manuels, confrontés au code et aux résultats déjà livrés ; ils ne constituent pas un rejeu indépendant :

1. **Accès réservé — cahier des charges §3.1 et chapitre 5.** Pour le contenu 10, le compte actif 2 est autorisé, le compte expiré 4 et l’anonyme 0 sont refusés. Après expiration provoquée de l’adhésion 13, l’accès `2:10` devient faux ; la comparaison livrée classe ce changement anormal. Ce cas est cohérent avec la conservation des réponses natives demandée par A-03. Le cas sans adhésion est insuffisamment représenté : voir C1.
2. **Conservation de l’historique — §4.3, précisé par le brief.** Avec `as_of_month = 2026-11`, la fenêtre couvre décembre 2025 à novembre 2026. Les commandes de 9,99 €, 20,15 € et 12,30 € sont retenues dans leurs mois et états respectifs : trois commandes, 4 244 centimes. Celle de novembre 2025 est exclue. La conversion en mois UTC inclurait exactement le 1er décembre 2025 à 00:00 UTC et exclurait le 1er décembre 2026 à 00:00 UTC. Le passage d’année est correctement calculé ; les instants frontières ne figurent pas dans les fixtures.
3. **Échéances — chapitre 5, critère « Échéances ».** La collecte conserve les dates de paiement et les actions individuelles. La suppression fictive de l’action 28 apparaît sous `actions.28`, classée anormale. Le test pur prévoit aussi qu’un déplacement du prochain paiement soit anormal.

- **C3 — Important — `wp/outils/bascule/a03/Report.php:11` : le comparateur accepte des rapports incomplets comme preuves valides.** Seule la chaîne `schema` est validée. Deux objets limités à `{"schema":"imagine-a03-v1"}` aboutissent, par lecture du code, à zéro changement et au code de sortie 0. De plus, supprimer entièrement `pages.home` dans un rapport autrement complet produit un changement « a regarder », sans passer par les contrôles de santé des sous-champs. **Correction proposée :** valider les champs obligatoires et leurs types selon le mode, refuser les rapports incomplets avec le code 1, et tester notamment les rapports minimaux, la disparition d’une page et la confusion entre photo et sonde de renouvellement.

- **C4 — Important — `wp/outils/bascule/a03/Site.php:243` : une erreur de lecture SQL peut devenir un inventaire vide.** La lecture des actions ne contrôle pas l’erreur du pilote, alors que les erreurs SQL sont masquées au démarrage. Une table Action Scheduler absente ou une lecture refusée n’est ainsi pas distinguée d’une table sans action en attente ; les boucles analogues sur les adhésions et les utilisateurs présentent le même risque. Un premier relevé peut donc constituer une référence incomplète sans signaler l’échec de collecte. **Correction proposée :** vérifier chaque lecture et interrompre la collecte avec un code technique sans données personnelles en cas d’erreur ; couvrir une table absente ou inaccessible, distinctement du cas vide légitime.

- **C5 — Important — `wp/outils/bascule/a03/Site.php:537` : l’échec d’écriture du rapport n’empêche pas le succès annoncé.** Le résultat de `file_put_contents` n’est pas vérifié ; celui de `chmod` non plus. Une écriture refusée ou interrompue après création du dossier peut laisser un rapport absent ou tronqué, puis retourner 0 et annoncer `A03_OK`. **Correction proposée :** contrôler l’écriture complète et la publication du fichier, retourner une erreur en cas d’échec et ajouter un test d’échec de sortie sans modifier le site.

## 3. Tests

**Exécution indépendante tentée, bloquée avant le démarrage de PHP.** PHP est absent du PATH de l’hôte. Une tentative des tests purs via le moteur PHP de l’image Docker existante, avec réseau désactivé, système de fichiers en lecture seule et sortie vers stdout, a échoué sur `Wsl/Service/E_ACCESSDENIED` (code processus 4294967295). Les adaptations de chemin et de sortie étaient uniquement en mémoire. Aucun test PHP n’a donc pu être exécuté dans cette session ; la suite classique/HPOS et le lint dépendent du même accès indisponible.

Le lanceur standard n’a pas été exécuté tel quel : il crée des fichiers dans `production/A-03`, interdits par la consigne de cette relecture. Aucun fichier de preuve supplémentaire n’a été écrit.

Les résultats **déjà livrés** indiquent quatre tests purs, 45 contrôles d’intégration et sept lints réussis ; le résultat de style annonce zéro erreur et zéro avertissement. Ils couvrent les mutations exigées, les deux stockages, le refus d’un staging non vérifié, certains garde-fous et le retour des lignes SQL à leur état initial après succès ou exception de renouvellement. Ces résultats ne sont pas présentés comme revérifiés ici. Les fixtures ne franchissent pas une page de 100 abonnements ou commandes ; les frontières UTC exactes et les entrées invalides du comparateur restent à couvrir.

## 4. Sécurité et données

Les rapports inspectés excluent noms, emails, adresses, arguments d’actions et corps HTML. Les comptes de test sont fictifs. Le code contrôle le témoin de vérification, les octets du MU de sécurité et plusieurs protections natives ; la sonde d’écriture est explicite. Aucun accès à un site, une base ou un compte n’a été réalisé pour cette relecture.

- **C6 — Important — `wp/tests/a03-non-regression/inside.py:134` : le test dit de confidentialité ne vérifie pas l’étanchéité du paywall.** Il recherche `A03_PRIVATE_CONTENT_CANARY` uniquement dans les JSON exportés, alors que le collecteur n’y écrit jamais les corps HTML. Si le rendu d’une page anonyme laisse sortir le texte réservé tout en conservant son marqueur, son statut 200 et les réponses de l’API Memberships, ces contrôles restent verts. Le chapitre 5 et la doctrine §4 exigent la protection dans les réponses servies. **Correction proposée :** tester directement l’absence du texte réservé dans la réponse anonyme, avec une mutation du rendu prouvant que le test échoue ; couvrir les voies REST, flux, oEmbed et recherche prévues par la doctrine. N’exporter que les résultats de ces vérifications, jamais le texte.

- **C7 — Important — `wp/outils/bascule/a03/Report.php:42` : les clés d’un rapport peuvent ressortir avec des données personnelles.** Le commentaire promet de ne rien divulguer même pour une entrée malformée, mais la validation autorise lettres, points et tirets dans le chemin. Une clé fictive `access.Jean.Dupont` dont la valeur change ressort telle quelle. Exclure les valeurs ne suffit donc pas à garantir l’absence de noms dans la comparaison. **Correction proposée :** valider la structure et les clés autorisées par section, notamment les IDs numériques et les couples d’IDs ; refuser les clés inattendues sans les reproduire. Ajouter un test avec un nom fictif placé dans une clé.

## 5. Doctrine

Le standard est réutilisé pour Memberships, Subscriptions et les commandes compatibles HPOS. Les classes de production déclarent les types stricts et l’espace de noms `Imagine`. Aucune modification d’extension tierce n’a été relevée dans le périmètre examiné. Les limites opérationnelles sont documentées ; aucune règle nouvelle de droits d’accès n’est à inventer pour ce lot de photographie de l’existant.

L’exigence d’étanchéité reste insuffisamment prouvée (C6). Les références officielles de `production/A-03/sources.md` sont présentes, mais les liens n’ont pas été consultés, conformément au périmètre local de cette relecture.

## 6. Études (lots sans code)

Sans objet : lot de code. Les références documentaires ne remplacent pas les tests du comportement réellement collecté.

## Verdict

**À corriger.** Ce verdict n’est pas un GO.

- **Bloquant :** aucun point classé à ce niveau sur les éléments examinés.
- **Important :** C1 (échantillon administratif), C3 (rapports incomplets acceptés), C4 (erreurs SQL silencieuses), C5 (écriture non vérifiée), C6 (étanchéité non testée), C7 (données personnelles dans les clés).
- **Mineur :** C2 (archives de preuves hors livrables demandés).

Le rejeu indépendant reste non réalisé : PHP hôte absent et accès WSL refusé. Il doit être effectué dans un environnement autorisé après correction ; les résultats livrés ne lèvent pas cette limite de vérification.
