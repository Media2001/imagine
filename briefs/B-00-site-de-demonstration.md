# Lot B-00 — Le site de démonstration

**Voie** : 2. **Chantier** : B. **Nature** : outillage et contenu fictif. **Délai** : une demi-journée.

## Pourquoi

Ced n'a encore rien vu. Tout ce qui est construit (numéros, décision d'accès, échéancier, liste d'envoi) vit dans des bibliothèques testées. Il faut un site qu'il ouvre dans son navigateur, où les lots de la voie 2 viennent se brancher un par un. Ce site est **entièrement fictif** : il ne dépend ni de l'import d'Imagine, ni des maquettes.

## Ce qu'on veut

Un site permanent dans l'outil de staging, nommé **`imagine-test-demo`**, reconstruit par un seul script : `wp/outils/demo/construire.ps1` (ou `.py`, comme tu préfères, lancé depuis PowerShell).

- **Pile cible** : la version de WordPress exigée par les extensions déposées par Ced (7.0.x), WooCommerce, Subscriptions et Memberships dans les versions du dossier des extensions premium. Extensions sur mesure du dépôt activées. Thème `imagine` activé dès que B-01 existe ; d'ici là, un thème par défaut.
- **Aucune connexion extérieure** : pas de compte WooCommerce.com, pas de clé de licence d'extension commerciale activée, pas de passerelle de paiement réelle (modes de test ou passerelle fictive), aucun email sortant (capturés ou désactivés).
- **Contenu fictif**, créé par le script, manifestement inventé :
  - le calendrier de parution fictif de `docs/recette/profils.md` (« Données communes ») ;
  - quatre numéros et un hors-série, chacun avec une couverture de remplacement (aplat de couleur et numéro, générée, aucune image prise sur le web), trois articles réservés, un article ouvert, un PDF factice ;
  - trois thématiques, deux événements, deux partenaires ;
  - textes de remplissage en français, assez longs pour qu'un extrait et un texte complet se distinguent à l'œil.
- **Modèle de contenu provisoire** : pour rattacher un article à son numéro, fais au plus simple (type de contenu et champ déclarés en code, dans une extension `wp/plugins/imagine-site/`). Pas d'ACF. C'est provisoire : le vrai modèle éditorial viendra après l'audit de l'existant. Dis-le en tête du fichier.
- **Rejouable** : relancer le script reconstruit le site à l'identique (mêmes adresses de pages, mêmes identifiants de test). Il ne touche à aucun autre site de l'outil et ne modifie pas l'outil.

## Règles propres à ce lot

- Le site s'appelle `imagine-test-demo` et rien d'autre. La voie 1 crée et détruit ses propres sites de test : tu n'y touches pas, elle ne touche pas au tien.
- Si l'outil refuse une opération parce qu'une autre est en cours, tu attends et tu réessaies (trois fois, à cinq minutes). Tu ne forces rien.
- Le site est créé par la création normale de l'outil, avec ce qu'elle installe d'office (Novamira et sa licence). Révision du 23/11, 13 h 45 : c'est autorisé pour ce site fictif, et tu peux t'en servir.
- Aucun mot de passe dans le dépôt. Le script écrit les identifiants de test dans un fichier **hors dépôt** et affiche son chemin.

## Livrables

- Le script et son mode d'emploi en cinq lignes (`production/B-00/notes.md`).
- **`production/B-00/A-VOIR.md`** : la liste des adresses à ouvrir par Ced (accueil, un numéro, un article réservé, un article ouvert, la page d'administration), avec pour chacune une phrase : ce qu'il doit y voir. C'est ce fichier que Claude lui transmet.
- Preuve : sortie du script, puis réponse HTTP de chaque adresse de `A-VOIR.md`.
- `production/B-00/PRET`.
