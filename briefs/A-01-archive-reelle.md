# Lot A-01 — Première archive réelle : refus `ARCHIVE_PATH`

**Voie** : 1. **Nature** : correction de la commande d'import. **Délai** : deux heures. **Passe avant tout.**

## Ce qui s'est passé

Le 23/11 à 13 h 41, Ced a lancé le premier import réel. Refus au prévol, avant toute création de site : `production/A-01/publication-23nov/8876588e7c6a/result.json`, code `ARCHIVE_PATH`, sans autre précision. Nettoyage correct. La commande a fait ce qu'elle devait (elle n'a rien ouvert), mais deux défauts apparaissent.

**1. Le refus ne dit rien d'exploitable.** On ne sait ni quelle règle a joué, ni sur combien de fichiers, ni où. Ni toi ni moi ne pouvons ouvrir l'archive : seul le rapport nous renseigne.

**2. La règle est plus stricte que la réalité.** `archive.py` (lignes 44 à 47) refuse dans le même code :
- un chemin absolu ou un segment vide, `.` ou `..` ;
- un caractère de contrôle, `\` ou `:` ;
- **deux chemins qui ne diffèrent que par la casse**.

Sur un site réel hébergé sous Linux depuis des années, deux fichiers `Photo.jpg` et `photo.jpg` dans le même dossier sont banals, et un nom de fichier avec `:` est légal. Ce ne sont pas des attaques. Le staging tourne sous Linux (système de fichiers sensible à la casse) : ces fichiers s'y restaurent sans collision.

## À faire

### A. Un diagnostic complet en une passe

Un mode `--diagnose` de `publish.py` (avec `--operator-ced --archive …`), **en lecture seule** : aucun site créé, aucun téléchargement, rien d'extrait sur disque. Il parcourt **toute** l'archive sans s'arrêter au premier refus et produit un rapport qui liste, pour **chaque** règle de refus de la commande (archive, manifeste, version du cœur, tables personnelles à trancher, secrets, tout ce qui peut être connu sans créer de site) :

- le code de la règle et le nombre de cas ;
- pour les fichiers : la zone seulement, c'est-à-dire les deux premiers segments du chemin (`plugins/<dossier>`, `uploads/<année>`, `themes/<dossier>`) et l'extension. **Jamais le nom du fichier** : un nom de média peut contenir un nom de personne ;
- pour les tables : le nom de la table et de ses colonnes, jamais une valeur ;
- en fin de rapport : la liste de ce qui bloquerait l'import, et de ce qui ne serait qu'un avertissement.

But : que Ced ne lance pas dix fois la commande pour découvrir dix refus l'un après l'autre.

Le refus ordinaire (sans `--diagnose`) doit lui aussi nommer la règle précise, le nombre de cas et la zone du premier.

### B. Assouplir ce qui est légitime, garder ce qui protège

- **Deux chemins différant par la casse** : acceptés tels quels si le système de fichiers cible est sensible à la casse (vérifie-le réellement sur la cible, ne le suppose pas). Deux chemins **strictement identiques** restent refusés. Signalés au rapport comme avertissement, avec leur nombre.
- **`:` dans un nom** : accepté, avertissement.
- **`\` et caractères de contrôle** : dis ce que tu recommandes et pourquoi, en trois lignes. Par défaut : toujours refusés, mais comptés et localisés par le diagnostic, pour qu'on décide sur pièces.
- **Restent des refus fermes** : chemin absolu, segment vide, `.`, `..`, tout ce qui sortirait du dossier cible, lien symbolique, arborescence `wp-config.php` / `wp-admin` / `wp-includes` à la racine.

Chaque assouplissement a son test : le cas légitime passe, le cas d'attaque voisin est toujours refusé (par exemple `a/../../b`, `C:/x`, un nom qui ne diffère d'un autre que par la casse **et** dont l'un est un lien).

### C. Ce que tu ne fais pas

Tu n'ouvres pas l'archive d'Imagine et tu ne lances aucun import : c'est Ced qui relancera, d'abord avec `--diagnose`. Tu travailles sur archives inventées, en y fabriquant les cas ci-dessus.

## Livrables

Le code, les tests, la commande `--diagnose` exacte pour Ced en tête de `production/A-01/notes.md`, puis `production/A-01/PRET`.
