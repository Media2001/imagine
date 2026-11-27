# B-12 — verrou du corps, avant consentement

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
- Image reconstruite avant réception ; **1 200 tests / 36 610 assertions, zéro échec/erreur**, 22 outils / 720 contrôles verts. PHPUnit B12 : **5 tests / 37 assertions** ; lecteur de preuves : **6 tests** ; syntaxe : 5 fichiers PHP.
- Deux paquets étrangers restent rouges : **A-31 `A31_PARTIAL_EVIDENCE`**, **A-32 `A32_PACKAGE_DRIFT`**. Signalés, jamais modifiés.

## Bootstrap partagé — réception complémentaire du même réveil

`imagine-site.php` reçoit seulement le bloc B12 additif. `reception-complement-voisins-V2.json/.log` conserve les anciens paquets : B11 32 hors ligne + 35 live, C28 31 + 37, C27 628 contrôles, plus adaptateurs natifs B11 23 et C28 25 rejoués sous rollback. Pour B11/C28, toutes les sources sont identiques aux sceaux, sauf bootstrap : enlever **l'unique bloc B12 exact** retrouve son empreinte historique. Ce contrôle de portion est explicite ; les fichiers déployés restent contrôlés intégralement. Les reçus historiques n'ont pas été écrasés. Les anciens vérificateurs bruts B11/C28 signaleront donc toujours la dérive globale du bootstrap ; utiliser ce complément pour leur réception sur l'arbre B12.

## Quand le consentement existera — trois lignes
1. Remplacer ce verrou inconditionnel par une décision serveur de consentement effectivement disponible, sans utiliser le réglage B11 comme preuve de consentement.
2. Lever ensemble handler, résolution directe, bloc et proxy, avec traitement des anciens caches et absence de chargement tiers tant que le consentement manque.
3. Rejouer mutation négative, enregistrement/cache, rendu et aperçu, OFF/ON, ainsi que la réception des voisins ; aucune levée automatique n'est livrée ici.

Périmètre : intégrations natives URL/bloc/shortcode `embed`, pas un assainisseur universel de HTML arbitraire ni un inventaire de toutes les ressources de la page. Aucun test C26 étendu, aucune bibliothèque close changée, aucun tiers contacté depuis le site, email ou paiement sortant.
