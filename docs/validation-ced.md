# Validation de Ced — lundi 30 novembre 2026

Tenu par Claude, mis à jour à chaque passage. Dernière mise à jour : 28 novembre 2026, 7 h 30.

Un seul parcours, dans l'ordre d'importance, faisable en une heure. Tout se regarde sur le site de démonstration, **entièrement fictif** : `http://192.168.129.32:8085` (réseau local). Les comptes sont des profils de test ; leurs identifiants sont dans ton fichier hors dépôt `C:\Users\Ced\.imagine-demo\identifiants.json` (entrée `c09_accounts`), aucun n'est recopié ici. Pour le détail d'un lot : `production/<lot>/A-VOIR.md`.

Ce que tu valides, c'est ce qui se voit et ce qui se comprend : la structure, l'ordre, les libellés, le comportement. Pas le graphisme : il viendra des maquettes. Un « non » ou un « à revoir » en une ligne suffit, je le transforme en correction.

## Les questions qui comptent vraiment

Sept pour toi, puis celles d'Imagine.

1. **Tes cinq réponses de la nuit du 28, à confirmer.** Je te les avais proposées et tu as répondu « on peut freiner oui » sans les contredire ; je ne les tiens pas pour acquises tant que tu ne les as pas redites. **Aucune n'est encore appliquée : tu verras donc l'ancien état sur le site.**
   - l'étiquette « Réservé » retirée du kiosque ;
   - « Mon compte » au lieu de « Connexion » dans le menu pour un lecteur connecté ;
   - les quatre sections de l'écran de réglages remontées au-dessus du bouton « Enregistrer » ;
   - la date du statut de coopérateur à l'heure belge, en clair ;
   - à l'import, les contenus d'un type inconnu sont comptés, et le statut « vérifié » est refusé tant que tu n'as pas dit, type par type, garder ou vider.
2. **Import d'Imagine : la cinquième réponse demande de rouvrir le code de l'import, gelé depuis le 27.** Hermès attend une consigne pour le faire et ne touche à rien. Ouvre-t-on ce dégel, limité à ce seul contrôle, sur des archives fictives ? Défaut proposé : oui, comme un petit lot relu et vérifié, tes commandes inchangées. À savoir d'ici là : un import complet lancé avant ce changement donnerait un statut « vérifié » sans ce contrôle ; la répétition de la base seule (`--diagnose-database`) n'est pas concernée.
3. **Un lien dont la page n'est pas publiée disparaît, sans repli visible** (« S'abonner », « Soutenir », « Notre coopérative », « Nos newsletters » : accueil, pied de page, fin d'article). Défaut proposé : on garde, cela évite un lien mort.
4. **Mon compte ne propose pas de bouton « ne pas renouveler ».** Il dit seulement comment l'abonnement se renouvelle. Le bouton attend un staging vérifié avec Stripe en mode test, donc un accord de ta part le moment venu. Défaut : on attend.
5. **Justificatifs du tarif solidaire : le dossier ne garde que la catégorie, la date de fin et l'état, pas le document.** Défaut proposé : on garde (c'est le moins de données possible).
6. **Cookies : sept cookies d'attribution d'origine de WooCommerce sont posés dès la simple lecture d'une page.** L'objectif « aucun cookie en simple lecture » n'est donc pas tenu sur la démonstration, et c'est écrit comme tel. Rien n'a été éteint et aucun bandeau n'est construit : savoir s'ils demandent un consentement est une question pour Imagine et son conseil. La liste des quatorze cookies du site se lit sur `/gestion-des-cookies/` (annexe, C-32). Veux-tu, en attendant, éteindre l'attribution sur la démonstration ? Défaut : on ne touche à rien.
7. **Après ta validation, que relance-t-on en premier ?** La file de la démonstration est vide depuis le 28 à 5 h 26 ; celle de l'existant le sera après A-33 et T-03. En attente, non commencés : le lot des liens vers les archives (A-34) côté existant ; rien côté démonstration.

**Pour Imagine**, `docs/decisions.md` range cinquante-quatre questions, toutes déjà réglées sur un défaut prudent. Le classement en tête de la section « Ouvert — chez Imagine » sépare la quinzaine qui change ce qu'on construit (tarifs, accès découverte, abonnements groupés, rétractation, cookies, offre de bienvenue, import des abonnés hors ligne) de celles qui ne sont que des réglages.

## Le parcours (une heure)

### 1. Paywall et PDF — 8 minutes

| Adresse | Compte | Ce que tu dois voir |
|---|---|---|
| `/demo-2026-t1-reserve-1/` | aucun (navigation privée) | Le titre, le résumé, l'extrait et le bloc qui invite à se connecter ou à s'abonner ; jamais le texte complet. |
| la même | `a-carte` | Le texte complet, sans appel à l'abonnement en fin d'article. |
| la même | `p-numero` | Le texte complet, puis un appel à l'abonnement en fin d'article : il a acheté ce numéro, il n'est pas abonné. |
| `/demo-2026-t2-reserve-1/` | `p-numero` | L'achat d'un numéro n'ouvre que ce numéro : les deux articles ne se comportent pas de la même façon (`production/C-14/A-VOIR.md`). |
| `/?imagine_pdf=39` | aucun, puis `a-carte` | Anonyme : retour au numéro et bloc de connexion, jamais le fichier. Connecté : le PDF se télécharge. |

