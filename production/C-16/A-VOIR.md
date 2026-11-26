# C-16 — À voir, corrections V2

**26 novembre 2026 : prêt à relire techniquement, gates frais verts, sans réserve historique C09.** Ni clôture, ni validation visuelle de Ced, ni GO sur le réel.

## Compte, adresses et parcours

Sur **imagine-test-demo seulement**, compte fictif **E-ABO** (`e-abo`) ou **E-ADMIN** (`e-admin`). Identifiants dans le fichier privé C09, jamais dans les preuves.

- **Imagine → Commande pour un client** : `http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-commandes`
- **Imagine → Échéances → Virements à valider** : `http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-echeances&vue=virements`
- **Imagine → Réglages**, administrateur : `http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-reglages`

1. Rechercher un compte par nom, email ou localité ; ou saisir un nouveau client fictif en `@example.org`, éventuellement **Sans email**. Une adresse déjà connue reprend le compte existant sans réécrire ses coordonnées. Vente directe reste un bouton distinct.
2. Choisir le produit fictif C09 **normal-1**, une adresse fictive et **Virement** ou **Mandat papier**. Exemple : `16 rue Imaginaire`, `1000`, `Localite O'Fictif V2`, `BE`. Les prix sont ceux des fixtures, pas une offre Imagine. Aucun compte ni objet commercial avant confirmation.
3. Confirmer : commande et souscription natives **pending**, sans paiement ni adhésion. Deux confirmations simultanées reprennent le même ID. Une interruption après persistance de `commence` laisse toute reprise fermée ; relire les objets natifs avant une nouvelle saisie.

Le nouveau compte reçoit par défaut prénom, nom et adresses natives billing/shipping à la confirmation : la recherche ultérieure par localité le retrouve, avec ou sans email. **Jamais de réécriture d'un compte préexistant**, même si son email est saisi comme « nouveau ».

**Décision à défaut / question Imagine** : initialiser l'adresse du nouveau compte ? Réglage C10 `imagine_commande_adresse_nouveau=oui|non`, **oui** prudent par défaut ; `non` garde l'adresse sur commande/souscription seulement, et l'UI annonce l'absence de recherche par localité pour ce nouveau compte. Les deux valeurs ont été enregistrées par le vrai formulaire Settings API et relues. Bibliothèque close C10 inchangée.

La souscription par virement apparaît dans C15. **Ne pas cliquer « Paiement reçu » pour cette recette.** Les commandes à l'unité restent hors de cette vue selon C15 ; leur règlement n'est pas reprouvé par C16. Don, pack, offert et groupé restent des emplacements nommés.

Sans email : marqueur unique `imagine_sans_email=1`, adresse technique `@sans-email.imagine.invalid`. Le filtre individuel refuse tout le message pour un destinataire TO/CC/BCC marqué ou `.invalid`, même mélangé à un normal. Coupe-circuit global conservé, aucun email émis, pas de Brevo ni de délivrabilité réelle annoncés prouvés. Décision C06 fermée, sans droit ni adhésion.

## Preuves actuelles

Dans `production/C-16/` :

| Preuve | Résultat |
|---|---|
| `red-concurrence-V2.json` | Défaut reproduit : deux connexions synchronisées avant GET_LOCK, deux commandes et deux souscriptions natives distinctes |
| `http-corrections-V2.json` | 23 contrôles verts : même ID sous concurrence, un seul couple natif, interruption/reprises fermées, adresses et préexistants, vrais GET par nom complet et localité apostrophés, réglage/restauration exacte |
| `http-base-V2.json` | 70 contrôles verts : cinq souscriptions, numéro sans souscription, sécurité, accès fermé et reset ciblé |
| `unit-focused-V2.json` | 15 tests / 38 assertions, dont 8 cas SansEmail avec deux lectures WordPress doublées ; aucun transport d'envoi |
| `unit-root-V2.json` | 113 tests / 579 assertions, hors réseau, conteneur supprimé et absence vérifiée |
| `preparer-image-V2.log`, `rejouer-t01-V2.log` | Préparation réellement exécutée ; T01 **1 077 tests / 34 327 assertions**, zéro échec, erreur ou ignoré |
| `installation-V2.json`, `final-V2.json` | Quatre classes C16 et reset relus après écriture ; contrat courant C16/C17/C18/C19 présent, aucun bootstrap/seed partagé réécrit |
| `c09-final-V2.json`, `final-V2.json` | **382/382**, A-PAPIER **#101**, action **#8793 pending**, état exact conservé avant/après ; aucune replanification ni exécution de file |

Le reset supprime **seulement les objets/comptes/brouillons C16**. Inventaires natifs finaux vides ; sonde temporaire retirée et absence relue. Aucun reset des profils C09 ou de leurs actions. Le formulaire C10 matérialise des défauts absents de C12/C17 : la recette restitue leur absence exacte et relit, en gardant les journaux append-only (`settings-restauration-V2.json`, relevés avant/après dans la preuve HTTP). Aucun changement de code d'un autre lot nécessaire.

## Rejouer depuis la racine

```powershell
python wp/tests/demo/c16-verifier-V2.py --prepare --deploy --canonical
python wp/tests/demo/c16-gates-V2.py --strict-global
```

La première commande déploie seulement C16 sur la démo existante, teste, nettoie et vérifie. La seconde relit sans mutation commerciale : **exit 0**, sans échec C09 imposé. Ne pas exécuter en parallèle d'une autre recette mutante. Comparaison standard en dix lignes et sources officielles : `natif.md`.

Les reçus sans suffixe V2, `final.json`, `c16-etat.py` et l'ancien `c16-gates.py` sont **historiques**, pas les gates actuels. La réserve C09 est levée par la consigne 1 et `production/C-09/papier-restauration-V2.json` ; ne pas réintroduire #8103 comme gate rouge. La dérive ancienne de `c09-seed.php` venait de l'ajout C17, pas de C16. Anciens A-VOIR/PRET conservés sous `*-historique-V1.*`. C20/C21 non traités.

