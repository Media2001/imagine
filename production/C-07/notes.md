# C-07 — Liste d'envoi d'un numéro

Remise du 22 novembre 2026. **PHP pur, prêt à relire ; ni clôture du lot, ni branchement, ni envoi réel.** Reprise d'une session interrompue : les sources étaient présentes et testées, mais il manquait les notes, le rapport et `PRET`. Les sources rejouées sont identiques à celles de `tests/final.json` ; les preuves historiques ne sont pas remplacées.

## Périmètre et références

Brief `briefs/C-07-liste-envoi.md`, exigences de C-01, doctrine du 21/11, cahier des charges §3.4, §3.5, §3.8 et §3.13. C-01 et C-04 sont clos dans `A-FAIRE.md`. Les profils de `docs/recette/profils.md` servent seulement de données fictives : aucun cas de recette ni fichier de `docs/` n'est modifié ou automatisé.

Le sur-mesure est limité à la projection historique et au CSV demandés. Aucun écran, lecture WooCommerce, nouvelle gestion de paiements, droit numérique, stockage, transport réseau ou intégration Odoo. Les branchements standard restent hors de ce lot, conformément au chantier C et à l'étude A-00 déjà close.

## Contrat et utilisation

Code : `wp/plugins/imagine-pilotage/src/Envoi/` ; tests : `tests/Envoi/` dans cette même bibliothèque. Namespace `Imagine\Pilotage\Envoi`, PHP 8.2 minimum, objets readonly, dates `DateTimeImmutable`, aucune lecture de l'horloge.

- `Destinataire(id, nom, rue, complement, codePostal, ville, pays)` : destinataire postal, sans email ni donnée d'acheteur.
- `Situation(effet, enregistre, etat, paiementValide, numerosDus, destinataires, fin = null)` : **photographie complète**, pas un patch. États `actif`, `grace`, `suspendu`, `expire`, `attente`. Les numéros dus sont fournis par C-01 ; C-07 ne les recalcule jamais. `fin` est la borne effective exclusive, notamment celle de la grâce si applicable ; aucune durée par défaut.
- `Abonnement(id, origine, creation, situations)` : origine `abonnement`, `offert`, `groupe`, `numero_unite`. Pour un offert, fournir le destinataire et non l'acheteur ; pour un groupe, uniquement les bénéficiaires effectivement attribués. Les places libres ne produisent rien. Les achats à l'unité sont exclus.
- `ListeEnvoi::etablir($numero, $calendrier, $abonnements, $cloture)` : retourne `numero`, `cloture`, `lignes`, `anomalies`. Le numéro et sa clôture doivent correspondre au calendrier. Un abonnement doit exister avant la clôture, être actif ou en grâce, avoir son paiement validé, ne pas avoir atteint sa fin et devoir ce numéro.

Les erreurs de calendrier, les états/origines inconnus, les abonnements dupliqués, un destinataire répété dans un groupe, plusieurs destinataires pour un abonnement individuel ou deux situations au même instant d'effet sont refusés. Les objets sont des entrées de confiance du futur adaptateur, pas un validateur universel des données WooCommerce.

## Gel et rejeu

J'ai compris la clôture comme dans C-01 : **strictement avant minuit de clôture**, en fournissant les dates métier en `Europe/Brussels`. Création, paiement ou réactivation exactement à la clôture arrivent trop tard.

Une situation n'est retenue que si **son effet et son enregistrement** précèdent la clôture. La plus récente par effet l'emporte. L'historique doit être complet, append-only et horodaté par une source de confiance : ajouter un changement après clôture, même rétrodaté, ne modifie pas la projection antérieure. Adresse et attribution d'un bénéficiaire suivent la même règle. Les lignes sont triées par identifiant d'abonnement puis de destinataire ; les anomalies par motif puis index.

**Limite explicite :** readonly n'est pas une archive persistante. Le futur adaptateur devra conserver la liste clôturée et l'historique fiable. Réécrire ou supprimer une ancienne situation dans les entrées peut changer un recalcul ; le moteur pur ne peut garantir l'intégrité d'un historique falsifié. Aucun stockage de gel n'est simulé ici.

