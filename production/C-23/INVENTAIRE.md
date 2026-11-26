# Inventaire C-23 — sorties et publics

**État courant après arbitrage de 19 h 30 :** `livraison-arbitrage1930` parcourt réellement les **136 voies × 14 publics** : **1 922 contrôles, 0 fuite, 0 échec, code 0**. La découverte lue fermée se teste comme état livré (`decouverte-fermee-livraison`, V-DEC-FIN sans droit), avec motif explicite du cas épuisé non joué. La recette distincte `decouverte-ouverte-epuisee-arbitrage1930` ouvre temporairement la politique du vrai personnage épuisé, joue les mêmes 136 voies puis restaure exactement. B06 reste inclus (cinq pages × sept sorties), preuve bornée supplémentaire 503 contrôles et 35 mutations de réponses détectées. Voir `A-VOIR.md`, `livraison-arbitrage1930-inventaire.json` et `manifest-arbitrage1930.json`. Les anciens inventaires V1/V2 restent historiques.

La cible et les coupe-circuits sont relus via l’outillage B-00/C-09 existant avant toute préparation. La commande visiteur ne connaît que l’origine fixe `http://192.168.129.32:8085`, refuse les chemins d’origine différente et les redirections extérieures. Tous ses appels sont GET ; elle ne charge pas les ressources tierces des pages.

## Sorties construites depuis C-08

