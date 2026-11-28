# Imagine — site (B-00, modèle provisoire)

## C-33 — comptes non publics en anonyme

### Le standard d’abord — cinq lignes
1. WordPress expose les archives d’auteur, et `redirect_canonical` transforme `?author=ID` en adresse d’auteur : https://developer.wordpress.org/reference/functions/redirect_canonical/ ; `template_redirect` avant cette redirection permet une vraie 404 sans adresse de compte.
2. Les routes natives REST `/wp/v2/users` et `/wp/v2/users/ID` donnent les auteurs publiés ; `rest_pre_dispatch` les ferme avant le contrôleur : https://developer.wordpress.org/reference/hooks/rest_pre_dispatch/.
3. Le fournisseur `users` du plan natif se retire avec `wp_sitemaps_add_provider` : https://developer.wordpress.org/reference/hooks/wp_sitemaps_add_provider/ ; les autres fournisseurs restent natifs.
4. `the_author` porte le nom dans RSS2/Atom ; `get_the_author_user_url` porte le site du compte dans Atom : https://developer.wordpress.org/reference/hooks/the_author/ ; les deux points d’accroche évitent nom et adresse de compte.
5. `oembed_response_data` remplace `author_name` et supprime `author_url` : https://developer.wordpress.org/reference/hooks/oembed_response_data/ . Sources officielles effectivement lues et empreintes du cœur installé : `production/C-33/standard-V2.json`.

Fermetures **uniquement anonymes**. Aucun comportement ni droit natif changé pour les connectés, notamment administrateur et éditeur ; pas d’extension de leurs droits. Routes REST insensibles à la casse et alias `rest_route` couverts. Les flux RSS2/Atom et l’oEmbed reprennent la signature B16, sinon le nom du site, jamais un repli sur le compte technique ; l’adresse de compte Atom est vide. RSS2 conserve sa CDATA (borne `]]>` protégée), Atom son échappement XML. Aucun gabarit B16 ni autre code clos modifié, aucun compte normal renommé ou altéré.

Le sitemap de la démo est **désactivé à l’état de repos** (`blog_public=0`). La recette le rend actif uniquement pour un témoin, puis restaure l’option exacte : index XML réel non vide, sans fournisseur utilisateurs. Dans ce cœur, l’ancienne adresse `wp-sitemap-users-1.xml` sans fournisseur retombe sur une page HTML 200 sans compte, et ne rend plus de plan d’utilisateurs ; aucune règle de serveur ajoutée pour fabriquer une 404 non demandée. Les autres plans observés : post, page, product, imagine_numero, imagine_evenement, imagine_partenaire ; aucun message de visiteur ni pièce privée dans cet index, aucun autre type corrigé.

Relecture : `python -B production/C-33/verifier.py --live`. Recettes natives et navigateur : `python -B wp/outils/demo/c33.py native LABEL`, `python -B wp/outils/demo/c33-browser.py LABEL`. Réponses anonymes brutes (sans cookies ni jetons), contrôles positifs de présence, six mutations sur cinq voies (index et détail du sitemap), administrateur/éditeur via leurs véritables API REST d’auteur/édition, et capture Edge. Compte et article fictifs supprimés, options de recette et cache natif d’invalidation restaurés depuis snapshot privé ; témoins C26 réutilisés, matrice inchangée. Le premier banc strict a laissé seulement une régénération de version du cache Woo à la suppression de son article : empreintes natives métier égales, cache historique non prétendu restauré ; FAIL conservé et snapshot de cette ligne ajouté pour les passages suivants. Aucune limitation de connexion, 2FA, règle d’hébergement, nouvelle collecte ou transmission. Pas de promesse de fermer les identifiants d’auteur des objets REST `posts`, hors périmètre de la liste de comptes demandée.

## C-31 — domaines refusés à l’inscription

