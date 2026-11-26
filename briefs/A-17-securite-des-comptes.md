# Lot A-17 — L'état des lieux de la sécurité des comptes de l'administration

**Voie** : 1. **Chantier** : A. **Délai** : trois heures. **Dépend de** : A-11. **Cahier des charges** : §4.4 (« limitation des tentatives de connexion, authentification à deux facteurs pour les comptes administrateurs »).

## Pourquoi

On repart de la production, donc on hérite de ses comptes : des administrateurs créés au fil des années, des prestataires partis, des mots de passe d'application oubliés. Le cahier des charges demande la double authentification pour les administrateurs et la limitation des tentatives. Avant la bascule, Ced doit savoir d'où l'on part. Ce lot fournit l'outil, prêt pour le staging d'Imagine vérifié.

**Ce lot ne supprime ni ne modifie aucun compte, n'active aucune protection et ne décide pas qui doit garder ses droits.**

## Ce qu'on veut

Un complément du script d'audit, en **lecture seule**, par le lanceur confiné d'A-11 :

- le nombre de comptes par rôle, pour les rôles qui ouvrent l'administration (administrateur, gestionnaire de boutique, éditeur, et tout rôle sur mesure portant une capacité de gestion, nommé par son identifiant) ;
- pour ces comptes, des comptes agrégés seulement : combien n'ont aucune connexion enregistrée depuis douze mois **si le site garde cette information** (sinon « inconnu », jamais une estimation), combien portent au moins un mot de passe d'application, combien ont une double authentification active ;
- les protections présentes : extension de double authentification, limitation des tentatives, pare-feu (noms, versions, active ou non), **sans aucun réglage** ;
- quelques oui ou non lisibles dans la configuration : inscription publique ouverte, rôle par défaut des nouveaux comptes, édition des fichiers depuis l'administration, interface XML-RPC, mots de passe d'application disponibles.

**Aucun identifiant de connexion, aucun nom, aucune adresse, aucune empreinte de mot de passe, aucun secret** ne sort de l'outil : des nombres, des identifiants de rôle, des noms d'extension. Sur un site anonymisé par l'import, les nombres restent justes ; c'est tout ce qu'on en attend.

La double authentification dépend de l'extension qui la porte. L'outil reconnaît celles qu'il sait lire, les nomme, et répond « inconnu » pour les autres : dis-le dans le mode d'emploi plutôt que de laisser croire à un zéro.

## Preuve

Sur le banc fictif, classique et HPOS : deux administrateurs dont un avec un mot de passe d'application, un rôle sur mesure portant une capacité de gestion, un identifiant de connexion canari, inscription publique ouverte. Les comptes sont exacts, le canari est absent de toutes les sorties, rien n'est écrit (empreintes identiques avant et après), aucune tentative de connexion n'est faite. **Un seul paquet de preuves.** Suite Python rejouable sous Windows.

## Livrables

Le script, ses tests, deux lignes dans le mode d'emploi de l'audit, `production/A-17/PRET`. Rapport court.
