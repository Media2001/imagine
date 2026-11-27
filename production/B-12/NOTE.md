# B-12 — verrou du corps, avant consentement

## Réception actuelle — arbitrage de 16h30 appliqué

**Réception actuelle : `reception-contrat-V2.json` ; le lecteur sans argument et `--live` utilisent ce contrat.** La file a changé pendant ce travail : l'instruction 3 de la fusion est remplacée. Le bootstrap partagé n'est **plus scellé intégralement** : `SOURCES` reste l'égalité stricte des fichiers propres B12 ; son **unique bloc d'enregistrement exact** est contrôlé séparément. Le README se limite à la section B12, bornée avant le titre du lot suivant. Une ligne d'un futur lot ne périme plus B12 ; suppression, altération ou duplication du bloc B12 et source B12 changée restent refusées. **7 tests de contrat** ajoutés aux 6 historiques et 11 tests de correction. En live, empreinte du vrai fichier fonctionnel B12 et bloc B12 exact relus, aucun contrôle du bootstrap entier ni du PRET voisin.

La correction fonctionnelle reste une seule comparaison `strcasecmp`, permissions intactes. Après le dernier changement des outils de preuve : nouveaux reçus `contrat-native-final-V2.json`, `contrat-mutation-final-V2.json`, `contrat-routes-final-V2.json`, image et rejeu `contrat-image-V2*` / `contrat-replay-V2*`. Résultats frais : **56 + 52 contrôles natifs**, zéro tentative avec verrou ; mutation 15 contrôles / 6 tentatives B00 avant transport, corps/essais/options restaurés. Rejeu **1 204 tests / 36 667 assertions**, B12 **6 tests / 47 assertions**, 22 outils / 720 contrôles sans échec ; A31/A32 rouges inchangés. Syntaxe de 6 fichiers PHP vérifiée. Limites : WP-CLI/REST en processus et non capture UI/HTTP navigateur ; B11 `UI_save_verified=false` ; AUTO_INCREMENT peut avancer malgré rollback.

Le complément C29 avait été vérifié avant l'arrivée de cet arbitrage et reste conservé **comme preuve historique**, avec `reception-corrections-V2.json` et les PRET précédents. **Il n'est pas une dépendance du contrat courant et aucune réception complémentaire de voisin n'est désormais requise pour une ligne d'amorçage.** Les lecteurs historiques B11/C28/C29 peuvent rester rouges, règle expressément acceptée à 16h30 ; aucun resceau silencieux. B11 et C29 doivent passer eux aussi au contrat : à faire par le parent, hors du périmètre d'écriture de ce sous-agent. Ni code fonctionnel ni dossier de production de ces voisins modifié.

À chaque montée de version WordPress, rejouer les deux matrices natives et leurs mutations avant clôture ; les doublures scellées ne prouvent pas le pipeline réel. Ancien PRET B12 conservé dans `PRET-avant-corrections-V2` ; PRET de la correction avant arbitrage conservé dans `PRET-avant-contrat-V2`. Le PRET courant nomme seulement `reception-contrat-V2.json`.

## Checkpoint de correction avant lecture de la nouvelle file — historique, non réception actuelle

**Six instructions de `corrections/B-12.md` appliquées ; réception courante `reception-corrections-V2.json`.** Le bootstrap C29 n'a pas été modifié. La seule correction fonctionnelle est `strcasecmp` sur la route proxy ; URL, erreurs et permission `edit_posts` gardent leurs gardes.

