# C-19 — à ouvrir

**Prêt technique, à relire ; validation visuelle de Ced attendue.** Seul site : `imagine-test-demo`, entièrement fictif. Aucun reset de profil, rôle enregistré changé, paiement, email ou appel métier sortant.

## Parcours

Se connecter avec **e-abo**, puis **Imagine → Tableau de bord** :

`http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-tableau-de-bord`

On doit voir quatre tableaux sobres, chacun suivi de sa phrase de comptage :

| Indicateur | Valeurs lues le 26 novembre 2026 |
|---|---|
| Actifs C18 | 9 lignes d’abonnement : 8 modes non renseignés, 1 mandat papier |
| Échéances C15 | 11 à 30 jours ; 13 à 90 jours ; 13 à 180 jours, fenêtres cumulatives |
| Paiements échoués C15 | 2 commandes liées impayées |
| Entrées / sorties du mois civil UTC | 12 créations natives / 1 fin native effective |

Six lignes grises « à venir », avec la donnée ou définition manquante : par tarif ; rétention annuelle ; non-renouvellements/motifs ; conversion découverte ; part solidaire/soutien ; personas. Aucun faux chiffre pour ces emplacements. Aucun nom, adresse, identifiant d’abonné, formulaire ou script dans le contenu C19. La barre native WordPress garde l’identité fictive de l’opérateur connecté.

Comparer l’actif à l’aperçu **Imagine → Extractions → état Actif** et les échéances/échecs à **Imagine → Échéances**, mêmes fenêtres. E-redac et a-carte obtiennent **403** ; un POST de e-abo est **405** ; l’anonyme n’obtient aucun chiffre. Un administrateur peut lire l’écran.

Capture finale : `tableau-de-bord-referent.png` (vrai Chromium, clic du menu Imagine, requêtes hors démo bloquées). Aucun choix graphique autre que les tableaux natifs ; les phrases et libellés restent à discuter à l’atelier.

## Ce qui est compté, et ce qui ne l’est pas

- **Actif** réemploie exactement C18/Mon compte : une ligne d’abonnement, pas une personne dédupliquée, ni la décision d’accès ou de liste d’envoi C13. La grâce est un autre état. Une méthode vide reste inconnue ; les deux exceptions fictives A-VIR/A-PAPIER sont celles de C15, sans nouvelle inférence.
- **Un/trois/six mois** réemploie les fenêtres existantes C15 **30/90/180 jours**, explicitement nommées. C18 sélectionne des journées UTC entières, tous états, et peut donc compter autrement : aucune formule concurrente n’a été introduite.
- **Échecs** compte les commandes natives liées au même titulaire, parent/renouvellement, failed, non payées et sans date payée : C15 inchangé.
- **Entrées** reprend le concept standard Woo **New Subscription** : créations natives dans le mois, y compris en attente ou créées par l’administration, et non les seules Signups payées. La création n’est pas remplacée par la date de début du calendrier. **Sorties** : cancelled/expired dont la fin native est déjà atteinte dans le mois (concept Ended), pas une demande d’annulation au terme futur. Mois civil **UTC**, du premier à maintenant inclus. Les dates absentes ne sont pas fabriquées. C18 n’a pas d’extraction création/fin ; l’égalité est contrôlée séparément sur les lignes et dates CRUD natives. Aucun historique de transitions, taux ou motif déduit.

## Droit dédié sans mutation de C09

`imagine_voir_tableau_bord` est une **méta-capacité WordPress** ; elle exige les capacités sources `imagine_extraire_abonnes` et `imagine_gerer_echeances`, déjà détenues par e-abo. Administrateur admis par `manage_options`. Aucun nouveau rôle, `add_cap`, activation, option ou seed nécessaire. La révocation d’un droit source refuse C19, même pour le référent. Cette composition technique évite de réécrire les profils clos ; ce n’est pas une nouvelle case de permission persistante indépendante.

## Vérifications exécutées

`final-V2.json` lie les empreintes locales aux octets relus sur la démo et aux reçus après les dernières écritures de code :

