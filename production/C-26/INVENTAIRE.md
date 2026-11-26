# C26 — Inventaire des sorties, une ligne chacune

Source : inventaire natif relu sur `imagine-test-demo` ; bootstrap courant comparé avant les essais. Aucun envoi, transport extérieur ou changement du code métier.

**131 sorties HTTP**, chacune jouée sur les **15 publics** : anonyme, connecte-sans-abonnement, decouverte-fermee-livraison, acheteur-autre-numero, faux-robot, profil-a-vir, profil-a-susp, profil-a-expire, profil-p-offrant, profil-p-offert, profil-p-gest, profil-p-benef, profil-p-pro, profil-p-coop, abonne-actif.

Tous sont des tiers de V-DEC, propriétaire fictif des données C26. Abonné actif ou coopérateur ne donne aucun droit sur ses réponses, demandes et inscriptions. T = texte réservé d’un numéro non possédé ; D = donnée privée d’un autre compte. Les droits C14 sont respectés. Les surfaces publiques ne sont pas artificiellement classées privées : leur contenu doit exister sans embarquer T ou D.

Les pages publiques exigent le bon h1, les recherches publiques un vrai lien de résultat vers le bon objet, les collections l’ID attendu, le flux événementiel des entrées et liens d’événements, les oEmbed un objet riche au bon titre. Les refus REST sont des erreurs JSON natives ; les recherches privées ont le résultat vide natif attendu, la réflexion étant masquée seulement aux positions exactes.

## Sorties nouvelles et surfaces communes réinspectées

