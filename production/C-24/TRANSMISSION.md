# C-24 — Contrat technique et relais

## État courant — fusion 20 h 50 corrigée le 26 novembre 2026

**PRET technique sur preuves fraîches ; aucune clôture ni validation visuelle ni autorisation du réel.** Le nouveau paquet est `manifest-fusion2050-V2.json`, vérifié par `verifier-fusion2050-V2.py` (sans réseau). Les anciens sceaux et reçus restent immuables et historiques, pas des preuves réutilisées du produit modifié.

1. `PersonnalisationReglages` : la restauration interne n'applique pas la règle d'interdiction de réutilisation à sa propre préimage, préalablement validée. Bypass limité à un drapeau privé **et** une égalité stricte avec cette préimage ; drapeau/préimage effacés dans `finally`, readback conservé. Nouvelle saisie réservée toujours refusée. Les deux RED d'origine ont reproduit réellement le 500 et la perte du catalogue (question et choix séparés), puis les deux GREEN lisent le catalogue exact via API et SQL.
2. `Personnalisation::attributsConnecteur` ne compte que les newsletters actives avec `choix === true` et `origine === lecteur`. La vraie création C22, activée uniquement dans une transaction de test puis rollbackée, produit `defaut_creation` et reste fermée. Inconnue/absente refusées ; lecteur explicite admis avec consentement distinct et email. Aucun fichier C22 modifié.
3. README : seule une nouvelle section C24 ajoutée par patch frais, les autres conservées. Quatre classes, réglage, deux métadonnées, deux accroches et commandes documentés ; vérification par contrat de section, jamais par empreinte globale du README partagé.
4. C10 : rendu de la vraie page administrative, section unique dans le formulaire `options.php`, sous le bouton existant sans déplacement. Mutation d'absence de l'injection réellement rouge, restauration métier vraie. Deux POST supplémentaires injectent l'échec SQL du journal après retrait d'une question puis d'un choix : redirection 302/303 sans 500, message de refus, préimage exacte relue par un autre processus.
5. Compteurs actuels : **1 128 tests / 35 565 assertions / zéro échec, erreur ou ignoré ; 16 outils / 331 contrôles / zéro échec**. `preparer-image.ps1` et `rejouer.ps1` frais à code 0, logs `fusion2050-preparation-V2.log` et `fusion2050-regression-durable-V2.log`. Les anciens chiffres ci-dessous datent des reçus historiques.

Qualification fraîche : **148 contrôles nominaux et 16 mutations détectées**, aucun nominal réutilisé du paquet précédent. Fichiers `fusion2050-*.json` : 29 purs, 35 natifs, 44 HTTP Chromium/POST, 8 gardes, 32 corrections ciblées ; 7 anciennes mutations rejouées, 5 gardes, 2 restaurations, 1 origine, 1 injection C10. HTTP : 51 requêtes observées, zéro tentative mail, 70/70 tentatives HTTP WordPress bloquées, aucune de Personnalisation. Snapshots privés durables écrits/relu/hachés avant sessions et mutations ; tous les readbacks métier exacts, observateur retiré. Pas de nouvelles exigences sur anciennes sessions/caches : arbitrage de 19 h inchangé.

```bash
# Contrôle hors réseau du nouveau paquet :
PYTHONIOENCODING=utf-8 python -B production/C-24/verifier-fusion2050-V2.py
# Nouveaux parcours seulement, étiquettes inédites -V2, démo seule :
python -B wp/outils/demo/c24-corrections.py journal-question nouveau-question-V2
python -B wp/outils/demo/c24-corrections.py journal-choix nouveau-choix-V2
python -B wp/outils/demo/c24-corrections.py newsletter nouveau-newsletter-V2
python -B wp/tests/demo/c24-http.py nouveau-http-V2
```

Choix techniques à défaut : origine lecteur uniquement ; style dense laissé en l'état (pas de chantier PSR-12). Questions Imagine : localité fermée et exclusion de l'inscription par défaut. Questions Ced : position inchangée et éditeur JSON. Aucun besoin de modifier bootstrap, C21/C22/B06/B07, bibliothèque close, rôle ou autre site. Aucun email extérieur, donnée réelle, Git ou installation hôte.

Incident de chemin privé : `TMPDIR` hérité pointait hors du scratch attendu ; les préimages ont été retrouvées **intactes par SHA-256**, pas reconstituées, puis copiées en durable dans le scratch Hermes (`fusion2050-prives-V2.json`). Le HTTP final et les recettes ciblées/gardes finales fixent désormais leur racine privée avant toute mutation, sans dépendre de ce `TMPDIR`. Un second batch a atteint la limite de l'outil après ses contrôles ciblés et ses cinq gardes terminés ; le paquet garde les sept mutations historiques déjà entièrement vérifiées du premier batch, pas le batch partiel. Aucune mutation nécessaire n'est supposée terminée.

