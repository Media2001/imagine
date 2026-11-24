# Imagine — site (B-00, modèle provisoire)

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

Achat de numéro non raccordé : fermé, y compris le profil fictif P-NUMERO. Aucun droit inféré d'une commande ou d'un rôle. Le DNS externe reste hors ligne : le faux robot est testé par HTTP, les deux politiques robots par une entrée synthétique au contrat C06/C10, pas par un faux robot déclaré réel. Les deux politiques PDF antérieurs utilisent les droits natifs actifs. Aucune bibliothèque close ni écran C10 n'est modifié.

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

Les paramètres sont figés à l’ouverture : les augmenter ne recrédite pas les comptes. Le périmètre courant peut retirer un numéro mais ne peut élargir le périmètre initial d’un compte. Fermer l’ouverture suspend tous les droits découverte. En mode articles, relire un ID déjà ouvert ne consomme pas de crédit supplémentaire tant que le quota n’est pas épuisé. Après le dernier crédit, **toute nouvelle requête découverte, même de relecture, est fermée**, conformément au moteur C06 (motif/bloc `decouverte_epuisee`) ; aucun nombre consommé n’est soustrait pour prolonger le droit. En mode durée, la fin UTC est exclue, y compris pour la relecture.

Seul le GET final d’un article publié et admissible consomme, après les redirections canoniques. REST connecté avec nonce natif, flux, recherche, aperçu, oEmbed/embed, HEAD/POST, préchargement et agents robots reconnaissables n’ouvrent ni ne consomment la découverte ; les autres droits natifs restent inchangés. Le réglage d’accès C10 est désormais réellement lu par le raccord C10/C11 (la réserve historique du §C08 ci-dessus est dépassée).

`DecouverteReglages.php` étend **la section Accès de l’écran C10 existant**, via les hooks de menu et l’enveloppement de son callback de rendu : C10 ne propose pas de hook interne ni `do_settings_sections`. Son formulaire, sa capacité, son nonce et son traitement `options.php` sont conservés. Les champs portent « À confirmer par Imagine » ; les changements rejoignent le journal visible C10, avec restauration en cas d’échec du journal. Ce raccord dépend du titre/tableau de cette section et doit être retesté si son balisage change ; aucun fichier de `imagine-pilotage` n’est modifié.

```bash
python C:/Users/Ced/imagine/wp/outils/demo/c12.py
python C:/Users/Ced/imagine/wp/outils/demo/c12.py --check-only
```

Cible unique fictive : installation ciblée, puis rejeu PHP/HTTP réel et non-régression C11, sans constructeur global ni reset d’autres profils. Les tests restaurent exactement les options et l’état V-DEC initial. Le script C09 sait initialiser/réinitialiser ses deux profils découverte ; le runner C12, lui, ne renouvelle pas un profil déjà consommé. Résultats sans corps HTML, cookies, secrets, captures ni reçus d’empreintes : `production/C-12/resultats.json`. Parcours et sources officielles : `production/C-12/A-VOIR.md`.

Limites : unicité **par compte**, pas d’identification de personne à travers plusieurs adresses ; refus des emails jetables et vraie confirmation email à raccorder au futur parcours d’inscription. Un robot utilisant une session valide et un UA humain n’est pas distinguable d’un lecteur. Aucun robot Internet n’a été vérifié hors ligne. PDF et achats de numéro n’acquièrent aucun droit découverte ; aucun accès réel ni email sortant.

## C-13 — Liste d’envoi native (relecture avec réserve C09)

`EnvoiNatif.php` lit les souscriptions natives et leurs adresses de livraison par CRUD. Les relevés observés sont append-only, non autoloadés (`imagine_envoi_releve_ID_UUID`) et ne sont jamais antidatés. Les sauvegardes natives ajoutent une observation si les champs postaux changent. C01 fournit les numéros théoriques ; C07 seul établit les lignes, le gel, les anomalies et l'éligibilité. Un historique antérieur manquant ferme l'export. Une projection future est explicitement provisoire.

`ListeEnvoiAdmin.php` ajoute **Imagine → Liste d’envoi**, sous la capacité C09 existante `imagine_exporter_liste_envoi`, ou `manage_options` pour les administrateurs. Aucun rôle ni droit sensible n'est ajouté. L'exception au blocage administratif Woo est limitée à cet écran et à sa capacité. L'export authentifié `admin-post.php` exige POST et un nonce lié au numéro ; C07/C04 protègent le CSV et C10 fournit les colonnes. Aucun fichier export public. L'audit `imagine_envoi_export_journal_UUID` est écrit/relu avant la réponse ; s'il échoue, l'export ferme. Cinquante événements affichés, sans purge.

```bash
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c13.py --deploy
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c13.py
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c13.py --require-complete
```

Cible unique `imagine-test-demo`, aucun reset global ou C09/C10/C11/C12. Deux témoins supplémentaires C13, avec une grâce explicitement fictive et aucun paiement, permettent un vrai CSV de deux destinataires BE/FR, sans email dans le format postal. **Ils ne remplacent pas l'acceptation positive des profils C09** : leurs douze souscriptions sont sans paiement validé, A-SANSMAIL reste exclu pour ce motif ; offerts/groupés ne disposent pas du lien natif nécessaire. Aucun statut actif n'est converti en règlement et aucun adaptateur offert/Teams complet n'est revendiqué. Le mode strict retourne 2 tant que ces gates restent bloquées ; le mode technique peut être vert. Voir `production/C-13/{A-VOIR.md,COMMANDES.md,resultats.json}`. PRET signifie ici relecture avec réserves, pas recette complète ni validation visuelle.

