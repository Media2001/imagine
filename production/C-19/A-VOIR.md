# C-19 — à ouvrir après corrections techniques

**Prêt technique, à relire ; Q-1 et validation visuelle de Ced attendues.** Seul site : `imagine-test-demo`, entièrement fictif. Corrections 1–4 appliquées ; Q-2 traité par le défaut prudent. Questions séparées dans `QUESTIONS.md`. Aucun reset de profil, rôle enregistré changé, paiement, email ou appel métier sortant.

## Parcours

Se connecter avec **e-abo**, puis **Imagine → Tableau de bord** :

`http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-tableau-de-bord`

On doit voir quatre tableaux sobres, chacun suivi de sa phrase de comptage :

| Indicateur | Valeurs lues le 26 novembre 2026 à 05 h 51 CET (04 h 51 UTC) |
|---|---|
| Actifs C18 | 9 lignes d’abonnement : 8 modes non renseignés, 1 mandat papier |
| Échéances C15 | 10 à 30 jours ; 12 à 90 jours ; 12 à 180 jours, fenêtres cumulatives |
| Paiements échoués C15 | 2 commandes liées impayées |
| Entrées / sorties du mois civil UTC | 12 créations natives / 1 fin native effective |

Sept lignes grises « à venir », avec la donnée ou définition manquante : par tarif ; **par moyen de paiement**, explication « Distinction mode/moyen à arrêter à l’atelier. » ; rétention annuelle ; non-renouvellements/motifs ; conversion découverte ; part solidaire/soutien ; personas. Aucun chiffre ni formule ajouté pour ces emplacements. Aucun nom, adresse, identifiant d’abonné, formulaire ou script dans le contenu C19. La barre native WordPress garde l’identité fictive de l’opérateur connecté. Les valeurs courantes peuvent différer des reçus historiques avec le temps : aucune fixture n’a été réinitialisée.

Comparer l’actif à l’aperçu **Imagine → Extractions → état Actif** et les échéances/échecs à **Imagine → Échéances**, mêmes fenêtres. E-redac et a-carte obtiennent **403** ; un POST de e-abo est **405** ; l’anonyme n’obtient aucun chiffre. Un administrateur peut lire l’écran.

Capture corrigée : `corrections-V2/tableau-de-bord-referent.png` (vrai Chromium, clic du menu Imagine, requêtes hors démo bloquées). Quatre tableaux, libellés et sept grisés lisibles dans la capture inspectée ; ce contrôle technique n’est pas la validation de Ced. Les phrases et libellés restent à discuter à l’atelier.

## Ce qui est compté, et ce qui ne l’est pas

- **Actif** réemploie exactement C18/Mon compte : une ligne d’abonnement, pas une personne dédupliquée, ni la décision d’accès ou de liste d’envoi C13. La grâce est un autre état. Une méthode vide reste inconnue ; les deux exceptions fictives A-VIR/A-PAPIER sont celles de C15, sans nouvelle inférence.
- **Un/trois/six mois** réemploie les fenêtres existantes C15 **30/90/180 jours**, explicitement nommées. C18 sélectionne des journées UTC entières, tous états, et peut donc compter autrement : aucune formule concurrente n’a été introduite.
- **Échecs** compte les commandes natives liées au même titulaire, parent/renouvellement, failed, non payées et sans date payée : C15 inchangé.
- **Entrées** reprend le concept standard Woo **New Subscription** : créations natives dans le mois, y compris en attente ou créées par l’administration, et non les seules Signups payées. La création n’est pas remplacée par la date de début du calendrier. **Sorties** : cancelled/expired dont la fin native est déjà atteinte dans le mois (concept Ended), pas une demande d’annulation au terme futur. Mois civil **UTC**, du premier à maintenant inclus. Les dates absentes ne sont pas fabriquées. C18 n’a pas d’extraction création/fin ; l’égalité est contrôlée séparément sur les lignes et dates CRUD natives. Aucun historique de transitions, taux ou motif déduit.

## Q-1 — composition des droits inchangée, décision attendue

`imagine_voir_tableau_bord` est une **méta-capacité WordPress** ; elle exige les capacités sources `imagine_extraire_abonnes` et `imagine_gerer_echeances`, déjà détenues par e-abo. Administrateur admis par `manage_options`. Aucun nouveau rôle, `add_cap`, activation, option ou seed nécessaire. La révocation d’un droit source refuse C19, même pour le référent. Cette composition technique évite de réécrire les profils clos ; ce n’est pas une nouvelle case de permission persistante indépendante.

Ni la file du 26 novembre à 4 h 30 ni les derniers arbitrages de 4 h ne tranchent Q-1. Les tests prouvent le modèle existant, pas l’indépendance d’un droit dédié. **Composition conservée exactement**, sans choisir qui verra quoi sur le réel. Q-2 : défaut (b) appliqué (septième ligne grisée), confirmation de la distinction à l’atelier. Voir `QUESTIONS.md` ; le parent/Claude reporte l’écart §3.13 dans `docs/ecarts.md`, non modifié ici.

## Vérifications exécutées

Reçu courant : **`corrections-V2/final.json`**, lié aux octets relus sur la démo après écriture. Le reçu historique `final-V2.json` et les preuves antérieures sont préservés, non réécrits.

