# C-28 — réception corrigée après fusion du 27 novembre 2026, 12 h 40

## État courant — remplace la note historique ci-dessous

**C28-01 corrigé** : gardes serveur d'achetabilité Woo, ajout direct et revalidation du panier au checkout, produit relu ; dernier garde avant première persistance du paiement. Un numéro dépublié bloque tout le pack. Prix global fictif inchangé, pas de prix recalculé.

**C28-02 corrigé** : état persisté relu avant sauvegarde ; capture éphémère liée au seul objet (`WeakMap`) uniquement pour la première transition non payée vers payée et datée, consommée après persistance et avant ligne. Commande déjà payée ou déjà datée : jamais de reconstruction depuis le produit vivant. Instantané absent/non fiable : fermeture, puis signalement persistant `imagine_pack_anomalie` visible sur la ligne lors de sa sauvegarde. Date et produit incohérents refusés ; la suppression native du produit (ID de ligne ramené à zéro) conserve le bon instantané acquis. Aucun moteur de réparation automatique.

**Déliement technique symétrique appliqué** : un numéro C14 valide retire la méta pack, même avec le seul champ C14 soumis. Règles `AchatNumero`, accès et remboursements C14 inchangés, aucun réglage/prix nouveau. Produit simple à prix global et blocage du pack entier sont les défauts prudents de la fusion ; les confirmations métier d'Imagine n'arrêtent pas le lot.

### Preuves actuelles

- `correction-unitaire-final.log` : **3 tests / 54 assertions** ; couche `candidat`/`payer`/`instantanes` et hooks panier sur doubles persistés, intégrée au paquet PHPUnit rejouable.
- `correction-canaris-final.json` : **5 mutants de source rouges puis GREEN**, copie jetable hors réseau : ajout direct, checkout, reconstruction tardive, commande déjà payée sans date fiable, déliement C14. Aucun mutant hors ligne appliqué au site.
- `correction-natif-final.json` : **25/25** contrôles ; `correction-fenetre-finale.json` : **18/18**, dont panier réel avant dépublication et vraie panne de sauvegarde de ligne **APRÈS paiement persisté**, objet rechargé, pack édité, sauvegarde tardive fermée/signalée, deux sens du déliement.
- `correction-c14-final.json` : **45/45** régressions du complément C14 existant inchangé.
- `correction-recette-finale.json` : **200/200** navigateur/HTTP ; profils, commandes, sessions, réglage et actions restaurés puis relus. **32 témoins C26**, **7 sorties non vides**, **32 injections de réponse détectées**, **1 mutation de source détectée/restaurée** ; matrice inchangée.
- `correction-preservation-finale.json` : état avant fixture retrouvé hors seul produit déclaré ; aucun achat C28 permanent ni droit C09 laissé ouvert.
- `correction-lint-final.json` : **19 fichiers PHP**, syntaxe valide.
- `correction-image-finale.*` : `preparer-image.ps1` rejoué après ajout des tests, sortie **0**, image vérifiée.
- `correction-regression-finale.*` : **1 190 tests / 36 548 assertions**, 0 échec/erreur/ignoré, **PASS** ; **22 outils / 720 contrôles**, 0 échec.

`reception-corrections.json` est le sceau courant ; `reception.json` et `PRET-avant-corrections-12h40-historique.txt` sont historiques. La fixture reste produit 3592, liste [11,18,25], 3.28 EUR fictifs ; aucun compte créé, article/PDF existant modifié ni paiement financier. Installation des seuls fichiers C28/C14 modifiés, sources relues.

### Limites et relectures

