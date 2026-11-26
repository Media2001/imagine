# B-07 — À voir sur la seule démonstration

## Adresses

Base : `http://192.168.129.32:8085` — `imagine-test-demo`, entièrement fictif.

- `/evenements/` : « À venir » trié du plus proche au plus lointain (10, 11 et 15 décembre 2026), puis « Événements passés » (1er novembre 2026).
- `/evenements/demo-events-1/` : rencontre gratuite, 10 décembre 2026 à 18 h 30 ; nom, email, consentement à être recontacté **non coché et facultatif**. Le consentement n'est pas une inscription marketing.
- `/evenements/demo-events-2/` : sortie de numéro, 11 décembre 2026 à 18 h 30 ; même inscription gratuite. Le titre fictif d'origine B-00 est conservé.
- `/evenements/b07-partenaire-fictif/` : partenaire, 15 décembre 2026 à 18 h 30 ; étiquette « Partenariat », lien commercial `rel="sponsored noopener noreferrer"`, aucun formulaire. Ne pas suivre le lien fictif pour la recette : il sort du site.
- `/evenements/b07-rencontre-passee/` : rencontre du 1er novembre 2026 ; mention « inscriptions closes », aucun formulaire, POST direct refusé également.
- Administration : `/wp-admin/edit.php?post_type=imagine_evenement`, boîte « Événement » pour type/date/heure/lieu/lien partenaire ; sous-menu « Inscriptions aux événements » (`/wp-admin/edit.php?post_type=imagine_inscription`). Après recette, la liste est vide : les inscriptions d'essai sont retirées.

Le JSON-LD se lit dans le source de chaque fiche : titre, début avec fuseau horaire du site, lieu et description correspondent au contenu affiché. Aucun prix, billet ou quota fabriqué. Squelette B-01 conservé, sans CSS ajouté. Validation visuelle de Ced attendue.

## Données et protections

Les inscriptions sont des contenus WordPress **privés** `imagine_inscription` dans les tables natives posts/postmeta, liés à l'événement par `post_parent`. Métadonnées : `imagine_agenda_nom`, `imagine_agenda_email`, `imagine_agenda_consentement` (0/1), `imagine_agenda_date` (UTC). Pas d'IP, de cookie, de mot de passe ou de compte créé par l'inscription. Administration réservée à `manage_options`, pas de REST ni d'export de liste natif (`can_export=false`).

Les callbacks `imagine-agenda` s'ajoutent aux outils WordPress d'export/effacement des données personnelles, sans modifier C-21. Ils retrouvent les inscriptions par adresse normalisée, y compris pour l'adresse d'un compte. L'effacement retire les inscriptions de cette adresse et garde celles des tiers. Un défaut de lecture ne devient jamais un export/effacement complet.

Le même événement et la même adresse donnent une seule inscription, sous exclusion mutuelle native en base. Création et doublon ont la même réponse ; une adresse ayant un compte ne reçoit aucune indication différente. Aucun consentement de newsletter n'est inventé.

## Preuves finales

- `STANDARD.md` : dix lignes et sources officielles du gratuit ; décision de raccord natif, sans installer Event Tickets / Plus ni The Events Calendar.
- `regles-V2.json` : règles pures.
- `adaptateur-livraison-V2.json` : types, champs, droits, callbacks, fermeture REST et export de liste, mutations témoins.
- `recette-livraison-V2.json` : vrais GET/POST, absence de formulaire et refus direct passé/partenaire, doublon, admin, RGPD, JSON-LD et mutations des réponses réellement reçues.
- `confidentialite-V2.json` : inscription native puis export/effacement, passage du filtre C-21, vraie erreur de lecture SQL provoquée/supprimée, données conservées jusqu'au rejeu réussi.
- `regression-articles-corrigee-V2.json` : article, REST, flux, recherche et oEmbed ; inverse abonné, refus anonyme/compte sans droit/coopérateur.
- `readback-final-V2.json` : sources réellement installées, deux événements B-00 intacts, deux seules nouvelles fixtures, inscriptions et observateur retirés, état métier exact depuis la première recette.
- `preparer-image-final.log`, `regression-livraison.log` : image préparée après les tests ajoutés, suite générale verte incluant `AgendaReglesTest`.
- `manifest.json`, `verifier.py` : contrôle hors réseau des sources B-07 et preuves ; bootstrap partagé contrôlé par son seul bloc, pas par son empreinte entière.

**Rien ne part** : zéro email et zéro transport HTTP externe déclenché. Le reçu distingue les 17 tentatives HTTP d'infrastructure WordPress/extensions, toutes arrêtées par la garde existante, des appels de l'agenda (zéro) et des transports (zéro). L'observateur ne bloque rien : il observe les protections déjà présentes. Son contrôle positif demande un mail et une URL fictifs, arrêtés avant transport, puis remet les compteurs à zéro avant le parcours.

Les préimages et sessions sont en scratch privé hors dépôt, écrites et relues avant mutation/session ; seuls les noms opaques et empreintes figurent dans les reçus. L'état métier a été relu exact ; sessions, caches et activité temporaire ne sont pas une restauration octet pour octet (arbitrage du 26 novembre 2026).

## Rejouer

Depuis `C:\Users\Ced\imagine`, choisir un **nom de reçu neuf** (les reçus existants ne sont jamais écrasés) :

```text
python production/B-07/verifier.py
python wp/outils/demo/b07.py rules regles-rejeu-neuf-V2
python wp/outils/demo/b07.py runtime adaptateur-rejeu-neuf-V2
python wp/outils/demo/b07.py runtime privacy-rejeu-neuf-V2 privacy
python wp/outils/demo/b07-recette.py recette-rejeu-neuf-V2
python wp/outils/demo/b07-regression.py articles-rejeu-neuf-V2
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

La recette refuse une inscription préexistante sur ses adresses témoins plutôt que de la retirer. Le script `b07-recovery.py` est un inverse **historique**, pas une commande de rejeu : voir les notes d'incident ci-dessous.

## Écarts conservés, non rebaptisés

Le premier parcours a terminé ses inverses de données mais n'a pas pu supprimer son observateur sous `www-data` (répertoire MU non inscriptible). Retrait exact effectué par le transport propriétaire après vérification d'empreinte, puis absence relue. Une préférence UI native créée à la première visite admin (`meta-box-order_product`) a été retirée sur sa préimage d'absence ; état métier initial relu exact (`recuperation-interface-V2.json`). Le harnais fait désormais ces deux inverses.

Les reçus rouges intermédiaires restent tels quels : nom de callback C-21 mal attendu dans un test, export de liste natif oublié puis fermé avec rouge/vert réel, comparaison trop large des en-têtes Date, et nonce REST absent du test abonné. Aucun de ces rouges n'est présenté comme un résultat de livraison. Le parcours final est vert sur les sources livrées. Pas de billetterie, quota, paiement, email de confirmation ni export d'inscrits ; pas de mise en ligne ni de validation visuelle automatique.
