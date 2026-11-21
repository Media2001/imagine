# C-04 — file du connecteur, prêt à relire

## Livré et frontières

PHP 8.2 pur, namespace `Imagine\Connecteur` : événement immuable, clé déterministe,
dépôt dédupliqué, transitions fermées, contrôles nommés extensibles, quarantaine et
alerte, rejeu plafonné à attente croissante, ordre par abonnement, quatre interfaces
techniques, doubles en mémoire et destination CSV avec journal durable dédupliqué.
Aucun hook WordPress, appel Odoo/n8n, accès réel, service partagé, Git, installation
hôte ou déploiement. Aucun changement aux consignes, au catalogue de recette ou aux
autres lots. Les tests concernent le cœur métier ; R-39/R-40/R-41 restent des cas de
recette proposés, non automatisés comme parcours de réception et non déclarés validés.
La commande explicite C-04 est le périmètre sur mesure, pas une décision de couverture
native des extensions (A-00) ni le branchement WooCommerce/Odoo, toujours en attente.

## Table exhaustive des transitions

| Depuis | Vers permis |
|---|---|
| En attente (`pending`) | En cours |
| En cours (`processing`) | Envoyé, échec temporaire, quarantaine |
| Échec temporaire (`temporary_failure`) | En cours |
| Envoyé (`sent`) | Aucun |
| Quarantaine (`quarantine`) | Aucun |

Toutes les autres transitions sont refusées. Un événement envoyé n’est plus réexpédié.
Le bail d’un traitement interrompu expire vers un échec temporaire, puis passe par
l’attente avant un nouvel essai. À la limite : une alerte, événement conservé, pas de
nouvelle tentative automatique. Les valeurs d’essais, attente, facteur, plafond et
délai d’envoi sont des paramètres obligatoires, pas des décisions d’exploitation.

## Ordre et quarantaine

Les événements sont triés par leur instant de survenue ; à égalité exacte, la clé
fournit un ordre déterministe. Un événement antérieur non envoyé bloque ceux **du même
abonnement**, y compris en quarantaine ou essais épuisés. Les autres abonnements et
commandes indépendantes continuent. J’ai compris qu’il serait dangereux de transmettre
un renouvellement avant la création ou un remboursement avant son antécédent ; aucun
contournement comptable automatique n’est donc autorisé. L’adaptateur doit fournir le
même `subscriptionId` pour toute cette chaîne et déposer les événements chronologiquement
avant traitement. Le moteur ne peut deviner un événement historique encore absent.
Un stockage durable futur devra assurer unicité et CAS atomiques entre processus ;
le stockage livré est volontairement en mémoire comme prescrit par le brief.

## Protection et données provisoires

Liste blanche stricte de champs de facturation, jusque dans les lignes. Les champs
hors schéma sont refusés avant dépôt sans recopier leur valeur dans l’erreur. Les
anomalies de contenu autorisé sont mises en quarantaine avec la première règle en
défaut et un message français lisible. Le validateur expose également toutes les
violations. Les erreurs brutes de transport ne sont pas journalisées. Les identités
et adresses de test sont inventées et les emails en `@example.org`.

L’identité se matérialise provisoirement par un nom, l’adresse par rue/CP/ville/pays.
L’email est facultatif (pas d’exclusion des abonnés hors ligne). Les montants sont déjà
normalisés en unités mineures, total égal à la somme des lignes ; pas de calcul TVA,
signe de remboursement, conversion de devise ou règle tarifaire inventé. Modes de
paiement explicitement injectés par l’adaptateur. La composition explicite
`BillingComposition::withEntreprise` charge le vrai C-02 via Composer depuis le dossier frère.
Le callable reste indépendant ; si absent et numéro renseigné, contrôle indisponible => quarantaine.
Aucun appel BCE/VIES ni contrôle approximatif n'est substitué au C-02 local.

## Réponse perdue : exigence à Step, pas promesse impossible