Incident de banc non produit : invoquer tout `admin_init` en WP-CLI sans chargement d'écran Woo déclenchait une fonction d'administration absente. Le harnais exécute désormais le vrai callback d'enregistrement C24 seulement ; la page administrative complète est testée séparément par HTTP. Aucun faux RED métier compté pour cet incident.

---

## Historique — qualification précédente, remplacée par le paquet fusion2050


**État courant : PRÊT pour relecture technique depuis une baseline récupérée explicite.** `A-VOIR.md` décrit les portes finales ; `manifest-final-V2.json` lie leurs reçus aux sources, et `verifier-V2.py` les vérifie hors réseau. L'incident initial reste documenté et `recovery-borned-V2.json` reste inchangé. Ce document n'autorise ni réel, ni email, ni autre site.

## Reprise finale V2

- Le snapshot privé durable du HTTP final a été écrit, `fsync`, relu et haché **avant** toute session. Il est conservé dans le scratch privé ; le reçu n'expose qu'un identifiant opaque et SHA-256. La restauration relit ses octets. L'état récupéré est une **nouvelle référence**, jamais la récupération du snapshot initial perdu.
- `http-metier-final-V2` : 38 contrôles navigateur/POST verts, état métier restauré. Le rouge intermédiaire lié au timeout d'un cache reste conservé ; seuls transients/cache et verrou AS sont exclus de la comparaison métier. Les anciennes sessions historiques ne sont pas reconstruite.
- `mutations-qualifiees-V2` : 8 contrôles natifs verts, 5 mutants réels détectés, gardes de question et de choix isolées ; consentement/newsletter/email testés séparément. Copies de classes en mémoire, transactions annulées, readbacks distincts. Le mutant masqué intermédiaire reste conservé.
- Les 64 contrôles et 7 mutations de la livraison partielle sont réutilisés uniquement si leurs classes et tests sont strictement identiques par empreinte. Aucune réexécution inutile ni verdict historique modifié.
- Préparation officielle d'image et régression rejouées : code 0 ; 1 126 tests/35 550 assertions, 16 outils/311 contrôles, aucun échec.
- Aucun fichier produit, bibliothèque close, C23/B06 ou bootstrap partagé modifié pendant cette reprise. Seuls harnais C24 et dossier de preuve évoluent. Les scripts de récupération historique restent hors rejeu.

Commandes de contrôle :

```bash
PYTHONIOENCODING=utf-8 python -B production/C-24/verifier-V2.py
# Pour une NOUVELLE qualification seulement, étiquettes inédites -V2 :
# python -B wp/tests/demo/c24-http.py <nouvelle-etiquette-V2>
# python -B wp/outils/demo/c24-mutations.py <nouvelle-etiquette-V2>
```

Questions visuelles à Ced et localité en choix fermés pour Imagine : conservées dans `A-VOIR.md`, non arbitrées par le code.

**Les sections ci-dessous conservent le relais initial ; leur « à terminer » est historique et remplacé par la qualification ci-dessus.**

## Fichiers et standard

Quatre classes nouvelles dans `wp/plugins/imagine-site/` :

- `PersonnalisationRegles.php` : validation PHP pure d'un catalogue fermé ; transitions de réponses datées ; conjonction consentement explicite ET newsletter ET admissibilité email.
- `Personnalisation.php` : trois formulaires indépendants dans le dashboard WooCommerce, garde compte courant/nonce/version, verrou par compte, métadonnées natives et projection des attributs admissibles.
- `PersonnalisationReglages.php` : raccord additif dans le même formulaire Settings API C10 ; journal natif ; réserves non personnelles des identifiants, y compris historiques et au retrait de métadonnées.
- `PersonnalisationConfidentialite.php` : callbacks supplémentaires aux listes natives d'export/effacement, et réservation avant suppression native d'un compte. C21 ne change pas.

Seul raccord partagé modifié : le bloc additif de huit lignes de `imagine-site.php`. Aucune bibliothèque close, aucun thème, aucun lot C23/B06 réécrit. Le schéma ne nécessite pas de table ni d'extension nouvelle. Les réglages, métadonnées, nonces et callbacks de confidentialité restent natifs ; seules les règles propres aux questions et aux étiquettes sont ajoutées.

Références officielles vérifiées (WordPress Plugin Handbook) :

```text
https://developer.wordpress.org/plugins/settings/settings-api/
https://developer.wordpress.org/plugins/privacy/adding-the-personal-data-exporter-to-your-plugin/
https://developer.wordpress.org/plugins/privacy/adding-the-personal-data-eraser-to-your-plugin/
```

## Données

