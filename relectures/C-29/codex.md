# Relecture indépendante Codex — C-29

Date : 27 novembre 2026. Références : `relecteurs/AGENTS.md`, doctrine, grille, brief C-29, cahier des charges §3.10, §4.4 et §2.2, décisions du dépôt. Production examinée : code C29, dépendances de lecture, tests, README et réception courante `reception-contrat-V2.json`.

Rapport Claude non consulté. Aucun accès à un site, une base ou un compte. Seul ce rapport est écrit.

## 1. Conformité

Les livrables sont présents. Le calcul pur est séparé de WordPress ; la personnalisation provient directement de `Personnalisation::attributsConnecteur`. Le statut repose sur `active`, conformément au brief et à A-14. Le tarif vient d'une correspondance fermée configurable, sans prix inventé. L'écran réutilise le droit C19 et présente la fiche, son absence et les totaux. Le formulaire de configuration tarifaire est distinct de la consultation.

Les inconnus sont documentés : bénéficiaires, tarif absent ou contradictoire, grille réelle et correspondance des attributs Brevo. Aucun transport, stockage de fiche ou branchement Odoo n'est ajouté. Deux restrictions du calcul empêchent toutefois de respecter complètement le brief : elles sont détaillées ci-dessous.

## 2. Exactitude métier

Déroulés manuels, comparés au code et aux attendus déposés — ces lectures ne sont pas présentées comme de nouvelles exécutions PHP :

| Cas | Chemin du calcul et résultat | Conclusion |
|---|---|---|
| A-CARTE : email recevable, choix lecteur, abonnement `active`, tarif `normal-1`, accord distinct | Fiche `abonne`, coopérateur `non`, tarif `normal-1`, newsletter et attribut personnel présents | Conforme au §3.10 et au brief |
| A-NONRENOUV : mêmes conditions de newsletter, abonnement `pending-cancel` | Aucun abonnement actif retenu : `non_abonne`, tarif `inconnu`, même si l'accès numérique subsiste | Conforme à A-14 ; aucun droit déduit |
| A-SANSMAIL avec choix préparé | Sortie avant tout statut : fiche absente, raison `email_non_recevable` | Conforme |
| A-CARTE après retrait du seul consentement distinct | C24 renvoie `[]`, repris tel quel ; la fiche et la newsletter restent présentes | Conforme au §4.4 |

**C29-01 — important — `wp/plugins/imagine-site/ContactBrevoRegles.php:20` : une désinscription explicite disparaît avec sa newsletter.** Le calcul ne recherche les refus que dans le catalogue courant. Exemple : un compte s'inscrit à sa seule lettre, s'en désinscrit, puis cette lettre est retirée du catalogue. Sa préférence conservée par C22 reste `choix=false, origine=lecteur`, mais le résultat devient `fiche=null, raison=aucun_choix_lecteur` au lieu de la fiche réduite `a_retirer`. Le compteur des retraits diminue sans nouvelle décision du lecteur. Le brief impose pourtant une fiche réduite au compte désinscrit de tout. La restriction documentée aux listes actuelles ne justifie pas l'effacement de ce refus explicite.

Correction proposée : distinguer la sélection des inscriptions encore actives dans le catalogue de la conservation d'une désinscription explicite. Sans inscription actuelle et avec un retrait explicite conservé, maintenir `a_retirer`. Ne pas transformer en désinscription la seule suppression administrative d'une lettre encore choisie. Ajouter le scénario séquentiel inscription → retrait → suppression de la lettre, ainsi que le témoin « suppression sans retrait ».

**C29-02 — important — `wp/plugins/imagine-site/ContactBrevo.php:171` : l'identification des bénéficiaires groupés dépend de leur activité postale.** C29 ne consomme que `relation['beneficiaires']`. Or le lecteur C13 exclut de cette liste une adhésion pour laquelle `is_active()` est faux (`EnvoiRelations.php:71`), tout en conservant son identité dans `relation_native`. Un bénéficiaire de groupe identifié, dont l'adhésion est suspendue et qui conserve son choix newsletter, devient donc `non_abonne` s'il ne possède pas de souscription personnelle. Le brief réserve précisément cette qualification à Imagine et demande `inconnu` pour le bénéficiaire ; il ne la conditionne pas à l'activité de son adhésion. Le lien cadeau, lui, ne subit pas ce filtre.

Correction proposée : dans l'adaptation C29, identifier les bénéficiaires à partir des liens natifs explicites, indépendamment du filtre d'éligibilité postale de C13. Conserver le statut et le tarif `inconnu` pour le bénéficiaire identifié. Ne pas modifier les règles postales de C13. Tester un même lien groupe actif puis suspendu dans des lectures indépendantes, avec état natif relu avant l'assertion.

Les dates de clôture, changements d'année et calendriers ne participent pas directement à ce calcul. Les transitions d'état et de catalogue sont en revanche pertinentes : C29-01 et C29-02 couvrent deux angles morts. Le rejeu ne doit ni écrire ni transmettre ; les preuves déposées contrôlent ces propriétés.

