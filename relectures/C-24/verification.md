# Vérification C-24 — second et dernier tour

Vérificateur indépendant. Base : `corrections/C-24.md` (fusion, verdict « À corriger »), relu contre le code actuel. Méthode : `git diff` de la version relue (`7c4124ff`, 20:43, juste avant l'écriture de `relectures/C-24/claude.md` à 20:46) jusqu'à `HEAD`, sur `wp/` et `production/C-24`, puis rejeu des contrôles autorisés. Ce verdict n'est pas un GO (doctrine §6).

Les deux fichiers produit C-24 ont été figés au commit `579f1c0d` (21:18 local) ; la régression conteneur et les recettes démo ont tourné après. Empreintes SHA-256 des quatre classes produit **identiques** entre les preuves démo et les fichiers actuels (`PersonnalisationReglages` c0ca6b…, `Personnalisation` 649f66…, `PersonnalisationRegles` 100fea…, `PersonnalisationConfidentialite` 4b101d…) : les preuves portent bien sur le code final.

## 1. État des instructions de la fusion (§4)

La fusion liste **cinq** instructions. R3 (PSR-12) n'en fait pas partie : il est explicitement reporté en « Décisions techniques » (laisser en l'état, chantier de style global). Les « À arbitrer » sont des questions, pas des corrections.

| # | Instruction | État | Fichier : ligne |
|---|---|---|---|
| 1 | Réparer la restauration de `journal()` (R1), séparer restauration interne et validation d'une nouvelle saisie, relire l'état restauré ; + 2 tests (retrait question ET choix) vérifiant le retour effectif à `$old` et l'absence de 500 | **Appliquée** | `wp/plugins/imagine-site/PersonnalisationReglages.php:47-50` (bypass sous drapeau `$restoring` + préimage, égalité stricte) et `:147-157` (préimage vérifiée, `wp_die` si préimage ≠ `$old`, relecture de l'état restauré). Tests : `wp/tests/demo/c24-corrections.php:60-76` (cas `journal-question` / `journal-choix`) + 2 vrais POST `options.php` dans `wp/tests/demo/c24-http.py:146-160` |
| 2 | Resserrer la porte « inscrit à au moins une newsletter » (R2) : ne compter qu'une origine `lecteur`, exclure `defaut_creation` et inconnue ; + tests | **Appliquée** | `wp/plugins/imagine-site/Personnalisation.php:51-55` (`($preference['origine'] ?? null) === 'lecteur'`). Tests : `wp/tests/demo/c24-corrections.php:77-92` (création défaut ferme la projection ; boucle `defaut_creation` / `inconnue` / absente / `lecteur`) |
| 3 | Compléter `README.md` (rôles des classes, réglage C-10, métadonnées, accroches, commandes de test en distinguant local et démo) | **Appliquée** | `wp/plugins/imagine-site/README.md:339-370` (section « C-24 — personnalisation facultative locale », bloc local hors réseau vs bloc nécessitant `imagine-test-demo`) |
| 4 | Ajouter un test d'intégration de l'injection C-10 : rendre la vraie page de réglages et vérifier `id="imagine-personnalisation-reglages"` entre l'ouverture du formulaire et `</form>` | **Appliquée** | `wp/tests/demo/c24-http.py:146-148` (contrôle `C10_vraie_section_entre_ouverture_et_fermeture`, vraie page `options.php`) + mutation témoin `c10-section` dans `wp/tests/demo/c24-observer.php:18-27` qui retire l'injection |
| 5 | Rafraîchir les compteurs de tests dans `A-VOIR.md` et `TRANSMISSION.md` (1128 / 35565) | **Appliquée** | `production/C-24/A-VOIR.md:11` et `production/C-24/TRANSMISSION.md:11` (« 1 128 tests / 35 565 assertions ») |

**Les cinq instructions sont appliquées.**

## 2. Résultat des tests

