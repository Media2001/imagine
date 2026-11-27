# B-11 — vidéos, podcasts et sommaire audio

## Réception courante — politique du 27 novembre 2026, 13h30

**PRET technique selon les critères adaptés de 13h30. Limite : aucune saisie/enregistrement/rechargement UI automatisé des deux éditeurs n'est revendiqué.** Le parcours de trois lignes pour Ced est en tête d'`A-VOIR.md`. Atteignabilité établie d'abord par lecture du code natif installé et enregistrement/rendu réels de la boîte ; persistance prouvée sur le vrai backend WordPress. Réception neuve : `reception-politique1330-V2.json`, et non les réceptions historiques. Ni validation visuelle, ni clôture, ni GO réel.

### Champ atteignable : aucune correction de déclaration nécessaire
`Medias::register()` déclare `imagine-medias` pour `post` et `imagine_numero`, contexte natif par défaut `advanced`, callback `champs`, arguments `null`. Dans le WordPress installé, `the_block_editor_meta_boxes()` (`wp-admin/includes/post.php:2376–2546`) propose les trois emplacements, dont `advanced`, à `setAvailableMetaBoxesPerLocation`. `do_meta_boxes()` (`template.php:1304–1469`) est compatible blocs par défaut ; seule une déclaration back-compat/incompatible peut l'écarter. Aucun de ces drapeaux ici. Le vrai registre filtré et le rendu natif contiennent les deux champs et le nonce pour 11 et 3454 : **11 contrôles verts**, `politique1330-editeurs-final-V2.json`. Les blocages de clic historiques ne prouvaient donc pas une boîte non proposée. Aucun changement fonctionnel de B11, aucun filtre d'éditeur ajouté, aucune nouvelle lutte UI.

### Vrai formulaire passif : 16 valeurs effectives, OFF → ON → OFF
`politique1330-final-V2-details.json` conserve les **16 options avant/après chacun des trois vrais POST** `options.php`, leurs valeurs effectives, présence SQL, défauts et empreintes PHP strictes (types compris). Aucun préremplissage d'autres options, aucun `allowed_options` réduit. Une ligne déjà présente est comparée telle quelle, sans assainissement de relecture qui cacherait une différence. Un écart réel reste rouge et attribuable au propriétaire, jamais réparé par B11.

Absente → explicite au **défaut exact**, acceptées et listées dans le reçu :
- `imagine_decouverte_reglages` (C12) : `ouverture=fermee`, `forme=articles`, `jours=7`, `nombre=2`, `numeros=[]` ;
- `imagine_decouverte_relecture` (C12) : `fermee` ;
- `imagine_solidaire_categories` (C17) : `["à préciser"]` ;
- `imagine_newsletters_creation` (C22) : `non` ;
- `imagine_retractation_reglages` (C25) : `jours=14`, `origine=paiement`.

Précision : ces cinq défauts sont enregistrés dans les **appels `get_option` du code propriétaire**, pas dans l'argument `default` de Settings API. La sonde relit ces mêmes valeurs, ancre de code vérifiée ; elle n'enregistre/injecte aucun défaut nouveau. Les défauts réellement déclarés à Settings API sont lus dans `get_registered_settings()`. Les cinq valeurs devenues explicites sont strictement identiques aux défauts effectifs ; **aucune différence métier**.

### Preuve réellement rejouée sur C28/C27 stabilisés
- Recette adaptée : **102/102**, zéro erreur, **32 sorties étanches non vides**, 32 témoins C26 inchangés ; 36 injections de réponse détectées, distinctes des deux mutations réelles des gardes article/audio.
- Changement et effacement des deux champs/deux objets dans OFF et ON : vrai hook `save_post`, nonce/capacité natifs, readback neuf ; ce n'est pas un POST navigateur de l'éditeur. Témoin API transactionnel distinct après code final : **8/8**, deux courts-circuits d'écriture détectés, rollback et état métier relus (`politique1330-ecritures-V2.json`). Hôte interdit et antislash refusés sans perte.
- Gravatar public : requête réellement déclenchée depuis la page publique identifiée, contrôle rouge, coupée avant transport ; exception toujours bornée au contexte admin **et** à son origine `/wp-admin/`. OFF/ON : aucun tiers public, aucun HTTP/oEmbed/mail B11.
- **54** tentatives Novamira, **2** dispatchs locaux Action Scheduler et **6** observations HTTP ambiantes : tous bloqués par B00. Les deux dispatchs sont qualifiés par hôte local exact, chemin `/wp-admin/admin-ajax.php` et les deux méthodes natives de leur pile ; aucun joker sur les requêtes locales. **9** Gravatar admin coupés. Le premier passage avait rougi sur ces dispatchs non encore qualifiés ; reçus bruts conservés sous `avant-qualification-loopback-*` et `avant-qualification-AS-*`, tests rouges puis verts. Le GIF tiers de l'ancien parcours éditeur n'est pas excepté : les éditeurs ne sont simplement plus visités dans cette recette adaptée.
- PHPUnit B11 **4 tests / 34 assertions**, natif **23/23**, **9 tests** d'assertions (dont contre-exemples des défauts et de la qualification réseau). Image reconstruite après ajout des tests ; vrai rejeu **1 195 tests / 36 573 assertions**, outils **22 / 720**, verts. Bilan distinct : 12 paquets, 2 rouges hors lot (`A31_PARTIAL_EVIDENCE`, `A32_PACKAGE_DRIFT`), laissés intacts.
- **16 restaurations relues** : lignes possédées, métas, options avec retour à l'absence, préférences, sessions, styles, sources et état métier ; deux sondes absentes. Aucun nouveau compte, profil, droit, achat ou paiement permanent.

