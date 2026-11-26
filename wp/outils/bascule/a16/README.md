# A-16 — Dix derniers numéros, lecture seule

Après autorisation de Ced sur une copie vérifiée, dans un conteneur Linux déconnecté sans montage sensible, PHP 8.2+ / mysqli, Python 3 et Landlock ABI ≥3 :

```text
python3 wp/outils/bascule/a16/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --correspondance=/hors-web/correspondance.json --output=/hors-web/numeros-date --limit=10
```

Correspondance obligatoire, exemple **fictif** `correspondance.exemple.json` à remplir d'après A-12. `numero_source` optionnel : `post_type` par défaut (produit ou type éditorial natif) ou `taxonomy` (un terme par numéro). `numero_type` est l'identifiant du type ou de la taxonomie, jamais un libellé. `article_type` et `thematique` désignent les registres natifs. `date_cle` vaut `post_date_gmt`, ou une métadonnée portant exactement `AAAA-MM-JJ HH:MM:SS` UTC ; un numéro-taxonomie exige une métadonnée de terme. `pdf_cle` porte l'identifiant scalaire canonique d'une pièce jointe PDF, dans postmeta ou termmeta. Clé absente de tout le domaine : refus nommé, pas un faux zéro.

`liaison.source` : `postmeta` (clé portée par l'article, identifiant de numéro scalaire), `post_parent` (numéros de type contenu), ou `taxonomy` (même taxonomie que les numéros). Aucune équivalence entre un ID de terme et un ID de contenu n'est inventée. Référence sérialisée/JSON, doublon de métadonnée, date invalide, chemin externe/traversée/lien symbolique : refus explicite sans valeur. Aucune thématique déduite. Pour une liaison taxonomique multiple, l'article compte dans chaque numéro effectivement rattaché.

Résultats `numeros.json` et `numeros.md`, 0700/0600, seulement comptes, identifiants et dates. Tous les états d'article sont comptés, publiés/non publiés séparés. N=10 par défaut, de 1 à 100 ; ordre date UTC décroissante puis ID décroissant en cas d'égalité. Les orphelins publiés sont comptés sur **tous** les numéros, pas seulement la sélection N, selon l'année UTC de l'article (inconnue explicitement si date nulle). Les médias attachés sont les pièces jointes dont `post_parent` est un article du numéro, distinctes par ID ; pas une recherche de liens dans les corps ni un inventaire de chaque dérivé. Image principale absente inclut une référence dont le fichier original manque. PDF : oui/non/déclaré mais fichier absent ; `pdf_public` signale l'emplacement dans uploads sous la racine publique, **pas** une tentative HTTP ni une preuve d'accessibilité ou de protection du serveur.

Sortie neuve, parent existant, frère du rapport A-02, disjoint du site et du dépôt dans les deux sens. A-12 fournit Landlock ; A-11 fournit l'unique connexion READ ONLY avant bootstrap natif, gardes mail/HTTP/cron et refus nommés des caches/pare-feu/symlinks. Ne pas écarter ces fichiers sur la source : l'opérateur prépare une copie. Aucune archive, aucun compte/service réel, aucun rattachement ni écriture du site.

Rejeu : `python wp/tests/a16/run.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a16-rejeu-NOUVEAU`. PHP uniquement dans le conteneur jetable A-02 classic/HPOS. Contrôle sans PHP hôte : `python wp/tests/a16/test_launcher.py`, puis `python wp/tests/a16/verify.py production/A-16/preuves/final`. Python natif 3.14.7 testé en UTF-8 et cp1252/PYTHONUTF8=0 ; le test fixe lui-même UTF-8 pour ses enfants.