## Anomalies et export

Une adresse sans nom, rue, code postal ou ville produit `adresse_incomplete` ; un pays vide, `pays_manquant`. Même nom et même adresse complète produisent `doublon_destinataire_adresse` sur chaque exemplaire concerné. Espaces normalisés, casse ASCII ignorée ; pas de rapprochement flou, ni de normalisation postale internationale. Un code postal est demandé par ce contrat provisoire, même pour un pays dont les usages diffèrent : à ajuster avec le format du routeur si nécessaire.

Les exemplaires restent dans la projection et les anomalies figurent séparément avec motif, index et copie de la ligne. **L'export d'expédition `ExportCsv::liste()` refuse par défaut une liste présentant des anomalies.** `anomaliesRevues: true` ne doit être fourni que par un futur parcours de traitement explicite ; ce booléen n'est pas une preuve d'approbation. Le sérialiseur bas niveau `ExportCsv::lignes()` n'est pas le point d'entrée d'expédition.

Colonnes provisoires et ordre stable : `abonnement_id,destinataire_id,destinataire,rue,complement,code_postal,ville,pays,origine`. Virgule, UTF-8 sans BOM, LF, échappement CSV standard avec doublement des guillemets et sans échappement antislash. Les valeurs postales restent des chaînes, dont les zéros initiaux.

La fonction de protection de C-04 est extraite dans `Imagine\Connecteur\CsvProtection::cellule()` et réutilisée par les deux exports, sans changer sa règle : apostrophe devant une formule potentielle, y compris après contrôles/espaces ASCII initiaux. Charger les deux autoloaders, pilotage **et** connecteur ; le chargement frère des tests ne remplace pas une dépendance d'intégration. Les 37 tests C-04 sont rejoués. Aucun fichier n'est transmis au routeur.

## À arbitrer par Ced — questions fermées du brief

1. **Grâce :** confirme-t-on qu'un abonné en grâce à la clôture reste dans la liste jusqu'à la fin effective de son délai, oui/non ? Implémentation provisoire isolée dans `ListeEnvoi::ETATS_EN_REGLE` et `Situation::fin`.
2. **Deux abonnements, même personne/adresse :** confirme-t-on deux exemplaires, conservés et signalés en anomalie, oui/non ? Aucun dédoublonnage supprimant un droit n'est effectué.
3. **Routeur :** Imagine confirme-t-elle les neuf colonnes, leur ordre et le format CSV décrits ci-dessus, oui/non ? Si non, le format cible doit être fourni avant branchement.

Ces interprétations sont celles explicitement autorisées par le brief, pas des décisions définitives. Aucune nouvelle règle sur l'argent, les droits numériques ou la comptabilité n'a été choisie.

## Tests et limites de remise

Détail : `production/C-07/tests/rapport.md`. Rejeu du 22/11 dans `production/C-07/replays/reveil-22nov-0340/` : `composer test` standard **270 tests / 29 594 assertions**, dont Envoi **36 / 78** ; régressions connecteur **37 / 224**, zéro échec, erreur ou ignoré. PSR-12 des fichiers PHP modifiés, syntaxe et Composer strict passent.

Le lanceur complet retourne toutefois **1**, uniquement à cause de six avertissements PSR-12 préexistants dans `tests/Echeancier/run.php` (C-05 en attente). Cette réserve n'est ni masquée, ni corrigée hors périmètre. Ce n'est pas un lint global vert. Les tests ciblés C-07 sont rejoués en mode strict, ainsi que C-04.

Le gel, les paiements aux bornes, l'adresse et les remplacements de bénéficiaires avant/après clôture, les numéros fournis par C-01, les profils concernés, les anomalies et le CSV sont exercés. Les tests restent unitaires et d'intégration entre bibliothèques ; **pas une recette WordPress ni une preuve d'envoi réel**. La clôture par Claude nécessite les relectures indépendantes, la vérification du second tour et le traitement des questions métier. Aucun GO réel n'est déduit de `PRET`.