### Historique et voisins
`reception.json`, `reception-corrections-V2.json`, leurs reçus et les documents de blocage `*-historique-bloque-1258-V2.md` restent conservés. Les anciens hashes ne sont pas remplacés par ceux de l'arbre courant. Seule la section B11 du README partagé est actualisée ; C27/C28 non clos sont vérifiés en complément dans `politique1330-voisins-V2.json`, sans réécriture de leurs paquets.

### Limites reportées, sans fonction nouvelle
L'oEmbed natif si l'URL est collée dans le corps relève du **futur B12**, non implémenté ici ; le `catch (Throwable)` de Paywall reste intact. L'écart partagé C28→B11 et ces deux limites sont déjà reportés par Claude selon la nouvelle file ; aucun écrit dans `docs/ecarts.md`. Consentement/fournisseur non choisis ; lecteur intégré absent ; validation visuelle de Ced toujours attendue.

<details>
<summary>Note historique avant corrections — provenance conservée, ne fonde plus PRET</summary>

## Le standard d'abord — cinq lignes
1. Une URL isolée dans le corps d'un contenu peut être transformée par `WP_Embed::autoembed()` en lecteur intégré ; un champ de métadonnées séparé n'entre pas dans ce filtre.
2. `WP_Embed::cache_oembed()` parcourt le corps pour mettre les intégrations en cache : déplacer seulement l'iframe au rendu ne supprime donc pas les demandes liées à l'enregistrement.
3. Le fournisseur oEmbed est interrogé côté serveur par `wp_safe_remote_get()` ; B11 ne demande ni oEmbed ni miniature et n'enregistre jamais ses adresses dans le corps.
4. Un lien HTML explicite ne charge pas le lecteur ou l'image du tiers ; l'intégration de B11 reste un emplacement vide quand son réglage est ON.
5. Le navigateur fournit `<audio controls>` ; `preload="none"` est une indication, pas une barrière d'accès : l'URL locale réévalue les droits à chaque GET/HEAD.

Documentation officielle consultée le 27 novembre 2026 :
- https://developer.wordpress.org/reference/classes/wp_embed/autoembed/
- https://developer.wordpress.org/reference/classes/wp_embed/cache_oembed/
- https://developer.wordpress.org/reference/classes/wp_oembed/_fetch_with_format/
- https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/audio

## Le jour du consentement — trois lignes
Choisir le gestionnaire de consentement et les fournisseurs autorisés ; ne pas assimiler le réglage ON à un consentement reçu.
Brancher la création du lecteur uniquement sur un consentement approprié, réversible, et conserver le lien sans cookies en solution de repli.
Rejouer l'observation serveur/navigateur avant et après accord/retrait : aucun fournisseur, script, vignette ou oEmbed avant accord.

