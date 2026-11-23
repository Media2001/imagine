# C09 — À voir sur la démonstration fictive

## Ouvrir

- Connexion : http://192.168.129.32:8085/wp-login.php
- Article réservé testé : http://192.168.129.32:8085/c08-article-reserve-article/ (ID 81).
- Administration : http://192.168.129.32:8085/wp-admin/ ; utilisateurs, commandes, abonnements et adhésions selon le rôle.
- Mots de passe : `C:\Users\Ced\.imagine-demo\identifiants.json`, entrée `c09_accounts`. Rien de secret dans le dépôt.

## Lecture des résultats

30 profils : 5 créés, 24 partiels, 1 impossible. **27 vrais comptes**, et non 30 : V-ANON, V-FAUX et V-ROBOT sont des scénarios de visite.
Objets C09 relus par les API natives : 13 commandes, 12 souscriptions, 14 adhésions, un plan (ID 86) et un produit Subscription privé à zéro (ID 87).
« Créé » signifie état de départ entièrement disponible ; « partiel » signifie compte et objets possibles créés, mais éléments manquants détaillés ci-dessous. Toutes les commandes sont non payées, à zéro, sans transaction et sans passerelle ; tous les renouvellements sont manuels. Cela ne démontre aucun débit ni paiement passé.
Les motifs ci-dessous proviennent du vrai `Imagine\Site\Paywall::decision` C08/C06, après lecture native Memberships/Subscriptions. 29 décisions relues et 27 connexions C09 réellement réalisées. V-ROBOT n’a pas de preuve positive inventée.