Lots : C-08, C-11, C-14, B-16 (appel de fin d'article), C-12 pour l'accès découverte (`/c12-decouverte-un/`, fermé par défaut). Question ouverte : aucune pour toi ; la forme de l'accès découverte est chez Imagine.

### 2. Mon compte — 8 minutes

| Adresse | Compte | Ce que tu dois voir |
|---|---|---|
| `/my-account/` | `a-carte`, puis `a-sepa4`, puis `a-susp` | Pour chacun, son abonnement, son état et comment il se renouvelle, dit en clair. Pas de bouton « ne pas renouveler ». |
| `/my-account/#mes-newsletters` | `a-carte` | « Mes newsletters » : des cases que le lecteur coche lui-même, aucune cochée d'office. |
| `/my-account/#ma-personnalisation` | `a-papier` | « Personnalisez ce que vous recevez » ; les questions affichées sont fictives. |
| `/my-account/view-order/126/` | `p-numero` | « Me rétracter », en deux étapes : une demande datée, sans aucun effet automatique. |

Lots : B-02, C-20, C-22, C-24, C-25. Question : la n° 4 ci-dessus. La rétractation (délai, point de départ, effets) est à faire valider par Imagine et son conseil.

### 3. Accueil et navigation — 8 minutes

| Adresse | Compte | Ce que tu dois voir |
|---|---|---|
| `/` | aucun | L'accueil dans l'ordre du cahier des charges, neuf sections ; la liste « Derniers articles » n'y est plus. |
| `/` | aucun | Le menu principal à huit entrées et le menu étendu des thématiques, trois articles illustrés par thématique. |
| `/` puis `/faq-service-client/` | aucun | Le pied de page en cinq zones, le même partout. |
| `/` | `a-carte` | Le menu d'un lecteur connecté : il affiche encore « Connexion » (ta réponse « Mon compte » n'est pas appliquée). |

Lots : B-14, B-13, B-15, B-00, B-01. Questions : les n° 1 et 3. La forme du menu étendu (panneau latéral ou grand déroulant) se décidera sur maquette.

### 4. Article et mode lecture — 6 minutes

| Adresse | Compte | Ce que tu dois voir |
|---|---|---|
| `/demo-2026-t1-ouvert/` | aucun | Un article libre : en-tête (titre, résumé, thématique, numéro, signature en texte sans lien), texte complet, pas d'appel final. |
| `/c08-article-reserve-article/` | `a-carte` | Le mode lecture : trois fonds, la position de lecture conservée ; l'en-tête et l'appel final disparaissent. |
| `/b11-article-medias-fictifs/` | aucun | Une vidéo et un podcast dans un article, sans lecteur ni vignette d'un service tiers. |

Lots : B-16, B-03, B-11 (B-12 est en annexe). Le contraste des trois fonds se revalidera après le choix des couleurs par le designer.

### 5. Kiosque et numéro — 5 minutes

| Adresse | Compte | Ce que tu dois voir |
|---|---|---|
| `/numeros/` | aucun | Le kiosque : couverture, titre, date. L'étiquette « Réservé » y est encore (ta réponse « retirer » n'est pas appliquée). |
| `/numeros/demo-2026-t4/` | aucun, puis `a-carte` | La page d'un numéro : couverture, sommaire, PDF et sommaire audio réservés à ceux qui y ont droit. |
| `/thematiques/demo-thematique-1/` | aucun | La page d'une thématique. |

Lots : B-04, B-11. Question : la n° 1.

### 6. Back-office : réglages — 5 minutes

| Adresse | Compte | Ce que tu dois voir |
|---|---|---|
| `/wp-admin/admin.php?page=imagine-reglages` | `e-admin` | L'écran de réglages : les réglages d'accès, puis, sous le bouton « Enregistrer », quatre sections (newsletters, questions de personnalisation, rétractation, « Comment nous avez-vous connus ? »). |

Lots : C-10, et les sections de C-22, C-24, C-25, C-27. Question : la n° 1 (remonter les quatre sections).

### 7. Back-office : liste d'envoi — 5 minutes

| Adresse | Compte | Ce que tu dois voir |
|---|---|---|
| `/wp-admin/admin.php?page=imagine-liste-envoi` | `e-abo` | La liste d'envoi d'un numéro : bénéficiaires, renouvellements, gel. Vérifie aussi que les menus « Imagine » ne se doublent pas. |

Lot : C-13. Les abonnements offerts et groupés n'y figurent pas : question chez Imagine.

### 8. Back-office : échéances — 5 minutes

| Adresse | Compte | Ce que tu dois voir |
|---|---|---|
| `/wp-admin/admin.php?page=imagine-echeances` | `e-abo` | L'écran des échéances : ce qui arrive à terme, les paiements en attente, les mandats à lancer. |
| `/wp-admin/admin.php?page=imagine-commandes` | `e-abo` | La commande passée pour un client. |

