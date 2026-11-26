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
- Abonnements : une seule ligne par clé et abonnement est retenue **avant** l'agrégation, celle au plus petit `meta_id` classique / `id` HPOS. C'est une convention de projection déterministe, jamais une correction des données ni un arbitrage de facturation. Les doublons (identiques inclus) et contradictions binaires sont décomptés séparément par clé dans `subscription_meta_anomalies`, sans valeurs ni identifiants d'abonnés. Le banc injecte volontairement ces corruptions dans les deux magasins.
- Surcharges Woo : rôles `stylesheet` / `template` distingués ; l'enfant masque le même chemin relatif du parent. L'inventaire conserve le parent avec `masked_by_child` et `effective=false`, tandis que la priorité n°4 ne compte que les fichiers effectifs. Un fichier du parent sans équivalent enfant reste effectif.
- Articles annuels : `post_date_gmt`, étiquette `post_year_basis=UTC_creation`. La fixture distingue volontairement les années UTC et locale.
- `custom_fields` : **toutes clés postmeta, métas internes WordPress/Woo incluses**, noms et fréquences seulement, 50 premières. Ce n'est pas une sélection éditoriale.
- `requires_woo` est **conservé sans extension** de périmètre, comme métadonnée structurelle non sensible déjà livrée. Choix propriétaire toujours ouvert : Ced souhaite-t-il le conserver ou le retirer ? Aucune décision de Ced n'est prétendue. L'autre question ouverte reste l'extension éventuelle du registre des tables pour l'audit réel ; le registre conservateur actuel est inchangé.
- Taille physique estimée par `information_schema`; décompte SELECT exact. L'empreinte n'est pas un hash des fichiers InnoDB ni des statistiques internes du moteur. Tables non transactionnelles signalées.

Vérification documentaire publique séparée et facultative : `python wp/tests/a02-audit/documentation.py` (réseau public uniquement, pas pendant la fixture). Références et empreintes dans `production/A-02/sources-officielles.json`. `style.py` est un contrôle PHPCS supplémentaire, hors replay fonctionnel, utilisant uniquement le PHAR public SHA-256 figé dans le scratch Hermes, jamais PHP hôte ; ses avertissements et son vrai code retour sont conservés dans `production/A-02/style/`.
Complement A-10 : php wp/outils/bascule/inventorier-codes --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/codes-date
Lecture seule ; sortie soeur du rapport A-02, hors site et depot ; noms de codes autorises, emails comptes uniquement ; rejeu : python wp/tests/a10/run.py

Après l'audit, lancer `php wp/outils/bascule/a11/inventorier-adresses --wp-path=/copie-verifiee/site --audit=/rapports/audit-001/audit.json --output=/rapports/adresses-001` dans la même copie confinée, avec un dossier de sortie neuf, frère du rapport d'audit et hors racine web/dépôt.
`adresses.csv` (UTF-8, `;`) fournit `ancienne` pour A-09 ; `adresses.json` porte les données structurées, la preuve et l'empreinte du rapport A-02 pour l'outillage A-09 ; `resume.md` donne les comptes/bases, sans client ni décision ; refus de cache/pare-feu/lien nommé et marche à suivre : `a11/README.md`.
Complément A-12 (registre natif, lecture seule) : python3 wp/outils/bascule/a12/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/contenus-date
Conteneur Linux déconnecté + Landlock obligatoire ; types/taxos réellement enregistrés et comptes, jamais titres/valeurs ; rejeu dédié : python wp/tests/a12/run.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a12-rejeu-nouveau
Complément A-15 (emails natifs, lecture seule) : python3 wp/outils/bascule/a15/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/emails-date
Noms et oui/non uniquement, jamais destinataire/objet/corps ; conteneur déconnecté + Landlock, garde d'envoi éprouvée ; limites des services extérieurs et mode d'emploi : wp/outils/bascule/a15/README.md
Complément A-16 (dix derniers numéros, lecture seule) : python3 wp/outils/bascule/a16/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --correspondance=/hors-web/correspondance.json --output=/hors-web/numeros-date
Comptes et identifiants uniquement ; correspondance opérateur obligatoire, aucun rattachement ; confinement et limites : wp/outils/bascule/a16/README.md
Complément A-17 (sécurité des comptes, lecture seule) : python3 wp/outils/bascule/a17/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/securite-date
Comptes par rôle et oui/non, jamais identités/secrets ; adaptateurs 2FA et dernières connexions limités et inconnus explicites : wp/outils/bascule/a17/README.md
Complément A-18 (conservation, lecture seule) : python3 wp/outils/bascule/a18/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/conservation-date
Formes par clé et références de jetons, médias sans ouvrir leurs fichiers ; règles serveur : présence seule, protection inconnue ; neutralisation et limites : wp/outils/bascule/a18/README.md
Complément A-19 (cohérence, lecture seule) : python3 wp/outils/bascule/a19/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/coherence-date
Comptes croisés par état et plan, jamais identités ni décisions ; liens natifs, références de paiement et dix lignes sur le standard : wp/outils/bascule/a19/README.md
Complément A-20 (récurrences enregistrées, lecture seule) : python3 wp/outils/bascule/a20/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/tarifs-date
Comptes par produit/variation, rythme, total récurrent et pays ; groupes de moins de cinq masqués, aucune correspondance ; bases et limites : wp/outils/bascule/a20/README.md
Complément A-21 (portes vers l'extérieur, lecture seule) : python3 /chemin/du/depot/wp/outils/bascule/a21/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/portes-date
Comptes de clés et webhooks, connexion locale oui/non, inconnus après neutralisation ; aucun secret ni domaine ; standard, confinement et limites : wp/outils/bascule/a21/README.md
Magasin d’extensions A-21 : lecture directe de l’option native `woocommerce_helper_data` via `get_option()`, présence de `auth.access_token` seulement ; aucun appel à `WC_Helper::is_site_connected()`, aucune vérification distante.
