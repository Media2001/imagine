# Relecture indépendante Codex — C-09

Date : 23 novembre 2026. Périmètre : brief C-09, profils de recette, production C-09 et sources concernées dans `wp/`. Doctrine et décisions lues ; rapprochement avec les §3.4, §3.5, §3.6, §3.8, §3.9 et §3.13 du cahier des charges. Le brief ne cite pas lui-même de paragraphe numéroté.

Le rapport Claude n’a pas été consulté. Aucun site, compte, secret hors dépôt ou base de données n’a été ouvert. Seul ce rapport est écrit.

## 1. Conformité

Les livrables existent : script Python, catalogue de 30 profils, tableau nominatif, décisions d’accès et `PRET`. Les trois scénarios sans compte sont correctement distingués des 27 comptes. Les identifiants sont prévisibles ; les mots de passe sont générés et destinés au fichier privé B-00. Les objets commerciaux passent par les API natives. La cible est même plus restrictive que le préfixe demandé : seul `imagine-test-demo`, à son adresse fixe, est accepté.

Les limites des profils offert, groupé, solidaire et coopérateur sont explicitement signalées, conformément à la possibilité de livraison partielle du brief. Une limite déclarée ne prouve toutefois pas que toutes les fonctions déjà réalisables ont été livrées.

- **C09-01 — important — `wp/outils/demo/c09-profils.json:30` : E-REDAC est présenté comme entièrement créé alors que la gestion du calendrier n’est pas disponible.** Le rôle `editor` permet d’éditer les contenus et les numéros, mais le calendrier B-00 est une option `imagine_demo_calendrier`, simplement affichée par un shortcode. Les sources examinées ne fournissent pas d’écran permettant à ce rôle de modifier ses dates de sortie et de clôture, comme le demande le §3.5. Le contrôle `contenus_calendrier` de la recette vérifie seulement `edit_posts`, la capacité du type numéro et l’absence de `manage_options`. **Correction proposée :** classer ce profil comme partiel et nommer ce raccord manquant, ou fournir le parcours d’édition attendu ; tester la modification effective d’une date sous ce rôle avant d’annoncer « créé ». Régénérer les décomptes et le tableau en conséquence.

- **C09-02 — important — `wp/outils/demo/c09-seed.php:57` : la grille tarifaire fictive demandée est remplacée par un seul produit à zéro.** Le script crée un unique produit Subscription, annuel, sans déclinaisons des trois tarifs et des deux modes de paiement. Or la section « Données communes » de `docs/recette/profils.md` demande expressément cette grille fictive en attendant les montants d’Imagine. L’absence de grille réelle n’empêche donc pas de préparer des variantes de démonstration ; les scénarios A-CARTE et A-SEPA4 restent indifférenciés sur cette dimension native. **Correction proposée :** créer les six combinaisons natives de test avec des valeurs explicitement fictives et sans passerelle active, puis rattacher les profils concernés. Distinguer cette préparation du tarif du futur raccord de l’échéancier ou du justificatif solidaire.

- **C09-03 — mineur — `production/C-09/A-VOIR.md:65` : le calendrier sur trois ans est annoncé incomplet à tort.** `readback.json`, dans `after.snapshot_b00.calendar`, contient déjà 15 parutions : quatre trimestriels et un hors-série pour chacune des années 2026, 2027 et 2028, avec sortie et clôture. Ce sont les objets éditoriaux qui ne couvrent que cinq numéros de 2026. **Correction proposée :** distinguer calendrier disponible, numéros matérialisés et raccords métier absents ; corriger aussi le texte générateur pour que le prochain rejeu conserve cette distinction.

## 2. Exactitude métier

Déroulement manuel, à partir du code et des preuves déposées, sans nouvelle interrogation du site :

| Cas | Résultat attendu | Comparaison |
|---|---|---|
| A-GRACE, §3.8 | Pendant la grâce, accès maintenu avec régularisation | À la date de la preuve, souscription `on-hold`, adhésion `paused`, fenêtre du 22 au 25 novembre 2026 : `delai_grace`, lecture complète, bloc `regularisation`. Cohérent pour cette fixture ; le rejet bancaire reste explicitement non simulé. |
| A-SUSP, §3.8 | Après la grâce, accès suspendu | Fin de grâce antérieure à l’instant de lecture : `suspendu`, lecture fermée. La sortie de liste postale n’est pas démontrée, ce que le tableau reconnaît. |
| A-NONRENOUV, §3.4 | Droit maintenu jusqu’au terme, sans nouvelle échéance | `pending-cancel`, adhésion active, fin au 23 décembre 2026, prochain paiement nul : `abonnement_actif`. Le numéro restant n’est pas raccordé et reste déclaré partiel. |
| A-VIR, §3.6 | Accès fermé avant validation | Commande `on-hold`, souscription et adhésion `pending` : fermé. Le motif `suspendu` vient du raccord C08 ; son écart avec `virement_non_valide` est correctement signalé. |

- **C09-04 — important — `wp/outils/demo/c09-seed.php:213` : le rejeu ne restaure pas le plan d’une adhésion existante.** Le `plan_id` est fourni uniquement lors de la création. Si une adhésion C09 conservant sa marque de propriété est déplacée vers un autre plan pendant la recette, le prévol l’accepte et le script rétablit commande, produit, dates et statut, mais jamais son plan. La recette native échoue ensuite sur `plan_adhesion` ; les droits peuvent rester différents. Cela contredit la remise à l’état de départ exigée par le brief. **Correction proposée :** rétablir explicitement l’association au plan attendu par l’API native, sans modifier les objets étrangers. Ajouter au test de reset une altération du plan d’une adhésion C09 et vérifier sa restauration ainsi que la décision d’accès.

