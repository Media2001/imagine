# Relecture C-11 — Le PDF du numéro, protégé

Relecteur : Claude (indépendant). Date : 24 novembre 2026.
Brief : `briefs/C-11-pdf-du-numero.md`. Cahier : §3.9, §4.4 (et §3.1, §3.5, §4.2).
Cas visés : R-25 à R-31 pour la partie PDF. Codex non ouvert à ce stade.

Fichiers lus : `wp/plugins/imagine-site/PdfNumero.php`, `Paywall.php`, `imagine-site.php`,
`wp/plugins/imagine-pilotage/src/Acces/{Moteur,Reglages,AdministrationReglages}.php`,
`wp/themes/imagine/single-imagine_numero.php`, `wp/outils/demo/{b00-seed.php,c11-migrate.php}`,
`production/C-11/{A-VOIR.md,RAPPORT.md,PRET,faults.json,runtime.json}`.

## Rejeu

Commande autorisée, sans argument :

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1
```

Dernière ligne :

```
REJEU : 812 tests, 33434 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Conteneur jetable, réseau `none`, dépôt monté en lecture seule : conforme.
Le rejeu couvre `imagine-connecteur` (37) et `imagine-pilotage` (775). Il affiche
deux avertissements : `plugins/imagine-site` et `themes/imagine` sont des paquets
**sans tests PHPUnit**. Donc le code C-11 lui-même (`PdfNumero`, `Paywall::decisionPdf`,
gabarit) n'est **pas** exécuté par la commande autorisée. Voir §3.

## 1. Conformité

Le lot fait ce que demande le brief, sans surplus visible.

- PDF servi par une adresse du site (`/?imagine_pdf=ID`) qui passe par la décision
  C-06 avec le type de contenu `pdf` (§3.9, §4.2 « PDF » du modèle numéro).
  `PdfNumero::serve()` → `Paywall::decisionPdf()` → `Moteur::decider()`.
  Droit → octets ; pas de droit → `wp_safe_redirect` vers la page du numéro, jamais
  le fichier. Conforme au brief « droit → le fichier ; pas de droit → page du numéro ».
- Fichier hors des voies de contournement : octets déplacés hors docroot
  (`PdfNumero::directory()`), pièce jointe passée en `private`, `_wp_attached_file`
  et métadonnées de chemin supprimées (`protect()`), `wp_get_attachment_url` filtré
  vers le contrôleur, `rest_prepare_attachment` renvoie 404, page pièce jointe
  redirigée (`is_attachment()`). Anciennes copies publiques retirées (`unlink`).
  Couvre : adresse directe médias, pièce jointe, API REST médias.
