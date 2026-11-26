# C-22 — À voir

Centre local des préférences livré sur la seule démonstration fictive ; aucun raccord Brevo, email ni double confirmation.
Prêt technique à relire ; l'habillage et la validation visuelle restent à Ced.
Défaut : aucune inscription automatique ; les profils ont retrouvé exactement leurs données initiales après la recette.

## Ouvrir

- Public : **http://192.168.129.32:8085/nos-newsletters/**. Trois lettres explicitement fictives, chacune présentée ; emplacement « Inscription aux newsletters — à venir », sans formulaire actif pour l'anonyme.
- Avec **A-PAPIER**, **http://192.168.129.32:8085/my-account/#mes-newsletters**. Trois cases décochées et « Aucun choix enregistré » après restauration. Cocher, enregistrer, recharger : choix et date UTC persistants. Décocher fonctionne également. La page publique connectée mène à ces préférences.
- Avec **A-SANSMAIL**, même compte : pas de rubrique ni de case newsletter ; une phrase explique que ce compte sans email ne propose pas ces préférences.
- Avec **E-ADMIN**, **http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-reglages** : section Newsletters dans le formulaire C10 existant. La dernière ligne vide ajoute une lettre ; un identifiant vidé la retire. Une seule principale requise ; identifiants stables, jamais recyclés. Le réglage d'inscription à la création reste **Non**.
- Export/effacement : outils natifs **Outils → Exporter/Effacer les données** de WordPress ; inventaire C21 étendu, aucun écran parallèle. La recette native transactionnelle a exporté puis effacé les préférences par leurs vrais callbacks, sans conserver ses mutations.

Identifiants uniquement dans le dispositif privé existant de la démonstration, jamais dans ce dépôt.

## Preuves courantes

- `t01-final-V2.log` : **1 102 tests, 34 454 assertions**, zéro échec/erreur/ignoré ; cinq tests C22 découverts. `preparation.log` : préparation réelle puis vérification hors ligne de l'image.
- `native-final-V2.json` : **19 contrôles**, dont choix datés, refus intercomptes/version périmée, export/effacement C21, vraie création avec les deux réglages et sans-email. Aucun email ni appel HTTP tenté par ce raccord.
- `http-final-V2.json` : **33 contrôles**, navigateur Chromium et POST réels. Ajout puis retrait d'une quatrième lettre par le formulaire C10, persistance des deux valeurs du réglage, profil qui coche/décoche/recharge, refus HTTP 403 intercomptes et nonce. Les préférences, réglages et cache de suivi de première visite sont restaurés par lignes/absences exactes ; journaux C10 append-only conservés.
- `quality-final-V2.json` : PSR12 bloquant, zéro erreur ; avertissements souples de longueur de ligne exclus (`-n`), notamment pour conserver les phrases traduisibles entières.
- Captures finales : `http-final-V2-nos-newsletters.png`, `http-final-V2-mes-newsletters.png`, `http-final-V2-sans-email.png`, `http-final-V2-reglages-newsletters.png`. Squelette sans nouvel habillage.
- `final-V2.json` et `manifest-V2.json` : sources propres, contrat successeur des fichiers partagés, relecture exacte sur site, **C09 382/382**, action **8793 pending**, souscription **101**, tous les autres états natifs préservés.

## Réseau : constat exact, pas « zéro tentative » inventé

Le parcours compte zéro tentative d'email et zéro appel HTTP issu du raccord newsletter. Les tentatives HTTP de bootstrap des extensions natives sont interceptées avant transport par la garde hors ligne : toutes ont un `WP_Error` de court-circuit ; aucun envoi n'a lieu. Chromium bloque aussi ses demandes d'avatars Gravatar avant réseau. L'observateur temporaire ne compte que ce parcours marqué et a été supprimé, absence relue. Les premiers reçus rouges restent historiques : chemin Woo supposé à tort, nettoyage de l'observateur nécessitant son propriétaire, et cache natif créé à la première visite. La recette finale lit la vraie route et restaure ce cache ; aucune preuve rouge n'est rebaptisée verte.

## Décisions prises à défaut et question Imagine

Le catalogue est une donnée (`imagine_newsletters_catalogue`), trois enregistrements fictifs, une principale. Un choix absent n'a ni date ni consentement fabriqués. Une lettre retirée disparaît des écrans mais son état historique reste exportable/effaçable ; ne jamais recycler son identifiant.

**Question fermée pour Imagine : faut-il inscrire à la principale à la création du compte, avec quel consentement explicite recueilli à cet instant ?** Défaut **Non**. La valeur **Oui**, testée mais non laissée active, porte l'origine `defaut_creation` et ne vaut jamais preuve de consentement ; une action volontaire ultérieure porte `lecteur`. Aucun statut de double confirmation ni persona inventé. Point d'accroche réservé : `imagine_newsletters_preferences_modifiees`, sans écouteur/connecteur.

## Rejouer

Depuis `C:/Users/Ced/imagine` :

```bash
python -B wp/tests/demo/c22-verifier.py
python -B wp/outils/demo/c22-unit.py relecture-c22
python -B wp/outils/demo/c22.py runtime relecture-native-c22
python -B wp/tests/demo/c22-http.py relecture-http-c22
```

Les labels de reçus sont neufs, jamais réécrits. Le premier vérificateur est en lecture seule sur le site ; les deux dernières recettes sont des mutations fictives réversibles. Aucun autre lot, site, compte réel, paiement ni règle fermée n'est modifié. Le parent conserve son verrou et décide de la clôture ; `PRET` n'est ni validation visuelle ni GO de mise en ligne.
