# C-27 — note de livraison

## Résultat

Question facultative sur la confirmation Woo payée du seul titulaire connecté ; rien dans le tunnel, aucun opérateur C16. Liste fermée dans C10, journalisée et restaurée si le journal échoue. Une réponse datée immuable par commande, source du compte initialisée uniquement si vide, chiffres sans identité par période UTC. Export/effacement déclarés et exécutés par leurs callbacks WordPress/C21. Aucune transmission Odoo/newsletter, aucun email, paiement, remboursement ou tâche de C27.

La documentation « standard d’abord » compte **cinq lignes** dans le README de l’extension ; références officielles effectivement consultées dans `sources-officielles.json`. Les bibliothèques closes, C10, les lots voisins et les fichiers de l’autre voie sont inchangés. Seul le bloc d’amorçage C27 et sa section README sont ajoutés aux fichiers partagés.

## Preuves finales et commandes réellement exécutées

Depuis `C:\Users\Ced\imagine`, sous Python 3.11.15 / PHP 8.2.33 :

```text
PYTHONIOENCODING=utf-8 python wp/outils/demo/c27.py local unitaire-final
PYTHONIOENCODING=utf-8 python wp/outils/demo/c27.py deploy deploy-final
PYTHONIOENCODING=utf-8 python wp/outils/demo/c27-mutations.py mutations-finales
PYTHONIOENCODING=utf-8 python wp/outils/demo/c27-gates.py prepare preparation-finale
PYTHONIOENCODING=utf-8 python wp/outils/demo/c27-gates.py regression regression-reprise-finale
PYTHONIOENCODING=utf-8 python wp/outils/demo/c27-seed.py liste-demo
PYTHONIOENCODING=utf-8 python wp/outils/demo/c27-native.py native-livraison
PYTHONIOENCODING=utf-8 python wp/outils/demo/c27-recette.py recette-antislash-livraison
PYTHONIOENCODING=utf-8 python wp/outils/demo/c27-readback.py readback-livraison recette-antislash-livraison
```

Les deux commandes de portes invoquent réellement, sans modification :