- Rouge avant code (`correction-red-route-V2.json`) : `PROXY` et `PrOxY` sans cache → **2 tentatives B00 bloquées avant transport** ; avec transient natif ancien → **iframe et vignette restituées**. Après correction : **52 contrôles / 6 cas**, routes canonique/MAJ/mixed × cache absent/ancien, lien exact seul et **zéro tentative**, ni iframe ni vignette. Les anciens transients sont d'abord réellement consommés par le proxy sans le filtre B12 : témoin positif de la clé native avec ses paramètres par défaut. Anonyme et éditeur privé d'`edit_posts` refusés dans les six cas.
- Mutation de **la vraie source PHP déployée** réintroduisant la comparaison sensible à la casse → même rouge ; octets exacts restaurés et relus, matrice verte (`correction-mutation-case-V2*.json`). Matrice générale fraîche : **56 contrôles**, zéro tentative ; mutation du verrou retiré : **15 contrôles / 6 tentatives B00 / zéro transport**. Articles, transients et probes retirés, état métier strictement restauré y compris après rouges.
- Image reconstruite : `sha256:97d17acd629b81a692b9bc6fe62649742eb70d586883eefa994618f823aba891`. Rejeu frais : **1 204 tests / 36 667 assertions**, 22 outils / 720 contrôles, zéro échec/erreur/ignoré de suite. C29 était à 1 203 / 36 657 avant ce nouveau test. B12 : **6 tests / 47 assertions** ; lecteurs **6 historiques + 11 nouveaux tests** ; syntaxe **6 fichiers PHP**. Sources finales liées aux trois reçus natifs courants ; les anciens nombres des JSON historiques ne sont pas un rejeu frais.
- **Complément C29 réutilisé après vérification**, dans `correction-bootstrap-C29-V2.json` : bootstrap courant entier **e27ee706…** ; retirer l'unique bloc C29 exact (lignes 178–181 : chargements ContactBrevoRegles/ContactBrevo et enregistrement) redonne **9530b508…**, empreinte historique B12. Branchement B12 lignes 174–176 inchangé octet pour octet. Sceaux/sources/preuves C29, portion README C29 et sources voisines B11/C28 vérifiés. Bloc C29 changé, branchement B12 changé, ajout étranger → refus. **`SOURCES` reste une égalité stricte sur l'arbre courant**, aucune empreinte remplacée dans le dictionnaire.
- `rejouer.ps1` utilise des **doublures maison** : il ne prouve pas le pipeline natif. La preuve zéro sortie vient de `b12-runtime.php` et de son complément `b12-routes-runtime.php` sur le vrai WordPress gardé. Ce n'est ni une capture UI Gutenberg ni une requête HTTP authentifiée externe.
- **À chaque montée de version du cœur WordPress, rejouer la matrice native avant clôture** : handlers/cache et dispatch/permissions/transient dépendent d'un ordre interne non contractuel. Inclure enregistrement/cache, rendu, proxy canonique/MAJ/mixed, cache absent/ancien, permissions et mutations.

### Conservation et limite du lecteur historique C29

Anciens reçus B12 et compléments B11/C28/C29 bruts et intacts. C29 a été relu **PASS hors ligne et live avant renouvellement du PRET B12**, puis ses sources, preuves, README propre, bootstrap et PRET sont vérifiés inchangés par le complément courant. Son lecteur historique figeait aussi l'ancien PRET B12 : celui-ci est conservé **octet pour octet** dans `PRET-avant-corrections-V2`, vérifié contre le sceau C29. Le nouveau PRET nomme la réception corrigée ; le lecteur C29 brut signale donc `HISTORICAL_PACKETS` sur ce seul pointeur ancien. Utiliser le nouveau lecteur B12 et son complément C29 pour l'arbre courant ; aucun lecteur historique n'est présenté comme un rejeu neuf et aucun reçu C29 n'est rescellé silencieusement. Les refus bruts B11/C28 restent documentés. A31/A32 restent hors lot, rouges intacts.

Sources officielles complémentaires consultées HTTP 200 : matcher REST (`@i`) et clé/cache du proxy, dans `correction-standard-V2.json`.

## Conception et historique initial (hors chiffres courants ci-dessus)

**Prêt technique à relire, site fictif seulement.** Aucune saisie UI automatisée revendiquée : preuve dans le vrai WordPress 7.0.9, via WP-CLI, enregistrement natif + cible de cache AJAX, rendu natif et véritable route REST distribuée en processus. La limite B11 `UI_save_verified=false`, acceptée à 13h30, est inchangée. Aucun champ B11, paywall ou réglage nouveau.