## Décisions prises à défaut
- Hôtes vidéo exacts, sans sous-domaine implicite, liste vide = fermé. Livraison : un seul hôte fictif, `video-fictive.example.invalid`. HTTPS, aucun port explicite/identifiant/contrôle/antislash ; un mauvais champ refuse les deux nouveaux liens et conserve l'existant.
- Option `imagine_medias`, clés `hosts`, `integration` chaîne `0|1`, OFF livré. Section additive sous le bouton C10 comme les lots précédents ; aucune modification du code C10.
- Métadonnées protégées `_imagine_video`, `_imagine_podcast`, non enregistrées pour REST ; aucune donnée visiteur, aucune intégration tierce. Ne pas coller une URL brute dans le corps natif : le mécanisme oEmbed général des autres lots n'est pas désactivé par B11.
- Les articles utilisent `Paywall::decision()`, et l'audio **exactement** `Paywall::decisionPdf()` : même moteur C06, même type PDF et même dossier privé/en-têtes de C11, sans modifier leurs sources. Aucun nouveau droit, plan, commande, paiement ou profil.
- PCM WAV mono 16 bits, 8 kHz, trois secondes de silence fabriqué : 48 044 octets ; SHA-256 `59db6dfb709393b7aab8efcc2b395df4def43f1c976d8b157bb9009dbacdc0ec`. Blob privé aléatoire, mode 0600, pas de pièce jointe publique. Seul dépôt local depuis le dossier C11 ; pas d'écran d'upload public ajouté.
- Deux numéros existants reçoivent ce même silence : 11 pour l'acheteur P-NUMERO, 39 pour A-CARTE actif. Le réglage C06 ferme l'audio/PDF antérieur de A-CARTE (motif `pdf_anterieur_ferme_par_reglage`) ; le forcer ouvert aurait créé un droit interdit. L'article fictif B11 est rattaché au 11 et reste lisible par A-CARTE selon la décision article C06 existante.

## Preuves et étanchéité
- RED conservés : classe de validation absente, puis adaptateurs absents sur le vrai site. Le premier essai audio sur le numéro 11 a réellement échoué pour A-CARTE ; la fixture a été complétée sur le 39 au lieu de changer un droit.
- PHPUnit dans le paquet racine ; recette WordPress transactionnelle séparée et recette navigateur/formulaires natifs. Refus hôte/antislash par vrai POST ; lecture metadata après sauvegarde ; deux réglages effectivement persistés puis rendus ; lecteur natif décodant trois secondes.
- GET binaires positifs acheteur/abonné, négatifs anonyme/connecté/expiré/suspendu/autre numéro, HEAD, 405 et 404 ; en-têtes privés. Témoins présents avec les bons profils avant l'absence ; deux mutations réelles et limitées aux gardes B11, réponses HTTP réellement fuyantes, puis sources restaurées et relues.
- Les 32 témoins réservés du reçu livré C26 sont réutilisés via son détecteur courant, sur les sorties B11 HTML, REST et alias, collection, flux, oEmbed, embed, recherche : aucune extension de la matrice C26, aucune réécriture de C23/C26 ou de leur historique. Les 36 injections de réponse brute sont uniquement des témoins de détecteur, pas présentées comme des mutations de sources.
- Les absences nouvelles sont précédées de pages/réponses identifiées et non vides. Les deux états de réglage ont de vraies requêtes navigateur observées ; les détecteurs réseau ont leur positif bloqué avant transport.

## Limites explicites
1. **Zéro B11 n'est pas zéro tentative de tout WordPress.** L'administration existante tente de vérifier des mises à jour Novamira. Ces tentatives sont identifiées par pile et hôte, comptées séparément, et le résultat `imagine_demo_offline` est observé après le coupe-circuit pour chacune : aucun transport. Les Gravatar admin sont aussi détectés et bloqués. Aucun appel B11/oEmbed, aucun chargement tiers public, aucun email/paiement. Rien n'est désactivé chez le tiers pour fabriquer le zéro.
2. **Premier essai interrompu dans l'éditeur blocs.** Il a créé un `wp_global_styles`, un verrou et des préférences admin ; les artefacts ajoutés sont retirés et les empreintes posts/postmeta rétablies (`recovery-01.json`). Une ancienne empreinte usermeta reste différente : la préimage du premier essai ne conservait que les sessions et pas toutes les préférences admin. Elle n'est ni reconstruite ni déclarée exactement restaurée. Les recettes suivantes prennent une préimage complète des lignes touchées avant toute session et restaurent leur état intégral, vérifié. Les états des commandes, abonnements, adhésions et réglages métier n'ont pas changé ; aucun profil C09 n'a été changé d'état.
3. La recette d'édition joue la boîte **classique native** : filtre temporaire limité aux IDs 11/3454, et `allowed_options` limité à l'option B11 pour ne pas resoumettre les autres sections C10. Elle ne prétend pas avoir validé la synchronisation de la boîte dans l'éditeur blocs. Les filtres ne sont pas livrés en permanence sur le site.
4. Pas de choix de consentement, de fournisseur réel, de téléchargement tiers, de diffusion CDN, d'upload audio dans les médias, ni de prise en charge Range ajoutée (même service complet que C11). WAV seulement sur ce squelette. Pas de style ou design nouveau ; validation visuelle de Ced attendue.
5. La suite générale peut afficher un paquet tiers rouge (A32 partiel connu), indépendamment de son verdict de tests ; B11 n'en corrige ni ne rescelle aucun.

Les résultats de cette section appartiennent à `reception.json`, historique. La réception adaptée courante et sa limite UI figurent en tête de ce document et dans `A-VOIR.md`.
</details>
