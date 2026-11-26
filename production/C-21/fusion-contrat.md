# C21 — Contrat de succession après fusion

Le sceau historique `final.json` et tous les reçus qu'il nomme restent intacts. Ils décrivent l'état historique, pas le nouvel arbre intégré. `final-fusion.json` est leur successeur : il épingle leur empreinte, les nouveaux fichiers du seul lot et les preuves rejouées. Le vérifieur refuse toute modification d'un reçu historique ; il n'écrit rien par défaut.

## Évolution autorisée C22

La fusion C21 §2/§4.6 autorise l'ajout à l'inventaire de la préférence locale de C22. La chaîne porte : empreinte de `Confidentialite.php` au sceau C21 ; empreinte du fichier intégré dans le reçu C22 `installation-final-V2.json` ; clés sémantiques actuelles `SansEmail::META`, `imagine_email_confirme`, `Newsletters::META`. Le passage des littéraux aux constantes conserve exactement ces trois valeurs. Le test natif crée une préférence, exporte sa valeur puis vérifie son retrait ; les POST C16 vérifient le marqueur sans-email. Aucun ancien hash n'est remplacé par le nouveau. Le bootstrap partagé est contrôlé par le bloc C21 et la conservation ordonnée de ses prédécesseurs, pas par l'empreinte d'un fichier partagé qui évolue.

## Instructions de fusion et preuves

| Instruction | Preuve actuelle |
|---|---|
| 1 — opérateur/client distincts | `fusion-http-green.json` : vrais POST C16 nouveau avec email ; ZIP natif de l'opérateur sans aucune valeur du client ; activité propre exactement ; effacement opérateur et relecture de tout le dossier client à l'identique, sauf `qui=0` |
| 2 — `resultat.client`, sans email | mêmes POST C16 sans email ; valeurs exactes du brouillon dans le ZIP HTML/JSON, retrait par AJAX natif ; `fusion-native-final.json` : vrai créateur C16, suppression native du compte avant expiration et transient absent |
| 3 — paiement réel | fixture historique remise au schéma produit par `CommandeRegles::commande` ; ZIP « Mode de règlement : Virement / Mandat papier », ni référence ni jeton |
| 4 — retrait d'un membre | fixture C21 uniquement : vrais comptes, produit privé, plan et adhésions Memberships natifs ; gel stocké, relu par `EnvoiNatif::apercu`, CSV produit par `ListeEnvoiAdmin::preparer` ; seules les lignes du membre sont retirées |
| 5 — effacement du payeur groupe/cadeau | mêmes gels/CSV ; nom, adresse, attribution, lignes et export personnel complets des tiers strictement identiques avant/après ; `user=0` pour le payeur seulement ; nouvelles observations après demandes natives terminées sans recollecte |
| 6 — sceau successeur | `final-fusion.json`, vérifieur en lecture seule, conservation intégrale du sceau et des reçus historiques |
| 7 — refus 409 | `fusion-failures-final.json` : vrai `wp_delete_user`, panne CAS de la seule découverte fictive, branche `Confidentialite::supprimerCompte`, arguments de `wp_die` 409 ; compte et donnée conservés ; succès après retrait de panne |
| constantes et i18n | 7 tests/78 assertions ciblés ; tous les premiers arguments de traduction sont littéraux, groupes affichés en français ; inventaire natif des trois clés |

## Défauts prudents et bornes

- Conserver le service déjà acquis des autres membres et du bénéficiaire du cadeau ; jamais rendre vraie une attribution initialement inconnue. Aucun droit, prix, paiement, calendrier ou bibliothèque close n'est modifié. Les règles C13 restent identiques. Questions d'organisation à confirmer par Imagine, non bloquantes selon la consigne permanente ; pas de nouvelle attribution.
- Conserver le filtre natif large du libellé « payment method », comme proposé par la fusion. Le mode de règlement du brouillon est un champ propre, distinct des références de paiement.
- `user=0` retire le seul rattachement personnel du payeur dans les observations partagées ; les bénéficiaires et leurs adhésions restent inchangés. Pas de nouveau stockage ni durée. La demande native terminée reste la garde anti-recollecte jusqu'à suppression du compte.
- Le calendrier du gel synthétique et son observation historique sont explicitement fictifs C21. Ces liens ne sont jamais ajoutés aux profils C09. Toute la fixture postale est dans une transaction InnoDB protégée contre COMMIT/DDL, avec rollback de toutes les tables comparées exactement. Les fixtures HTTP sont supprimées par identifiants exacts, leurs lignes/articles et métadonnées résiduelles incluses.
- Seuls les jobs natifs `wcs_report_update_cache` sont volatils. Toutes les autres actions et logs, dont 8793/pending/subscription_id=101, restent exacts. Réglages de conservation relus, jamais écrits. Aucun email ni service extérieur ; aucune action Git.

## Commande de contrôle

`python -B wp/tests/demo/c21-verifier.py`

Le contrôle courant délègue au contrat de succession. `python -B wp/tests/demo/c21-fusion-verifier.py` est son point d'entrée explicite. Il relit les sources installées et l'état natif après les dernières écritures, contrôle tous les totaux, le T01 complet et l'absence des fixtures. Pas de nouvelle exécution d'un parcours modifiant le site pendant ce contrôle.
