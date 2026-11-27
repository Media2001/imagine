# A-33 — Le poids des archives

Lecture seule ; à lancer uniquement sur une copie vérifiée, après l'audit A-02 et avec la correspondance d'A-16 remplie par l'opérateur. Aucun choix de rattachement, aucune commande lue par le collecteur. La correspondance d'exemple est fictive, pas celle d'Imagine.

```sh
python3 wp/outils/bascule/a33/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --correspondance=/hors-web/correspondance.json --output=/hors-web/archives-date
```

Le parent de sortie existe déjà, hors du site et du dépôt, sans être leur ancêtre. Le dossier cible doit être absent. Linux avec Landlock, PHP 8.2+ et Python 3 est nécessaire pour l'outil ; la suite Python est également jouable sur Windows.

A-16 est appelé directement : correspondance, refus et tri UTC/ID décroissant inchangés, dix numéros au plus. Un article lié à plusieurs numéros dont un des dix est conservé du côté des dix, compté une seule fois. En dehors : contenus `publish` seulement, année UTC du contenu parent pour les fichiers ; dates nulles regroupées en `inconnu`. Les types de site ne sont jamais exportés : `article` et `numero` sont les deux rôles de la correspondance ; `post`, `page`, `product`, `product_variation` sont fermés dans le code, tout autre type devient `autre`. Les commandes, abonnements, coupons, adhésions, révisions et pièces jointes ne sont pas des publications archivables.

Les pièces des numéros conservés incluent leurs articles, même non publiés ; les autres pièces sont rangées soit avec les publications hors dix, soit sans parent (zéro ou absent), soit dans `other_media` (parent existant non publié/non éditorial). Une pièce n'est pas une preuve de fichier inutilisé. Les originaux `_wp_attached_file` sont mesurés par `stat`, sans ouverture ni miniatures ; une même pièce compte une fois, deux inscriptions du même fichier restent deux pièces. Fichiers absents séparés ; `known_bytes` ne les transforme pas en zéro : `total_bytes` est inconnu s'il en manque, même lorsque les fichiers présents pèsent zéro.

Sur une copie importée/neutralisée (option native `imagine_staging_disabled_plugins` présente), les publications conservées et les poids locaux présents restent lisibles ; les dossiers écartés par l'import ne sont pas reconstituables : `excluded_directories_bytes` vaut « inconnu après import », y compris sans pièce survivante. Une absence y rend également le total correspondant inconnu après import. Sur une copie non importée, le poids des dossiers exclus est « non évalué », jamais un zéro inventé. Aucun total global de sauvegarde, aucun dossier privé extérieur, aucune protection serveur n'est déduit.