## Standard d'abord — cinq lignes
1. Une adresse seule (ligne/paragraphe), le bloc natif `core/embed` et `[embed]` passent par `WP_Embed` ; les handlers sont consultés avant le cache et les fournisseurs.
2. À l'affichage, `autoembed()`/`run_shortcode()` résolvent ; le handler natif `wp_embed_register_handler`, priorité `PHP_INT_MIN`, rend un lien pour une URL externe et délègue l'interne avec `false`.
3. Après sauvegarde, le cache natif `cache_oembed()` est demandé par l'AJAX `oembed-cache` : le même handler ferme la résolution ; `pre_oembed_result` couvre aussi `wp_oembed_get()` direct.
4. Le bloc conserve parfois du HTML ancien : `pre_render_block` coupe avant ce HTML pour empêcher le retour d'un ancien cadre/script/vignette, sans changer le corps enregistré.
5. L'éditeur utilise `/oembed/1.0/proxy`, qui appelle `get_data()` et lit son transient avant les handlers : `rest_dispatch_request` court-circuite après permissions et avant ce cache ; ni `pre_oembed_result` seul ni `rest_request_before_callbacks` ne suffisent.

Références officielles : `sources-officielles-V2.json`, sept pages Developer.WordPress.org réellement consultées (200), et lecture des trois classes natives installées. La première tentative avec `rest_request_before_callbacks` a été détectée rouge et corrigée ; diagnostics conservés, pas de succès inventé.

## Preuve et restauration

- Test préalable sans verrou : **6 tentatives**, couvrant save/render/preview pour URL seule et bloc, toutes arrêtées par B00 `imagine_demo_offline` avant transport. Test d'acceptation rouge `apercu_0_lien` avant code.
- Mutation finale retirant les quatre branchements B12 en mémoire seulement : **15 contrôles**, 6 tentatives B00, zéro transport. Verrou remis dans la requête suivante : **56 contrôles**, **zéro tentative**, B11 OFF et ON. URL seule, bloc, shortcode, résolution directe et caches HTML/transient anciens testés.
- Deux vrais articles temporaires à chaque passage ; corps avec antislash relu exactement après sauvegardes, cache et rendus. Suppression explicite relue, puis rollback ; état métier avant/après strictement identique. Aucun essai ni observateur laissé. Les compteurs InnoDB AUTO_INCREMENT peuvent avancer malgré le rollback : ce n'est pas une modification de contenu métier.
- Interne constaté inchangé : handler délégué, résultat de résolution conservé, bloc identique et réponse native du proxy comparée avec/sans B12 (seul le secret aléatoire natif d'iframe est normalisé). Liens ordinaires conservés. Permissions du proxy inchangées.
- Image initiale reconstruite avant réception historique ; ses compteurs et ceux de PHPUnit/lecteur sont conservés dans les reçus initiaux. **Les seuls chiffres courants sont ceux du rejeu frais en tête de cette note : 1 204 tests / 36 667 assertions, B12 6 tests / 47 assertions.**
- Deux paquets étrangers restent rouges : **A-31 `A31_PARTIAL_EVIDENCE`**, **A-32 `A32_PACKAGE_DRIFT`**. Signalés, jamais modifiés.

## Bootstrap partagé — réception complémentaire du même réveil

`imagine-site.php` reçoit seulement le bloc B12 additif. `reception-complement-voisins-V2.json/.log` conserve les anciens paquets : B11 32 hors ligne + 35 live, C28 31 + 37, C27 628 contrôles, plus adaptateurs natifs B11 23 et C28 25 rejoués sous rollback. Pour B11/C28, toutes les sources sont identiques aux sceaux, sauf bootstrap : enlever **l'unique bloc B12 exact** retrouve son empreinte historique. Ce contrôle de portion est explicite ; les fichiers déployés restent contrôlés intégralement. Les reçus historiques n'ont pas été écrasés. Les anciens vérificateurs bruts B11/C28 signaleront donc toujours la dérive globale du bootstrap ; utiliser ce complément pour leur réception sur l'arbre B12.

## Quand le consentement existera — trois lignes
1. Remplacer ce verrou inconditionnel par une décision serveur de consentement effectivement disponible, sans utiliser le réglage B11 comme preuve de consentement.
2. Lever ensemble handler, résolution directe, bloc et proxy, avec traitement des anciens caches et absence de chargement tiers tant que le consentement manque.
3. Rejouer mutation négative, enregistrement/cache, rendu et aperçu, OFF/ON, ainsi que la réception des voisins ; aucune levée automatique n'est livrée ici.

Périmètre : intégrations natives URL/bloc/shortcode `embed`, pas un assainisseur universel de HTML arbitraire ni un inventaire de toutes les ressources de la page. Aucun test C26 étendu, aucune bibliothèque close changée, aucun tiers contacté depuis le site, email ou paiement sortant.
