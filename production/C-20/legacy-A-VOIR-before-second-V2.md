# C-20 — blocage natif démontré, pas de PRET

## À ouvrir

Sur le seul site fictif `http://192.168.129.32:8085` :

- `/my-account/` avec A-CARTE : le tableau de bord B-02 reste celui livré, sans nouvelle action C-20.
- `/my-account/view-subscription/89/` : abonnement A-CARTE, revenu `active` après l’essai ; prochaine date `2026-12-25 18:01:50` UTC.
- `/my-account/view-subscription/92/` avec A-SEPA4 : abonnement actif ; B-02 lit deux paiements fictifs réglés et deux positions à venir. Aucun prélèvement réel.
- `/wp-admin/admin.php?page=imagine-liste-envoi` avec le référent : écran C-13 existant, inchangé. Ne pas confirmer d’action native pour « essayer » C-20.

## Ce que la preuve établit

`native-acceptance-red-V2.json` contient deux transitions **natives réelles**, écrites puis relues sur le site dans une transaction InnoDB annulée intégralement : `active` → `pending-cancel`, puis examen de la possibilité native de reprise. Il ne s’agit ni d’un mock ni d’une recette HTTP achevée.

Dans les deux cas, Memberships passe de `active` à `pending` ; la décision C-06 passe immédiatement de `abonnement_actif` à `virement_non_valide`. Pour le prochain numéro papier `DEMO-2027-T1`, C-13 ne conserve pas la même liste. A-SEPA4 perd également `next_payment`, alors que B-02 affiche toujours les positions 3 et 4 « À venir ». La reprise native est refusée dans ces profils (`can_be_updated_to('active') === false`).

Le brief ordonne l’arrêt si l’accès se ferme ou si les échéances du bloc sont supprimées. Aucun filtre de droits, aucune réécriture de calendrier et aucun ordonnanceur parallèle n’ont été ajoutés. **Ni le thème ni le plugin métier ne sont modifiés.**

## État rendu et limites

- `verification-V2.json` : vérification ciblée du blocage, **pas** validation fonctionnelle de C-20. Les assertions de réception restent rouges : 3 sur 10 satisfaites, 7 échouées.
- `fresh-readback-V2.json` : les quatre profils A-CARTE/A-SEPA4/A-VIR/A-PAPIER et leurs actions natives actives sont exactement ceux de `before-V2.json`.
- `c09-native-final-V2.json` : 382 contrôles, aucun échec ; action A-PAPIER **8793**, abonnement **101**, toujours `pending`, date `2026-11-26 02:13:28` UTC.
- Les 55 tables sont identiques immédiatement après chaque rollback. Après arrêt de PHP, la base globale n’est **pas** identique : tâches natives `wcs_report_update_cache`, journaux, options et sessions Woo ont évolué (`shutdown-diagnostic-V2.json`). Ne pas annoncer une restauration intégrale de toute la base. Aucun changement de profil ni d’action de paiement n’est constaté au readback frais.
- Tous les profils C-09 sont volontairement manuels, moyen de paiement vide, y compris A-CARTE : aucune recette de carte automatique réelle n’est revendiquée. Ne pas fabriquer de passerelle pour la rendre possible.
- Le compteur postal B-02 reste `restants = null` (non raccordé). Aucun historique d’envoi ni compteur n’a été inventé.
- Pas de nouvelle interface, donc les confirmations HTTP, l’action inter-abonnés et les libellés manuels C-20 ne sont pas livrés/testés. A-VIR et A-PAPIER sont seulement relus, non mutés.
- Point d’accroche réservé pour un futur branchement : `imagine_non_renouvellement_confirme`, **non enregistré** puisque la transition sûre n’est pas livrée. Aucun email, service, remboursement ou rétractation.

## Commandes parent, depuis `C:/Users/Ced/imagine`

```sh
python wp/outils/demo/c20.py --verify
```

Relit les profils dans un nouveau processus WP, C-09 et les empreintes de la sonde. Retour attendu : 0 pour les preuves et la restauration ciblée ; ne signifie jamais « C-20 fonctionnel ».

```sh
python wp/outils/demo/c20.py --probe
```

Rejoue les écritures natives transactionnelles puis rollback sur `imagine-test-demo` seulement ; **retour attendu 2**, réception rouge et blocage explicite. Génère aussi des effets de cache/session à l’arrêt de PHP. À n’utiliser que si le parent veut réellement refaire le contre-exemple.

Aucun paquet PHPUnit ajouté, aucune image reconstruite, aucune suite globale revendiquée ; C-21 non traité. La file et les corrections ont été relues avant remise ; pas de correction C-20.
