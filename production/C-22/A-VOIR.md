# C-22 — À voir

Centre local des préférences livré sur la seule démonstration fictive ; aucun raccord Brevo, email ni double confirmation.
Corrections du 26 novembre 2026 prêtes techniquement à relire ; l'habillage et la validation visuelle restent à Ced.
Défaut : aucune inscription automatique ; les profils ont retrouvé exactement leurs données initiales après la recette.

## Ouvrir

- Public : **http://192.168.129.32:8085/nos-newsletters/**. Trois lettres explicitement fictives, chacune présentée ; emplacement « Inscription aux newsletters — à venir », sans formulaire actif pour l'anonyme.
- Avec **A-PAPIER**, **http://192.168.129.32:8085/my-account/#mes-newsletters**. Trois cases décochées et « Aucun choix enregistré » après restauration. Cocher, enregistrer, recharger : choix et date UTC persistants. Décocher fonctionne également. La page publique connectée mène à ces préférences.
- Avec **A-SANSMAIL**, même compte : pas de rubrique ni de case newsletter ; une phrase explique que ce compte sans email ne propose pas ces préférences.
- Avec **E-ADMIN**, **http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-reglages** : section Newsletters dans le formulaire C10 existant, **toujours sous le bouton Enregistrer**, sans déplacement. La dernière ligne vide ajoute une lettre ; un identifiant vidé la retire. Une seule principale requise ; un identifiant retiré est désormais **refusé par le code**, pas seulement déconseillé. Le réglage d'inscription à la création reste **Non**.
- Export/effacement : outils natifs **Outils → Exporter/Effacer les données** de WordPress ; inventaire C21 étendu, aucun écran parallèle. La recette native transactionnelle a exporté puis effacé les préférences par leurs vrais callbacks, sans conserver ses mutations.

Identifiants uniquement dans le dispositif privé existant de la démonstration, jamais dans ce dépôt.

## Preuves courantes — corrections V2

- `correction-t01-V2.log` : **1 123 tests, 34 569 assertions**, zéro échec/erreur/ignoré ; les cinq tests PHPUnit C22 sont découverts. **14 outils, 279 contrôles**, zéro échec. `correction-preparation-V2.log` : préparation réelle de l'image après ajout des nouveaux parcours, puis vérification hors ligne ; code 0.
- `correction-final-retired-V2.json` : **9 contrôles** ; vrai choix lecteur, retrait, refus de recyclage, écrans sans réattribution, historique intact, réserve durable même sans catalogue ni préférences.
- `correction-final-history-V2.json` : **8 contrôles** ; ancien choix hors catalogue, effacement avant/après édition et lettre connue uniquement par un ancien journal C10 : tous les identifiants restent réservés.
- `correction-final-utf8-V2.json` : **6 contrôles** ; titre accentué de 150 caractères et présentation de 500 acceptés, bornes 151/501 refusées.
- `correction-final-privacy-V2.json` : **6 contrôles** sur les vrais callbacks C21 : un choix historique retiré est exporté exactement puis réellement effacé. Les mutations `correction-mutation-export-V2.json` et `correction-mutation-erase-V2.json` sont **rouges attendues** : une omission d'export ou un effaceur sans effet sont détectés. Aucun fichier partagé de confidentialité n'a été modifié.
- `correction-native-V2.json` : **19 contrôles**, vraie création, choix datés, refus intercomptes/version périmée et confidentialité. Nouveaux parcours spécifiques dans `wp/tests/demo/`, exécutés séparément de PHPUnit ; ils ne gonflent pas ses compteurs.
- `correction-http-rejeu-V2.json` : **40 contrôles**, Chromium et POST réels : présence C10 et position sous le bouton, quatrième lettre choisie puis retirée, recyclage refusé avec erreur visible, aucun ancien choix réattribué. Préférences, réglages, réservations et cache de première visite restaurés par lignes/absences exactes ; journaux C10 append-only conservés.
- `correction-quality-V2.json` : PSR12 des trois sources Newsletters et du test PHPUnit préexistant, zéro erreur ; avertissements souples de longueur de ligne exclus (`-n`). Les nouveaux parcours PHP sont aussi exécutés réellement par WP-CLI.
- Captures : `correction-http-rejeu-V2-nos-newsletters.png`, `correction-http-rejeu-V2-mes-newsletters.png`, `correction-http-rejeu-V2-sans-email.png`, `correction-http-rejeu-V2-reglages-newsletters.png`.
- `correction-gates-V2.json`, puis `correction-final-V2.json` / `correction-manifest-V2.json` : sources propres, export/effacement contrôlés par comportement et non par syntaxe, **C09 382/382**, action **8793 pending**, souscription **101**, profils et action relus exacts. Les **39 reçus historiques** photographiés dans `correction-baseline-V2.json` sont conservés octet pour octet ; les anciens `final-V2.json` / `manifest-V2.json` ne sont pas réécrits.

