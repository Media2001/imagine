# C-07 — Liste d'envoi d'un numéro

**Remise du 22 novembre 2026, file de 13 h 20 : format d’export configurable.** Les neuf colonnes provisoires restent le défaut ; sélection et ordre sont désormais un réglage validé. **Bibliothèque PHP et adaptateur d’administration autonome prêts à relire, pas clos** ; aucun branchement au bootstrap, envoi réel ou GO. Preuves actuelles : `production/C-07/replays/format-export-22nov-final/`. Détail : `format-export-2026-11-22.md`. Les preuves de corrections précédentes restent historiques.

## Périmètre et références

Brief `briefs/C-07-liste-envoi.md`, exigences de C-01, doctrine du 22/11 et arbitrages du 22/11, cahier des charges §3.4, §3.5, §3.8 et §3.13. C-01 et C-04 sont clos dans `A-FAIRE.md`. Les profils de `docs/recette/profils.md` servent seulement de données fictives : aucun cas de recette ni fichier de `docs/` n'est modifié ou automatisé.

Le sur-mesure est limité à la projection historique et au CSV demandés, plus un adaptateur Settings API dédié au format d’export pour satisfaire la nouvelle doctrine sans modifier le bootstrap partagé. Aucun écran métier d’expédition, lecture WooCommerce, nouvelle gestion de paiements, droit numérique, stockage du gel, transport réseau ou intégration Odoo. Les branchements standard restent hors de ce lot, conformément au chantier C et à l’étude A-00 déjà close. Aucune dépendance à C-05 ou C-06, candidats non clos.

## Contrat et utilisation

Code : `wp/plugins/imagine-pilotage/src/Envoi/` ; tests : `tests/Envoi/` dans cette même bibliothèque. Namespace `Imagine\Pilotage\Envoi`, PHP 8.2 minimum, objets readonly, dates `DateTimeImmutable`, aucune lecture de l'horloge.

- `Destinataire(id, nom, rue, complement, codePostal, ville, pays)` : destinataire postal, sans email ni donnée d'acheteur.
- `Situation(effet, enregistre, etat, paiementValide, numerosDus, destinataires, fin = null)` : **photographie complète**, pas un patch. États `actif`, `grace`, `suspendu`, `expire`, `attente`. Les numéros dus sont fournis par C-01 ; C-07 ne les recalcule jamais. `fin` est la borne effective exclusive, notamment celle de la grâce si applicable ; aucune durée par défaut.
- `Abonnement(id, origine, creation, situations)` : origine `abonnement`, `offert`, `groupe`, `numero_unite`. Pour un offert, fournir le destinataire et non l'acheteur ; pour un groupe, uniquement les bénéficiaires effectivement attribués. Les places libres ne produisent rien. Les achats à l'unité sont exclus.
- `ListeEnvoi::etablir($numero, $calendrier, $abonnements, $cloture, inclureGrace: true)` : retourne `numero`, `cloture`, `lignes`, `anomalies`. Numéro et clôture correspondent au calendrier. L'abonnement existe avant clôture, doit ce numéro et n'a pas atteint sa fin. Un état actif exige un paiement validé ; **la grâce est incluse quel que soit `paiementValide`**. Le réglage unique `inclureGrace` (true par défaut) permet de désactiver toute grâce, même payée. Le futur adaptateur centralisera ce réglage ; aucune durée n'est inventée.

Les erreurs de calendrier, les états/origines inconnus, les abonnements dupliqués, un destinataire répété dans un groupe, plusieurs destinataires pour un abonnement individuel ou deux situations au même instant d'effet sont refusés. Les objets sont des entrées de confiance du futur adaptateur, pas un validateur universel des données WooCommerce.

## Gel et rejeu

J'ai compris la clôture comme dans C-01 : **strictement avant minuit de clôture**, en fournissant les dates métier en `Europe/Brussels`. Création, paiement ou réactivation exactement à la clôture arrivent trop tard.

Une situation n'est retenue que si **son effet et son enregistrement** précèdent la clôture. La plus récente par effet l'emporte. L'historique doit être complet, append-only et horodaté par une source de confiance : ajouter un changement après clôture, même rétrodaté, ne modifie pas la projection antérieure. Adresse et attribution d'un bénéficiaire suivent la même règle. Les lignes sont triées par identifiant d'abonnement puis de destinataire ; les anomalies par motif puis index.

