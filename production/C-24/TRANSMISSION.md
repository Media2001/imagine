# C-24 — Contrat technique et relais

**État : BLOQUÉ, sans PRET.** Lire d'abord `A-VOIR.md` et `recovery-borned-V2.json`. Ce document n'autorise ni réel, ni email, ni déploiement autre qu'au site fictif déjà gardé.

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
