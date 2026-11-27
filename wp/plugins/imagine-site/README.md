# Imagine — site (B-00, modèle provisoire)

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

Stockage non autoloadé : `imagine_acquisition_vue_ID` (proposition, compte, date UTC) et `imagine_acquisition_reponse_ID` (commande, compte, date UTC, choix, libellé figé). L’unicité SQL de l’option et un verrou utilisateur ferment les doubles envois et les courses de première source. Aucune interface d’édition, aucune métadonnée ajoutée au payload de commande Woo. `imagine_source_acquisition` sur le compte est initialisé **seulement si vide**, avec `wp_slash` à la frontière `update_user_meta` ; aucun autre profil n’est réécrit.

**Imagine → Acquisition déclarée**, mêmes droits que C19, GET/HEAD seulement : nombres par réponse et période civile UTC inclusive. Aucun nom, compte ou numéro de commande dans le tableau. Un libellé historique reste distinct après changement de la liste ; l’effacement retire ses déclarations du compte. Une lecture impossible n’est pas remplacée par zéro.

Les callbacks natifs `imagine-acquisition` de C21 exportent réponses, propositions et source de compte ; l’effacement retire ces données personnelles et laisse seulement commande/état effacé pour interdire un redépôt, sans date ni source ni compte. Cette opération de confidentialité est la seule exception à l’immutabilité. Tiers préservés ; panne de lecture ou d’écriture signalée comme incomplète, suppression du compte refusée si le nettoyage échoue. Aucun événement d’export commercial, email, appel HTTP, tâche planifiée ou consentement newsletter ajouté.

```text
python -B production/C-27/verifier.py
python -B wp/outils/demo/c27.py local parent-unitaire-NOM-NEUF
python -B wp/outils/demo/c27-mutations.py parent-mutations-NOM-NEUF
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Le vérificateur sans argument est local, hors réseau, Python 3.11 standard. Les sept tests PHPUnit sont découverts par le paquet racine existant. Recettes réellement mutantes sur le seul site fictif gardé : `python -B wp/outils/demo/c27-native.py LABEL-NEUF` puis `python -B wp/outils/demo/c27-recette.py LABEL-NEUF`. Préimages privées durables, sept commandes fictives jetables dont un vrai brouillon C16, profils/commandes/options/actions natifs restaurés exactement et relus. La boutique de démo reste nativement « À venir » : la recette emploie le filtre Woo de prévisualisation uniquement pour ses requêtes marquées et retire son observateur, sans ouvrir la boutique ni changer ses réglages. Adresses, commandes parent et limites : `production/C-27/{A-VOIR.md,NOTE.md,final-V2.json}`. Aucun paiement réel ni email ; PRET technique n’est pas validation visuelle ou GO sur le réel.

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
python -B wp/outils/demo/b11-recette.py LABEL-NEUF
python -B wp/tests/demo/b11-verifier.py
python -B wp/tests/demo/b11-verifier.py --live
```

La réception courante est **BLOQUÉE, sans PRET**, dans `production/B-11/reception-corrections-V2.json` ; `reception.json` et ses reçus sont conservés comme historique. Le code fonctionnel B11 n'a pas changé. La recette et l'observateur ne forcent plus l'éditeur classique ni `allowed_options` : vrai formulaire complet de 16 options, vrais éditeurs blocs. Le contrôle strict révèle cinq autres options créées depuis une absence initiale ; les champs B11 ne sont pas accessibles dans le parcours des deux éditeurs, donc persistance/effacement/reload UI, ON et mutation no-persist UI **ne sont pas validés**. Le témoin Gravatar public est réellement détecté avant transport ; exception limitée au contexte et à l'origine admin. Témoin backend réel distinct : changements, effacements, deux mutations d'écriture sous transaction, 8/8, jamais substitués à la preuve UI. Image reconstruite, PHPUnit B11 4/34, natif 23/23, sept unités de preuve et vrai rejeu général 1189/36512 verts ; bilan distinct des paquets A31/A32 rouge, hors lot et sans resceau. État initial et absence des sondes relus, historiques conservés. Les deux commandes du vérificateur ci-dessus pointent la réception complémentaire et rendent **BLOCKED / code 1**. Limites oEmbed dans le corps, catch Paywall hors lot, captures, preuves et commandes parent : `production/B-11/{NOTE.md,A-VOIR.md}`. Aucun GO sur le réel ni validation visuelle revendiqués.

## C-28 — packs thématiques