- Relectures initiales : Claude avait joué `rejouer.ps1` (1 189 tests / 36 512 assertions). Codex n'avait pas pu lancer PHPUnit (`Wsl/Service/E_ACCESSDENIED`) et avait joué seulement le vérificateur (27 contrôles). **Aucun des deux n'avait rejoué les recettes `--live`/mutantes**. Les exécutions corrigées ci-dessus sont celles de livraison, pas un rejeu indépendant des relecteurs.
- Le témoin de panne est une exception réelle lors de la sauvegarde de ligne, pas un arrêt brutal du conteneur. Woo 11.2.2 l'absorbe dans `save()` : le témoin atteste son déclenchement puis relit séparément paiement persisté et ligne absente. Premier essai rouge conservé (attente erronée d'une exception propagée), état métier restauré. Autre rouge conservé : ID produit remis à zéro à la suppression, garde ajusté sans retirer le test puis vert.
- Paiement/remboursement **fictifs natifs**, sans passerelle ni checkout bancaire. Pas de garantie nouvelle de concurrence d'éditions simultanées, réparation automatique ou identité intégrale de base : caches/transients, logs/analytics et compteurs peuvent varier ; exclusions historiques des caches de rapports WCS conservées. Comparaison métier et restitutions ciblées seulement.
- Paquets hors lot : **A-31 hors rejeu, journaux absents**, **A-32 / A32_PACKAGE_DRIFT** ; **11 paquets vérifiés, 1 échec**. Aucun code/reçu/sceau A31/A32 corrigé. Le PASS porte sur tests/outils, pas sur tous les paquets.
- **B-11 reste BLOQUÉ sans PRET**, aucun code/réglage/preuve B11 touché ; bootstrap inchangé. Aucun autre site, file, verrou ou bibliothèque close modifié. Validation visuelle de Ced attendue, aucun GO sur le réel.

---

## HISTORIQUE — réception initiale antérieure à la fusion, périmée

Les nombres, empreintes et limites des sections suivantes décrivent uniquement l'état initial ; ils ne valent pas preuve courante.

# C-28 — note de réception initiale

## Livré

Un produit simple WooCommerce à prix global et liste éditoriale de numéros. Le choix face au produit groupé natif et à Product Bundles est documenté en cinq lignes dans le README de l'extension, sur la documentation officielle effectivement consultée :
- https://woocommerce.com/document/managing-products/#grouped-products
- https://woocommerce.com/document/bundles/bundles-configuration/#pricing

La classe native `WC_Product_Grouped` installée a aussi été relue : le conteneur ne s'achète pas lui-même, son prix vient des enfants. Aucune extension commerciale ajoutée ou activée. Le produit simple garde prix, panier et commande natifs ; il n'ajoute ni moteur de vente ni produits enfants artificiels.

La question métier de modification passée du pack suit exactement `docs/decisions.md`, ligne C28 : les numéros au paiement, ni plus ni moins, **pas de réglage nouveau**. Le remboursement conserve l'unique réglage C14 existant. Aucune règle d'accès n'est copiée.

## Raccord et stockage

- `PacksRegles.php` : validation pure d'IDs et de l'enveloppe payée.
- `PacksThematiques.php` : champ multiple dans les données générales du produit simple ; nonce/capacité natifs Woo et contrôle `edit_post`. Une liste invalide ne remplace pas l'ancienne. Aucun texte libre nouveau.
- `imagine_pack_numeros` : IDs de numéros, jamais les articles/PDF. Une liste valide de pack enlève le mapping produit C14 à l'unité.
- `_imagine_pack_candidat` : à la création de la ligne, éligibilité seulement. Une ancienne ligne sans marque n'est pas reprise.
- `_imagine_pack_paye` : tableau `numeros`, `paye_le` (timestamp de `date_paid`), `produit`. Écrit une seule fois **après persistance du paiement**, liste du produit relue, pas liste du panier. Un paiement qui échoue avant sa persistance ne fige rien. Une liste devenue vide est elle-même figée : pas de rétro-octroi lors d'une réaffectation ultérieure.
- `AchatsNumeros.php` : seul changement du raccord C14, un filtre d'expansion `imagine_achat_instantanes` avant l'appel existant à `AchatNumero::droit`. Même propriétaire, statut, date, quantité, publication, remboursements et pagination. La ligne commerciale reste unique. Pas de table de droits, nouveau type de droit ou accès anonyme.
- `AchatNumero`, `Paywall`, `PdfNumero`, `MonCompte` et les bibliothèques closes sont inchangés. La décision C06 garde le motif `numero_achete` ; B02 et C11 voient donc naturellement les numéros du pack.
- `single-product.php` : classes du squelette B01, métadonnées publiques B04 (couverture, titre, date), prix fictif et bouton/panier natifs. Aucun corps réservé lu pour fabriquer la fiche, aucun CSS/JS nouveau.