| Lot / sortie | Retenu dans la recette | Motif / limite |
|---|---|---|
| C-08 — article réservé, article sans extrait, HTML source, contenus et extraits REST | Pages réservées inventoriées, REST item/collection/champs/contextes embed/edit, alias `rest_route`, révisions | Présence de l’objet réellement ciblé et témoins absents ; révisions/édition doivent rendre une erreur REST native 401/403, pas une page quelconque |
| C-08 — flux, oEmbed, vue intégrée, recherche, partage | RSS2, RSS, RDF, Atom, variante de flux, oEmbed JSON, `/embed/`, recherche HTML et deux recherches REST, balises de description/JSON-LD | Flux non vide et chemin d’un article réservé réellement présent ; métadonnées de partage réellement présentes. Le titre/formulaire qui réaffiche un terme recherché n’est pas assimilé à une fuite du corps |
| C-08 — variations de rendu | Aperçu, multipage, AMP inactif, prefetch, requête conditionnelle ; faux Googlebot avec X-Forwarded-For/X-Real-IP et faux Bingbot | Mêmes réponses inspectées ; aucune confiance accordée à un agent utilisateur seul |
| C-09 — personnages de test | Inventaire des 30 profils du catalogue, état des 27 comptes natifs, 13 sessions inspectées dont l’abonné actif ; deux publics sans compte | Les rôles, adhésions et abonnements ne sont jamais créés/réparés par C-23. Restauration des sessions et relecture C-09 existante |
| C-10 — écran de réglages | GET de `admin.php?page=imagine-reglages` et article témoin C-10 existant | Vérification de fermeture au public sans capacité, aucun POST de réglages dans la commande principale |
| C-11 — téléchargement PDF et médias | Cinq numéros : endpoints contrôlés, anciens chemins uploads/source, pièces jointes et médias REST ; variantes supplémentaires pour le T4 | Inverse actif sur les octets exacts du T4 ; inverse achat sur le T1. Aucune copie publique nouvellement créée |
| C-12 — découverte | V-DEC-FIN sans droit si découverte livrée fermée ; vrai épuisé si réglage lu ouvert | Rejeu normal sans politique forcée ; refus d’un personnage incompatible quand ouvert. Preuve ouverte/épuisée dans la recette nommée séparée, puis restauration exacte des réglages |
| C-13 — liste d’envoi | Écran exact `imagine-liste-envoi`, GET sans nonce de l’action d’export `imagine_exporter_liste_envoi` | Refus natif 403 attendu pour l’export ; pas de génération CSV, gel ou nouvel événement d’envoi |
| C-14 — achat au numéro | Vrai `P-NUMERO`, commandes et droits existants ; T1 lisible, T4 inaccessible | Aucune nouvelle commande ou transaction, pas de droit fictif fabriqué pour obtenir un vert |
| B-02 — Mon compte | Chemin natif réel `/my-account/`, lu comme chaque public | Pas le faux chemin `/mon-compte/` ; aucune modification de coordonnées, adresse ou abonnement |
| B-03 — mode lecture | HTML de l’article et variantes, présence/absence du texte dans la réponse serveur | Cette vue est le même HTML, transformé par CSS/stockage local : pas d’autre transport de texte à simuler |
| B-04 — accueil, numéro, kiosque, thématique, archives | Toutes ces listes, avec présence de leurs vrais objets/liens avant contrôle d’absence | L’accueil ne liste pas le témoin T4 principal, mais liste réellement des articles C-08/T4 dont les témoins sont contrôlés ; pas de réussite à vide |
| C-15 — échéances | Page `imagine-echeances` exacte, refus d’administration | Aucune échéance/action planifiée modifiée, pas de simulation du renouvellement |
| C-16 — commande pour un client | Page exacte `imagine-commandes`, refus d’administration | Le brouillon est privé, pas un canal public de texte d’article ; aucune nouvelle commande, aucun brouillon et aucune confirmation créés |
| C-17 — justificatifs | Page `imagine-justificatifs`, refus d’administration ; affichage compte existant | Les pièces ne sont pas des PDF de numéros ni du texte d’article. Pas de nouveau justificatif/upload ni de création de dossier pour cette recette ; les tests du lot documentaire ne sont pas remplacés par ce test de paywall |
| C-18 — extractions | Page exacte `imagine-extractions`, GET sans nonce de l’action exacte `imagine_extraire_abonnes` | Refus 403 attendu ; aucune extraction ou journalisation d’extraction réussie |
| C-19 — tableau de bord | Page exacte `imagine-tableau-de-bord` | Refus sans capacité ; aucune nouvelle statistique inventée |
| C-20 — ne pas renouveler | Même espace compte et HTML de lecture | Le périmètre réduit existant ne fournit pas de bouton ; aucune annulation ou modification de date de fin |
| C-21 — export et effacement | Écrans natifs `export-personal-data.php` / `erase-personal-data.php`, refus d’administration | Aucune demande d’export, email de confirmation, export effectif ou effacement. Ces opérations exigeraient une mutation et ne sont pas des canaux publics de texte réservé. Les garanties de données personnelles restent celles de C-21 |
| B-05 — partenaires | Accueil/bloc partenaire, archive, deux fiches natives | Réponses complètes inspectées sans suivre les liens commerciaux ni charger de service extérieur |
| C-22 — newsletters | `/nos-newsletters/` et section de préférences dans le compte | Aucun changement de consentement, pas d’appel Brevo, pas d’envoi ; les invariants d’identifiant/effacement restent couverts par C-22 |
| B-06 — espace coopérateurs | Cinq pages natives 2867–2871 ; HTML, REST item/alias/collection, oEmbed, embed et recherche | Cinq témoins fictifs temporaires hors commande GET, réception réelle par le coopérateur et absence pour les 13 publics non coopérateurs. Corps vides refusés comme preuve. 35 mutations de réponses HTTP distinctes détectées, puis octets et site restaurés. Le flux forcé retournant des posts n’est pas crédité comme flux de ces pages |
| WordPress — plans de site | Index, articles, numéros et pièces jointes | Leur désactivation native est constatée ; 404 obligatoire. Un plan activé sera contrôlé comme un vrai XML non vide par le même code, mais cette configuration activée n’a pas été exécutée ici |

### Témoins et corpus réellement lus

`inventaire-source.json` est lu sur la cible, pas recopié d’un ancien manifeste de lot : 27 articles publiés dont 22 réservés, cinq numéros/PDF et deux partenaires. Les 22 articles réservés portent déjà un témoin reconnu. L’inventaire refuse un nouvel article réservé sans témoin au lieu de l’ignorer.

Le témoin principal est `CONTENU_FICTIF_RESERVE_DEMO-2026-T4_1` (article 42, numéro 39, PDF 41). Les phrases C-08 (articles 81 et 82), C-10 (188) et C-12 sont conservées. Le T1 acheté (numéro 11) appartient légitimement à `P-NUMERO` ; ses témoins sont retirés de ses absences attendues et soumis à des contrôles inverses dédiés. Le texte T4 ne lui est jamais autorisé.

## Publics

