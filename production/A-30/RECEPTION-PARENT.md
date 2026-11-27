# A30 — réception native du 27 novembre 2026

Un seul paquet courant : `production/A-30/preuves/final/`. Les candidats et vrais échecs antérieurs restent hors dépôt dans `C:/Users/Ced/AppData/Local/hermes/cache/scratch/a30-t03-20261127/` ; aucun reçu rouge renommé vert.

## Établi par exécution réelle

- Windows `C:/Python314/python.exe`, **3.14.6** : **25 tests Python PASS en UTF-8 et 25 en cp1252**, ce dernier avec `PYTHONUTF8=0`. Les deux sondes conservent les encodages stdout/stderr/locale/preferred réels.
- Dans chaque contexte : **7 contrôles PHP purs** et **122 contrôles natifs PASS**, classique et HPOS, PHP exclusivement en conteneurs déconnectés. WordPress 7.0.9, WooCommerce 11.1.1, Subscriptions 9.4.1, Memberships 1.30.3 : banc fictif compatible, pas qualification d'Imagine 6.9.1.
- Cinq issues exactes : créer lignes 2–6, existant 7–11, sans email 12–16, type à décider 17–21, refus A13 22–26. Seuls les numéros vont à côté du CSV hors dépôt. Résumés K5 par issue/produit/paiement, aucune cellule ; les petits groupes sont fondus.
- Le lecteur strict A13 est inchangé et appelé directement. Fichiers propres/sales, IBAN et encodage sont joués en natif ; les CLI Windows comparent aussi les mêmes fichiers invalides (structure, guillemets, en-tête IBAN cassé, encodage), avec les mêmes codes et flux fermés.
- Gardien commun A22 **inchangé** : affichage normal absorbé, canaris réels stdout/stderr, arrêt précoce/silencieux/forgé, shutdown sur les flux et affichage, dépassement/UTF-8 invalide ; fichier JSON encore valide mais modifié au shutdown, clé/fichier supplémentaires et suppression refusés avant publication. Base complète et fichiers du site identiques avant/après, tentative SQL/fichier/mail/HTTP/scheduler éprouvée. Neutralisation/anonymisation réelle par l'import gelé, puis rapprochement « inconnu après neutralisation », jamais zéro ni sixième décision, avec nouvelle immutabilité.
- Commande opérateur du README exécutée avec ses seuls arguments ; arguments manquants, libres, doublés, vides et date invalide refusés. Pas d'écriture de compte/site par l'outil. Les trois options restent false ; true est refusé, aucune règle d'échéance/doublon/prochaine date implémentée.
- **PSR-12 strict : 0 erreur, 0 avertissement** sur les six PHP d'A30 ; lint natif de ces six fichiers, receipts réels. Conteneurs exacts supprimés et absence relue. Le banc réemploie le style A20, sans en modifier un contrôle.

## Corrections circonscrites

L'essai natif a réellement révélé un warning ABSPATH dans la configuration WP-CLI fictive et le mauvais aplatissement des chemins A13. Le banc A30 garde désormais leur profondeur canonique dans sa copie privée et ne garde ABSPATH que si absent dans sa configuration writable d'oracle. Configuration du sujet restaurée exactement avant les empreintes ; aucun fichier A13/A22/import modifié. PHPCS a révélé quatre erreurs et trois avertissements A30 ; seules leurs formes locales ont été corrigées, sans découpage commun.

Les **deux lignes exactes** de `README-AJOUT-2-LIGNES.txt` sont intégrées dans le vrai mode d'emploi de l'audit `wp/tests/a02-audit/README.md`, et non dans `wp/outils/bascule/README.md` comme le candidat le proposait. Contrat de ces lignes seules, jamais empreinte du document commun. Déclaration `rejeu.json` posée avant le premier sceau ; lecteur `production/A-30/verify.py` sans argument pour T03, inventaire exact puis vérificateur natif inchangé dans son rôle.

## Portes parent

Préparation d'image réellement rejouée et deux gates globales PASS après arrêt du rejeu extérieur concurrent ; les vérificateurs A21–A28 et A30 sont tous relus à 0 sans aucune écriture dans leurs paquets voisins. Logs complets et codes réels dans `preuves/final/parent/`, synthèse `parent-gates.json`. T03 y vérifie A21–A28 et A30 ; A20 est hors rejeu « declaration absente ». Première gate interrompue par disparition du conteneur, conservée hors dépôt et jamais renommée verte. Les champs pending de `candidate.json` restent le constat historique exact de la matrice.

Contexte utf-8 : REJEU : 1153 tests, 36075 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
Contexte cp1252 : REJEU : 1153 tests, 36075 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS

## Limites

Aucun accès au réel, archive Imagine, site existant, compte, Novamira, Git, voie 2 ou A29. Aucun import ni activation/invitation/Odoo. Les trois règles métier ouvertes restent chez Imagine ; le classement est un comptage seulement. L'import A28 et le gardien sont gelés, y compris style. Rapport et verrou conservés par le parent, sans libération.