- Catalogue : `imagine_personnalisation_questions`.
- Réponses : `imagine_personnalisation_reponses`, indexées par identifiant de question ; chaque valeur contient `choix` (liste d'identifiants) et `date_utc`.
- Consentement séparé : `imagine_personnalisation_consentement`, avec `accord` booléen et `date_utc`. Répondre ne le crée pas ; le retirer ne touche pas aux réponses. Effacer les réponses ne retire pas l'accord : deux opérations indépendantes, visibles.
- Réserves : options `imagine_personnalisation_reserve_q_*` et `imagine_personnalisation_reserve_c_*`, valeur technique `1`, sans identité. Les choix ont des identifiants uniques dans l'ensemble du catalogue ; un choix actif ne peut pas changer de question. Le catalogue courant, les réponses historiques et le journal C10 alimentent ces réserves. Elles survivent à l'effacement personnel ; aucune réponse historique ne devient un attribut d'une autre question.
- Le retrait d'une question la masque sans réattribuer ses anciennes réponses ; « Effacer toutes mes réponses » supprime aussi cet historique. L'export natif l'inclut tant qu'il subsiste.
- Compte sans email : réponses locales possibles, aucune case de consentement ni attribut transmissible. Aucun contrôle d'accès aux articles modifié.

Exemple de champ « Choix fermés (JSON) » dans C10 :

```json
[{"id":"choix-entierement-fictif","titre":"Choix entièrement fictif"}]
```

## Accroches, sans écouteur

- `Imagine\Site\Personnalisation::attributsConnecteur($id)` : seul accès prévu aux attributs pour le futur connecteur, projection relue et filtrée par les trois conditions ; les métadonnées brutes ne doivent jamais être envoyées.
- `imagine_personnalisation_attributs_modifies` : notification nommée, émise uniquement avec des attributs admissibles ; aucun écouteur livré.
- `imagine_personnalisation_apres_inscription_achat` : emplacement nommé pour le futur tunnel, non raccordé.

Pas de client Brevo, d'appel Odoo, de rappel email ni d'action planifiée nouvelle. Une future synchronisation devra aussi traiter ses propres suppressions d'attributs et relire les conditions à l'instant de l'envoi ; aucun connecteur n'est livré ici.

## Commandes et preuves

Depuis `C:/Users/Ced/imagine`, bash Windows, Python existant :

```bash
# Déjà exécuté : 64 contrôles nominaux verts, 7 mutations attendues rouges.
# Retour 0 = paquet PARTIEL constitué, PAS une acceptation de livraison.
PYTHONIOENCODING=utf-8 python -B wp/outils/demo/c24-recette.py livraison-partielle-V2
```

Le nom du reçu est immuable : pour rejouer, choisir une **nouvelle** étiquette finissant par `-V2`, jamais réutiliser celle-ci. Résultat conservé : `production/C-24/livraison-partielle-V2.json`, explicitement `result: BLOCKED`, `pret: false`.

Règles pures : conteneur Docker existant, réseau `none`, racine et dépôt en lecture seule, utilisateur non privilégié, suppression du seul conteneur créé vérifiée. Natif : WordPress réel du seul site gardé, transaction avec rollback et readback métier par processus distinct. Mutations : case sans email injectée, écouteur ajouté, tentative de mail bloquée, tentative HTTP bloquée, export vide, tiers ajouté à l'export, effacement remplacé par une non-opération. Sept contrôles deviennent effectivement rouges.

Le premier parcours HTTP, ses captures et son diagnostic restent historiques. `c24-recovery.py` et `c24-recovery-plan.py` ne font **jamais** partie du rejeu courant : reprise unique déjà exercée, coordonnées propres à cet incident, pas un outil de nettoyage générique.

## À terminer avant PRET

1. Ne pas prétendre retrouver le snapshot initial perdu : les anciennes sessions/option-verrou AS/caches de ce premier HTTP restent non prouvables. Les empreintes natives métier sont revenues à la référence, ce qui est un résultat distinct.
2. À la reprise, la nouvelle version `wp/tests/demo/c24-http.py` persiste un snapshot privé dans le scratch avant toute session, garde les identifiants hors dépôt et restaure uniquement les clés modifiées constatées. Elle est corrigée mais **non requalifiée** ; ses échecs conservent le snapshot pour reprise. Exemple de nouvelle étiquette : `http-reprise-V2`.
3. Compléter les mutations spécifiques aux gardes de réutilisation d'identifiants et à la conjonction de consentement ; les huit combinaisons booléennes passent déjà dans les règles pures.
4. Rejouer la suite générale sans toucher à ses sources closes ; repréparer l'image par `wp/tests/preparer-image.ps1` avant tout PRET, selon la consigne permanente. Aucun paquet Composer ni outil hôte n'a été installé pendant C24.
5. Produire un nouveau reçu complet lié aux sources finales, puis seulement décider du PRET. La validation visuelle reste à Ced.

Question pour Imagine : si la future localité doit être du texte libre, le confirmer explicitement. Défaut appliqué : choix fermés exclusivement. La présentation JSON de l'éditeur C10 est un squelette technique, pas une validation d'ergonomie par Ced.