- TDD : RED puis GREEN de l’adaptateur à horloge contrôlée (borne 180 franchie pendant la lecture : 0 au lieu de 1 avant correction), capture unique de l’instant par défaut, cache catalogue, libellés par indicateur ; RED HTTP de Q-2 absent, puis GREEN.
- **Instant unique** transmis à la présélection native C15 et aux trois calculs purs. Seul ajout au raccord C15 : argument optionnel, appels à deux arguments compatibles, `EcheancesRegles` inchangé. Aucun double de la règle C15.
- **Libellés colocalisés** avec calcul/titre/phrase ; rendu admin générique et clé brute comme filet. Catalogue mémoïsé en mémoire pour la requête ; variable morte retirée ; le 30 des échecs sert à la validation, pas à un filtre temporel.
- PHP C19 **10 tests / 79 assertions** ; paquet site complet **124 / 662** ; **2 tests Python** du contrat des ajouts partagés.
- Image préparée après ajout des tests (`corrections-V2/preparer-image.log`, `T01 IMAGE READY`, PHP **8.2.33**), sans modifier le lanceur ; canonique **1088 tests / 34410 assertions**, zéro échec, erreur ou saut. Python exécuté : **3.11.15**, sorties UTF-8 explicites.
- PSR-12 C19 : zéro erreur. Les **8 erreurs antérieures** du fichier partagé `EcheancesNatives.php` sont comparées avant/après, strictement identiques ; aucun reformatage hors périmètre.
- **18 contrôles natifs** : parité C15/C18, même instant injecté ; zéro SQL non SELECT, HTTP/email pendant calcul/rendu ; source WCS refusée sans faux zéro ; droits et absence d’identité.
- **29 contrôles HTTP/Chromium** : vrai menu, nombres, phrases, sept grisés/Q-2, 403/405, HEAD, paramètres sans effet et empreintes protégées avant/après.
- C09 : **382/382** ; **action 8793 pending et abonnement 101 inchangés**, pas de réserve historique remise en attente.
- C18 natif corrigé : **62 contrôles** verts, sans export ni écriture de journal. Sources des derniers reçus C17/C18 contrôlées sur disque et sur la démo, reçus hérités inchangés.
- README partagé : **contrat de section**, pas empreinte bloquante du document entier. Empreinte actuelle observée dans le successeur, aucune substitution manuelle d’une empreinte historique.

### Portée de la lecture seule

**C19 lui-même : zéro écriture SQL, zéro appel sortant, zéro tâche créée.** Les données commerciales, comptes, rôles, échéances/actions/logs du planificateur et options métier restent identiques. L’administration WordPress complète renouvelle toutefois des caches/verrous internes : trois seules options volatiles sont explicitement exclues des comparaisons HTTP (`_transient_timeout_wcs_woocommerce_active_version`, `_transient_timeout_novamira-pro_update_checker`, `action_scheduler_lock_async-request-runner`). Les sessions d’authentification ont l’exclusion C18 préexistante. Le diagnostic initial est conservé ; aucune donnée métier n’a été restaurée pour masquer un écart. On ne prétend pas que le bootstrap WordPress entier ne fait jamais d’écriture.

Une exception remontée par la source ferme les chiffres. Une erreur que WooCommerce absorberait lui-même en liste vide n’est pas une panne détectable universellement par cet adaptateur ; cette limite est explicite, sans modifier les lots clos.

Premier passage long : seule l’expiration native `_site_transient_timeout_wp_theme_files_patterns-55884c82b8cc78f0affc1677838a8dc8` a varié ; données commerciales, rôles et planificateur inchangés. Diagnostic avant/après conservé dans `corrections-V2/bootstrap-diagnostic-{before,after}.json`. **Aucune exclusion élargie, aucune restauration pour masquer l’écart** : second passage borné strictement identique avant/après, canonique réutilisé avec les mêmes empreintes de sources.

## Commandes ciblées pour le parent

Depuis `C:/Users/Ced/imagine` :

```powershell
$env:PYTHONIOENCODING='utf-8'
python wp/tests/demo/c19-corrections.py --readback-only
python wp/tests/demo/c19-corrections.py
```

Le premier relit sources, démo et empreintes natives, sans écriture sur le site. Le deuxième rejoue les tests ciblés/complets du site, natif et HTTP/Chromium, sans reset ni installation ; le résultat canonique n’est accepté qu’avec les mêmes empreintes. Si les sources changent, pour reconstruire seulement ce lot et non le site :

```powershell
python wp/tests/demo/c19-corrections.py --prepare --deploy --canonical
```

Ne pas rejouer le finaliseur historique `c19-verifier.py` : ses hypothèses antérieures restent dans les preuves passées. Ne pas lancer les finaliseurs C17/C18 historiques pour réécrire leurs reçus ; le successeur contrôle leurs dernières sources séparément. Ne pas appeler le constructeur global, `profils.py --reset`, les actions C15 ou les lots C20/C21/B05/C22. Aucun autre site, bibliothèque close ou Git.

## Standard consulté

Documentation officielle, HTTP 200 vérifié le 26 novembre 2026 ; aucune source tierce :

- WordPress `map_meta_cap` : https://developer.wordpress.org/reference/hooks/map_meta_cap/ — composition d’une méta-capacité à partir des primitives existantes.
- Subscriptions, dates natives : https://woocommerce.com/document/subscriptions/develop/functions/ — dates GMT start/next_payment/end et timestamp de fin, pas de calendrier reconstruit.
- Rapports Subscriptions : https://woocommerce.com/document/subscriptions/reports/ — distingue New Subscription, Signups, Cancellations et Ended. Les rapports standard ne remplacent pas l’écran Imagine demandé ni ses filtres C15/C18 ; ils donnent le sens de création/fin repris ici, sans reprendre leur métrique Current Subscriptions qui diffère du filtre Actif existant.

Aucune validation visuelle de Ced, clôture de code par relecteurs, autorisation sur du réel ou mise en ligne n’est déduite de ces preuves.
