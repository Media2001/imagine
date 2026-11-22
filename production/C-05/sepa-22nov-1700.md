Fait : C-05, ajout de la file du 22/11 à 17 h appliqué en TDD ; premier SEPA derrière un réglage, marge appliquée par défaut.
Prêt à relire : C-05 ; PRET redéposé uniquement après vérification finale des sources, reçus et nettoyage.
À valider ou à arbitrer par Ced : aucune question bloquante ; ni nouvelle durée, ni choix financier ajouté. Validation du réel et branchement restent hors lot.
Bloqué : rien pour cette bibliothèque/prototype ; aucun écran branché sur un site, sauvegarde HTTP ou débit bancaire revendiqué.
Ensuite : remise au parent et aux relecteurs ; aucun autre lot repris, verrou global non touché.

# C-05 — marge de confirmation du premier SEPA

Lectures intégrales : A-FAIRE (file dite 17 h), consigne permanente, doctrine du 22/11, brief C05 et arbitrages (61 lignes, dont défaut marge appliquée). Code, notes, PRET, corrections et preuves de la remise précédente lus ; elle n’était **pas conforme** à l’ajout : Q1 y restait ouverte, sans réglage SEPA. La consigne C05 déléguée n’a pas rouvert A01, C06, C07 ni les lots en attente.

## Réglage et effets retenus

Option existante `imagine_c05_reglages`, nouvelle clé `confirmation_premier_sepa` : `avec_marge` par défaut / `sans_marge`. Deux positions de la sélection d’administration, Settings API réelle, capacité et nonce inchangés, pas de REST. Ancienne clé absente : `avec_marge` ; valeur invalide ou corrompue : refus, conservation intégrale de l’option précédente à la sauvegarde. Aucune migration destructive.

**J’ai compris le délai comme un seuil après la commande, pas comme une nouvelle date de prélèvement :** `Reglages::premierSepaPayeLe(commande, confirmationEffectiveOuNull)` retourne `max(confirmation effective, commande + marge_jours civils Europe/Brussels)` avec marge, la confirmation seule sans marge. Pas de confirmation : null, jamais payé par le temps seul. Confirmation antérieure à la commande : refus. La durée reste le réglage obligatoire existant, sans valeur numérique par défaut. Aucun débit, report de numéro, ajout d’échéance, remise, modification des droits numériques ou de la liste d’envoi.

Cas fictif : commande **09/04/2027 12 h**, confirmation **13 h**, durée de démonstration 7 jours. Avec marge : payé au plus tôt **16/04 12 h**, donc pas avant clôture du premier numéro le **10/04** ; sans marge : **09/04 13 h**. Confirmation plus tardive : sa vraie date dans les deux positions. Paiement exactement à la clôture : pas payé *avant* clôture. Le numéro initial C01 et le versement initial à la commande restent identiques ; aucune règle de remplacement inventée. L’appelant futur teste date non nulle et atteinte ; cette méthode est réservée au premier SEPA, pas aux renouvellements ou autres moyens.

## Résultats réels

Paquet final : `production/C-05/replays/sepa-22nov-1715-final/`.

- **`composer test` : 765 tests, 33 143 assertions ; 0 échec, 0 erreur, 0 ignoré.** Dont Echeancier **403 / 2 373**, nouveaux cas SEPA **19 / 66**. Six suites découvertes dans le JUnit standard ; pas de modification du XML ni de Composer. Les autres suites restent 42/121, 101/298, 41/19 561, 63/10 388 et 115/402.
- **Lint PSR-12 global, syntaxe de tous les PHP et `composer validate --strict --no-check-publish` : exit 0**, comme les tests. PHP 8.2.36 uniquement dans les runners jetables ; aucun PHP hôte.
- **Vrai Subscriptions 9.4.1 / Woo 11.1.1 / WP 7.0.9**, classique + HPOS : **8 abonnements, 64 commandes dont 56 renouvellements** ; **766 contrôles de scénario/administration dont 62 SEPA**, plus **12 d’enveloppe**, tout vert. Deux valeurs persistées/relues et rendues sélectionnées ; effet sur les dates, absence/retard de confirmation et conservation après saisie invalide vérifiés dans les deux stockages. Pas de sauvegarde HTTP ni validation visuelle revendiquée.
- Tests dates : avant/à/après clôture, veille/jour, heure d’été/hiver, UTC et 29 février. Aucune modification du moteur de dates C01 ou de `Planificateur`/`RaccordManuel`. Les actions futures natives restent vérifiées puis traitées explicitement une à une, jamais la file globale ; confirmations Woo à l’heure réelle, aucune opération bancaire.

