# A-12 — résultat de la livraison

**Verdict technique : NATIVE_VERIFIE. Le blocage registre est levé.** Le dépôt de `PRET` attend uniquement la lecture des deux formalités communes réservées au parent (préparation d'image et mode d'emploi). Aucun résultat de ces opérations n'est inventé ici.

## Acquis vérifiés

Le lanceur obligatoire est `python3 wp/outils/bascule/a12/confine.py` ; il exécute le collecteur PHP sous Landlock, dans un conteneur Linux déconnecté. Sorties privées JSON/Markdown liées par SHA-256 à l'audit A-02 frère, hors racine web et dépôt. Aucun fichier partagé ni README d'audit modifié par ce worker ; les deux lignes **mises à jour pour ce lanceur** sont dans `integration.md`.

Dernier rejeu : `preuves/final/`, manifeste exact de **16 fichiers source/test/documentation**. **118 assertions natives**, **7 assertions pures**, **7 contrôles runner**, **6 contrôles style** et **41 contrôles d'intégrité** réussis ; zéro échec. Ce sont des assertions nommées, pas des nombres PHPUnit. PHPCS PSR-12 strict : exit 0, zéro erreur et avertissement. Suite dédiée proportionnée au brief, pas de rejeu global T01.

Banc A-02 et sources/tests A-11 inchangés : WordPress 7.0.9, Woo 11.1.1, Subscriptions 9.4.1, Memberships 1.30.3 ; classique puis HPOS. Pour chaque mode : **55 tables** identiques avant/après, schémas et toutes lignes logiques, options/cron et Action Scheduler inclus ; fichiers du site identiques, configuration non exécutée. Connexion A-11 native déjà READ ONLY avant tout MU-plugin, gardée pour toutes les agrégations/métas/pièces jointes. Le sujet possède SELECT seulement. Sous root fictif, le serveur refuse réellement UPDATE (1792), le wrapper bloque COMMIT/changement de transaction ; HTTP/mail/cron refusés avant les extensions. Landlock ABI **7** observée : création et troncature dans le site effectivement refusées au code tiers. Conteneurs A-12 sans réseau/montage/port supprimés, absence relue.

Comptes prouvés : cinq contenus de quatre états, type vide et type déclaré dans le thème, champs dupliqués comptés par contenu distinct, taxonomie de 23 rubriques et vingt premières exactes, dates UTC limitées aux publications, deux PDF (23 et 28 octets, un PDF orphelin), liens produits directs/inverses, clés différant par casse, données sérialisées non interprétées. Le placeholder natif Woo explique quatre médias/deux parents nuls **au total** ; l'oracle natif est conservé, aucun média n'a été supprimé pour réduire ce total. Absence des titres/textes/valeurs/contacts et noms de médias dans les rapports, permissions et refus de chemins/configurations/audits invalides vérifiés.

## Registre acquis ; formalités du parent

1. **Registres natifs et attribution runtime : acquis.** Dans les deux magasins, **30 types et 18 taxonomies** exactement égaux à l'oracle ; `a12_dynamic` inclus, `a12_never` exclu, taxonomie calculée incluse, appels non exécutés et objets retirés exclus. Les deux fichiers `*-registry-gap.json` ont leurs listes vides. Fichiers déclarants cœur/WooCommerce/MU/thème exacts ; observation par hooks réels et pile sans arguments, pas d'analyse statique. L'ancien `Declarations.php` est supprimé.
2. **Préparation de l'image partagée avant PRET : responsabilité du parent.** Non exécutée par ce worker. Le runner de style a réellement inspecté/utilisé l'image `sha256:fde840f6e05fc66a4985114182f4edc0cf4090f43ac48d1d674b089baddc3377` ; cela ne fabrique pas un reçu de `preparer-image.ps1`. Aucun package Composer ajouté.
3. **Deux lignes communes : responsabilité du parent.** Fichier `integration.md` à jour ; ne pas intégrer l'ancienne commande PHP brute ni l'ancien avertissement de registre partiel. `coordination-parent.md` demande la référence du reçu de préparation et la lecture de l'intégration avant `PRET`.

## Décisions prises à défaut

J'ai réutilisé directement le runtime A-11 **sans toucher à aucun de ses fichiers**, plutôt que reconstruire un bootstrap ou une approximation statique. Ses hooks ne suffisent pas à neutraliser du PHP arbitraire : Landlock et le réseau coupé sont appliqués avant exec PHP, et les écritures de fichiers sont réellement éprouvées. Un déclarant hors API/illisible reste `unknown`. Registre photographié après `wp_loaded`, sans inventer d'autres contextes front/admin/REST. Aucun rattachement, droit, paiement ni modèle éditorial décidé.

Orphelin signifie parent nul/inexistant, pas inutilisé. Poids signifie originaux locaux, pas miniatures. Les liens ne sont reconnus que pour les scalaires canoniques et clés explicitement décrites. Valeurs suspectes dans les seuls noms de rubriques autorisés : masquées. Ces conventions sont dans chaque rapport et le README.

## Commandes effectivement exécutées pour le paquet final

```text
python wp/tests/a12/style.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a12-runtime/final-style
python wp/tests/a12/run.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a12-runtime/final-native
python wp/tests/a12/verify.py C:/Users/Ced/AppData/Local/hermes/cache/scratch/a12-runtime/final-native --save
python wp/tests/a12/verify.py production/A-12/preuves/final --save
```

Le dossier de style a été copié sous le paquet natif ; les empreintes de sources concordent. Ne pas réutiliser ces destinations déjà existantes pour un nouveau rejeu.

Ancien paquet partiel archivé hors dépôt dans `a12-runtime/previous-partial-final/`. RED runtime réellement observé dans `a12-runtime/red-runtime/` avant modification : l'exigence d'égalité du registre échouait. Essais intermédiaires au scratch seulement : garde de chemin du lanceur corrigée, cinq avertissements de longueur de ligne corrigés. Une seule livraison finale verte au dépôt, liée aux sources finales ; dépendances A-02 et A-11 stables. Aucun fichier d'un autre lot restauré/modifié.

Références officielles publiques : `standards.md`, `sources-officielles.json`. Aucun réel, compte, archive Imagine, secret, site de staging, bootstrap production, envoi, achat, déploiement ou opération Git. Aucun rapport réel ne doit rejoindre ce dépôt.