Lots : C-15, C-16.

### 9. Back-office : extractions — 3 minutes

| Adresse | Compte | Ce que tu dois voir |
|---|---|---|
| `/wp-admin/admin.php?page=imagine-extractions` | `e-abo` | Les extractions, avec leurs filtres (pays, code postal, mode de paiement) : une ligne par abonnement. |

Lot : C-18.

### 10. Back-office : tableau de bord — 3 minutes

| Adresse | Compte | Ce que tu dois voir |
|---|---|---|
| `/wp-admin/admin.php?page=imagine-tableau-de-bord` | `e-abo` (il faut les deux droits, extractions et échéances) | Des nombres seulement, aucune identité ; « par moyen de paiement » est grisé, sans chiffre. |

Lot : C-19.

## Annexe — si tu as le temps

Code clos, ton œil seulement. Dans l'ordre où je les regarderais.

| Lot | Adresse | Compte | En une phrase |
|---|---|---|---|
| C-17 Justificatifs du tarif solidaire | `/wp-admin/admin.php?page=imagine-justificatifs` | `e-abo` | Les demandes, leur état ; côté lecteur, `p-sol-att` et `p-sol-ok` dans Mon compte. Question n° 5. |
| C-30 Page « Bienvenue » et codes suivis | `/bienvenue/` | aucun | La page accueille et renvoie vers « S'abonner » ; aucun prix modifié, aucun avantage. |
| C-32 Les cookies du site | `/gestion-des-cookies/` | aucun (navigation privée) | Un tableau de quatorze cookies : nom, qui le pose, à quel geste, combien de temps, pour quoi. Aucun bandeau, aucun texte juridique. Question n° 6. |
| C-31 Adresses refusées à l'inscription | `/wp-admin/options-general.php?page=imagine-domaines-refuses` | `e-admin` | Un domaine par ligne ; liste vide, rien n'est refusé. À juger aussi : le ton du message de refus, qui ne dit pas « jetable » et propose une autre adresse (`production/C-31/A-VOIR.md`). |
| C-33 Aucun compte montré à un visiteur | `/?author=2`, `/wp-json/wp/v2/users`, `/?feed=rss2&withoutcomments=1` | aucun (navigation privée) | Page introuvable, erreur 404, et un flux signé du nom de l'auteur ou du site, jamais d'un compte. |
| C-28 Pack thématique | `/product/c28-pack-thematique-fictif/` | aucun | La fiche du pack et ce que l'achat ouvre, numéro par numéro. |
| C-27 « Comment nous avez-vous connus ? » | `/checkout/` | voir `production/C-27/A-VOIR.md` | La question après une commande ; sa section dans les réglages. |
| C-21 Export et effacement | `/wp-admin/export-personal-data.php` | `e-admin` | Les outils de confidentialité de WordPress, complétés. |
| C-29 Fiche du contact pour Brevo | `/wp-admin/admin.php?page=imagine-contact-brevo&compte=9` | `e-abo` | Ce qui partirait vers Brevo pour un contact ; rien n'est envoyé. |
| B-08 « Soutenir » et « Notre coopérative » | `/soutenir/`, `/notre-cooperative/`, `/proposer-un-sujet/` | aucun | Les deux pages et le formulaire de proposition de sujet ; le don est éteint. |
| B-06 Espace coopérateurs | `/espace-cooperateurs/` | `p-coop` | L'espace et ses quatre pages ; la date du statut est encore affichée brute. |
| B-07 Agenda | `/evenements/`, `/evenements/demo-events-1/` | aucun | La liste, la fiche, l'inscription simple, l'événement partenaire. |
| B-09 FAQ, pages légales, contact | `/faq-service-client/`, `/contact/`, `/gestion-des-cookies/` | aucun | Pages légales et FAQ vides exprès : les textes viendront d'Imagine. |
| B-10 Points de vente | `/points-de-vente/` | aucun | La recherche par localité ou code postal ; trente commerces fictifs, carte éteinte. |
| B-05 Partenaires | `/partenaires/` | aucun | La liste et la fiche d'un partenaire, l'étiquette « Partenariat ». |
| B-11 Saisie dans l'éditeur | `production/B-11/A-VOIR-contrat-V2.md` | un compte de rédaction | Un geste de trois lignes que l'automate n'a pas pu faire : saisir, enregistrer, recharger. |
| B-12 Vidéo collée dans un brouillon | `production/B-12/A-VOIR.md` | un compte de rédaction | Sur un brouillon à toi : un simple lien, aucun appel vers un service tiers. |

Rien à regarder : C-23 et C-26 (tests d'étanchéité), C-09 (les profils de test eux-mêmes).

## Ce qui n'est pas dans ce parcours

- **L'archive d'Imagine.** Rien à valider à l'œil : la répétition de la base seule, puis l'import, restent tes décisions (`ETAT.md`, point 1), avec la question n° 2.
- **Les outils de l'existant** (inventaires, mise à jour, nettoyage, répétition de bascule) : clos sur preuves, sur des sites fictifs. Ils attendent un staging d'Imagine vérifié.
- **Le graphisme** : il attend les maquettes.