Commandes exactes d’orchestration et de rejeu : `wp/tests/echeancier-runner/README-sepa.md`. Les reçus `final.json`, `final.xml`, `final-e2e.json`, `final-e2e-result.json`, logs et `verification.json` lient les octets actuels aux résultats. Exemples réellement exécutés depuis `C:/Users/Ced/imagine` :

```bash
IMAGINE_C05_PACKET=sepa-22nov-1715-final python -B wp/tests/echeancier-runner/sepa.py run --name final
IMAGINE_C05_PACKET=sepa-22nov-1715-final python -B wp/tests/echeancier-runner/sepa.py e2e --name final-e2e
IMAGINE_C05_PACKET=sepa-22nov-1715-final python -B wp/tests/echeancier-runner/sepa.py verify
```

TDD conservé dans `replays/sepa-22nov-1700/` : sept cycles RED/GREEN purs (défaut, positions, date, sans marge, confirmation effective, marge obligatoire, chronologie), puis RED admin sur `sepa_admin_field_present` et GREEN classique/HPOS. Les RED d’API absente/nullabilité signalent des fonctionnalités manquantes ; aucun défaut de transport présenté comme RED métier. Les cas de frontières ajoutés au comportement déjà vert sont des non-régressions, pas un RED fabriqué.

## Changements, empreintes et nettoyage

- PHP de production modifié : seulement `src/Echeancier/Reglages.php` et `ReglagesAdministration.php`. README de ce même dossier actualisé. Nouveau `tests/Echeancier/ConfirmationPremierSepaTest.php`.
- Banc C05 : deux lignes d’appel dans `admin-scenario.php`, nouveau `sepa-scenario.php`, wrapper/vérificateur `sepa.py`, instructions `README-sepa.md`. Aucun moteur du banc partagé modifié.
- Notes : `proposition.md`, présente note, nouveaux paquets de preuves, ancien PRET archivé dans le premier paquet, nouveau PRET lié à `remise.json` après scellement. Aucun fichier protégé, rapport global, Git ou verrou touché ; **647 fichiers protégés inchangés**. Bootstrap, Composer, XML, C01/C04/C06/C07 inchangés.
- SHA-256 `src/Echeancier/Reglages.php` : `414a10f9b8e252d64cac1d9bb8bcee7db6640b689b01477c05875027ba0c12f0`.
- SHA-256 `src/Echeancier/ReglagesAdministration.php` : `0ab7a89640da4532ff954bf0ed09088a5743d4e1de67706b7c366fe3eb222db0`.
- SHA-256 nouveau test : `40be1c38b4530d817b98b0ad5eaaca858817ca06cc4647ea5651d95235d4ad6b`. Manifest complet et hashes des preuves/notes : `verification.json` ; hash PRET et hash de ce manifeste : `remise.json`.

**Nettoyage : quatre conteneurs possédés supprimés, absence revérifiée par noms exacts.** Premier paquet : `imagine-c03-c1076eca8437`, `imagine-c05-add4c69efa41`. Paquet final : `imagine-c03-9f50aa77507c`, `imagine-c05-994b61ae2f01`. Reçus `standard-cleanup.json`, `cleanup.json` dans chacun ; contrôle vivant dans le vérificateur. Sans montage/volume/port/privilèges, capacités supprimées, réseau standard déconnecté avant tests, `none` dès création e2e ; MariaDB sur socket, emails/HTTP bloqués. Sept initialisations de sites entièrement fictifs sur l’ensemble des essais, dont deux dans le passage final ; **zéro licence Novamira**, aucun outil de staging ni compte réel utilisé.

Incident de collecte corrigé : le wrapper historique partageait `preparation.json` entre standard et e2e ; le premier passage a donc remplacé ce seul reçu de préparation standard. Aucun reçu de test RED/GREEN n’a été écrasé. `sepa.py` range immédiatement chaque reçu sous `standard-preparation.json` / `e2e-preparation.json` ; le passage final neuf a rejoué les vraies suites avec ces deux reçus distincts et le lock comparé byte-à-byte. Les anciens paquets restent historiques, sans réécriture de leurs sceaux.

**Limite inchangée :** bibliothèque/prototype non branché. Aucun changement de paiement réel, de droits ou de données clients ; PRET n’est ni clôture indépendante, ni validation visuelle, ni GO financier, réel ou déploiement. Les demandes de recette `docs/recette/` ne sont ni automatisées ni modifiées.