Le test `late_ack` simule une écriture distante réussie suivie d’un délai dépassé.
La file rejoue la même clé ; la fausse destination déduplique et retourne l’accusé
sans deuxième écriture. Step doit faire de même **atomiquement avec l’effet comptable**,
clé unique persistante pour contact/commande/écriture concernée et accusé récupérable.
Un simple « chercher puis créer » ou une déduplication n8n en mémoire ne suffit pas.
Une destination sans ce contrat ne peut pas être branchée en prétendant garantir
l’absence de doublon. Le délai réel doit être appliqué par l’adaptateur transport ;
le moteur PHP ne peut pas interrompre arbitrairement un appel synchrone tiers.

## Export : veille, jours civils, relances et arrivées tardives

La destination accuse le journal durable ; `sent` signifie pris en charge pour export,
pas facturé par Odoo ni remis à Step. Une tâche future appelle `exportPreviousDay(now)`
après minuit : journée civile précédente de `Europe/Brussels`, fichiers vides inclus,
rattrapage des lots plus anciens si un passage a été manqué. CSV UTF-8, colonnes fixes,
une ligne par événement, liste des lignes en JSON dans `lines_json` ; format provisoire.

Les journées publiées sont scellées. En retard **après** leur publication, les nouveaux
événements rejoignent un lot technique ouvert du jour de leur prise en charge ; leur
véritable date reste inchangée dans `occurred_at`, et `batch_day` explicite le lot.
J’ai compris « aucun manque, aucun doublon, fichier identique au rejeu » ainsi : ne
jamais réécrire un export déjà remis ni perdre une arrivée tardive. Ce report technique
ne décide aucune date de facture/écriture ni période de TVA. Clé et lot sont mémorisés
avant l’accusé, sous le même verrou ; un rejeu ne change jamais cette affectation.
Journal/CSV à conserver et sauvegarder ensemble ; divergence détectée => arrêt explicite.
Les fichiers restent tous dans le dossier privé passé en argument, jamais dans les
médias publics. Le CSV est un fichier d’échange : colonnes texte à importer comme texte,
non comme formules de tableur. Aucun envoi automatique de fichier vers un tiers.

## Connecteur intégré ou n8n — conséquence du cœur livré

Le cœur sépare acquisition métier, stockage, contrôles, transport, horloge et alerte.
En intégré, un adaptateur WooCommerce déposera chaque événement, un stockage WordPress
assurera transactions et prises atomiques, un ordonnanceur appellera le worker et un
transport Odoo remplacera le CSV. On garde les règles au même endroit, proches des
événements et testables sans site. En contrepartie, exploitation des reprises, alertes,
observabilité et écran administratif restent à construire dans le site.

Avec n8n, ce même cœur peut demeurer la frontière de validation/déduplication côté site
et n8n devenir une destination qui accuse durablement les clés. Ou ses contrats peuvent
servir de spécification à une implémentation équivalente ; il faudra alors rejouer ces
tests pour éviter deux vérités métier. n8n apporte orchestration et visibilité, pas
magiquement l’unicité comptable : l’accusé d’un webhook sans enregistrement durable ne
suffit pas, et l’ordre d’un abonnement doit survivre aux branches et reprises.

Ainsi le travail n’est pas perdu dans l’une ou l’autre option ; le choix dépend surtout
du lieu d’exploitation, des responsabilités d’hébergement et du contrat d’idempotence
de Step. Il ne tranche ni le choix de Ced ni le vocabulaire comptable inconnu. Le CSV
permet de tester la frontière sans connecter un service réel.

## À arbitrer / confirmer avant branchement (questions fermées)

- **Ced/Step :** confirmer l’unicité transactionnelle côté destinataire et la reprise
  d’accusé par clé : oui/non ? Sinon, pas de garantie « une seule écriture » possible.
- **Ced/Step :** valider le rattrapage technique des événements tardifs dans un lot
  ouvert, date de survenue conservée, sans réécriture d’un CSV remis : oui/non ?
- **Step :** valider/remplacer le schéma provisoire et le détail des lignes JSON, ainsi
  que la convention d’unité mineure et l’import des textes comme textes : oui/non ?
- **Ced :** maintenir le blocage des événements suivants du même abonnement en
  quarantaine jusqu’à une reprise administrative auditée : oui/non ? Pas de bouton
  de correction/retrait silencieux dans ce lot ; parcours administratif à définir.