| Profil | État | Identifiant / ID | Objets natifs (C/S/M) | Ce qu’on voit | Décision réelle sur ID81 | Limite précise |
|---|---|---|---|---|---|---|
| V-ANON | créé | Sans compte | —/—/— | Sans session : extrait et invitation à se connecter. | `anonyme` ; fermé ; bloc `connexion` | Scénario de visite, pas un compte. |
| V-ROBOT | impossible | Sans compte | —/—/— | Aucun robot vérifié disponible sur cette démonstration hors ligne. | Non testable : robot vérifié indisponible | DNS désactivé par C08 ; aucune IP de robot vérifiée, aucune usurpation de preuve robot. |
| V-FAUX | créé | Sans compte | —/—/— | Sans session, UA Googlebot depuis une IP locale non vérifiée : extrait. | `anonyme` ; fermé ; bloc `connexion` | Scénario local de faux robot, jamais présenté comme un vrai robot vérifié. |
| V-DEC | partiel | `v-dec` / 6 | —/—/— | Compte utilisable, article fermé faute de raccord découverte. | `sans_droit` ; fermé ; bloc `abonnement` | Validation email et stockage/consommation découverte non raccordés à C08 ; aucun faux droit posé. |
| V-DEC-FIN | partiel | `v-dec-fin` / 7 | —/—/— | Compte utilisable sans abonnement ; article fermé. | `sans_droit` ; fermé ; bloc `abonnement` | Pas de parcours email ni de compteur découverte natif ; épuisement et bloc découverte non démontrés. |
| V-INSCRIT | partiel | `v-inscrit` / 8 | —/—/— | Compte client natif, sans commande ni adhésion, article fermé. | `sans_droit` ; fermé ; bloc `abonnement` | Aucun workflow de vérification email installé ; compte fictif utilisable mais vérification non attestée. |
| A-CARTE | partiel | `a-carte` / 9 | 88/89/90 | Abonnement et adhésion actifs : lecture complète. | `abonnement_actif` ; complet ; bloc `aucun` | Pas de carte, de paiement ni de renouvellement automatique : renouvellement manuel de sécurité ; compteur 3 numéros non raccordé. |
| A-SEPA4 | partiel | `a-sepa4` / 10 | 91/92/93 | Abonnement et adhésion actifs ; prochaine échéance native à 30 jours. | `abonnement_actif` ; complet ; bloc `aucun` | Pas de mandat SEPA ni de deux paiements inventés ; échéancier 2/4 et calendrier C05 non raccordés. Échéance native manuelle seulement. |
| A-PAYPAL | partiel | `a-paypal` / 11 | 94/95/96 | Abonnement et adhésion actifs : lecture complète. | `abonnement_actif` ; complet ; bloc `aucun` | Aucun accord de facturation PayPal ni jeton ; renouvellement manuel uniquement. |
| A-VIR | partiel | `a-vir` / 12 | 97/98/99 | Commande administrative on-hold, abonnement pending, adhésion pending : lecture fermée. | `suspendu` ; fermé ; bloc `regularisation` | État d'attente natif créé ; méthode de paiement volontairement vide, aucun compte bancaire. C08 renvoie suspendu pour une souscription pending, pas virement_non_valide. |
| A-PAPIER | partiel | `a-papier` / 13 | 100/101/102 | Abonnement et adhésion actifs ; échéance manuelle native ce mois-ci. | `abonnement_actif` ; complet ; bloc `aucun` | Aucun mandat papier ou IBAN, ni mode métier domiciliation ; export bancaire et lancement de prélèvement absents. |
| A-GRACE | partiel | `a-grace` / 14 | 103/104/105 | Souscription on-hold, adhésion paused, fenêtre UTC bornée : lecture et bandeau de régularisation. | `delai_grace` ; complet ; bloc `regularisation` | Fenêtre de fixture explicite de maintenant moins 1 jour à plus 2 jours ; aucune durée métier arrêtée ni rejet bancaire réel simulé. |
| A-SUSP | partiel | `a-susp` / 15 | 106/107/108 | Souscription on-hold, adhésion paused, grâce déjà finie : lecture fermée. | `suspendu` ; fermé ; bloc `regularisation` | Aucun rejet bancaire inventé ; sortie réelle de la liste d'envoi non démontrable sans son adaptateur natif. |
| A-EXPIRE | créé | `a-expire` / 16 | 109/110/111 | Souscription et adhésion expirées hier, sans prochain paiement : lecture fermée. | `expire` ; fermé ; bloc `abonnement` | État administratif fictif, aucun historique de paiement ajouté. |
| A-NONRENOUV | partiel | `a-nonrenouv` / 17 | 112/113/114 | Souscription pending-cancel jusqu'au terme dans 30 jours, adhésion active : lecture complète. | `abonnement_actif` ; complet ; bloc `aucun` | Fin de renouvellement native démontrée, mais le compteur métier 1 numéro restant n'est pas raccordé. |
| A-ETRANGER | partiel | `a-etranger` / 18 | 115/116/117 | Abonnement actif, adresse fictive en France et ligne de port visible à zéro euro de fixture. | `abonnement_actif` ; complet ; bloc `aucun` | Supplément de port non chiffré pour ne pas décider le tarif ; aucun recalcul métier raccordé. |
| A-SANSMAIL | partiel | `a-sansmail` / 19 | 118/119/120 | Abonnement actif, adresse technique a-sansmail@example.org et adresse postale fictive. | `abonnement_actif` ; complet ; bloc `aucun` | Pas de donnée personnelle ; exclusion individuelle des emails et inclusion liste postale non raccordées. Le coupe-circuit email global ne prouve pas cette exclusion. |
| A-ECHEANCE | partiel | `a-echeance` / 20 | 121/122/123 | Abonnement actif, terme natif à 30 jours et prochain paiement manuel planifié à 29 jours (avant le terme). | `abonnement_actif` ; complet ; bloc `aucun` | Renouvellement manuel de sécurité ; automate de rappel et marqueur non-envoyé non raccordés, aucun email envoyé. |
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
| E-REDAC | créé | `e-redac` / 31 | —/—/— | Rôle rédaction natif : contenus, numéros et calendrier de parution ; lecture complète. | `equipe` ; complet ; bloc `aucun` | Rôle WordPress editor, sans accès aux réglages techniques ni gestion commerciale. |
| E-ABO | partiel | `e-abo` / 32 | —/—/— | Shop manager natif : commandes et adhésions ; article réservé fermé selon C08. | `sans_droit` ; fermé ; bloc `abonnement` | Les écrans métier échéances, justificatifs, liste d'envoi et extractions ne sont pas tous raccordés ; shop_manager donne aussi des capacités éditoriales natives, à revoir avant production. |

## Profils et documentation à préciser — propositions seulement

Aucun fichier de `docs/` n’a été modifié.