Le bouchon **de lecture** `tests/b04-adapter-fixture.php` reçoit seulement `apply_filters` retournant la valeur initiale lorsqu'aucun filtre n'est enregistré, conforme à WordPress. Le premier rejeu général était rouge sur l'absence de cette API ; aucune assertion B04 n'a été retirée ni affaiblie. Aucun bouchon d'écriture nouveau.

## Preuves finales réellement jouées

| Preuve | Résultat |
|---|---|
| `unitaire-final.log` | PHPUnit **2 tests, 18 assertions**, vert ; intégrés à la découverte du paquet existant |
| `natif-final.json` | **25/25 contrôles** WordPress/Woo HPOS, rollback et état métier identique |
| `c14-regressions-finales.json` | **45/45 contrôles** du complément C14 existant, deux modes de remboursement, état métier identique |
| `recette-finale.json` | **200/200 contrôles** navigateur/HTTP natifs, aucun échec, restauration relue |
| `preservation-finale.json` | État avant création de fixture retrouvé en retirant **seulement le produit déclaré 3592** de la comparaison : profils, commandes, souscriptions, adhésions, options, PDFs et actions métier conservés |
| `lint-final.json` | **16 fichiers PHP** analysés par `php -l`, sans erreur |
| `preparation-image.*` | Commande parent inchangée, sortie **0**, image vérifiée `sha256:b796e678063ce6019fc4938c26dc440b1708296dc9593990142764c0c0942166` |
| `regression-finale.*` | **1 189 tests, 36 512 assertions**, 0 échec/erreur/ignoré, **PASS** ; **22 outils / 584 contrôles**, tous verts |

Le paiement est vraiment parcouru par les objets Woo et `payment_complete()`, mais **synthétique, méthode/transaction vides**, sans passerelle. La recette traverse le vrai formulaire d'administration du produit et son nonce, le vrai bouton d'ajout au panier, les vrais GET d'articles et d'octets PDF, et le vrai compte Woo lu à son URL native. Profils : V-INSCRIT acheteur d'essai, V-DEC-FIN tiers, anonyme. Avant : rien ; après : trois articles et trois PDF pour le seul acheteur ; ajout 32 : aucun droit neuf ; retrait 11 : droit conservé ; remboursement par commande : fermeture ; par ligne non ventilée : conservation ; remboursement de la ligne pack : fermeture. Le natif ajoute le remboursement total des deux modes, le cas déjà possédé sans remise, la disparition du produit, le refus de rétro-octroi historique et l'instantané au paiement plutôt qu'au panier.

Étanchéité : les **32 témoins réservés C26**, inventaire inchangé, sont cherchés par son détecteur existant dans **7 sorties non vides** : fiche HTML, Store API REST directe et `rest_route`, flux produits, recherche, embed et oEmbed. La redirection native de recherche est inspectée avant sa destination. **32 injections dans la réponse brute** détectées ; elles ne sont pas présentées comme des mutations de source. **Une mutation réelle du raccord C28** remplaçant l'instantané par la liste vivante produit `[18,25,32]` au lieu de `[11,18,25]` : détectée, source restaurée et empreinte relue. Matrice C26/C23 et leurs paquets inchangés.

Réseau : **40 tentatives HTTP et 4 tentatives email** du parcours natif/ambiance, toutes observées bloquées par B00 avant transport. Pas d'attribution précise à chaque composant dans cet observateur ; ce n'est donc pas un « zéro tentative ». **6 requêtes Gravatar d'administration** interceptées et bloquées côté navigateur ; aucun tiers public chargé. Le détecteur a ses témoins positifs mail/HTTP bloqués. Aucun mail, paiement ou remboursement financier réel.

## Fixture laissée et restauration

