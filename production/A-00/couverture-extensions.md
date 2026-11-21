# A-00 — Étude de couverture des extensions

**Date : 20 novembre 2026. Statut : étude documentaire prête à relire, pas recette fonctionnelle ni GO.**

Références internes : `briefs/A-00-couverture-extensions.md`, cahier des charges v3.1, `docs/decisions.md` (11, 19 et 20 novembre 2026), doctrine du 19 novembre et consigne permanente. Les décisions de Ced prévalent sur l'ancien scénario de migration du cahier des charges : repartir de la production et conserver ses comptes, abonnements et références de paiement.

## Lecture et limites de la preuve

- **Natif** : possibilité décrite par l'éditeur, à configurer et à recetter sur les versions effectivement retenues. Ce mot ne signifie pas « testé chez Imagine ».
- **Module** : autre extension officielle ou du catalogue retenu, distincte du composant examiné. Une fonctionnalité déjà intégrée au cœur n'est pas un module à acheter.
- **Sur mesure** : raccord métier imposé par le cahier des charges mais non couvert intégralement par la documentation consultée ; sa conception financière ou d'accès reste soumise à arbitrage.
- **Doute** : absence de preuve documentaire suffisante, documentation contradictoire ou inaccessible. Ce n'est pas une démonstration que le produit ne sait pas le faire.
- Les appels **[n]** renvoient aux URL officielles dans « Sources ». Les citations anglaises sont des **extraits exacts**, parfois de phrase ou de tableau ; leur contexte est identifié. `sources-officielles.json` conserve URL demandée, URL finale, date de consultation et extraits. Aucune information de forum, article de blog ou comparateur ne fonde les conclusions.
- L'étude ne comporte aucune installation, connexion à un compte, lecture du site réel, donnée client, opération Git, achat ou déploiement. Les pages publiques de documentation seules ont été consultées. Les textes en ligne ne constituent pas l'audit des versions installées en production ; celui-ci relève d'A-02.

### Ce qui a réellement été testé dans A-01 — et seulement cela

Lecture des preuves **préexistantes**, sans les rejouer ni les modifier : `files/rapports/2026-11-20-15h35-A-01-commercial.md`, `files/rapports/2026-11-20-A-01-commercial-cases.json` et `wp/tests/licensed-a01/evidence/e49f54c5e931/result.json`. Le reçu annonce **104 contrôles PASS, 4 observations, sans échec** ; ce ne sont pas 104 tests métier indépendants. La concordance du reçu avec son empreinte et ses compteurs est contrôlée dans `verification.json` d'A-00.

| Preuve A-01 | Portée admise ici | Ce qu'elle ne prouve pas |
|---|---|---|
| Vrais Subscriptions 9.4.1 et Memberships 1.30.3 ; stockage classique et HPOS | Création d'abonnements fictifs et conservation des champs métier avant/après neutralisation/anonymisation | Engagement annuel, quatre échéances, coupon, passerelle ou migration Stripe |
| Adhésions autonomes et shortcode de restriction | Membre actif autorisé ; invité, non-membre, adhésion expirée, annulée ou en pause refusés | Liaison automatique achat/abonnement → adhésion ; paywall HTTP, thème, cache, REST, flux ou oEmbed |
| Détection de duplication/staging, ordonnanceur | Mode staging constaté ; un renouvellement **manuel sans paiement** créé comme témoin ; exécution bloquée sous verrou | Débit bancaire, mandat, retries, grâce, PayPal, cadeau, équipe ou billetterie |

**A-00 n'ajoute aucun test fonctionnel d'extension.** A-01 ne déclare pas l'import opérateur prêt : la fidélité des fichiers de l'importeur reste non démontrée. Le futur fichier `PRET` d'A-00 désigne uniquement la remise de cette étude à la relecture ; il ne change aucun statut d'A-01.

## Tableau de synthèse

| N° | Besoin et référence | Natif / module / sur mesure | Sources |
|---|---|---|---|
| 1 | Annuel, une fois, reconduction — §3.4 | Natif Subscriptions pour la facturation annuelle automatique ; sur mesure pour engagement/non-renouvellement conformes au projet | [4][5] |
| 2 | Quatre paiements dus, dates civiles communes — §3.4–3.5 | Natif pour intervalle et première charge entière ; **synchronisation insuffisante** pour une phase trimestrielle civile commune ; raccord métier requis | [1][2][3][4] |
| 3 | Carte/Bancontact puis SEPA — §3.6 | Module Stripe officiel ; Bancontact → SEPA documenté ; carte → carte documenté ; carte → SEPA systématique : doute, collecte d'un mandat distinct à prévoir | [5][6][7][8] |
| 4 | SEPA et case de mandat — §3.6 | Module Stripe officiel pour SEPA ; mandat documenté ; case explicite dans le tunnel Woo : doute ; ouverture dès mandat à raccorder | [8][9][22] |
| 5 | PayPal initial et automatique — §3.6 | Module PayPal Payments ; deux mécanismes ; conditions Reference Transactions documentées, compatibilité des dates modifiables/synchronisation par moteur : **doute**, cellules probantes absentes | [11][12] |
| 6 | Virement/mandat papier administrateur — §3.6, §3.13 | Natif pour abonnement/renouvellement manuels ; circuit papier, écran de validation et Odoo : sur mesure | [13][14] |
| 7 | Emails Stripe supprimés, PayPal minimisés — §3.8 | Reçus Stripe réglables avec exceptions ; **zéro email Stripe non garanti avec son identifiant créancier** ; PayPal : doute documentaire signalé | [8][10] |
| 8 | Cadeau, destinataire et choix de reconduction — §3.4 | Cadeau intégré au cœur documenté ; **pas d'achat de l'ancien module Gifting** ; coordonnées immédiates, surprise et consentement de reconduction : adaptation | [15][16] |
| 9 | Gestionnaire et bénéficiaires remplaçables — §3.4 | Module Teams for WooCommerce Memberships ; comptes/droits/places ; adresses papier et liste d'envoi à raccorder | [17] |
| 10 | Réduction première année/campagne — §3.4 | Natif : coupons limités en nombre de paiements ; limites/expiration Woo ; quatre paiements ≠ garantie d'année contractuelle | [18][19][20] |
| 11 | Accès actif et achat d'un numéro à vie — §3.9 | Natif Memberships, plans distincts abonnement/numéro ; rattachement numéro → articles/PDF à organiser | [21][22] |
| 12 | Découverte unique durée/articles — §3.9 | Natif pour durée ; unicité par personne, compte vérifié et compteur d'articles : doute puis raccord à développer si retenu | [21][24] |
| 13 | REST, flux, oEmbed, recherche, partages — §3.9, §4.4 | Couverture partielle ; RSS documenté ; recherche avec risque explicitement signalé ; autres voies : doute ; étanchéité serveur à développer/vérifier | [23][24] |
| 14 | PDF contrôlé à chaque requête — §3.9 | Téléchargements Woo protégés sous conditions serveur ; **Memberships ne protège pas les URL de fichiers** ; contrôle métier courant à raccorder | [24][25] |
| 15 | Échec, grâce, nouvelles tentatives — §3.8 | Retry natif ; grâce maintenant les droits non couverte par défaut on-hold ; adaptation des règles et des droits | [22][26][27] |
| 16 | Port/pays et recalcul aux renouvellements — §3.4, §3.7 | Zones et adresses natives ; recalcul automatique du reliquat et notification non établis : sur mesure à qualifier | [13][28][29][30] |
| 17 | Billets QR, tarif abonné, quotas — §3.11 | Event Tickets + Plus, via Woo et Memberships ; capacité/QR documentés ; intégration à recetter, pas de nouvelle extension de remise présumée nécessaire | [21][31][32][33][34] |
| 18 | Reprise des abonnements et tokens Stripe — §4.3 | **Copie conservant l'existant**, selon décision de Ced ; CSV possible mais pas preuve de transfert de moyens de paiement ; migration entre comptes : doute | [35] |
| 19 | Balisage payant — §3.9 | Rank Math PRO : Custom Schema Builder avec exemple paywall ; réglage/modèle métier, pas réécriture d'un générateur ; pas une protection d'accès | [36][37][38] |

