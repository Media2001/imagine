# Relecture indépendante Codex — C-25

Référence : brief `briefs/C-25-retractation-en-ligne.md`, cahier des charges §3.7 et §3.8, doctrine et grille de relecture. Examen du code, des tests et des livrables C-25, avec lecture des raccords C-10 et C-21. Aucun accès au site ni à une base ; aucun autre fichier modifié. Le rapport de l’autre relecteur n’a pas été lu.

## 1. Conformité

Le périmètre « demande seule » est respecté à la lecture : deux étapes, accusé persistant, contrôle du titulaire et du délai, note privée WooCommerce, journal de demande, liste administrative et raccords de confidentialité. Aucun appel financier, changement d’accès ou envoi explicite dans les classes C-25. Les trois questions métier demandées figurent dans `A-VOIR.md`, avec les comportements par défaut. Le choix de la commande initiale pour un abonnement et le calcul en UTC sont déclarés.

- **R1 — Important — `wp/plugins/imagine-site/RetractationReglages.php:13`.** Les deux réglages sont enregistrés dans C-10, mais leurs modifications ne sont pas journalisées. Le journaliseur existant ne traite que les options retournées par `Imagine\Pilotage\Administration\Reglages::options()`, dont `imagine_retractation_reglages` ne fait pas partie ; aucun raccord C-25 à `added_option`/`updated_option` ne compense cette exclusion. Passer de 14 à 1 jour ou du paiement à une date manuelle modifie donc l’admissibilité des demandes sans ancienne valeur, auteur ni date. Cela rompt l’exigence C-10 « chaque modification est journalisée ». **Correction proposée :** ajouter une journalisation additive après persistance, avec restauration de la valeur précédente si le journal échoue, et tester création, modification et panne du journal par le chemin de sauvegarde natif.

## 2. Exactitude métier

Cas déroulés à la lecture, sans prétendre les avoir exécutés :

- Paiement le 1er janvier 2030 à 10 h UTC, délai de 14 jours : ouvert jusqu’au 15 janvier à 10 h inclus, refus une seconde après. L’entrée et l’envoi direct utilisent la même règle. Un rejeu après enregistrement retourne l’accusé initial, même après expiration.
- Origine manuelle au 25 décembre 2030, délai de 14 jours : fin au 8 janvier 2031 à minuit UTC. Une date manuelle absente ferme le parcours même si une date de paiement existe. Pour un abonnement, la commande initiale est utilisée après contrôle des deux titulaires.

- **R2 — Important — `wp/plugins/imagine-site/Retractation.php:115`.** Le tableau `$record`, contenant un motif déjà déséchappé, est transmis directement à `add_comment_meta`. L’API de métadonnées WordPress déséchappe à nouveau sa valeur. Un motif valide tel que `Document C:\dossier` perd son antislash ; la comparaison stricte de relecture échoue alors et annule toute la demande. Le lecteur obtient un refus malgré un délai, un titulaire et une confirmation valides. **Correction proposée :** adapter la valeur au contrat d’échappement de l’API de métadonnées, en conservant l’original pour la comparaison, puis vérifier sur WordPress un motif avec antislashs jusqu’à sa relecture et son export. Constat statique, non reproduit dans cette session faute de moteur PHP accessible.

## 3. Tests

- **Exécuté avec succès :** `python -B wp/outils/demo/c25-finaliser.py verifier` → `PASS`, 14 sources concordantes et sceau `PRET` vérifié. Les preuves contrôlées annoncent 8 tests / 146 assertions, 11 mutations détectées, 48 contrôles d’intégration et une régression de 1 143 tests / 35 855 assertions, plus 417 contrôles d’outils.
- **Rejeu PHP tenté :** commande Docker locale de `c25.py`, appelée directement avec dépôt en lecture seule, réseau coupé et fichiers temporaires dans le conteneur, pour éviter la création de reçus. Échec avant lancement de PHPUnit : `Wsl/Service/E_ACCESSDENIED`. Aucun `php`, `phpunit` ou `docker` accessible dans le PATH Windows, ni dépendances PHPUnit locales. Les résultats historiques vérifiés ne constituent donc pas un nouveau passage des tests PHP.
- La recette sur site, la préparation d’image et les scripts produisant des fichiers n’ont pas été lancés, conformément au périmètre du relecteur.

Les tests couvrent bornes, origines, abandon, rejeu, titulaire, pannes de stockage, pagination et absence d’effets explicites. Ils ne détectent pas R2 : le bouchon `add_comment_meta` conserve directement la valeur (`RetractationWPStubs.php:90`). Le bouchon de nonce accepte aussi le même jeton pour toutes les actions ; la séparation des étapes repose sur la preuve HTTP livrée. Compléter les tests natifs pour R1 et R2 avant nouvelle relecture.

## 4. Sécurité et données

Contrôles de titulaire présents avant affichage et écriture ; nonce de confirmation lié à la cible et au motif ; échappement HTML et requêtes préparées présents. Les demandes concurrentes sont sérialisées par commande. Export et effacement sont déclarés aux outils natifs ; le journal résiduel est explicitement décrit comme pseudonymisé. Aucun secret ni donnée réelle identifié dans les fichiers examinés. Aucun nouveau chemin de livraison de contenu réservé repéré. La restauration des profils est attestée par les reçus vérifiés, sans contrôle indépendant du site.

## 5. Doctrine

Le stockage réutilise les notes privées WooCommerce ; la règle de délai est isolée en PHP pur. Les textes sont traduisibles et aucun style supplémentaire n’est introduit.

- **R3 — Mineur — `wp/plugins/imagine-site/README.md:370` (fin du fichier).** Le README s’arrête à C-24 et ne décrit ni C-25, ni ses réglages, ni ses tests, contrairement au §5 de la doctrine. **Correction proposée :** ajouter une section C-25 avec fonctionnement, options, commandes de test et distinction entre vérification locale et recette sur site ; un renvoi vers `production/C-25/NOTE.md` peut porter les détails.

## 6. Études (lots sans code)

Sans objet : lot avec code. La note « standard d’abord » fournit dix lignes et trois liens officiels WooCommerce. Ces pages n’ont pas été consultées, l’accès à un site étant interdit au relecteur. Aucune validation juridique du délai ou des dates légales n’est donnée ici.

## Verdict

**À corriger.**

- **Bloquant :** aucun établi.
- **Important :** R1, changements de réglages sans journal ; R2, demande refusée pour un motif contenant des antislashs.
- **Mineur :** R3, documentation C-25 absente du README.

Les corrections proposées sont techniques et ne demandent aucun arbitrage de Ced. Ce verdict n’est pas un GO.
