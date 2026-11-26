# C-17 — réception actuelle

**PRET TECHNIQUE instructions 1–4 / ATTENTE CED question 5 RGPD.** Voir **`A-VOIR-corrections.md`** pour les adresses, commandes et preuves courantes ; **`ATTENTE-ARBITRAGE-RGPD.md`** pour la question non arbitrée. Modèle cinq champs inchangé, aucun audit ajouté. Aucun GO réel.

Reçu actuel : `corrections-20261126/verification-successeur-V2.json`. B02 : 84 natifs + 51 HTTP, tous verts ; C17 nominal 49 + 8 + 8, corrections 10 + 17 + 10, tous verts. Pur 8/26, plugin 116/587, T01 1080/34335 zéro échec/erreur/saut ; C09 382/382, action 8793 pending pour subscription_id 101 exactement préservée. Bootstrap partagé non réécrit. C18/C21 non touchés.

---

# Historique avant corrections — ne pas utiliser pour le rendu actuel

**La suite de ce fichier conserve l'ancien état documentaire. Ses nombres, réserve C09 et commandes sont historiques ; les commandes à rejouer sont uniquement celles de `A-VOIR-corrections.md`.**

# C-17 — justificatifs solidaires à voir

**Prêt techniquement à relire, pas de validation visuelle ni de clôture.** Site uniquement fictif : `http://192.168.129.32:8085`. Identifiants C09 déjà hors dépôt, `C:\Users\Ced\.imagine-demo\identifiants.json`, clé `c09_accounts`. Aucun mot de passe dans les preuves.

## Les deux côtés

- **`p-sol-att`** : `http://192.168.129.32:8085/my-account/#imagine-compte-factures`. Dans « Mes factures et justificatifs », statut **En attente**, téléchargement du dépôt fictif protégé, catégorie **à préciser**, rappel de masquer le numéro de registre national, dépôt PDF/JPEG/PNG de **5 Mio maximum**. Télécharger ce document entièrement synthétique si un fichier de démonstration est nécessaire pour redéposer ; ne jamais employer un vrai justificatif. Le nouveau dépôt remplace physiquement l'ancien. Une URL ancienne ne sert plus rien.
- **`p-sol-ok`** : même adresse, **Validé jusqu’au 2027-01-10** à l'état de remise ; aucun justificatif conservé pour ce profil. La date de la fixture est recalculée à +45 jours lors d'un reset.
- **`e-abo`** : `http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-justificatifs`, sous **Imagine → Justificatifs solidaires**. Un seul personnage fictif P-SOL-ATT est en attente. Le téléchargement exige la session et le droit dédié. Saisir une date de fin pour valider, cocher la confirmation de suppression, puis **Valider** ou **Refuser**. Les deux décisions retirent réellement le fichier du disque ; le compte montre ensuite la décision. Aucun prix, commande, abonnement ou accès numérique ne change.
- **`e-admin`** : `http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-reglages`, formulaire C10 existant, bloc **Justificatifs du tarif solidaire** : catégories, une par ligne, défaut neutre unique **à préciser**, question pour Imagine. L'enregistrement passe par Settings API et le journal C10 ; aucune bibliothèque close n'a été modifiée.
- **Anonyme, `a-carte` et `e-redac`** : l'URL de lecture du justificatif de P-SOL-ATT répond **403**, même s'ils connaissent son URL complète. Ni compte client ni rôle rédaction ne confèrent la capacité `imagine_traiter_justificatifs`.

Déconnecter le personnage précédent avant de changer de compte. Le fichier est téléchargé, jamais prévisualisé dans une page. Les contrôles natifs du navigateur (sélecteur de fichier, calendrier) peuvent suivre sa langue propre ; les libellés applicatifs sont français.

## Rejeu parent — depuis la racine du dépôt

```powershell
# Préparation publique des dépendances, installation ciblée et tous les gates C17.
python wp/tests/demo/c17-verifier.py --prepare --deploy

# Captures Chromium en lecture seule des écrans natifs actuels.
python wp/tests/demo/c17-visuel.py

# Retour aux deux états documentaires C09 seulement ; pas de seed global.
python wp/outils/demo/c17.py --reset

# Contrôle exact des huit fichiers déployés, sans écriture sur le site.
python wp/outils/demo/c17.py
```

Le reset ciblé appelle **la même fonction `Imagine\Demo\C17\profils(true)` que le reset C09**, désormais incluse à sa fin. Le rejeu n'exécute pas le seed global C09, qui toucherait inutilement à des échéances historiques et aux autres profils. Le crochet de reset C16 et son marqueur sans-email restent intacts. Les commandes n'installent aucune licence, ne lancent aucun paiement ou email et ne visent aucun autre site.

## Preuves exactes du 26 novembre 2026

