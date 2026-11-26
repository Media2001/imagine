# C-17 — réception actuelle, instructions 1 à 5

**PRET technique. Question 5 résolue par `A-FAIRE-2.md` à 4 h 30 (26 novembre 2026).** La conservation après **validation et refus** est limitée à `categorie`, `decision` (l'état affiché) et `fin` : trois champs, pas un de plus. Date UTC et opérateur sont dans le journal natif C10, ajouté par les hooks `updated_option` / `added_option` existants ; aucune bibliothèque close ni capacité n'a changé. L'écran référent n'affichait pas ces métadonnées et n'en a pas besoin pour sa file en attente : aucune copie n'est recréée dans le dossier. Le journal C10 les affiche déjà.

## À ouvrir maintenant — seul site fictif `http://192.168.129.32:8085`

- `p-sol-att` : `/my-account/#imagine-compte-factures`, **En attente**, dépôt fictif protégé ; `p-sol-ok` : **Validé jusqu'au…**, sans fichier. Le reset documentaire restaure ces deux seuls profils.
- `e-abo` : `/wp-admin/admin.php?page=imagine-justificatifs`, **Imagine → Justificatifs solidaires**. Valider ou refuser supprime le fichier ; le compte affiche l'état et, si validé, la fin. Ni date de décision ni opérateur ne sont stockés dans le dossier.
- `e-admin` : `/wp-admin/admin.php?page=imagine-reglages`, **Journal des modifications** : lignes `imagine_justificatif_26` / `27`, date UTC et opérateur dans les colonnes C10. Avant/après ne contiennent aucune référence de fichier. Les catégories restent dans le formulaire C10 existant.
- Identifiants C09 hors dépôt : `C:\Users\Ced\.imagine-demo\identifiants.json`, clé `c09_accounts`. Ne déposer aucune vraie pièce, aucun compte ou email réel.

## Preuves actuelles — `instruction5-20261126/`

- **`verification-successeur-V2.json`**, sceau en lecture seule des sources, empreintes natives et reçus. Les preuves antérieures ne sont pas réécrites.
- **`green-final-http.json` : 54/54**, vrais POST de validation et refus, puis relecture WP-CLI dans un autre processus : objet strictement égal aux trois champs attendus. Le journal C10 conserve l'auteur `e-abo` et la date UTC pour les deux décisions ; son écran natif les rend réellement. Fichiers absents après décision, ancien formulaire refusé et reset vérifié.
- **`journal-failure.json` : 6/6**, panne de l'ajout au journal injectée seulement dans le processus de recette : refus explicite, option restaurée sans fausse décision, compte indisponible sans lien mort, ancien formulaire HTTP refusé 409 ; redépôt/reset réparateur. Aucun mécanisme de panne dans le plugin.
- **`green-final-b02.json` : 84/84** avec C17 chargé ; **`green-final-c09.json` : 382/382**. Action 8793 `pending`, arguments `{"subscription_id":101}` : ligne entière inchangée. Aucun seed global ni replanification.
- **`unit-green.json` : 8 tests / 27 assertions** ; **`unit-root.json` : 120 / 615**. **`preparer-image.log`**, puis **`rejouer.log` : T01 canonique 1084 tests / 34363 assertions, zéro échec/erreur/saut**. Conteneurs unitaires hors réseau retirés.
- Déploiement limité à `JustificatifRegles.php` et `Justificatifs.php`, relus par SHA-256. Ancienne décision fictive P-SOL-OK transférée en trois champs ; **son auteur et sa date initiaux** retrouvés dans C10, non réinventés. Bootstrap, seed global, extension de reset C17, template, C18 et adaptateur C10 inchangés.
- RED pur et HTTP conservés ; essais de banc initiaux conservés (dossier de sortie absent puis concaténation PHP sans espace corrigés). Ce ne sont pas des échecs applicatifs résiduels.

## Commandes parent — depuis `C:\Users\Ced\imagine`

```powershell
# Relecture seule du sceau courant ; choisir un nom neuf à chaque passage.
python wp/tests/demo/c17-instruction5.py seal verification-parent-V2

# Rejouer les parcours réels sous un nom neuf (reset ciblé inclus), puis relecture seule.
python wp/tests/demo/c17-instruction5.py run parent-parcours
python wp/tests/demo/c17-instruction5.py seal verification-apres-parcours-V2
```

`seal` contrôle l'état natif exact et les sources, pas le blob aléatoire régénéré par le reset. Les anciens lanceurs ci-dessous sont historiques : **ne pas les rejouer vers leurs anciens noms**, afin de conserver les reçus. Les quatre instructions techniques antérieures n'ont pas été réimplémentées. Capacité accordée uniquement par le jeu démo, aucune règle tarifaire/d'accès touchée. Aucun traitement de C19, C20 ou C21 ; validation visuelle et relecture restent attendues, aucun GO réel.

---

# Historique du rendu à quatre corrections — attente alors déclarée, désormais résolue

**PRET technique / ATTENTE Ced pour la question RGPD.** `ATTENTE-ARBITRAGE-RGPD.md` isole la question : deux ou cinq champs après décision ? Le modèle existant à cinq champs est conservé, sans audit supplémentaire. Aucun GO réel, clôture ou validation visuelle.

## À ouvrir sur la seule démo fictive

Base : `http://192.168.129.32:8085`. Identifiants C09 déjà hors dépôt, dans `C:\Users\Ced\.imagine-demo\identifiants.json`, clé `c09_accounts`.

- `p-sol-att`, `/my-account/#imagine-compte-factures` : factures distinctes, vides faute de raccord Odoo ; justificatif **En attente**, catégorie **à préciser**, fichier synthétique protégé, rappel de masquer le registre national. Ne jamais déposer de document réel.
- `p-sol-ok`, même adresse : **Validé jusqu’au…**, aucun fichier conservé. Le reset fixe la date à +45 jours.
- `e-abo`, `/wp-admin/admin.php?page=imagine-justificatifs` : file sous Imagine, téléchargement puis validation/refus avec confirmation. Les deux décisions suppriment le fichier du disque ; la date d'aujourd'hui est acceptée pour valider.
- `e-admin`, `/wp-admin/admin.php?page=imagine-reglages` : catégories dans le formulaire C10 existant.
- Anonyme, autre abonné et rédaction : lecture interdite 403 ; ancienne URL remplacée ou décidée : 404. Attachment + sandbox + nosniff ; aucune prévisualisation active. Le contrôle PDF n'est pas une désinfection universelle.

Un échec de remplacement après suppression de l'ancien fichier affiche **Document indisponible** dans le compte et la file, sans lien mort ni décision possible. L'ancien formulaire est refusé 409 ; un nouveau dépôt répare. Au rendu, les deux états C09 sont restaurés et un seul fichier privé subsiste.

## Preuves de ce rendu

Dossier `corrections-20261126/`, reçu courant **`verification-successeur-V2.json`**, détail site `final-V2.json`.

- B02 avec C17 chargé : **84/84 natifs et 51/51 HTTP**, factures distinctes du justificatif, aucun check supprimé.
- C17 : **49/49 HTTP**, **8/8 réglages**, **8/8 refus/concurrence**. Corrections : remplacement **10/10**, suppression native **17/17**, bornes **10/10**.
- Pur **8 tests / 26 assertions**, plugin complet **116 / 587**. Image préparée ; T01 canonique **1080 / 34335**, zéro échec/erreur/saut.
- C09 **382/382** ; action **8793 pending**, arguments `{"subscription_id":101}`, ligne entière strictement préservée. Aucune réécriture de l'ancienne action 8103.
- JPEG et PNG complets vérifiés avec Pillow puis servis octet pour octet ; PDF complet de **5 242 880 octets** ; fin **26 novembre 2026**, égale au jour UTC de l'exécution. Cinq champs après décision inchangés.
- Nettoyage par **`delete_user`**, avant perte du titulaire, compatible avec le verrou ; pas `deleted_user`, qui arrive après. `wp_delete_user()` natif réellement joué sur des comptes uniques fictifs en attente, validés et refusés. Obstacle physique : erreur 409 explicite, compte et référence conservés. Aucun hook privacy C21 ajouté.

L'échec fopen est injecté seulement dans le processus PHP de recette ; la suppression de l'ancien fichier, les options et le refus HTTP du vieux formulaire sont réels. Le plugin ne contient aucun mécanisme d'injection de panne. Sources relues par SHA-256 ; bootstrap, seed et template partagés inchangés. Reçus historiques conservés. Les sorties RED et le premier rejeu infructueux sont conservés : chemin de fixtures canonique et capture du formulaire avant obstacle corrigés.

## Rejeu parent depuis `C:\Users\Ced\imagine`

```powershell
# Facultatif : réinstallation du seul fichier applicatif corrigé, sans bootstrap.
python wp/tests/demo/c17-corrections.py deploy parent
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1 > production/C-17/corrections-20261126/preparer-image.log
python wp/outils/demo/c17-unit.py corrections-20261126/unit-rules
python wp/outils/demo/c17-unit.py corrections-20261126/unit-root --root
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1 > production/C-17/corrections-20261126/rejouer.log
python wp/tests/demo/c17-corrections.py all final-V2
python wp/tests/demo/c17-corrections.py seal verification-successeur-V2

# Vérification lecture seule des sources, reçus et état final :
python wp/tests/demo/c17-corrections.py seal verification-successeur-parent-V2
```

Le reset documentaire ciblé est inclus dans les recettes ; pas de seed global. Les comptes temporaires `c17-fictif-delete-*`, en `@example.org`, sont nettoyés ; aucun compte C09 n'est supprimé. Aucun prix, paiement, abonnement ou droit ne change.

Source officielle consultée pour l'ordre des hooks : `https://developer.wordpress.org/reference/functions/wp_delete_user/` (code source, pas la note de description contradictoire).

Claude doit reporter la contradiction brief/CDC dans `docs/ecarts.md` ; aucun fichier de `docs/` n'a été écrit. **C18 et C21 non touchés.** Besoins visuels existants : `besoins-designer.md`.
