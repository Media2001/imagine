# Méthode — retours d'expérience

Ce projet sert aussi à mettre au point une manière de travailler réutilisable : Claude prépare et arbitre, Hermès produit, Codex et Claude Code relisent, Git fait circuler. Objectif de Ced : qu'Hermès puisse réaliser le prochain site vitrine presque seul.

Ce fichier note ce qu'on apprend au fil de l'eau, pour en tirer un gabarit de projet. Tenu par Claude.

## Ce qui est réutilisable tel quel

| Élément | Fichiers | Remarque |
|---|---|---|
| Règles du dépôt | `README.md` | Source de vérité unique, pas de secret, pas de donnée réelle, rien de réel sans accord |
| Qui valide quoi | `doctrine/doctrine.md` §6 | Le code se clôt sur preuves ; Ced valide le visuel, tranche le métier, autorise le réel |
| File de travail | `A-FAIRE.md`, `ETAT.md`, `JOURNAL.md` | Tenue par Claude, lue par Hermès |
| Consigne permanente | `prompts/consigne-permanente.md` | Travail en continu, délai par lot, proportion, arrêt à file vide, réveil et verrou |
| Relecture croisée | `relecteurs/`, `doctrine/grille-relecture.md`, `scripts/relire.ps1` | Deux relecteurs séparés, fusion, vérification du second tour |
| Synchronisation | `scripts/sync.ps1` | Fusion, verrou, erreur de commit signalée |
| Arbitrages | `docs/arbitrages-*.md` | Une question absente n'est pas tranchée |
| Registre des écarts | `docs/ecarts.md` | Ce qui sort du cahier des charges, daté |

## Ce qui est propre à Imagine

Le staging neutralisé et anonymisé, les lots métier (numéros, connecteur, robots), la recette d'abonnement. Sur un site vitrine, rien de tout cela n'existe.

## Leçons

### Mise en route

- **Vérifier la chaîne complète avant la première nuit.** Deux nuits perdues : Git refusait les commits faute d'identité et le script ne le disait pas ; puis rien ne réveillait Hermès une fois sa file vide. À faire le premier jour : un lot bidon qui traverse tout le circuit, de la file à la vérification, synchro comprise.
- **Identité Git** à régler sur chaque nouveau dépôt de la machine (`user.name`, `user.email`).
- **Un agent arrêté n'attend pas.** Il faut un réveil planifié (`/cron`), et un verrou pour éviter deux sessions en même temps.
- **Délai de synchro** : jusqu'à cinq minutes entre un push de Claude et sa lecture par Hermès.

### Écrire les consignes

- **Une exigence absolue est suivie à la lettre.** « Aucune clé restante dans toute la base » a produit un outil qui vidait le site de sa configuration. Écrire ce qu'on veut obtenir et à quoi ça sert, pas seulement ce qu'on veut éviter.
- **Donner un délai et une règle de proportion à chaque lot.** Sans eux, un lot d'une demi-journée en prend deux.
- **Dire à quoi sert le livrable.** Le staging devait « ressembler à la production pour vérifier que le site continue de fonctionner » : cette phrase manquait dans le premier brief.
- **Préférer les questions fermées.** Les relectures qui se terminent par « oui ou non » se tranchent en une minute ; les autres attendent.

### Relecture

- **Deux relecteurs de modèles différents se complètent.** Sur cinq lots, Codex a été le plus sévère et a trouvé le seul bloquant ; Claude a tranché des désaccords dans les deux sens.
- **Le second tour doit être une vérification, pas une nouvelle relecture** : instruction par instruction, appliquée ou non, régression ou non.
- **Hermès respecte ses zones d'écriture** et renvoie ce qui n'est pas à lui. Prévoir qui reprend ces renvois (ici, Claude pour `docs/`).

### Pilotage

- **Ordonner par ce que Ced peut voir**, pas seulement par ce qui est indépendant. Des fondations invisibles pendant plusieurs jours entament la confiance, même quand elles sont bonnes.
- **Ne demander à Ced que ce que lui seul peut donner** : son œil, une règle métier, un accord sur le réel.
- **Proposer une réponse par défaut à chaque question.** Un « oui à tout » débloque treize points d'un coup.

## Ce qui manque encore pour un site vitrine presque autonome

1. **Un gabarit de dépôt** prêt à cloner, tiré de la première table.
2. **Un banc de validation visuelle** : captures comparées aux maquettes, par composant et par largeur d'écran, pour que Ced ne regarde que les écarts. C'est la pièce centrale d'un projet où presque tout est visuel.
3. **Un jeu de lots types** pour un site vitrine : socle du thème, pages types, formulaire de contact, référencement de base, performance et accessibilité, mentions et consentement.
4. **Une recette type** : la liste de contrôle d'un site vitrine, comme les cas d'acceptance d'Imagine.
5. **Le passage par l'outil de staging**, en cours de mise au point ici.

Le chantier B d'Imagine (le thème) sera le premier vrai essai des points 2 et 3.