## 1. Abonnement annuel payé en une fois

**Référence : §3.4. Verdict : natif pour la cadence, pas pour tout le contrat Imagine.**

Subscriptions documente une fréquence en années et le renouvellement sans expiration tant qu'il n'est pas annulé ; les paiements automatiques nécessitent une passerelle compatible.[4][5] Citation : « By default, subscriptions renew indefinitely until the subscriber or store manager cancels them. »[4]

Le réglage à examiner est donc un abonnement annuel, sans expiration, montant annuel, avec passerelle automatique. Un virement reste un renouvellement manuel, même si le produit est annuel.[4][5][13] Aucun module de fractionnement n'est nécessaire pour cette ligne.

**Reste métier :** engagement d'un an, arrêt à son terme, opposition à la reconduction, préavis après reconduction et mentions du tunnel (§3.4, §3.7–3.8). Le simple bouton d'annulation standard n'est pas une preuve de conformité à ces règles. Aucun avis juridique n'est rendu ici ; ne pas choisir une règle de résiliation à la place de Ced/Imagine.

**Test :** pas de renouvellement annuel payé exercé dans A-00 ou dans le reçu A-01 cité.

## 2. Quatre échéances dues et synchronisées sur les trimestres civils

**Référence : §3.4–3.5 et décision du 19 novembre. Verdict : standard utile, mais insuffisant.**

### Synchronisation examinée en premier

Le guide permet une première charge entière à la souscription : « Customers are charged the full recurring amount when they subscribe. »[1] Il décrit aussi la fenêtre de coupure : la laisser à zéro est la configuration à examiner si aucun inscrit ne doit échapper à la première charge immédiate ; pas de prorata.[1]

**L'obstacle n'est donc pas le montant de la première charge.** Le guide détaillé explique que, pour les intervalles supérieurs à une unité, le premier alignement ignore cet intervalle : « It always uses the next occurring alignment date, regardless of the billing interval. »[2] Son exemple est explicite : souscription le 6 avril, tous les trois mois, alignée au premier du mois → premier renouvellement le **1er mai**, pas le 1er juillet.[2] Deux inscriptions à des mois différents peuvent ainsi amorcer des phases trimestrielles différentes. **« Tous les trois mois, le même jour du mois » ne garantit pas « mêmes quatre dates de l'année pour tous ».** C'est une déduction de cet exemple, pas un test exécuté.[2]

Le guide général précise que l'alignement s'applique au premier renouvellement, que les suivants sont calculés depuis le paiement précédent, et qu'un changement de réglage ne réaligne pas les abonnements existants.[1] Il faut donc aussi prévoir retards, échecs, changements exceptionnels du calendrier et reprise de l'existant ; ne pas promettre que la seule synchronisation maintient le calendrier métier.[1][2]

Les deux pages ne décrivent pas exactement les mêmes choix pour les derniers jours du mois (1–28 dans le guide général, 1–27 ou dernier jour dans le guide détaillé) : **doute de version/interface**, sans conséquence sur le contre-exemple du premier du mois.[1][2]

### Peut-on déplacer chaque prochaine échéance ?

Oui, l'API documentaire expose `WC_Subscription::update_dates( $dates, $timezone )`, avec la clé `next_payment`, et `can_date_be_updated( $date_type )`. Extraits : « Set the dates on the subscription. » et « Check if a given date type can be updated for this subscription. »[3]
Les dates sont interdépendantes ; le fuseau par défaut est GMT. La possibilité effective dépend également des fonctionnalités de la passerelle.[3][5][30]
Une mise à jour directe d'une métadonnée n'est pas l'interface documentée ici.

**Raccord à prévoir, après arbitrage :** faire calculer la prochaine date par le calendrier métier et la transmettre par ces API, sans recréer l'encaissement Woo. Les contraintes de dates, le repositionnement après chaque résultat de paiement et la compatibilité passerelle/ordonnanceur seront des tests du branchement futur ; aucune preuve A-01 ne les couvre.[3][5]

### Quatre paiements ne constituent pas une reconduction annuelle

La documentation propose une expiration après un nombre de paiements et précise que le paiement initial compte ; l'abonnement expire alors, au lieu de se reconduire automatiquement.[4] Citation illustrative : « After the 12th payment, the subscription expires. »[4] Régler une durée finie ou quatre paiements ne fournit donc pas, à lui seul, un nouveau bloc annuel reconduit avec quatre sommes dues.[4]

**Contre-exemple documentaire indépendant des extensions :** dans un calendrier fictif aux 10 janvier, avril, juillet et octobre, une inscription le 20 février 2027 payant immédiatement puis à chaque date commune donnerait aussi le 10 janvier 2028 avant son anniversaire du 20 février 2028 : **cinq charges**, et non quatre, sur cette première année. Les dates sont des hypothèses de démonstration, jamais le calendrier d'Imagine. Le décompte est vérifié mécaniquement dans `verification.json`.

**Garde-fou contractuel : quatre numéros réguliers par année d'engagement (§3.5)** ; le contre-exemple civil ne substitue pas un décompte de jours ou d'année civile à ce bornage. Il faut donc distinguer **année d'engagement, quatre créances/échéances, numéros papier et validité numérique** (§3.5). La façon de traiter la date commune supplémentaire, la première tranche de l'année reconduite et l'opposition à la reconduction doit être arbitrée, pas déduite d'un réglage « trimestriel ». L'étude n'arrête pas une architecture financière à la place de Ced.

**Tests :** exemples documentaires et décompte de dates seulement ; pas de commande synchronisée, déplacement réel, encaissement ni reconduction en quatre fois testé.

## 3. Carte ou Bancontact au départ, puis SEPA

**Référence : §3.6. Verdict : distinguer les deux parcours.**

Pour la **carte**, la matrice officielle dit : « The Stripe extension can support automatic renewals via normal card payments ».[5]
Elle documente donc une récurrence par carte, pas une transformation systématique carte → mandat SEPA.[5]
**Divergence brief / cahier (§3.6) :** le cahier exige carte → carte automatique ; seul Bancontact prévoit SEPA pour les échéances suivantes. L'extension à carte → SEPA vient du besoin 3 du brief, pas du §3.6, et n'est pas arbitrée. **Doute :** aucun parcours Woo officiel consulté ne prouve cette transformation automatique. Si l'extension du brief est confirmée par Ced, collecter et rattacher un mandat SEPA explicite sera à concevoir ; une carte enregistrée ne prouve pas l'acceptation de ce mandat.[5][8]

