# C-09 — Profils fictifs à ouvrir

**Complément du 25 novembre 2026 : prêt à relire avec réserves explicites ; aucune acceptation globale de C13/B02 revendiquée.**

## Ouvrir

- Connexion : `http://192.168.129.32:8085/wp-login.php`.
- Mon compte : `http://192.168.129.32:8085/my-account/`.
- Article réservé : `http://192.168.129.32:8085/c08-article-reserve-article/`.
- Liste : `http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-liste-envoi&numero=DEMO-2027-T1` (e-abo/e-admin).
- Identifiants exclusivement hors dépôt : `C:\Users\Ced\.imagine-demo\identifiants.json`, clé `c09_accounts`.

## État réellement relu

30 profils : **9 créés, 20 partiels, 1 impossible**. 27 comptes ; V-ANON/V-FAUX/V-ROBOT sont des scénarios.
13 commandes initiales et 3 renouvellements = 16 commandes, 12 souscriptions manuelles, 14 adhésions. Six tarifs natifs privés/cachés entièrement fictifs ; calendrier 2026–2028 complet (15 parutions), cinq numéros matérialisés.
« Créé » : tout l’état de départ est disponible à la précision fictive autorisée ; « partiel » : une composante manque ; « impossible » : scénario non attestable. Les passerelles/mandats réels et la reconduction automatique restent absents.
Chaque objet C09 et ses lignes portent `imagine_demo_fictif=1` ; titre natif **Paiement fictif de démonstration**, identifiant de passerelle vide, aucun jeton/transaction. Les métadonnées de fixture ne donnent aucun droit.
A-CARTE/A-PAYPAL/A-PAPIER/A-ETRANGER/A-SANSMAIL/A-ECHEANCE/A-NONRENOUV : initiale payée fictive. A-SEPA4 : initiale + un renouvellement payés, total natif 2 ; prochaine action planifiée et deux échéances encore à venir, sans seconde action anticipée pour la quatrième. A-GRACE/A-SUSP : renouvellement failed à J-1/J-4 ; grâce J-1/J+2 ou J-4/J-1. A-VIR reste non payé.
Les dates de début des six profils payés destinés à la projection postale sont normalisées à J-90 (A-SEPA4 : J-180), paiement à ce début ; seconde échéance A-SEPA4 à J-30. A-ECHEANCE et A-NONRENOUV conservent leur année native J-335/J+30 (365 jours), sans changer leur date de départ. Pour ces six profils postaux, cela garde une année C01 comprenant DEMO-2027-T1 sans inventer un renouvellement annuel ni modifier C01/C13. Les observations sont horodatées maintenant, jamais antidatées.

