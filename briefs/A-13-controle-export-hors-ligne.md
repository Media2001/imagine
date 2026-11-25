# Lot A-13 — Le contrôle d'un export d'abonnés hors ligne

**Voie** : 1. **Chantier** : A. **Délai** : une demi-journée. **Cahier des charges** : §4.3 (« Abonnés hors ligne », « Abonnés sans email »), §2.3.

## Pourquoi

Environ 1 500 abonnés par domiciliation ou par virement vivent dans une base Access. Ils seront importés à partir d'un export qu'Imagine n'a pas encore fourni. Le cahier des charges prévoit un contrôle des doublons et des échéances, un rapport des rejets et une « boucle de correction avec l'administration » : cette boucle peut commencer dès que l'export arrive, bien avant l'import, si l'outil de contrôle existe. C'est ce lot.

**Ce lot n'importe rien.** Il ne crée aucun compte, aucun abonnement, n'écrit dans aucun site. Il lit un fichier et dit ce qui ne va pas. Tu ne verras jamais le vrai fichier : il sera contrôlé par Ced, sur le NUC, hors du dépôt.

## Ce qu'on veut

`wp/outils/bascule/controler-export`, en PHP ou Python pur, sans WordPress, qui prend un fichier tableur (CSV) et un **fichier de correspondance des colonnes** :

- le format de l'export n'est pas connu. La correspondance (quelle colonne du fichier est le nom, la rue, l'échéance…) est donc un fichier de configuration, pas du code. Livre un exemple, `correspondance.exemple.json`, sur les champs que nomme le cahier des charges : contact, type d'abonnement, numéros dus, échéance, statut de coopérateur, mode de paiement, référence du mandat papier ;
- **aucun IBAN** : si une colonne ressemble à un IBAN (par son nom ou par son contenu), l'outil s'arrête avant tout traitement, dit laquelle, et n'en recopie aucune valeur nulle part ;
- contrôles par ligne : champs obligatoires absents, date d'échéance illisible ou passée, nombre de numéros dus illisible ou négatif, adresse postale incomplète, adresse électronique mal formée, mode de paiement hors de la liste déclarée dans la correspondance, mandat papier sans référence ;
- contrôles d'ensemble : doublons (même adresse électronique ; même nom et même adresse postale, après normalisation de la casse, des accents et des espaces), références de mandat en double ;
- les lignes **sans adresse électronique** ne sont pas des rejets : elles sont comptées à part (elles suivront la règle du §3.13). L'outil n'invente aucune adresse ;
- encodage et séparateur détectés ou déclarés, jamais devinés en silence : en cas de doute, arrêt avec un message clair.

Sorties, écrites à côté du fichier contrôlé et **jamais dans le dépôt** :

- un résumé lisible : nombre de lignes, de lignes sans défaut, de rejets par motif, de doublons, de lignes sans adresse électronique ;
- un fichier des rejets pour l'administration : numéro de ligne dans le fichier d'origine et motif en français. **Pas de recopie des données de la ligne** : l'administration a le fichier d'origine sous les yeux ;
- code de retour non nul s'il y a des rejets.

Aucune règle métier nouvelle : l'outil ne décide pas si un abonné échu doit être importé, ni comment un « type d'abonnement » d'Access devient un produit. Si un contrôle demande une règle que le cahier des charges ne donne pas, c'est une option de la correspondance, désactivée par défaut, et tu le signales.

## Preuve

Un fichier fictif de trente lignes dans `wp/tests/fixtures/` (noms manifestement inventés, adresses en `@example.org`), qui porte chaque défaut au moins une fois, plus un second fichier avec une colonne IBAN fictive. Chaque défaut est reconnu sur la bonne ligne ; le fichier avec IBAN est refusé sans qu'aucune valeur n'apparaisse dans une sortie ; un fichier propre sort avec le code 0. Tests en code pur. Preuves proportionnées.

## Livrables

L'outil, ses tests, la correspondance d'exemple, une page de mode d'emploi pour Ced (`wp/outils/bascule/controler-export.md`), `production/A-13/PRET`. Rapport court.