1. **V-ANON/V-ROBOT/V-FAUX** : distinguer explicitement scénarios de requête et comptes. Définir la preuve DNS/IP pour V-ROBOT ; hors ligne, il reste impossible, jamais remplacé par une UA ou une IP déclarée.
2. **V-DEC/V-DEC-FIN/V-INSCRIT** : préciser la preuve de vérification email, la forme de découverte choisie, ses dates/compteurs et le raccord natif. Un compte WordPress utilisable ne prouve pas un email vérifié.
3. **A-CARTE/A-SEPA4/A-PAYPAL/A-PAPIER/A-ECHEANCE** : séparer l’état de lecture démontrable des mandats/accords et paiements réellement prouvés. Aucun 2/4 payé ni accord PayPal ne doit être déclaré ici ; les prochaines actions natives manuelles sont vérifiées. A-ECHEANCE a son terme à J+30 et une action à J+29 car WCS exige le prochain paiement avant la fin.
4. **A-VIR** : définir le motif attendu pour pending Subscriptions ; C08 renvoie actuellement suspendu malgré adhésion pending. Ne pas le présenter comme virement_non_valide. Le mode de règlement reste vide sur la démo.
5. **A-GRACE/A-SUSP/A-NONRENOUV/A-SANSMAIL** : distinguer fenêtre UTC de fixture d’une durée métier ; préciser le raccord des compteurs de numéros et de la liste postale. Le blocage global des emails ne prouve pas l’exclusion individuelle d’A-SANSMAIL.
6. **A-ETRANGER** : préciser pays, barème et supplément avant d’affirmer « supplément appliqué ». La ligne de port à zéro actuelle n’est pas un vrai supplément.
7. **P-OFFRANT/P-OFFERT/P-GEST/P-BENEF** : préciser les objets/relations du module offert et de Teams, leurs propriétaires et bénéficiaires. Aucun droit indépendant substitutif n’est accordé en attendant ces raccords.
8. **P-PRO** : remplacer « numéro valide » par « cohérence locale » ou « existence BCE attestée » selon la preuve voulue. 0000000097 est uniquement une entrée synthétique cohérente, pas une entreprise attestée ni un attribut de compte raccordé.
9. **P-SOL-ATT/P-SOL-OK** : préciser dépôt, décision, tarif et durée de validité du justificatif séparément de la fin d’adhésion. Une adhésion native de démonstration ne remplace pas une validation de justificatif.
10. **P-NUMERO/P-COOP** : définir la preuve d’achat et le rattachement après achat, puis les adaptateurs achat/CoopHub. La commande en attente n’est pas un achat acquis ; aucun attribut coopérateur non raccordé n’est maquillé en droit.
11. **E-ABO** : définir un rôle administratif dédié et sa matrice de capacités. Le rôle Woo shop_manager actuel est partiel et plus large (capacités éditoriales natives) ; C08 ne le considère pas comme équipe de lecture. Ne pas le réutiliser tel quel en production.
12. **Données communes** : B00 fournit cinq numéros de 2026 avec articles et PDF ; ni le calendrier sur trois ans ni la grille native trois tarifs × une/quatre fois ne sont complets. Le produit C09 à zéro est une fixture privée, pas une grille commerciale validée. Ces limites n’ont pas été masquées par des montants ou des compteurs inventés.

## Preuves et rejeu

- `installation.json` : première installation réelle historique ; `relance.json`, `reset.json` et `readback.json` : contrôles après les sources finales. Les ID principaux restent identiques.
- `readback.json` : objets natifs et décisions nominatives ; `http.json` : connexions, témoin de contenu et blocs, sans cookie/nonce/mot de passe enregistré.
- `red-runtime.json`, `red-safety.json`, `red-reset.json` : échecs réellement observés avant installation/correction ou après altérations ; `reset-preuve.json` : restauration après altérations et ajout de doublons possédés.
- `safety.json`, `integrite.json`, `references.md`, `local-tests.json` et `verification-finale.json`.

```bash
python wp/outils/demo/profils.py --site imagine-test-demo
python wp/outils/demo/profils.py --preuve readback --readback-only
python wp/tests/demo/c09-verifier.py
```

Le vérificateur complet altère intentionnellement uniquement les comptes C09 avant de les restaurer ; il ne faut pas l’exécuter pendant une lecture manuelle de ces comptes. Les sessions C09 sont révoquées à chaque reset. Aucun autre site, création/arrêt de site, Git, verrou ou rapport global n’est touché. Si un objet est étranger à C09, le script refuse de l’écraser.