Pour **Bancontact**, la matrice inclut les méthodes qui tokenisent via SEPA ; le guide Stripe du plugin précise, à propos des paiements iDEAL enregistrés, « They are saved as SEPA Direct Debit tokens. », puis que le réglage Bancontact « does the same, but for Bancontact payments. »[5][6]
La chaîne Bancontact initial → SEPA ultérieur est donc **documentée**, sans module de conversion supplémentaire identifié.[5][6]
Bancontact exige notamment EUR : « For example, Bancontact requires that payments be in euros (EUR). »[7]

**Reste à vérifier :** texte de consentement visible, identification du mandat, preuve d'acceptation, cas compte existant/nouveau et parcours réellement choisi au checkout. Ne pas confondre le réglage de sauvegarde pour achats ultérieurs et les prérequis exacts des abonnements : le guide précise que la sauvegarde générale des moyens n'a pas à être activée pour traiter Subscriptions.[6]

**Module :** passerelle Stripe officielle pour WooCommerce (WooCommerce), en plus de Subscriptions. **Test :** aucun paiement Stripe dans A-00 ou le reçu A-01.

**Note d'articulation pour besoins 4, 6 et 15 (priorité à arbitrer par Ced) :** §3.6 vise l'accès anticipé après mandat et son retrait au premier rejet ; §3.8 vise un impayé de renouvellement établi et un délai de grâce. Pour un premier rejet SEPA ou un paiement manuel non validé, la priorité entre retrait immédiat et grâce reste ouverte : cette étude ne la choisit pas. Les reprises natives ne valent pas décision de droits.

## 4. Domiciliation SEPA et mandat par case à cocher

**Référence : §3.6. Verdict : SEPA documenté ; présentation exacte et accès anticipé à raccorder.**

Stripe impose le mandat : « The customer must accept a mandate that authorizes the debit. »[8] La documentation du Payment Element dit, dans son contexte de valeurs d'essai, « The Payment Element automatically validates the IBAN and displays the mandate when you enter one of these test values. »[9] La passerelle Woo offre SEPA Direct Debit parmi ses moyens supplémentaires.[7]

Cela prouve un support du mandat et de SEPA, **pas la présence garantie de la case à cocher précise demandée par Imagine dans chaque tunnel Woo/blocs**. La documentation Stripe décrit aussi une acceptation liée à la confirmation du paiement.[8][9] **Doute sur la case native :** conserver le besoin de case explicite et de preuve de consentement ; qualifier le rendu puis adapter uniquement si nécessaire. Aucun formulaire SEPA séparé ou stockage local d'IBAN n'est décidé ici.

Le cahier des charges ouvre le numérique dès le mandat accepté et retire l'accès en cas de rejet. La confirmation bancaire est asynchrone selon Stripe, tandis que l'accès Memberships lié à un abonnement suit son état.[8][22] **Raccord à prévoir :** événement d'acceptation réellement exploitable par l'intégration, accès provisoire, puis rejet/succès, sans assimiler l'acceptation à un paiement encaissé. La documentation examinée ne prouve pas la chaîne complète pour Imagine : doute, à recetter.

**Module :** même Stripe officiel, pas de module de mandat supplémentaire établi. **Test :** aucun IBAN, mandat ou webhook de paiement exercé.

## 5. PayPal : achat initial et renouvellements automatiques

**Référence : §3.6. Verdict : oui sous conditions, sans assimiler les deux moteurs PayPal.**

