# A-02 — replay synthétique indépendant

Depuis `C:\Users\Ced\imagine`, sans PHP Windows :

```text
python wp/tests/a02-audit/run.py
python wp/tests/a02-audit/verify.py production/A-02/preuves/IDENTIFIANT_AFFICHE
```

`run.py` ne prend **aucun chemin de site ni d'archive**. Il crée ses propres fixtures WordPress/WooCommerce/Subscriptions/Memberships, classiques puis HPOS, dans un conteneur jetable. Les deux entrées commerciales autorisées sont lues sous `/home/ced/staging-wp/plugins/`, jamais copiées au dépôt. Aucun téléchargement, installation hôte, activation de licence, compte, import Imagine, Novamira ou service Web.

Prérequis déjà présents : Docker via `wsl.exe -d Ubuntu -- docker`, image publique synthétique `sha256:2fa44089da3ca9aeaba5da0b74bbb3e9e1592b14c07d114c6a635b5c814208f2`, les deux ZIP dont les SHA-256 sont figés dans `run.py`. Il s'agit du **banc compatible clos**, pas d'une dépendance au code A-01 en qualification. Le banc est WordPress 7.0.9 / WooCommerce 11.1.1, nécessaire aux commerciaux disponibles ; ce n'est ni une modification ni une qualification de la production 6.9.1.

Isolation : `--network none`, aucun port, aucun montage/volume, capacités supprimées, `no-new-privileges`, MariaDB par socket Unix avec `--skip-networking`. Le runner vérifie ces points avant l'entrée des fichiers et après l'exécution. Cleanup limité au nom et au label créés par ce run ; absence relue par `docker inspect`.

## Ce que prouvent les tests

- Les sept rubriques et les deux sorties, leur cohérence, les cinq priorités finales.
- Les véritables extensions actives : trois abonnements, trois adhésions, deux règles de restriction, dont sept jours de différé ; commandes datées et produit récurrent.
- Magasin faisant autorité classique/HPOS, sans compter deux fois les commandes.
- Versions installées, minima des en-têtes et constantes littérales, cache local de mises à jour connu/inconnu, inactive/MU et thèmes.
- Plans et objets par identifiants, jamais leurs titres, utilisateurs, adresses ou valeurs de réglage. Canaris synthétiques dans contenus, options, comptes, commandes, arguments, table inconnue et journal absents des rapports.
- Empreinte **logique** de chaque table (schéma + multiensemble de toutes les lignes) avant/après, oracle PDO indépendant, compte SELECT uniquement pour le sujet ; tentative d'écriture refusée même avec root dans la transaction du sujet.
- Empreinte des fichiers du site inchangée ; piège d'exécution du `wp-config.php` non déclenché. Aucun bootstrap WordPress par l'auditeur.
- Refus des réglages dynamiques/conditionnels, d'une sortie dans le site, d'une sortie existante et d'un lien symbolique parent ; aucun écrasement.
- Rejeu identique des sections. Variante séparée sans cache local ni journal : inconnues explicites et nouvelle paire d'empreintes indépendante.

`unit.json`, `result.json` et `runner.json` donnent des **assertions nommées**, pas des nombres PHPUnit. Les paquets RED historiques restent historiques. Seul le paquet final désigné dans `production/A-02/notes.md` correspond aux fichiers actuels. Le vérificateur refuse une dérive de contenu **ou d'inventaire** des sources.

## Commande opérateur, après autorisation sur une copie vérifiée

Dans le conteneur disposant de PHP 8.2+ et `pdo_mysql`, avec répertoire de destination parent existant, vide de tout rapport précédent :

```text
php /chemin/du/depot/wp/outils/bascule/audit --wp-path=/chemin/de/la/copie-verifiee --output=/hors-racine-web/audit-AAAAMMJJ
```

Cette commande n'a **pas** été lancée sur Imagine. Elle n'est volontairement pas ajoutée à `bascule/lancer`, qui ne prend que les transformations numérotées. `audit` reste autonome et en lecture seule.

L'auditeur tokenise les cinq coordonnées littérales de configuration sans exécuter le fichier. Il utilise seulement SELECT dans une transaction READ ONLY et lit les en-têtes/sources/journal. Il crée uniquement `audit.md` et `audit.json` dans un nouveau répertoire externe au site (0700 ; fichiers 0600). Les erreurs sont des codes fermés, jamais le SQL, ses valeurs ou une trace.

## Limites explicites

- Site simple, disposition `wp-content` standard, `DB_*` et préfixe littéraux au niveau supérieur ; environnement dynamique, multisite, symlink ou fichier trop gros refusé sans exécution.
- PHP observé = runtime **CLI** exécutant l'audit, pas une promesse sur un autre pool PHP-FPM.
- Dernières versions et date de maintenance : uniquement le cache local disponible ; `null` si absent. Une réponse périmée n'est pas un contrôle frais du fournisseur. Aucune interrogation réseau par l'audit.
- Passerelles = implémentations statiques présentes dans les sources actives, pas leur activation fonctionnelle. L'héritage est suivi entre fichiers de la même extension, sans le préfiltre du nom Woo. Les classes non résolues (ascendance manquante ou ID non statique, y compris un enfant dynamique) sont signalées dans `gateway_unresolved`; une classe sans lien passerelle n'est pas un moyen de paiement. PayPal historique peut être livré par Woo sans être enregistré. Imports PHP simples et namespaces sont reconnus ; imports groupés, traits, fabriques, filtres et contrôle de flux dynamique nécessitent une revue distincte. Aucun fichier tiers n'est exécuté.
- Types/taxonomies stockés plus socle WordPress vide connu ; les types dynamiques vides non observables sans bootstrap ne sont pas inventés. Constructeurs : noms connus d'extensions/thèmes actifs, détection non exhaustive.
- Registre de tables conservateur WordPress/Woo/WCS/Action Scheduler. « non attribuée » est une **candidate à examiner**, jamais un diagnostic certain ni une autorisation de suppression.
- Règles Memberships enregistrées, pas validation de tous les droits effectifs. Les plans/objets ont des ID pour éviter la fuite possible de titres personnels.
- Journal conventionnel `wp-content/debug.log`, dernier 4 Mio, noms de fonctions/méthodes dépréciées seulement ; chemin personnalisé ou autres formats non explorés.
- Taille physique estimée par `information_schema`; décompte SELECT exact. L'empreinte n'est pas un hash des fichiers InnoDB ni des statistiques internes du moteur. Tables non transactionnelles signalées.

Vérification documentaire publique séparée et facultative : `python wp/tests/a02-audit/documentation.py` (réseau public uniquement, pas pendant la fixture). Références et empreintes dans `production/A-02/sources-officielles.json`. `style.py` est un contrôle PHPCS supplémentaire, hors replay fonctionnel, utilisant uniquement le PHAR public SHA-256 figé dans le scratch Hermes, jamais PHP hôte ; ses avertissements et son vrai code retour sont conservés dans `production/A-02/style/`.
