# A-23 — notes de construction

Périmètre : nouveaux fichiers A-23 uniquement. Aucun PRET, fichier partagé, Git,
site existant, archive de production, compte externe ni voie 2 touché.

## Frontière A-22

Au premier contrôle, `production/A-22/notes.md` est absent. A-23 attend le gardien
commun pour publier ses sorties ; **aucun gardien bis ne sera écrit dans A-23**.
Le lanceur A-23 aura trois arguments (`--wp-path`, `--audit`, `--output`), un
marqueur de succès fixe `A23_OK comptes.json comptes.md`, un validateur fermé du
paquet, et les mêmes barrières A-11/A-12. Tant que le seam commun n'est pas
présent, refus fermé `A23_SUPERVISOR_UNAVAILABLE`. Intégration parent à la
frontière si nécessaire. Notes à actualiser après lecture du contrat A-22.

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

TDD préfixes/seuil puis agrégats : RED réel dans les conteneurs jetables propres
A-23, puis GREEN réel ; essais intermédiaires uniquement en scratch. Matrice
finale et canaris natifs encore à produire. Aucun accord de bascule réelle.
