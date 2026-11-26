# Lot A-28 — Les messages de formulaires ne survivent pas à l'import

**Voie** : 1. **Chantier** : A. **Délai** : trois heures. **Dépend de** : A-01 (clos), A-25. **Doctrine** : §3 (« un agent ne travaille que sur la copie anonymisée » ; la copie est « neutralisée, anonymisée et vérifiée » avant tout accès). **Cahier des charges** : §4.4.

## Pourquoi

A-25 l'a montré sur le banc : avec la décision `garder` posée sur une table de messages de formulaires, les messages restent en clair après neutralisation et anonymisation. Un message de formulaire est un texte libre écrit par un visiteur : un nom, une adresse, parfois une situation personnelle. Il ne s'anonymise pas colonne par colonne. Il se vide.

Le parcours que Ced lance (`wp/outils/staging-court/`) vide par défaut les tables hors catalogue : le cas courant est donc sans doute couvert. Mais rien ne le prouve pour les messages, rien n'empêche un `garder` posé par mégarde, et certaines extensions rangent leurs messages ailleurs que dans une table à elles (comme des contenus, dans la table des articles).

**Ce lot n'ouvre pas l'archive d'Imagine et ne change aucune commande de Ced.** A-01 reste clos pour tout le reste.

## Ce qu'on veut

**Le standard d'abord.** Dix lignes : où les extensions de formulaires courantes rangent les messages reçus (table dédiée, type de contenu, autre), d'après leur documentation officielle, phrase citée. Une liste fermée, courte ; ce qui n'y est pas reste « autre ».

**La preuve d'abord.** Par le vrai parcours d'import, sur archives entièrement fictives, un texte canari dans chacune de ces formes : une table dédiée de la liste, une table dédiée inconnue, un type de contenu de la liste. Dis ce qu'il en reste après l'import, avec la politique par défaut, puis avec un `garder`.

**Puis fermer, au plus simple :**

- les tables et les types de contenu de la liste fermée sont vidés par l'import, par la politique, sans décision à prendre ;
- un `garder` posé sur une table de la liste est refusé, comme les autres refus d'A-01 (étape, code, table ; aucune valeur) ;
- l'étape qui déclare une copie « vérifiée » compte ce qui reste dans ces rangements et refuse s'il en reste. Un nombre et un code, jamais un texte.

Pour un type de contenu **inconnu**, ne décide rien : les contenus du magazine en font peut-être partie. Dis ce que l'import en fait aujourd'hui et pose la question dans tes notes.

## Preuve

Sur le banc fictif : après l'import par défaut, aucun canari dans la base restaurée, pour chaque forme de la liste ; le `garder` est refusé ; l'étape de vérification refuse une copie où un message reste, et une mutation témoin (le contrôle retiré) la laisse passer. Les suites d'A-01 rejouées au vert, le rejeu global aussi. Le mode d'emploi de Ced, relu : aucune de ses commandes n'a changé. **Un seul paquet de preuves.** Suite Python rejouable sous Windows (cp1252).

## Livrables

Le code, ses tests, trois lignes dans le mode d'emploi de l'import (ce qui est vidé, ce qui est refusé), `production/A-28/PRET`. Rapport court, avec la question des types inconnus.
