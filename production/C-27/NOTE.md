# C-27 — réception corrective du 27 novembre 2026

**Reçu courant : `correction-final-V2.json`, lié à `final-V2.json` conservé comme historique.** Le code C27 corrige les cinq instructions de `corrections/C-27.md`. Le corps ancien ci-dessous est explicitement historique et ne décrit pas les sources actuelles.

**Limites :** PRET technique de la seule démo fictive, ni clôture ni GO réel. Rejeu général PASS pour tests/outils, mais paquets annexes **A-31 `A31_PARTIAL_EVIDENCE` / A-32 `A32_PACKAGE_DRIFT` rouges**, signalés sans intervention. Boutique Woo « À venir » conservée ; visuel et place C10 toujours à Ced.

## Les cinq instructions appliquées

1. **I1 :** sous verrou et transaction, lecture SQL directe SOURCE avec invalidation `user_meta`, contrôle de `last_error` et du résultat. Absence = aucune ligne ; erreur = rollback de la déclaration, source antérieure intacte. Une ligne existante, même vide, est conservée (défaut prudent).
2. **I2 :** même lecture fiable avant suppression, vérification SQL de disparition avant commit, puis relecture finale SOURCE après commit. Cache vide périmé, lecture défaillante ou suppression refusée ne donnent jamais `done=true` : `items_retained=true`. Une incertitude après commit reste incomplète même si l’effacement a déjà eu lieu.
3. **M1 :** VUE invalidée et tombstone `etat=effacee` contrôlé sous le même verrou, même sans REPONSE. Un vieux POST de proposition vue seule effacée est refusé. README corrigé ; SOURCE garde le tableau complet `commande`, `compte`, `date`, `choix`, `libelle`.
4. **Tests :** cinq nouvelles régressions, rouges avant correctif puis vertes : première lecture SOURCE à l’écriture et à l’effacement, cache empoisonné avec suppression refusée, relecture finale en échec, ancien formulaire après proposition vue seule effacée. Les doubles propres C27 reproduisent cache/erreur et déséchappement WordPress ; aucun bootstrap partagé modifié.
5. **Relecteurs :** recettes mutantes Python non rejouées des deux côtés ; PHPUnit non rejoué côté Codex (`Wsl/Service/E_ACCESSDENIED`) lors du premier tour. Limite conservée dans `A-VOIR.md`. La livraison corrective a réellement lancé ces preuves, sans attribuer ce rejeu aux relecteurs.

## Réception actuelle vérifiée

- **12 tests / 80 assertions** ciblés ; journaux TDD rouges `correction-I1-rouge.log`, `correction-I2-rouge.log`, `correction-M1-rouge.log` : respectivement 1, 3, 1 échecs d’assertion sans erreur PHP ; verts intermédiaires conservés.
- **11 mutants de source** détectés hors réseau, chacun sortie 1 et échecs d’assertion, sans erreur PHP.
- **56 contrôles natifs/HTTP** : 7 natifs, 40 HTTP nominaux, 9 correctifs. **5 témoins mutants réels** : paiement/transmission, plus I1/I2/M1 correctifs.
- Vraies erreurs SQL d’une seule lecture avec écritures ensuite fonctionnelles. I1 mutant écrase réellement la source et valide la réponse ; corrigé, refus/rollback. I2 mutant annonce réellement `done=true` avec SOURCE toujours présente SQL ; corrigé, incomplet. Suppression refusée sur cache vide et troisième lecture défaillante couvertes.
- M1 utilise le nonce du vrai formulaire Woo, efface VUE sans réponse, puis soumet le vieux POST : **403**, aucune donnée recréée ; garde retirée : **200**, réponse/source réellement créées. Octets corrigés restaurés aussitôt.
- Chaque recette restaure et relit **18 ensembles**, profils, commandes classiques/HPOS, options métier, adresses, items, notes, navigation et quatre tables Action Scheduler. Huit commandes correctives supprimées ; les commandes HTTP et brouillon C16 aussi. Readback final : code distant exact, aucune réponse/proposition de recette, trois fichiers temporaires absents. Aucune transmission réelle, email ou paiement bancaire/service.
- Image reconstruite/sondée `correction-image.*`. Rejeu courant : **1 195 tests / 36 573 assertions**, 0 échec/erreur/ignoré ; **720 contrôles d’outils**, 0 échec ; **12 paquets annexes, 2 échecs** nommés en tête, jamais présentés comme verts.
- PHPCS des cinq classes : **0 erreur / 32 avertissements de longueur** ; sa sortie 1 est conservée dans `correction-style-command.json`, pas assimilée à un succès strict sans avertissement.

Commandes réellement exécutées depuis `C:\Users\Ced\imagine`, Python 3.11.15 / PHP 8.2.33 :

```text
python -B wp/outils/demo/c27.py local correction-unitaire-final
python -B wp/outils/demo/c27-mutations.py correction-mutants-horslive
python -B wp/outils/demo/c27.py deploy deploy-correction
python -B wp/outils/demo/c27-corrections.py correction-recette-fusion-exacte
python -B wp/outils/demo/c27-native.py correction-native
python -B wp/outils/demo/c27-recette.py correction-HTTP
python -B wp/outils/demo/c27-gates.py prepare correction-image
python -B wp/outils/demo/c27-gates.py regression correction-regression
python -B wp/outils/demo/c27-readback.py correction-readback correction-HTTP
```

Les portes appellent réellement `wp/tests/preparer-image.ps1` et `wp/tests/rejouer.ps1`, inchangés. Commandes parent dans `A-VOIR.md`.

**Partage :** seuls les deux adaptateurs C27, ses tests/doubles et lanceurs propres changent. Dans le README partagé, seule la section C27 change. **Ni `imagine-site.php`, ni bootstrap partagé, ni C10, ni bibliothèque close, ni code voisin modifié par C27.** Pas de réception voisine à refaire pour un bootstrap qui n’a pas changé. L’ancien paquet C27 et son vérificateur (`verifier-historique-avant-fusion.py`) restent historiques, sans substitution d’empreintes.

**Incidents de banc conservés :** premier essai trop large (lectures usermeta avant verrou) et concaténation PHP sans espace ; second essai I2 rouge mais sans présence de SOURCE. Le banc final cible sous verrou et exige la vraie présence SQL de SOURCE du mutant. Ces essais ont restauré exactement leur état ; ils ne servent pas de réception finale. Aucun changement métier supplémentaire.

Pas de nouveau test d’entrelacement simultané effacement/réponse revendiqué : verrou symétrique et cache périmé couverts, deux POST concurrents nominaux toujours exercés. Pas d’email/ZIP natif, de second parcours classique, de qualification réelle ni de validation visuelle. Aucun style ou déplacement C10.

---

# Historique de la livraison initiale — non applicable aux sources corrigées

Ancien reçu `final-V2.json`, ancien `PRET` préservé dans `PRET-historique-avant-fusion`. Les comptes, promesses et incidents qui suivent appartiennent à cette livraison antérieure à la fusion.

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
