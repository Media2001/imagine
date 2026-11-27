# B-09 — choix natifs, stockage et limites

**Actualisation après fusion du 27/11 : instructions 1–5 appliquées.** Preuves courantes et compteurs : `CORRECTIONS.md` et `A-VOIR.md`, paquet `corrections-final-V2.json`. Les paragraphes de première livraison ci-dessous restent historiques : leurs anciens nombres, fenêtres d'interruption et quatre paquets rouges ne décrivent pas le rejeu corrigé.

## Le standard d’abord — cinq lignes

1. Les cinq écrans sont des pages WordPress ; pas de type FAQ, constructeur ni table éditoriale supplémentaire.
2. La FAQ reçoit quatre blocs natifs **Titre** niveau 2, sans questions/réponses ; la rédaction ajoute un bloc **Détails** sous la rubrique choisie (résumé = question, paragraphe intérieur = réponse), puis Enregistrer.
3. La confidentialité est réellement la page désignée par `wp_page_for_privacy_policy` ; `get_privacy_policy_url()` est relu, pas un simple lien portant le bon nom.
4. Le pied de page est un menu natif à l’emplacement `imagine-footer` ; le menu principal n’est pas réécrit et les textes édités ne sont jamais réinitialisés au rejeu du seed.
5. Le seul ajout nécessaire est le traitement privé du contact et sa déclaration aux exporteurs/effaceurs natifs déjà utilisés par C-21 ; aucun transport, cookie de suivi, bandeau ou moteur FAQ nouveau.

## Sources officielles effectivement consultées

Métadonnées des dix pages récupérées (URL, empreinte de la réponse, extrait borné) : `sources-officielles.json`.

- Pages et éditeur natif : <https://wordpress.org/documentation/article/pages/> ; bloc Détails : <https://wordpress.org/documentation/article/details-block/>.
- Désignation native de confidentialité : <https://developer.wordpress.org/reference/functions/get_privacy_policy_url/>.
- Insertion et déséchappement : <https://developer.wordpress.org/reference/functions/wp_insert_post/> et <https://developer.wordpress.org/reference/functions/update_post_meta/>. Le traitement fait `wp_unslash` une seule fois sur POST, puis `wp_slash($meta)` à la frontière d’écriture. Le double de test déséchappe lui aussi les métadonnées.
- Visibilité du type : <https://developer.wordpress.org/reference/functions/register_post_type/>.
- Menu et marqueurs précoces : <https://developer.wordpress.org/reference/functions/wp_update_nav_menu_item/> et <https://developer.wordpress.org/reference/hooks/wp_create_nav_menu/>. Le hook `wp_add_nav_menu_item` précède l’achèvement du rattachement ; son marqueur permet de retrouver l’item interrompu.
- Exporteurs et effaceurs : <https://developer.wordpress.org/plugins/privacy/adding-the-personal-data-exporter-to-your-plugin/> et <https://developer.wordpress.org/plugins/privacy/adding-the-personal-data-eraser-to-your-plugin/>.

## Stockage — information pour l’import de la voie 1

**Un contact est un message de formulaire : son contenu doit être vidé sur une future copie de travail, pas anonymisé mot à mot.**

| Emplacement | Valeur / fonction |
|---|---|
| `wp_posts.post_type` | `imagine_contact` |
| Statut / auteur / parent / corps | `private` / `0` / `0` / chaîne vide |
| Titre natif | `Message de contact`, aucune identité ni extrait du message |
| `wp_postmeta.meta_key` | `imagine_contact_nom`, `imagine_contact_email`, `imagine_contact_texte`, `imagine_contact_consentement`, `imagine_contact_date` |
| Consentement | chaîne `1` si la personne coche, `0` sinon ; uniquement le recontact au sujet du message |
| Date | UTC, format `DATE_ATOM` |
| Compte du visiteur | aucun rattachement ; aucun `user_id`, rapprochement ou test d’existence au dépôt |
| C-21 / WordPress | registre `imagine-contacts` ; `ContactConfidentialite::exporter/effacer`, recherche par email normalisé, tranches de 50 |
| Option technique de reprise d'effacement | `imagine_contact_effacement_<sha256(adresse normalisée)>`, non autoloadée ; seuls IDs connus en attente, écrits et relus avant suppression ; retirée après absence SQL vérifiée des métas. À vider lors d'une future copie, sans rouvrir l'import clos ici |

L’import fermé de la voie 1 **n’est pas modifié**. Lui transmettre ce type et ses cinq clés pour compléter sa politique fermée lors d’un lot autorisé : retirer les posts connus **et leurs postmeta**, y compris les metas orphelines attachées à leurs IDs. Ne pas prétendre que l’import actuel reconnaît déjà B-09. Aucun message d’essai B-09 n’est laissé dans la démonstration.

Les pages et menus ne sont pas des messages : option `imagine_b09_pages` (cinq IDs), marqueur `imagine_b09_page` par page ; option `imagine_b09_menu` (menu + cinq items), marqueur `imagine_b09_menu_item` par item, nom `imagine-b09-footer`, emplacement `imagine-footer`. Ils ne contiennent aucune donnée de visiteur.

## Preuves et décisions prises à défaut

Correctif courant : scan de tous les marqueurs, y compris détachés/hors option ; refus de type, marqueur, rattachement ou propriété ambigus. Interruption réellement déplacée entre marqueur et option. Effacement : relecture SQL des clés `imagine_contact_*`, `done=false` si une survit, reprise par IDs persistés même sans méta email. Test PHPUnit et injection native d'une suppression partielle, rouges/verts et mutations : `CORRECTIONS.md`. Espaces après casts corrigés dans les fichiers B-09 neufs. Duplication Contact/Sujet et succès par chaîne maintenus, sans modifier Sujet ni autre lot.

