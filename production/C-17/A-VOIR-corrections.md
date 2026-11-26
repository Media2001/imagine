# C-17 — réception actuelle après les quatre corrections

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
