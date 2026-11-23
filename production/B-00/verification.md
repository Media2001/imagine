# B00 — corrections arbitrées du 23 novembre 2026, 16 h 30

## Résultat actuel

Site unique `imagine-test-demo`, http://192.168.129.32:8085, état `running`. Thème `imagine`, locale `fr_FR`, WordPress 7.0.9, PHP 8.3.32, WooCommerce 11.2.2, Subscriptions 9.4.1 et Memberships 1.30.3 relus réellement. Aucune reconstruction destructive, aucun autre site, Git, verrou, rapport global ou fichier de `docs/` touché.

Le vrai CLI `construire.py --preuve reconstruction` a réussi sur le site déjà enrichi C08+C09+C10, puis **après le vrai seed C08**. `b00-integre.py --rejouer` appelle la fonction inchangée `c08.run(seed=True)` correspondant à `c08.py --seed`, en redirigeant uniquement son dossier de preuves vers B00, puis lance effectivement le CLI B00 en sous-processus. Les sources/rapports des autres lots ne sont pas réécrits.

## Corrections

- Cardinalités des articles et événements/partenaires limitées aux objets portant `imagine_demo_key`. Les deux articles C08 rattachés au numéro T1 restent en place : six articles dans son sommaire, dont quatre B00 ; la recette B00 n'en exige que ses quatre.
- Retrait de la protection native par mot de passe quand C08 est actif. Migration des anciennes valeurs en base sans changer les corps, IDs ou droits ; filtre ciblé `wp_insert_post_data` dans `Paywall.php` empêchant leur réintroduction, notamment par le seed C08 inchangé. Pages non concernées. Aucune assertion « mot de passe → corps » restante : ancien cookie sans droit, compte fictif C08 actif avec lecture positive.
- Locale `fr_FR` avec paquet officiel 7.0.9 téléchargé par l'outil hôte, SHA et fichiers relus. Le garde hors ligne du site n'est pas désactivé pour installer cette langue. Les extensions premium n'ont pas reçu de paquet de traduction : certains libellés tiers peuvent rester anglais.
- Purge limitée aux IDs/signatures d'installation : article 1 `hello-world`/`Hello world!`, page 2 `sample-page`/`Sample Page`, commentaire WordPress d'installation. Aucun filtre d'accueil B01 ajouté, aucun contenu des autres lots supprimé.
- Une politique de reprise par transport, sans enrobages imbriqués : toute mutation refusée pour occupation est reprise trois fois à 300 secondes ; lectures jusqu'à douze reprises à cinq secondes, puis arrêt explicite. Pas de forçage. GET initial, GET de suivi, lecture durablement refusée, mutation et épuisement sont testés ; les attentes sont doublées dans les tests, aucun refus réel de concurrence n'est revendiqué.

## Résultats de la dernière passe

| Suite | Réussis / exécutés |
|---|---:|
| Tests locaux B00+C08+C09+C10, sans test ignoré | 27 / 27 |
| Recette native B00 | 81 / 81 |
| Arbitrages B00 natifs (langue, purge, mot de passe, intégration) | 10 / 10 |
| Recette native C08 | 30 / 30 |
| Recette native C10 | 13 / 13 |
| Recette native C09, horloge de fixture explicitée ci-dessous | 364 / 364 |
| HTTP B00 et disponibilité de tous ses objets/médias | 68 / 68 |
| Étanchéité HTTP du propriétaire C08 | 229 / 229 |
| Non-régression C08/B00/B01, 71 fichiers métier relus | 120 / 120 |
| 27 connexions HTTP C09, corps/blocs comparés aux décisions natives | 108 / 108 |
| HTTP C10 en lecture seule, autorisations et huit champs | 9 / 9 |

**1 059 tests/assertions de suites, zéro échec**, plus **21 gardes finales** au vert dans `b00-final-verification.json`. Ce sont des assertions de recettes et 27 tests unittest, pas 1 059 méthodes unittest distinctes. B00 représente 11 des 27 tests locaux.

Les preuves RED sont conservées : cardinalités intégrées rouges (`quatre_articles_11`, `trois_reserves_11`), six contrôles d'arbitrage rouges, reprises non gérées, migration de snapshot et anciennes attentes HTTP rouges. Elles ne sont pas des reçus verts actuels.

## Conservation et snapshots

