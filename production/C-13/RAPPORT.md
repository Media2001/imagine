Fait : corrections C13 appliquées au raccord natif : bénéficiaires, renouvellements C01, gel persistant, logique pure et libellés.
Prêt à relire : corrections techniques rejouées par le parent et PRET redéposé, avec réserves d’acceptation C09 ; ni recette complète, ni validation visuelle, ni clôture.
À valider par Ced : coexistence visuelle des menus C10/C13 ; aucune question technique n’attend Ced.
Bloqué : acceptation nominative C09 : 12/12 souscriptions sans paiement validé, 0 destinataire, A-SANSMAIL exclu ; liens offert/groupe C09 absents.
Ensuite : rejeu indépendant du parent ; aucun changement de C09, C14, B02 ou bibliothèque close.

## Corrections et décisions prises à défaut

- `EnvoiRegles.php` : règles pures injectées, blocs délégués à C01, lignes/éligibilité à C07 ; adaptateur natif séparé.
- Cadeaux WCS Gifting : identité/adresse du bénéficiaire, jamais remplacement par le payeur. Groupes Memberships : liens `_subscription_id`, identité/adresse des membres, quantités produits = capacité ; deux places attribuées sur trois donnent deux personnes.
- **Réglage métier administrateur**, deux valeurs testées : `imagine_envoi_groupes=ferme|liens_memberships`, défaut **ferme**. Modèle collectif à confirmer par Imagine ; aucun adaptateur Teams absent revendiqué.
- Renouvellements natifs payés, propriétaire cohérent, sans remboursement : `Moteur::renouveler()`, début initial inchangé. Annuel intervalle 1, sinon début de bloc enregistré requis ; une échéance trimestrielle n’est pas une année. Dernier paiement WCS ≠ paiement initial absent.
- Gel persistant : calendrier/clôture/observations/blocs. Réécritures passées refusées, relecture indépendante du calendrier courant. Historique/calendrier incomplet ou bénéficiaires requis non résolus : fermé. Égalité à la clôture exclue.
- Hooks Subscriptions/Memberships/adresses : observations append-only, rejeux dédupliqués. GET idempotent avant clôture ; coût linéaire non qualifié en volume.

## Résultats réellement exécutés

- `preparer-image.ps1` : **0**, image préparée/vérifiée ; le paquet `imagine-site` est désormais découvert automatiquement sans toucher au runner fermé ni à T01.
- `rejouer.ps1` : **1010 tests, 33978 assertions, 0 échec/erreur/ignoré**, code **0**. Dont `imagine-site` : **46 tests, 230 assertions** (C11 conservé + C13).
- C13 pur autonome : **10 tests, 30 assertions**, code **0**, sans WordPress ni réseau.
- Démonstration PHP/HTTP réelle : **75 contrôles verts**, deux CSV de deux lignes BE/FR ; sources B02/C14/fermées relues conformes et préservées, états C09/rôles/options/contenus inchangés.
- Mode strict : **2**, `recette_complete=false` ; ce code n’est pas un succès d’acceptation. Les témoins fictifs C13 ne remplacent pas les profils C09.
- Objets natifs jetables nettoyés/relus absents. Commande neuve à zéro, statut/date **fictifs** (recopiés par WCS sur sa souscription jetable). Aucun profil actif existant transformé en paiement, aucun `payment_complete()` ni transport réel.

## Limites et écarts proposés à Claude (aucune écriture dans docs/)

1. « Contradiction §3.13/brief résolue par le brief : sans email admis si droits démontrés. A-SANSMAIL exclu pour paiement non validé, pas pour email. »
2. « Raccord cadeau/groupe livré/testé sur liens natifs fictifs ; profils C09 toujours sans liens : limite de données d’acceptation, plus absence du code. »
3. « Actif administratif ≠ expédition. Aucun complément C09 sans preuve native ; fixtures techniques autorisées sans changer leurs états. Modèle collectif configurable, fermé par défaut, à confirmer par Imagine. »

Rouges corrigés : fin WCS `0`, intervalle chaîne `"1"`, recopie du dernier paiement, nonce de réglages distinct de l’export. Commandes : `COMMANDES.md` ; reçus : `resultats.json`, `resultats-purs.json`. Aucun GO réel ni PRET émis.