- `final.json` : **PRET_TECHNIQUE_C17_AVEC_RESERVE_HISTORIQUE_C09**, huit SHA-256 lus sur le site égaux aux sources ; état commercial, adhésions, rôles, options d'accès, découverte, PDFs C11 et action 8103 identiques à l'avant de la première installation C17.
- `http-final.json` : **49/49** contrôles réels, octets/hash servis au titulaire et au référent, refus anonymes/autre abonné/rédaction, nonces, contenu trompeur/exécutable/SVG/PDF actif et dépassement de taille, remplacement, anciennes URL et décisions périmées, validation/refus et suppression disque, état minimal conservé et reset.
- `reglages-final.json` : **8/8**, vrai POST C10, catégorie configurée utilisée au dépôt, liste vide et nonce invalide refusés, journal et restauration exacte des options. Les anciennes absences d'options découverte sont restaurées, pas remplacées par leurs valeurs par défaut matérialisées par le formulaire C10.
- `faults-final.json` : **8/8**, obstacle réel à l'emplacement du fichier : décision et remplacement refusés sans décision enregistrée ; octets restaurés. Deux sessions référent indépendantes : une décision **200**, l'autre **409**, une seule suppression ; reset relu.
- `unit-final.json` : **5 tests / 18 assertions** ; `unit-root-final.json` : **81 / 499**, conteneurs hors réseau retirés. `preparer-image-final.log` et `rejouer-t01-final.log` : **T01 canonique 1045 tests / 34247 assertions, zéro échec/erreur/saut**. PHPUnit est strict ; le style PSR12 a zéro erreur (`phpcs-final.log`, mode `-n`, les avertissements de longueur de ligne ne sont pas présentés comme une qualification sans avertissement).
- `site-final.json` : P-SOL-ATT utilisateur **26**, un seul fichier sous `/var/www/imagine-private-pdf/site-1/` ; P-SOL-OK utilisateur **27**, aucun fichier. `fixture-pdf-final.json` : PDF synthétique HTTP 200, cinq offsets xref vérifiés, hash `d3da00dbc0fb5e99491e93d735d9e0c66ffa8d8530b2e12d446d3bf415474845`.
- `visuel.json` et captures `compte-attente.png`, `compte-valide.png`, `file-referent.png`, `reglage-categories.png` : Chromium sur les vraies routes et sessions, aucun changement d'état métier. Les demandes d'avatars Gravatar ont été bloquées avant transport. Ce ne sont pas des maquettes validées.

**Réserve historique explicite : C09 n'est pas globalement vert.** `c09-native-final.json` : **381/382**, seul échec `A-PAPIER:action_native_planifiee_ou_absente_selon_statut`. `historique-action8103.json` confirme l'annulation du **25 novembre 2026 à 20:38:22 UTC**, antérieure à C16. Aucun replanifiage ni réécriture de cette action. Cette réserve ne bloque pas C17, selon la consigne du parent.

Les empreintes historiques C16/B04 restent conservées. `final.json/shared_digest_successor_not_historical_rewrite` documente les nouveaux hashes de `imagine-site.php` et `c09-seed.php` ; un ancien sceau qui les attend au hash précédent doit constater cette succession, pas être falsifié. Les cinq fichiers C16 non partagés sont relus identiques. Les reçus des premiers essais infructueux C17 restent présents ; les faux départs de harness (route anglaise native, guillemets natifs C10, nonce propre à chaque session) sont corrigés, pas dissimulés.

## Défauts prudents et limites

Catégorie unique « à préciser » ; 5 Mio ; PDF/JPEG/PNG ; date de fin valide et non passée, sans conséquence automatique. Décision et date UTC/opérateur conservés conformément au brief, en plus de la catégorie et de la fin. Aucune relance, transition tarifaire ou de droit n'a été inventée. Le contrôle de type et le refus de contenus actifs usuels ne sont pas une désinfection PDF universelle ni un antivirus. Une impossibilité de stockage/persistance ferme l'opération sans annoncer de succès ; si un fichier déjà supprimé n'a pas pu être remplacé/persisté, recharger puis redéposer.

Les choix de catégories et les conséquences du statut/échéance restent à confirmer par **Imagine**, pas par le designer. Les besoins visuels sont dans `besoins-designer.md`. **C18 non traité.**

## Standard et sources primaires consultées

Le formulaire, les sessions, capacités, nonces, `admin-post.php` et Settings API sont natifs. Le chemin média standard créerait une pièce jointe WordPress ; le seul stockage spécifique réemploie donc C11, hors public, sans média ni miniature.

- WordPress : `https://developer.wordpress.org/reference/functions/wp_handle_upload/` et `https://developer.wordpress.org/reference/functions/media_handle_upload/`.
- Settings API : `https://developer.wordpress.org/reference/functions/register_setting/`.
- Nonces, distincts du contrôle d'autorisation : `https://developer.wordpress.org/plugins/security/nonces/`.