Standard d'abord : WordPress `register_new_user()` filtre `registration_errors` avant insertion ; Woo `wc_create_new_customer()` filtre `woocommerce_registration_errors` avant `wp_insert_user`. Le checkout classique `WC_Checkout::process_customer()` appelle cette même fabrique. Un seul validateur pur raccordé à ces frontières, jamais un filtre global `wp_insert_user` qui toucherait C16/administration.
Sources officielles installées lues sur la démo, chemins/lignes/empreintes et appels constatés : `production/C-31/standard-V2.json`. Références documentaires : [register_new_user](https://developer.wordpress.org/reference/functions/register_new_user/), [registration_errors](https://developer.wordpress.org/reference/hooks/registration_errors/), source Woo `includes/wc-user-functions.php` et `includes/class-wc-checkout.php`.
Le changement d'email de Mon compte passe par `woocommerce_save_account_details_errors`, uniquement si l'adresse diffère de l'existante ; aucune révocation ni modification d'un ancien compte.

`DomainesRefusesRegles` compare le domaine exact sans casse. Un sous-domaine n'hérite pas du refus ; le déclarer sur sa propre ligne si nécessaire. ASCII/punycode saisi, pas de conversion IDN ni résolution DNS ; pas de wildcard/URL/email, pas de domaine réparé. Réglage `imagine_domaines_refuses`, liste vide par défaut ; démonstration avec trois domaines réservés en `example.org` manifestement fictifs. Écran propre « Réglages → Adresses à l’inscription », capacité manage_options et nonce Settings API. Liste normalisée et journalisée, restauration si journal en échec, sans mettre une adresse de lecteur dans le journal.

Message public neutre : utiliser une autre adresse email. Aucun stockage ni journalisation de l'adresse refusée. La création administrative et C16 utilisent `wp_insert_user`, hors de ces filtres ; aucune bibliothèque close modifiée. Pas d'appel sortant, téléchargement de liste, email ou service ajouté par le lot.

Tests : `python -B production/C-31/verifier.py` (puis `--live`). Vrais register_new_user, wc_create_new_customer, WC_Checkout::process_customer, hook natif Mon compte et vrais formulaires HTTP WP/Woo. Mutant : retirer le filtre Woo crée réellement un compte et fait échouer le contrôle d'absence ; témoin ciblé retiré, puis rollback et relecture. Comptes/options/profils/sessions restitués. Une limite **native hors lot** est explicite dans la preuve HTTP : le sélecteur de langue de wp-login tente deux appels à translations_api, tous bloqués par la sonde hors ligne ; aucun autre appel, aucun mail. Woo et C31 : zéro tentative, aucun octet sortant. Pas de prétention « zéro tentative du cœur WordPress ».

## C-30 — bienvenue et codes suivis

Le standard d'abord (sources officielles livrées par WooCommerce, lues sur la seule démo : `production/C-30/standard2-V2.json`).
L'attribution native utilise Sourcebuster, ses cookies `sbjs_*` et les métadonnées d'origine de commande ; elle n'est pas un catalogue de codes imprimés.
`OrderAttributionController.php` porte l'origine/UTM et une session d'attribution de 30 minutes ; aucun de ses traceurs n'est ajouté par ce lot.
Le code imprimé est une liste fermée distincte, sans JavaScript, prix, coupon, source du compte ni transmission.
`WC_Session_Handler` conserve la sélection côté serveur ; le navigateur ne reçoit que son cookie de session opaque HTTPOnly, à la durée native Woo, sans nouveau cookie de pistage.

`/bienvenue/?code=fictif-affiche` : page native, texte d'Imagine laissé vide, seul lien vers `Navigation::abonnementUrl()`. Seed idempotent `wp/outils/demo/c30-seed.py`, trois codes FICTIF. Réglages propres « Réglages → Codes suivis », capacité/nonce Settings API et journal C10 ; sur échec du journal relu sans cache, ancienne liste restaurée. Identifiants commençant par une lettre minuscule, puis minuscules, chiffres ou tirets, 1 à 40 caractères, libellé interne de 80 caractères ; liste vide par défaut.

Dernier code valide visité avant la commande gagne ; inconnu/absent ne remplace rien et ne démarre aucune session pour ce lot. Au checkout classique et au hook natif `woocommerce_store_api_checkout_order_processed` de Blocks/Store API, le candidat validé est conservé **provisoirement** en métadonnée privée `_imagine_code_suivi_candidat` : nécessaire aux paiements asynchrones sans navigateur. Il n'est jamais compté comme conversion. Au premier état payé avec date native, transfert vers `_imagine_code_suivi`, suppression du candidat et sceau sous verrou SQL par commande. Le code devient immuable, même si la liste ou la session change. C16 (`created_via=imagine-c16`) exclu ; seuls `checkout` et `store-api` sont admis pour candidat et paiement. Aucun tunnel de paiement réel livré. Aucun prix recalculé par C30 et aucun avantage inventé.

« Imagine → Codes suivis » : nombres des commandes processing/completed, date de paiement UTC bornes incluses, à côté des réponses volontaires de C27 sur leur propre date. Aucune identité affichée. CRUD Woo paginé, lecture en échec non prise pour zéro. Export/effacement natifs C21 déclarés par callbacks additionnels ; candidat inclus ; sceau technique conservé après effacement pour empêcher la recréation. Aucun fichier C21/C27/C19 clos modifié.

Tests : `python -B production/C-30/verifier.py` (puis `--live`) ; natif/Woo, sessions et HTTP, mutation inconnue PHPUnit, restauration après tests. La recette ne déclenche aucun paiement ni email : états/date payés sur objets fictifs puis rollback. Voir `production/C-30/A-VOIR.md`.

Corrections du 28 novembre : confidentialité par union des commandes du compte et des invitées de la même adresse vérifiée, dédoublonnée/ordonnée par ID avant pagination stable de 50 ; aucune commande liée à un tiers n’est ajoutée par son email. Le filtre ne dépend pas de la présence des métadonnées effacées, donc pas de saut à la page suivante. Échec de lecture, verrou ou relecture de suppression : `items_retained`, jamais un effacement annoncé complet. `compter()` conserve l’attribution historique : code stocké sur la commande, encore compté s’il est retiré du catalogue. Le bornage SQL par date est différé, comme autorisé par la fusion ; aucun besoin de volume démontré.

`CodesSuivisC30AdapterTest` est découvert par la suite scellée : session, revalidation du candidat, raccord Store API, verrou, sceau immuable, comptage historique, export/effacement compte+invité+tiers, pagination 102 commandes, pannes de lecture/verrou/persistance. La preuve de prix utilise **le même produit fictif payant et deux unités**, deux vrais paniers/calculs/créations Woo avec/sans code ; total, taxes, remises et coupons comparés. Une sonde de remise dépendant du code sur `woocommerce_before_calculate_totals` fait refuser le même comparateur, puis est retirée. Les tâches de cache de rapport WCS déclenchées à shutdown sont snapshotées en privé avant le test et restaurées exactement après sortie du processus, indépendamment du rollback des commandes/produit. Reçus antérieurs immuables sous `avant-corrections-V2/` et réception courante `reception-corrections-V2.json`. Aucun autre lot clos modifié.

## B-16 — enveloppe de la page article

Résumé : `post_excerpt` natif saisi, lu brut, jamais `get_the_excerpt()` ni génération depuis le corps ; vide, omis.
Mots-clés : étiquettes natives `post_tag`, noms publics sans lien imposé. Thématiques : liens natifs existants.
Signature : `imagine_signature`, nom éditorial dans une boîte native sécurisée (nonce/capacité), pas l'auteur technique du compte.
Numéro : relation B00 existante, uniquement si numéro publié ; aucun lien pour une relation absente/invalide.
WordPress fournit extrait/étiquettes/auteur ; l'auteur du compte ne garantit pas le journaliste signé, d'où le seul champ ajouté. Références officielles WordPress : [get_post_field (contexte raw)](https://developer.wordpress.org/reference/functions/get_post_field/), [get_the_excerpt (extrait potentiellement généré)](https://developer.wordpress.org/reference/functions/get_the_excerpt/), [get_the_terms](https://developer.wordpress.org/reference/functions/get_the_terms/) et [get_the_author (display_name du compte)](https://developer.wordpress.org/reference/functions/get_the_author/). Pas de navigation vers un autre site pendant cette correction : liens documentaires seulement.

`PageArticle` ne lit pas `post_content`. Corps C08, JSON-LD/descriptions et assets B03 inchangés. Le même marqueur B03 `data-imagine-distraction` masque l'en-tête et l'appel final hors du flux du texte. Depuis la correction R1, aucune seconde projection Memberships : `abonne()` supprimée ; appel piloté exclusivement par la décision/motif C08 déjà mémorisée. Seuls `numero_achete`, `decouverte_duree`, `decouverte_articles` complets donnent l'appel. Abonnement/offert/groupe/grâce/équipe et motif inconnu : aucun appel. Un article libre de motif `contenu_ouvert` ne permet pas d'inférer un achat/abonnement : pas d'appel final, choix technique de l'instruction 1 de la fusion, sans recréer les droits. Lien unique `Navigation::abonnementUrl()`.

Tests : `python -B wp/outils/demo/b16.py native native-final-V2`, navigateur et réception dans `production/B-16/`. Données fictives temporaires restaurées, C26 utilisé sans modification. Aucun style ajouté.

## B-04 — catalogue : corrections techniques du 25 novembre

`Paywall::decisionListe()` prédit la lecture d'un article sans activer le contexte de lecture et sans écrire l'ouverture ou le quota découverte. Il utilise le même raccord `Decouverte::decider()` et le moteur C06 ; les décisions de liste et de lecture ont des clés mémoire distinctes. L'état figé, le périmètre courant, la vérification du compte, la relecture et les deux formes découverte restent communs.

`Paywall::couvreNumero()` sert uniquement à masquer un achat inutile : même moteur PDF, avec une évaluation à la sortie si elle est future, sur les droits natifs existants. Il ne sert jamais à ouvrir un PDF. `decisionPdf()` et C11 gardent l'instant courant et la fermeture avant sortie ; l'achat payé est reconnu avant et à la sortie. A-carte avec PDF antérieur fermé conserve son bouton.

Le paquet PHPUnit existant découvre `tests/CatalogueTest.php` et `tests/CatalogueStatusTest.php` par sa configuration racine, sans nouveau manifeste ni dépendance. `phpunit.b04.xml` sélectionne ce sous-ensemble : mapping pur des quatre codes/libellés (les deux motifs découverte inclus), découverte sans effet d'écriture et possession/PDF autour de la seconde de sortie. Rejeu Docker documenté dans `production/B-04/COMMANDES-CORRECTIONS.md`.

La seule exemption produit fictif est désormais un mu-plugin de démonstration issu de `wp/outils/demo/b04-preview.php`, copié uniquement sur imagine-test-demo. Aucune IP ni logique de staging dans le thème. Aucun réglage métier ou visuel changé ; statut kiosque conservé en attendant Ced.

**Ce modèle de démonstration n’est pas le modèle éditorial définitif.** Il sera remplacé après l’audit de l’existant. Aucun ACF, thème ou constructeur de pages n’est embarqué ici.

- Types publics : `imagine_numero`, `imagine_evenement`, `imagine_partenaire` ; taxonomie `imagine_thematique` sur les articles natifs `post`.
- Rattachement d’un article : métadonnée entière `imagine_numero_id` ; indicateur `imagine_reserve`. Déclarations en code, exposées par le REST natif ; écriture réservée aux personnes pouvant éditer les articles.
- Calendrier fictif stocké dans `imagine_demo_calendrier`, visible avec `[imagine_demo_calendrier]`.
- Bibliothèques `Imagine\Pilotage` et `Imagine\Connecteur` chargées par un autoloader PSR-4 simple, depuis leurs `src/` frères copiés sans modification. Ce sont des bibliothèques, **pas des plugins activables** : aucune fausse déclaration d’activation. Aucun moteur métier ni connecteur réseau n'était appelé par B-00.
- Depuis C-08, `Acces\Moteur` et le vérificateur `Robots` sont réellement appelés par `Paywall`. Les bibliothèques closes ne sont ni modifiées ni activées comme extensions.
- Les mots de passe natifs ont été retirés sous C08 (arbitrage B00 du 23 novembre, 16 h 30). Ils ne protègent pas la recherche et ne donnent jamais un droit. Le seed écrit explicitement une valeur vide. Le point de sortie du thème ferme aussi le corps si l'adaptateur est absent ; cela ne remplace pas l'activation obligatoire du plugin pour les autres API.

## Installation et réglages

Depuis PowerShell, à la racine du dépôt : `python wp/outils/demo/construire.py`. Le constructeur ne vise que `imagine-test-demo`, installe d’abord sa garde MU hors ligne, copie ce plugin et les bibliothèques, l’active et crée les fixtures. Il garde le thème par défaut tant que le thème `imagine` n’existe pas.

Les mots de passe générés restent dans `C:\Users\Ced\.imagine-demo\identifiants.json`, jamais dans le dépôt. Aucune licence commerciale, compte WooCommerce.com ou passerelle de paiement n’est configuré. L’exception Novamira relève exclusivement de la création normale autorisée de l’outil.

## Tests B-00

```powershell
python -m unittest discover -s wp/tests/demo -p "test_b00*.py" -v
python wp/outils/demo/construire.py --preuve reconstruction
python wp/tests/demo/b00-verifier.py
```

`b00-recette.php` est inclus par WP-CLI (pas évalué par `eval-file`, incompatible avec `strict_types`) : types, 15 dates, 5 numéros, 20 articles, 10 médias, thématiques, comptes fictifs, bibliothèques et versions réelles, email/HTTP/paiements fermés. `b00-snapshot.php` inventorie indépendamment les objets tagués et leurs empreintes ; la reconstruction vérifie mêmes IDs, slugs, URL, textes et médias sans doublon. La recette HTTP B-00 décrivait le verrou natif provisoire; ses attentes « mot de passe => complet » sont délibérément remplacées par C-08.

## C-08 — paywall serveur

`Paywall.php` assemble numéro/date éditoriale, identité WordPress, adhésions Memberships, lien natif `_subscription_id` et état/dates CRUD Subscriptions. Il appelle les bibliothèques pures C-06/C-03, sans les modifier. Il ne lit aucun corps dans le moteur de décision. Tous les articles natifs `post` sont gouvernés : sans indicateur d'ouverture explicite et numéro/date valides, la réponse est fermée; l'absence de métadonnées n'ouvre jamais un article.

Réglages de l'adaptateur effectivement lus (l'écran C10 existe, mais les options de `Acces\Reglages` du moteur ne sont **pas raccordées** ici : valeurs par défaut du moteur, ne pas les prétendre actives) :

- `imagine_acces_plans` : tableau `ID du plan Memberships => abonnement|offert|groupe`, vide par défaut (aucun accès abonné). Les états et dates natifs restent obligatoires. Les rôles natifs `administrator` et `editor` correspondent à l'équipe C-06.
- `imagine_acces_extrait_caracteres` : 320 par défaut, borné à 40–1000. C'est un plafond sur **l'extrait éditorial explicitement public**, jamais sur `post_content`. Sans extrait, phrase neutre.
- La grâce n'est pas un synonyme de `on-hold`. Elle exige les deux métadonnées UTC `_imagine_acces_grace_debut` / `_imagine_acces_grace_fin` de l'objet Subscriptions, une adhésion active/paused, un propriétaire cohérent et des dates valides; la fin effective est le minimum des bornes natives. Aucun délai n'est inventé. Les fixtures posent une large fenêtre **entièrement fictive** pour la démonstration; le cycle réel des impayés est hors lot.

Les réponses dynamiques sont conservativement privées/no-store (pas de cache d'hébergement testé). La portée large, y compris les pages ouvertes, est **provisoire** : distinguer connecté/anonyme au lot cache/performance. Les objets refusés sont clonés et expurgés, jamais réécrits dans le cache objet. Gardes supplémentaires : contenu, REST rendu/brut, extraits, flux, oEmbed, partage `NewsArticle` sans articleBody. XML-RPC coupé. DNS robots volontairement indisponible hors ligne : aucun vrai robot Internet déclaré validé.

### Contrats corrigés le 23 novembre, 17 h 10

- `imagine_reserve` reste un booléen REST natif. Clé présente avec `false` (chaîne vide en stockage) / `0` : ouvert si numéro/date valides ; `true` / `1` : réservé. Clé absente ou valeur invalide : fermé. Les écritures native et REST sont éprouvées.
- Recherche HTML/REST : `posts_search` **et** `posts_orderby` masquent le corps SQL des articles non complets avant appariement/classement (`CASE`). Titre et extrait public restent recherchables ; l'abonné trouve la phrase du corps. Les termes SQL cités et les exclusions natives sont conservés. L'inventaire parcourt les IDs de la démo, sans WP_Query récursif ; pas de promesse de performance à grande échelle.
- Mémoïsation PHP `(site, post, utilisateur)` sur **la seule requête**, même instant UTC à la seconde, aucun transient/cache inter-requêtes. Invalidation par les écritures natives post/user/options, nettoyage de cache, rôles, sauvegardes/statuts Woo ; ajout/retrait des filtres de lecture surveillés détecté. Les canaris mutateurs tournent dans le même processus et ne réutilisent pas un ancien droit ouvert. Des doublures hors API/hooks doivent appeler explicitement `Paywall::invalidate()` ; ne pas contourner les hooks natifs.
- Le bloc régularisation vérifie `function_exists('wc_get_page_permalink')`, sinon lien de connexion. Banc séparé sans Woo, sans désactivation persistante.

**Interdit : `echo get_post($id)->post_content` ou toute sortie directe du corps brut.** Le cache objet reste volontairement intégral : passer par `Imagine\Theme\imagine_article_body()` et les sorties filtrées. Ne pas utiliser `suppress_filters=true` ou du SQL direct pour produire une recherche publique ; ces API bas niveau ne sont pas des sorties sécurisées.

```powershell
python wp/outils/demo/c08.py --seed
python wp/tests/demo/c08-faults.py
python wp/tests/demo/c08-verifier.py
python wp/tests/demo/c08-regression.py
python -m unittest discover -s wp/tests/demo -p "test_*.py" -v
```

Recette complète actuelle : `python wp/tests/demo/c08-final.py`, dans un environnement neuf hors dépôt. Réutiliser les **six wheels et le lock B01**, sans nouveau packaging : `python -m pip install --no-index --find-links production/B-01/validation -r production/B-01/validation/requirements.lock`. Le reçu C08 relève versions/empreintes et résultats réels. Les articles jetables sont supprimés dans `finally`, accueil final `[82,81,45,44,43]`.

Cible fixe `imagine-test-demo`, aucune création/reconstruction B-00. `c08.py` sans `--seed` réinstalle seulement les fichiers C-08 et exécute la recette PHP. `--seed` réutilise les mêmes IDs pour 3 comptes fictifs, 1 plan, 2 adhésions, 2 abonnements manuels sans passerelle et 2 articles réservés supplémentaires. Les identifiants restent dans `C:\Users\Ced\.imagine-demo\c08-identifiants.json`. `construire.py --theme-only` reste inchangé.

Preuves actuelles : `production/C-08/` ; anciennes preuves seulement dans `historique/`. Les recettes B00/B01 corrigées ont déjà remplacé les anciens oracles « quatre articles globaux » / « mot de passe ⇒ complet » ; ne pas les restaurer. C08 compare le snapshot B00 en ne tolérant que le retrait explicite des drapeaux de mot de passe, puis vérifie URL/HTML/droits. `NumeroPublication.php` et son chargement B01 sont préservés. Aucun PDF, découverte complète, achat d'un numéro ou mode lecture spécifique n'est déclaré sécurisé par C08.

## C-11 — PDF du numéro

`PdfNumero.php` sert `/?imagine_pdf=ID_DU_NUMERO` après `Paywall::decisionPdf()` : identité/droits natifs C08, moteur C06 avec son type exact `pdf`, réglages C10 lus à chaque décision. Le raccord C11 ajoute cette méthode sans changer les décisions d'articles ni les adaptateurs C10. Le lecteur sans droit retourne au numéro avec le bloc connexion/abonnement/régularisation.

Les octets sont déplacés hors de la racine HTTP : par défaut, `imagine-private-pdf` voisin de cette racine, puis `site-ID/nom-aleatoire.pdf` (0700/0600). `IMAGINE_PDF_PRIVATE_DIR` permet un autre emplacement applicatif, jamais sous la racine publique. Le répertoire privé doit être créé, conservé et sauvegardé comme données ; aucune règle de refus Apache/nginx n'est requise. Pour WP-CLI sans DOCUMENT_ROOT, l'adaptateur déduit une racine seulement si les chemins disque/URL concordent ; sinon il ferme. Aucune URL physique, pas de délégation X-Sendfile, pas de cache partagé ; GET/HEAD seulement. Un fichier manquant, corrompu, un nom traversant ou une dépendance en erreur ferment la livraison.

Les médias PDF gardent leurs IDs mais deviennent privés, sans `_wp_attached_file` ni métadonnées de chemin. GUID/URL native pointent vers le contrôleur, le REST média est fermé. `PdfNumero::protect(..., $publicCopies)` mutualise suppression **et relecture d'absence** : le seed PDF et la migration donnent les deux anciens chemins publics exacts. Le seed converge donc depuis un média public, sans migration externe préalable ; sa source reste hors docroot. Une copie inattendue, non supprimable, en répertoire ou en lien ne donne jamais une protection annoncée réussie. Le lien du thème exige une décision PDF complète ; article et PDF partagent l'instant immuable de requête.

Depuis C14, P-NUMERO (alias V-NUM du brief) ouvre les articles et le PDF de son seul numéro T1, par la commande native de fixture. Les autres numéros restent fermés ; la recette C11 conserve donc son témoin T4 fermé. Aucune commande en attente ni rôle client ne donne un droit. Le DNS externe reste hors ligne : le faux robot est testé par HTTP, les deux politiques robots par une entrée synthétique au contrat C06/C10, pas par un faux robot déclaré réel. Les deux politiques PDF antérieurs utilisent les droits natifs actifs. Aucune bibliothèque close ni écran C10 n'est modifié.

```bash
python C:/Users/Ced/imagine/wp/outils/demo/c11.py             # installer/rejouer, démo existante seulement
python C:/Users/Ced/imagine/wp/outils/demo/c11.py --check-only # recettes ciblées et unitaires, sans reconstruction B00
```

Les unitaires utilisent les six wheels universelles gelées B01 en lecture seule (zipimport), sans installation ni réseau ; pas besoin de `html5lib` dans le Python global.

La commande de contrôle commence par les tests PHPUnit du paquet (`tests/PdfNumeroTest.php`, `phpunit.c11.xml`) dans un conteneur local hors réseau, avec les dépendances déjà préparées T01 ; commande autonome : `python wp/outils/demo/c11-unit.py`. Le runner partagé `wp/tests/rejouer.ps1` ne sélectionne pas cette configuration locale et son image n'a pas de cache Composer imagine-site : **ses 812 tests ne comprennent pas C11**. Ce repli autorisé est explicite, aucune modification de runner ou installation d'image n'est faite. Les tests couvrent le vrai contrôleur `serve`/`exit` (404/405/GET/HEAD/302), `path`, `directory`, `block` et la frontière canonique Unix/Windows. WP est doublé seulement pour ce banc local ; la recette démo conserve les vrais droits.

La commande de contrôle téléverse ensuite les recettes, teste les options natives avec restauration exacte et supprime ses canaris dans `finally`. Le départ public du seed est réellement recréé sur le seul témoin T4 sans référence privée puis rejoué deux fois ; les autres profils ne sont pas reconstruits. Sources officielles, limites de la démo, URL à ouvrir et choix de stockage en cinq lignes : `production/C-11/A-VOIR.md`. Les preuves sont limitées à `production/C-11/{http,runtime,faults}.json`.

## C-12 — accès découverte branché

`Decouverte.php` raccorde **les classes closes C06**, sans copier leurs règles. Une option non autoloadée `imagine_decouverte_compte_ID` conserve l’ouverture UTC, les paramètres figés et les IDs d’articles ouverts. INSERT IGNORE sur l’index natif puis mise à jour compare-and-swap binaire : une course ne donne pas de crédits supplémentaires. Un état invalide ou une persistance refusée ferme l’accès, sans recréer le parcours.

`imagine_decouverte_reglages` : `ouverture=fermee` (défaut) ou `premiere_lecture`, `forme=articles|duree`, `nombre=2` (1–100), `jours=7` (1–365), `numeros=[]` (IDs explicites, aucun par défaut). Le compte doit avoir prénom, nom et email valide, plus `imagine_email_confirme=1`. Sur cette démonstration seulement, le script des deux profils C09 pose ce **drapeau fictif** : ce n’est pas un parcours de confirmation d’email. Aucune métadonnée de droit n’est exposée en REST.

Le contenu transmis par `Paywall` lit la désignation éditoriale native **imagine_decouverte** : booléen déclaré depuis `Decouverte::register()`, écriture réservée aux éditeurs autorisés. Absente, fausse ou invalide : aucun accès découverte, aucune ouverture/consommation, même si le numéro est listé. Ce filtre s’ajoute aux périmètres initial/courant ; il ne réduit pas les droits natifs prioritaires. Les fixtures C12 désignent un seul témoin par numéro existant 39/25/18, plus un témoin non désigné du même 39.

Durée/nombre/périmètre initial sont figés à l’ouverture : les augmenter ne recrédite pas. Le périmètre courant peut retirer, pas élargir l’initial. Fermer suspend la découverte. En mode articles, l’ID déjà ouvert ne recompte pas. **Relecture après quota : question ouverte, à confirmer par Imagine**, isolée derrière l’option courante `imagine_decouverte_relecture=fermee|rester_lisible`, défaut prudent **fermee**, affichée/enregistrée par Settings API et journalisée. Le choix `fermee` transmet au moteur le nombre total consommé ; `rester_lisible` transmet le rang de l’ID déjà ouvert, jamais un recrédit du stockage. Les autres articles restent épuisés et la désignation/périmètres restent requis. Ce choix est celui du raccord, pas une contrainte de C06 ni un arbitrage acquis. En durée, la fin UTC reste exclue pour toute relecture.

Seul le GET final d’un article publié et admissible consomme, après les redirections canoniques. REST connecté avec nonce natif, flux, recherche, aperçu, oEmbed/embed, HEAD/POST, préchargement et agents robots reconnaissables n’ouvrent ni ne consomment la découverte ; les autres droits natifs restent inchangés. Le réglage d’accès C10 est désormais réellement lu par le raccord C10/C11 (la réserve historique du §C08 ci-dessus est dépassée).

`DecouverteReglages.php` étend **la section Accès de l’écran C10 existant**, via les hooks de menu et l’enveloppement de son callback de rendu : C10 ne propose pas de hook interne ni `do_settings_sections`. Son formulaire, sa capacité, son nonce et son traitement `options.php` sont conservés. Les champs portent « À confirmer par Imagine » ; les changements rejoignent le journal visible C10, avec restauration en cas d’échec du journal. Ce raccord dépend du titre/tableau de cette section et doit être retesté si son balisage change ; aucun fichier de `imagine-pilotage` n’est modifié.

```bash
python C:/Users/Ced/imagine/wp/outils/demo/c12.py
python C:/Users/Ced/imagine/wp/outils/demo/c12.py --check-only
```

Cible unique fictive : installation ciblée, puis rejeu PHP/HTTP réel et non-régression C11, sans constructeur global ni reset d’autres profils. Les tests restaurent exactement les options et l’état V-DEC initial. Le script C09 sait initialiser/réinitialiser ses deux profils découverte ; le runner C12, lui, ne renouvelle pas un profil déjà consommé. Résultats sans corps HTML, cookies, secrets, captures ni reçus d’empreintes : `production/C-12/resultats.json`. Parcours et sources officielles : `production/C-12/A-VOIR.md`.

Rejeu hors réseau autonome : `PYTHONDONTWRITEBYTECODE=1 python C:/Users/Ced/imagine/wp/outils/demo/c12-unit.py`. Configuration `phpunit.c12.xml`, répertoire distinct `tests-c12/` (ne change pas la sélection C11). Vrais Paywall/raccord/moteur C06, doubles WP/SQL explicites. Le repli local C11 réutilise sans installation les dépendances de l’image T01 existante, dépôt monté en lecture seule, réseau `none`, nettoyage vérifié. `wp/tests/rejouer.ps1` et ses 812 tests **n’incluent pas ce raccord** ; runner et T01 restent hors périmètre, inchangés. La recette native de la démo prouve séparément SQL/concurrence, routes HTTP et restauration. Bootstrap C13 et PdfNumero C11 ne sont pas réinstallés par C12.

Limites : unicité **par compte**, pas d’identification de personne à travers plusieurs adresses ; refus des emails jetables et vraie confirmation email à raccorder au futur parcours d’inscription. Un robot utilisant une session valide et un UA humain n’est pas distinguable d’un lecteur. Aucun robot Internet n’a été vérifié hors ligne. PDF et achats de numéro n’acquièrent aucun droit découverte ; aucun accès réel ni email sortant.

## C-14 — achat d'un numéro

`AchatNumero.php` convertit une ligne validée vers le contrat `achat` du moteur C06, inchangé. `AchatsNumeros.php` est le raccord CRUD Woo : commandes `shop_order` du seul `customer_id` connecté, statuts strictement `processing|completed`, `is_paid()` et date native `date_paid` obligatoire. Aucune durée de fin n'est inventée. Une date future reste fermée par C06. Le montant peut être nul (fixture), jamais assimilé à une transaction bancaire démontrée.

Dans les données générales d'un **produit simple**, `imagine_achat_numero_id` désigne un seul numéro publié. L'enregistrement conserve le contrôle natif Woo (nonce/capacité), plus la capacité d'édition dans le raccord. L'instantané caché `_imagine_achat_numero_id` est figé à la création de la ligne : il est la **seule référence du numéro acquis**, qui doit encore être un `imagine_numero` publié. Vider/réaffecter/supprimer le produit ne ferme pas l'achat de A et n'ouvre jamais B à l'ancien acheteur ; seuls les achats suivants utilisent le nouveau mapping. Instantané absent/zéro/invalide, quantité nulle, numéro acquis dépublié/supprimé : fermé. Aucune reprise rétroactive ni régénération d'instantané sur une ligne existante. Variantes, packs et souscriptions restent hors de ce modèle provisoire.

**Réglages → Achats de numéros**, capacité `manage_options`, formulaire/nonce/validation `options.php` natifs : `imagine_achat_remboursement=commande|ligne`, question à confirmer par Imagine. Défaut prudent **commande**, également appliqué à une valeur absente/invalide : tout remboursement natif, même partiel/non ventilé, retire toutes les acquisitions de cette commande. Alternative **ligne** : seule une ligne produit référencée par `_refunded_item_id` perd son achat (même pour une quantité partielle) ; un partiel non ventilé ou portant uniquement sur le port ne désigne aucune ligne produit, donc conserve les autres acquisitions. Un remboursement **complet** ferme tout dans les deux modes (statut natif `refunded`, ou total monétaire remboursé atteignant le total strictement positif). Une autre commande valide reste indépendante. Les deux modes sont éprouvés sur des commandes à deux numéros, avec partiel ventilé/non ventilé et remboursement complet, articles et PDF.

Les suppressions/trash de commande ou de ligne et les changements de quantité/propriétaire sont relus. Les invalidations natives C08 conservent la mémoïsation **de requête** C12. Les remboursements sont relus par `wc_get_orders(parent=...)`, objets et ventilations natifs, sans les agrégats que Woo peut garder après un `delete()` brut. Requête par commande conservée (N+1 optionnel de la relecture, volume démo) ; pagination de 50, test sur 51 commandes. Aucune table miroir ni cache partagé. Les tests ne passent jamais `refund_payment=true` : objets zéro euro, aucune passerelle/transaction. Sur le seul scénario zéro non ventilé, un filtre Woo local à la commande distingue explicitement le partiel de l'égalité artificielle 0=0 ; il ne remplace ni les objets natifs, ni le raccord de droits.

Le §3.7 autorise l'achat papier invité et propose la création de compte ensuite. Le parcours de revendication de cet achat n'est pas implémenté par ce lot : sans `customer_id` rattaché, fermé, même avec la même adresse email. Aucun rapprochement automatique par email ni droit anonyme. Articles et PDF passent par les adaptateurs C08/C11 existants ; pas de téléchargement Woo statique.

Le profil demandé « V-NUM » est absent des identifiants C09 : son équivalent existant **P-NUMERO**, login `p-numero`, est conservé et porte un alias explicite. `c09-seed.php` appelle `c14-profil.php` et son transport est ajouté à `profils.py`. C14 ne réinitialise que cette commande existante à zéro euro : état payé/date synthétiques déclarés, jamais `payment_complete()`, aucune passerelle ni transaction. T1 (ID 11) ouvert ; T2/T4 fermés. Les autres profils ne sont pas reconstruits.

```bash
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c14.py --deploy  # installation ciblée + fixture P-NUMERO
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c14.py --deploy-code # code seul, aucun reset de profil
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c14.py           # rejeu, sans reset de profil
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c14-regressions.py
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c14-validation.py # T01 + C14 natif/HTTP + régressions + PSR12
```

`tests/AchatNumeroTest.php` est désormais **découvert par T01** via le paquet racine C13 existant, sans changer ses manifests, son lock ni le runner. La recette PHP autonome, le natif HPOS et le vrai HTTP restent complémentaires. `preparer-image.ps1` a été relancé ; `c14-validation.py --prepare --deploy-code` reproduit la préparation publique et l'installation ciblée sans reset de compte. L'ancien banc C11 qui change temporairement les plans tourne dans une transaction native rollbackée, callbacks C13 inclus : pas d'effacement de l'historique postal append-only. Le runner vérifie InnoDB et l'absence de cache objet externe avant ce test. Les preuves et limites sont dans `production/C-14/`. Le `PRET` initial du parent existe et n'est pas modifié ; les corrections restent **à relire**, pas une clôture ni un GO sur le réel.


## B-02 — tableau de bord Mon compte (squelette)

`MonCompte.php` ajoute les cinq sections au **dashboard natif WooCommerce** ; le thème ne remplace ni la connexion, ni les routes Subscriptions, ni le formulaire d'adresse. Aucun endpoint public de données, aucune identité fournie par GET/POST : `donnees()` lit seulement la session et recontrôle le propriétaire de chaque souscription/commande. Les PDF viennent exclusivement de la décision C11/C14. Aucun CSS ajouté.

La formule, le total récurrent, la prochaine date et les adresses viennent du CRUD natif. C01 fournit premier/dernier numéros théoriques ; sans historique d'activation, le compteur reste nommé non raccordé. C05 fournit les positions théoriques seulement si sa marge obligatoire est renseignée. Sans elle, A-SEPA4 affiche quatre emplacements, pas de fausses dates ni de fausses échéances payées. Les renouvellements sans rang métier restent non raccordés. Les factures/justificatifs sont une liste vide explicite, jamais les commandes rebaptisées factures.

L'adresse postale affichée est celle de la souscription (source C13), pas seulement l'adresse par défaut du client. Le lien ouvre le formulaire Woo/WCS `edit-address/shipping/?subscription=ID` : validations, deux nonces et sauvegarde restent natifs. **Raccord B02 supplémentaire, limité au formulaire client** : `woocommerce_after_subscription_object_save` appelle le relevé C13 existant uniquement pendant `woocommerce_customer_save_address` et pour le titulaire connecté, append-only et dédupliqué ; le hook `after_order_object_save` de C13 ne recevait pas la sauvegarde réelle Subscriptions 9.4.1. Aucun fichier C13/close modifié, aucune réécriture du passé postal. La recette change puis restaure l'adresse et garde les deux observations et les notes natives, sans reset.

```bash
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/b02.py --deploy
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/b02.py --require-complete
```

La seconde commande renvoie **2** tant que l'acceptation nominative est incomplète : `a-4x-j45` n'existe pas dans C09, A-SEPA4 n'est pas présenté comme son équivalent 2/4 ; marge C05 absente ; aucun rejet/paiement fabriqué. La recette technique PHP+HTTP peut être verte sans prétendre remplir ces gates. Le paquet B02 n'est pas découvert par T01 ; `preparer-image.ps1` a néanmoins été exécuté et vérifié. Parcours, commandes, limites et résultats : `production/B-02/`. Aucun PRET déposé.

## C-15 — écran des échéances

`EcheancesRegles.php` contient les filtres purs et le CSV ; `EcheancesNatives.php` lit exclusivement commandes et souscriptions Woo/WCS paginées ; `EcheancesAdmin.php` ajoute **Imagine → Échéances** au parent existant, sans créer de menu principal. Le doublon préexistant C10/C13 du parent pour le référent est dédupliqué à l'affichage, sans modifier leurs fichiers. Capacité C09 existante `imagine_gerer_echeances`, ou administrateur `manage_options` ; aucun nouveau rôle ni droit global.

Cinq vues : fin/prochain renouvellement à 30/90/180 jours ; commandes natives `pending|on-hold` impayées ; virements impayés `bacs` ; prochains mandats papier actifs, dates déjà dues conservées ; commandes `failed`. Aucun délai de retard, aucune nouvelle décision d'accès. L'action unique **Paiement reçu** est un POST avec nonce lié à la commande, puis écran de confirmation et case obligatoire ; relecture de l'objet natif, contrôle type/propriétaire/méthode/statut/date/remboursements, `payment_complete()`, note Woo portant opérateur et instant UTC. Une commande déjà payée est refusée, aucune action en masse ni remboursement. Les transports email/HTTP et le report des emails sont bloqués pendant cette transition.

L'export des mandats est un flux `php://output` privé/no-store, POST/capacité/nonce lié à la période, cinq colonnes fixes (abonné, montant, devise, référence, échéance UTC), cellules protégées contre les formules. Aucun fichier public, aucun IBAN lu ou exporté.

**Particularité explicite de la démo C09** : ses méthodes de passerelle restent volontairement vides. Sur la seule URL locale autorisée, les marqueurs natifs `imagine_demo_fictif=1`, `_imagine_c09_fixture`, l'ID du manifeste et son propriétaire identifient A-VIR comme virement et A-PAPIER comme mandat papier. La référence fictive existante est l'identifiant **A-PAPIER**, pas un mandat bancaire créé. Sans ces quatre contrôles, une méthode vide reste inconnue ; une méthode native non vide reste prioritaire. Hors démo : `bacs` ou `imagine_papier`, référence native `imagine_mandat_reference` pour le papier. Aucun état payé parallèle et aucun nouveau profil.

```powershell
python wp/outils/demo/c15-unit.py
python wp/outils/demo/c15.py --deploy --http
python wp/tests/demo/c15-verifier.py --prepare --action
```

Le dernier rejeu exerce réellement A-VIR par HTTP puis le reset C09 existant à son horloge initiale. Il restaure les états découverte dépendants et la date payée native de P-NUMERO que l'initialiseur C14 déplacerait sinon ; comparaison sémantique relue de tous les profils commerciaux C09, rôles et IDs. Les notes d'audit natives sont conservées ; le reset invalide les sessions C09, se reconnecter ensuite. Aucun thème téléversé ou restauré. `preparer-image.ps1` est exécuté sans modification ; les tests C15 autonomes de `wp/tests/demo/` ne sont pas annoncés comme découverts par T01. Preuves et limites : `production/C-15/`.

## C-13 — Liste d’envoi native (relecture avec réserve C09)

`EnvoiRegles.php` porte les règles **pures**, avec horloge, calendrier et observations injectés, sans WordPress. C01 fournit les blocs, y compris `renouveler()` ; C07 établit les lignes, anomalies et éligibilité. `EnvoiNatif.php` lit le CRUD natif et conserve les relevés append-only non autoloadés (`imagine_envoi_releve_ID_UUID`), jamais antidatés. Les hooks Subscriptions/Memberships et les adresses client ajoutent les changements observés ; le rejeu identique ne duplique pas. Historique/calendrier incomplet ou bénéficiaires requis non résolus : export fermé. Projection future explicitement provisoire.

`ListeEnvoiAdmin.php` ajoute **Imagine → Liste d’envoi**, sous la capacité C09 existante `imagine_exporter_liste_envoi`, ou `manage_options` pour les administrateurs. Aucun rôle ni droit sensible n'est ajouté. L'exception au blocage administratif Woo est limitée à cet écran et à sa capacité. L'export authentifié `admin-post.php` exige POST et un nonce lié au numéro ; C07/C04 protègent le CSV et C10 fournit les colonnes. Aucun fichier export public. L'audit `imagine_envoi_export_journal_UUID` est écrit/relu avant la réponse ; s'il échoue, l'export ferme. Cinquante événements affichés, sans purge.

```bash
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c13.py --deploy
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c13.py
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c13.py --require-complete
```

`EnvoiRelations.php` lit les liens WCS Gifting (bénéficiaire, adresse de livraison, origine `offert`) et les attributions natives Memberships `_subscription_id` des plans `groupe` (identités et adresses clients, origine `groupe`). La capacité est la quantité des produits natifs liés au plan ; seules les places attribuées actives ont une adresse. Aucun payeur n’est substitué à un cadeau/groupement incomplet. **Réglage métier fermé par défaut** : `imagine_envoi_groupes=ferme|liens_memberships`, affiché/enregistré par Settings API uniquement pour l’administrateur dans C13 ; les deux valeurs sont testées. Modèle « quantité = places et attributions Memberships » à confirmer par Imagine ; aucune extension Teams absente n’est simulée.

Les commandes de renouvellement reliées et effectivement enregistrées (statut payé, date native, propriétaire cohérent, aucun remboursement) alimentent `Moteur::renouveler`, sans décaler le début initial. Défaut annuel intervalle 1 ; un autre cycle exige `_imagine_envoi_bloc_debut` UTC explicitement enregistré sur la commande de renouvellement. Les échéances quatre fois ne sont pas quatre années. Le paiement initial vient du parent quand il existe ; le dernier paiement WCS d’une souscription renouvelée ne reconstitue pas un paiement initial absent.

`imagine_envoi_calendrier_reference` conserve le calendrier contrôlé ; la voie persistante refuse réécritures/suppressions rétroactives avec les gardes C01. `imagine_envoi_gel_CODE` conserve version, calendrier, clôture, observations et blocs retenus. Un gel n’est plus relu avec l’option courante, ni réécrit par `update_option`. Égalité à la clôture exclue ; pas de reconstitution d’un passé absent. Les rafraîchissements GET avant clôture restent idempotents, mais leur balayage linéaire n’est pas qualifié en volume réel.

```bash
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c13-unit.py
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Depuis cette correction, `composer.json`, son lock et `phpunit.xml` racine rendent le paquet **automatiquement découvert par T01**, sans modifier le runner fermé. Racine complète `tests/` : C11 conservé et C13 pur. Les anciens paragraphes C11 signalant son absence de T01 décrivent l’état antérieur à cette intégration ; C12 garde son banc dédié. `phpunit.c13.xml` permet aussi le rejeu pur C13 sans site. Les recettes natives C13 préexistantes sont conservées ; `c13-corrections-runtime.php` ajoute des objets natifs fictifs jetables, leur nettoyage et restauration relus. Une seule commande neuve à zéro reçoit statut/date de paiement explicitement fictifs pour tester le renouvellement ; aucun profil C09 existant ne devient payé, aucun appel bancaire ni `payment_complete()`.

Cible unique `imagine-test-demo`, aucun reset global ou C09/C10/C11/C12, sources B02/C14 et bootstrap préservés. Deux témoins permanents C13 en grâce fictive, sans paiement, permettent un CSV réel de deux personnes BE/FR. **Ils ne remplacent pas l’acceptation positive C09** : douze souscriptions sans paiement validé, A-SANSMAIL exclu pour ce motif (aucun filtre email), offerts/groupés C09 sans liens natifs. Le raccord est désormais livré et testé sur liens natifs jetables ; la gate C09 reste fermée, mode strict **2**, `recette_complete=false`. État unique : **prêt à relire avec réserves**, pas recette complète ni validation visuelle/clôture ; aucun PRET créé/modifié par ce worker. Parcours, commandes et reçus : `production/C-13/`.

## C-16 — commande administrative en trois écrans

`CommandeRegles` valide la saisie pure ; `CommandeAdmin` ajoute **Imagine → Commande pour un client** au menu unique, sans bibliothèque close modifiée. Capacité C15 `imagine_gerer_echeances` **et** C09 `imagine_creer_compte_client`, ou `manage_options`. Les POST sont traités avant les en-têtes administratifs pour des refus HTTP 403/409 réels. Client/recherche ou création, produit/adresse/paiement hors ligne, confirmation : trois écrans serveur sans JavaScript. Aucun objet n'est créé avant la confirmation.

Le brouillon est un transient privé lié au référent, durée d'une heure ; son jeton et le nonce ne transportent pas la saisie. Pour confirmer, le verrou MySQL est acquis **avant toute lecture du brouillon** ; les caches natifs du transient sont invalidés sous verrou. Deux vrais POST synchronisés avant `GET_LOCK` reprennent le même ID ; une interruption après persistance de `commence` reste fermée à toute nouvelle création. Le verrou identité/email reste distinct. `CommandeNative` utilise uniquement les produits fictifs C09 existants et les produits simples reliés à un numéro publié par C14 ; catalogue/prix relus avant confirmation. Pas de prix, taxe ou port Imagine inventé. `WC_Order` et, pour l'abonnement, `WC_Subscription` liée nativement au parent, tous **pending**, renouvellement manuel explicite, aucune transaction ni adhésion. Les virements liés apparaissent dans C15 ; les numéros à l'unité restent exclus de sa vue selon son périmètre actuel.

`SansEmail::META = imagine_sans_email` réutilise le marqueur de la fixture C13. A-SANSMAIL C09 ne le portait pas : C09 le pose désormais sans changer son adresse historique. Les nouveaux sans-email utilisent `@sans-email.imagine.invalid`, domaine réservé non livrable ; le compte générique `imagine-vente-directe` utilise le même mécanisme. Le filtre individuel `pre_wp_mail` refuse tout message comportant un tel destinataire en TO/CC/BCC, même mélangé à un destinataire normal ; le coupe-circuit global de la démo reste actif. Aucun envoi externe Brevo n'est exercé ni annoncé branché.

Le reset C09 inclut `wp/outils/demo/c16-reset.php` lorsqu'il est déployé : prévol de tous les objets C16 impayés possédés, refus d'objets payés/modifiés ou étrangers, puis suppression native des objets/comptes et des brouillons. La recette appelle cette même extension **ciblée** du reset, sans réinitialiser les profils C09/C12/C14 ni leurs échéances. Les relevés postaux append-only C13 sont conservés.

```powershell
python wp/tests/demo/c16-verifier-V2.py --prepare --deploy --canonical
python wp/tests/demo/c16-gates-V2.py --strict-global
```

Corrections V2 : `imagine_commande_adresse_nouveau=oui|non` est affiché dans le formulaire Settings API C10 existant, **oui par défaut prudent**, à confirmer par Imagine. Seul le compte réellement créé à la confirmation reçoit prénom, nom et adresses billing/shipping par `WC_Customer`; jamais un compte préexistant, une adresse email déjà connue ou le compte de vente directe. `non` conserve l'adresse sur commande/souscription seulement, et l'UI explique que la recherche par localité ne retrouvera pas ce nouveau compte. La recherche GET est déséchappée avec `wp_unslash()` avant validation, puis échappée en HTML. Tests réels par nom complet et localité avec apostrophe, avec et sans email.

`SansEmailTest` double uniquement les deux lectures de compte/marqueur, dans des processus PHPUnit isolés : TO/CC/BCC, destinataire marqué mélangé à un normal, domaine `.invalid`, conservation de la décision précédente pour les seuls destinataires normaux. Aucun transport d'envoi appelé. Le déploiement V2 n'écrit que les quatre classes C16 et son reset ; bootstrap/seed partagés restent intacts et leur contrat courant C16/C17/C18/C19 est relu, sans imposer les anciens hashes. Le formulaire natif initialise certains réglages absents de C12/C17 : la recette restitue leur absence exacte et relit, en conservant les journaux append-only.

Don, pack, offert et groupé restent des emplacements nommés. Parcours et reçus frais : `production/C-16/{A-VOIR.md,final-V2.json}`. Les anciens reçus et `c16-gates.py` restent historiques ; le gate V2 exige C09 entièrement vert et n'accepte aucune exception historique. Ce lot n'appelle jamais `payment_complete()` et ne valide aucun paiement. Prêt technique seulement, pas une validation visuelle ni un GO sur le réel.

## C-17 — justificatifs solidaires

`JustificatifRegles` vérifie catégories, contenu PDF/JPEG/PNG et plafond de 5 Mio, puis produit une décision documentaire pure. `Justificatifs` branche le dépôt dans le seul emplacement B02 « Mes factures et justificatifs » par `imagine_compte_justificatif`, et ajoute **Imagine → Justificatifs solidaires** sous la capacité dédiée existante `imagine_traiter_justificatifs`. Aucun prix, commande, abonnement, adhésion, droit numérique ou email n'est modifié.

Le stockage réutilise `PdfNumero::directory()` et `PdfNumero::privateHeaders()` (seule visibilité de cette méthode passée à public). Les octets sont hors document root, nom aléatoire `c17-<128 bits>.bin`, mode 0600 ; aucun média WordPress ni chemin public créé. Chaque GET/HEAD contrôle à nouveau titulaire ou capacité du référent ; téléchargement en pièce jointe, `nosniff`, CSP sandbox et privé/no-store, jamais de prévisualisation. Les PDF actifs usuels, SVG et contenus exécutables identifiés sont refusés ; ce contrôle n'est pas un antivirus ou une désinfection PDF universelle.

Les opérations et lectures d'un titulaire partagent un verrou MySQL. Les formulaires portent la version de l'état, en plus du nonce natif : un dépôt ou une décision périmé(e) est refusé(e). Validation et refus suppriment le fichier, relisent son absence, puis enregistrent **exactement catégorie, état (`decision`) et fin**, conformément à la consigne du 26 novembre 2026 à 4 h 30. Les hooks d'options ajoutent séparément date UTC et opérateur au **journal C10**, dont les avant/après ne portent aucun blob ou chemin. Si l'audit échoue, la décision est refusée et l'option restaurée ; un fichier déjà retiré impose alors un nouveau dépôt, sans lien mort ni validation possible. Le nouveau fichier n'est pas écrit avant retrait du précédent. La capacité dédiée reste attribuée uniquement par le seed démo.

`imagine_solidaire_categories` est une liste du formulaire **C10 existant**, via hooks, Settings API et journal C10, défaut unique **à préciser**, une catégorie par ligne, inconnue refusée. Une modification de liste ne réécrit pas les décisions anciennes. Les conséquences tarifaires/de droits et la conduite après échéance restent hors de ce raccord, ouvertes chez Imagine.

```powershell
python wp/tests/demo/c17-instruction5.py seal verification-parent-V2
python wp/tests/demo/c17-visuel.py
python wp/outils/demo/c17.py --reset
```

Les recettes historiques couvrent aussi réglages natifs C10, suppression physiquement impossible et décisions concurrentes. La preuve courante de l'instruction 5, dans `production/C-17/instruction5-20261126/`, ajoute les trois champs stricts après validation/refus, journal C10 séparé et refus si ce journal échoue ; `seal` relit les sources, reçus et état natif sans mutation. `--reset` appelle seulement l'extension documentaire des deux profils C09, aussi appelée par `c09-seed.php` ; il ne rejoue pas le seed global, les échéances ou le reset C16. C09 est désormais 382/382, son action 8793 strictement préservée. Les anciens sceaux et reçus restent historiques, sans réécriture. Parcours, captures et limites : `production/C-17/A-VOIR.md`.

## C-18 — extractions en lecture seule

**Imagine → Extractions**, capacité C09 existante `imagine_extraire_abonnes` (ou administrateur), présente localité, mode de paiement, période d’échéance et état ; âge/étiquette sont désactivés « à venir ». Aucun rôle ou droit global ajouté. Deux formulaires GET choisissent l’extraction et ses filtres ; l’aperçu compte réellement les lignes natives, sans les mémoriser. Le POST CSV recontrôle capacité, jeton lié à l’extraction et à tous ses filtres, puis relit l’état courant. Un changement intervenu entre aperçu et téléchargement peut changer le nombre, explicitement signalé dans l’écran.

`ExtractionsRegles` est pur. Chaque fichier `extractions/*.php` contient titre, colonnes, filtres typés, requête native et prédicat ; ajouter une extraction de même source revient à ajouter un fichier, découvert automatiquement. `ExtractionsNatives` parcourt les abonnements WCS par pages de 100, lit l’identité du titulaire et la livraison de la souscription, les libellés de formule natifs, le mode C15 et l’état B02 existants. Aucun save, paiement, note, droit, relevé postal ou échéance n’est créé. Une ligne représente un abonnement (tous états), pas une personne dédupliquée. Échéance = minimum des dates natives non vides prochain paiement/fin, UTC ; une date absente reste vide et les bornes de période sont inclusives. Les modes C09 non raccordés restent vides, hormis les deux marqueurs fictifs A-VIR/A-PAPIER déjà reconnus par C15. Offerts/groupés absents non reconstruits.

Le flux `php://output` applique directement `Imagine\Connecteur\CsvProtection::cellule`, la primitive sécurisée partagée de C13/C04, puis `fputcsv` avec échappement explicite vide. Colonnes fermées ; adresse électronique vide quand `SansEmail::META` vaut `1`. Aucun mot de passe, jeton, référence bancaire, IBAN ou note n’est lu pour constituer une ligne. Aucun fichier produit par le contrôleur sur disque. Réponse privée/no-store, pièce jointe, `nosniff`. L’unique écriture est une option non autoloadée `imagine_extraction_journal_UUID` : opérateur, date UTC, extraction, nombre ; aucune sélection ni ligne d’abonné conservée. Elle est relue avant le flux ; son échec refuse le téléchargement. Le journal signifie « lignes préparées pour ce téléchargement », pas preuve de réception sur le poste client ; cinquante dernières lignes affichées, sans purge.

```powershell
python wp/tests/demo/c18-verifier.py                 # ciblé, aucun reset ni installation
python wp/tests/demo/c18-verifier.py --prepare --deploy --canonical
python wp/tests/demo/c18-visuel.py                  # capture Chromium, requêtes hors démo bloquées
```

Les tests purs sont ajoutés au paquet racine existant, sans manifeste/lock nouveau ; T01 les découvre. Le lanceur ciblé réemploie le runtime PHPUnit C16 et le bootstrap B04 en lecture seule, sans changer leurs octets. Préparation d’image réellement exécutée. Les recettes natives/HTTP n’ajoutent aucun profil et vérifient les empreintes avant/après ; seuls les événements d’extraction s’ajoutent. Les CSV de preuve fictifs sont relus depuis `production/C-18/`, jamais téléversés dans une racine publique. Parcours, décomptes exacts, réserve C09 historique inchangée et succession des empreintes partagées : `production/C-18/{A-VOIR.md,final.json}`. Prêt technique n’est ni validation visuelle de Ced ni GO sur du réel.




## C-19 — tableau de bord

**Imagine → Tableau de bord**, droit dédié `imagine_voir_tableau_bord`. C’est une méta-capacité WordPress résolue par `map_meta_cap` vers les deux capacités sources C18/C15 (`imagine_extraire_abonnes` et `imagine_gerer_echeances`) ; administrateur `manage_options` également admis. Le référent C09 est donc lecteur sans mutation de son rôle ni de ses capacités enregistrées. Le refus est contrôlé avant le rendu et avant le menu ; l’exception Woo d’accès administratif reste limitée à cette seule page. GET/HEAD seulement, POST 405 pour un lecteur autorisé, 403 sans droit.

Chaque fichier `indicateurs/*.php` contient son titre, son calcul pur, sa phrase affichée et ses libellés de mesures (`libelles`, tableau ou fonction des valeurs). Le rendu admin est générique, avec la clé brute comme filet. Catalogue mémoïsé en mémoire pour la seule requête : chaque fichier est exécuté une fois. Découverte automatique, aucune bibliothèque de graphiques ni script propre. `TableauBordNatives` réutilise les lignes C18 et les projections C15 ; sa sortie ne contient que titres, phrases, libellés et entiers, pas d’identité. Aucun journal, cache persistant, option, note, droit, paiement ou tâche planifiée n’est écrit par C19.

- Actifs : exactement les lignes du filtre **Actif** C18, donc des abonnements et non des personnes distinctes. Répartition par méthode native C15 ; vide reste « non renseigné ». Ni un paiement validé, ni un droit d’accès ou d’envoi C13 n’est déduit de cet état d’affichage.
- Échéances : mêmes fenêtres cumulatives C15 **30/90/180 jours**, nommées ainsi sous les libellés un/trois/six mois ; pas une nouvelle convention calendaire. Un instant unique, capturé avant les lectures ou injecté, est transmis à `EcheancesNatives::lire` et aux trois calculs purs. La règle C15 n’est pas dupliquée et ses appels à deux arguments restent compatibles. La phrase explique pourquoi le filtre de jours entiers tous états de C18 peut différer.
- Échecs : mêmes commandes liées et impayées que la vue C15, pas un nombre de personnes.
- Mouvements : standard **New Subscription** (créations natives, tous états), et abonnements **Ended** (fin native sur cancelled/expired), mois civil **UTC** jusqu’à maintenant. Les entrées incluent les créations en attente, pas seulement les souscriptions payées ; la création n’est jamais remplacée par la date de début du calendrier. C18 ne fournit pas ces dates ; aucun historique manquant, taux ou motif n’est reconstruit. Il ne s’agit pas de la métrique Woo « Signups » payée ni des annulations dont le terme est futur.

Les six emplacements du brief restent grisés « à venir », avec leurs données/définitions manquantes. S’y ajoute « Par moyen de paiement — distinction mode/moyen à arrêter à l’atelier », sans chiffre ni formule (défaut métier Q-2). Q-1 reste en attente : la composition des droits est conservée, aucun droit indépendant n’est créé. Une exception native remontée affiche « indisponibles », jamais un zéro de remplacement. Cela ne prétend pas détecter une erreur SQL que WooCommerce absorberait lui-même en une liste vide.

```powershell
python wp/tests/demo/c19-corrections.py --prepare --deploy --canonical
python wp/tests/demo/c19-corrections.py --readback-only
python wp/outils/demo/c19-unit.py unit-corrections TableauBord
python wp/tests/demo/test_c19_contract.py
```

Les tests PHP, dont l’adaptateur à horloge contrôlée à la borne 180 jours, sont découverts par le paquet racine existant ; aucun manifeste, lock ou runner fermé modifié. Le vrai parcours Chromium suit Imagine → Tableau de bord, avec requêtes hors démo bloquées. La recette native intercepte toute tentative SQL non SELECT ainsi que HTTP/email pendant calcul et rendu. Les empreintes commerciales, utilisateurs, rôles, actions/logs du planificateur et options métier sont inchangées. Pour les requêtes administratives complètes, trois seules options de bootstrap sont volatiles et explicitement exclues : expirations de cache de version WCS et de mise à jour Novamira, verrou du runner asynchrone Action Scheduler. Les sessions de connexion sont déjà exclues par la projection C18. Ce n’est pas une promesse d’absence d’écriture du cœur WordPress entier.

Les reçus historiques, dont `final-V2.json`, restent immuables. Le successeur `production/C-19/corrections-V2/final.json` lie les nouveaux octets et vérifie le README partagé par contrat de section, pas par l’empreinte figée du fichier entier. Les sources des derniers reçus C17/C18 sont contrôlées séparément, sans réécriture de ces lots. Le reçu C09 restauré est exigé exactement, action A-PAPIER comprise ; aucun reset. Voir `production/C-19/A-VOIR.md`. Prêt technique seulement ; validation visuelle de Ced et arbitrage Q-1 attendus.

## C-20 — livraison réduite acceptée le 26 novembre 2026 à 7 h 30

**PRET technique sur le seul périmètre réduit**, après les corrections de deuxième relecture : raccord d’accès borné et écrans sans bouton. Ce n’est pas une clôture ni la réalisation complète du §3.4. Le bouton « ne pas renouveler », sa confirmation, l’émission de `imagine_non_renouvellement_confirme` et la preuve de fin native du quatre-fois restent reportés au branchement sur staging vérifié avec GO explicite de Ced. Aucun profil automatique ni passerelle n’est fabriqué.

`Paywall` lit une adhésion Memberships `pending` liée nativement à une souscription `pending-cancel` avec fin renseignée comme active dans le minimum des fins Memberships/Subscriptions. Tests locaux du véritable raccord `Paywall::decisionPdf`, doublures natives et horloge de requête contrôlée : sans fin natif fermé ; une seconde avant ouvert ; à la fin exacte et après fermé ; fin Memberships antérieure prioritaire. Le vrai moteur C06 est appelé, aucune règle recopiée. C06 et C13 restent inchangés. Les contre-exemples `pending` non lié, lié à `active` et premier virement A-VIR restent fermés dans la recette native existante.

La sortie postale de la seule ligne A-CARTE 89 est **attendue** : terme payé du 25 décembre 2026 à 18:01:50 UTC avant clôture du 5 janvier 2027 à 00:00 Europe/Brussels ; **8 → 7**, motif `expire`. Aucun droit postal forcé. Le profil est manuel, méthode vide, produit privé ; la reprise est refusée par `contains_unavailable_product()`.

`RenouvellementRegles` retourne des codes de message, sans phrase d’interface ; `Renouvellement` associe ces codes à des traductions WordPress à chaînes littérales puis échappe le résultat HTML. Aucun contrôleur de mutation. A-VIR/A-PAPIER : manuel ; A-CARTE : absence de carte/passerelle déclarée ; A-SEPA4 : « faites la demande auprès d’Imagine », sans bouton, échéances du bloc dues. Marge C05 absente : **aucune fin native essayée**, ni preuve positive ni échec natif allégué. Cancel/Reactivate restent retirés sur la seule démo locale, sans modifier permission ou état natifs. Le hook de confirmation est réservé mais non émis ; aucun email, paiement, remboursement ou rétractation.

**À verrouiller au branchement, sans changement ici :** l’ordre actuel `arret_a_terme` avant `quatre_fois` est conservé ; décider explicitement sa priorité pour un quatre-fois natif `pending-cancel`. Hors démo, A-PAPIER avec méthode native vide reste inconnu (`EcheancesNatives::methode()` retourne `''`) et peut tomber dans `quatre_fois` : prévoir un raccord de méthode réelle validé, sans utiliser le drapeau fictif comme règle de production.

```powershell
python -B wp/tests/demo/c20-fusion-verifier.py
python -B wp/outils/demo/c20-unit.py parent-fusion-c20 C20
python -B wp/outils/demo/c20-unit.py parent-fusion-presentation RenouvellementRegles
```

Les preuves courantes et commandes parent sont dans `production/C-20/A-VOIR.md`. Préparation d’image/T01 complet et recettes natives existantes sont rejoués après les dernières écritures de code. README partagé contrôlé par section ; bootstrap, confidentialité et successeurs C21/B05/C22 préservés. Les reçus rouges et sceaux historiques restent immuables.

### Historique daté — 26 novembre 2026, deuxième passe avant l’arbitrage de 7 h 30

La mention d’alors « Pas PRET : le point 2 reste bloqué » constatait la sortie postale 8 → 7. L’arbitrage de 7 h a corrigé **le critère de réception**, pas C13 : ce comportement est attendu. L’ancien README et les preuves de blocage sont archivés dans `production/C-20/fusion-V2/README.md.before` et les reçus historiques, sans constituer l’état courant du lot.

## C-21 — confidentialité native

`Confidentialite` déclare un exporteur et un effaceur dans les outils natifs WordPress, par pages de 50. Il étend l’export Woo/WCS pour les numéros acquis et dates Imagine, sans réécrire commandes, souscriptions ou réglages de conservation. Options personnelles, marqueurs, brouillons, justificatifs et données personnelles des journaux sont projetés explicitement ; jamais de copie brute des metas, notes, jetons ou références de paiement. L’archive native masque les emails techniques, y compris son en-tête.

Le raccord C13 ajoute seulement deux filtres d’observation : empêcher la recollecte après une demande native d’effacement terminée et expurger les bénéficiaires concernés. La demande native reste nécessaire tant que le compte est conservé ; aucune durée ou table personnelle supplémentaire n’est créée. Le nettoyage des gels est un compare-and-swap relu, limité aux données de la personne. Les règles pures C13, les commandes et les abonnements restent sous leurs comportements natifs. Le hook de suppression du compte retire aussi les ajouts Imagine restants.

Rejeu : `python -B wp/outils/demo/c21-unit.py LABEL`, `python -B wp/tests/demo/c21-http.py LABEL`, `python -B wp/outils/demo/c21.py security LABEL`, `python -B wp/tests/demo/c21-verifier.py`. Le parcours réel crée puis supprime un seul compte fictif et vérifie les autres profils, actions métier comprises. Inventaire, limites de conservation, outils à ouvrir et preuves : `production/C-21/`. Les sections historiques de ce README et les sceaux des lots précédents ne sont pas réécrits ; C21 vérifie ses seules sections partagées par contrat.

## B-05 — partenaires

`Partenaires` enregistre `imagine_partenaire_du_mois` dans le formulaire Settings API **C10 existant**, via les hooks administratifs, sans modifier la bibliothèque close. Un seul identifiant de partenaire publié, choix manuel ; absent, zéro, invalide ou dépublié : pas de bloc. Les valeurs invalides soumises conservent le choix valide courant. Nonce, contrôle `manage_options` et sauvegarde restent ceux de `options.php`. Pas de rotation, nouveau rôle, service ni règle d'acceptation.

Le thème conserve le gabarit individuel B01 et son filtre natif `WP_HTML_Tag_Processor` : `sponsored` ajouté aux liens HTTP(S) sortants du corps partenaire, avec conservation des autres relations. Les fiches internes restent ordinaires ; aucun lien d'article n'est touché. Bloc, cartes de liste et fiche portent la classe structurelle `imagine-partnership` et le texte **Partenariat** ; aucun CSS ajouté. Le designer doit encore dessiner leur distinction.

Le CPT est exclu de la recherche ; les requêtes publiques de recherche/flux sont également fermées lorsqu'un visiteur force explicitement son type. Les requêtes éditoriales du thème restent sur `post`. Rejeu ciblé : `python -B wp/tests/demo/b05-verifier.py` ; installation autorisée sur la seule démo : `python -B wp/outils/demo/b05.py deploy LABEL`. Tests natifs/Chromium et deux captures, sources officielles et limites : `production/B-05/`. Les reçus antérieurs et les sections partagées sont préservés par contrat, pas par un hash global de README.

## C-22 — préférences locales des newsletters

`NewslettersRegles` valide le catalogue et les transitions pures. `NewslettersReglages` étend le formulaire Settings API C10 existant : identifiant stable, intitulé, présentation et principale (une seule). Ajouter la dernière ligne vide suffit ; vider un identifiant retire la lettre des écrans, sans prétendre effacer les choix historiques du compte. Ne jamais recycler un identifiant. Catalogue vide en l'absence de réglage ; les trois lettres fictives sont des données du constructeur C22, pas des constantes du rendu.

`Newsletters` ajoute **Mes newsletters** au dashboard Woo existant et le shortcode `[imagine_newsletters]` à la page **Nos newsletters**. POST natif `admin-post.php`, nonce lié au titulaire, identité issue de la session, verrou utilisateur et version du formulaire/catalogue. Stockage dans `imagine_newsletters_preferences` : par identifiant, `choix` booléen, `date_utc`, `origine=lecteur|defaut_creation`. Aucun choix absent n'est antidaté. Une sauvegarde identique ne déplace pas sa date. Le compte marqué sans email n'a aucune case ni rubrique ; seule une phrase explique l'absence.

`imagine_newsletters_creation=non|oui` est fermé par défaut et ne touche jamais aux comptes existants. `oui` choisit la seule principale lors du hook natif `user_register`, sauf sans-email. L'origine reste explicitement un réglage, pas un consentement ; une confirmation volontaire ultérieure remplace cette origine par `lecteur`. Question pour Imagine : à la création du compte, faut-il inscrire à la principale et avec quel consentement explicite ? Aucun statut de double confirmation, persona ou synchronisation n'est fabriqué.

Le seul point d'accroche est `imagine_newsletters_preferences_modifiees` (ID, nouvel état, ancien état), émis après persistance, sans écouteur ni transport dans ce lot. Aucun email, API Brevo ou paiement. Les outils WordPress C21 exportent et effacent la méta via leur inventaire existant ; aucun outil de confidentialité parallèle ni durée de conservation nouvelle. Inventaire détaillé et parcours : `production/C-22/{inventaire-confidentialite.md,A-VOIR.md}`.

Rejeu ciblé : `python -B wp/tests/demo/c22-verifier.py` (lecture et vérification), `python -B wp/outils/demo/c22-unit.py LABEL`, `python -B wp/outils/demo/c22.py runtime LABEL`, `python -B wp/tests/demo/c22-http.py LABEL`. Les tests purs sont découverts par le paquet racine existant/T01, sans nouveau manifeste ni lock. La recette HTTP utilise la vraie route Woo lue à l'exécution, restaure les lignes/absences des préférences, réglages et cache de suivi créé à la première visite ; les journaux C10 restent append-only. Les tentatives HTTP natives de bootstrap sont toutes court-circuitées par la garde hors ligne et les avatars navigateur bloqués : ce n'est pas une assertion de zéro tentative du cœur. Les sources partagées sont contrôlées par contrat successeur, sans réécrire les reçus historiques.

## C-24 — personnalisation facultative locale

`PersonnalisationRegles` valide les questions et choix fermés, les réponses datées et la conjonction de transmission en PHP pur. `Personnalisation` raccorde trois formulaires distincts au dashboard WooCommerce : réponses, effacement, consentement. `PersonnalisationReglages` ajoute les questions au formulaire Settings API **C10 existant**, sous son bouton sans déplacement, réserve définitivement les identifiants et journalise les changements. `PersonnalisationConfidentialite` ajoute les callbacks natifs d'export/effacement sans modifier C21.

Réglage : `imagine_personnalisation_questions` (identifiant, titre, choix simple/multiple, liste JSON de choix fermés). Métadonnées : `imagine_personnalisation_reponses` (choix et `date_utc` par question), `imagine_personnalisation_consentement` (`accord`, `date_utc`), séparées des préférences newsletters. Répondre ne vaut pas consentir. Compte sans email : réponses locales possibles, aucune case de consentement et projection fermée. Les réserves techniques d'identifiants survivent à l'effacement.

`Personnalisation::attributsConnecteur($id)` est la seule projection prévue pour le futur connecteur : consentement distinct explicite **ET** au moins une newsletter active choisie avec `origine=lecteur` **ET** compte admissible à l'email. `defaut_creation`, origine absente ou inconnue ne comptent jamais. `imagine_personnalisation_attributs_modifies` est émis après sauvegarde admissible, sans écouteur livré ; `imagine_personnalisation_apres_inscription_achat` reste un emplacement nommé non raccordé. Aucun transport Brevo, email ou tâche planifiée nouvelle.

En cas d'échec réel d'insertion du journal C10, seule la préimage interne validée, sous drapeau privé et égalité stricte de valeur, évite la validation des identifiants réservés. L'option restaurée est relue ; une nouvelle saisie réservée reste refusée. Les tests retirent séparément une question puis un choix avec refus SQL du journal, et contrôlent préimage persistée et absence de 500, aussi par deux vrais POST `options.php`.

Depuis la racine du dépôt, contrôle local hors réseau, sans site ni mutation :

```bash
PYTHONIOENCODING=utf-8 python -B production/C-24/verifier-fusion2050-V2.py
python -B wp/outils/demo/c24-gates.py prepare nouvelle-preparation-V2
python -B wp/outils/demo/c24-gates.py regression nouvelle-regression-V2
```

Recettes **nécessitant le seul site fictif gardé `imagine-test-demo`**, données métier restaurées et snapshots durables privés avant les sessions/mutations ; choisir des étiquettes neuves terminées par `-V2` :

```bash
python -B wp/outils/demo/c24.py rules nouvelles-regles-V2
python -B wp/outils/demo/c24.py runtime nouveau-natif-V2
python -B wp/outils/demo/c24-corrections.py journal-question nouveau-journal-question-V2
python -B wp/outils/demo/c24-corrections.py journal-choix nouveau-journal-choix-V2
python -B wp/outils/demo/c24-corrections.py newsletter nouvelle-origine-V2
python -B wp/tests/demo/c24-http.py nouveau-parcours-V2
python -B wp/outils/demo/c24-mutations.py nouvelles-gardes-V2
```

`c24.py rules` utilise seulement le conteneur local hors réseau ; les autres recettes de ce second bloc accèdent à la démonstration. Le parcours HTTP rend la vraie page C10 et vérifie la section entre ouverture/fermeture de son formulaire ; sa mutation témoin retire uniquement l'injection C24 de la requête d'essai. Les scripts historiques de récupération ne font pas partie du rejeu. Questions rangées : localité fermée par défaut, inscription par défaut exclue de la transmission, emplacement visuel à valider par Ced. Preuves courantes et limites : `production/C-24/{A-VOIR.md,TRANSMISSION.md,manifest-fusion2050-V2.json}`. PRET technique ne vaut ni clôture, ni validation visuelle, ni GO sur le réel.

## B-06 — espace coopérateurs

`CooperateursRegles` porte les règles pures ; `Cooperateurs` protège côté serveur les cinq pages de l’espace et leurs sorties REST/recherche/flux. Le lien public de B-08 ne donne aucun droit. Le statut privé `imagine_cooperateur` ne remplace ni un abonnement, ni un achat de numéro. Deux réglages de rôles, `imagine_cooperateurs_roles_attribut` et `imagine_cooperateurs_roles_lecture`, ont le défaut **Administrateur seul**. Les changements sont journalisés ; un journal illisible rend les outils de confidentialité incomplets. Les callbacks natifs exportent/effacent les seules données du titulaire, sans modifier les tiers.

Rejeu local : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1` ; parcours et commandes natives ciblées dans `production/B-06/A-VOIR.md`. Aucun raccord CoopHub ni paiement.

## B-07 — agenda

`AgendaRegles` porte la validation pure ; `Agenda` raccorde les événements `imagine_evenement`, l’archive `/evenements/`, les fiches et les inscriptions locales privées `imagine_inscription`. Métadonnées éditoriales : `imagine_type`, `imagine_date`, `imagine_heure`, `imagine_lieu`, `imagine_url_partenaire`. Les événements partenaires renvoient au site extérieur avec la relation commerciale ; aucun billet ni paiement n’est livré. Rien ne part par email ou HTTP. Les callbacks `AgendaConfidentialite::exporter/effacer`, enregistrés sous `imagine-agenda` dans les outils natifs C-21/WordPress, travaillent par adresse ; une lecture en erreur ne devient pas un export vide réussi.

Tests de l’adaptateur inclus dans la suite racine : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1`. Recette fictive et limites : `production/B-07/A-VOIR.md`.

## B-08 — Soutenir et Notre coopérative

Pages et menu WordPress natifs, sept sous-pages éditoriales vides et formulaire discret hors menu. Réglages natifs **Réglages → Soutenir**, option `imagine_soutenir[don]` fermée par défaut et `imagine_soutenir[parts_url]` vide par défaut. Une adresse de parts n’accepte que **HTTPS**, sans identifiants ; elle produit un lien `rel="sponsored"`, pas une intégration CoopHub. Le don ouvert reste un emplacement **sans paiement**.

Les propositions restent dans le type privé `imagine_sujet` (`wp_posts`), corps vide et métadonnées `imagine_sujet_nom/email/texte/consentement/date` (`wp_postmeta`). Aucun email, appel, rapprochement de compte ou inscription newsletter. `Sujet::enregistrer()` échappe à la frontière `wp_insert_post` avec `wp_slash($meta)` et compare les valeurs normalisées après lecture : les antislashs restent identiques au formulaire, au détail admin et à l’export. `SujetConfidentialite::exporter/effacer` sont les callbacks natifs `imagine-sujets`, additifs à C-21, paginés et recherchés par adresse (avec ou sans compte), tiers préservés.

Le seed de démonstration marque le menu dès le hook de création natif, puis chaque item dès son insertion ; le rejeu récupère aussi un item interrompu avant son rattachement, mais refuse un menu/item étranger. Une cible absente donne une URL custom vide, jamais un repli silencieux vers une autre page. Rejeu local, sans site : `python -B wp/outils/demo/b08-local.py LABEL_NEUF`. Suite partagée : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1`. Recettes HTTP et seed exclusivement sur `imagine-test-demo`, commandes et preuves corrigées dans `production/B-08/{NOTE.md,A-VOIR.md}` ; contrôle du paquet sans réseau ni argument : `python -B production/B-08/verifier.py`.


## C-25 — rétractation, demande seule

Dans Mon compte, une commande admissible (ou la commande initiale de son abonnement, titulaires vérifiés) propose **Me rétracter**. Étape 1 : référence, délai UTC et motif libre facultatif, sans écriture. Étape 2 : confirmation explicite avec nonce lié à la cible et au motif. Une note WooCommerce **privée**, sa métadonnée et un événement du journal partagé C10 sont persistés ; l’accusé daté se retrouve ensuite. Rejeu : le premier accusé, pas une deuxième demande. Aucun remboursement, annulation, accès fermé, email ou transport extérieur. Un motif avec antislash est adapté à l’API WP par `wp_slash($record)` ; l’original sert à la comparaison stricte après lecture et sort à l’export natif C21 sans perte.

Deux réglages dans le formulaire C10 existant : `imagine_retractation_reglages[jours]`, entier **1–365**, défaut **14** ; `imagine_retractation_reglages[origine]`, **paiement** par défaut ou **manuelle** (champ de date UTC sur la commande). Date absente/invalide : fermé. Borne finale incluse et trace anti-doublon dépersonnalisée conservées en attendant les arbitrages métier ; aucune règle légale validée. Les hooks additifs C25 `added_option`/`updated_option` journalisent avant/après, auteur et date UTC. Si le journal échoue, la préimage exacte (ou l’absence initiale) est restaurée et relue ; un échec de cette inverse interrompt la requête. Aucune modification de la bibliothèque close C10 : son injection HTML actuelle reste inchangée pour la démo, le hook de rendu dédié relève d’un prochain passage.

Export/effacement : callbacks ajoutés aux outils natifs C21/WordPress, sans changer leur politique de conservation. Le motif et la note sont retirés, la trace métier date/référence est dépersonnalisée pour éviter le redépôt. **Suppression du compte (`delete_user`) : une panne SQL persistante empêchant le nettoyage provoque `wp_die` et refuse la suppression par prudence**, pour ne pas laisser de trace orpheline. Réparer le stockage puis réessayer ; ce refus n’est ni une suppression réussie, ni une durée légale de conservation.

Depuis la racine du dépôt, contrôles **locaux hors réseau**, sans charger le site (image de tests déjà disponible ; aucune installation sur l’hôte) :

```text
python -B wp/outils/demo/c25.py local canonique-<nom-neuf>
python -B wp/outils/demo/c25-mutations.py mutations-<nom-neuf>
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
python -B wp/outils/demo/c25-finaliser.py verifier
```

Recette **live uniquement sur `imagine-test-demo`**, avec garde d’identité et coupe-circuit B00 vérifiés ; mutation puis restauration, jamais un audit du réel :

```text
python -B wp/outils/demo/c25-recette.py recette-<nom-neuf>
```

Cette recette écrit une préimage durable privée dans le scratch Hermes avant les sessions/mutations. Elle passe réellement par `options.php` (création/modification et refus SQL du journal dans les deux cas ; groupe de recette borné à C25 pour préserver les autres réglages), puis relit les valeurs, et traverse le POST du motif à antislash jusqu’à la métadonnée et au callback enregistré de l’export C21. Les profils, commandes classiques/HPOS, options et actions métier reviennent à leur état initial et sont relus ; caches et données temporaires ne sont pas des règles métier. Les anciens reçus restent historiques. Commandes exactes, preuves courantes et questions visuelles/juridiques : `production/C-25/{NOTE.md,A-VOIR.md}` ; PRET technique seulement.

## B-09 — FAQ, pages légales et contact

Cinq **pages WordPress natives**, menu natif `imagine-footer`, sans changement du menu principal. La FAQ contient seulement quatre blocs Titre : **Accès numérique, Abonnement, Facturation, Livraison**. Dans Pages → FAQ du service client, ajouter un bloc **Détails** sous une rubrique ; le résumé est la question, le paragraphe intérieur est la réponse. Enregistrer depuis l’éditeur natif, sans code. Le seed ne réécrit jamais les textes déjà édités. CGV, politique de confidentialité et gestion des cookies sont vides ; `wp_page_for_privacy_policy` désigne vraiment la page de confidentialité publiée. Aucun bandeau ni texte juridique livré.

`Contact` réemploie la validation pure `SujetRegles` et la mécanique B-08 corrigée : POST natif avec nonce, consentement au recontact facultatif et non coché, aucune recherche de compte ni newsletter. Stockage privé `imagine_contact`, corps vide, cinq clés `imagine_contact_nom/email/texte/consentement/date`. Les POST sont déséchappés une fois, puis `wp_slash($meta)` compense le déséchappement natif à l’écriture ; nom et message avec antislash sont relus identiquement au détail admin et à l’export. Toutes les capacités du type exigent `manage_options`, création manuelle refusée ; ni REST, recherche ni export WXR. Rien ne part par email ou HTTP.

`ContactConfidentialite::exporter/effacer` est déclaré sous **`imagine-contacts`** dans les outils natifs WordPress/C-21, par adresse (avec ou sans compte), pages de 50, tiers préservés ; une panne de lecture/effacement reste incomplète. Inventaire destiné à la voie 1 dans `production/B-09/NOTE.md` : ce type et ses postmeta devront être vidés par un prochain lot d’import autorisé, **l’import clos n’est pas modifié ici**.

Le seed marque le menu dès sa création et les items dès leur insertion, récupère un item interrompu avant son rattachement, refuse les pages/menus/items étrangers et n’actualise pas les items déjà identiques. La preuve coupe réellement un processus au troisième item, puis reprend dans un autre processus. Le footer n’ajoute ni style ni fallback vers le menu principal.

Contrôle du paquet **hors réseau, sans argument, Python 3.11** :

```text
python -B production/B-09/verifier.py
```

Tests ciblés isolés et suite générale (les six tests Contact sont découverts par le paquet racine existant ; les recettes natives demeurent explicitement séparées) :

```text
python -B wp/outils/demo/b09-local.py parent-unitaires-NOM-NEUF
python -B wp/outils/demo/b09-mutations.py parent-mutations-NOM-NEUF
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Recettes **sur le seul `imagine-test-demo` fictif**, avec snapshots privés durables, remise en état et readback ; choisir chaque fois une étiquette neuve :

```text
python -B wp/outils/demo/b09.py runtime parent-structure-NOM-NEUF
python -B wp/outils/demo/b09.py reseed parent-seed-stable-NOM-NEUF
python -B wp/outils/demo/b09-recette.py parent-contact-NOM-NEUF
python -B wp/outils/demo/b09-readback.py parent-readback-NOM-NEUF
```

`seed` est la recette de première création/interruption déjà jouée, pas une commande à relancer sur le squelette complet. `reseed` relit deux rejeux sur le squelette livré. Adresses, preuves finales et limites : `production/B-09/{A-VOIR.md,NOTE.md,final-V2.json}`. PRET technique du squelette ne vaut ni validation visuelle ni conformité juridique, ni accord sur le réel. Les paquets clos C-23/C-26 et les autres sections de ce README restent inchangés.

## C-27 — Comment nous avez-vous connus ?

### Le standard d'abord — cinq lignes

1. WooCommerce propose déjà l’attribution d’origine d’une commande à partir du référent, des UTM et de cookies de session ([documentation officielle](https://woocommerce.com/document/order-attribution-tracking/)).
2. Cette origine de navigation n’est pas une réponse volontaire du lecteur ; C27 ne la remplace pas et n’active aucun traceur.
3. Le hook natif `woocommerce_thankyou` reçoit la commande sur la confirmation classique et dans le bloc Woo « informations supplémentaires » ; C27 recontrôle propriétaire, paiement daté et clé de commande.
4. Les commandes sont lues par `wc_get_order` et les getters CRUD, compatibles HPOS ([contrat Woo officiel](https://developer.woocommerce.com/docs/best-practices/data-management/crud-objects/)).
5. Le petit complément déclaratif est enregistré localement et déclaré aux [exporteurs](https://developer.wordpress.org/plugins/privacy/adding-the-personal-data-exporter-to-your-plugin/) et [effaceurs WordPress](https://developer.wordpress.org/plugins/privacy/adding-the-personal-data-eraser-to-your-plugin/), sans Odoo ni newsletter.

**Après paiement uniquement**, le titulaire connecté voit une liste fermée facultative sur sa confirmation. Jamais de champ de profil dans le tunnel ni dans C16. `is_paid()` et `date_paid` sont obligatoires ; `created_via=imagine-c16` reste refusé même payé. Les invités et autres comptes sont refusés, sans rapprochement par email. Une seule proposition est mémorisée à l’affichage ; rafraîchir ou ignorer ne relance pas la question. « Continuer sans répondre » et la réponse vide ne bloquent rien.

Réglage **C10**, `imagine_acquisition_choix` : une ligne `identifiant|libellé`, maximum 20 choix ; identifiants minuscules de 1–40 caractères, libellés de 80 caractères maximum. Liste absente, vide ou invalide : question fermée. La démonstration reçoit seulement « Radio fictive \\ lune » et « Journal martien fictif ». La section reste sous le bouton, comme C22/C24/C25 ; aucune retouche de C10 ou de ses autres sections. Journal C10 avant/après/auteur/date UTC ; panne du journal : préimage exacte relue et réglage refusé.

Stockage non autoloadé : `imagine_acquisition_vue_ID` (proposition, compte, date UTC) et `imagine_acquisition_reponse_ID` (commande, compte, date UTC, choix, libellé figé). L’unicité SQL de l’option et un verrou utilisateur ferment les doubles envois et les courses de première source. Aucune interface d’édition, aucune métadonnée ajoutée au payload de commande Woo. `imagine_source_acquisition` garde le **tableau structuré complet** (`commande`, `compte`, `date`, `choix`, `libelle`), jamais un simple libellé. Il est initialisé uniquement après une lecture SQL fraîche, fiable et sans ligne existante, sous le verrou et dans la transaction ; une ligne préexistante, même vide, est conservée. Une erreur de lecture annule la déclaration et sa source par rollback. `wp_slash` reste à la frontière `update_user_meta` ; aucun autre profil n’est réécrit.

**Imagine → Acquisition déclarée**, mêmes droits que C19, GET/HEAD seulement : nombres par réponse et période civile UTC inclusive. Aucun nom, compte ou numéro de commande dans le tableau. Un libellé historique reste distinct après changement de la liste ; l’effacement retire ses déclarations du compte. Une lecture impossible n’est pas remplacée par zéro.

Les callbacks natifs `imagine-acquisition` de C21 exportent réponses, propositions et source de compte ; l’effacement retire ces données personnelles et laisse seulement commande/état effacé, sans date ni source ni compte. Sous le même verrou, le POST refuse le tombstone **REPONSE ou VUE**, y compris une proposition seulement vue et effacée sans réponse : un ancien formulaire signé ne peut plus recréer la donnée. L’effaceur invalide `user_meta` avant sa lecture SQL fiable, vérifie la disparition effective de toutes les lignes SOURCE avant commit, puis relit aussi SOURCE après commit avant `done`. Cache vide empoisonné, première lecture en échec, suppression refusée ou relecture finale incertaine : `done=false`, `items_retained=true`. Cette opération de confidentialité est la seule exception à l’immutabilité. Tiers préservés ; suppression du compte refusée si le nettoyage échoue. Aucun événement d’export commercial, email, appel HTTP, tâche planifiée ou consentement newsletter ajouté.

```text
python -B production/C-27/verifier.py
python -B wp/outils/demo/c27.py local parent-unitaire-NOM-NEUF
python -B wp/outils/demo/c27-mutations.py parent-mutations-NOM-NEUF
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Le vérificateur sans argument est local, hors réseau, Python 3.11 standard. Les douze tests PHPUnit sont découverts par le paquet racine existant, dont cinq régressions de la fusion d’abord rouges puis vertes. Onze mutants hors réseau sont détectés. Recettes réellement mutantes sur le seul site fictif gardé : `python -B wp/outils/demo/c27-native.py LABEL-NEUF`, `python -B wp/outils/demo/c27-recette.py LABEL-NEUF`, puis `python -B wp/outils/demo/c27-corrections.py LABEL-NEUF` (vraies pannes SQL I1/I2, effacement refusé, relecture finale défaillante et ancien POST de proposition sans réponse). Préimages privées durables, commandes fictives jetables, profils/commandes/options/actions natifs restaurés exactement et relus. La boutique reste « À venir » ; filtre Woo de prévisualisation temporaire et retiré, sans changement des réglages. Le reçu courant est `production/C-27/correction-final-V2.json` ; `final-V2.json` et le vérificateur historique sont l’historique antérieur à la fusion, non une réception des sources actuelles. Adresses, commandes parent et limites dans `production/C-27/{A-VOIR.md,NOTE.md}`. Aucun paiement réel ni email ; PRET technique n’est pas validation visuelle ou GO sur le réel.

## B-10 — points de vente

Type privé natif `imagine_vente`, titre + métadonnée `imagine_vente_ligne` ; option non autoloadée `imagine_vente_actifs` pour la liste publiée. Une page WordPress ordinaire restitue le formulaire et la liste, sans nouveau gabarit ni CSS. Le pied de page natif B09 reçoit un lien ; son menu et les items existants sont conservés, le principal ne change pas. Les cinq lignes de choix standard et les trois lignes pour la carte future sont dans `production/B-10/NOTE.md`.

**Réglages → Points de vente** (`manage_options`, POST et nonce natif) : correspondance JSON et séparateur `;`, `,` ou tabulation ; charger un CSV UTF-8 avec en-tête remplace la liste. Mapping requis : `nom`, `adresse`, `localite`, `postal` ; `personne` et `telephone` uniquement sur correspondance explicite et toujours échappés. Retirer leur mapping masque immédiatement leur affichage, même avant un nouvel import. Les autres colonnes ne sont ni rangées ni affichées. Le CSV n’est pas ajouté aux médias et n’est pas conservé. Réglages techniques d’import sur leur écran dédié : l’écran C10 clos reste inchangé.

`imagine_vente_configuration` contient `mapping`, `separateur`, `carte`. `carte=0|1`, défaut `0` ; valeur inconnue fermée. À `1`, simple emplacement textuel sans fournisseur, géocodage, image, iframe ou script. Recherche exacte sur localité ou code postal, insensible aux accents/casse, sans préfixe ni rayon ; liste entière triée par localité puis nom quand la recherche est vide.

Un rejeu identique conserve les IDs, sans doublons ; une nouvelle liste est préparée avant bascule puis l’ancienne est retirée. L'option non autoloadée `imagine_vente_nettoyage` garde les IDs restant à supprimer, avant bascule ; un échec affiche « Liste remplacée ; nettoyage incomplet », pas un import refusé. Le même CSV reprend ce nettoyage, même lors du no-op et dans une nouvelle requête, sans réinsérer les actifs. Une ancienne liste illisible est réparable par remplacement. Refus : compte, numéro physique initial, code fixe en résultat, **libellé français traduisible dans l'interface**, jamais la donnée. En-tête invalide ou aucune ligne acceptée : ancienne liste conservée ; dans le second cas, les numéros/motifs des lignes sont tout de même rendus. Plafonds techniques : 2 Mio, 2 000 commerces acceptés, 500 caractères par champ. Un arrêt brutal peut laisser un verrou d’import à retirer après diagnostic ; pas de tâche de reprise automatique ni géocodage ajouté.

Unicode : décomposition NFD par intl/Normalizer si disponible, retrait des marques et ligatures `œ→oe`, `æ→ae`. Sans intl, repli latin étendu déclaré dans NOTE.md, sans promesse de translittération de tout Unicode ; intl devra être garanti pour la décomposition Unicode générale sur le futur hébergement. Configuration lue une seule fois par rendu. Défaut C2 documenté : le no-op strict reste sensible à l'ordre des clés JSON du mapping. La liaison page↔extension devra quitter le seed démo pour un futur script de bascule versionné ; **hors lot**.

```text
python -B wp/tests/demo/b10-verifier.py
python -B wp/tests/demo/b10-verifier.py --live
python -B wp/outils/demo/b10-local.py LABEL-NEUF
python -B wp/outils/demo/b10.py runtime LABEL-NEUF
python -B wp/outils/demo/b10-recette.py LABEL-NEUF
```

Le premier vérificateur est autonome et hors réseau, le second lit uniquement imagine-test-demo. Corrections du 27 novembre 2026 : **14 tests PHPUnit / 80 assertions**, découverts par T01 ; **13 contrôles natifs**, **31 contrôles navigateur**. Tests rouges avant corrections puis verts. Repli sans intl réellement exercé en PHP isolé ; Normalizer présent et testé sur WordPress natif (rollback InnoDB, sans bouchon d’écriture). La recette navigateur charge/recharge réellement le CSV par multipart, injecte un refus natif de suppression ciblé puis reprend entre requêtes sans changer les IDs, répare une méta active cassée, refuse la ligne 32 et un nonce invalide, exerce NFC/NFD hors ancienne table, ligatures, casse/postal et les deux valeurs de carte. Observations positives des détecteurs ; aucun tiers sur les deux rendus publics, aucune tentative email/HTTP issue de B10. Les avatars Gravatar de l’administration native sont détectés et bloqués avant transport par la recette, séparément du rendu public. Préimage privée durable, sessions exactes et observateur retirés puis relus ; 30 commerces manifestement fictifs laissés pour Ced, carte OFF, reprise vide ; les autres objets métier et navigations sont inchangés. Rebuild `wp/tests/preparer-image.ps1` effectué après ajout des tests avant PRET. Rejeu frais : **1 187 tests / 36 494 assertions**, aucun échec/erreur ; **584 contrôles outils** verts. A32 / `A32_PARTIAL_EVIDENCE` reste hors périmètre. Sources et preuves courantes : `production/B-10/corrections-reception-V2.json`, parcours et limites dans A-VOIR/NOTE ; reçus historiques conservés. Aucun B11/C28 ni bibliothèque close modifié.

## B-11 — vidéos, podcasts et sommaire audio

Champs éditoriaux séparés du contenu : `_imagine_video`, `_imagine_podcast`, protégés, non exposés dans REST. Boîte « Vidéo et podcast » des articles et numéros, capacité native `edit_post`, nonce, refus global conservant les deux anciennes valeurs si une adresse est invalide. Ne pas coller l'adresse brute dans le corps : l'auto-oEmbed natif des autres contenus n'est pas modifié. Le lien est créé directement par le thème, sans oEmbed, iframe, vignette ou JavaScript distant. Sur un article, `Paywall::decision()` est vérifiée avant lecture/rendu des champs ; les publics qui ne reçoivent que l'extrait ne reçoivent ni lien ni adresse.

Option `imagine_medias` : `hosts` liste fermée d'hôtes exacts (vide par défaut, un seul hôte fictif livré : `video-fictive.example.invalid`) et `integration` chaîne fermée `0|1`, défaut `0`. HTTPS sans identité, port, caractère de contrôle ou antislash ; le podcast reste un simple lien HTTPS. La section rejoint le formulaire C10 sous le bouton existant, sans modifier C10. À `1`, un div vide est affiché, sans appel, même après un éventuel clic : aucun consentement/lecteur tiers n'est implémenté.

`AudioNumero` réutilise **sans modification** `PdfNumero::directory()`, ses en-têtes privés/no-store et `Paywall::decisionPdf()` (C06, type PDF). Blob aléatoire `.wav` dans le même répertoire hors webroot, mode 0600 ; pas d'attachment WordPress, ni chemin/URL physique publié. Chaque GET/HEAD `/?imagine_audio=ID` reprend la décision ; méthodes étrangères 405, références invalides 404, refus vers la page numéro sans adresse audio. Le `<audio controls preload="none">` n'existe que pour l'ayant droit. Dépôt éditorial local explicite via `AudioNumero::proteger(ID, SOURCE)` : SOURCE doit déjà être dans le répertoire privé C11 ; pas d'upload public ou distant. Démo : trois secondes de silence PCM fabriquées, sans contenu tiers. Le même silence est déposé sur les numéros 11 (acheteur existant) et 39 (abonné actif existant), car C06 ferme le PDF antérieur du profil A-CARTE ; aucune règle ni aucun droit changé.

```text
python -B wp/outils/demo/b11-local.py LABEL-NEUF
python -B wp/outils/demo/b11.py runtime LABEL-NEUF
python -B wp/outils/demo/b11-recette.py LABEL-NEUF --policy-1330
python -B wp/tests/demo/b11-verifier.py
python -B wp/tests/demo/b11-verifier.py --live
```

La réception courante est **PRET technique selon la consigne du 27 novembre 2026 à 13h30**, dans `production/B-11/reception-politique1330-V2.json`. Limite explicite en tête de NOTE : **aucune saisie/enregistrement/rechargement UI automatisé n'est revendiqué** ; trois lignes de parcours Ced ouvrent A-VOIR. Lecture du WordPress installé et rendu natif : les deux champs sont réellement proposés par le pont blocs (`advanced/default`, compatibilité native par défaut), 11 contrôles verts ; aucun défaut de déclaration, donc aucun changement du code fonctionnel. Observateur passif, sans filtre d'éditeur ni réduction d'`allowed_options`. Le vrai formulaire complet compare les **16 valeurs effectives avant/après OFF→ON→OFF** avec les défauts du propriétaire (ou ceux déclarés à Settings API), sans normaliser les valeurs existantes. Les cinq absences devenues explicites à leur défaut exact sont listées dans le reçu et NOTE : découverte, relecture, solidaire, création newsletter, rétractation. Aucune différence métier ; tout écart réel reste rouge, au lot propriétaire, sans réparation B11. Recette adaptée `python -B wp/outils/demo/b11-recette.py LABEL-NEUF --policy-1330` : **102/102**, vrai hook `save_post` sous nonce/capacité, changement et effacement relus, refus d'hôte/antislash, OFF/ON, 32 sorties étanches. Témoin backend transactionnel distinct après code final **8/8**, deux mutations no-persist détectées, jamais présenté comme preuve UI. Gravatar public réellement déclenché, rouge et bloqué avant transport ; exception limitée à l'origine et au contexte admin. Zéro tiers public et HTTP/oEmbed/mail B11 ; tentatives ambiantes Novamira et dispatchs locaux Action Scheduler qualifiés par chemin/pile, tous bloqués, sans joker local. Neuf tests d'assertions, PHPUnit B11 **4/34**, natif **23/23**, image reconstruite et vrai rejeu **1195/36573**, outils **22/720**, verts ; bilan distinct des paquets A31/A32 rouge hors lot. **16 restaurations relues**, options et absences comprises ; sondes absentes. `reception.json`, `reception-corrections-V2.json`, leurs preuves et les documents bloqués archivés restent historiques, intacts. La seule section B11 de ce README partagé est changée ; complément de vérification des voisins non clos C27/C28 dans `politique1330-voisins-V2.json`, sans resceau. Les deux commandes du vérificateur ci-dessus lisent la nouvelle réception et rendent **PASS / code 0**. B12 non implémenté ; `catch` Paywall intact ; limites du corps/oEmbed et parcours dans `production/B-11/{NOTE.md,A-VOIR.md}`. Aucun GO réel ni validation visuelle revendiqués.

**Réception courante — contrat du 27 novembre 2026, 16h30 :** `production/B-11/reception-contrat-V2.json`, `NOTE-contrat-V2.md` et `A-VOIR-contrat-V2.md` remplacent uniquement le contrat de réception ci-dessus ; les preuves et réceptions 13h30 restent historiques, intactes. Les commandes `python -B wp/tests/demo/b11-verifier.py` et `python -B wp/tests/demo/b11-verifier.py --live` contrôlent les empreintes des fichiers propres, le bloc B11 exact et unique et cette section bornée au prochain titre de niveau 2. Aucun sceau entier de l’amorçage, aucune condition sur les PRET voisins. La politique 13h30 demeure : `UI_save_verified=false`, 16 options effectives, témoin backend 8/8 et trois lignes Ced, sans nouvelle recette UI. Qualification courte : `python -B wp/tests/demo/b11-c29-contract-tests.py B11` ; mutation propre/bloc absent ou modifié/doublon refusés, ajout étranger accepté. Aucun code fonctionnel ni amorçage modifié ; pas de rejeu général supplémentaire sans nouveau PHP.

## C-28 — packs thématiques

### Le standard d'abord — cinq lignes

1. Le [produit groupé natif WooCommerce](https://woocommerce.com/document/managing-products/#grouped-products) présente plusieurs produits sur une page ; chaque enfant entre séparément au panier.
2. Ce conteneur n'est pas lui-même achetable et n'a pas de prix global autonome (`WC_Product_Grouped::is_purchasable()` et prix des enfants, code Woo installé relu).
3. [Product Bundles](https://woocommerce.com/document/bundles/bundles-configuration/#pricing) ajouterait un prix de base global, des enfants configurables et leurs règles de prix/stock ; aucune extension commerciale n'est activée.
4. Choix proportionné : **un produit simple natif**, une liste de numéros publiée dans son administration et un prix pour l'ensemble ; pas de nouveau type Woo, produit enfant ou moteur de vente.
5. Le seul complément est l'instantané des numéros à la persistance du paiement ; chaque numéro repasse ensuite par **la décision et le remboursement C14**, sans modifier les bibliothèques closes C06/C11/C14.

Dans les données générales d'un produit simple : sélection multiple **Pack : numéros inclus**. La saisie passe par le formulaire natif Woo (nonce/capacité), les IDs sont stricts, dédoublonnés, publiés ; une liste invalide est refusée sans remplacer l'ancienne. Un pack valide retire le rattachement C14 « un seul numéro » ; inversement, un numéro unique valide délie le pack, même lors d'un enregistrement programmatique partiel. Vider la sélection retire le pack pour les achats suivants. Aucune remise pour un numéro déjà possédé.

`imagine_pack_numeros` contient seulement les IDs éditoriaux. Un pack invalide est refusé côté serveur : achetabilité native, ajout direct et revalidation du panier déjà constitué au checkout ; un dernier garde refuse la première persistance d'un paiement à composition vide. Défaut prudent : **bloquer tout le pack**, prix global inchangé, aucun recalcul ni règle tarifaire nouvelle.

À la création d'une ligne, `_imagine_pack_candidat` note son éligibilité sans figer la liste. La liste est préparée en mémoire seulement pour la **première transition persistée non payée vers payée**, puis `_imagine_pack_paye` garde `numeros`, `paye_le`, `produit` après la sauvegarde du paiement. Une commande déjà payée ou déjà datée n'est jamais reconstruite depuis le produit vivant : instantané manquant/non fiable = fermé ; une sauvegarde le signale par la méta visible `imagine_pack_anomalie`. Une panne après paiement persisté et avant ligne laisse donc la ligne fermée et signalée lors de la sauvegarde tardive d'un objet rechargé, jamais antidatée avec une nouvelle composition. Une modification/suppression du produit ne retire pas les instantanés fiables acquis. Une erreur avant persistance n'en crée aucun.

Le filtre additif `imagine_achat_instantanes` du **raccord** `AchatsNumeros::droits()` déroule les IDs de la même ligne commerciale, puis appelle inchangé `AchatNumero::droit()` pour chacun. Propriétaire, statut, date, quantité, publication et remboursement restent ceux de C14. Même réglage `imagine_achat_remboursement=commande|ligne`, aucun réglage parallèle : rembourser la ligne pack retire tous les numéros de cette ligne ; un partiel non ventilé suit la politique existante ; un total ferme les deux modes. `MonCompte`, `Paywall`, `PdfNumero` et les bibliothèques closes sont inchangés. La question de composition passée suit `docs/decisions.md` : pas de réglage nouveau.

`single-product.php` réutilise les classes B01, les couvertures/titres/dates publics de B04 et le bouton/panier Woo ; aucun corps d'article, PDF embarqué, CSS ou JS nouveau. La fiche démo affiche un prix explicitement fictif. Le seul MU de démonstration `c28-demo.php` exempte **la fiche du pack fictif** de Coming Soon sur le seul `imagine-test-demo`, sans changer l'option de boutique, les passerelles ni les autres fiches.

```text
python -B wp/tests/demo/c28-verifier.py
python -B wp/tests/demo/c28-verifier.py --live
python -B wp/outils/demo/c28-local.py LABEL-NEUF
python -B wp/tests/demo/c28-canaris.py LABEL-NEUF
python -B wp/outils/demo/c28-corrections.py native LABEL-NEUF
python -B wp/outils/demo/c28.py runtime LABEL-NEUF
python -B wp/outils/demo/c28-recette.py LABEL-NEUF
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Les deux premières commandes vérifient le paquet et, avec `--live`, relisent seulement le site fictif. PHPUnit C28 inclut les doubles persistés de `candidat`/`payer`/`instantanes` et des gardes panier ; les cinq canaris de source rouges puis verts sont rejouables hors réseau dans une copie jetable. Le banc natif prouve aussi la panne **après** paiement persisté, le rechargement, l'édition du pack et la sauvegarde tardive fermée/signalée. La recette navigateur est temporairement mutante : formulaire produit natif, panier réel, paiement/remboursements natifs **sans passerelle ni transfert**, GET articles/PDF et compte pour acheteur/tiers/anonyme ; ajout du quatrième et retrait du premier sans changer le passé. Les 32 témoins C26 sont réutilisés sans changer sa matrice. Snapshot privé avant la recette, retour relu des profils, commandes, réglages, sessions et actions métier ; aucune réinitialisation C09. Fixture laissée : seul produit pack fictif, liste de trois numéros et option de déclaration, pas de nouvel achat permanent. Preuves, commandes exactes et limites : `production/C-28/{NOTE.md,A-VOIR.md,reception-corrections.json}` ; `reception.json` est historique. PRET signifie prêt à relire, ni clôture, ni validation visuelle, ni GO sur le réel.

## C-29 — la fiche du contact pour Brevo, sans Brevo

### Le standard d'abord — cinq lignes

1. L’[extension WordPress officielle de Brevo](https://wordpress.org/plugins/mailin/), publiée par Brevo, fournit formulaires, listes, champs personnalisés, consentement/double opt-in et SMTP après connexion au compte.
2. [Brevo for WooCommerce](https://wordpress.org/plugins/woocommerce-sendinblue-newsletter-subscription/), du même éditeur, synchronise clients et nouveaux inscrits ainsi que les données historiques et nouvelles de commandes.
3. Elle permet notamment opt-in, opt-out, double opt-in et segmentation par achats ; cela ne définit pas le statut métier Imagine d’un bénéficiaire, d’un coopérateur ou d’un tarif.
4. Rien n’est installé ni activé ici : aucun compte, aucune clé, aucun traceur, aucun envoi et aucune synchronisation ; notices publiques vérifiées dans `production/C-29/sources-officielles-V2.json`.
5. Le seul complément C29 est une projection locale des sources du site et un aperçu administratif ; les noms Brevo et le branchement restent à définir.

`ContactBrevoRegles::fiche(array $source)` est l’unique calcul pur. Une newsletter du catalogue choisie avec `origine=lecteur` et un email recevable donnent une fiche ; sans choix ou sans email, fiche absente avec raison. Un retrait explicite de tout donne uniquement `{"statut":"a_retirer"}`, sans identité, tarif ni attribut personnel. Les anciens choix de listes supprimées ne sont pas inventés comme choix actifs ou désinscriptions.

`ContactBrevo::fiche($id)` lit le statut CRUD WCS **active seulement**, pas le droit numérique C06 : grâce, pending-cancel, achat d’un numéro, adhésion manuelle ou rôle d’équipe ne deviennent pas « abonné ». Les bénéficiaires identifiés par le contrat de lecture `EnvoiRelations::beneficiaires` restent `inconnu`, tarif compris. Aucun rapprochement par email, nom ou login ; les profils C09 offerts/groupés sans lien natif ne sont pas prétendus reliés. Les tests ajoutent des liens natifs temporaires puis les retirent par rollback. Le coopérateur vient de l’attribut B06, sans ouvrir de droit.

La personnalisation est **directement** la valeur de `Personnalisation::attributsConnecteur($id)`. Aucune copie de sa règle du consentement distinct, aucune lecture des réponses brutes dans le code C29. Les clés internes sont `email`, `statut`, `cooperateur`, `tarif`, `newsletters`, `personnalisation` ; les codes de statut sont `abonne|non_abonne|inconnu|a_retirer`.

**Imagine → Ce qui partirait vers Brevo** réutilise exactement `TableauBordAdmin::autorise()` : administrateur ou les deux droits C19 existants, sans modifier rôle/capacité. Identifiant de compte saisi par GET ; fiche/raison et totaux sur tous les comptes, une seule fiche par compte. HEAD admis, autre méthode 405 pour le lecteur autorisé, 403 sans droit. Privé/no-store, aucune sauvegarde, option, méta, cache persistant, payload stocké, export de fichier, journal, écouteur métier, file, tâche ou transport. Une source native remontant une exception donne « indisponible », sans faux zéro ; aucune promesse sur une erreur SQL absorbée par Woo en liste vide.

**Réglages → Tarifs de la fiche Brevo** est une configuration distincte, réservée à `manage_options`, par le groupe Settings API autonome `imagine_brevo_tarifs` (jamais le groupe C10). La correspondance JSON fermée est `ID natif produit/variation → clé interne de tarif` ; défaut vide, toute configuration invalide ferme la liste. Seules les lignes de l’abonnement actif sont lues. Produit non listé, ligne manquante, plusieurs tarifs contradictoires ou aucun abonnement actif : `inconnu`. Aucune somme ni grille de prix calculée. La démo reçoit les six correspondances fictives des produits C09 existants, par `c29.py seed`, sans changer les profils ; aucun tarif Imagine présumé. L’écran de consultation n’enregistre jamais ce réglage.

```text
python -B production/C-29/verifier.py
python -B production/C-29/verifier.py --live
python -B wp/outils/demo/c29.py pure NOM-NEUF
python -B wp/outils/demo/c29.py native NOM-NEUF
python -B wp/outils/demo/c29-http.py NOM-NEUF
python -B wp/outils/demo/c29-neighbors.py NOM-NEUF
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Le premier lecteur est hors réseau, sans site ; `--live` ne fait que relire la démo gardée. Les recettes native/HTTP mutent temporairement **le seul imagine-test-demo**, restaurent profils/options/actions et sessions de leur départ, puis vérifient ; jamais un reset global. Tableau attendu indépendant des 27 comptes dans `wp/tests/demo/c29-attendus.php`, tests purs découverts par le paquet racine existant. Preuve positive de personnalisation, retrait du consentement distinct puis mutant lisant les réponses brutes détecté. SQL, HTTP et mail interceptés pendant le vrai calcul/rendu, avec témoins positifs ; vrai parcours administratif GET, refus et capture. Les caches d’amorçage du cœur restent distincts du zéro écriture/appel de C29 ; détails et incidents de banc réparés dans NOTE.

Bootstrap partagé : ajout du seul bloc C29. La réception complémentaire courante est dans `production/C-29/reception-complement-voisins-V2.json` ; les historiques C27/C28/B11/B12 et le complément B12 restent intacts. Aucun changement de bibliothèque close, de prix, d’accès, de paiement ou d’Odoo. PRET technique ne vaut ni clôture, ni validation visuelle, ni GO sur le réel.

**Réception courante — corrections du 27 novembre 2026, reprise 21h18 :** `production/C-29/reception-corrections-V2.json`, `NOTE-corrections-V2.md` et `A-VOIR.md`. Le refus explicite du lecteur survit à la sortie de sa lettre du catalogue ; un choix positif supprimé administrativement n'est jamais un retrait. Pour les groupes, C29 lit les liens natifs `relation_native/user_id`, actifs ou suspendus, sans changer EnvoiRelations ni ses règles postales. Appels multilignes et traductions littérales corrigés. Réceptions antérieures conservées. Preuves courantes : 23 pures, 57 natives, 73 HTTP, 27 profils ; états natifs active/paused relus avant assertion. Le socle `lot_reception_contract.py` est inchangé : empreintes des fichiers propres, bloc C29 exact et unique, seule section README bornée. Aucune empreinte globale ni dépendance de PRET voisin. Lecteurs usuels offline/live PASS. Ni clôture, validation visuelle ni GO réel.

## B-12 — aucun appel sortant depuis le corps
WordPress traite URL seule, bloc `core/embed` et `[embed]` via `WP_Embed` ; un handler natif prioritaire rend les seules URL externes en liens, avant tout cache/lecteur.
L'affichage et le cache post-enregistrement (`cache_oembed`, AJAX natif) sont verrouillés ; `pre_oembed_result` couvre la résolution directe, `pre_render_block` les anciens HTML embarqués.
L'aperçu `/oembed/1.0/proxy` appelle `get_data()` : `rest_dispatch_request`, après permissions et avant son cache, rend un lien sans cadre/script/vignette ; réglages B11 sans effet sur ce verrou.
Interne délégué sans changement, corps jamais réécrit, aucun réglage nouveau ; sources natives officielles et levée future en trois lignes dans `production/B-12/NOTE.md`.
Tests : `python -B wp/tests/demo/b12-verifier.py` (`--live` = lecture seule) ; rejeu PHPUnit standard, matrice native et mutation B00 : `production/B-12/A-VOIR.md`.
La suite scellée `rejouer.ps1` utilise des **doublures maison** (`IntegrationsCorpsB12Stubs.php`) : elle **ne prouve pas le pipeline natif ni le zéro appel sortant réel**. Cette preuve vient de `wp/tests/demo/b12-runtime.php`, complétée par `b12-routes-runtime.php` pour les routes MAJ/mixed, caches anciens et permissions ; exécution sur le seul WordPress fictif gardé, observateur avant transport.
**À chaque montée de version du cœur WordPress**, rejouer cette matrice native (enregistrement/cache, rendu, aperçu, variantes de casse, cache absent/ancien et permissions) avant de déclarer le lot prêt : l'ordre handlers/cache et dispatch/permissions/transient est un détail interne non contractuel. Réception courante : `production/B-12/reception-contrat-V2.json`. Arbitrage de 16h30 : `SOURCES` vérifie exactement les fichiers propres B12, le bootstrap partagé seulement l'unique bloc d'enregistrement B12 exact, et le README sa seule section bornée ; aucun sceau entier du bootstrap ni PRET voisin n'entre dans le contrat. Les anciens reçus et le complément C29 restent historiques, sans resceau silencieux.

## B-13 — menu principal et menu étendu

### Le standard d'abord — cinq lignes
1. Les menus natifs WordPress conservent les liens, l'ordre et les sous-menus : https://developer.wordpress.org/reference/functions/wp_nav_menu/.
2. Le filtre natif `walker_nav_menu_start_el` permet d'ajouter la sélection sous l'entrée Thématiques sans remplacer le menu : https://developer.wordpress.org/reference/hooks/walker_nav_menu_start_el/.
3. La sélection d'articles illustrés n'est pas une simple entrée de menu : `Navigation` ajoute uniquement titre, image à la une et lien, jamais extrait ni corps.
4. Les listes HTML imbriquées restent lisibles au clavier sans JavaScript ; aucune forme, animation ou feuille de style ajoutée.
5. Les Transients fournissent le cache natif : https://developer.wordpress.org/apis/transients/ ; reconstruction après expiration, publication/dépublication, méta, modification/affectation de thématique et réglage du nombre.

Menu B08 conservé, mêmes identifiants : huit entrées dans l'ordre du §3.1. Connexion reste Connexion pour un lecteur connecté, comme le menu natif existant ; il ouvre Mon compte. S'abonner pointe vers `/abonnement-en-attente/`, explicitement fictive et sans paiement. Le seed B13 ne recrée aucun menu. Trois articles réservés illustrés fictifs sont ajoutés à la démonstration, chacun avec couverture synthétique existante ; leurs corps et extraits sont des témoins interdits dans le menu.

Réglages → Menu principal : 1 à 10 articles récents par thématique, défaut 3. Les thématiques vides sont conservées. Cache du seul fragment public indépendant du lecteur, images différées et non prioritaires ; aucun nouveau contenu de visiteur collecté. Réception : `production/B-13/reception-V2.json`, `A-VOIR.md` ; `python -B production/B-13/verifier.py` et `--live`. Socle `lot_reception_contract.py` inchangé, adapté localement par injection temporaire de paramètres : fichiers propres, bloc B13 exact/unique et section README bornée, aucune empreinte globale ni disponibilité de voisin. Tests natifs transactionnels, vrai navigateur sans JS et témoins existants de C26, matrice C26 non étendue. Ni habillage, validation visuelle ni GO réel.

### Corrections B13-01 à B13-04 — réception courante

Réception courante `production/B-13/reception-corrections-V2.json`, anciens reçus et PRET conservés. Les neuf articles récents de la sélection fictive reçoivent individuellement une couverture synthétique existante comme image à la une si manquante, sans remplacer un récent par un ancien ; chaque article est contrôlé sur les six surfaces. **Hors cette préparation de démonstration, un article récent sans image reste sélectionné sans image, sans placeholder ni exclusion** : défaut technique retenu, aucun habillage inventé.

Le seed contrôle et rétablit le lien S'abonner détenu vers la page d'attente **avant son retour sur fixture existante**. La séquence native réelle B08 → B13 → B08 → B13 est testée en transaction, IDs et nombre d'entrées conservés. Invalidation ajoutée pour `deleted_term_relationships` : retrait direct par `wp_remove_object_terms`, cache d'abord présent, reconstruction sans l'article et thématique devenue vide conservée. Pour les limites 1, 3 et 10 : identifiants exacts comparés par thématique sur deux thématiques temporaires de douze articles, dates décroissantes puis ID décroissant ; oracle indépendant de la requête du composant.

L'ordre alphabétique des thématiques est conservé. La sur-invalidation `save_post` est laissée telle quelle (cache public reconstructible, sans risque métier). Le menu étendu dépend de la classe native `imagine-nav-thematiques` de l'entrée B08 : la retirer le fait disparaître silencieusement ; fragilité héritée documentée, pas de nouvelle fonction en correction. Libellé Connexion inchangé.

Commandes courantes : `python -B wp/outils/demo/b13-corrections.py native NOM-NEUF`, `... browser NOM-NEUF`, et `python -B production/B-13/verifier.py` (`--live` lecture seule). Le banc partagé B13, utilisé par B14/B15, et le socle commun sont inchangés ; les copies de seeds utilisées pour la séquence sont temporaires, ciblées et supprimées après vérification.

## B-14 — accueil dans l’ordre du cahier des charges

### Le standard d'abord — cinq lignes
1. WordPress choisit nativement `front-page.php` pour l'accueil : https://developer.wordpress.org/themes/classic-themes/basics/template-hierarchy/.
2. Les images à la une viennent des pièces jointes natives, avec dimensions et variantes : https://developer.wordpress.org/reference/functions/wp_get_attachment_image/.
3. L'API accepte explicitement `loading` et `fetchpriority` : seule la couverture de l'accueil est eager/high, toutes les autres images B13/B14 sont lazy/low.
4. WordPress ne compose pas l'ordre métier §3.2 : `Accueil::rendre` relie les composants existants, sans constructeur ni second réglage de numéro.
5. Numéro = `Imagine\Theme\imagine_issue_query(1)` de B04 ; produit C14, reportage libre B04, Agenda B07 et partenaire B05 restent leurs sources natives, sans droits ni prix recalculés.

`front-page.php` appelle seulement le composant de structure : numéro/couverture/titre/date/résumé ; conversion ; reportage libre si présent ; newsletter par lien ; thématiques ; trois événements futurs au plus ; Soutenir ; coopérative ; partenaire du mois **inchangé avec son étiquette Partenariat**. La section Derniers articles de B01 est retirée, comme demandé ; l'ancre `imagine-thematiques` du menu reste valide. Recherche native conservée après les sections. Aucun style, animation, vidéo, iframe ou collecte d'email ajouté.

Le produit du numéro courant n'est pas en vente dans la démo : le bouton Acheter est donc absent. Le test natif crée un produit simple entièrement fictif **dans une transaction annulée**, vérifie le lien positif, dépublie le produit, relit son état natif et vérifie l'absence ; aucune vente ni commande n'est effectuée. Le reportage déjà désigné reçoit seulement la couverture synthétique existante comme image à la une si elle manquait, seed idempotent, pas de second article ni numéro.

Réception : `production/B-14/reception-V2.json`, `A-VOIR.md` ; `python -B production/B-14/verifier.py` (`--live` = lecture seule). Tests natifs transactionnels, vrai HTTP anonyme/A-PAPIER, contrôle Partenariat de B05 conservé, témoins C26 et mutations témoins ; matrice C26 inchangée. Socle et banc B13 inchangés, contrat propre uniquement pour l'amorçage/README. Aucune bibliothèque close modifiée, aucun contenu réservé rendu, aucun message de visiteur nouveau. Validation visuelle attendue, aucun GO réel.

### Corrections B14 — ancre, contrat rejouable et reportage partagé

Réception courante `production/B-14/reception-corrections-V2.json`. `imagine-abonnement` est rétabli sur la conversion qui contient réellement S'abonner ; `imagine-agenda` est également conservé pour les anciennes entrées. Le navigateur clique le vrai lien d'un paywall anonyme et vérifie l'arrivée sur cette cible unique avec son CTA. Un second test PHPUnit, exécuté en processus séparé avec bouchons minimaux, appelle **le vrai `Accueil::rendre`** et verrouille ordre des neuf sections, unique eager/high, cible d'abonnement et absence vidéo/iframe/corps réservé : il est bien dans le JUnit canonique.

`imagine_issue_free_article($issue)` dans `inc/catalogue.php` est l'unique sélection, appelée par B04 et `Accueil::libre`. Deux articles libres temporaires d'ordres distincts puis égaux prouvent l'identité et le départage par ID. L'extraction touche `single-imagine_numero.php`, également scellé par B11 : complément natif B11 de 23 contrôles sous B14 et preuve du diff strict limité au choix du libre ; aucun octet média/audio changé, aucun reçu B11 réécrit silencieusement. Les empreintes historiques du gabarit B11 restent celles de son époque, avec ce complément explicite.

Les deux anciennes recettes B01 ont été **réellement tentées mais ne sont pas vertes** : le test statique exige encore l'ancien token `imagine_pdf_id` et aucun JavaScript (incompatible avec C11/B03 déjà clos), et la recette démo refuse l'inventaire étendu avant même sa première requête HTTP (articles ajoutés depuis B00/C08). Ces rouges sont conservés dans B14, sans modifier B01 ; le contrat d'ancre courant est prouvé nativement et par clic réel. Modules Python html5lib/BeautifulSoup uniquement en scratch isolé pour ce rejeu, rien installé dans le dépôt ou sur un site.

La dérive 1206 → 1208 n'est **pas** imputable à A32/A33 : la comparaison des vrais JUnit trouve exactement les deux tests B15 et cinq assertions ajoutées, aucune suppression. `derive-comptage-V2.json` fait foi. Le nouveau garde-fou B14 ajoute ensuite son propre test. Les absences de pages cibles restent la question non bloquante de la fusion : aucun nouveau repli inventé, dépendances de la démonstration présentes.

## B-15 — pied de page identique sur toutes les pages

### Le standard d'abord — trois lignes
1. L'emplacement de menu natif et `wp_nav_menu` conservent les liens B09 et leurs identifiants, sans recréer ni dupliquer le menu : https://developer.wordpress.org/reference/functions/wp_nav_menu/.
2. Une zone de widgets native est disponible via `register_sidebar` : https://developer.wordpress.org/reference/functions/register_sidebar/ ; elle n'est pas ouverte ici, les cinq zones et leur ordre étant imposés et identiques partout.
3. Le gabarit natif `footer.php` appelle un composant de structure, et le fragment numéro utilise les Transients natifs : https://developer.wordpress.org/apis/transients/ ; aucune géolocalisation, carte ou service tiers.

Cinq zones : abonnement vers la page d'attente B13 ; newsletter par lien ; numéro de `Accueil::numero()` (même requête B04, couverture miniature lazy/low, titre et lien) ; recherche B10 par lien ; mentions avec le menu existant B09, **données natives inchangées**, y compris le lien de points de vente que B10 y avait ajouté. Les cinq liens B09 restent une seule fois chacun. Pas de formulaire d'email. Aucun contenu de visiteur nouveau collecté.

Cache du fragment numéro seulement, indépendant du public. Publication/dépublication d'un numéro, modification de métadonnée, couverture ou suppression invalident ce cache ; disparition/expiration le reconstruit. Les indicateurs natifs de page courante du seul menu footer sont neutralisés au rendu (classes current/page_item et aria-current) pour rendre le HTML identique même sur une page légale ; ni menu stocké ni menu principal modifié. Les identifiants que WordPress déduplique lors de rendus répétés dans **une même requête** sont une différence de banc natif déclarée ; les vraies réponses HTTP sont comparées **entières et brutes sans normalisation**.

Le mode lecture B03 masque déjà `.imagine-shell > footer` par CSS ; comportement conservé et observé dans le navigateur. Réception `production/B-15/reception-V2.json`, `A-VOIR.md` ; `python -B production/B-15/verifier.py` (`--live` lecture seule). Preuves : quatre pages demandées et FAQ pour vérifier le contexte courant, anonyme/A-PAPIER, cache renouvelé après publication native puis retour exact après retrait ; témoins C26 et mutations, sans étendre sa matrice. Socle, banc B13 et lots clos inchangés. Structure seule, visuel à valider, aucun GO réel.

## C-32 — cookies observés sur la démonstration

### Le standard d’abord — cinq lignes
1. WordPress ne dépose pas de cookie en simple lecture ; connexion : test, authentification et état connecté ; langue choisie : `wp_lang`. Source officielle : https://developer.wordpress.org/advanced-administration/wordpress/cookies/.
2. Les commentaires peuvent retenir nom/email/adresse si le visiteur choisit cette option ; ils sont fermés sur cette démonstration, aucun cookie de commentaire n’y a été observé (même source).
3. WooCommerce emploie deux témoins de panier de session et `wp_woocommerce_session_[hash]`, deux jours par défaut : https://woocommerce.com/document/woocommerce-cookies/ ; aucun de ces trois cookies en lecture sans geste.
4. L’attribution d’origine WooCommerce pose sept `sbjs_…` dès lecture JavaScript ; six de session, `sbjs_session` à trente minutes : https://woocommerce.com/document/order-attribution-tracking/ et documentation cookies ci-dessus.
5. Le réglage natif **WooCommerce → Réglages → Avancé → Fonctionnalités → Attribution des commandes**, option `woocommerce_feature_order_attribution_enabled=no`, éteindrait l’attribution ; il est resté activé, aucun lot rendu n’est modifié.

`Cookies::liste()` contient exactement les quatorze noms/motifs réellement observés, producteur, geste, durée et usage. Le filtre natif de contenu rend cette liste sous le texte B09 demeuré vide, sur sa seule page Cookies, sans bandeau, consentement, service ni script livré. Motifs entièrement ancrés ; aucune valeur de cookie dans les preuves du dépôt. Les durées de session et d’authentification sont recoupées avec le code installé ; connexion testée sans « Se souvenir de moi ». La démo HTTP ne prétend pas qualifier les cookies HTTPS/administratifs ni un futur outil de consentement.

**Écart explicite : l’attendu « aucun cookie en simple lecture » est rouge**, sept cookies natifs d’attribution sur les 44 pages relevées, zéro `Set-Cookie` serveur. Le brief interdit de les retirer : liste fermée et étanchéité vertes, pas de promesse de zéro cookie ni de conformité juridique. Consentement à décider par Imagine et son conseil. `strict-reading-V2.json` conserve ce FAIL séparément.

Recettes : `python -B wp/outils/demo/c32.py native LABEL`, `python -B wp/outils/demo/c32-browser.py LABEL`, `python -B production/C-32/verifier.py --live`. Le navigateur exécute réellement les scripts ; code connu C30, vrai ajout au panier B04, vraie connexion d’un compte fictif supprimé et langue de connexion ; deux sondes HTTP/JavaScript font refuser le même contrôleur hors liste puis sont retirées. Paniers/sessions et état métier restaurés avec lecture native, préimages privées persistées ; aucun nouveau contenu de visiteur stocké. PHPUnit est découvert dans le paquet existant, préparation d’image puis rejeu canonique exigés avant PRET ; socle de contrat et C26 inchangés.