Exécution autorisée au vérificateur : tests du lot en local. Contrainte de session : le mode de permission de cette session bloque toute exécution Docker / WSL / PHP / PowerShell imbriqué (garde-fou d'approbation, **non** une limite de doctrine). Je n'ai donc pas pu relancer moi-même `wp/tests/rejouer.ps1` ni les recettes démo (qui exigent de toute façon le site `imagine-test-demo`, interdit sans GO). Deux appuis compensent :

- **Rejeu que j'ai lancé** : `production/C-24/verifier-fusion2050-V2.py` (hors réseau, sans site, sans conteneur) → `{"result":"PASS","checks":318,"positive_checks":148,"detected_mutations":16,"PRET_eligible":true}`. Ce vérificateur relit toutes les preuves démo, contrôle les empreintes de source et exige que chaque mutation témoin soit bien détectée.
- **Preuve de régression d'Hermès, inspectée** : `fusion2050-regression-durable-V2.json` → exit 0 ; **1128 tests, 35565 assertions, 0 échec / 0 erreur / 0 ignoré** ; 16 outils / 331 contrôles / 0 échec ; conteneur `network=none`, rootfs ro, montage ro. Horodatage 20:47 UTC = **21:47 local**, soit après le gel du code C-24 (21:18) : elle couvre l'état final. Réserve : la suite pure du conteneur ne contient **aucun** test de `Personnalisation*` (recherche : zéro occurrence) ; toute la couverture C-24 vit dans les recettes démo.

Validité de la couverture C-24 (preuves démo, empreintes de source identiques aux fichiers actuels) :

- **R1** — vert `fusion2050-final-question-V2.json` : échec du journal réellement injecté (`journal_inserts_refused:1`), `aucun_500_reel`, `preimage_restauree_exacte`, `readback_SQL_preimage_exacte`, `erreur_journal_signalee`, `nouvelle_saisie_reservee_toujours_refusee` tous vrais, exit 0. Mutation `restauration` (`fusion2050-final-mut-question-V2.json` / `-choix`) : réapparition exacte du défaut décrit par Codex (`dies:[500]`, préimage non restaurée, relecture SQL fausse, erreur non signalée). Le correctif est porteur.
- **R2** — vert `fusion2050-final-newsletter-V2.json` : `vraie_creation_defaut_projection_fermee`, `origine_defaut_creation`/`_inconnue`/`_absente` ferment, `origine_lecteur` ouvre, `lecteur_sans_consentement_ferme`, exit 0. Mutation `origine` (`→ true`) : réouverture de la projection sur `defaut_creation`/inconnue/absente. Le correctif est porteur.
- **Instruction 4** — vert `fusion2050-http-durable-V2.json` : `C10_vraie_section_entre_ouverture_et_fermeture` vrai sur la vraie page C-10, plus les deux POST réels `journal_question_POST_reel_sans500` / `journal_choix_POST_reel_sans500` et préimage relue distincte. Mutation `c10-section` : tue ce seul contrôle. Le test est porteur.

Bilan : **vert**, aux conditions ci-dessus. Je n'ai pas pu produire un rejeu Docker neuf de ma main ; je m'appuie sur le vérificateur hors réseau (lancé, PASS) et sur la preuve de régression d'Hermès (inspectée, exit 0), toutes deux liées au code final par empreinte.

## 3. Régressions et modifications non demandées

- **Aucune régression visible dans le périmètre C-24.** Les fichiers C-24 (`Personnalisation.php`, `PersonnalisationReglages.php`, `README.md`, docs `production/C-24`) sont modifiés exactement selon les cinq instructions.
- **Micro-refactor lié à R2, non une régression** : `attributsConnecteur` met désormais `Newsletters::preferences($id)` en cache hors de la boucle (`Personnalisation.php:50`) au lieu d'un appel par itération. Amélioration raisonnable, portée par le même correctif, couverte par les preuves vertes.
- **R3 (PSR-12, lignes multi-instructions) non appliqué : conforme à la fusion**, qui l'a délibérément reporté comme chantier de style global. Rien à corriger ici.
- **Hors périmètre C-24 — à signaler, non jugé ici** : le `git diff` depuis la version relue touche de nombreux autres lots en parallèle (bascule a23→a27, démo b07, templates `themes/imagine` évènement, et dans `imagine-site` les classes `Agenda*` + `AgendaAdapterTest`/`AgendaWPStubs`). Ces changements appartiennent à d'autres lots, pas à la correction C-24 ; ils n'altèrent pas les fichiers C-24 et sortent du cadre de cette vérification. Ils relèvent de leurs propres relectures.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les cinq instructions de `corrections/C-24.md` sont appliquées ; R1 et R2 — les deux points de fond — sont corrigés, couverts par des tests verts et prouvés porteurs par mutation témoin, sur un code dont les empreintes correspondent aux preuves. Aucun problème de fond restant, aucune régression dans le périmètre C-24.

Rappels (doctrine §3 et §6) : ce verdict ne vaut que pour la clôture du code. Restent à Ced la **validation visuelle** (placement des sections Mon compte C-22/C-24 et de la section C-10) et deux **questions métier** ouvertes posées dans la fusion §5 (localité en choix fermés ; une préférence newsletter `defaut_creation` doit-elle rester exclue de la transmission). Le défaut prudent appliqué par Hermès (origine `lecteur` seule, localité fermée) est le bon tant que Ced n'a pas tranché. Aucun déploiement ni accès réel autorisé.