- **Ced :** connecteur intégré ou n8n ? Paramètres d’essais/alertes à fixer au branchement.

Ces questions ne déclenchent aucun acte financier ; ce sont des conditions du futur
lot de branchement. `PRET` signifie prêt à la relecture, pas GO ni validation de recette.

## Corrections, décisions écrites et traçabilité — 21 novembre 2026

Instructions 1 à 4, 6, 7 corrigées : lot CSV monotone durable par abonnement sous verrou (journal existant), instantané détaché avant validation, notifications dans la révision de file et rejeu indépendant jusqu'à accusé, composition vraie C-02. Décisions Ced du 21/11 lues sur pièces : neutralisation formule CSV dès ce lot, blocage du même abonnement conservé, alerte de doublon divergent sans données de contenu. Aucun choix intégré/n8n ni unicité distante validé.

Le README décrit le chargement Composer du dossier frère et la protection CSV (apostrophe avant préfixes = + - @, y compris espaces/contrôles ASCII initiaux ; montants entiers négatifs inchangés). Les alertes utilisent le couple (clé événement, code) pour déduplication, conservées avec la transition par CAS ; un nouvel appel à run/replay retente une notification échouée sans réenvoi comptable. Le futur stockage durable doit implémenter ce contrat, le stockage mémoire n'est pas présenté comme persistant après perte du processus.

Règle → source → tests :
- Événement/clé immuable, whitelist détachée → §2.2, brief 1/3 → EventTest, CorrectionsTest::testInstantaneDetacheAvantValidationDepotEtJournal.
- États/CAS et conservation notification → §2.5/4.5, brief 2/4/6 → EventTest::testTransitionTableExhaustive, WorkerTest, testAlerteSurvitPanneEtRedemarrageSansNouvelEnvoi.
- Identité/adresse/montants/paiement/C-02 → §2.2/2.4, brief 3 → ValidationTest, testCompositionAvecVraiC02EtQuarantaine.
- Backoff, limite, panne, accusé perdu → §2.5/4.5, brief 4 → WorkerTest, testRetryPlafondMemeTresGrandNumeroDessai, testRetryRefuseParametresInvalides.
- Ordre/blocage même abonnement → brief 5 + décision Ced C-04 → WorkerTest, testEpuisementBloqueSonAbonnementMaisPasLesAutres.
- Export veille/relance/scellement/monotonie → §2.5/4.5, brief 7 → ExportTest, testRattrapageMonotoneDurableEtOrdreDansLeCsv.
- Formules CSV et doublon divergent → décisions écrites C-04 du 21/11 (protection technique, pas exigence comptable inventée) → testCsvNeutraliseFormulesMaisPasMontantsNumeriques, testDivergenceAlerteeSansRemplacerEvenement.

Différés : instruction 8 demande une écriture dans docs/ecarts.md, interdite par le périmètre. À reporter par son tenant : R-39/40/41 dus au branchement ; i18n au branchement ; payment_reference à confirmer Step. Le schéma, l'unicité transactionnelle distante, le choix intégré/n8n et paramètres d'exploitation restent ouverts. Les interprétations d'identité/email/unité mineure et du rattrapage ci-dessus restent provisoires sauf décisions explicitement citées.

Preuves fraîches tests-21nov/ : suite complète 37 tests / 224 assertions, aucun échec ; PHPCS, syntaxe, Composer strict, exemple C-02 et empreintes des sources réellement chargées passent. Conteneur jetable sans montage/port/service, réseau coupé pendant tests ; nettoyage et manifeste contrôlés. Les anciens reçus tests/ ne sont pas remplacés.

## Preuves

Voir `production/C-04/tests/rapport.md` : PHPUnit, lint, syntaxe, validation Composer,
manifestes SHA-256 des sources réellement copiées, cycles RED/GREEN, non-régression C-01,
CSV fictif réellement produit et reçu de nettoyage du conteneur possédé. Les lanceurs
C-04 importent C-01 sans le modifier ; les caches Python ont été désactivés pour ne pas
laisser de fichiers dans son dossier. Le préfixe de nom du conteneur demeure celui du
banc C-01 ; **son étiquette et son état sont propres à C-04**.
