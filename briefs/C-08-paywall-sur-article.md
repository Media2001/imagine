# Lot C-08 — Le paywall branché sur l'article

**Voie** : 2. **Chantier** : C. **Nature** : branchement WordPress et tests. **Délai** : une demi-journée.
**Dépend de** : C-06 (clos), C-03 (clos), B-01.
**Cas d'acceptance concernés** : R-25 à R-31 (lis-les, ne les automatise pas tous : voir « Preuve »).

## Pourquoi

La décision d'accès (C-06) existe et elle est testée, mais rien ne l'appelle. Ce lot la branche sur l'affichage d'un article, sur le site de démonstration. C'est la première fois que Ced verra le paywall.

## Ce qu'on veut

Dans `wp/plugins/imagine-site/` (pas dans `imagine-pilotage`, dont les bibliothèques closes ne changent pas) :

1. **Un adaptateur** qui, pour la requête en cours, rassemble les entrées de la décision (contenu réservé ou ouvert, numéro, visiteur et ses droits, résultat de la vérification des robots, instant) et appelle `Acces\Moteur`. Les droits du visiteur viennent de Memberships et de Subscriptions tels qu'ils sont sur le site de démonstration.
2. **Le point de sortie du corps d'article** (B-01) sert le texte complet ou l'extrait selon la décision, puis le bloc indiqué (abonnement, connexion, régularisation, découverte épuisée). Les blocs sont des gabarits du thème, neutres, avec un texte provisoire.
3. **Étanchéité côté serveur** : quand la décision est « extrait », le texte complet ne doit sortir **nulle part** pour cette requête. Couvre au minimum : la page, l'API REST du contenu, les flux RSS, l'extrait automatique, les balises de partage. Fermé par défaut : si l'adaptateur échoue, c'est l'extrait.
4. **Pages réservées et cache** : une page servie à un abonné ne doit pas être mise en cache pour tous. Pose les en-têtes qu'il faut ; pas d'extension de cache dans ce lot.

## Hors périmètre

Le PDF du numéro, le mode lecture, l'accès découverte complet (ouverture et décompte), le tunnel. Le PDF fera l'objet d'un lot à part.

## Preuve

- Un test d'étanchéité automatique, rejouable sur le site de démonstration : pour un article réservé, une phrase témoin placée au milieu du texte est **absente** de chacune des sorties ci-dessus pour un anonyme, et **présente** dans la page pour un abonné actif.
- À la main ou par script, quatre situations au moins : anonyme, abonné actif, abonné en délai de grâce (bandeau), faux robot.

## Livrables

- Le code et ses tests.
- `production/C-08/A-VOIR.md` : l'adresse d'un article réservé et la marche à suivre pour le voir en anonyme puis en abonné (identifiants de test : chemin du fichier hors dépôt, jamais les mots de passe).
- `production/C-08/PRET`.
