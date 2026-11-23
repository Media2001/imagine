# C09 — À voir sur la démonstration fictive

## Ouvrir

- Connexion : http://192.168.129.32:8085/wp-login.php
- Article réservé testé : http://192.168.129.32:8085/c08-article-reserve-article/ (ID 81).
- Administration : http://192.168.129.32:8085/wp-admin/ ; utilisateurs, commandes, abonnements et adhésions selon le rôle.
- Mots de passe : `C:\Users\Ced\.imagine-demo\identifiants.json`, entrée `c09_accounts`. Rien de secret dans le dépôt.

## Lecture des résultats

30 profils : 4 créés, 25 partiels, 1 impossible. **27 vrais comptes**, et non 30 : V-ANON, V-FAUX et V-ROBOT sont des scénarios de visite.
Objets C09 relus par les API natives : 13 commandes, 12 souscriptions, 14 adhésions, un plan (ID 86), un produit historique privé à zéro (ID 87) et six produits Subscription tarifaires FICTIFS privés et cachés.
Classement strict uniforme (arbitrage 21h10) : « créé » exige tout l’état de départ disponible ; « partiel » signifie qu’au moins une composante manque, même si le compte fonctionne ; « impossible » signifie que le scénario ne peut être attesté. E-REDAC et V-INSCRIT sont donc partiels.
Les montants de la grille sont exclusivement synthétiques, jamais des tarifs Imagine ni une règle de droit. Commandes non payées on-hold, sans transaction ni passerelle ; renouvellements manuels. Aucun débit, mandat ou paiement antérieur inventé.
Calendrier de parution 2026–2028 complet : 15 parutions avec sortie et clôture. Cinq numéros de 2026 sont matérialisés avec articles/PDF ; les raccords métier C05/compteurs/listes restent distincts et absents.
« Renouvellement activé » (A-CARTE/A-ECHEANCE) est non démontrable sur la démo hors ligne, explicitement accepté par l’arbitrage du 23/11/2026 à 21h10. Aucun drapeau de reconduction automatique sans moyen de paiement.
Les motifs ci-dessous proviennent du vrai `Imagine\Site\Paywall::decision` C08/C06, après lecture native Memberships/Subscriptions. 29 décisions relues et 27 connexions C09 réellement réalisées. V-ROBOT n’a pas de preuve positive inventée.

