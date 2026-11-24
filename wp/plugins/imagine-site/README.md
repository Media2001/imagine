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

Les médias PDF gardent leurs IDs mais deviennent privés, sans `_wp_attached_file` ni métadonnées de chemin. GUID/URL native pointent vers le contrôleur, le REST média est fermé. Les cinq anciennes copies uploads et les cinq copies sources de construction sont retirées. Le seed B00 reçoit dorénavant ses sources PDF directement hors docroot et ne recrée pas ces fichiers publics ; seule sa branche médias PDF est adaptée.

Achat de numéro non raccordé : fermé, y compris le profil fictif P-NUMERO. Aucun droit inféré d'une commande ou d'un rôle. Le DNS externe reste hors ligne : le faux robot est testé par HTTP, les deux politiques robots par une entrée synthétique au contrat C06/C10, pas par un faux robot déclaré réel. Les deux politiques PDF antérieurs utilisent les droits natifs actifs. Aucune bibliothèque close ni écran C10 n'est modifié.

```bash
python C:/Users/Ced/imagine/wp/outils/demo/c11.py             # installer/rejouer, démo existante seulement
python C:/Users/Ced/imagine/wp/outils/demo/c11.py --check-only # recettes ciblées, sans reconstruction B00
python -m unittest discover -s C:/Users/Ced/imagine/wp/tests/demo -p 'test_*.py' -v
```

La commande de contrôle téléverse les recettes, teste les options natives avec restauration exacte et supprime ses canaris dans `finally`. Sources officielles, limites de la démo, URL à ouvrir et choix de stockage en cinq lignes : `production/C-11/A-VOIR.md`. Les preuves sont limitées à `production/C-11/{http,runtime,faults}.json`.

