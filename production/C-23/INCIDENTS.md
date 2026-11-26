# C-23 — Incidents et décisions techniques

## Résultat actuel

Aucune fuite constatée sur le corpus livré, hors mutation volontaire. Dernier rejeu opposable : `livraison.json` — 1 432 contrôles, zéro fuite, zéro échec. La mutation séparée rend le même détecteur rouge : 177 fuites, dont la page d’article pour l’anonyme, puis restauration et rejeu vert. Aucun code de paywall, plugin ou thème n’a été modifié.

## Faux rouges de construction — conservés, pas présentés comme des fuites du site

1. `diagnostic-01` avait cinq faux signalements sur la recherche HTML : WordPress réaffiche le terme saisi dans le titre et le formulaire, sans résultat correspondant. Le détecteur inspecte maintenant les résultats dans le vrai `<main>`, retire exclusivement le titre/formulaire réfléchis et vérifie l’absence de l’identifiant de l’article cible. Un résultat contenant réellement le témoin reste rouge (test automatisé).
2. Une première normalisation masquait du texte encapsulé dans CDATA. Une régression est devenue rouge avant correction ; les délimiteurs CDATA sont désormais retirés avant l’analyse, et le texte est conservé.
3. L’accueil ne liste que cinq articles : il ne contient pas le témoin principal 42. Archives/flux connectés n’ont pas non plus tous les mêmes objets que la réponse anonyme. Les témoins de C-08 réellement présents et la structure non vide sont donc contrôlés, avec tous les témoins interdits du corpus. Aucun contrôle n’a simplement été supprimé pour obtenir le vert.
4. Chemins réels rétablis dans le test : compte natif `/my-account/`, page C-16 `imagine-commandes`, tableau de bord `imagine-tableau-de-bord`, constantes natives relues pour les écrans. Le PDF refusé redirige maintenant vers la page numéro : cette vraie page et l’absence de PDF sont contrôlées, pas un ancien libellé de bloc.
5. Le plan de site est désactivé nativement. Le test distingue une fermeture 404 confirmée par l’inventaire d’un faux XML vide. La configuration activée n’est pas annoncée comme testée.

## Métadonnée WooCommerce apparue lors des refus administratifs

Le premier rejeu élargi avait une matrice verte mais **un état natif différent** : deux lignes `_woocommerce_tracks_anon_id` avaient été ajoutées par WooCommerce aux personnages 7 et 8. Le lanceur a échoué au lieu de prétendre prêt.

Le chemin natif installé `WC_Tracks_Client` a été lu : il utilise d’abord le cookie `tk_ai`, sinon crée une métadonnée. Deux lignes temporaires exactement identifiées (`12169`, `12170`, utilisateurs `8`, `7`, clé technique vérifiée) ont été retirées ; le SHA-256 complet de l’état métier initial a été retrouvé (`restauration-tracks.json`). La préparation fournit depuis un cookie `tk_ai` éphémère, uniquement en mémoire. Les derniers reçus prouvent que les GET ne changent plus cet état ; la garde hors ligne demeure en place et aucun transport de télémétrie n’a été ouvert.

## Chaîne de trois rejeux interrompue par le plafond du terminal

Une commande shell enchaînant trois rejeux a atteint le plafond externe de 420 secondes. Le troisième sous-processus avait écrit sa matrice verte (`matrice-finale.json`) mais le lanceur a été tué avant son reçu de restauration. **Ce reçu sans restauration n’est pas utilisé comme preuve de livraison.**

Une récupération bornée, en lecture puis en application, a :

- vérifié la cible et l’intervalle entre le reçu de restauration de mutation et la matrice interrompue ;
- trouvé exactement une session créée dans cet intervalle, avec durée native de 7 200 secondes, pour chacun des quatre personnages alors utilisés ;
- révoqué uniquement ces quatre sessions, conservant les autres sessions encore présentes ;
- supprimé les deux options de découverte qui étaient absentes avant la préparation ;
- retrouvé exactement le SHA-256 initial de l’état métier et la même action planifiée native.

Preuve : `recuperation-timeout.json`, diagnostic et application dans `recuperation-timeout.txt`, script ponctuel `wp/tests/demo/c23-recovery.py`. Ce script est conservé pour la traçabilité et ne fait pas partie du rejeu courant.

**Limite honnête de cette récupération :** le snapshot brut des sessions, gardé uniquement en mémoire pour ne pas déposer de secrets, a été perdu lors de l’arrêt. Une éventuelle purge par WordPress d’une session déjà expirée à la création n’est pas reconstituable. Aucune nouvelle session créée par le rejeu interrompu ne subsiste, et aucun droit métier, profil C-09 ou calendrier n’a changé. Il ne faut pas appeler cette récupération une preuve des octets de toutes les anciennes sessions.

Depuis : sous-processus HTTP limité en interne à 240 secondes, appels complets lancés séparément et terminés sous le plafond externe. Les rejeux `publics-complets-01`, `mutation-publics-complets`, puis `livraison` possèdent tous leurs reçus de restauration exacte des métadonnées courantes, des profils et des actions planifiées. La recette C-09 a été relue ensuite : 382 contrôles, aucun échec, code 0, état natif inchangé.

## Décisions prises à défaut

- Réutiliser exclusivement le jeu fictif et les coupe-circuits déjà présents. Aucun nouveau compte, article, PDF, paiement, lien offert/groupé ou document réel.
- Conserver C-08 comme témoin additionnel et prendre le T4 comme cible négative commune : l’acheteur existant possède le T1/C-08.
- Préparer/restaurer les sessions et le réglage existant **hors commande visiteur**, plutôt que faire un POST de connexion ou de réglages dans la commande certifiée GET.
- Inventorier tous les profils et inclure les neuf autres personnages sans droit natif. Ne pas consommer la découverte encore ouvrable de `V-DEC` pour fabriquer une preuve lecture seule ; le cas découverte épuisée est celui de `V-DEC-FIN`.
- Aucun correctif de paywall n’a été tenté : une vraie fuite hors mutation aurait bloqué le lot et aurait dû être corrigée par le lot propriétaire de la sortie.

Pas de rapport écrit dans `files/rapports/` : il appartient au parent. Ni verrou ni file modifiés.