| Profil | État | Identifiant / ID | Objets natifs (C/S/M) | Ce qu’on voit | Décision réelle sur ID81 | Limite précise |
|---|---|---|---|---|---|---|
| V-ANON | créé | Sans compte | —/—/— | Sans session : extrait et invitation à se connecter. | `anonyme` ; fermé ; bloc `connexion` | Scénario de visite, pas un compte. |
| V-ROBOT | impossible | Sans compte | —/—/— | Aucun robot vérifié disponible sur cette démonstration hors ligne. | Non testable : robot vérifié indisponible | DNS désactivé par C08 ; aucune IP de robot vérifiée, aucune usurpation de preuve robot. |
| V-FAUX | créé | Sans compte | —/—/— | Sans session, UA Googlebot depuis une IP locale non vérifiée : extrait. | `anonyme` ; fermé ; bloc `connexion` | Scénario local de faux robot, jamais présenté comme un vrai robot vérifié. |
| V-DEC | partiel | `v-dec` / 6 | —/—/— | Compte utilisable, article fermé faute de raccord découverte. | `sans_droit` ; fermé ; bloc `abonnement` | Validation email et stockage/consommation découverte non raccordés à C08 ; aucun faux droit posé. |
| V-DEC-FIN | partiel | `v-dec-fin` / 7 | —/—/— | Compte utilisable sans abonnement ; article fermé. | `sans_droit` ; fermé ; bloc `abonnement` | Pas de parcours email ni de compteur découverte natif ; épuisement et bloc découverte non démontrés. |
| V-INSCRIT | partiel | `v-inscrit` / 8 | —/—/— | Compte client natif, sans commande ni adhésion, article fermé. | `sans_droit` ; fermé ; bloc `abonnement` | Aucun workflow de vérification email installé ; compte fictif utilisable mais vérification non attestée. |
| A-CARTE | partiel | `a-carte` / 9 | 88/89/90 | Abonnement et adhésion actifs, tarif natif FICTIF normal en une fois : lecture complète. | `abonnement_actif` ; complet ; bloc `aucun` | Aucune carte ni paiement. Renouvellement activé non démontrable sur la démo hors ligne, accepté le 23/11 à 21h10 ; renouvellement manuel. Compteur 3 numéros non raccordé. |
| A-SEPA4 | partiel | `a-sepa4` / 10 | 91/92/93 | Tarif natif FICTIF normal en quatre fois, périodicité trimestrielle ; prochaine échéance manuelle à 30 jours. | `abonnement_actif` ; complet ; bloc `aucun` | Préparation tarifaire seulement : aucun mandat SEPA ni deux paiements inventés ; échéancier métier 2/4 et calendrier C05 non raccordés. |
| A-PAYPAL | partiel | `a-paypal` / 11 | 94/95/96 | Abonnement et adhésion actifs, tarif natif FICTIF normal en une fois : lecture complète. | `abonnement_actif` ; complet ; bloc `aucun` | Aucun accord de facturation PayPal ni jeton ; renouvellement manuel uniquement. |
| A-VIR | partiel | `a-vir` / 12 | 97/98/99 | Commande administrative on-hold, abonnement et adhésion pending : lecture fermée pour virement non validé. | `virement_non_valide` ; fermé ; bloc `regularisation` | Motif C08 corrigé et relu ; méthode de paiement volontairement vide, aucun compte bancaire ni virement réel. |
| A-PAPIER | partiel | `a-papier` / 13 | 100/101/102 | Tarif natif FICTIF normal en quatre fois ; échéance à lancer ce mois-ci, dernière seconde incluse. | `abonnement_actif` ; complet ; bloc `aucun` | Choix technique de fixture quatre fois, pas une règle de domiciliation. Aucun mandat papier ou IBAN ; export bancaire et lancement de prélèvement absents. |
| A-GRACE | partiel | `a-grace` / 14 | 103/104/105 | Souscription on-hold, adhésion paused, fenêtre UTC bornée : lecture et bandeau de régularisation. | `delai_grace` ; complet ; bloc `regularisation` | Fenêtre de fixture explicite de maintenant moins 1 jour à plus 2 jours ; aucune durée métier arrêtée ni rejet bancaire réel simulé. |
| A-SUSP | partiel | `a-susp` / 15 | 106/107/108 | Souscription on-hold, adhésion paused, grâce déjà finie : lecture fermée. | `suspendu` ; fermé ; bloc `regularisation` | Aucun rejet bancaire inventé ; sortie réelle de la liste d'envoi non démontrable sans son adaptateur natif. |
| A-EXPIRE | créé | `a-expire` / 16 | 109/110/111 | Souscription et adhésion expirées hier, sans prochain paiement : lecture fermée. | `expire` ; fermé ; bloc `abonnement` | État administratif fictif, aucun historique de paiement ajouté. |
| A-NONRENOUV | partiel | `a-nonrenouv` / 17 | 112/113/114 | Souscription pending-cancel jusqu'au terme dans 30 jours, adhésion active : lecture complète. | `abonnement_actif` ; complet ; bloc `aucun` | Fin de renouvellement native démontrée, mais le compteur métier 1 numéro restant n'est pas raccordé. |
| A-ETRANGER | partiel | `a-etranger` / 18 | 115/116/117 | Abonnement actif, adresse fictive en France et ligne de port visible à zéro euro de fixture. | `abonnement_actif` ; complet ; bloc `aucun` | Supplément de port non chiffré pour ne pas décider le tarif ; aucun recalcul métier raccordé. |
| A-SANSMAIL | partiel | `a-sansmail` / 19 | 118/119/120 | Abonnement actif, adresse technique a-sansmail@example.org et adresse postale fictive. | `abonnement_actif` ; complet ; bloc `aucun` | Pas de donnée personnelle ; exclusion individuelle des emails et inclusion liste postale non raccordées. Le coupe-circuit email global ne prouve pas cette exclusion. |
| A-ECHEANCE | partiel | `a-echeance` / 20 | 121/122/123 | Abonnement actif, terme natif à 30 jours et prochain paiement manuel planifié à 29 jours (avant le terme). | `abonnement_actif` ; complet ; bloc `aucun` | Renouvellement activé non démontrable sur la démo hors ligne, accepté le 23/11 à 21h10 ; renouvellement manuel. Automate de rappel et marqueur non-envoyé non raccordés, aucun email envoyé. |
| P-OFFRANT | partiel | `p-offrant` / 21 | —/—/— | Compte sans droit ; aucune facturation fictivement attribuée au donateur. | `sans_droit` ; fermé ; bloc `abonnement` | Raccord abonnement offert et renouvellement à la charge du tiers absent ; pas de transaction ni de lien de paiement inventé. |
| P-OFFERT | partiel | `p-offert` / 22 | —/—/— | Compte destinataire créé, lecture prudente fermée. | `sans_droit` ; fermé ; bloc `abonnement` | Aucun lien natif bénéficiaire/offrant disponible ; pas d'adhésion indépendante inventée pour masquer ce manque. |
| P-GEST | partiel | `p-gest` / 23 | —/—/— | Compte créé, aucun lot ni siège fictivement attribué. | `sans_droit` ; fermé ; bloc `abonnement` | Teams/raccord groupé absent : pas de groupe de 5, ni 3 sièges attribués/2 libres ; aucune licence acquise. |
| P-BENEF | partiel | `p-benef` / 24 | —/—/— | Compte propre sans commande, article fermé. | `sans_droit` ; fermé ; bloc `abonnement` | Rattachement au groupe et droit bénéficiaire non disponibles ; pas de facturation au bénéficiaire. |
| P-PRO | partiel | `p-pro` / 25 | —/—/— | Compte client avec société Fictive C09 ; aucun abonnement. | `sans_droit` ; fermé ; bloc `abonnement` | Contrôle local C02 de 0000000097 possible (cohérence seulement) ; existence BCE non attestée, adaptateur de saisie entreprise absent, aucun numéro réel utilisé. |
| P-SOL-ATT | partiel | `p-sol-att` / 26 | —/—/124 | Adhésion native manuelle active de fixture : lecture ouverte. | `abonnement_actif` ; complet ; bloc `aucun` | Aucun justificatif réel/factice déposé ; workflow de dépôt et traitement ainsi que tarif solidaire non raccordés. |
| P-SOL-OK | partiel | `p-sol-ok` / 27 | —/—/125 | Adhésion native manuelle active expirant dans 45 jours : lecture ouverte. | `abonnement_actif` ; complet ; bloc `aucun` | La fin de droit est native ; aucune validation de justificatif ni décision tarifaire solidaire inventée. |
| P-NUMERO | partiel | `p-numero` / 28 | 126/—/— | Commande native de numéro à zéro en attente, aucun abonnement : article fermé. | `sans_droit` ; fermé ; bloc `abonnement` | Pas d'achat payé inventé ; acquisition invité puis rattachement après achat et raccord droit achat au numéro absents de C08. |
| P-COOP | partiel | `p-coop` / 29 | —/—/— | Compte sans abonnement ni droit : article fermé. | `sans_droit` ; fermé ; bloc `abonnement` | Attribut coopérateur et raccord CoopHub absents ; aucun statut réel ou drapeau de droit inventé. |
| E-ADMIN | créé | `e-admin` / 30 | —/—/— | Administration WordPress native et lecture complète. | `equipe` ; complet ; bloc `aucun` | Tous les droits locaux natifs ; les interdictions réseau/paiement de la démo restent en place. |
| E-REDAC | partiel | `e-redac` / 31 | —/—/— | Contenus et numéros éditables, calendrier consultable seulement ; lecture complète des articles. | `equipe` ; complet ; bloc `aucun` | Pas d’écran d’édition du calendrier pour editor. La capacité réelle de modifier son option (manage_options) est absente ; aucun parcours de date éditable revendiqué. |
| E-ABO | partiel | `e-abo` / 32 | —/—/— | Rôle dédié Référent abonnements, commandes natives et lecture équipe, sans capacité éditoriale. | `equipe` ; complet ; bloc `aucun` | Matrice limitée au §3.13. Capacités réservées pour compte client, échéances, justificatifs, liste d’envoi et extractions ; ces écrans métier ne sont pas raccordés. Aucun manage_woocommerce ni gestion générale des utilisateurs. |