```text
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

- **7 tests PHPUnit, 55 assertions**, tous verts ; ils sont découverts dans le paquet racine existant.
- **7 contrôles natifs + 40 HTTP**, tous verts. Vrais POST `options.php`, `admin-post.php`, confirmation Woo à blocs, deux POST concurrents (un succès, un 403), vrai brouillon C16 et commande native d’un numéro ; statuts/dates de paiement explicitement fictifs, aucune banque appelée.
- **8 mutants de source** rouges sans erreur PHP : paiement, tiers, opérateur, source écrasée, export, effacement, export des tiers, réglage invalide. **2 témoins natifs** : retrait de la garde paiement autorise un POST impayé et écrit une réponse, puis la garde remise refuse ; injection email/HTTP détectée avant le coupe-circuit B00 inchangé. Le modèle Woo lui-même ne rend pas le formulaire impayé : le mutant natif tue le contrôle du POST, pas ce rendu ; aucun succès de mutation visuelle n’est inventé.
- Restauration exacte de **18 ensembles** : profils et métadonnées, commandes classiques/HPOS, adresses, items, notes, navigation, options métier et les quatre tables Action Scheduler. Les trois profils de session sont remis en place, les sept commandes de la recette, son brouillon et ses fichiers temporaires retirés. Readback final relu après le seed ; aucune réponse de recette conservée, deux choix fictifs seulement.
- Image reconstruite et sondée hors réseau ; replay final : **1 166 tests, 36 318 assertions, 0 échec/erreur/ignoré**, **584 contrôles d’outils verts**, **11 paquets annexes vérifiés, aucun échec**. Cela constate le résultat courant du lanceur partagé : aucun paquet de voie 1 n’a été ouvert ni réparé par C27.
- PSR-12 sur les cinq nouvelles classes : **0 erreur**, **32 avertissements de longueur de ligne** ; aucun reformatage d’un ancien lot. L’image isole PHP et ses dépendances : aucune installation sur l’hôte.

## Choix prudents et confidentialité

- Pas de relance : une trace de proposition est écrite **seulement** à la confirmation payée autorisée ; recharger ou ignorer ne repropose pas la question. La réponse vide et le lien « Continuer sans répondre » laissent la commande intacte.
- Les réponses restent dans des options non autoloadées `imagine_acquisition_reponse_ID` ; commande, compte, instant UTC, choix et libellé figés. `imagine_acquisition_vue_ID` conserve compte/date de proposition. Aucune de ces valeurs n’entre dans les métadonnées de commande Woo ou un événement de synchronisation.
- Le compte reçoit `imagine_source_acquisition` seulement si sa valeur est vide. Le bouchon des tests reproduit le déséchappement réel de `update_user_meta` ; le libellé `Radio fictive \ lune` traverse réglage, réponse, source et export sans perte.
- L’effacement supprime choix, libellé, compte **et date** ; reste uniquement `commande`/`etat=effacee`, sans source ni identité, pour interdire un redépôt. C’est une trace technique liée à la commande, pas une statistique personnelle conservée. Les déclarations effacées sortent des nombres. Seule la confidentialité déroge à l’immutabilité.
- Invités refusés, aucun rapprochement par email ; c’est le défaut prudent cohérent avec le rattachement non livré de C14. Une panne de lecture de compte/registre ne devient pas un export vide réussi.
- Inventaire pour un futur lot d’import autorisé : préfixes d’options `imagine_acquisition_reponse_` / `imagine_acquisition_vue_` et usermeta `imagine_source_acquisition` portent des données personnelles. La liste C10 est une configuration. Aucune modification de l’import clos ici.

## Limites réelles et incidents résolus

La boutique de démonstration reste en mode natif Woo **« À venir »**. La recette utilise le filtre standard `woocommerce_coming_soon_exclude` exclusivement dans son observateur temporaire, sur ses requêtes marquées, avec identité locale fictive contrôlée. Il est retiré ensuite ; aucune ouverture permanente ni réglage Woo changé. Un lecteur ordinaire ne peut donc pas ouvrir aujourd’hui une confirmation sans l’accès natif de prévisualisation de la boutique. La confirmation à blocs de la démo est testée ; la confirmation classique utilise le même hook, relu dans le standard Woo, sans second parcours HTTP classique revendiqué.

Les callbacks enregistrés d’export/effacement ont réellement tourné ; aucune demande email ou archive ZIP native n’a été envoyée/générée. Aucun compte réel, Odoo, Brevo, Stripe ou autre tiers contacté. Pas de qualification en volume réel ni de validation visuelle/designer ; aucun CSS ajouté. La place sous « Enregistrer » reste la question visuelle C10 déjà en attente, sans déplacement ni nouveau point d’accroche.

Les premiers reçus rouges sont conservés hors du paquet final : concaténation PHP du banc, accès boutique « À venir », puis inverse C16 incomplète. La dernière a révélé des adresses classiques orphelines en HPOS et l’invalidation d’une tâche native de cache de rapport Subscriptions. L’inverse finale ne vise que les IDs créés et cette action connue, avec comparaison des colonnes avant restauration ; `11-restauration-C16.json` puis les recettes finales prouvent le retour exact. Aucune correction de C16.

Un premier replay final a perdu son conteneur (`Inspection du conteneur impossible`) : conservé rouge dans `regression-finale.*`, puis rejoué seul avec succès dans `regression-reprise-finale.*`. Le seed a d’abord comparé aussi une expiration de cache Woo volatile ; seule `_transient_timeout_wcs_woocommerce_active_version` est explicitement exclue de cette comparaison non métier, jamais des profils/commandes/actions. Le moteur de restauration final conserve les options métier exactes.

Le processus Windows héritait d’un `TMPDIR` pointant vers `Local/Temp` : C27 force maintenant le scratch Hermes explicite. Ses 51 préimages déjà produites ont été déplacées, octets inchangés, dans `C:\Users\Ced\AppData\Local\hermes\cache\scratch` ; aucune préimage C27 ne reste dans `Local/Temp`. Cookies et snapshots ne sont jamais déposés dans le dépôt.

**PRET technique du périmètre prouvé uniquement** : pas une clôture, pas validation visuelle, pas GO sur le réel. Le vérificateur parent, sans argument/site/réseau, recalcule les totaux, exige les ensembles exacts de contrôles/restaurations et les empreintes des sources/preuves. Les contre-exemples de ce vérificateur ont leur commande dans `A-VOIR.md`.