## Réseau : constat exact, pas « zéro tentative » inventé

Le parcours compte zéro tentative d'email et zéro appel HTTP issu du raccord newsletter. Les tentatives HTTP de bootstrap natives sont interceptées avant transport par la garde hors ligne ; Chromium bloque ses demandes Gravatar. L'observateur temporaire a été supprimé et son absence relue. Les reçus rouges sont conservés, notamment `correction-http-V2.json` : son unique contrôle rouge venait d'un sélecteur d'erreur supposant une ancienne classe CSS WordPress. Le rejeu vert vise l'identifiant réel de l'erreur Settings API, sans modification du code métier ni affaiblissement du refus.

## Décisions prises à défaut et question Imagine

Le catalogue est une donnée (`imagine_newsletters_catalogue`), trois enregistrements fictifs, une principale. Un choix absent n'a ni date ni consentement fabriqués. Les réservations `imagine_newsletters_reserve_<identifiant>` ne contiennent que `1`, aucune identité ni date de lecteur. Le nettoyage réserve les lettres actives ainsi que les identifiants des préférences et journaux C10 historiques ; le hook préalable à l'effacement réserve aussi un ancien choix avant sa disparition. Une lettre retirée disparaît des écrans mais son état personnel reste exportable/effaçable ; son identifiant reste refusé même après effacement. Aucun schéma de table nouveau. Un historique illisible ferme prudemment l'édition du catalogue.

**Question visuelle pour Ced :** conserver la section sous le bouton Enregistrer, ou la déplacer au-dessus ? Aucun déplacement dans cette correction.

**Question fermée pour Imagine : faut-il inscrire à la principale à la création du compte, avec quel consentement explicite recueilli à cet instant ?** Défaut **Non**. La valeur **Oui**, testée mais non laissée active, porte l'origine `defaut_creation` et ne vaut jamais preuve de consentement ; une action volontaire ultérieure porte `lecteur`. Aucun statut de double confirmation ni persona inventé. Point d'accroche réservé : `imagine_newsletters_preferences_modifiees`, sans écouteur/connecteur.

## Rejouer

Depuis `C:/Users/Ced/imagine` :

```bash
python -B wp/tests/demo/c22-verifier.py
python -B wp/outils/demo/c22-unit.py relecture-c22
python -B wp/outils/demo/c22.py runtime relecture-native-c22
python -B wp/tests/demo/c22-http.py relecture-http-c22
```

Les labels de reçus doivent être neufs, jamais réécrits. Le premier vérificateur inclut désormais une **sonde transactionnelle réversible** des vrais callbacks d'export/effacement C21 ; rollback et relecture exacte des profils/options sont obligatoires. Les deux dernières recettes sont également des mutations fictives réversibles. Nouveaux cas ciblés : `python -B wp/outils/demo/c22-corrections.py <label-neuf> retired` (ou `history`, `utf8`, `privacy`). Aucun autre lot, site, compte réel, paiement ni règle fermée n'est modifié. Le parent conserve son verrou et décide de la clôture ; `PRET` n'est ni validation visuelle ni GO de mise en ligne.
