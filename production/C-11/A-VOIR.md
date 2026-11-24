# C-11 — À ouvrir et à rejouer

- Site fictif exclusivement : http://192.168.129.32:8085 ; sonde initiale : `slug=imagine-test-demo`, `running`, environnement `local`, garde B00 conforme.
- Ouvrir http://192.168.129.32:8085/?imagine_pdf=39 en navigation anonyme : retour au numéro et bloc connexion, jamais le fichier.
- Même adresse après connexion avec le compte fictif `actif` de `C:\Users\Ced\.imagine-demo\c08-identifiants.json` : téléchargement du PDF témoin exact. Aucun secret n'est reproduit ici.
- Ancienne adresse : http://192.168.129.32:8085/wp-content/uploads/imagine-demo/demo-2026-t4.pdf ; refus même connecté. Les cinq copies sources publiques B00 ont aussi été retirées.

## Choix de stockage — cinq lignes

1. Les octets sont dans `/var/www/imagine-private-pdf/site-1/`, en dehors du document root `/var/www/html`, et non dans uploads.
2. Noms aléatoires 128 bits, répertoire 0700, fichiers 0600 ; aucune URL physique publiée, même pour l'abonné.
3. Le téléchargement PHP réévalue le moteur C06 à chaque GET/HEAD et ne délègue pas à X-Sendfile, X-Accel ou une redirection statique.
4. Aucune règle Apache/nginx/.htaccess ajoutée : ancienne URL, source, nom privé connu, listes et API sont éprouvés par HTTP sans règle de fermeture spécifique.
5. Hors démo, créer/sauvegarder ce répertoire de données privé ; `IMAGINE_PDF_PRIVATE_DIR` peut désigner un autre chemin hors racine publique. Inaccessible/ambigu/absent signifie fermé, y compris en installation WordPress en sous-dossier.

## Rejeu parent

Depuis le dépôt (bash Windows) :

```bash
python C:/Users/Ced/imagine/wp/outils/demo/c11.py --check-only
```

La commande inclut les tests unitaires locaux avec les six wheels universelles déjà gelées dans `production/B-01/validation` chargées en lecture seule ; aucune installation ni récupération réseau. Un `python -m unittest` nu peut échouer si `html5lib` n'est pas installé dans le Python appelant.

`--check-only` ne réinstalle pas le plugin et ne reconstruit pas B00 ; il exécute d'abord PHPUnit C11 hors ligne, puis téléverse les recettes ciblées. Le test du seed remet le seul média fictif T4 dans son état public (deux copies et aucune référence privée), appelle la vraie branche PDF du seed, puis la rejoue : suppression des deux copies relue, mêmes IDs/chemin/octets privés au second passage. Un `finally` restaure le nom privé initial et retire le blob créé pour le test. Les options C10 sont restaurées exactement, les canaris supprimés. Pour réinstaller les trois fichiers C11 et les cinq PDF fictifs : même commande sans `--check-only` ; le bootstrap partagé C12/C13 n'est plus téléversé.

Les cinq fichiers partagés `imagine-site.php`, `Decouverte.php`, `DecouverteReglages.php`, `EnvoiNatif.php`, `ListeEnvoiAdmin.php` sont comparés octet pour octet avant/après. Le déploiement refuse un `Paywall.php` distant qui diffère autrement que par la correction C11 de l'instant. Les états découverte par compte, réglages et options d'envoi C13 sont comparés en mémoire, sans reçu général ni reset des profils. Cela ne remplace pas les recettes métier C12/C13 du parent ; C13 reste BLOQUÉ, non traité ici.

### PHPUnit du contrôleur et limite du runner partagé

```bash
PYTHONDONTWRITEBYTECODE=1 python C:/Users/Ced/imagine/wp/outils/demo/c11-unit.py
powershell.exe -NoProfile -File C:/Users/Ced/imagine/wp/tests/rejouer.ps1
```

Le premier exécute réellement `plugins/imagine-site/tests/PdfNumeroTest.php` avec `phpunit.c11.xml`, PHP 8.2/PHPUnit 11.5 déjà préparés dans l'image locale T01. Nouveau conteneur sans réseau, dépôt en lecture seule, rootfs RO, utilisateur non privilégié ; aucune installation ni modification d'image. Le processus enfant exécute le vrai `PdfNumero`, ses sorties/exit, et de vrais fichiers temporaires ; les API WP et la décision Paywall sont doublées. Les vrais droits natifs restent éprouvés séparément par WP-CLI et HTTP.