- Réglages C-10 lus à chaque décision : `pdf_robot` (robots vérifiés) et
  `pdf_anterieur_abonnement` (PDF antérieurs à l'abonnement) via
  `AdministrationReglages::lire()` → `Reglages::depuisOptions()`. Conforme au brief
  « lus depuis l'écran de C-10 ». Aucun écran C-10 modifié.
- Acheteur d'un numéro : **laissé fermé** et déclaré (A-VOIR, RAPPORT). Aucun mapping
  natif commande/produit → numéro. `Paywall::rights()` ne produit jamais de droit
  `achat`. Conforme au brief « Si ce droit n'est pas encore branchable, dis-le et
  laisse fermé ». Conséquence : la partie PDF de **R-29 n'est pas satisfaite**, elle
  est reportée (voir §2).
- En-têtes : `privateHeaders()` pose `Cache-Control: private, no-store…`,
  `Vary: Cookie, Authorization, User-Agent`, retire ETag/Last-Modified, ajoute
  `X-Robots-Tag: noindex`. Conforme au brief « pas de mise en cache partagée ».
- Fermé par défaut : `decisionPdf`, `serve`, `path`, `directory` ferment sur toute
  exception ; fichier absent/corrompu/lien/traversée → redirection, jamais d'octets.
- Choix de stockage justifié en cinq lignes (A-VOIR) : **cumul** hors-docroot ET nom
  non devinable (128 bits, 0700/0600), **aucune** règle serveur, relecture C-06 à
  chaque GET, pas de X-Sendfile/X-Accel. Conforme à l'exigence de portabilité.

Interprétations signalées par Hermès et acceptables : type C-06 nommé `pdf`
(et non `pdf_numero`) ; décision robot « synthétique » à la frontière C-06 car le DNS
est volontairement coupé hors ligne. Aucune interprétation non signalée relevée.

## 2. Exactitude métier (déroulé à la main)

Déroulé sur le moteur `Moteur::evaluer()` et l'adaptateur `decisionPdf()`.

- **R-25 (abonné connecté)** : `rights()` renvoie un droit `abonnement`/`offert`/
  `groupe` ; branche `abonnement()` ; `etat=actif`, `debut ≤ instant < fin` →
  `AbonnementActif`, `complet=true` → octets servis. Correct. Réserve : si le numéro
  est sorti **avant** le début de l'abonnement et que `pdf_anterieur_abonnement=ferme`
  (défaut C-10), fermé (`PdfAnterieurFermeParReglage`). C'est la règle C-06/C-10, pas
  un écart C-11.
- **R-26 (anonyme)** : `userId=0`, droits `[]`, non robot → `Anonyme`/`Connexion`,
  `complet=false` → redirection 302 vers le numéro, aucun octet. Adresse directe
  ancienne : fichier supprimé → 404. Pièce jointe : redirigée. REST média : 404.
  Correct.
- **R-27 (robot vérifié / faux robot)** : faux robot (bon UA, IP quelconque) →
  non vérifié → extrait. Robot vérifié + `pdf_robot=extrait` (défaut) →
  `PdfRobotExtraitParReglage`, `complet=false` → pas d'octets ; `pdf_robot=complet` →
  `RobotVerifie`, octets. Correct et prudent (aligné décision 5 « sans téléchargement
  du PDF »). À confirmer : le défaut « extrait » pour les robots est bien voulu.
- **R-29 (acheteur d'un numéro)** : moteur prévu (branche `achat`, `NumeroAchete`)
  mais `rights()` n'émet jamais ce droit → fermé. Reporté, déclaré. À tracer pour un
  lot ultérieur (branchement commande → numéro).
- **R-30 (découverte)** : `rights()` n'émet aucun droit `decouverte` et `decisionPdf`
  passe `decouverte=null` ; un compte découverte seul n'a aucun droit → fermé.
  Conforme à la décision 5 (« sans téléchargement du PDF »). Correct.
- **R-31 (bénéficiaires et coopérateur)** : offert/groupe actifs → mêmes droits qu'un
  abonné (branche `abonnement()`) → octets. Coopérateur non abonné : `rights()`
  n'émet pas de droit `cooperateur` → fermé. Résultats `runtime.json` cohérents
  (`offert_natif_meme_droit`, `groupe_natif_meme_droit`, `P-COOP_ferme`). Correct.

Cas limites vérifiés dans le code et dans `runtime.json`/`faults.json` :
date éditoriale invalide → fermé ; `imagine_pdf` non entier positif → 404 ;
numéro non publié → 404 ; méthode autre que GET/HEAD → 405 ; HEAD → en-têtes sans
corps ; erreur native après un positif → refermé (`erreur_native_fermee_apres_positif`) ;
racine publique parent refusée (`racine_publique_parent_refusee`) ; canari supprimé ;
options restaurées exactement. Idempotence du transport (seed rejoué deux fois) : vert.

## 3. Tests

- Suite PHP autorisée : **verte** (812 tests), mais elle **ne couvre pas** le code C-11
  (avertissement T01 « plugins/imagine-site … sans tests PHPUnit »). Elle couvre la
  **logique de décision** dont dépend le PDF : type `pdf`, `pdfRobotComplet`,
  `pdfAnterieurAbonnement` sont testés dans `imagine-pilotage` (`Acces\AbonnementTest`,
  `ReglagesTest`, `OptionsReglagesTest`…), inclus dans le rejeu. La sémantique C-06
  héritée est donc éprouvée.
- La preuve d'étanchéité propre à C-11 (74 HTTP, 8 défauts, 24 natifs, 10 seed,
  32 unitaires — rapportés par Hermès) s'exécute via `c11.py` **contre la démo
  en ligne** (`192.168.129.32:8085`). Je ne l'ai **pas** rejouée : les droits du
  relecteur interdisent l'accès à un site/une base. Je n'ai donc pas pu re-exécuter
  la preuve demandée par le brief ; je l'ai vérifiée par lecture du code et par le
  rejeu du moteur sous-jacent. Les fichiers `http.json`/`runtime.json`/`faults.json`
  sont des résultats rapportés, non reproduits par la commande autorisée.
- Qualité : les cas listés dans `runtime.json`/`faults.json` vérifient des règles
  (fermé par défaut, antérieur/robot par réglage, racine parent refusée, restauration
  des options), pas seulement le cas nominal. Bon. Limite : ces tests ne tournent que
  contre la démo ; aucun test unitaire PHP du contrôleur `PdfNumero` (parsing de
  `imagine_pdf`, 405, HEAD, redirection) n'est rejouable hors staging.

## 4. Sécurité et données

- Pas de secret ni de donnée réelle : contenus `@example.org`, sources fictives,
  passerelles désactivées dans le seed.
- Fermé par défaut partout ; relecture des droits C-06 à chaque GET, pas de
  délégation statique (X-Sendfile/X-Accel), GET/HEAD seulement.
- Échappement des sorties : `esc_attr`/`esc_html`/`esc_url` dans `block()` et le
  gabarit ; `Content-Disposition: attachment` + `X-Content-Type-Options: nosniff`.
- Paywall PDF : aucune voie testée ne renvoie les octets à un non-ayant droit
  (adresse directe, pièce jointe, REST média, ancienne URL). Voie « plan de site »
  non reproductible ici : A-VOIR indique le sitemap natif désactivé sur la démo et
  les routes sollicitées sans PDF — **non vérifié** de mon côté.
- Dépendance au cache d'hébergeur : le contrôleur pose `DONOTCACHEPAGE` et des
  en-têtes privés ; la distinction connecté/anonyme du cache de pages (§4.4) reste
  une exigence d'hébergement que C-11 ne peut pas forcer. Portable, non revendiqué.

## 5. Doctrine

- Standard d'abord : WooCommerce/Memberships ne branchent pas la décision C-06 d'un
  numéro sur un téléchargement ; le mince adaptateur se justifie (A-VOIR, sources
  officielles citées). Pas de table de droits dupliquée. Conforme §4 doctrine.
- Conventions §5 : `declare(strict_types=1)`, espace de noms `Imagine\`, préfixe
  `imagine_`, textes passés par les fonctions de traduction. Conforme.
- Aucune modification d'extension tierce ni de bibliothèque close ; README du plugin
  à jour (section C-11). Conforme.

## Points

**Important**

1. Preuve d'étanchéité non rejouable par la commande autorisée. Le rejeu PHP (vert)
   n'exécute pas `imagine-site` ; la preuve C-11 (HTTP + runtime) ne tourne que
   contre la démo via `c11.py`, hors de mes droits. Conséquence : conformité établie
   par lecture + moteur vert, mais la preuve exigée par le brief n'a pas été
   reproduite indépendamment. (Grille §3 ; doctrine « tests d'abord », « rejouable ».)
   Proposition : ajouter des tests PHPUnit du contrôleur `PdfNumero`
   (`serve()` : 404/405/HEAD/redirection, `path()`/`directory()` fail-closed,
   `block()`) au paquet `plugins/imagine-site`, pour qu'ils entrent dans `rejouer.ps1`.

**Mineur**

2. `wp/themes/imagine/single-imagine_numero.php:26-28` : le lien « Ouvrir le PDF
   factice du numéro » est affiché pour **tout** visiteur dès que le numéro a un PDF,
   même quand `block()` affiche le bloc connexion/abonnement (donc sans droit).
   Pas de fuite d'octets (`serve()` recontrôle et redirige), mais l'affichage montre
   à la fois « connectez-vous » et un lien de téléchargement. Proposition : n'afficher
   le lien que lorsque `decisionPdf()['complet']` est vrai (ou intégrer le lien dans
   `block()` côté ayant droit).

3. `Paywall::decisionPdf()` (Paywall.php:106) crée un `DateTimeImmutable` neuf au lieu
   de réutiliser `self::$requestInstant`. Un article et un PDF de la même requête
   peuvent différer de moins d'une seconde. Aucun impact fonctionnel (précision
   seconde, UTC). À uniformiser si l'occasion se présente.

4. Voie « plan de site » (§3.9) non vérifiable ici : repose sur l'affirmation d'A-VOIR
   (sitemap natif désactivé sur la démo). À confirmer sur l'hébergement cible avec
   Rank Math actif.

## À arbitrer par Ced

- Le défaut C-10 « robot vérifié → extrait (pas de PDF complet) » est-il bien la
  politique voulue pour le PDF du numéro (aligné décision 5) ? Oui / Non.
- L'acheteur d'un numéro (droit PDF de R-29) reste fermé faute de mapping
  commande → numéro : faut-il ouvrir un lot de branchement dédié ? Oui / Non.

## Verdict

**Conforme** — avec un point **important** (3·1 : preuve non rejouable par la commande
autorisée, à couvrir par des tests PHPUnit du contrôleur) et trois points **mineurs**
(lien PDF toujours affiché ; instant dédoublé ; plan de site non vérifié).
Le code répond au brief et aux cas R-25 à R-31 pour ce qui est branchable ; R-29 (PDF)
est reporté et déclaré. Ce verdict n'est pas un GO.

Fusion non faite : `corrections/C-11.md` sera écrit après lecture de `codex.md`
(non ouvert à ce stade), sur demande.
