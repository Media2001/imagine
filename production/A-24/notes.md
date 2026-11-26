# A-24 — notes et checkpoints

## 2026-11-26 17:12 CET — démarrage (limite ferme 20:08 CET)
Brief entier, consigne permanente, doctrine, file 16 h 30, arbitrages passage 16 h et CDC §3.13/§4.3 lus. Travail délégué, sans verrou, PRET ni rapport partagé ; périmètre seulement `wp/outils/bascule/a24/`, `wp/tests/a24/`, `production/A-24/`. Le chemin `production/A24/notes.md` du message est compris comme `production/A-24/notes.md` pour respecter le scope explicite.

Défauts prudents : adresses des seuls abonnements active/pending/on-hold/pending-cancel comme A-20 ; aucune correction, aucun repli de facturation ; comparaison littérale des champs natifs de livraison, espaces et casse compris ; aucun identifiant ni texte libre publié. Pays absents/inconnus sous noms fermés, pays de moins de cinq regroupés. Gardien A-22 chargé par son API `supervise`/`closed_refusal`, sans modification. Paquet unique seulement après dernier vert ; essais RED hors dépôt.

## 2026-11-26 17:39 CET — checkpoint 1

Deux tranches pures TDD RED→GREEN observées (5 puis 12 contrôles). Le parcours natif absent a échoué, puis l’outil complet a passé classique et HPOS. Dernier essai complet encore en scratch : `a24-complete-06`, code 0, sorties contrôlées par gardien A-22 réemployé sans changement. Comptes exacts sur 12 vivants / 2 terminaux exclus ; canaris directs stdout/stderr, arrêt affiché/muet, shutdown stdout/stderr/affichage ; six mutations sans gardien par stockage ; altérations des rapports fermées. Compte SELECT, transaction même avec root, essais de création/troncature/rename/unlink/mkdir, HTTP/mail/cron/Action Scheduler refusés ; empreintes tables/planification/fichiers inchangées. Vrai clone passé dans neutraliser+anonymiser A-01 : pays conservés, autres champs effacés, inconnus correctement propagés.

Qualification standard : WordPress 7.0.9, Woo 11.1.1, WCS 9.4.1, Memberships 1.30.3 (pile du banc, pas prétendue dernière). Documentation officielle consultée. Premier problème de fixture résolu par lecture de WCS : la fabrique exige un compte positif ; l’anomalie sans compte est créée après sa création native. Aucun code tiers modifié. Deux refus d’écrasement du tool write_file ont été respectés ; modifications ciblées ensuite.

Reste : compléter cas limites purs, réception future-PRET et intégrité sources/dépendances, matrice Windows 3.14 UTF-8/cp1252 et paquet unique dernier vert, delta README parent. Pas de PRET enfant.