Nom | Famille | Voie | Chemin GET exact | Risques / public
---|---|---|---|---
cooperative-3115-page | cooperative | page | `/notre-cooperative/` | T + D ; 15 tiers
cooperative-3115-rest | cooperative | rest | `/wp-json/wp/v2/pages/3115` | T + D ; 15 tiers
cooperative-3115-collection | cooperative | rest | `/wp-json/wp/v2/pages?include=3115` | T + D ; 15 tiers
cooperative-3115-alias | cooperative | rest | `/?rest_route=/wp/v2/pages/3115` | T + D ; 15 tiers
cooperative-3115-oembed | cooperative | oembed | `/wp-json/oembed/1.0/embed?url=http%3A%2F%2F192.168.129.32%3A8085%2Fnotre-cooperative%2F` | T + D ; 15 tiers
cooperative-3115-embed | cooperative | embed | `/notre-cooperative/embed/` | T + D ; 15 tiers
cooperative-3115-search | cooperative | search | `/?s=Notre+coop%C3%A9rative&post_type=page` | T + D ; 15 tiers
cooperative-3116-page | cooperative | page | `/soutenir/` | T + D ; 15 tiers
cooperative-3116-rest | cooperative | rest | `/wp-json/wp/v2/pages/3116` | T + D ; 15 tiers
cooperative-3116-collection | cooperative | rest | `/wp-json/wp/v2/pages?include=3116` | T + D ; 15 tiers
cooperative-3116-alias | cooperative | rest | `/?rest_route=/wp/v2/pages/3116` | T + D ; 15 tiers
cooperative-3116-oembed | cooperative | oembed | `/wp-json/oembed/1.0/embed?url=http%3A%2F%2F192.168.129.32%3A8085%2Fsoutenir%2F` | T + D ; 15 tiers
cooperative-3116-embed | cooperative | embed | `/soutenir/embed/` | T + D ; 15 tiers
cooperative-3116-search | cooperative | search | `/?s=Soutenir&post_type=page` | T + D ; 15 tiers
cooperative-3117-page | cooperative | page | `/proposer-un-sujet/` | T + D ; 15 tiers
cooperative-3117-rest | cooperative | rest | `/wp-json/wp/v2/pages/3117` | T + D ; 15 tiers
cooperative-3117-collection | cooperative | rest | `/wp-json/wp/v2/pages?include=3117` | T + D ; 15 tiers
cooperative-3117-alias | cooperative | rest | `/?rest_route=/wp/v2/pages/3117` | T + D ; 15 tiers
cooperative-3117-oembed | cooperative | oembed | `/wp-json/oembed/1.0/embed?url=http%3A%2F%2F192.168.129.32%3A8085%2Fproposer-un-sujet%2F` | T + D ; 15 tiers
cooperative-3117-embed | cooperative | embed | `/proposer-un-sujet/embed/` | T + D ; 15 tiers
cooperative-3117-search | cooperative | search | `/?s=Proposer+un+sujet&post_type=page` | T + D ; 15 tiers
cooperative-3118-page | cooperative | page | `/notre-cooperative/projet-editorial-et-manifeste/` | T + D ; 15 tiers
cooperative-3118-rest | cooperative | rest | `/wp-json/wp/v2/pages/3118` | T + D ; 15 tiers
cooperative-3118-collection | cooperative | rest | `/wp-json/wp/v2/pages?include=3118` | T + D ; 15 tiers
cooperative-3118-alias | cooperative | rest | `/?rest_route=/wp/v2/pages/3118` | T + D ; 15 tiers
cooperative-3118-oembed | cooperative | oembed | `/wp-json/oembed/1.0/embed?url=http%3A%2F%2F192.168.129.32%3A8085%2Fnotre-cooperative%2Fprojet-editorial-et-manifeste%2F` | T + D ; 15 tiers
cooperative-3118-embed | cooperative | embed | `/notre-cooperative/projet-editorial-et-manifeste/embed/` | T + D ; 15 tiers
cooperative-3118-search | cooperative | search | `/?s=projet+%C3%A9ditorial+et+manifeste&post_type=page` | T + D ; 15 tiers
cooperative-3119-page | cooperative | page | `/notre-cooperative/charte-independance/` | T + D ; 15 tiers
cooperative-3119-rest | cooperative | rest | `/wp-json/wp/v2/pages/3119` | T + D ; 15 tiers
cooperative-3119-collection | cooperative | rest | `/wp-json/wp/v2/pages?include=3119` | T + D ; 15 tiers
cooperative-3119-alias | cooperative | rest | `/?rest_route=/wp/v2/pages/3119` | T + D ; 15 tiers
cooperative-3119-oembed | cooperative | oembed | `/wp-json/oembed/1.0/embed?url=http%3A%2F%2F192.168.129.32%3A8085%2Fnotre-cooperative%2Fcharte-independance%2F` | T + D ; 15 tiers
cooperative-3119-embed | cooperative | embed | `/notre-cooperative/charte-independance/embed/` | T + D ; 15 tiers
cooperative-3119-search | cooperative | search | `/?s=charte+d%27ind%C3%A9pendance&post_type=page` | T + D ; 15 tiers
cooperative-3120-page | cooperative | page | `/notre-cooperative/charte-ia/` | T + D ; 15 tiers
cooperative-3120-rest | cooperative | rest | `/wp-json/wp/v2/pages/3120` | T + D ; 15 tiers
cooperative-3120-collection | cooperative | rest | `/wp-json/wp/v2/pages?include=3120` | T + D ; 15 tiers
cooperative-3120-alias | cooperative | rest | `/?rest_route=/wp/v2/pages/3120` | T + D ; 15 tiers
cooperative-3120-oembed | cooperative | oembed | `/wp-json/oembed/1.0/embed?url=http%3A%2F%2F192.168.129.32%3A8085%2Fnotre-cooperative%2Fcharte-ia%2F` | T + D ; 15 tiers
cooperative-3120-embed | cooperative | embed | `/notre-cooperative/charte-ia/embed/` | T + D ; 15 tiers
cooperative-3120-search | cooperative | search | `/?s=charte+IA&post_type=page` | T + D ; 15 tiers
cooperative-3121-page | cooperative | page | `/notre-cooperative/barometre-egalite-diversite/` | T + D ; 15 tiers
cooperative-3121-rest | cooperative | rest | `/wp-json/wp/v2/pages/3121` | T + D ; 15 tiers
cooperative-3121-collection | cooperative | rest | `/wp-json/wp/v2/pages?include=3121` | T + D ; 15 tiers
cooperative-3121-alias | cooperative | rest | `/?rest_route=/wp/v2/pages/3121` | T + D ; 15 tiers
cooperative-3121-oembed | cooperative | oembed | `/wp-json/oembed/1.0/embed?url=http%3A%2F%2F192.168.129.32%3A8085%2Fnotre-cooperative%2Fbarometre-egalite-diversite%2F` | T + D ; 15 tiers
cooperative-3121-embed | cooperative | embed | `/notre-cooperative/barometre-egalite-diversite/embed/` | T + D ; 15 tiers
cooperative-3121-search | cooperative | search | `/?s=barom%C3%A8tre+%C3%A9galit%C3%A9-diversit%C3%A9&post_type=page` | T + D ; 15 tiers
cooperative-3122-page | cooperative | page | `/notre-cooperative/equipe/` | T + D ; 15 tiers
cooperative-3122-rest | cooperative | rest | `/wp-json/wp/v2/pages/3122` | T + D ; 15 tiers
cooperative-3122-collection | cooperative | rest | `/wp-json/wp/v2/pages?include=3122` | T + D ; 15 tiers
cooperative-3122-alias | cooperative | rest | `/?rest_route=/wp/v2/pages/3122` | T + D ; 15 tiers
cooperative-3122-oembed | cooperative | oembed | `/wp-json/oembed/1.0/embed?url=http%3A%2F%2F192.168.129.32%3A8085%2Fnotre-cooperative%2Fequipe%2F` | T + D ; 15 tiers
cooperative-3122-embed | cooperative | embed | `/notre-cooperative/equipe/embed/` | T + D ; 15 tiers
cooperative-3122-search | cooperative | search | `/?s=%C3%A9quipe&post_type=page` | T + D ; 15 tiers
cooperative-3123-page | cooperative | page | `/notre-cooperative/gouvernance/` | T + D ; 15 tiers
cooperative-3123-rest | cooperative | rest | `/wp-json/wp/v2/pages/3123` | T + D ; 15 tiers
cooperative-3123-collection | cooperative | rest | `/wp-json/wp/v2/pages?include=3123` | T + D ; 15 tiers
cooperative-3123-alias | cooperative | rest | `/?rest_route=/wp/v2/pages/3123` | T + D ; 15 tiers
cooperative-3123-oembed | cooperative | oembed | `/wp-json/oembed/1.0/embed?url=http%3A%2F%2F192.168.129.32%3A8085%2Fnotre-cooperative%2Fgouvernance%2F` | T + D ; 15 tiers
cooperative-3123-embed | cooperative | embed | `/notre-cooperative/gouvernance/embed/` | T + D ; 15 tiers
cooperative-3123-search | cooperative | search | `/?s=gouvernance&post_type=page` | T + D ; 15 tiers
cooperative-3124-page | cooperative | page | `/notre-cooperative/imagine-coop/` | T + D ; 15 tiers
cooperative-3124-rest | cooperative | rest | `/wp-json/wp/v2/pages/3124` | T + D ; 15 tiers
cooperative-3124-collection | cooperative | rest | `/wp-json/wp/v2/pages?include=3124` | T + D ; 15 tiers
cooperative-3124-alias | cooperative | rest | `/?rest_route=/wp/v2/pages/3124` | T + D ; 15 tiers
cooperative-3124-oembed | cooperative | oembed | `/wp-json/oembed/1.0/embed?url=http%3A%2F%2F192.168.129.32%3A8085%2Fnotre-cooperative%2Fimagine-coop%2F` | T + D ; 15 tiers
cooperative-3124-embed | cooperative | embed | `/notre-cooperative/imagine-coop/embed/` | T + D ; 15 tiers
cooperative-3124-search | cooperative | search | `/?s=Imagine+COOP&post_type=page` | T + D ; 15 tiers
agenda-2971-page | agenda | page | `/evenements/b07-rencontre-passee/` | T + D ; 15 tiers
agenda-2971-rest | agenda | rest | `/wp-json/wp/v2/imagine_evenement/2971` | T + D ; 15 tiers
agenda-2971-collection | agenda | rest | `/wp-json/wp/v2/imagine_evenement?include=2971` | T + D ; 15 tiers
agenda-2971-alias | agenda | rest | `/?rest_route=/wp/v2/imagine_evenement/2971` | T + D ; 15 tiers
agenda-2971-oembed | agenda | oembed | `/wp-json/oembed/1.0/embed?url=http%3A%2F%2F192.168.129.32%3A8085%2Fevenements%2Fb07-rencontre-passee%2F` | T + D ; 15 tiers
agenda-2971-embed | agenda | embed | `/evenements/b07-rencontre-passee/embed/` | T + D ; 15 tiers
agenda-2971-search | agenda | search | `/?s=Rencontre+pass%C3%A9e+des+Horizons+%E2%80%94+fictive&post_type=imagine_evenement` | T + D ; 15 tiers
agenda-2970-page | agenda | page | `/evenements/b07-partenaire-fictif/` | T + D ; 15 tiers
agenda-2970-rest | agenda | rest | `/wp-json/wp/v2/imagine_evenement/2970` | T + D ; 15 tiers
agenda-2970-collection | agenda | rest | `/wp-json/wp/v2/imagine_evenement?include=2970` | T + D ; 15 tiers
agenda-2970-alias | agenda | rest | `/?rest_route=/wp/v2/imagine_evenement/2970` | T + D ; 15 tiers
agenda-2970-oembed | agenda | oembed | `/wp-json/oembed/1.0/embed?url=http%3A%2F%2F192.168.129.32%3A8085%2Fevenements%2Fb07-partenaire-fictif%2F` | T + D ; 15 tiers
agenda-2970-embed | agenda | embed | `/evenements/b07-partenaire-fictif/embed/` | T + D ; 15 tiers
agenda-2970-search | agenda | search | `/?s=Rencontre+partenaire+des+Nuages+%E2%80%94+fictive&post_type=imagine_evenement` | T + D ; 15 tiers
agenda-47-page | agenda | page | `/evenements/demo-events-2/` | T + D ; 15 tiers
agenda-47-rest | agenda | rest | `/wp-json/wp/v2/imagine_evenement/47` | T + D ; 15 tiers
agenda-47-collection | agenda | rest | `/wp-json/wp/v2/imagine_evenement?include=47` | T + D ; 15 tiers
agenda-47-alias | agenda | rest | `/?rest_route=/wp/v2/imagine_evenement/47` | T + D ; 15 tiers
agenda-47-oembed | agenda | oembed | `/wp-json/oembed/1.0/embed?url=http%3A%2F%2F192.168.129.32%3A8085%2Fevenements%2Fdemo-events-2%2F` | T + D ; 15 tiers
agenda-47-embed | agenda | embed | `/evenements/demo-events-2/embed/` | T + D ; 15 tiers
agenda-47-search | agenda | search | `/?s=Atelier+des+possibles+invent%C3%A9s&post_type=imagine_evenement` | T + D ; 15 tiers
agenda-46-page | agenda | page | `/evenements/demo-events-1/` | T + D ; 15 tiers
agenda-46-rest | agenda | rest | `/wp-json/wp/v2/imagine_evenement/46` | T + D ; 15 tiers
agenda-46-collection | agenda | rest | `/wp-json/wp/v2/imagine_evenement?include=46` | T + D ; 15 tiers
agenda-46-alias | agenda | rest | `/?rest_route=/wp/v2/imagine_evenement/46` | T + D ; 15 tiers
agenda-46-oembed | agenda | oembed | `/wp-json/oembed/1.0/embed?url=http%3A%2F%2F192.168.129.32%3A8085%2Fevenements%2Fdemo-events-1%2F` | T + D ; 15 tiers
agenda-46-embed | agenda | embed | `/evenements/demo-events-1/embed/` | T + D ; 15 tiers
agenda-46-search | agenda | search | `/?s=Rencontre+au+village+Imaginaire&post_type=imagine_evenement` | T + D ; 15 tiers
agenda-flux | agenda | feed | `/?feed=rss2&post_type=imagine_evenement&posts_per_rss=100` | T + D ; 15 tiers
agenda-prive-page | agenda | private-page | `/?p=3158` | T + D ; 15 tiers
agenda-prive-rest | agenda | rest-denied | `/wp-json/wp/v2/imagine_inscription/3158` | T + D ; 15 tiers
agenda-prive-collection | agenda | rest-denied | `/wp-json/wp/v2/imagine_inscription` | T + D ; 15 tiers
agenda-prive-feed | agenda | private-feed | `/?feed=rss2&post_type=imagine_inscription` | T + D ; 15 tiers ; repli natif articles publics, pas flux privé non vide
agenda-prive-search | agenda | search | `/?s=C26_AGENDA_FICTIF` | T + D ; 15 tiers
agenda-admin | agenda | admin | `/wp-admin/edit.php?post_type=imagine_inscription` | T + D ; 15 tiers
agenda-admin-detail | agenda | admin | `/wp-admin/post.php?post=3158&action=edit` | T + D ; 15 tiers
sujet-prive-page | sujet | private-page | `/?p=3159` | T + D ; 15 tiers
sujet-prive-rest | sujet | rest-denied | `/wp-json/wp/v2/imagine_sujet/3159` | T + D ; 15 tiers
sujet-prive-collection | sujet | rest-denied | `/wp-json/wp/v2/imagine_sujet` | T + D ; 15 tiers
sujet-prive-feed | sujet | private-feed | `/?feed=rss2&post_type=imagine_sujet` | T + D ; 15 tiers ; repli natif articles publics, pas flux privé non vide
sujet-prive-search | sujet | search | `/?s=C26_SUJET_FICTIF` | T + D ; 15 tiers
sujet-admin | sujet | admin | `/wp-admin/edit.php?post_type=imagine_sujet` | T + D ; 15 tiers
sujet-admin-detail | sujet | admin | `/wp-admin/post.php?post=3159&action=edit` | T + D ; 15 tiers
personnalisation-compte | personnalisation | account | `/my-account/` | T + D ; 15 tiers
personnalisation-utilisateur-rest | personnalisation | rest-denied | `/wp-json/wp/v2/users/6?context=edit` | T + D ; 15 tiers
personnalisation-reglages | personnalisation | admin | `/wp-admin/admin.php?page=imagine-reglages` | T + D ; 15 tiers
personnalisation-action-GET | personnalisation | refusal | `/wp-admin/admin-post.php?action=imagine_personnalisation` | T + D ; 15 tiers
retractation-compte-tiers | retractation | account | `/my-account/?imagine_retractation=3160` | T + D ; 15 tiers
retractation-commande-tiers | retractation | account | `/my-account/view-order/3160/` | T + D ; 15 tiers
retractation-admin | retractation | admin | `/wp-admin/admin.php?page=imagine-retractations` | T + D ; 15 tiers
retractation-rest | retractation | rest-denied | `/wp-json/wc/v3/orders/3160` | T + D ; 15 tiers
sujet-action-GET | sujet | refusal | `/wp-admin/admin-post.php?action=imagine_sujet` | T + D ; 15 tiers
agenda-action-GET | agenda | refusal | `/wp-admin/admin-post.php?action=imagine_agenda` | T + D ; 15 tiers
privacy-export-personal-data | personnalisation | admin | `/wp-admin/export-personal-data.php` | T + D ; 15 tiers
privacy-erase-personal-data | personnalisation | admin | `/wp-admin/erase-personal-data.php` | T + D ; 15 tiers
commun-accueil | commun | common-page | `/` | T + D ; 15 tiers
commun-flux-articles | commun | common-feed | `/?feed=rss2&posts_per_rss=100` | T + D ; 15 tiers
commun-rest-articles | commun | rest | `/wp-json/wp/v2/posts?per_page=100` | T + D ; 15 tiers
commun-rest-pages | commun | rest | `/wp-json/wp/v2/pages?per_page=100` | T + D ; 15 tiers
personnalisation-search | personnalisation | search | `/?s=2001-01-01T01%3A26%3A24Z` | T + D ; 15 tiers
retractation-search | retractation | search | `/?s=C26_RETRACTATION_FICTIF` | T + D ; 15 tiers