### Le standard d'abord — cinq lignes

1. Le [produit groupé natif WooCommerce](https://woocommerce.com/document/managing-products/#grouped-products) présente plusieurs produits sur une page ; chaque enfant entre séparément au panier.
2. Ce conteneur n'est pas lui-même achetable et n'a pas de prix global autonome (`WC_Product_Grouped::is_purchasable()` et prix des enfants, code Woo installé relu).
3. [Product Bundles](https://woocommerce.com/document/bundles/bundles-configuration/#pricing) ajouterait un prix de base global, des enfants configurables et leurs règles de prix/stock ; aucune extension commerciale n'est activée.
4. Choix proportionné : **un produit simple natif**, une liste de numéros publiée dans son administration et un prix pour l'ensemble ; pas de nouveau type Woo, produit enfant ou moteur de vente.
5. Le seul complément est l'instantané des numéros à la persistance du paiement ; chaque numéro repasse ensuite par **la décision et le remboursement C14**, sans modifier les bibliothèques closes C06/C11/C14.

Dans les données générales d'un produit simple : sélection multiple **Pack : numéros inclus**. La saisie passe par le formulaire natif Woo (nonce/capacité), les IDs sont stricts, dédoublonnés, publiés ; une liste invalide est refusée sans remplacer l'ancienne. Un pack valide retire le rattachement C14 « un seul numéro ». Vider la sélection retire le pack pour les achats suivants. Aucune remise pour un numéro déjà possédé.

`imagine_pack_numeros` contient seulement les IDs éditoriaux. À la création d'une ligne, `_imagine_pack_candidat` note son éligibilité sans figer la liste. Après persistance native d'un paiement daté, `_imagine_pack_paye` garde `numeros`, `paye_le`, `produit`, une seule fois, y compris une liste devenue vide. La liste est donc celle **du paiement**, pas du panier ; absence de marque historique : pas de reprise rétroactive. Une modification/suppression du produit ne modifie pas l'instantané. Un échec avant persistance du paiement ne crée pas cet instantané, testé rouge puis vert.

Le filtre additif `imagine_achat_instantanes` du **raccord** `AchatsNumeros::droits()` déroule les IDs de la même ligne commerciale, puis appelle inchangé `AchatNumero::droit()` pour chacun. Propriétaire, statut, date, quantité, publication et remboursement restent ceux de C14. Même réglage `imagine_achat_remboursement=commande|ligne`, aucun réglage parallèle : rembourser la ligne pack retire tous les numéros de cette ligne ; un partiel non ventilé suit la politique existante ; un total ferme les deux modes. `MonCompte`, `Paywall`, `PdfNumero` et les bibliothèques closes sont inchangés. La question de composition passée suit `docs/decisions.md` : pas de réglage nouveau.

`single-product.php` réutilise les classes B01, les couvertures/titres/dates publics de B04 et le bouton/panier Woo ; aucun corps d'article, PDF embarqué, CSS ou JS nouveau. La fiche démo affiche un prix explicitement fictif. Le seul MU de démonstration `c28-demo.php` exempte **la fiche du pack fictif** de Coming Soon sur le seul `imagine-test-demo`, sans changer l'option de boutique, les passerelles ni les autres fiches.

```text
python -B wp/tests/demo/c28-verifier.py
python -B wp/tests/demo/c28-verifier.py --live
python -B wp/outils/demo/c28-local.py LABEL-NEUF
python -B wp/outils/demo/c28.py runtime LABEL-NEUF
python -B wp/outils/demo/c28-recette.py LABEL-NEUF
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Les deux premières commandes vérifient le paquet et, avec `--live`, relisent seulement le site fictif. La recette navigateur est temporairement mutante : formulaire produit natif, panier réel, paiement/remboursements natifs **sans passerelle ni transfert**, GET articles/PDF et compte pour acheteur/tiers/anonyme ; ajout du quatrième et retrait du premier sans changer le passé. Les 32 témoins C26 sont réutilisés sans changer sa matrice. Snapshot privé avant la recette, retour relu des profils, commandes, réglages, sessions et actions métier ; aucune réinitialisation C09. Fixture laissée : seul produit pack fictif, liste de trois numéros et option de déclaration, pas de nouvel achat permanent. Preuves, commandes exactes et limites : `production/C-28/{NOTE.md,A-VOIR.md,reception.json}`. PRET signifie prêt à relire, ni clôture, ni validation visuelle, ni GO sur le réel.