- Les cycles rouges puis verts sont conservés : `red-contact.log` (quatre vrais échecs de fonctionnalité absente), `red-structure.json` (seed absent), puis recettes vertes. Les deux tests complémentaires couvrent ensuite capacités/admin et raccord limité à la page de contact.
- La création initiale a été interrompue réellement par `exit(73)` au troisième item, **avant son rattachement** : deux items attachés et trois IDs marqués en base. Un autre processus WP-CLI a repris les mêmes pages et les trois premiers items, puis un troisième a relu le même résultat. Ce n’est pas une reprise simulée par un reçu inventé.
- Les essais structurels utilisent une transaction InnoDB rollbackée : édition par blocs natifs avec antislash, seed non destructif, refus de page/menu/item étrangers, confidentialité et menu principal relus.
- La recette HTTP crée des contacts à une adresse de compte fictif et à une adresse sans compte : même accusé, consentements `0` et `1`, détail admin et export à l’identique, effacement ciblé sans toucher au tiers. Les callbacks appelés sont ceux des registres natifs ; pas de nouvel outil d’export.
- L’absence REST/recherche a un témoin public positif. Une MU temporaire inverse les arguments natifs du seul type et publie le seul contact témoin : la collection REST, la recherche REST et les liens de recherche HTML le détectent. Statut privé restauré, MU retirée et contrôles revenus verts avant l’effacement.
- Les mutations de sources sont jouées dans des copies éphémères hors réseau ; celles d’email et HTTP prouvent que les compteurs ne sont pas constamment à zéro. Les coupe-circuits B-00 sont conservés pendant toutes les tentatives positives.
- Le brouillon `Privacy Policy` natif préexistant est conservé intégralement ; seule la désignation de politique pointe désormais sur la page B-09 publiée et vide. Une politique existante différente du brouillon natif attendu est refusée par le seed.

## Incidents de preuve et bilan transversal

**Historique de la première livraison seulement.** Le rejeu courant a 1 167 tests / 36 333 assertions, 22 outils / 584 contrôles verts ; 11 paquets vérifiés, zéro échec, A-32 hors rejeu (journaux absents). Les quatre anciens rouges ci-dessous ont disparu sans aucune intervention de cette voie dans leurs fichiers.

Le premier rejeu général a perdu son conteneur avant l’inspection finale : reçu conservé rouge, nouvelle tentative après cinq minutes. La dernière préparation d’image a réussi. Le dernier rejeu a réellement exécuté **1 159 tests PHP / 36 263 assertions**, plus **22 outils / 584 contrôles**, sans échec de ces suites. Il a également signalé **quatre échecs de paquets de la voie 1** : A-26 et A-27 `SEALED_VERIFICATION_FAILED`, A-30 `PACKAGE_DRIFT`, A-31 `A31_PARENT_GATES_MISSING`. Ils sont conservés dans le reçu et le compteur `foreign_packet_failures` ; aucun « tout le dépôt est vert » n’est revendiqué. Le PRET porte sur B-09 complet, pas sur ces autres paquets, que ce worker n’a ni corrigés ni rescellés. Le vérificateur refuse toujours un échec de B-09 ou des tests PHP eux-mêmes.

Le premier rejeu stable a révélé une actualisation native des dates des **seuls cinq items B-09** : le premier reçu porte bien `business_preserved=false`. Un test rouge a imposé l’absence de cette écriture, puis le seed a été corrigé pour ne pas réenregistrer un item déjà identique. La preuve initiale a été retirée par ses IDs et marqueurs, sans toucher aux autres contenus ; le contrôle attendait à tort la disparition de l’emplacement, alors que WordPress laisse sa valeur à zéro. La fixture finale a ensuite été recréée, réellement interrompue/reprise avec les sources finales, et tous les readbacks ont été rejoués. Les reçus anciens ne sont pas rebaptisés verts.

## Limites assumées — pas de PRET partiel de fonctionnalité

Squelette seulement : aucun texte juridique, aucune réponse FAQ, aucun design, aucun bandeau cookies ni décision d’outil. Les pages vides ne constituent pas une conformité juridique ni une publication réelle. Le consentement facultatif n’inscrit à aucune newsletter. Aucun email, HTTP extérieur, paiement ou tiers n’est raccordé.

Les exports/effacements B-09 ont été exercés via leurs callbacks **enregistrés dans les vrais outils natifs**, sur la base du site fictif ; le parcours complet de génération du ZIP WordPress et son email de livraison ne sont pas rejoués dans ce lot. Aucune durée de conservation automatique ni anti-spam de production ajouté : à arrêter avant ouverture au public.

La restauration est celle de l’état métier et des lignes applicatives relues. Les compteurs AUTO_INCREMENT, caches, transients et verrous temporaires de WordPress ne sont pas une prétendue restauration octet pour octet. Les sessions utilisées par la recette sont retirées par restitution des usermeta observées avant leur création.

Les pages publiques B-09 ne sont pas ajoutées à la matrice C-23/C-26. Aucun lot clos n’est étendu ou rescellé. Le bootstrap partagé, le footer et la section README sont contrôlés par contrat B-09 ; les anciens paquets ne sont pas réécrits. Le paquet C-23 historique, déjà périmé par C-26 selon le contexte parent, reste historique.