La documentation PayPal Payments distingue **PayPal Subscriptions** (plan piloté par PayPal) et **PayPal Vaulting** (moyen enregistré réutilisé par l'intégration).[11] La matrice mentionne « Business accounts only » et, pour Vaulting, « Requires Vault approval (Reference Transactions) ».[11] La page dédiée précise : « Vaulting requires your PayPal business account to be approved for Reference Transactions ».[12]

**Doute documentaire :** les extraits conservés de [11] ne donnent ni cellules et en-têtes de comparaison ni phrases équivalentes prouvant les dates modifiables et la synchronisation/proratisation pour chacun des deux moteurs. Le libellé « Synchronized or prorated payments » ne prouve pas ses valeurs. La compatibilité différenciée de PayPal Subscriptions/Vaulting et la préférence pour Vaulting restent donc à confirmer sur une preuve exacte avant décision ; ne pas déclarer l'un conforme ni l'autre incapable sur cette seule pièce. L'approbation Reference Transactions demeure une condition documentée, pas obtenue.[11][12]

La connexion, les autorisations et les webhooks du compte professionnel devront être vérifiés ultérieurement par un opérateur autorisé ; aucun compte n'a été consulté. L'approbation n'est ni un module payant supplémentaire ni un réglage que nous pouvons déclarer obtenu.[11][12] Si elle manque, ne pas présumer qu'un plan PayPal fixe satisfait le besoin n°2 : compatibilité encore en doute et arbitrage nécessaire.

**Module :** WooCommerce PayPal Payments (WooCommerce/PayPal). Ne pas remplacer cette étude par PayPal Standard, ni confondre une offre Pay Later éventuelle et les quatre échéances d'Imagine. **Doute :** disponibilité de Pay Later pour les acheteurs belges au lancement, non établie ici et non indispensable à la facilité SEPA prévue au cahier des charges.

**Test :** aucun premier paiement, renouvellement ou compte sandbox PayPal exercé.

## 6. Renouvellement manuel : virement et mandat papier

**Référence : §3.6, §3.13. Verdict : briques natives, procédure métier spécifique.**

Subscriptions peut créer des commandes de renouvellement à payer manuellement ; les méthodes de paiement Woo peuvent servir aux renouvellements manuels.[5][13] La création d'un abonnement par un gestionnaire est documentée : « WooCommerce Subscriptions also gives store managers the ability to create subscriptions manually. »[14]

Le socle évite donc de recréer abonnements et commandes. En revanche le mode interne « domiciliation bancaire sur mandat papier », invisible au tunnel, la référence du mandat sans IBAN, l'export des prélèvements à lancer, la sélection des paiements reçus, l'ouverture des droits et la reprise du statut Odoo restent le raccord des §2.2, §3.6 et §3.13. **Doute :** aucune fonction native complète correspondant à cet écran métier n'a été établie.[13][14]

Distinguer « abonnement actif », « commande de renouvellement en attente » et « paiement validé » ; voir la note commune aux besoins 4/6/15 : premier paiement manuel non validé et renouvellement établi ne sont pas assimilés, priorité retrait/grâce non tranchée ; ne jamais marquer une somme payée pour la seule raison qu'un abonnement a été créé. La règle du mandat papier et celle de l'accès dès mandat Stripe ne sont pas interchangeables (cahier des charges, §3.6).

**Module supplémentaire :** aucun établi au-delà du socle. **Test :** A-01 a créé une commande de renouvellement manuel sans paiement ; ni validation bancaire administrateur ni droits liés à ce paiement n'y sont testés.

## 7. Emails Stripe et PayPal

**Référence : §3.8. Verdict : écart bloquant à arbitrer avant de promettre zéro email Stripe.**

Stripe ne transmet pas automatiquement chaque reçu : « Stripe doesn’t email every receipt it creates. »[10] Le réglage des reçus existe, mais une adresse `receipt_email` explicitement transmise peut forcer l'envoi, « even if Successful payments is turned off. »[10] Il faut donc contrôler réglages **et** comportement de l'intégration, pas seulement désactiver un bouton.[10]

**Les prénotifications SEPA ne sont pas de simples reçus.** La documentation décrit l'envoi propre, son contenu et son délai ; elle précise, pour « If you use the Stripe Creditor ID », que « Stripe always sends the notifications. »[8] Désactiver les reçus ne démontre donc pas qu'aucun email Stripe ne partira. Utiliser un identifiant créancier propre et remplacer les notifications est une possibilité documentaire conditionnelle, pas une situation constatée sur le compte Imagine.[8]

Le besoin « aucun email Stripe » est par conséquent **non garanti et potentiellement incompatible avec l'identifiant créancier Stripe**. Faire choisir à Ced/Imagine soit l'exception de notification obligatoire, soit l'examen d'un identifiant propre et d'une prénotification assurée par Imagine/Brevo. Ne jamais désactiver des notifications obligatoires sans remplacement qualifié.[8]

**PayPal : doute.** Les notices d'aide publique ont renvoyé HTTP 403, y compris la notice correcte `https://www.paypal.com/us/cshelp/article/how-do-i-update-my-email-notification-preferences-help193`. La tentative dans un navigateur n'a fourni aucun texte exploitable. Le résultat de moteur de recherche n'est pas retenu comme preuve. Ni la liste exacte des messages obligatoires ni un réglage global permettant au vendeur de supprimer ceux des acheteurs ne sont établis. Ne pas promettre le silence des comptes PayPal destinataires.

**Reste :** inventaire des messages réellement émis en mode test, routage des messages métier Woo via Brevo et remplacement des modèles selon §3.8. **Test :** aucun email de paiement envoyé ; les barrières d'envoi testées par A-01 ne prouvent pas les réglages du prestataire.

## 8. Abonnement offert

**Référence : §3.4. Verdict : socle cadeau natif dans la documentation actuelle, adaptations Imagine nécessaires.**

L'ancienne notice annonce « The Gifting feature has been merged into the core » et « the Gifting for WooCommerce Subscriptions extension has been retired. »[15] **Ne pas ajouter cet ancien module à la liste des achats.** La version effectivement auditée en A-02 devra être comparée à la documentation, sans supposer que la production possède déjà la fonction.[15]

Le guide du cœur décrit l'email du destinataire, sa création de compte et les emails de prise en main : « only needs to enter the recipient’s email address. », « an account will be created for them. », « sent to the recipient via email. »[16] Il précise que la première connexion peut demander l'adresse de livraison, et qu'en l'absence d'adresse existante la livraison de l'abonnement peut rester `N/A` jusque-là.[16]

**Écarts avec Imagine :** l'acheteur doit saisir dès la commande nom, adresse postale et email ; il peut ne pas vouloir d'email au destinataire, qui doit pourtant obtenir un compte ; la reconduction à sa charge est un choix explicite, absent par défaut ; deux propositions distinctes doivent partir à l'échéance (§3.4). Le simple formulaire cadeau natif ne prouve pas ces règles.[16] Prévoir uniquement les champs et le cycle manquants ; conserver les liens acheteur/destinataire natifs. L'absence de reconduction ne doit pas couper l'année déjà offerte (besoins 1–2 et 11).

**Doute :** option native exacte du choix annuel par cadeau et compatibilité de ce choix dans un panier contenant aussi l'abonnement personnel ; non établies dans les documents consultés.[4][16] À recetter avant toute adaptation additionnelle.

**Module supplémentaire :** aucun Gifting autonome dans la cible documentaire. **Test :** aucun cadeau, destinataire, panier mixte ou consentement de reconduction exercé dans A-01.

## 9. Abonnements groupés

**Référence : §3.4. Verdict : Teams couvre le groupe numérique ; la distribution papier reste à raccorder.**

Teams distingue propriétaire, gestionnaires et membres ; le propriétaire gère notamment la facturation et les bénéficiaires.[17] Le réglage de retrait précise : « Check to let team owners and managers remove members from their teams. » ; le rôle du propriétaire inclut « adding members and managing billing ».[17] Invitations, comptes individuels, nombre de places et liaison à Subscriptions sont décrits.[17]

Le remplacement peut donc être étudié par retrait puis attribution d'une place, avec le réglage adapté, sans développer un autre gestionnaire d'équipes.[17] **Doute :** aucune preuve que les invitations standard collectent, pour chaque bénéficiaire, toutes les coordonnées postales exigées au §3.4 et alimentent la liste d'envoi figée de chaque numéro. Prévoir ce raccord aux champs métier et à la liste d'envoi ; ne pas assimiler une place numérique à une adresse postale validée.

**Module nécessaire au scénario groupé :** Teams for WooCommerce Memberships, éditeur SkyVerge, distribué par WooCommerce ; il requiert Memberships et s'intègre à Subscriptions.[17] Aucun achat effectué. **Test :** aucun groupe exercé dans A-01.

## 10. Codes de réduction première année ou campagne

**Référence : §3.4. Verdict : natif, avec une limite en paiements à ne pas confondre avec une année.**

Les coupons de panier/produit ordinaires ne touchent que le premier paiement : « However, these coupons apply only to the first payment of a subscription. »[19] Les coupons récurrents limités sont une fonction documentée de Subscriptions, pas un module à acheter.[18] Le guide précise : « The term “payments” in this document can also include the initial payment for a subscription in addition to renewal payments. »[18]

Pour l'annuel payé en une fois, limiter la remise au paiement initial/à un paiement est donc une base standard. Pour un plan trimestriel régulier, une limite à quatre paiements est la base à examiner pour les quatre premières fractions, paiement initial compris.[18][19] **Doute d'équivalence contractuelle :** une limite en paiements ne garantit pas la remise sur exactement la première année si le calendrier n°2, les remboursements ou les paiements exceptionnels divergent ; ne pas figer le réglage avant ce raccord.[18]

Les campagnes peuvent s'appuyer sur les restrictions, plafonds d'utilisation et expiration Woo ; la date d'expiration rend le code inutilisable à la date fixée : « Coupons expire/cannot be used on the date that is set. »[20]
Cela ne signifie pas qu'une remise déjà attachée à un abonnement cesse le même jour : la durée de la remise suit sa propre règle Subscriptions.[18][20]
La documentation signale aussi qu'abaisser la limite d'un coupon existant n'a pas un effet immédiat sur tous ses abonnements : un renouvellement supplémentaire peut encore être remisé.[18]

**Sur mesure limité :** suivi métier de source/campagne et extractions si le standard ne fournit pas les indicateurs arrêtés ; aucune nouvelle extension d'affiliation décidée. **Test :** aucun coupon exercé.

## 11. Accès par abonnement actif ou numéro acheté sans limite

**Référence : §3.9. Verdict : deux règles natives distinctes, pas un droit unique qui expire partout.**

Memberships peut attribuer une adhésion par achat de produit et la rendre illimitée : « Select whether the membership is unlimited (never expires) or specify a length. »[21] Un plan rattaché à Subscriptions peut suivre l'état de l'abonnement : « the membership will be valid so long as the subscription is active. »[22]

**Configuration à examiner :** un plan d'abonné rattaché à l'abonnement, et un droit indépendant illimité pour chaque numéro acheté, avec les contenus concernés. L'achat d'un numéro ne doit ni ouvrir les autres numéros ni disparaître avec l'abonnement global.[21][22] Le modèle numéro → articles/PDF, la fenêtre des derniers numéros de la zone 2 et la création répétable des règles relèvent du modèle éditorial prévu (§3.1, §3.3, §4.2). Aucune capacité automatique d'héritage des droits par le lien ACF « numéro » n'a été établie : **doute**, raccord à prévoir.

Le plan exact (un plan par numéro ou attribution équivalente) et le devenir des achats sans compte restent à arbitrer, conformément au chapitre 7 ; cette étude ne choisit pas de nouveau modèle de droits à la place de Ced.

**Test :** A-01 prouve uniquement les états d'adhésions autonomes et le shortcode, pas l'attribution après achat/renouvellement ni la permanence d'un numéro acheté.

## 12. Accès découverte unique

**Référence : §3.9 et décision Imagine n°5 ouverte. Verdict : durée native ; anti-réutilisation et compteur non démontrés.**

Memberships permet une adhésion de durée déterminée, y compris en jours : capacité de durée conservée.[21] **Attribution via inscription gratuite : doute**, les extraits conservés de [21][24] n'établissent pas cette méthode d'octroi. La durée native ne prouve ni un déclenchement à l'inscription ni l'absence de prélèvement dans un parcours à construire ; cet octroi doit être documenté avant usage.

**Doute :** le périmètre documentaire consulté ne prouve ni un plafond d'articles consultés, ni l'unicité « une seule fois par personne » contre la recréation de comptes, ni le refus d'adresses jetables ou la vérification obligatoire d'email demandés au §3.9. Prévoir, si retenus, marqueur de consommation, contrôle du compte vérifié, politique anti-abus et éventuellement décompte serveur des lectures. Un compte ou une adresse email unique n'est pas automatiquement une personne unique.

Ne pas ajouter un module de paywall « au compteur » sans décision. Le chapitre 7 propose sept jours sur le numéro courant sans PDF, mais ce n'est pas une décision arrêtée. **À arbitrer :** durée ou compteur ; l'étendue du droit et le seuil seront ensuite fournis par Imagine.

**Test :** aucune consommation unique, expiration de découverte ou lecture comptée exercée.

## 13. Étanchéité des canaux secondaires

**Référence : §3.9, §4.4. Verdict : ne pas déclarer Memberships étanche sur la seule base du shortcode.**

La FAQ décrit le retrait des contenus restreints des flux RSS : « Any content that is restricted will be removed from your site’s RSS feeds ».[24] Il s'agit d'une possibilité documentée, pas d'une réponse RSS mesurée sur Imagine.

Pour **la recherche interne**, la documentation du mode `Hide content only` signale que la recherche porte sur le contenu réservé, au point que « it's technically possible for a non-member to extract content that's been restricted under this mode. »[23] Le mode `Hide Completely` supprime aussi la visibilité/indexation des contenus, alors que le projet exige un extrait public et une indexation adaptée.[23] Il ne constitue donc pas un remplacement équivalent du paywall demandé.

| Canal | Ce que la documentation permet d'affirmer | Qualification pour Imagine |
|---|---|---|
| HTML normal | Plusieurs modes de restriction et extrait possible | Natif partiel ; rendu du thème/cache non testé[23] |
| RSS | Retrait du contenu restreint décrit dans la FAQ | Documenté ; requête réelle et flux personnalisés non testés[24] |
| REST WordPress et routes personnalisées | Pas de description officielle probante de toutes les réponses dans les pages consultées | **Doute**, contenu, extrait, métadonnées et voies de contournement à tester |
| oEmbed | Pas de contrat de réponse officiel probant trouvé | **Doute**, à tester |
| Recherche interne | Avertissement explicite pour `Hide content only` | Risque documentaire, pas certification d'étanchéité[23] |
| Aperçus de partage, Open Graph et descriptions | Pas de garantie exhaustive dans les documents consultés | **Doute**, texte et données structurées à tester |
| Robot prétendant être Google/Bing | Pas de fonction documentaire établie ici qui réalise la vérification d'identité exigée | Raccord au futur contrôle des robots ; user-agent seul insuffisant selon le §4.4 du cahier des charges |

**Reste à développer/qualifier :** une politique de rendu serveur commune aux canaux, contrôles des droits effectifs, distinction robots vérifiés, séparation des caches et un test d'étanchéité avec texte sentinelle (§4.4). Ne pas retirer les protections natives déjà utiles ; étendre uniquement les voies que la recette révèle insuffisantes.

**Test :** A-01 ne couvre aucune requête HTTP de cette matrice. Les capacités documentées et l'avertissement sur la recherche ne sont pas des résultats de cette recette.

## 14. PDF et contrôle à chaque téléchargement

**Référence : §3.9, §4.4. Verdict : Woo fournit la distribution protégée ; Memberships seul ne protège pas un fichier public.**

La FAQ est explicite : « Memberships does not restrict downloadable file URLs specifically ».[24] Cacher le lien sur une page ne supprime donc pas l'accès direct à un PDF déjà public.[24]

WooCommerce propose `Force downloads` et `X-Accel-Redirect/X-Sendfile`, sous conditions de configuration serveur, et un réglage « Downloads require login ».[25] Le mode `Redirect only` est incompatible avec la garantie demandée : « Anyone with the URL can access the file, even if they are not logged in. »[25] Interdire aussi son utilisation en dernier recours ; pour NGINX, la documentation exige une configuration explicite, pas la seule sélection du mode dans Woo.[25]

La FAQ propose notamment un produit téléchargeable réservé aux membres ou, selon le montage, Subscription Downloads.[24] Ce sont des pistes, **pas la preuve qu'un droit de téléchargement acquis par une commande gratuite est automatiquement retiré dès qu'une adhésion expire**. **Doute sur ce contrôle dynamique :** il faut vérifier le droit actuel à chaque requête (abonnement actif **ou** achat permanent du numéro), les liens déjà obtenus et la remise en cache ; raccorder seulement la décision métier manquante au distributeur Woo.

**Module :** aucun gestionnaire de fichiers supplémentaire établi nécessaire ; Subscription Downloads demeure une option à qualifier, pas un achat imposé. **Test :** aucun PDF ou URL directe exercé dans A-01/A-00.

## 15. Échecs, grâce et nouvelles tentatives

**Référence : §3.8. Verdict : retry natif ; maintien des droits pendant la grâce non équivalent au défaut.**

Subscriptions possède un système de reprises automatiques activable, avec « five (5) default retry rules to retry failed payments over 7 days by default. »[26] Ses règles standard indiquent aussi « Subscription’s status is set to On-hold ».[26] Or un plan Memberships lié suit l'état de l'abonnement ; la réactivation est documentée : « Access will resume when the subscription is reactivated. »[22]

**Conséquence déduite :** activer les reprises ne suffit pas à assurer la grâce Imagine qui maintient l'accès avant suspension. Un passage immédiat `on-hold` peut suspendre les droits liés ; la combinaison des deux paramètres doit être conçue et testée.[22][26] Les sept jours du système par défaut ne sont pas une durée de grâce décidée par Imagine.[26]

Le guide développeur expose l'ajustement des règles ; « Status of the subscription is updated according to the rule: ».[27]
Réutiliser les reprises existantes et adapter, après arbitrage, la politique d'accès temporaire, les alertes, la fin de grâce, les envois papier et la mise à jour du moyen de paiement ; ne pas recréer un ordonnanceur de prélèvements.[26][27] Voir la note commune 4/6/15 : cette grâce d'impayé établi n'est pas déclarée prioritaire sur le retrait d'accès anticipé au premier rejet (§3.6).
La prise en charge dépend de la passerelle et du mode utilisé, notamment côté PayPal où le plan PayPal et Vaulting ne pilotent pas les échecs de la même manière.[11][26]

**Doute :** déclenchement « immédiatement après mise à jour du moyen de paiement » garanti sur tous les parcours retenus ; à exercer, sans promettre une double tentative concurrente. **Test :** aucun rejet bancaire, retry réel ou maintien de droit en grâce testé dans A-01.

## 16. Port par pays et changement d'adresse

**Référence : §3.4, §3.7. Verdict : paramètres natifs, recalcul métier non prouvé.**

Woo règle la livraison par zones : « Customers only see the methods available for their address and its corresponding shipping zone. »[28] Subscriptions permet de changer l'adresse d'un abonnement : « This process updates the shipping address for that subscription only. »[29] Mais le renouvellement automatique reprend le mode d'expédition : « The same shipping method is used for all renewal payments ».[13]

Le guide d'édition permet de modifier les totaux récurrents, dont le port : « There are a few different recurring totals that you can edit in an active subscription: product pricing/qty, shipping prices, fees, and taxes. »[30] **Modifier une adresse ou disposer d'un écran de modification des totaux ne prouve pas le recalcul automatique demandé.** Doute documentaire sur le recalcul complet des numéros restant dus, du renouvellement et de l'alerte à l'administration.

**Raccord à prévoir :** évaluer les zones/tarifs existants lors d'un changement de pays, calculer le reliquat lié aux numéros et mettre à jour les sommes futures par les interfaces Woo, en tenant compte des taxes et de la compatibilité passerelle ; notifier l'administration (§3.7). Le sort d'une différence de port déjà payée d'avance (avoir, somme additionnelle ou ajustement futur) est un arbitrage d'argent, pas une valeur par défaut à inventer.

**Module supplémentaire :** aucun établi pour des suppléments fixes par pays. **Test :** aucun changement de pays avec recalcul/prélèvement exercé.

## 17. Billetterie payante, QR, remise abonné et quotas

**Référence : §3.11. Verdict : assemblage standard documenté, pas recette effectuée.**

La documentation de l'éditeur, accessible via les anciennes URL The Events Calendar redirigées vers son portail Nexcess, indique : « Event Tickets Plus adds attendee registration forms, Apple Wallet and PDF tickets, QR check-in, and WooCommerce ticketing. »[31] Event Tickets est le socle gratuit ; Plus ajoute notamment le moteur Woo ; The Events Calendar est optionnel pour attacher la billetterie à son calendrier.[31]

La capacité est native, y compris partagée : « As tickets sell, the remaining stock drops for every ticket that shares it. »[32]
Les billets ont un contrôle QR individuel : « Event Tickets Plus uses QR codes to embed unique check-in URLs for each ticket in your order database ».[33]
Le guide d'intégration Woo décrit des réglages « to provide an exclusive discount to members. »[34]
Memberships peut également définir des remises sur des produits ou catégories.[21]

**Configuration à examiner :** Event Tickets + Plus avec WooCommerce comme moteur de vente, produits billets et remise Memberships conditionnée à l'abonné connecté. Ne pas supposer que le moteur autonome Tickets Commerce réutilise les passerelles Woo ou les règles Memberships.[31][34] Les documents permettent d'éviter d'emblée une nouvelle extension de promotion ; le montant du tarif abonné reste à fournir par Imagine.

**À recetter :** affichage et total réellement réduits, invité/non-abonné refusé pour le tarif réservé, capacité partagée, dernières places et achats concurrents, statut des billets en paiement différé, QR et email, annulation/remboursement. La compatibilité documentaire Woo n'est pas une garantie générale de toutes les extensions tierces : le guide le signale lui-même.[34]

**Modules :** Event Tickets et Event Tickets Plus, éditeur The Events Calendar ; aucun achat effectué. **Test :** aucun billet ou QR exercé.

## 18. Reprise d'abonnements et moyens de paiement Stripe

**Référence : §4.3, précisée par les décisions du 11 et du 19 novembre. Verdict : préserver l'existant, pas inventer un transfert de tokens.**

Le scénario décidé copie la production et conserve comptes, mots de passe, abonnements et références ; seuls les abonnés hors ligne passent par un import spécifique. L'ancien besoin « d'un site vers un autre » doit donc être étudié comme capacité/réversibilité, **pas lancé comme nouveau chantier de migration des abonnés en ligne** (`docs/decisions.md`).

Le guide officiel sépare clairement données d'abonnement et moyens de paiement : « Moving subscription records and moving the payment methods used for renewals are separate parts of a migration. »[35] Il présente l'ajout manuel et un importeur CSV en bêta publique, avec limites de support ; cela n'établit ni un export complet, ni le transfert de tokens Stripe entre comptes marchands.[35]

**Scénario confirmé par Ced le 21/11, à vérifier lors de la bascule :** conserver le même compte Stripe, les références client/moyen/mandat et leurs relations, la configuration de passerelle et les notifications adéquates, avec un seul site autorisé à déclencher les prélèvements. Ce sont des conditions de préservation à vérifier, pas une preuve de succès donnée par un CSV.[35] Pour un changement de compte ou de passerelle, obtenir la procédure officielle correspondant aux deux intégrations ; **doute** tant qu'elle n'est pas qualifiée.[35]

**Module nécessaire au scénario décidé :** aucun nouvel importeur pour les abonnés en ligne établi. Un outil CSV reste une option de migration exceptionnelle à qualifier, pas un achat recommandé ni un remplacement de la copie fidèle.

**Test :** A-01 conserve des références fictives et verrouille l'ordonnanceur ; aucun token Stripe réel ou test n'a servi à un renouvellement après copie. La fidélité complète de l'import opérateur reste non démontrée.

## 19. Balisage de contenu payant

**Référence : §3.9. Verdict : fonction de configuration PRO documentée, avec branchement éditorial.**

Le Custom Schema Builder de Rank Math PRO permet d'ajouter des propriétés/groupes : « The Custom Schema Builder allows you to create new fields by adding properties and property groups. »[36] Le guide comporte explicitement « Subscription and Paywalled Content », avec `isAccessibleForFree` et `cssSelector` ; un modèle peut être réutilisé.[36] Le type presse existe : « If your post is an article on a News website, then you can set the type as News Article. »[37]

Google fournit l'exemple de référence : « Here's an example of NewsArticle structured data with paywalled content. »[38]
Son exemple emploie `isAccessibleForFree: false`, `hasPart` et un `WebPageElement` portant un `cssSelector` sur la section réservée.[38]
**Conclusion :** commencer par un modèle Rank Math PRO correctement paramétré ; ne pas écrire un second générateur JSON-LD avant d'avoir qualifié ce modèle.[36][37][38]

**Reste :** relier le statut éditorial « libre/réservé/découverte », le sélecteur réel du thème et les données de l'article au schéma ; éviter les doublons et tester le résultat selon la spécification du référenceur. Le balisage décrit un accès payant, il ne réalise pas le contrôle de droit ni la vérification des robots prévue au §4.4.[36][38]

**Module supplémentaire :** aucun au-delà de Rank Math PRO déjà imposé par §4.1. **Test :** aucun balisage rendu ou résultat enrichi validé dans A-01/A-00.

## Modules complémentaires nécessaires et éditeurs

Cette liste distingue une **dépendance documentaire à prévoir** d'un achat autorisé. Aucun achat, compte ni installation n'a eu lieu.

| Élément | Éditeur / distribution | Qualification |
|---|---|---|
| Passerelle Stripe officielle pour WooCommerce | WooCommerce | Nécessaire aux parcours carte/Bancontact/SEPA ; ne pas confondre avec WooPayments[5][6][7] |
| WooCommerce PayPal Payments | WooCommerce / PayPal | Nécessaire au parcours PayPal ; approbation Vaulting/Reference Transactions conditionnelle, pas licence supplémentaire[11][12] |
| Teams for WooCommerce Memberships | SkyVerge, distribué par WooCommerce | Complément nécessaire au scénario groupé ; nécessite Memberships, liaison Subscriptions pour la récurrence[17] |
| Event Tickets + Event Tickets Plus | The Events Calendar | Socle et complément billetterie ; choix du moteur Woo pour le scénario étudié[31][34] |
| WooCommerce Subscriptions + Memberships ; Rank Math PRO | WooCommerce / SkyVerge ; Rank Math | Composants déjà retenus, pas de doublon à ajouter[4][21][36] |

**À ne pas ajouter par défaut :** ancien Gifting autonome retiré (fonction intégrée) et module de coupons limités (fonction native).[15][18]
Subscription Downloads ou un gestionnaire de fichiers restent des options à qualifier, pas des dépendances établies.[24]
Un importeur CSV n'est pas nécessaire au scénario de copie décidé.[35]
Aucun gestionnaire de paywall au compteur n'est sélectionné : le besoin n°12 reste à arbitrer.

## Ce qui reste à développer ou à raccorder

Les postes ci-dessous sont un **périmètre d'adaptation proposé**, pas du code produit ni un GO financier. Une absence de preuve signalée comme doute doit être levée en recette avant de réimplémenter une fonction native.

1. **Année et quatre échéances** (§3.4–3.5) : engagement/reconduction distincts de la fréquence, quota par année, première charge entière, dates communes et conservation des créances ; utiliser le calendrier et les API Subscriptions, ne pas réécrire l'encaissement (besoins 1–2).[1][2][3]
2. **Mandats et accès anticipé** (§3.6) : parcours carte → SEPA si confirmé, case de consentement si absente, ouverture dès mandat, retrait sur rejet ; conserver Stripe comme dépositaire des informations bancaires (besoins 3–4).[5][6][8]
3. **Paiements hors ligne et messages métier** (§3.6, §3.8, §3.13) : mode papier interne, échéancier/export bancaire sans IBAN, validation administrateur et modèles Brevo (besoin 6).[13][14]
Respecter aussi les messages prestataires incompressibles et qualifier les prénotifications propres (besoin 7).[8][10]
4. **Cadeaux et groupes** (§3.4) : coordonnées papier des bénéficiaires, surprise sans email si choisie, consentement de reconduction absent par défaut, double proposition à l'échéance et liste d'envoi ; réutiliser les identités et relations natives (besoins 8–9).[16][17]
5. **Droits éditoriaux et découverte** (§3.9) : rattachement aux numéros, permanence des achats, marqueur de découverte, vérification du compte et compteur éventuel ; la décision « une personne » reste à préciser (besoins 11–12).[21][22]
6. **Étanchéité serveur et fichiers** (§3.9, §4.4) : politique cohérente HTML/REST/flux/oEmbed/recherche/partages, robots vérifiés, cache, droit PDF courant à chaque demande et distribution privée ; tester les protections natives avant de les remplacer (besoins 13–14).[23][24][25]
7. **Grâce et port** (§3.7–3.8) : conserver les droits durant la grâce décidée, suspendre ensuite ; garder les retries natifs (besoin 15).[22][26][27]
Recalcul pays/reliquat/renouvellement et alerte, en réutilisant les totaux et commandes Woo (besoin 16).[28][29][30]
8. **Raccords de configuration** : suivi de campagne et remise sur billets, sans nouveau moteur de coupon ou de QR justifié à ce stade (besoins 10 et 17).[18][33][34]
Modèle de schéma payant, sans second générateur JSON-LD (besoin 19).[36][38]

Aucun nouveau chantier d'import des abonnés en ligne n'est ouvert (besoin 18). Le branchement financier, le paywall et les intégrations restent soumis aux dépendances et GO de la file projet.

## À arbitrer par Ced

Questions fermées ; aucune réponse n'a été présumée. Les questions touchant aux droits, à l'argent ou aux obligations sont à faire confirmer par Imagine/conseil juridique selon le cas.

1. **Quatre fois — réponse écrite de Ced du 21/11** : exactement quatre paiements, initial compris, par **année d'engagement de date à date**, pas année civile ; bornage associé : quatre numéros réguliers par année d'engagement (§3.5). Autorisation de soumettre seulement un mécanisme écartant la date commune en trop ; aucune mise en œuvre. Proposition à relire : pour chaque année de contrat, conserver quatre positions de paiement dont l'initiale, rattacher les trois suivantes aux numéros réguliers dus via le calendrier ; avant toute planification, contrôler le nombre de positions déjà attribuées à cette année et écarter une cinquième date commune. Ne pas utiliser un remboursement ou un échec comme nouvelle position. Ne pas décider ici des montants, rattrapages ou première tranche de reconduction ; ces points doivent être validés avant branchement.
2. **Carte → SEPA** : maintient-on le prélèvement SEPA obligatoire après une première carte ? **Oui : parcours avec mandat distinct à qualifier / non : carte récurrente acceptée, Bancontact → SEPA conservé**.
3. **PayPal** : retient-on Vaulting sous condition d'approbation Reference Transactions pour les échéances pilotées ? **Oui / non**. Si l'approbation n'est pas obtenue, le circuit fixe ne satisfaisant pas le calendrier, faut-il suspendre cette variante PayPal plutôt que l'annoncer conforme ? **Oui / non**.
4. **Emails Stripe** : si le compte utilise l'identifiant créancier Stripe, accepter l'exception de ses notifications SEPA obligatoires, ou instruire un identifiant propre permettant l'envoi par Imagine ? **Exception admise / étude d'identifiant propre**. La demande « aucun email » ne peut rester une promesse non qualifiée.
5. **Cadeau** : autorise-t-on la collecte immédiate des coordonnées du destinataire et l'adaptation du cycle d'emails et du choix explicite de reconduction, plutôt que le seul parcours email natif ? **Oui / non**.
6. **Teams** : retenir Teams comme gestionnaire numérique, avec raccord spécifique des adresses postales et de la liste d'envoi ? **Oui / non**. Cela ne vaut pas autorisation d'achat.
7. **Découverte** : présenter à Imagine une variante **en durée / au nombre d'articles** ? Et l'unicité technique à faire valider est-elle **par compte vérifié / par personne avec politique anti-abus complémentaire** ? Le seuil et le périmètre restent des données attendues, pas des chiffres inventés.
8. **Grâce** : confirme-t-on que les droits et l'envoi papier doivent rester ouverts jusqu'au terme du délai arrêté, malgré le défaut `on-hold` des retries ? **Oui / non**. La durée exacte reste à fournir par l'administration avant recette.
9. **Port déjà payé** : pour une différence de pays au milieu d'une année réglée d'avance, faut-il **un ajustement immédiat / un ajustement à l'échéance suivante** ? La règle doit préciser également les baisses et la notification ; aucun avoir ou débit n'est créé ici.
10. **Reprise en ligne — réponse écrite de Ced du 21/11** : même compte Stripe, références conservées sur une copie fidèle, sans import CSV des abonnés en ligne. Tout changement de compte sort du scénario décidé et impose une qualification distincte.

## Limites documentaires et remise à la relecture

- PayPal : aide publique sur les préférences d'emails inaccessible (403 ; navigateur sans contenu exploitable). La minimisation exacte des emails reste **doute** ; elle n'est pas justifiée par une citation de moteur de recherche.
- Plusieurs anciennes routes Woo/Rank Math/The Events Calendar ont répondu 404. Des pages officielles de remplacement ont été trouvées pour synchronisation, migration, schéma et billetterie ; elles seules fondent les conclusions. Les redirections The Events Calendar → `docs.nexcess.com/software/the-events-calendar/` sont consignées.
- Le premier extracteur a échoué pour une raison de backend. La collecte retenue est une lecture HTTP directe des documents officiels ; aucun changement de configuration ni installation pour contourner l'échec.
- **Doutes non bloquants pour la remise de l'étude, bloquants pour une promesse de couverture totale :** case SEPA exacte, carte → SEPA automatique, emails PayPal, découverte par personne/compteur, canaux secondaires non décrits, révocation dynamique des PDF, grâce et recalcul complet du port. Chaque doute est affecté à son besoin et à une recette/adaptation future.
- La relecture est à mener avec `doctrine/grille-relecture.md`. Le contrôleur documentaire vérifie structure, références, littéralité des extraits, sources officielles et décomptes A-01 ; il ne certifie pas les conclusions financières, une conformité juridique ou l'étanchéité d'un site.

## Sources

[1] https://woocommerce.com/document/subscriptions/billing-date-alignment — Guide to Billing Date Alignment Documentation - WooCommerce
[2] https://woocommerce.com/document/subscriptions/billing-date-alignment/creating-an-aligned-subscription-product — Creating an Aligned Subscription Product Documentation - WooCommerce
[3] https://woocommerce.com/document/subscriptions/develop/functions — Subscription Function & Property Reference Documentation - WooCommerce
[4] https://woocommerce.com/document/subscriptions/creating-subscription-products — Creating a Subscription Product Documentation - WooCommerce
[5] https://woocommerce.com/document/subscriptions/payment-gateways — Subscriptions Payment Methods & Gateways Documentation - WooCommerce
[6] https://woocommerce.com/document/stripe/setup-and-configuration/settings-guide — Settings Guide Documentation - WooCommerce
[7] https://woocommerce.com/document/stripe/setup-and-configuration/additional-payment-methods — Additional payment methods Documentation - WooCommerce
[8] https://docs.stripe.com/payments/sepa-debit — SEPA Direct Debit payments | Stripe Documentation
[9] https://docs.stripe.com/payments/sepa-debit/accept-a-payment — Accept a SEPA Direct Debit payment | Stripe Documentation
[10] https://docs.stripe.com/receipts — Receipts and paid invoices | Stripe Documentation
[11] https://woocommerce.com/document/woocommerce-paypal-payments/subscriptions — Subscriptions Documentation - WooCommerce
[12] https://woocommerce.com/document/woocommerce-paypal-payments/save-payment-methods — Save Payment Methods (Vaulting) Documentation - WooCommerce
[13] https://woocommerce.com/document/subscriptions/renewal-process — Subscription Renewal Process Documentation - WooCommerce
[14] https://woocommerce.com/document/subscriptions/add-or-modify-a-subscription — Manually Add or Import a Subscription Documentation - WooCommerce
[15] https://woocommerce.com/document/subscriptions-gifting — Gifting for WooCommerce Subscriptions Documentation - WooCommerce
[16] https://woocommerce.com/document/subscriptions/customers-view/gifting-a-subscription — Gifting a Subscription Documentation - WooCommerce
[17] https://woocommerce.com/document/teams-woocommerce-memberships — Teams for WooCommerce Memberships Documentation - WooCommerce
[18] https://woocommerce.com/document/subscriptions/subscriptions-coupons/limited-payment-coupon-guide — Limited Subscription Payment Coupons Documentation - WooCommerce
[19] https://woocommerce.com/document/subscriptions/subscriptions-coupons — Subscriptions Coupons Documentation - WooCommerce
[20] https://woocommerce.com/document/coupon-management — Managing Coupons in WooCommerce Documentation - WooCommerce
[21] https://woocommerce.com/document/woocommerce-memberships-plans — WooCommerce Memberships Plans Documentation - WooCommerce
[22] https://woocommerce.com/document/woocommerce-memberships-subscriptions-integration — WooCommerce Memberships Subscriptions Integration Documentation - WooCommerce
[23] https://woocommerce.com/document/woocommerce-memberships-settings — WooCommerce Memberships Settings Documentation - WooCommerce
[24] https://woocommerce.com/document/woocommerce-memberships-faq — WooCommerce Memberships FAQ Documentation - WooCommerce
[25] https://woocommerce.com/document/digital-downloadable-product-handling — Digital/Downloadable Product Guide Documentation - WooCommerce
[26] https://woocommerce.com/document/subscriptions/failed-payment-retry — Failed Recurring Payment Retry System Documentation - WooCommerce
[27] https://woocommerce.com/document/subscriptions/develop/failed-payment-retry — Developer Guide to Failed Recurring Payment Retry System Documentation - WooCommerce
[28] https://woocommerce.com/document/setting-up-shipping-zones — Setting up Shipping Zones Documentation - WooCommerce
[29] https://woocommerce.com/document/subscriptions/customers-view/update-address — Change Address on Subscriptions Documentation - WooCommerce
[30] https://woocommerce.com/document/subscriptions/add-or-modify-a-subscription/update-an-existing-subscription — Edit an Existing Subscription Documentation - WooCommerce
[31] https://docs.nexcess.com/software/the-events-calendar/setting-up-event-tickets — Setting up Event Tickets - Nexcess Documentation
[32] https://docs.nexcess.com/software/the-events-calendar/create-tickets — Creating Event Tickets - Nexcess Documentation
[33] https://docs.nexcess.com/software/the-events-calendar/ticket-qr-codes — Check In Attendees with QR Codes and the Event Tickets Plus App - Nexcess Documentation
[34] https://docs.nexcess.com/software/the-events-calendar/woocommerce-extensions — Using WooCommerce Extensions with Event Tickets - Nexcess Documentation
[35] https://woocommerce.com/document/subscriptions/migrating-subscribers-woocommerce-subscriptions — Migrating Subscribers to WooCommerce Subscriptions Documentation - WooCommerce
[36] https://rankmath.com/kb/schema-generator — How to Use Rank Math’s Custom Schema Generator » Rank Math
[37] https://rankmath.com/kb/article-schema — Article Schema Type » Rank Math
[38] https://developers.google.com/search/docs/appearance/structured-data/paywalled-content — Subscription and Paywalled Content Markup | Google Search Central  |  Documentation  |  Google for Developers