## Profils et documentation à préciser — propositions seulement

Aucun fichier de `docs/` n’a été modifié.

1. **V-ANON/V-ROBOT/V-FAUX** : distinguer explicitement scénarios de requête et comptes. Définir la preuve DNS/IP pour V-ROBOT ; hors ligne, il reste impossible, jamais remplacé par une UA ou une IP déclarée.
2. **V-DEC/V-DEC-FIN/V-INSCRIT** : préciser la preuve de vérification email, la forme de découverte choisie, ses dates/compteurs et le raccord natif. Un compte WordPress utilisable ne prouve pas un email vérifié.
3. **A-CARTE/A-SEPA4/A-PAYPAL/A-PAPIER/A-ECHEANCE** : séparer l’état de lecture démontrable des mandats/accords et paiements réellement prouvés. Aucun 2/4 payé ni accord PayPal ne doit être déclaré ici ; les prochaines actions natives manuelles sont vérifiées. A-ECHEANCE a son terme à J+30 et une action à J+29 car WCS exige le prochain paiement avant la fin.
4. **A-VIR** : motif arbitré `virement_non_valide`, corrigé dans C08/C10 et constaté par C09. Le mode de règlement reste vide sur la démo.
5. **A-GRACE/A-SUSP/A-NONRENOUV/A-SANSMAIL** : distinguer fenêtre UTC de fixture d’une durée métier ; préciser le raccord des compteurs de numéros et de la liste postale. Le blocage global des emails ne prouve pas l’exclusion individuelle d’A-SANSMAIL.
6. **A-ETRANGER** : préciser pays, barème et supplément avant d’affirmer « supplément appliqué ». La ligne de port à zéro actuelle n’est pas un vrai supplément.
7. **P-OFFRANT/P-OFFERT/P-GEST/P-BENEF** : préciser les objets/relations du module offert et de Teams, leurs propriétaires et bénéficiaires. Aucun droit indépendant substitutif n’est accordé en attendant ces raccords.
8. **P-PRO** : remplacer « numéro valide » par « cohérence locale » ou « existence BCE attestée » selon la preuve voulue. 0000000097 est uniquement une entrée synthétique cohérente, pas une entreprise attestée ni un attribut de compte raccordé.
9. **P-SOL-ATT/P-SOL-OK** : préciser dépôt, décision, tarif et durée de validité du justificatif séparément de la fin d’adhésion. Une adhésion native de démonstration ne remplace pas une validation de justificatif.
10. **P-NUMERO/P-COOP** : définir la preuve d’achat et le rattachement après achat, puis les adaptateurs achat/CoopHub. La commande en attente n’est pas un achat acquis ; aucun attribut coopérateur non raccordé n’est maquillé en droit.
11. **E-ABO** : rôle dédié Référent abonnements installé, matrice §3.13 limitée et lecture équipe prouvée. Les capacités dédiées réservent les futurs écrans métier, elles ne prouvent pas que ces écrans existent. Aucun droit éditorial, manage_woocommerce, manage_options, gestion générale des utilisateurs ou suppression de commandes. E-REDAC reste partiel : calendrier consultable, pas d’écran d’édition pour editor ; la capacité réelle de sauvegarde native manage_options est refusée et testée.
12. **Données communes** : calendrier 2026–2028 complet (15 parutions avec sortie/clôture), cinq numéros de 2026 matérialisés avec articles/PDF, six tarifs natifs FICTIFS complets. Les raccords métier C05/compteurs/listes restent absents. Aucune grille commerciale validée ni compteur inventé.

