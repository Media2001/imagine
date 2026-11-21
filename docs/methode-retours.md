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

## À l'échelle : quatre sites en parallèle

Objectif annoncé par Ced le 21/11 : l'agence partenaire vise deux sites vendus par mois, soit quatre en cours à tout moment (deux qui démarrent, deux en finition). Ce que ça impose à la méthode :

1. **Le système de design devient le contrat entre le design et la production.** Décision de Ced : il sera fourni systématiquement à partir de maintenant, ce qui n'était pas le cas. Pour qu'Hermès l'applique sans interprétation, il faut **un seul format, le même pour tous les sites** : les valeurs sous forme de variables (couleurs, typographie, espacements, grille, rayons) et la liste des composants avec leurs états. Un espacement faux devient alors une valeur hors système, détectable par un contrôle, au lieu d'un défaut à repérer à l'œil.
2. **Un socle de thème commun**, piloté par ces variables, et une bibliothèque de blocs. Un site = un jeu de variables, un choix de blocs, des contenus. On ne reconstruit pas le thème à chaque fois.
3. **Valider des composants, pas des pages.** Avec quatre sites, le temps de validation visuelle de Ced est la ressource rare. Une page catalogue par site, comparée aux maquettes, et Ced ne regarde que les écarts.
4. **Un dépôt par site**, cloné depuis le gabarit, avec sa file, son verrou et son réveil.
5. **Une vue d'ensemble** : une seule page qui dit, pour tous les sites en cours, ce qui attend Ced. Sans elle, il faut ouvrir quatre dépôts.
6. **La charge de la machine** : quatre réveils horaires, les tâches planifiées des autres projets et les relectures tournent sur le même poste. Décaler les réveils et surveiller les quotas.
7. **Une fiche d'entrée type** par site : ce que le commercial doit fournir pour que la production démarre sans aller-retour (contenus, logo, accès, hébergement, nom de domaine, pages attendues).
