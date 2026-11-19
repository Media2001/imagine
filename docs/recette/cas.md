# Catalogue des cas d'acceptance

Proposition du 19/11/2026. Format et règles : `README.md`. Profils : `profils.md`.
« → Odoo » : l'événement arrive dans la file du connecteur avec le bon contenu (voir `README.md`).

## 1. S'abonner

### R-01 — Abonnement en une fois, par carte
§3.4, §3.6, §3.7 · Profil : V-ANON · État : Attend la grille tarifaire (décision 3) pour les montants ; automatisable avec la grille fictive
- **Étant donné** un visiteur sans compte sur la page d'abonnement
- **Quand** il choisit le tarif normal en une fois, saisit ses coordonnées et paie par carte
- **Alors** la clause de reconduction était affichée en gras dans un encadré avant le paiement ; son compte est créé ; l'accès numérique est ouvert immédiatement ; son compte affiche le premier et le dernier numéro, la date d'échéance, le tarif et le mode de paiement ; il reçoit l'email de confirmation ; aucun email de Stripe ; → Odoo

### R-02 — Abonnement en quatre fois, par domiciliation en ligne
§3.4, §3.5, §3.6 · V-ANON · Attend : marge avant clôture (à fixer avec l'administration)
- **Étant donné** un visiteur sans compte
- **Quand** il choisit le paiement en quatre fois, saisit son IBAN et coche l'acceptation du mandat
- **Alors** l'accès s'ouvre aussitôt ; quatre échéances sont planifiées, chacune avant la clôture de la liste d'envoi du numéro qu'elle paie ; l'email de confirmation donne le calendrier des prélèvements ; le site ne stocke pas l'IBAN ; → Odoo

### R-03 — Premier paiement par Bancontact
§3.6 · V-ANON · Attend : résultat de l'étude A-00
- **Quand** il paie par Bancontact
- **Alors** le mandat de prélèvement pour les échéances suivantes était affiché en clair et accepté dans le même geste ; le renouvellement est planifié par prélèvement

### R-04 — Abonnement par PayPal
§3.6 · V-ANON · Attend : compte PayPal professionnel d'Imagine (décision 22), étude A-00
- **Quand** il paie par PayPal
- **Alors** l'abonnement est actif avec un accord de facturation ; le renouvellement est automatique ; → Odoo

### R-05 — Compte existant
§3.7 · V-INSCRIT · Prêt
- **Quand** un lecteur déjà inscrit s'abonne
- **Alors** ses coordonnées sont préremplies ; aucun second compte n'est créé pour la même adresse

### R-06 — Commande d'un professionnel
§3.4 · V-ANON · Attend : arbitrage sur la recherche de dénomination (`decisions.md`, point 8)
- **Quand** il indique commander pour une organisation et saisit un numéro d'entreprise
- **Alors** un numéro mal formé est refusé avec un message clair ; un numéro valide est accepté ; le numéro d'entreprise est transmis ; → Odoo

### R-07 — Tarif solidaire
§3.4, §3.13, §4.4 · V-ANON puis E-ABO · Attend : catégories (décision 4)
- **Quand** il choisit le tarif solidaire, sa catégorie, et dépose un justificatif depuis son téléphone
- **Alors** l'accès est ouvert tout de suite ; le justificatif apparaît dans la file du référent ; le fichier n'est pas accessible par une adresse publique
- **Quand** le référent valide
- **Alors** le statut porte une date de fin ; le fichier est supprimé ; seules la catégorie et la date de fin sont conservées
- **Variante refus** : le fichier est supprimé ; l'abonné est prévenu de la suite (à préciser avec Imagine)

### R-08 — Abonnement offert, sans renouvellement
§3.4 · V-ANON · Prêt
- **Quand** il offre un abonnement en saisissant le nom, l'adresse et l'email du destinataire, sans demander le renouvellement, et sans demander de prévenir le destinataire
- **Alors** le destinataire a un compte rattaché à l'abonnement, avec les droits d'un abonné ; il ne reçoit aucun email ; son adresse postale entre dans la liste d'envoi ; l'abonnement s'arrête après un an ; l'acheteur n'est pas prélevé une seconde fois

### R-09 — Abonnement offert, avec renouvellement
§3.4 · V-ANON · Prêt
- **Quand** il offre un abonnement en choisissant explicitement le renouvellement à sa charge, et demande de prévenir le destinataire
- **Alors** le destinataire reçoit le message prévu ; à l'échéance, c'est l'acheteur qui est renouvelé et prélevé

### R-10 — Abonnement offert et abonnement pour soi dans le même panier
§3.4 · V-ANON · Prêt
- **Alors** une seule commande, deux abonnements distincts, deux adresses de livraison

### R-11 — Abonnement groupé et attribution
§3.4 · P-GEST · Attend : étude A-00
- **Quand** le gestionnaire attribue un abonnement libre à un bénéficiaire (nom, adresse, email)
- **Alors** le bénéficiaire a son propre compte et les droits d'un abonné ; il n'est pas prélevé ; son adresse entre dans la liste d'envoi
- **Quand** le gestionnaire remplace un bénéficiaire en cours d'année
- **Alors** l'ancien perd ses droits, le nouveau les reçoit pour les numéros restants ; le lot reste sur une commande et une facture

## 2. Payer hors tunnel

### R-12 — Virement validé à la main
§3.6, §3.13 · A-VIR, E-ABO · Prêt
- **Étant donné** une commande par virement créée par le référent, non payée
- **Alors** l'accès numérique est fermé et la page le dit
- **Quand** le référent coche le paiement dans l'écran des échéances
- **Alors** l'accès s'ouvre ; l'abonné entre dans la liste d'envoi ; → Odoo

### R-13 — Mandat papier listé puis validé
§3.6, §3.13 · A-PAPIER, E-ABO · Prêt
- **Étant donné** un abonné sur mandat papier dont l'échéance tombe ce mois-ci
- **Alors** il figure dans la liste exportable des prélèvements à lancer (abonné, montant, référence du mandat, échéance) ; le site ne contient aucun IBAN
- **Quand** le référent valide le paiement
- **Alors** l'accès reste ouvert et l'abonné reste dans la liste d'envoi
- **Variante** : paiement non validé à la date prévue → l'accès se referme

### R-14 — Passage du mandat papier à la domiciliation en ligne
§3.6, §3.7 · A-PAPIER · Prêt
- **Quand** il signe un mandat en ligne depuis son compte
- **Alors** son mode de paiement change ; le référent est prévenu qu'il doit clôturer l'ancien mandat

### R-15 — Abonné sans adresse électronique
§3.13 · E-ABO · Prêt
- **Quand** le référent crée un abonné sans email
- **Alors** le compte porte une adresse technique interne et la marque « sans email » ; il n'est destinataire d'aucun envoi ; il figure dans la liste d'envoi

## 3. Vie de l'abonnement

### R-16 — Renouvellement annuel
§3.4, §3.5, §3.8 · A-ECHEANCE · Attend : délai exact du rappel (cadre légal à confirmer par Imagine)
- **Étant donné** un abonné à 30 jours de son échéance
- **Alors** il reçoit le rappel de reconduction au plus tard 15 jours avant la date limite d'opposition, avec la date, le montant et le lien de gestion
- **Quand** l'échéance arrive
- **Alors** il est prélevé ; ses quatre numéros suivants commencent au numéro qui suit son dernier numéro ; → Odoo

### R-17 — Avis avant prélèvement
§3.8 · A-SEPA4 · Prêt
- **Alors** avant chaque prélèvement, il reçoit un email avec le montant, la date et le numéro concerné

### R-18 — Prélèvement rejeté et délai de grâce
§3.8 · A-SEPA4 · Attend : durée du délai (décision 12)
- **Quand** un prélèvement est rejeté
- **Alors** l'abonné garde son accès ; il reçoit l'email d'échec avec le lien de mise à jour du moyen de paiement ; le référent en reçoit copie ; le paiement apparaît dans les paiements échoués

### R-19 — Régularisation pendant le délai de grâce
§3.7, §3.8 · A-GRACE · Prêt
- **Quand** il met à jour son moyen de paiement
- **Alors** le paiement est relancé automatiquement ; s'il réussit, l'abonnement redevient normal sans intervention

### R-20 — Suspension au terme du délai, puis réactivation
§3.8 · A-GRACE puis A-SUSP · Attend : décision 12 ; décision 8 pour le paiement en quatre fois
- **Quand** le délai de grâce s'achève sans régularisation
- **Alors** l'accès est fermé ; l'abonné sort de la liste d'envoi du prochain numéro
- **Quand** il régularise ensuite
- **Alors** l'abonnement est réactivé ; les numéros dont la liste était déjà clôturée ne sont pas rattrapés

### R-21 — Non-renouvellement en un clic
§3.4, §3.7, §3.8 · A-CARTE · Prêt
- **Quand** il désactive le renouvellement depuis son compte
- **Alors** un seul clic suffit ; il reçoit l'email de non-renouvellement avec la date de fin, les numéros encore dus et la question de sortie ; l'abonnement va à son terme ; aucun prélèvement à l'échéance

### R-22 — Rétractation en ligne
§3.7, §3.8 · abonné depuis moins que le délai légal · Attend : modalités à confirmer par le conseil juridique d'Imagine
- **Quand** il utilise la fonction de rétractation, en deux étapes
- **Alors** l'abonnement est annulé ; l'accès est fermé ; le remboursement est enregistré ; → Odoo (note de crédit)
- **Variante** : hors délai, la fonction n'est plus proposée

### R-23 — Changement de pays
§3.7 · A-CARTE · Prêt
- **Quand** il change son adresse de livraison pour un autre pays
- **Alors** le supplément de port des numéros restants et le montant du renouvellement sont recalculés et affichés ; le référent est prévenu

### R-24 — Fin du statut solidaire
§3.4 · P-SOL-OK · Attend : décision 4
- **Alors** avant la date de fin, l'abonné est invité à confirmer son statut et peut déposer un nouveau justificatif depuis son compte

## 4. Lire

### R-25 — Abonné connecté
§3.9 · A-CARTE · Prêt
- **Alors** il lit le texte complet d'un article réservé ; il télécharge le PDF du numéro ; le mode lecture du navigateur affiche l'article complet

### R-26 — Anonyme : extrait seul, partout
§3.9, §4.4 · V-ANON · Attend : longueur de l'extrait (décision 20), réglable en attendant
- **Quand** il demande un article réservé
- **Alors** il reçoit l'extrait et le bloc d'abonnement ; le texte réservé est absent du code de la page, de l'interface REST, des flux, de l'oEmbed, de la recherche interne et des aperçus de partage ; le mode lecture du navigateur n'affiche que l'extrait ; l'adresse directe du PDF est refusée

### R-27 — Robot vérifié et faux robot
§3.9, §4.4 · V-ROBOT, V-FAUX · Prêt
- **Alors** le robot vérifié reçoit le texte complet et le balisage de contenu payant ; le faux robot (bon agent utilisateur, mauvaise adresse) reçoit l'extrait

### R-28 — Cache
§4.4 · A-CARTE puis V-ANON · Attend : hébergeur
- **Quand** un abonné puis un anonyme demandent la même page
- **Alors** l'anonyme ne reçoit jamais la version complète

### R-29 — Acheteur d'un numéro
§3.7, §3.9 · V-ANON puis P-NUMERO · Attend : décision 7
- **Quand** il achète un numéro papier sans compte, puis crée son compte
- **Alors** il lit les articles et le PDF de ce numéro, sans limite de durée ; il n'a pas accès aux autres numéros ; il ne reçoit pas le hors-série

### R-30 — Accès découverte
§3.9 · V-INSCRIT puis V-DEC-FIN · Attend : forme et étendue (décision 5), réglables en attendant
- **Quand** un compte vérifié ouvre son accès découverte
- **Alors** il lit dans les limites réglées
- **Quand** l'accès est consommé
- **Alors** il ne peut pas en ouvrir un second ; une adresse email jetable est refusée à l'inscription

### R-31 — Bénéficiaires et coopérateur
§3.9 · P-OFFERT, P-BENEF, P-COOP · Attend : niveau d'intégration CoopHub (décision 21) pour la pose automatique
- **Alors** le destinataire d'un abonnement offert et le bénéficiaire d'un groupe lisent comme un abonné ; le coopérateur non abonné n'a pas accès aux articles réservés et accède à l'espace coopérateurs

## 5. Administrer

### R-32 — Liste d'envoi figée
§3.5, §3.13 · E-ABO · Prêt
- **Quand** le référent exporte la liste d'envoi d'un numéro après sa clôture
- **Alors** elle contient les abonnés qui y ont droit, bénéficiaires d'abonnements offerts et groupés compris ; ni A-SUSP, ni A-VIR, ni P-NUMERO ; un abonnement créé après la clôture n'y entre pas

### R-33 — Commande pour le compte d'un client
§3.13 · E-ABO · Prêt
- **Alors** le référent crée un abonnement en trois écrans au plus, en retrouvant le compte existant ou en le créant

### R-34 — Calendrier de parution
§3.5 · E-REDAC · Prêt
- **Quand** la rédaction modifie la date de clôture d'un numéro à venir
- **Alors** les droits et les échéances qui en dépendent sont recalculés ; rien ne change pour un numéro déjà clôturé

### R-35 — Grille tarifaire modifiable
§3.4 · E-ABO · Prêt
- **Quand** l'administration change un montant ou le tarif présélectionné
- **Alors** le tunnel l'applique sans intervention technique ; les abonnements en cours ne sont pas modifiés avant leur renouvellement

## 6. Autour

### R-36 — Achat d'un billet
§3.11 · V-ANON, A-CARTE · Attend : licence Event Tickets Plus
- **Alors** l'acheteur reçoit son billet avec un QR code ; l'abonné connecté obtient le tarif réduit ; le quota est respecté ; → Odoo

### R-37 — Formulaire de personnalisation et Brevo
§3.7, §3.10 · A-CARTE · Attend : questions du formulaire (décision 19), compte Brevo de test
- **Quand** il remplit le formulaire après son achat, en donnant son consentement
- **Alors** les réponses deviennent des étiquettes sur son compte, modifiables ; elles sont transmises à Brevo ; sans consentement, rien n'est transmis ; ne pas répondre ne bloque rien ; rien de tout cela n'est transmis à Odoo

### R-38 — Emails
§3.8 · tous · Prêt pour le déclenchement ; textes à fournir
- **Alors** les cinq emails du §3.8 partent au bon moment, au nom d'Imagine, en français ; aucun email de Stripe ; A-SANSMAIL ne reçoit rien

## 7. Connecteur

### R-39 — Odoo indisponible
§2.5, §4.5 · Prêt
- **Étant donné** Odoo injoignable
- **Quand** une commande est payée
- **Alors** le lecteur ne s'aperçoit de rien ; l'événement attend dans la file ; il est rejoué au retour d'Odoo ; rejoué deux fois, il ne crée pas de doublon

### R-40 — Anomalie mise en quarantaine
§2.5 · Prêt
- **Quand** un événement contient une donnée invalide
- **Alors** il est mis en quarantaine et signalé ; il n'atteint pas Odoo ; les événements suivants passent

### R-41 — Export quotidien de secours
§2.4 · Attend : format attendu par Step
- **Étant donné** l'interface d'Odoo non disponible
- **Alors** le connecteur écrit chaque jour un export des événements de la veille, sans trou ni doublon d'un jour à l'autre

## Ce qui n'est pas dans ce catalogue

Les seuils mesurés (performance, Lighthouse, accessibilité, balisage, compatibilité mobile) ont leurs propres contrôles automatiques. Le tableau de bord, les extractions et l'intégration CoopHub seront détaillés quand leur contenu sera arrêté (atelier, décision 21). La migration a son plan de contrôle propre (lot A-06 et répétition générale).