## Privacy : vrais callbacks enregistrés, en lecture seule

Nom | Famille | Voie et registre natif | Risque / publics
---|---|---|---
privacy-agenda | agenda | callback `imagine-agenda` → `AgendaConfidentialite::exporter()` | D ; 15 tiers + propriétaire positif
privacy-personnalisation | personnalisation | callback `imagine-personnalisation` → `PersonnalisationConfidentialite::exporter()` | D ; 15 tiers + propriétaire positif
privacy-retractation | retractation | callback `imagine-retractation` → `RetractationConfidentialite::exporter()` | D ; 15 tiers + propriétaire positif
privacy-sujet | sujet | callback `imagine-sujets` → `SujetConfidentialite::exporter()` | D ; 15 tiers + propriétaire positif

Pas de demande native ni d’archive/email généré. Les réponses privées ne sont pas conservées dans les reçus : seulement empreintes et verdicts. Aucun effaceur n’est exécuté par la matrice ; leurs pages administratives sont lues en GET et refusées. Les types privés n’ont pas de REST/oEmbed/flux privé natif : les URL risquées sont sondées sans inventer de surface privée. Les callbacks positifs prouvent que les données existent.

## Pages coopérateurs maintenues dans C23 et soumises à relecture C26

Ces **35 voies sont déjà comprises dans les 136 voies / 1 922 contrôles C23** : ne pas les ajouter une seconde fois aux sorties nouvelles. Les 14 publics C23 sont ceux ci-dessus moins abonne-actif ; P-COOP est l’inverse autorisé, les 13 autres sont refusés. Risque : contenu de l’espace réservé, sans droit d’article. Aucun faux flux de pages n’est crédité.

