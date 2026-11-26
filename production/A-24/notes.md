# État actif — qualification finale 2026-11-26T22:56:39.447669+01:00

Voir `FINALISATION.md` : matrices natives complètes et gates communes réellement vertes sur le gel **2026-11-26T22:56:09.803345+01:00**. Un seul paquet retenu `preuves/final`, vérification sans argument ; anciens paragraphes et chiffres ci-dessous **historiques**, pas une nouvelle attestation. Comparaison Unicode casse/espaces et vraies divergences natives confirmées. Nettoyage PSR-12 par wrapper isolé, découpe de lignes et fermeture locale du helper de tests, sans changement de règle. La recette PHP portable Windows antérieure contrevenait à la consigne : signalée, retirée de COMMANDES.md et jamais répétée ici. PHP pur, lint et natif exclusivement dans Docker jetable.

---

# A-24 — notes et checkpoints

**État courant du réveil correctif du 26 novembre 2026 :** les paragraphes ci-dessous sont historiques. Leur comparaison littérale est remplacée par la comparaison Unicode casse/espaces en mémoire décrite au README. Les comptes de complétude restent bruts. Voir `corrections-reveil.md` : 15 tests Python par encodage et 27 contrôles purs locaux au vert ; nouveau banc natif et reseal réservés au parent, non exécutés par l’enfant. Le paquet natif antérieur est conservé sans le requalifier ; PRET retiré après sauvegarde scratch.

## 2026-11-26 17:12 CET — démarrage (limite ferme 20:08 CET)
Brief entier, consigne permanente, doctrine, file 16 h 30, arbitrages passage 16 h et CDC §3.13/§4.3 lus. Travail délégué, sans verrou, PRET ni rapport partagé ; périmètre seulement `wp/outils/bascule/a24/`, `wp/tests/a24/`, `production/A-24/`. Le chemin `production/A24/notes.md` du message est compris comme `production/A-24/notes.md` pour respecter le scope explicite.

Défauts prudents : adresses des seuls abonnements active/pending/on-hold/pending-cancel comme A-20 ; aucune correction, aucun repli de facturation ; comparaison littérale des champs natifs de livraison, espaces et casse compris ; aucun identifiant ni texte libre publié. Pays absents/inconnus sous noms fermés, pays de moins de cinq regroupés. Gardien A-22 chargé par son API `supervise`/`closed_refusal`, sans modification. Paquet unique seulement après dernier vert ; essais RED hors dépôt.

## 2026-11-26 17:39 CET — checkpoint 1

Deux tranches pures TDD RED→GREEN observées (5 puis 12 contrôles). Le parcours natif absent a échoué, puis l’outil complet a passé classique et HPOS. Dernier essai complet encore en scratch : `a24-complete-06`, code 0, sorties contrôlées par gardien A-22 réemployé sans changement. Comptes exacts sur 12 vivants / 2 terminaux exclus ; canaris directs stdout/stderr, arrêt affiché/muet, shutdown stdout/stderr/affichage ; six mutations sans gardien par stockage ; altérations des rapports fermées. Compte SELECT, transaction même avec root, essais de création/troncature/rename/unlink/mkdir, HTTP/mail/cron/Action Scheduler refusés ; empreintes tables/planification/fichiers inchangées. Vrai clone passé dans neutraliser+anonymiser A-01 : pays conservés, autres champs effacés, inconnus correctement propagés.

Qualification standard : WordPress 7.0.9, Woo 11.1.1, WCS 9.4.1, Memberships 1.30.3 (pile du banc, pas prétendue dernière). Documentation officielle consultée. Premier problème de fixture résolu par lecture de WCS : la fabrique exige un compte positif ; l’anomalie sans compte est créée après sa création native. Aucun code tiers modifié. Deux refus d’écrasement du tool write_file ont été respectés ; modifications ciblées ensuite.

## 2026-11-26 17:54 CET — checkpoint final avant scellement

Matrice finale `a24-final-matrice-01` exécutée normalement jusqu’au code 0 : sources/deps inchangées pendant les deux contextes. Windows effectif **Python 3.14.6**, pas 3.14.7 annoncé ; UTF-8 (mode UTF8=1) et cp1252 (mode UTF8=0), métadonnées mesurées conservées. Par contexte : Python 14, PHP pur 17, lint PHP 9, natif classique+HPOS 206, portes du runner 9 ; tous verts. Six témoins sans gardien par stockage et par contexte. Aucun défaut de l’outil dans le dernier rejeu. Les essais de préparation ont été conservés en scratch, jamais rebaptisés ni déposés comme paquet vert.

Vérificateur et scellement testés en TDD (refus source absente RED puis GREEN) ; contrat des seules deux lignes partagées et inventaire indépendant du futur PRET couverts. `seal.py` est chargé de prouver encore la réception complète sur miroir avec/sans PRET et après trois mutations restaurées avant de publier le paquet unique ; le vert final est son préalable. Rapports et commandes propres au lot rédigés. Le conteneur de développement exact `imagine-a24-addresses-dev-20261126` a été supprimé après contrôle de son étiquette, puis absence sémantique confirmée ; les deux runners finaux sont nettoyés par leur banc.

Aucun blocage restant pour le périmètre enfant. Intégration README, portes globales et PRET réservés au parent ; aucune revendication d’intégration ou de préparation globale. Durée depuis 17:08 : moins d’une heure, très en deçà du plafond 20:08. Les empreintes de livraison figent ces notes ; la réception finale est lisible dans le paquet, sans re-rédiger ces notes après scellement.


