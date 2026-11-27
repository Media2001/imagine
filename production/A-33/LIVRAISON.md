# A-33 — Livraison

## Portée et décisions à défaut

§4.3 a été relu. A-12, A-16 et A-22 sont clos et utilisés en lecture seule ; aucun de leurs fichiers n'est changé. `STANDARD.md` contient les trois lignes du standard et les références officielles consultées. L'outil est `wp/outils/bascule/a33/confine.py`, son mode d'emploi détaillé est `wp/outils/bascule/a33/README.md` ; seules trois lignes contractuelles de la section A-33 du mode d'emploi commun sont contrôlées, jamais l'empreinte du fichier entier.

A-16 est appelé directement avec dix, sans nouveau tri ni règle concurrente ; les correspondances postmeta, parent et taxonomie sont exercées. Les quatre suffixes de champ dans les refus sont exactement ceux d'A-16. A-33 ajoute seulement le refus d'une correspondance non éditoriale avant bootstrap : pas de commande, abonnement, coupon ou adhésion comme numéro/article. Les types inconnus restent séparés par indice numérique anonyme ; aucun titre, identifiant d'objet, nom de type de site ou chemin n'est publié. Année des pièces : celle du contenu parent en UTC. Une liaison à un des dix l'emporte sur une liaison à un numéro ancien ; aucun rattachement n'est écrit.

Les tailles sont les tailles logiques des originaux inscrits dans `_wp_attached_file`, par `stat` uniquement. Les miniatures, fichiers non inscrits et liens présents dans le texte ne sont pas déduits. Deux inscriptions du même fichier restent deux pièces. Les fichiers absents sont un nombre séparé et rendent le total incomplet inconnu ; `known_bytes` n'est que le sous-total des fichiers réellement présents. `other_media` évite de confondre une pièce attachée à un brouillon avec une pièce sans parent. Sur la copie importée/neutralisée, la présence de l'option native d'import impose « inconnu après import » pour le poids des dossiers exclus, même s'il ne subsiste aucune inscription ; le poids de ces dossiers n'est jamais deviné à zéro.

## Preuves et limites

Le banc est fictif, un seul magasin classique. WordPress réel ; extensions commerciales installées pour le semis puis inactives pendant ce collecteur purement éditorial. Les requêtes vers les tables de commandes sont piégées. SELECT seul et transaction native READ ONLY, Landlock, réseau absent, guards mail/HTTP/tâches et empreintes de toutes les tables/fichiers. Les ouvertures/lectures des médias sont observées par inotify autour du sujet uniquement, avec inverse positif du détecteur avant le passage. Le semis contient douze numéros, deux anciens, deux types inconnus distincts, tailles connues dont zéro, une absence, un parent zéro et un parent inexistant. Echo, STDOUT, STDERR, arrêt anticipé, shutdown, exception et altération du rapport fichier sont éprouvés séparément ; chaque variante compare de nouveau base et fichiers.

La variante d'import reproduit l'empreinte native de neutralisation sur ce semis ; elle ne rejoue pas l'import gelé et n'est pas une preuve sur l'archive d'Imagine. Aucun site, compte ni fichier réel utilisé. Le banc ne prétend pas qualifier une autre pile WordPress/PHP que celle inscrite dans ses reçus. Pas de taille d'archive compressée, d'occupation allouée par le système, de fichiers privés extérieurs à la racine uploads, ni de protection HTTP déduite. Les refus de disposition d'A-11/A-12 restent.

Un seul paquet courant : `production/A-33/preuves/final/`. Essais rouges/intermédiaires hors dépôt dans le scratch A-33. La matrice Windows retire TMPDIR, mesure les encodages des vrais fils et joue Python, natif et PSR-12 ; chaque sous-processus fixe son décodage. L'image est repréparée après les ajouts ; préparation et replays généraux sont strictement successifs. Le premier portail qualifie les douze paquets préexistants avant l'enregistrement du nouveau ; après enregistrement et sceau local, le portail est rejoué avec A-33 inclus. PRET exige ce second reçu sans paquet exclu ni rouge, puis une lecture sans argument. Aucun lecteur antérieur, lanceur, gardien ou import assoupli.

## Commandes de reproduction

Depuis `C:\Users\Ced\imagine`, dans cet ordre et sans concurrence Docker :

```text
python -B wp/tests/a33/matrix.py --include-native --parent-serialized --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a33-rejeu-neuf
python -B wp/tests/a33/gates.py --parent-serialized --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a33-gates-neufs
```

Les destinations doivent être neuves et hors dépôt. Ces deux commandes produisent seulement des preuves scratch ; elles ne remplacent aucun sceau ni PRET existant. `seal.py` vérifie ces données avant toute création/remplacement autorisé du paquet : aucune empreinte à remplacer à la main.

Lecture parent, sans mutation ni argument :

```text
python -B production/A-33/verify.py
python -B production/A-31/verify.py
python -B production/A-32/verify.py
```

Le vérificateur A-33 relit inventaire scellé, snapshots exécutés, témoins natifs nommés, oracles, base/fichiers, encodages et résultats globaux ; il refuse tout argument. Avant PRET, son portail doit déjà être vert sur les douze paquets existants. Avec PRET il exige en plus qu'A-33 figure dans les deux replays : cette distinction de cycle ne modifie aucun lecteur clos.
