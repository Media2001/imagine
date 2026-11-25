# A-12 — résultat de la livraison

**Verdict : PARTIEL_NON_PRET. Aucun `production/A-12/PRET`.**

## Acquis vérifiés

Le collecteur dédié est `wp/outils/bascule/a12/inventorier-contenus`. Sorties privées JSON/Markdown, liées par SHA-256 à l'audit A-02 frère, hors racine web et hors dépôt. Aucun fichier partagé ni README d'audit modifié ; les deux lignes à intégrer sont dans `integration.md`.

Dernier rejeu : `preuves/final/`, source manifest exact de **14 fichiers**. **100 assertions natives**, **5 assertions pures**, **7 contrôles runner**, **6 contrôles style** et **32 contrôles d'intégrité** réussis ; zéro échec dans ces suites bornées. Ce ne sont pas des nombres PHPUnit et ce n'est pas une réception complète du brief. PHPCS PSR-12 strict : exit 0, zéro erreur, zéro avertissement. Les recettes du cahier des charges et le rejeu global T01 ne sont pas étendus.

Banc A-02 inchangé : WordPress 7.0.9, Woo 11.1.1, Subscriptions 9.4.1, Memberships 1.30.3 ; mode classique puis HPOS. Pour chaque mode, empreintes de **55 tables** identiques avant/après, schémas et toutes lignes logiques compris, options/cron et Action Scheduler inclus. Empreintes des fichiers du site identiques ; piège de bootstrap absent ; compte du sujet SELECT seul ; UPDATE zéro ligne sous root réellement refusé par la transaction READ ONLY. Conteneurs propres A-12 sans réseau/montage/port, supprimés puis absence relue.

Comptes prouvés : cinq contenus de quatre états, type vide et type déclaré dans le thème, champs dupliqués comptés par contenu distinct, taxonomie de 23 rubriques et vingt premières exactes, dates UTC limitées aux publications, deux PDF (23 et 28 octets, un PDF orphelin), liens produits directs/inverses, clés différant par casse, données sérialisées non interprétées. Le placeholder natif Woo explique quatre médias/deux parents nuls **au total** ; l'oracle natif est conservé, aucun média n'a été supprimé pour réduire ce total. Absence des titres/textes/valeurs/contacts et noms de médias dans les rapports, permissions et refus de chemins/configurations/audits invalides vérifiés.

## Exigences non acquises

1. **Registre effectivement enregistré et attribution exacte** : non prouvés. L'analyse sans bootstrap restitue les objets stockés et les appels littéraux candidats, pas les registres exécutés. Le banc observe un type dynamique réellement enregistré (`a12_dynamic`) absent de l'inventaire, et un appel conditionnel non exécuté (`a12_never`) présent comme candidat. Les fichiers `*-registry-gap.json` conservent les autres écarts natifs. `registry.runtime_verified=false` partout ; aucun compte exact de registre n'est prétendu. Les taxonomies/déclarations dynamiques ont la même limite générale. Une stratégie runtime sûre doit être qualifiée avant `PRET`.
2. **Préparation de l'image partagée avant PRET** : non exécutée, explicitement réservée au parent. L'image A-02 et les dépendances T01 déjà présentes ont été réutilisées sans rebuild ; leurs IDs inspectés sont dans les reçus. Le paquet dédié n'ajoute pas de package Composer au banc global.
3. **Deux lignes dans le mode d'emploi partagé** : fournies séparément au parent dans `integration.md`, pas appliquées à un fichier hors ownership. Les marquer « registre partiel » tant que le point 1 n'est pas résolu.

## Décisions prises à défaut

J'ai privilégié le READ ONLY sans bootstrap établi par A-02 plutôt que de charger des extensions susceptibles d'écrire ou d'envoyer. Les appels statiques restent explicitement des candidats ; je ne rebaptise pas leur réussite partielle en conformité du brief. Aucun choix de rattachement, de droits, de paiement ou de modèle éditorial.

Orphelin signifie parent nul/inexistant, pas inutilisé. Poids signifie originaux locaux, pas miniatures. Les liens ne sont reconnus que pour les scalaires canoniques et clés explicitement décrites. Valeurs suspectes dans les seuls noms de rubriques autorisés : masquées. Ces conventions sont dans chaque rapport et le README.

## Commandes effectivement exécutées pour le paquet final

```text
python wp/tests/a12/style.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a12-work/final-style
python wp/tests/a12/run.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a12-work/final-native
python wp/tests/a12/verify.py C:/Users/Ced/AppData/Local/hermes/cache/scratch/a12-work/final-native
python wp/tests/a12/verify.py production/A-12/preuves/final
```

Le dossier de style a été copié sous le paquet natif ; les empreintes de sources concordent. Ne pas réutiliser ces destinations déjà existantes pour un nouveau rejeu.

Les RED et essais intermédiaires sont seulement dans le scratch `a12-work/` : analyseur absent, collecteur absent, ajout du sous-compte PDF orphelin, fermeture d'erreur au chargement et distinction de casse des clés. Un premier gate trop large a aussi observé des changements concurrents de fichiers A-10 ; rien n'a été restauré ou modifié dans ces fichiers. Le gate final porte sur les dépendances A-02 effectivement lues, et leur inventaire est stable. Les échecs de style intermédiaires ont été corrigés avant le dernier double rejeu.

Références officielles publiques : `standards.md`, `sources-officielles.json`. Aucun réel, compte, archive Imagine, secret, site de staging, bootstrap production, envoi, achat, déploiement ou opération Git. Aucun rapport réel ne doit rejoindre ce dépôt.
