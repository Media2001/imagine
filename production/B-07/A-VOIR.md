# B-07 — À voir sur la seule démonstration

**Corrections fusion21h41 appliquées le 26 novembre 2026.** Preuves courantes ci-dessous ; le rendu initial et ses reçus restent conservés sous leurs noms historiques.

## Adresses

Base : `http://192.168.129.32:8085` — `imagine-test-demo`, entièrement fictif.

- `/evenements/` : « À venir » trié du plus proche au plus lointain (10, 11 et 15 décembre 2026), puis « Événements passés » (1er novembre 2026).
- `/evenements/demo-events-1/` : rencontre gratuite, 10 décembre 2026 à 18 h 30 ; nom, email, consentement à être recontacté **non coché et facultatif**. Le consentement n'est pas une inscription marketing.
- `/evenements/demo-events-2/` : sortie de numéro, 11 décembre 2026 à 18 h 30 ; même inscription gratuite. Le titre fictif d'origine B-00 est conservé.
- `/evenements/b07-partenaire-fictif/` : partenaire, 15 décembre 2026 à 18 h 30 ; étiquette « Partenariat », lien commercial `rel="sponsored noopener noreferrer"`, aucun formulaire. Ne pas suivre le lien fictif pour la recette : il sort du site.
- `/evenements/b07-rencontre-passee/` : rencontre du 1er novembre 2026 ; mention « inscriptions closes », aucun formulaire, POST direct refusé également.
- Administration : `/wp-admin/edit.php?post_type=imagine_evenement`, boîte « Événement » pour type/date/heure/lieu/lien partenaire ; une saisie de type/date/heure invalide y porte une alerte explicite. Sous-menu « Inscriptions aux événements » (`/wp-admin/edit.php?post_type=imagine_inscription`). Après recette, la liste est vide : les inscriptions d'essai sont retirées.

Le JSON-LD se lit dans le source de chaque fiche : titre, début avec fuseau horaire du site, lieu et description correspondent au contenu affiché. Aucun prix, billet ou quota fabriqué. Squelette B-01 conservé, sans CSS ajouté. Validation visuelle de Ced attendue.

## Données et protections

Les inscriptions sont des contenus WordPress **privés** `imagine_inscription` dans les tables natives posts/postmeta, liés à l'événement par `post_parent`. Métadonnées : `imagine_agenda_nom`, `imagine_agenda_email`, `imagine_agenda_consentement` (0/1), `imagine_agenda_date` (UTC). Pas d'IP, de cookie, de mot de passe ou de compte créé par l'inscription. Administration réservée à `manage_options`, pas de REST ni d'export de liste natif (`can_export=false`).

Les callbacks `imagine-agenda` s'ajoutent aux outils WordPress d'export/effacement des données personnelles, sans modifier C-21. Ils retrouvent les inscriptions par adresse normalisée, y compris pour l'adresse d'un compte. L'effacement retire les inscriptions de cette adresse et garde celles des tiers. Un défaut de lecture ne devient jamais un export/effacement complet.

Le même événement et la même adresse donnent une seule inscription, sous exclusion mutuelle native en base. Création et doublon ont la même réponse ; une adresse ayant un compte ne reçoit aucune indication différente. Aucun consentement de newsletter n'est inventé.

## Preuves finales

- `correction2141-horslive-final.log` : **9 tests PHPUnit, 159 assertions**, dont 7 nouveaux tests sur les vrais adaptateurs et gabarits à bouchons WP. Type/date/heure invalides, borne de fermeture, doublon, R1, R2, R4, partenaire passé, i18n et alerte admin. Aucun WordPress live chargé.
- `correction2141-mutant-*.log`, `correction2141-mutations-sources.json` : **6 mutations de sources jetables exécutées**, toutes détectées : R1, R2, double exécution du contenu, R4, formulaire interdit, alerte retirée. Ce ne sont pas des mutations de réponses en mémoire.
- `correction2141-recette-finale-V2.json` : **26 contrôles de vrais parcours HTTP/WP** : corps partenaire commercial, contre-exemple rencontre, shortcode rendu une fois et description balisée exactement égale au corps affiché, partenaire passé avec label/lien, POST refusé, doublon, admin, saisie invalide. Deux témoins changent réellement la métadonnée : retour à l'agenda et apparition du formulaire en devenant rencontre. Fixtures retirées ensuite.
- `correction2141-privacy-V2.json` : **18 contrôles natifs**, erreur SQL réelle aux pages 1 et 2, `WP_Error`, reprise de la même page ; **121 inscriptions** exportées en 50/50/21 sans omission ni doublon, puis effacées. Le filtre C-21 est conservé.
- `correction2141-compat-privacy-V2.json` : ancien chemin de recette confidentialité adapté à `WP_Error`, rejoué vert (9 contrôles).
- `correction2141-readback-V2.json` : 6 contrôles indépendants, sources installées exactes, événements/métadonnées et état métier pré-installation exacts, réglages exacts, inscriptions et observateur absents.
- `correction2141-preparer-image.log`, `correction2141-suite-finale.log` : image préparée ; commande canonique **1 135 tests, 35 709 assertions, zéro échec/erreur/ignoré**, avec les deux classes Agenda dans son JUnit ; 18 outils / 417 contrôles verts.
- `manifest-correction2141.json`, `verifier.py` : contrôle hors réseau courant. Le fichier partagé `functions.php` est contrôlé par son **seul filtre autorisé**, le bootstrap par le seul bloc B07 ; aucun autre lot épinglé.
- `STANDARD.md` reste la justification initiale du raccord gratuit ; aucun ajout d'extension ou de billetterie.