## Six combinaisons natives entièrement fictives

| Combinaison | ID produit | EUR synthétiques par échéance | Période / intervalle / durée |
|---|---|---|---|
| normal-1 | 192 | 120 | year / 1 / 1 |
| normal-4 | 193 | 30 | month / 3 / 12 |
| solidaire-1 | 194 | 60 | year / 1 / 1 |
| solidaire-4 | 195 | 15 | month / 3 / 12 |
| soutien-1 | 196 | 240 | year / 1 / 1 |
| soutien-4 | 197 | 60 | month / 3 / 12 |

Raccords natifs commande/souscription/produit de l’adhésion : A-CARTE et A-PAYPAL → normal-1 ; A-SEPA4 et A-PAPIER → normal-4. Pour A-PAPIER, quatre fois est un choix de fixture, pas une règle de domiciliation. Variantes solidaire/soutien préparées sans justificatif ni nouveau droit. Quatre fois signifie périodicité trimestrielle sur douze mois, pas preuve de deux échéances payées.

Matrice persistante exacte du rôle `imagine_referent_abonnements` (Référent abonnements) : `read`, `edit_shop_orders`, `edit_others_shop_orders`, `read_private_shop_orders`, `edit_private_shop_orders`, `edit_published_shop_orders`, `publish_shop_orders`, `imagine_creer_compte_client`, `imagine_gerer_echeances`, `imagine_traiter_justificatifs`, `imagine_exporter_liste_envoi`, `imagine_extraire_abonnes`.

