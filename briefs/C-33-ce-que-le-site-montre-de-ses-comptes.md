# Lot C-33 — Ce que le site montre de ses comptes à un visiteur

**Voie** : 2. **Chantier** : C. **Délai** : deux à trois heures. **Dépend de** : B-16 (signature de l'article, sans page d'auteur), C-26 (parcours des pages publiques), B-06 (plan du site des pages coopérateurs). **Cahier des charges** : §4.4 (sécurité des comptes, limitation des tentatives de connexion) et §3.3 (« signature du journaliste »). Relis-les.

## Pourquoi

Le site sera la seule base d'abonnés d'Imagine. WordPress publie de lui-même, à qui le demande, la liste de ses comptes qui ont écrit : par les archives d'auteur, par l'interface REST, par le plan du site, par les flux. B-16 a déjà séparé la signature d'un article du compte qui l'a saisi ; il reste à fermer les autres portes, et à le prouver.

## Ce qu'on veut

**Le standard d'abord.** Cinq lignes, sources officielles citées : par quelles voies natives un visiteur anonyme obtient un identifiant, un nom ou un numéro de compte (archives d'auteur et leur redirection par numéro, liste des utilisateurs de l'interface REST, plan du site des utilisateurs, auteur dans les flux et dans l'oEmbed), et le point d'accroche natif qui ferme chacune.

- Pour un visiteur anonyme, sur la démonstration :
  - une archive d'auteur, par nom ou par numéro, répond « introuvable » ; aucune redirection ne révèle un identifiant ;
  - l'interface REST ne liste aucun compte et n'en rend aucun par son numéro ;
  - le plan du site natif n'a pas de section pour les utilisateurs ;
  - les flux et l'oEmbed d'un article ne portent ni identifiant ni nom de compte : la signature de B-16 si elle existe, sinon le nom du site.
- **Rien ne change pour un compte connecté qui a le droit de lister les utilisateurs**, ni pour l'éditeur de WordPress, qui a besoin de l'interface REST pour choisir un auteur.
- Dis au passage, sans le corriger, ce que le plan du site natif liste d'autre : un type de contenu qui est un message de visiteur (propositions de sujet, contact) ou une pièce privée ne doit pas y figurer ; s'il y figure, écris-le dans le rapport.

Règles :

- les points d'accroche natifs, pas de réécriture d'adresse ni de règle de serveur ;
- aucun compte créé, renommé ou modifié en dehors des comptes d'essai du test ;
- la limitation des tentatives de connexion et la double authentification ne sont pas dans ce lot : elles dépendent de l'hébergement et d'un choix d'outil.

## Preuve

Proportionnée. Chaque voie, en anonyme : la réponse et l'absence, dans le corps et les en-têtes, de l'identifiant et du nom d'un compte témoin qui a publié un article ; un contrôle qui vérifie d'abord que la voie existe (l'article témoin est bien publié, le plan du site répond). Une mutation témoin par voie fermée. Un administrateur connecté liste toujours les comptes. Compte et article témoins supprimés.

## Livrables

Le code, ses tests, la section du README, `production/C-33/A-VOIR.md` (trois adresses à ouvrir en navigation privée), `PRET`. Rapport court.