- **C09-05 — mineur — `wp/outils/demo/c09-seed.php:194` : A-PAPIER échoue à la frontière de fin de mois.** À `2026-12-31 23:59:59 UTC`, le minimum entre « maintenant + une heure » et la dernière seconde du mois vaut maintenant. La recette exige pourtant `next_payment > time()` ; elle ne peut donc pas réussir, même si la persistance native accepte cette date. Une exécution commencée quelques secondes plus tôt peut également franchir la limite avant la vérification. **Correction proposée :** rendre l’horloge injectable, définir un état cohérent d’échéance à lancer en fin de mois et aligner sa vérification sur cet état. Tester la dernière seconde du mois et le passage à l’année suivante, sans déplacer silencieusement l’échéance dans le mois suivant.

## 3. Tests

Commande exécutée localement, avec désactivation de l’écriture des caches Python :

```text
python -B -m unittest discover -s wp/tests/demo -p test_c09_profils.py -v
```

**Résultat : 7 tests, 0 échec, 0 erreur ; code de sortie 0.** Ces tests couvrent notamment les cibles refusées avant transport, la fusion des identifiants, les redirections interdites et le catalogue.

Les neuf SHA-256 des sources listées dans `verification-finale.json` correspondent aux fichiers présents. La production annonce 610 contrôles réussis, dont 364 natifs et 192 HTTP. Ce sont des preuves fournies, pas 610 tests relancés par ce relecteur. Le vérificateur complet accède au site, modifie les comptes et réécrit les livrables : il n’a pas été exécuté, conformément aux restrictions de `relecteurs/AGENTS.md` et à l’interdiction de modifier d’autres fichiers.

Les tests de reset déposés altèrent rôles, emails, mots de passe, statuts et périodicité, puis ajoutent des doublons marqués. Ils ne changent pas le plan d’adhésion (C09-04). La preuve d’E-REDAC ne teste pas le parcours annoncé (C09-01). Les tests natifs déduisent largement leurs attentes du même catalogue que la production : ils attestent sa réalisation technique, sans établir à eux seuls sa conformité aux profils demandés. Aucun cas C09 à horloge fixée ne couvre la fin de mois, la frontière exacte de grâce ou la clôture d’une liste d’envoi.

## 4. Sécurité et données

Les données examinées sont fictives et utilisent `@example.org`. Aucun secret en clair n’a été repéré dans les fichiers examinés ; le scan fourni annonce également zéro correspondance. Les contrôles de cible, de propriété et la révocation des sessions sont présents. Les écritures commerciales utilisent les objets natifs, sans SQL de mutation ajouté par C09.

- **C09-06 — important — `wp/outils/demo/c09-seed.php:13` : la garde hors ligne peut produire l’effet qu’elle doit interdire.** Après le seul contrôle de présence du fichier MU-plugin, elle appelle réellement `wp_mail`, puis `wp_remote_get`. Si le fichier existe mais que ses filtres ne sont plus actifs, le courriel peut partir avant le refus ; si le mail retourne `false` pour une autre raison, la requête réseau est tentée. Une erreur réseau quelconque suffit ensuite à faire passer le contrôle HTTP. Le test de sécurité remplace `pre_wp_mail` par un retour `true`, qui court-circuite précisément l’envoi et ne couvre pas ce défaut. **Correction proposée :** vérifier le chargement effectif et les interceptions attendues sans autoriser de transport réel ; exiger le refus propre à la garde, et tester des filtres absents ou inopérants avec des transports sentinelles qui doivent rester non appelés.

Pour le paywall, les preuves C09 portent sur l’article HTML réservé et ses blocs. Elles ne constituent pas une nouvelle validation de toutes les voies REST, RSS, oEmbed ou PDF du §3.9. Aucun contournement supplémentaire du paywall n’a été identifié dans le code C09 examiné.

## 5. Doctrine

Le standard est globalement utilisé : WordPress pour les comptes, CRUD WooCommerce, Subscriptions pour les dates et statuts, Memberships pour les adhésions. Les fichiers PHP C09 déclarent le typage strict et un espace de noms `Imagine`. Les métadonnées de propriété sont distinctes des droits ; les dates de grâce utilisent le raccord C08 existant. Aucune modification d’extension tierce n’apparaît dans ces sources.

Les références officielles et extraits locaux sont fournis. Les renvois aux paragraphes métier restent moins explicites que les références aux API : il serait utile de les associer aux états et aux limites du catalogue. Le respect de l’exigence de rejeu reste à corriger en C09-04 ; la fermeture des sorties en C09-06.

## 6. Études (lots sans code)

Sans objet : ce lot contient du code. Les références et extraits déposés ont été lus localement ; aucune documentation distante n’a été ouverte, conformément au rôle de relecteur.

## Verdict

**À corriger.** Ce verdict n’est pas un GO.

- **Bloquant :** aucun point classé à ce niveau.
- **Important :** C09-01 — calendrier d’E-REDAC non démontré ; C09-02 — grille tarifaire fictive absente ; C09-04 — plan d’adhésion non restauré ; C09-06 — garde hors ligne susceptible d’effectuer un transport.
- **Mineur :** C09-03 — description erronée du calendrier disponible ; C09-05 — frontière de fin de mois d’A-PAPIER.