## Preuves et rejeu

- `installation.json`, `relance.json`, `reset.json` et `readback.json` : contrôles de la dernière recette complète après les sources finales. Les ID principaux restent identiques.
- `readback.json` : objets natifs et décisions nominatives ; `http.json` : 27 connexions, témoin de contenu et blocs ; E-ABO ouvre les écrans natifs liste/création de commande (200), mais pas éditorial/réglages (403). E-REDAC ne peut ouvrir le parcours natif de réglages (403). Aucun cookie/nonce/mot de passe enregistré.
- `red-runtime.json`, `red-safety.json`, `red-reset.json` : échecs réellement observés avant installation/correction ou après altérations ; `reset-preuve.json` : restauration après altérations et ajout de doublons possédés.
- `corrections.json` : six tarifs et raccords natifs, classement strict, capacité réelle E-REDAC, matrice E-ABO, lecture équipe et motif A-VIR indépendants du catalogue.
- `clock.json` : générateur réellement exécuté aux 30/11/2026 23:59:59, 31/12/2026 23:59:59 et 01/01/2027 00:00:00 UTC ; échéance dans le mois, puis restauration à l’horloge réelle relue.
- `plan.json` : plan altéré par API Memberships, restauré par la même API avec décision d’accès et nettoyage relus. `reset-preuve.json` exerce également cette altération dans la recette de reset complète.
- `safety.json` : chargement et filtres MU vérifiés passivement ; fichier présent/filtres morts refusés, sentinelles de transport non appelées. Aucun envoi ou requête pour prouver leur interdiction.
- `integrite.json`, `local-tests.json` et `verification-finale.json` : décomptes réconciliés par code. Les red-* sont des échecs attendus de développement, pas la recette finale.

```bash
python -B -m unittest discover -s wp/tests/demo -p test_c09_profils.py -v
python -B wp/outils/demo/profils.py --site imagine-test-demo
python wp/outils/demo/profils.py --preuve readback --readback-only
python -B wp/tests/demo/c09-verifier.py
```

Le vérificateur complet altère intentionnellement uniquement les comptes C09 avant de les restaurer ; il ne faut pas l’exécuter pendant une lecture manuelle de ces comptes. Les sessions C09 sont révoquées à chaque reset. Aucun autre site, création/arrêt de site, Git, verrou ou rapport global n’est touché. Si un objet est étranger à C09, le script refuse de l’écraser.
