# A-23 — notes de construction

Périmètre : nouveaux fichiers A-23 uniquement. Aucun PRET, fichier partagé, Git,
site existant, archive de production, compte externe ni voie 2 touché.

## Frontière A-22

`production/A-22/notes.md` a été relu aux frontières. Le seam désormais présent
est utilisé directement : `stream_guard.py::supervise` et `closed_refusal`.
Aucun gardien bis dans A-23. Trois arguments, marqueur fixe
`A23_OK comptes.json comptes.md` et validateur fermé des deux fichiers. Seul
l'enfant PHP reçoit les droits Landlock du dossier privé ; aucune publication
avant code de fin et EOF des deux flux. Le seam absent reste un refus fermé testé.
Les dépendances sont scellées séparément : si A-22 change après le dernier
rejeu, le parent doit rejouer la matrice avant son PRET, sans recycler l'ancien
paquet. Préparation/T01 globaux et PRET sont réservés au parent.

## Décisions prudentes

- Pas de verdict sur une reconnexion ; le préfixe ne valide ni une empreinte ni
  sa compatibilité. Un MD5 sans préfixe identifiable reste `autre`.
- Les collisions d'email/login d'un lecteur sont cherchées contre **tous** les
  comptes, administration comprise. L'administration n'entre pas dans les
  comptes rendus. Les mêmes ensembles de comparaison servent à la sous-population
  des abonnés vivants : aucun doublon n'est perdu à sa frontière.
- Vivant = `active`, `pending`, `on-hold`, `pending-cancel`, comme A-20 ; pas une
  décision de droits. Un compte n'est compté qu'une fois malgré plusieurs contrats.
- Un petit groupe (<5) est absorbé dans `autres`, par tableau. Les anomalies
  pouvant se recouper, `autres` est une somme d'occurrences de comptes, pas un
  nombre de personnes distinctes. Les zéros n'affichent pas leur libellé.
- L'égalité login/email est exacte ; les collisions ignorent la casse ASCII,
  sans rogner les espaces ni corriger l'adresse. Vide = chaîne vide ; un espace
  est mal formé. Les adresses mal formées non vides peuvent aussi être partagées.

## Import lu sans modification

`wp/outils/staging/lib.php:447-455` remplace login, email, empreinte, nom et
nicename par utilisateur. La marque existante
`imagine_staging_disabled_plugins` est posée par `transform` (ligne 489), y compris
lors de la neutralisation seule ; lecture prudente de sa présence, pas de son
contenu. Six blocs `families`/`emails`/`logins` (lecteurs et abonnés vivants) doivent
répondre `inconnu après neutralisation`, jamais zéro. Restent lisibles : nombre
de lecteurs, nombre de lecteurs portant un contrat vivant, absence de commande
et d'abonnement. Les liens client/commande et les rôles ne sont pas réécrits par
ces lignes ; la création de l'administrateur technique est exclue du périmètre.

## État de preuve

TDD réel : préfixes/seuil puis agrégats, lanceur, schéma public, vérificateur,
inclusion pure sans écriture et garde de planification, RED puis GREEN. Les
essais intermédiaires sont uniquement en scratch. Le seul paquet à livrer est
`preuves/final` ; son vérificateur dérive les comptes réellement observés et
refuse les reçus vides, mixtes `checks`/`tests`, dupliqués ou rouges. Le README
est rejoué avec ses seuls trois arguments, chemins fictifs substitués seulement.

Les deux magasins ont déjà passé 160 contrôles natifs, dont les canaris sur
chaque canal et quatre mutations sans gardien par magasin (octets uniquement
en mémoire). Des bases fictives clonées ont traversé le vrai neutraliseur puis
l'anonymiseur : les trois champs ont changé pour chaque compte initial. Les
nombres utiles restent 32 lecteurs, 20 portant un contrat vivant et 3 sans
historique (ce dernier petit groupe est fondu). Empreintes de toutes les tables
identiques avant/après, variantes neutralisées comprises. Aucun mot de passe
n'est essayé ; aucune notification ni compte n'est modifié par l'outil.

La matrice finale utilise `C:/Python314/python.exe` (version et encodages
mesurés dans ses `environment.json`), pas le Python du PATH (3.11.15 utilisé
seulement pour les premiers essais). UTF-8 et cp1252 sont deux contextes complets.
PSR-12 strict et contrôle statique des sources WordPress sont dans le paquet.
Les dix lignes de standard citent trois sources officielles effectivement lues ;
la prose historique phpass de « More Information » est distinguée du code et
du changelog. Aucun verdict de reconnexion n'est rendu.

## Besoin transversal relevé, autres lots laissés intacts

Après le vrai import, Action Scheduler tente de recréer des tâches effacées ;
`ActionFactory` écrit explicitement une erreur d'enqueue sur STDERR quand le
SQL READ ONLY refuse l'écriture. Le gardien refuse correctement cette sortie :
il ne faut ni la cacher ni affaiblir la barrière. A-23 préinitialise les quatre
filtres natifs `pre_as_*` à 0 avant `Runtime::boot`, selon le mécanisme natif de
`WP_Hook::build_preinitialized_hooks`. Les quatre API sont réellement essayées
par une extension fictive ; leurs sources installées sont scellées dans
`standard.json`. Cela peut être utile aux autres inventaires sur copie
neutralisée : laissé au parent, aucun changement au Runtime, au gardien ou aux
autres lots. Ce raccord local ne modifie pas l'import.

Dernière lecture de la frontière A-22 : son checkpoint de 14 h 56 a déjà choisi,
pour les anciens inventaires, de rejeter ces diagnostics explicites dans le
seul périphérique `/dev/null`, avec un droit noyau limité à ce périphérique.
A-23 ne change ni ce choix partagé ni sa mise en œuvre : il empêche localement
les tentatives de planification par les filtres natifs ci-dessus. Ses canaris
directs sur les deux flux restent observés et refusés par le gardien commun.
La matrice finale A-23 et son contrôle de dépendances ont réellement porté sur
ces dernières sources partagées ; aucun besoin de recoller un superviseur.

Dernier paquet sélectionné : `a23-final-matrix-02` du scratch, copié seul dans
`preuves/final`. Par console : 23 tests Python, 34 contrôles purs, 14 contrôles
statiques du standard, 160 contrôles natifs et 9 contrôles runner, tous verts ;
PSR-12 : zéro erreur et zéro avertissement. Python mesuré : 3.14.6 sous Windows,
UTF-8 puis cp1252, UTF-8 mode respectivement 1 et 0. Le vérificateur scellé a
retourné 66 PASS, zéro FAIL et code 0 avant cette seule actualisation de notes ;
le manifeste de packaging est rescellé et le contrôle rejoué ensuite.

Delta partagé séparé : `readme-ajout.txt`, non appliqué. Reprise et vérification :
`FINALISATION.md`. Aucun PRET ni accord de bascule réelle.