**Rien ne part** : zéro email et zéro transport HTTP externe déclenché. Le reçu final distingue les **19 tentatives HTTP d'infrastructure** WordPress/extensions, toutes arrêtées par la garde existante, des appels de l'agenda (zéro) et des transports (zéro). L'observateur ne bloque rien ; son contrôle positif est arrêté par les protections existantes, puis ses compteurs sont remis à zéro.

Les préimages et sessions sont en scratch privé hors dépôt, écrites et relues avant mutation/session ; seuls les noms opaques et empreintes figurent dans les reçus. L'état métier a été relu exact ; sessions, caches et activité temporaire ne sont pas une restauration octet pour octet (arbitrage du 26 novembre 2026).

## Rejouer

Depuis `C:\Users\Ced\imagine`, choisir un **nom de reçu neuf** (les reçus existants ne sont jamais écrasés) :

```text
python production/B-07/verifier.py
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
python -B wp/outils/demo/b07-horslive.py preuve-horslive-neuve.log
python -B wp/outils/demo/b07-horslive.py preuve-mutant-neuve.log r4
```

La dernière commande doit échouer avec le seul test R4 attendu : c'est le témoin source, pas une livraison rouge. Les autres mutations disponibles sont `r1`, `r2`, `double-contenu`, `formulaire`, `alerte`.

Recettes applicatives **réservées à la seule démonstration gardée**, non nécessaires au rejeu horslive du relecteur :

```text
python -B wp/outils/demo/b07-corrections.py privacy privacy-nom-neuf-V2
python -B wp/outils/demo/b07-corrections.py recipe recette-nom-neuf-V2
```

La recette confidentialité refuse une inscription préexistante sur son adresse témoin. La recette HTTP crée ses propres événements éphémères et ne retire que leurs identifiants ; les cas partenaire passé/shortcode/saisie invalide sont retirés après preuve et ne sont pas de nouvelles pages permanentes à ouvrir. Le script `b07-recovery.py` est un inverse **historique**, pas une commande de rejeu : voir les notes d'incident ci-dessous.

## Écarts conservés, non rebaptisés

Le premier parcours des corrections est conservé rouge (`correction2141-recette-V2.json`) : tous ses contrôles fonctionnels passent, mais la première visite de l'éditeur natif a créé le post `wp_global_styles` du thème. Création exacte retirée, état métier initial relu exact (`correction2141-restauration-style-V2.json`). Le harnais photographie maintenant ces posts avant toute session et inverse seulement sa création. Le rejeu final est vert. Pas de chasse aux sessions, caches ou verrous, conformément à l'arbitrage de 19 h.

Les anciens reçus sans préfixe `correction2141` et `manifest.json` restent **historiques** ; leurs mutations de réponses ne sont plus la preuve canonique de clôture. `A-VOIR-historique-avant-correction2141.md`, `RAPPORT-historique-avant-correction2141.md`, `verifier-historique-avant-correction2141.py` et l'ancien PRET renommé les accompagnent. Un premier vert R2 a signalé des avertissements du parseur DOM de test sur HTML5 ; reçu conservé, parseur corrigé, vert sans avertissement rejoué.

Le premier parcours a terminé ses inverses de données mais n'a pas pu supprimer son observateur sous `www-data` (répertoire MU non inscriptible). Retrait exact effectué par le transport propriétaire après vérification d'empreinte, puis absence relue. Une préférence UI native créée à la première visite admin (`meta-box-order_product`) a été retirée sur sa préimage d'absence ; état métier initial relu exact (`recuperation-interface-V2.json`). Le harnais fait désormais ces deux inverses.

Les reçus rouges intermédiaires restent tels quels : nom de callback C-21 mal attendu dans un test, export de liste natif oublié puis fermé avec rouge/vert réel, comparaison trop large des en-têtes Date, et nonce REST absent du test abonné. Aucun de ces rouges n'est présenté comme un résultat de livraison. Le parcours final est vert sur les sources livrées. Pas de billetterie, quota, paiement, email de confirmation ni export d'inscrits ; pas de mise en ligne ni de validation visuelle automatique.