- B00 : **41 objets tagués**, manifeste de **45 entrées** (41 objets, trois termes, un compte), zéro doublon. La première migration ne change que les 15 indicateurs `protected` des articles réservés. IDs, slugs, URL, empreintes des textes/médias, métadonnées et calendrier sont égaux à l'ancien snapshot après cette unique normalisation autorisée. La référence pré-migration est conservée ; les reconstructions suivantes et la référence intégrée sont **strictement égales**, sans normalisation.
- C09 : **27 comptes, 13 commandes, 12 souscriptions, 14 adhésions**, tous IDs, états, dates, relations et décisions conservés. Aucun seed/reset C09 : les mots de passe et rôles existants sont vérifiés nativement, puis les 27 connexions sont exercées. Fichier privé B00 enrichi strictement égal à sa sauvegarde, avec ses 27 comptes C09, jamais recopié dans le dépôt.
- C10 : bootstrap `imagine-pilotage/imagine-reglages.php` toujours actif, PHP des bibliothèques et adaptateurs relu identique ; **options et toutes les entrées du journal strictement identiques**. Les tests HTTP n'enregistrent aucun réglage. Pas de restauration des anciens wrappers B00 à la place de C10.
- Les snapshots avant/après chaque reconstruction complète sont strictement égaux pour les autres lots. Le seed C08 peut, légitimement, réécrire ses propres hashages de connexion/dates techniques ; ses IDs, états et décisions sont revérifiés. Il ne modifie pas les objets C09/C10.
- Une première passe HTTP a révélé des métadonnées d'activité/télémétrie UI natives (`wc_last_active`, identifiant Tracks, messages d'administration), sans changement d'identité, mot de passe, rôle ni droit. L'ancien hachage global de toutes les métadonnées utilisateur n'est donc **pas présenté comme identique depuis le tout premier prévol**. Les reçus rouges et le diagnostic restent disponibles. Les passes finales prennent une référence privée en mémoire et restaurent uniquement ces champs UI testés ; leurs snapshots avant/après sont exacts. Les jetons de session et `last_update`, exclus dès le premier snapshot, ne sont ni exportés ni révoqués arbitrairement.

## Limite explicite de la recette C09

La recette C09 brute affirme que deux échéances restent à J+30/J+45 du **moment du test**, avec une tolérance de 300 secondes. Plus d'une heure après son seed original, elle renvoie deux échecs attendus : `A-ECHEANCE:terme_30_jours` et `P-SOL-OK:fin_45_jours` (`tests/b00-c09-runtime-brut.json`). Les corriger en reseedant C09 aurait déplacé les échéances et violé la conservation demandée.

La passe intégrée utilise donc **uniquement dans l'espace de noms du test C09** une horloge calée sur son reçu original `production/C-09/reset.json`, daté `2026-11-23T15:14:33.186101+00:00`. Les 364 assertions sont réellement exécutées ; aucune n'est ignorée ni déclarée réussie sans exécution. L'horloge de WordPress/Woo/C08, leurs droits à l'heure réelle et toutes les données restent inchangés. La comparaison exacte des objets/dates au prévol et les parcours HTTP à l'heure réelle sont indépendants de cette adaptation. Cela ne constitue pas une correction de C09 ; son oracle temporel est à améliorer dans son propre lot si sa recette brute doit se rejouer tardivement.

## Calendrier : clarification sans changement métier

B00 fournit bien le **calendrier brut complet de 15 lignes sur 2026–2028**, dans `imagine_demo_calendrier`, affiché par `/calendrier-fictif/`, et contrôlé nativement/en HTTP. Seuls les cinq numéros de **2026** sont matérialisés avec leurs articles/PDF. La remarque C09 disant que « le calendrier sur trois ans n'est pas complet » est donc trop large : le calendrier brut existe ; les numéros éditoriaux sur trois ans et la grille commerciale trois tarifs × une/quatre fois ne sont pas créés. Aucun prix, date métier ou durée de droit n'a été inventé pour combler ces autres limites.

## Preuves, historique et sécurité

- Actuelles : `b00-reconstruction.json`, `b00-final-verification.json`, `b00-verification-http-idempotence.json`, `tests/b00-integre-actuel.txt`, `tests/*-actuel.json`, `tests/b00-c09-horloge-fixture.json`, snapshots `tests/b00-integre-*.json`, `regression-c08/` et réponses anonymes `http/`.
- Historiques exclusivement : `historique/avant-corrections-23nov-16h30/` contient les premiers PRET, rapport, construction, captures TT25 et HTTP « 81/81 ». L'ancien rapport et le reçu de construction ont quitté la racine pour éviter de les confondre avec le rejeu courant. Les versions/minima initiaux restent tracés mais ne remplacent pas le readback actuel.
- Motifs de sécurité : email `false`, HTTP WordPress extérieur refusé, passerelles vides ; pas de licence commerciale, de paiement, d'archive réelle ou de compte réel. Novamira normal autorisé sur cette démo seulement. La garde MU n'est pas un pare-feu Docker : aucune isolation réseau de bas niveau n'est revendiquée.
- Aucun mot de passe, cookie, nonce ou HTML authentifié sauvegardé dans les preuves. Paquet de langue public et mécanismes standards documentés dans `sources-corrections.json` ; fichiers relus et secrets comparés aux artefacts de livraison.

## Écart à reporter par le parent / Claude

`imagine-site` réunit le modèle provisoire B00 et le moteur de droits C08 : B00 ne se certifie plus isolément. C'est assumé pour le site intégré ; C08 possède entièrement l'étanchéité. La correction demandant d'écrire dans `docs/ecarts.md` est transmise au parent/Claude, conformément à la file et à la doctrine §7 : **aucun fichier docs n'a été modifié**. La clarification du calendrier ci-dessus et l'oracle temporel C09 sont aussi à reporter sans changer le métier.

`PRET` signifie prêt à relire techniquement ; ce n'est ni une validation visuelle de Ced ni un GO de production.