Les cinq publics imposés sont : anonyme ; `V-INSCRIT` connecté ; `V-DEC-FIN` sans droit en découverte livrée fermée (vrai épuisé dans la recette séparée ouverte) ; `P-NUMERO` acheteur d’un autre numéro ; faux robot sans adresse vérifiée. S’ajoutent tous les personnages natifs de ce catalogue sans droit article/PDF sur le T4, sauf la découverte encore ouvrable explicitée ci-dessous : `A-VIR`, `A-SUSP`, `A-EXPIRE`, `P-OFFRANT`, `P-OFFERT`, `P-GEST`, `P-BENEF`, `P-PRO`, `P-COOP`.

La situation actuelle de chaque compte est relue par le vrai adaptateur, sans fabriquer les liens offert/groupé manquants. Les comptes de l’équipe et les abonnements qui ont un droit ne sont pas classés comme des refus. `A-CARTE` sert de contrôle inverse actif.

`V-DEC` est inventorié mais pas consommé : les GET d’un article désigné ouvriraient son état de découverte, ce qui violerait la lecture seule. Ce n’est pas le personnage du cas « découverte épuisée » demandé au brief : ce cas est couvert par `V-DEC-FIN`. La matrice ne prétend pas avoir exécuté une découverte fraîche ou la résolution inverse d’un vrai moteur.

### Inventaire réel des 30 profils C-09

Profil | Compte natif | Article T4 | PDF T4 | Recette HTTP C-23
---|---|---|---|---
V-ANON | non | — | — | anonyme
V-ROBOT | non | — | — | non vérifiable hors ligne
V-FAUX | non | — | — | faux robots
V-DEC | oui | fermé | fermé | découverte fraîche non consommée
V-DEC-FIN | oui | fermé | fermé | matrice de refus
V-INSCRIT | oui | fermé | fermé | matrice de refus
A-CARTE | oui | droit | droit | contrôle inverse actif
A-SEPA4 | oui | droit | droit | droit valide, hors publics sans droit
A-PAYPAL | oui | droit | droit | droit valide, hors publics sans droit
A-VIR | oui | fermé | fermé | matrice de refus
A-PAPIER | oui | droit | droit | droit valide, hors publics sans droit
A-GRACE | oui | droit | droit | droit valide, hors publics sans droit
A-SUSP | oui | fermé | fermé | matrice de refus
A-EXPIRE | oui | fermé | fermé | matrice de refus
A-NONRENOUV | oui | droit | droit | droit valide, hors publics sans droit
A-ETRANGER | oui | droit | droit | droit valide, hors publics sans droit
A-SANSMAIL | oui | droit | droit | droit valide, hors publics sans droit
A-ECHEANCE | oui | droit | droit | droit valide, hors publics sans droit
P-OFFRANT | oui | fermé | fermé | matrice de refus
P-OFFERT | oui | fermé | fermé | matrice de refus
P-GEST | oui | fermé | fermé | matrice de refus
P-BENEF | oui | fermé | fermé | matrice de refus
P-PRO | oui | fermé | fermé | matrice de refus
P-SOL-ATT | oui | droit | droit | droit valide, hors publics sans droit
P-SOL-OK | oui | droit | droit | droit valide, hors publics sans droit
P-NUMERO | oui | fermé | fermé | matrice de refus
P-COOP | oui | fermé | fermé | matrice de refus
E-ADMIN | oui | droit | droit | droit valide, hors publics sans droit
E-REDAC | oui | droit | droit | droit valide, hors publics sans droit
E-ABO | oui | droit | droit | droit valide, hors publics sans droit

## Limites restantes

- Pas de preuve de cache partagé de l’hébergeur ni de robots vérifiés par DNS/plages publiées sur cette démonstration : limites expressément prévues au brief.
- Plans de site fermés sur la configuration présente, pas de preuve sur leur configuration activée.
- Les exports, consentements, documents et autres commandes de gestion ne sont pas déclenchés par un test visiteur lecture seule. Leurs points d’entrée et refus sont inspectés ; C-23 ne remplace pas leurs régressions métier et de confidentialité.
- La restauration repose sur `finally` et un délai interne de 240 secondes pour le sous-processus HTTP. Ne pas tuer le lanceur avant son reçu de restauration ; un arrêt brutal de la machine ne peut pas exécuter un `finally`. L’incident de la première chaîne trop longue est expliqué, sans effacer ses reçus, dans `INCIDENTS.md`.