## 3. Tests

Commandes réellement exécutées pendant cette relecture, sans fichier de sortie ni bytecode Python :

| Commande | Résultat |
|---|---|
| `python -B production/C-29/verifier.py` | PASS, code 0 |
| `python -B wp/tests/demo/b11-c29-contract-tests.py C29` | 12 tests réussis, code 0 |
| `python -B wp/tests/demo/c29-proof-tests.py` | 9 tests réussis, code 0 |

Le rejeu direct du PHP pur a aussi été tenté, sans passer par le lanceur qui écrit une preuve :

```text
wsl.exe -d Ubuntu -- docker run --rm --pull never --network none --read-only --mount type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly --entrypoint php imagine-tests-t01:1 /repo/wp/tests/demo/c29-pure.php
```

Échec d'environnement avant PHP : code 1, « Accès refusé », `Wsl/Service/E_ACCESSDENIED`. PHP n'est pas disponible dans le PATH Windows. Les 21 contrôles purs et les trois tests PHPUnit ne sont donc pas annoncés comme rejoués ici.

Le lecteur valide les preuves historiques de 21 contrôles purs, 51 natifs, 73 HTTP et 27 profils, ainsi que trois tests PHPUnit / 47 assertions. Les 1 203 tests / 36 657 assertions du rejeu général sont également historiques. Les anomalies A-31/A-32 signalées par le lecteur sont extérieures au lot. Les recettes natives, HTTP et `--live` n'ont pas été exécutées : elles accèdent à un site, ce qu'interdit le rôle de relecteur.

Les tests couvrent plusieurs états WCS, les tarifs incohérents, l'inscription automatique, les droits et le consentement distinct avec mutation témoin. Les attendus des profils sont explicites. En revanche, le cas `liste_supprimee` de `tests/fixtures/c29-cases.php:22` conserve un choix positif : il ne couvre pas C29-01. La variante groupe de `wp/tests/demo/c29-runtime.php` couvre seulement l'adhésion active : elle ne couvre pas C29-02. La note reconnaît qu'un essai d'expiration a été retiré après un problème de cache ; il ne constitue pas une preuve de ce cas limite.

## 4. Sécurité et données

Aucun défaut supplémentaire établi dans le périmètre inspecté. Les contrôles d'accès sont ceux de C19 ; la consultation refuse les méthodes autres que GET/HEAD et échappe les valeurs affichées. Le réglage distinct utilise les droits et le nonce de la Settings API. Les sources métier ne construisent pas de SQL C29. Aucun contenu d'article réservé n'est exposé par cet écran.

Le code inspecté n'ajoute ni appel réseau ni secret. Les scénarios utilisent des profils fictifs. Les preuves déposées comportent des témoins positifs des interceptions SQL/HTTP/mail et une restauration vérifiée. Cela atteste les expériences archivées, sans remplacer un rejeu natif actuel. Les écritures volatiles de l'amorçage WordPress et les limites historiques de restauration des sessions sont explicitement distinguées dans la note.

## 5. Doctrine

Le complément métier est justifié par rapport aux extensions Brevo ; namespace, typage strict, préfixes WordPress et séparation du calcul sont présents. Les règles ouvertes restent à des valeurs prudentes ; aucun prix ou droit n'est créé.

**C29-03 — mineur — `wp/plugins/imagine-site/ContactBrevo.php:17` : présentation des appels multiligne non conforme à PSR-12.** L'appel commence ses arguments sur la ligne d'ouverture et place plusieurs arguments sur une même ligne malgré son découpage multiligne. La doctrine §5 demande PSR-12. Correction proposée : reformater les appels multiligne du fichier avec un argument par ligne, le premier sur la ligne suivante et la parenthèse fermante sur sa propre ligne ; aucun changement fonctionnel.

## 6. Études (lots sans code)

Non applicable comme lot d'étude. Les cinq lignes « standard d'abord » sont présentes, avec les liens vers les notices publiées par Brevo et des extraits dans `production/C-29/sources-officielles-V2.json`. Ces pages n'ont pas été ouvertes pendant cette relecture. Les extraits archivés étayent la connexion au compte et la synchronisation des clients ; ils ne suffisent pas, seuls, à vérifier toutes les fonctionnalités annexes énumérées : doute documentaire sur ces détails.

## Verdict

**À corriger.**

- **Bloquant** : aucun point établi.
- **Important** : C29-01, maintien du retrait après suppression d'une lettre ; C29-02, identification du bénéficiaire groupé indépendamment de l'activité postale.
- **Mineur** : C29-03, format PSR-12 des appels multiligne.

Les corrections proposées appliquent le brief existant ; aucune question nouvelle n'est adressée à Ced. Le rejeu PHP reste à obtenir dans un environnement autorisé. Ce verdict ne vaut ni GO, ni validation visuelle, ni autorisation de branchement Brevo.