**Limite explicite de l'instruction 3** : le runner partagé ne découvre que `phpunit.xml`/`.dist`, exige `bootstrap=vendor/autoload.php`, des manifests Composer et un cache `/opt/t01/imagine-site` préparé dans son image. Ce cache n'existe pas dans l'image actuelle. La configuration locale C11 et son rejeu obligatoire par `c11.py` sont le repli autorisé ; les tests C11 ne sont donc **pas comptés dans les 812 tests T01**. Aucun fichier de runner, `scripts/`, `relecteurs/`, bibliothèque close ou image de l'outil n'a été modifié pour contourner cette limite. L'intégration automatique T01 nécessitera sa préparation autorisée avec le nouveau paquet ; elle n'est pas revendiquée ici.

Tests : `wp/plugins/imagine-site/tests/PdfNumeroTest.php`, `pdf-fixture.php`, `phpunit.c11.xml` ; `wp/tests/demo/c11-verifier.py`, `c11-runtime.php`, `c11-seed-runtime.php`, `c11-faults.py`, `test_c11_seed.py`. Résultats courants : `http.json`, `runtime.json`, `faults.json` ici ; pas de captures ni d'archives de preuves.

## Limites explicites

- Le contrat fermé C06 appelle le type de contenu `pdf` (le « PDF du numéro » du brief), non un type inventé `pdf_numero`.
- Acheteur à l'unité : **fermé**. Il n'existe pas encore de mapping natif produit/commande → numéro validé dans l'adaptateur. Le profil C09 `P-NUMERO` est éprouvé fermé ; aucun droit déduit d'une commande, d'un rôle ou d'un cookie.
- Robots : contrôle HTTP du faux Googlebot fermé ; les deux valeurs C10 sont testées avec une décision robot **synthétique** à la frontière C06. Le DNS extérieur est volontairement indisponible sur la démo : aucun vrai robot Internet déclaré vérifié.
- PDF antérieurs : les deux valeurs C10 sont testées avec les vrais droits Memberships/Subscriptions du compte actif et un numéro-canari supprimé ensuite. Offert/groupe réutilisent les mêmes objets natifs via le mapping de plans, pas des faux droits stockés ailleurs.
- Les options sont restaurées exactement ; le journal natif C10 conserve normalement les traces fictives des changements de réglages des recettes. Aucun effacement du journal n'est effectué.
- Le sitemap natif est désactivé sur cette démo non indexable ; les routes de sitemap réelles sont sollicitées et ne publient aucun PDF. Un sitemap actif (ex. extension cible) reste à éprouver sur cet hébergement, sans revendiquer ici sa validation. Aucun cache hébergeur ni déploiement réel n'est revendiqué.
- Comparaison de chemins centralisée : `realpath` avant comparaison, séparateurs normalisés, frontière `/`, casse sensible Unix / insensible Windows. La matrice PHPUnit couvre enfant/égalité/frère et volumes Windows ainsi que la source publique ; les opérations fichiers réelles sont éprouvées sous Linux. Aucun PHP Windows/IIS n'est installé ici : pas de revendication de recette IIS native. Aucun choix Linux-exclusif ni refus Windows arbitraire.
- Politique C10 `pdf_robot=extrait` prudente conservée ; aucun arbitrage réel tranché. Achat à l'unité explicitement laissé fermé comme permis par le brief.

## Standard consulté

- PHP `realpath` : développe liens et `..`, mais ne garantit pas la normalisation de casse sur un système insensible à la casse ; le contrôle normalise donc après résolution.
  https://www.php.net/manual/en/function.realpath.php
- PHP `clearstatcache` : la relecture de disparition n'utilise pas un état `stat` antérieur à la suppression.
  https://www.php.net/manual/en/function.clearstatcache.php
- PHPUnit 11.5, organisation des suites : suffixe `Test.php`, composition XML locale et sélection explicite de configuration.
  https://docs.phpunit.de/en/11.5/organizing-tests.html
- WordPress `wp_get_attachment_url` : URL native à partir de `_wp_attached_file`, repli GUID et filtre final. Un statut privé de pièce jointe ne protège pas les octets statiques : ils sont déplacés physiquement.
  https://developer.wordpress.org/reference/functions/wp_get_attachment_url/
- WordPress `template_redirect` : point de contrôle avant chargement du gabarit et redirection vers la page canonique en cas de refus.
  https://developer.wordpress.org/reference/hooks/template_redirect/
- REST médias : `source_url`, GUID et `media_details` doivent rester sans chemin physique. Média privé et garde `rest_prepare_attachment` ; le lecteur reçoit seulement l'endpoint protégé.
  https://developer.wordpress.org/rest-api/reference/media/
- WooCommerce : téléchargement PHP standard, mais stockage médias public et dépendance serveur pour les URL directes ; le téléchargement natif de produit ne branche pas la décision C06 d'un numéro abonné. D'où le mince adaptateur, sans nouvelle table de droits ni serveur spécifique.
  https://woocommerce.com/document/digital-downloadable-product-handling/