| Profil | État | Compte | C / S / M / renouvellement | Décision réelle article | Ce qui devient visible / limite |
|---|---|---|---|---|---|
| V-ANON | créé | Sans compte | — / — / — / — | anonyme / fermé | Sans session : extrait et invitation à se connecter. Limite : Scénario de visite, pas un compte. |
| V-ROBOT | impossible | Sans compte | — / — / — / — | Non attestable hors ligne | Aucun robot vérifié disponible sur cette démonstration hors ligne. Limite : DNS désactivé par C08 ; aucune IP de robot vérifiée, aucune usurpation de preuve robot. |
| V-FAUX | créé | Sans compte | — / — / — / — | anonyme / fermé | Sans session, UA Googlebot depuis une IP locale non vérifiée : extrait. Limite : Scénario local de faux robot, jamais présenté comme un vrai robot vérifié. |
| V-DEC | créé | v-dec | — / — / — / — | sans_droit / fermé | Défaut fermé. Après activation C10 : première lecture vérifiée, compteur compte de 2 articles distincts, puis bloc découverte épuisée. Limite : Email confirmé par drapeau fictif du script, pas un email envoyé. Paramètres à confirmer par Imagine ; ouvrir le périmètre C12 dans C10 avant la démonstration. |
| V-DEC-FIN | créé | v-dec-fin | — / — / — / — | sans_droit / fermé | Défaut fermé. Après activation C10 : quota de fixture déjà consommé, bloc découverte épuisée sur un article nouveau. Limite : Email confirmé par drapeau fictif. Deux articles C12 déjà ouverts ; relecture fermée une fois le quota épuisé, conformément à C06. Aucun droit PDF. |
| V-INSCRIT | partiel | v-inscrit | — / — / — / — | sans_droit / fermé | Compte client natif, sans commande ni adhésion, article fermé. Limite : Aucun workflow de vérification email installé ; compte fictif utilisable mais vérification non attestée. |
| A-CARTE | partiel | a-carte | 88 / 89 / 90 / — | abonnement_actif / complet | Commande initiale processing et date payée fictives, tarif normal-1 ; abonnement actif et lecture complète. Limite : Aucune carte réelle. Reconduction automatique non posée ; renouvellement manuel maintenu. Compteur 3 numéros et historique C01 non raccordés. |
| A-SEPA4 | partiel | a-sepa4 | 91 / 92 / 93 / 2419 | abonnement_actif / complet | Deux paiements natifs fictifs sur quatre : commande initiale et un renouvellement processing ; prochaine échéance manuelle planifiée, deux échéances restant à venir. Limite : Aucun mandat SEPA ni jeton. WCS planifie seulement la prochaine action, pas une seconde action pour la quatrième échéance. B02 ne lit encore que la commande initiale : sa table ne montre qu’une Payée ; marge C05/dates théoriques non raccordées. |
| A-PAYPAL | partiel | a-paypal | 94 / 95 / 96 / — | abonnement_actif / complet | Commande initiale payée fictive, abonnement actif normal-1 et lecture complète. Limite : Aucun accord PayPal ni jeton ; renouvellement manuel uniquement. |
| A-VIR | partiel | a-vir | 97 / 98 / 99 / — | virement_non_valide / fermé | Commande administrative on-hold, abonnement et adhésion pending : lecture fermée pour virement non validé. Limite : Motif C08 corrigé et relu ; méthode de paiement volontairement vide, aucun compte bancaire ni virement réel. |
| A-PAPIER | partiel | a-papier | 100 / 101 / 102 / — | abonnement_actif / complet | Commande initiale payée fictive normal-4, abonnement actif ; prochaine échéance manuelle ce mois-ci. Limite : Aucun mandat papier ou IBAN, aucun export bancaire. Quatre fois reste une fixture, pas une règle de domiciliation. |
| A-GRACE | créé | a-grace | 103 / 104 / 105 / 2420 | delai_grace / complet | Renouvellement natif failed fictif daté à J-1 ; abonnement on-hold, adhésion paused ; lecture et régularisation pendant la fenêtre J-1/J+2. Limite : Rejet et fenêtre explicitement fictifs ; aucun rejet bancaire réel. Durée de fixture, pas une règle métier décidée. |
| A-SUSP | créé | a-susp | 106 / 107 / 108 / 2421 | suspendu / fermé | Renouvellement natif failed fictif daté à J-4 ; grâce finie à J-1, lecture fermée et exclusion postale suspendu. Limite : Rejet explicitement fictif, jamais un incident bancaire réel ; aucune reconduction automatique. |
| A-EXPIRE | créé | a-expire | 109 / 110 / 111 / — | expire / fermé | Souscription et adhésion expirées hier, sans prochain paiement : lecture fermée. Limite : État administratif fictif, aucun historique de paiement ajouté. |
| A-NONRENOUV | partiel | a-nonrenouv | 112 / 113 / 114 / — | abonnement_actif / complet | Commande initiale payée fictive, souscription pending-cancel jusqu’au terme J+30 ; lecture complète. Limite : Fin native de renouvellement démontrée ; compteur métier 1 numéro restant et historique non raccordés. |
| A-ETRANGER | partiel | a-etranger | 115 / 116 / 117 / — | abonnement_actif / complet | Commande initiale payée fictive, adresse France et ligne de port fictif zéro ; inclusion postale positive. Limite : Supplément de port non chiffré : zéro n’est pas un supplément appliqué ni un tarif Imagine. |
| A-SANSMAIL | partiel | a-sansmail | 118 / 119 / 120 / — | abonnement_actif / complet | Commande initiale payée fictive, adresse technique a-sansmail@example.org ; inclusion positive dans la liste et le CSV postaux C13. Limite : Exclusion individuelle des emails non raccordée. Le coupe-circuit global garantit aucun email mais ne prouve pas ce critère individuel. |
| A-ECHEANCE | partiel | a-echeance | 121 / 122 / 123 / — | abonnement_actif / complet | Commande initiale payée fictive ; abonnement actif, terme J+30, prochaine échéance manuelle J+29. Limite : Reconduction automatique non posée. Rappel/non-envoi non raccordés ; aucun email envoyé. |
| P-OFFRANT | partiel | p-offrant | — / — / — / — | sans_droit / fermé | Compte sans droit ; aucune facturation fictivement attribuée au donateur. Limite : Raccord abonnement offert et renouvellement à la charge du tiers absent ; pas de transaction ni de lien de paiement inventé. |
| P-OFFERT | partiel | p-offert | — / — / — / — | sans_droit / fermé | Compte destinataire créé, lecture prudente fermée. Limite : Aucun lien natif bénéficiaire/offrant disponible ; pas d'adhésion indépendante inventée pour masquer ce manque. |
| P-GEST | partiel | p-gest | — / — / — / — | sans_droit / fermé | Compte créé, aucun lot ni siège fictivement attribué. Limite : Teams/raccord groupé absent : pas de groupe de 5, ni 3 sièges attribués/2 libres ; aucune licence acquise. |
| P-BENEF | partiel | p-benef | — / — / — / — | sans_droit / fermé | Compte propre sans commande, article fermé. Limite : Rattachement au groupe et droit bénéficiaire non disponibles ; pas de facturation au bénéficiaire. |
| P-PRO | partiel | p-pro | — / — / — / — | sans_droit / fermé | Compte client avec société Fictive C09 ; aucun abonnement. Limite : Contrôle local C02 de 0000000097 possible (cohérence seulement) ; existence BCE non attestée, adaptateur de saisie entreprise absent, aucun numéro réel utilisé. |
| P-SOL-ATT | partiel | p-sol-att | — / — / 124 / — | abonnement_actif / complet | Adhésion native manuelle active de fixture : lecture ouverte. Limite : Aucun justificatif réel/factice déposé ; workflow de dépôt et traitement ainsi que tarif solidaire non raccordés. |
| P-SOL-OK | partiel | p-sol-ok | — / — / 125 / — | abonnement_actif / complet | Adhésion native manuelle active expirant dans 45 jours : lecture ouverte. Limite : La fin de droit est native ; aucune validation de justificatif ni décision tarifaire solidaire inventée. |
| P-NUMERO | créé | p-numero | 126 / — / — / — | numero_achete / complet | V-NUM du brief C14 : commande payée de fixture du numéro T1, ses articles et son PDF ouverts ; les autres numéros restent fermés. Limite : Compte/login P-NUMERO conservés. État processing et date_paid synthétiques, zéro euro, aucune passerelle ni transaction réelle. Achat invité et rattachement après achat restent hors lot, sans rapprochement email. |
| P-COOP | partiel | p-coop | — / — / — / — | sans_droit / fermé | Compte sans abonnement ni droit : article fermé. Limite : Attribut coopérateur et raccord CoopHub absents ; aucun statut réel ou drapeau de droit inventé. |
| E-ADMIN | créé | e-admin | — / — / — / — | equipe / complet | Administration WordPress native et lecture complète. Limite : Tous les droits locaux natifs ; les interdictions réseau/paiement de la démo restent en place. |
| E-REDAC | partiel | e-redac | — / — / — / — | equipe / complet | Contenus et numéros éditables, calendrier consultable seulement ; lecture complète des articles. Limite : Pas d’écran d’édition du calendrier pour editor. La capacité réelle de modifier son option (manage_options) est absente ; aucun parcours de date éditable revendiqué. |
| E-ABO | partiel | e-abo | — / — / — / — | equipe / complet | Rôle dédié Référent abonnements : commandes, liste d’envoi C13 et export accessibles ; lecture équipe sans capacité éditoriale. Limite : Échéances, justificatifs et extractions métier non entièrement raccordés. Aucun manage_woocommerce, manage_options ou gestion générale des utilisateurs. |