Nom | Page | Voie | Chemin GET exact | Publics
---|---|---|---|---
b06-2867-html | 2867 | html | `/espace-cooperateurs/` | 13 refus + P-COOP inverse
b06-2867-rest | 2867 | rest | `/wp-json/wp/v2/pages/2867` | 13 refus + P-COOP inverse
b06-2867-rest-route | 2867 | rest-route | `/?rest_route=/wp/v2/pages/2867` | 13 refus + P-COOP inverse
b06-2867-collection | 2867 | collection | `/wp-json/wp/v2/pages?include=2867` | 13 refus + P-COOP inverse
b06-2867-oembed | 2867 | oembed | `/wp-json/oembed/1.0/embed?url=http%3A%2F%2F192.168.129.32%3A8085%2Fespace-cooperateurs%2F` | 13 refus + P-COOP inverse
b06-2867-embed | 2867 | embed | `/espace-cooperateurs/embed/` | 13 refus + P-COOP inverse
b06-2867-recherche | 2867 | recherche | `/?s=Espace+coop%C3%A9rateurs&post_type=page` | 13 refus + P-COOP inverse
b06-2868-html | 2868 | html | `/espace-cooperateurs/appels-a-benevolat/` | 13 refus + P-COOP inverse
b06-2868-rest | 2868 | rest | `/wp-json/wp/v2/pages/2868` | 13 refus + P-COOP inverse
b06-2868-rest-route | 2868 | rest-route | `/?rest_route=/wp/v2/pages/2868` | 13 refus + P-COOP inverse
b06-2868-collection | 2868 | collection | `/wp-json/wp/v2/pages?include=2868` | 13 refus + P-COOP inverse
b06-2868-oembed | 2868 | oembed | `/wp-json/oembed/1.0/embed?url=http%3A%2F%2F192.168.129.32%3A8085%2Fespace-cooperateurs%2Fappels-a-benevolat%2F` | 13 refus + P-COOP inverse
b06-2868-embed | 2868 | embed | `/espace-cooperateurs/appels-a-benevolat/embed/` | 13 refus + P-COOP inverse
b06-2868-recherche | 2868 | recherche | `/?s=Appels+%C3%A0+b%C3%A9n%C3%A9volat&post_type=page` | 13 refus + P-COOP inverse
b06-2869-html | 2869 | html | `/espace-cooperateurs/lettre-de-missions/` | 13 refus + P-COOP inverse
b06-2869-rest | 2869 | rest | `/wp-json/wp/v2/pages/2869` | 13 refus + P-COOP inverse
b06-2869-rest-route | 2869 | rest-route | `/?rest_route=/wp/v2/pages/2869` | 13 refus + P-COOP inverse
b06-2869-collection | 2869 | collection | `/wp-json/wp/v2/pages?include=2869` | 13 refus + P-COOP inverse
b06-2869-oembed | 2869 | oembed | `/wp-json/oembed/1.0/embed?url=http%3A%2F%2F192.168.129.32%3A8085%2Fespace-cooperateurs%2Flettre-de-missions%2F` | 13 refus + P-COOP inverse
b06-2869-embed | 2869 | embed | `/espace-cooperateurs/lettre-de-missions/embed/` | 13 refus + P-COOP inverse
b06-2869-recherche | 2869 | recherche | `/?s=Lettre+de+missions&post_type=page` | 13 refus + P-COOP inverse
b06-2870-html | 2870 | html | `/espace-cooperateurs/cadastre-des-competences/` | 13 refus + P-COOP inverse
b06-2870-rest | 2870 | rest | `/wp-json/wp/v2/pages/2870` | 13 refus + P-COOP inverse
b06-2870-rest-route | 2870 | rest-route | `/?rest_route=/wp/v2/pages/2870` | 13 refus + P-COOP inverse
b06-2870-collection | 2870 | collection | `/wp-json/wp/v2/pages?include=2870` | 13 refus + P-COOP inverse
b06-2870-oembed | 2870 | oembed | `/wp-json/oembed/1.0/embed?url=http%3A%2F%2F192.168.129.32%3A8085%2Fespace-cooperateurs%2Fcadastre-des-competences%2F` | 13 refus + P-COOP inverse
b06-2870-embed | 2870 | embed | `/espace-cooperateurs/cadastre-des-competences/embed/` | 13 refus + P-COOP inverse
b06-2870-recherche | 2870 | recherche | `/?s=Cadastre+des+comp%C3%A9tences&post_type=page` | 13 refus + P-COOP inverse
b06-2871-html | 2871 | html | `/espace-cooperateurs/relais-des-evenements/` | 13 refus + P-COOP inverse
b06-2871-rest | 2871 | rest | `/wp-json/wp/v2/pages/2871` | 13 refus + P-COOP inverse
b06-2871-rest-route | 2871 | rest-route | `/?rest_route=/wp/v2/pages/2871` | 13 refus + P-COOP inverse
b06-2871-collection | 2871 | collection | `/wp-json/wp/v2/pages?include=2871` | 13 refus + P-COOP inverse
b06-2871-oembed | 2871 | oembed | `/wp-json/oembed/1.0/embed?url=http%3A%2F%2F192.168.129.32%3A8085%2Fespace-cooperateurs%2Frelais-des-evenements%2F` | 13 refus + P-COOP inverse
b06-2871-embed | 2871 | embed | `/espace-cooperateurs/relais-des-evenements/embed/` | 13 refus + P-COOP inverse
b06-2871-recherche | 2871 | recherche | `/?s=Relais+des+%C3%A9v%C3%A9nements&post_type=page` | 13 refus + P-COOP inverse

Autres voies historiques : `c23.build_routes()` inchangé et `livraison-finale-c23.md`. Plans de site fermés qualifiés comme fermés, pas comme collections ouvertes. Les six mutations sont qualifiées dans A-VOIR.md ; les anciennes mutations de corps en mémoire ne sont pas des parcours applicatifs mutés.