Produit **3592**, slug `c28-pack-thematique-fictif`, **3.28 EUR fictifs**, liste `[11,18,25]`. Numéro témoin ajouté puis retiré : 32. Articles existants utilisés : 14, 21, 28, 35 ; aucun corps existant modifié. Option déclarative `imagine_c28_fixture`. **Aucune commande d'achat C28 permanente**, aucun compte créé, aucun droit C09 laissé ouvert.

Le mode Coming Soon existant empêchait la fiche publique. `wp/outils/demo/c28-demo.php`, copié comme `mu-plugins/imagine-c28-demo.php`, utilise le filtre natif Woo uniquement pour **cette fiche fictive** sur l'unique site autorisé. Option Coming Soon, autre boutique et passerelles inchangées. Ce fichier n'est pas une règle du plugin de production.

Préimages durables privées avant sessions et mutations, hors dépôt ; aucun cookie, nonce, mot de passe ou HTML authentifié dans les preuves publiques. Le produit, les métadonnées des trois utilisateurs touchés, leurs sessions WP/Woo, le réglage C14 et les commandes éphémères reviennent à leur préimage et sont relus. Les seules tâches natives créées par la recette pour son produit/écran sont retirées par leurs IDs nouveaux et signatures précises ; aucune action C09 n'est reconstruite. L'action produit créée initialement par le seed est également retirée : l'empreinte des actions métier **avant fixture** est retrouvée.

Les essais rouges sont conservés. Deux récupérations explicites (`recuperation-01.json`, `recuperation-05.json`) ont retiré exactement des tâches d'édition propres à C28 puis une ligne résiduelle de remboursement, et prouvé le retour à leur préimage. Un essai supplémentaire du vieux banc C14 avec suppression de son utilisateur a montré qu'un rollback extérieur seul ne suffisait pas ; ses résidus propres ont été retirés et l'état intégral de comparaison retrouvé (`c14-regression-recuperation.json`). **La preuve de régression C14 retenue est le complément de 45 contrôles**, pas une revendication de restauration automatique du vieux banc complet. Aucune source de ces bancs clos n'est modifiée.

## Limites exactes

- Squelette sans habillage ; capture publique fournie. Validation visuelle de Ced encore attendue.
- Pas de transaction financière, checkout bancaire, licence commerciale, réel, production, import ou tiers intégré. Invité sans compte : fermeture C14 existante, pas de rapprochement email.
- Pas de promesse de concurrence de mises à jour simultanées de composition ou de récupération après crash entre la persistance du paiement et celle des métadonnées de ligne. En l'absence d'instantané valide, fermé. Pas de couche transactionnelle nouvelle ni matrice disproportionnée.
- L'immutabilité est celle du raccord applicatif : aucun écran d'édition de l'instantané. Elle ne prétend pas empêcher un administrateur de base de modifier les tables hors API.
- Conservation de l'état **métier**, pas identité totale de toute la base : compteurs auto-incrémentés, caches/transients, tables analytiques et logs techniques peuvent évoluer ; les caches de rapports WCS sont exclus par la projection historique utilisée. Les profils, commandes, métadonnées métier et actions métier sont, eux, contrôlés ; les sessions/usermeta touchés ont aussi leur restitution ciblée exacte.
- Le rejeu des paquets signale toujours **A-32 / A32_PARTIAL_EVIDENCE** : 12 paquets vérifiés, 1 échec connu hors lot, aucun resceau ou correction d'A32.
- Les vieux reçus à empreinte globale du bootstrap C14/B11 sont historiques après ajout C28 ; aucun paquet clos n'est réécrit. Le nouveau raccord est qualifié par les régressions C14 et le rejeu général, pas par une réécriture de leurs empreintes.

## Décisions prises à défaut

Produit simple + liste plutôt qu'extension commerciale ; instantané après persistance du paiement (échec avant persistance testé) ; pas de reprise d'anciennes lignes ; exception Coming Soon limitée à la fiche fictive et hors plugin applicatif ; réglage de remboursement C14 réutilisé tel quel ; composition passée sans réglage nouveau conformément à la décision actuelle. Aucune question technique laissée bloquante.