**Limite explicite :** readonly n'est pas une archive persistante. Le futur adaptateur devra conserver la liste clôturée et l'historique fiable. Réécrire ou supprimer une ancienne situation dans les entrées peut changer un recalcul ; le moteur pur ne peut garantir l'intégrité d'un historique falsifié. Aucun stockage de gel n'est simulé ici.

## Anomalies et export

Nom, rue, code postal et ville sans contenu produisent `adresse_incomplete` ; pays vide, `pays_manquant`. Le contrôle commun retire les espaces Unicode, dont U+00A0 et U+202F. Les valeurs exportées restent inchangées.

Un individuel ou offert **éligible** sans destinataire produit `destinataire_manquant`, avec `abonnement_id`, sans ligne/index inventé. Un groupe sans place attribuée ne produit ni ligne ni anomalie. Un non-éligible sans destinataire ne produit pas de fausse alerte.

Doublons : même adresse complète normalisée et ID de destinataire commun ; à défaut d'ID commun, nom et adresse normalisés. L'ID reste exact, non réécrit ; vide, il ne sert pas de clé commune. Espaces Unicode regroupés et retirés aux bornes, casse UTF-8 abaissée par `mb_strtolower` (**mbstring requis à l'exécution**). Deux exemplaires conservés, chacun signalé **une seule fois**, même si nom et ID se recoupent. Noms différents à même adresse : pas de fusion ; même ID à adresses différentes : pas d'alerte de doublon à même adresse. Pas de rapprochement flou, d'effacement d'accents, de normalisation postale internationale ou canonique NFC. Entrées attendues : UTF-8 de confiance. Le code postal reste obligatoire dans le contrat provisoire, à confirmer avec le routeur.

Les exemplaires restent dans la projection ; les anomalies postales portent motif, index et copie de la ligne. L'anomalie sans destinataire porte seulement motif et identifiant d'abonnement. Tri déterministe par motif, index, puis abonnement pour les anomalies sans ligne. **`ExportCsv::liste()` refuse toute anomalie non revue, même sans ligne.** `anomaliesRevues: true` exige un futur traitement explicite, pas une preuve d'approbation. `ExportCsv::lignes()` reste bas niveau, pas le point d'entrée d'expédition.

Colonnes provisoires et ordre stable **par défaut** : `abonnement_id,destinataire_id,destinataire,rue,complement,code_postal,ville,pays,origine`. `FormatExport($colonnes)` accepte une liste ordonnée non vide de colonnes connues et uniques ; `ExportCsv::liste($liste, anomaliesRevues: false, format: $format)` et `ExportCsv::lignes($lignes, $format)` l’appliquent sans modifier la projection ni contourner les anomalies. Sans argument, le CSV reste identique. Pas de libellés arbitraires, colonne nouvelle ou modification du séparateur. Virgule, UTF-8 sans BOM, LF, échappement CSV standard avec doublement des guillemets et sans échappement antislash. Les valeurs postales restent des chaînes, dont les zéros initiaux.

`AdministrationFormatExport` expose le réglage `imagine_envoi_colonnes_export` : une colonne par ligne, dans l’ordre souhaité, sans écrire de PHP. La Settings API gère l’enregistrement via `options.php`, `manage_options` et `settings_fields()`. Une saisie invalide signale une erreur et conserve le dernier réglage valide ; une option absente ou corrompue revient aux neuf colonnes provisoires. `exporter($liste)` relit le réglage à chaque export en conservant la barrière d’anomalies. **Limite :** `brancher()` est livré mais n’est pas appelé par le bootstrap partagé ; il n’existe donc pas encore de parcours d’administration activé sur un site. Tests d’adaptateur avec doublures explicites uniquement, pas une sauvegarde HTTP, base WordPress native ou validation visuelle. Le branchement reste le lot prévu par le brief. Références officielles et commandes : `format-export-2026-11-22.md`.

La fonction de protection de C-04 est extraite dans `Imagine\Connecteur\CsvProtection::cellule()` et réutilisée par les deux exports, sans changer sa règle : apostrophe devant une formule potentielle, y compris après contrôles/espaces ASCII initiaux. Charger les deux autoloaders, pilotage **et** connecteur ; le chargement frère des tests ne remplace pas une dépendance d'intégration. Les 37 tests C-04 sont rejoués. Aucun fichier n'est transmis au routeur.

## À arbitrer par Ced — questions fermées du brief

1. **Grâce :** le brief précisé le 22/11 impose l'inclusion, même paiement faux. Imagine doit encore confirmer le maintien et la durée du délai avant branchement ; choix isolé dans `inclureGrace` et `Situation::fin`. **La borne C-01 reste inchangée** : `fin <= cloture` exclut, y compris la grâce, paiement vrai ou faux. Sans fin fournie, aucune expiration n'est inventée.
2. **Doublons :** la précision du 22/11 impose deux exemplaires conservés et chacun signalé, par ID commun ou à défaut nom/adresse normalisés. Pas de nouvelle décision à prendre ici. **Sans email :** l'exclusion vise les emails, pas la liste postale. La contradiction historique est signalée à Claude ; instruction 8 et registre des écarts lui appartiennent, aucun `docs/` modifié.
3. **Routeur :** les neuf colonnes provisoires restent le défaut. La réponse d’Imagine s’appliquera par le réglage de sélection et d’ordre, sans modification du code ; elle ne bloque plus cette remise. Tout champ nouveau ou changement de format autre que les colonnes reste hors de la consigne.

Ces interprétations sont celles explicitement autorisées par le brief, pas des décisions définitives. Aucune nouvelle règle sur l'argent, les droits numériques ou la comptabilité n'a été choisie.

## Tests et limites de remise

Détail actuel : `production/C-07/format-export-2026-11-22.md`. Paquet final `production/C-07/replays/format-export-22nov-final/` : `composer test` **362 tests / 30 770 assertions**, Envoi strict **115 / 402**, C-04 strict **37 / 224**, zéro échec/erreur/ignoré. Les suites utilisent `--fail-on-warning --fail-on-risky --fail-on-deprecation`. Lint global, PSR-12 ciblé, syntaxe PHP globale et Composer strict : codes **0**. Ces totaux agrégés n’impliquent aucune clôture de C-05/C-06.

Historique des corrections précédentes : six avertissements C-05 traités sur autorisation, sans reprise pendant cette consigne de format ; détail dans `corrections-2026-11-22.md`. Lors de cette remise, les **34 fichiers C-04** sont identiques, inventaire et SHA-256 comparés sur l’hôte et dans sa copie séparée au conteneur. Aucun fichier C-04, C-05, C-06 ni configuration partagée modifié.

Le paquet `corrections-22nov-1155/` conserve les cinq RED→GREEN (grâce, absence de destinataire, champs Unicode, doublons Unicode, ID stable). Les GREEN précoces ont encore un retour global non nul dû au lint C-05 : les reçus ne le masquent pas. L'essai C-04 initial isolé (37 / 222, un échec) manquait du chemin frère C-02 déclaré par Composer ; le lien interne au conteneur vers les vraies sources copiées rétablit ce contrat, puis `c04-strict-c02.*` passe 37 / 224, sans changer C-04. L'échec initial reste conservé ; le paquet final rejoue le banc corrigé depuis un conteneur neuf.

Oracle CSV : 16 couples entrée/sortie **littéraux**, sans prédicat de production, vérifiés dans les neuf cellules réellement exportées. Profils : attendus littéraux, grâce paiement faux, compte sans email (null) et ID postal distinct, étranger FR et zéro postal initial dans le CSV. Pas de preuve d'adaptateur WooCommerce, absent du lot. C-01 : 170 effectivement absent sans filtre de date ; 171–174 + HS-2027 et renouvellement 175–178 + HS-2028 explicitement attendus.

PHP uniquement dans les deux conteneurs jetables possédés, entrée `sleep`, réseau coupé avant tests, aucun montage, port, BDD ou WordPress. `sample.csv` (défaut) et `format-sample.csv` (sélection/ordre configurés, formule protégée et zéro postal) sont réellement générés et rejoués à l’identique. Chaque `cleanup.json` contient le diagnostic exact d’absence. `format-seal.json` et `format-verification.json` vérifient les fichiers finaux après les dernières écritures. Les RED→GREEN sont conservés dans `replays/format-export-22nov/`, y compris le lint initial non vert ; l’incident d’autoload du seul exemple est conservé dans le paquet final, puis corrigé dans le banc, sans changer C-04. Aucun blocage technique ; l’activation du parcours d’administration appartient au futur branchement, non prouvée ici.

Le gel, les paiements aux bornes, l'adresse et les remplacements de bénéficiaires avant/après clôture, les numéros fournis par C-01, les profils concernés, les anomalies et le CSV sont exercés. Les tests restent unitaires et d'intégration entre bibliothèques ; **pas une recette WordPress ni une preuve d'envoi réel**. La clôture par Claude nécessite les relectures indépendantes, la vérification du second tour et le traitement des questions métier. Aucun GO réel n'est déduit de `PRET`.