## Réception et réserves

C09 : 382 contrôles natifs, 149 paiements/marques, 197 HTTP, 10 sécurité, 41 corrections, 30 régression C08 ; tous verts. 7 tests locaux, reset 6/6 ; ID principaux conservés.
C13 strict : 51 PHP + 26 HTTP verts, 10 tests purs/30 assertions ; **exit 2** : P-OFFERT/P-GEST/P-BENEF n’ont pas de liens natifs. Aucun de ces liens n’a été inventé. L’export comporte 8 destinataires (6 BE/2 étranger), dont 6 C09 et A-SANSMAIL.
B02 strict : **140/140**, dont 55 HTTP ; **exit 2**. Les données natives A-SEPA4 sont bien 2/4, mais B02 n’affiche encore qu’une ligne Payée car il ne lit que la commande initiale. Marge C05, historique/compteurs C01 et documents restent non raccordés. Aucun code B02/C13 modifié.
Le runner B02 conserve trois libellés de blocage désormais périmés (profil A-4x-J45, absence de failed, A-CARTE impayé). Le reçu brut est conservé : la consigne de 16h30 corrige le profil en A-SEPA4 ; failed et export A-CARTE sont maintenant attestés. Les attentes des tests de démonstration, pas le code produit ni le runner, ont été adaptées.

## Rejouer

```bash
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/profils.py --preuve relance
PYTHONDONTWRITEBYTECODE=1 python wp/tests/demo/c09-verifier.py
PYTHONDONTWRITEBYTECODE=1 python wp/tests/demo/c09-strict-recipes.py C13
PYTHONDONTWRITEBYTECODE=1 python wp/tests/demo/c09-strict-recipes.py B02
```

Le vérificateur complet est long : le lancer en processus suivi si le terminal a un watchdog court. Il réinitialise les seuls profils C09 et révoque leurs sessions. Son statut global est TECHNIQUE_VERIFIE_ACCEPTATIONS_PARTIELLES ; les sorties strictes 2 sont conservées, pas converties en succès complet. Les reçus des recettes restent sous C09, sans écraser les rendus C13/B02.
Aucune observation existante ni incident n’est nettoyé. Les recettes C13 nettoient uniquement leurs propres objets/relevés temporaires ; B02 ajoute ses deux observations d’adresse et restaure exactement l’adresse. Les anciens reçus/RAPPORT.md restent historiques, remplacés pour l’état actuel par RAPPORT-complement.md et complement-verification.json.
Propositions hors lot : préciser la preuve robot/email, les raccords offert/groupé, justificatifs/CoopHub et le barème de port. Aucun fichier docs/ modifié.
