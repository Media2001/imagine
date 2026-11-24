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

`--check-only` ne réinstalle pas le plugin et ne reconstruit pas B00 ; il téléverse les recettes ciblées, rejoue deux fois les seules fonctions médias PDF du seed, teste les réglages C10 natifs puis les défauts et l'étanchéité HTTP. Les canaris C11 sont supprimés dans `finally` ; les options sont restaurées à leur valeur ou absence exacte. Pour réinstaller/régénérer les cinq PDF fictifs : même commande sans `--check-only`.

Tests : `wp/tests/demo/c11-verifier.py`, `c11-runtime.php`, `c11-seed-runtime.php`, `c11-faults.py`, `test_c11_seed.py`. Résultats courants : `http.json`, `runtime.json`, `faults.json` ici ; pas de captures ni d'archives de preuves.

## Limites explicites

- Le contrat fermé C06 appelle le type de contenu `pdf` (le « PDF du numéro » du brief), non un type inventé `pdf_numero`.
- Acheteur à l'unité : **fermé**. Il n'existe pas encore de mapping natif produit/commande → numéro validé dans l'adaptateur. Le profil C09 `P-NUMERO` est éprouvé fermé ; aucun droit déduit d'une commande, d'un rôle ou d'un cookie.
- Robots : contrôle HTTP du faux Googlebot fermé ; les deux valeurs C10 sont testées avec une décision robot **synthétique** à la frontière C06. Le DNS extérieur est volontairement indisponible sur la démo : aucun vrai robot Internet déclaré vérifié.
- PDF antérieurs : les deux valeurs C10 sont testées avec les vrais droits Memberships/Subscriptions du compte actif et un numéro-canari supprimé ensuite. Offert/groupe réutilisent les mêmes objets natifs via le mapping de plans, pas des faux droits stockés ailleurs.
- Les options sont restaurées exactement ; le journal natif C10 conserve normalement les traces fictives des changements de réglages des recettes. Aucun effacement du journal n'est effectué.
- Le sitemap natif est désactivé sur cette démo non indexable ; les routes de sitemap réelles sont sollicitées et ne publient aucun PDF. Aucun cache hébergeur ni déploiement réel n'est revendiqué.

## Standard consulté

- WordPress `wp_get_attachment_url` : URL native à partir de `_wp_attached_file`, repli GUID et filtre final. Un statut privé de pièce jointe ne protège pas les octets statiques : ils sont déplacés physiquement.
  https://developer.wordpress.org/reference/functions/wp_get_attachment_url/
- WordPress `template_redirect` : point de contrôle avant chargement du gabarit et redirection vers la page canonique en cas de refus.
  https://developer.wordpress.org/reference/hooks/template_redirect/
- REST médias : `source_url`, GUID et `media_details` doivent rester sans chemin physique. Média privé et garde `rest_prepare_attachment` ; le lecteur reçoit seulement l'endpoint protégé.
  https://developer.wordpress.org/rest-api/reference/media/
- WooCommerce : téléchargement PHP standard, mais stockage médias public et dépendance serveur pour les URL directes ; le téléchargement natif de produit ne branche pas la décision C06 d'un numéro abonné. D'où le mince adaptateur, sans nouvelle table de droits ni serveur spécifique.
  https://woocommerce.com/document/digital-downloadable-product-handling/