- TDD : RED/GREEN des quatre indicateurs, puis distinction création native/début de calendrier et refus du droit source révoqué.
- PHP pur C19 **6 tests / 32 assertions** ; paquet site complet **104 / 555** ; deux tests Python du contrat des fichiers partagés.
- Image préparée à nouveau par `preparer-image.ps1`, sans modifier son code ; canonique **1 068 tests / 34 303 assertions**, zéro échec, erreur ou saut. PSR-12 : zéro erreur.
- **18 contrôles natifs** : égalité des comptes avec C15/C18 et les dates natives ; aucune requête SQL non SELECT, aucun HTTP/email pendant calcul/rendu ; source WCS refusée sans faux zéro ; droits et absence d’identité.
- **28 contrôles HTTP/Chromium** : vrai menu, nombres, phrases, grisés, 403/405, HEAD, paramètres sans effet et empreintes protégées avant/après.
- C09 : **382/382**, action A-PAPIER restaurée incluse. Empreinte exacte du reçu `production/C-09/papier-restauration-V2.json`, pas de réserve historique remise en attente.
- Gates successeurs C17/C18 réexercés, reçus neufs **sous C19** : C18 natif 14, ses neuf CSV historiques rouverts, preuves anciennes inchangées. Les ajouts partagés du bootstrap/README sont vérifiés par retrait de la seule section C19, jamais par réécriture des anciens sceaux.

### Portée de la lecture seule

**C19 lui-même : zéro écriture SQL, zéro appel sortant, zéro tâche créée.** Les données commerciales, comptes, rôles, échéances/actions/logs du planificateur et options métier restent identiques. L’administration WordPress complète renouvelle toutefois des caches/verrous internes : trois seules options volatiles sont explicitement exclues des comparaisons HTTP (`_transient_timeout_wcs_woocommerce_active_version`, `_transient_timeout_novamira-pro_update_checker`, `action_scheduler_lock_async-request-runner`). Les sessions d’authentification ont l’exclusion C18 préexistante. Le diagnostic initial est conservé ; aucune donnée métier n’a été restaurée pour masquer un écart. On ne prétend pas que le bootstrap WordPress entier ne fait jamais d’écriture.

Une exception remontée par la source ferme les chiffres. Une erreur que WooCommerce absorberait lui-même en liste vide n’est pas une panne détectable universellement par cet adaptateur ; cette limite est explicite, sans modifier les lots clos.

## Commandes ciblées pour le parent

Depuis `C:/Users/Ced/imagine` :

```powershell
python wp/tests/demo/c19-verifier.py
python wp/tests/demo/c17-verifier.py --readback-only
python wp/tests/demo/c18-verifier.py --readback-only
```

Le premier rejoue C19 sans reset ni déploiement, utilise le résultat canonique lié aux mêmes octets et vérifie C09/les sources prédécesseurs. Les deux autres produisent de nouveaux reçus successeurs dans leurs lots (à lancer par le parent propriétaire). Pour reconstruire seulement ce lot, et non le site :

```powershell
python wp/tests/demo/c19-verifier.py --prepare --deploy --canonical
```

Ne pas appeler le constructeur global, `profils.py --reset`, les actions C15 ou les lots C20/C21.

## Standard consulté

Documentation officielle, HTTP 200 vérifié le 26 novembre 2026 ; aucune source tierce :

- WordPress `map_meta_cap` : https://developer.wordpress.org/reference/hooks/map_meta_cap/ — composition d’une méta-capacité à partir des primitives existantes.
- Subscriptions, dates natives : https://woocommerce.com/document/subscriptions/develop/functions/ — dates GMT start/next_payment/end et timestamp de fin, pas de calendrier reconstruit.
- Rapports Subscriptions : https://woocommerce.com/document/subscriptions/reports/ — distingue New Subscription, Signups, Cancellations et Ended. Les rapports standard ne remplacent pas l’écran Imagine demandé ni ses filtres C15/C18 ; ils donnent le sens de création/fin repris ici, sans reprendre leur métrique Current Subscriptions qui diffère du filtre Actif existant.

Aucune validation visuelle de Ced, clôture de code par relecteurs, autorisation sur du réel ou mise en ligne n’est déduite de ces preuves.
