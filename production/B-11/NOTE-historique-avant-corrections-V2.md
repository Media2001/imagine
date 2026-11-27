# B-11 — vidéos, podcasts et sommaire audio

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

Résultats exacts, commandes et données laissées : `A-VOIR.md`, `reception.json` et reçus nommés. PRET signifie candidat technique à relire, pas clôture de code, validation visuelle ou GO sur le réel.
