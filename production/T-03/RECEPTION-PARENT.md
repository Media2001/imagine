# T03 — correction étroite et nouvelle preuve native

La file du 27 novembre, 4 h 30 est appliquée : **A20 n'a plus de déclaration `rejeu.json`**. Son lecteur sans argument est conservé, inscrit avec l'ajout T03 dans son manifeste de métadonnées ; ses sources, contrôles et tous ses reçus natifs sont identiques aux octets antérieurs. Vérificateur A20 réellement relu à 0 avant/après ; ce n'est ni une nouvelle matrice A20 ni une requalification de ses anciens reçus.

A21–A28 restent inchangés (PRET, manifestes, journaux et preuves inclus) : aucun simple remplacement d'empreintes pour les faire passer. Les 2 524 fichiers protégés et l'inventaire sont relus identiques ; gel des propriétaires de la qualification précédente également identique. Le gardien et l'import, style compris, sont intacts. Aucun inventaire de sources ni gel de la voie 2.

## Résultat neuf, après les dernières métadonnées A20/A30

**9 paquets vérifiés, 0 échec** : A-21, A-22, A-23, A-24, A-25, A-26, A-27, A-28, A-30. Hors rejeu : A-20 (declaration absente), A-31 (journaux absents).

Commande réellement exécutée, sans modifier le collecteur ni son isolation :

```text
powershell.exe -NoProfile -ExecutionPolicy Bypass -File production/T-03/native-copy-proof.ps1 -Output C:\Users\Ced\AppData\Local\hermes\cache\scratch\a30-t03-20261127\t03-final-copy-proof02
```

Cette copie du banc de preuve appartient à T03 ; seul le calcul de sa racine et les assertions de sélection sont adaptés. Le script commun `wp/tests/t01/test-paquets-native.ps1` reste exactement à son empreinte précédente pour ne pas périmer les lots voisins. Aucun contrôle de collecteur, test métier, compteur ou drapeau d’isolation n’a changé.

Deux vrais passages de `wp/tests/rejouer.ps1` sur une copie jetable : vert avec A20 exclu, A21–A28 et A30 ; puis exactement un octet de `production/A-28/preuves/final/before/native.json` modifié. Le second annonce **un seul échec PAQUETS : A-28 PACKAGE_DRIFT**, tandis que la dernière ligne REJEU PASS et tous ses compteurs sont identiques. Les deux nettoyages exacts sont relus ; copie absente, reçu original A28 inchangé. Ce sont les logs complets `native/copy-proof/green.log` et `one-byte.log`, jamais des doubles.

REJEU : 1153 tests, 36075 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS

Préparation d’image réellement exécutée et gates globales UTF-8/cp1252 à 0 ; nouveaux contrats Windows Python 3.14.6 : 15 collecteur + 9 intégration dans chaque contexte, deux scripts de doubles à 0. Ces contrats/doubles ne sont pas la preuve native ci-dessus. T01 conserve ses deux montages RO exacts, réseau none, rootfs RO, utilisateur 65534, cap-drop ALL, no-new-privileges et limites ; inspections avant/après et absence du runner par le vrai lanceur. Lire les paquets ne rejoue pas leurs matrices natives.

## Incidents et limites honnêtes

Une gate initiale puis la première nouvelle copie ont réellement échoué après disparition du conteneur T01, pendant des rejeux indépendants de `scripts/relire.ps1`. Leurs logs restent intacts hors dépôt ; aucun script de relecture/processus tiers n’a été modifié ni arrêté. Après retour à un créneau libre, la nouvelle preuve ci-dessus est un vrai exit 0 (handle `proc_acdb95e08fb8`) ; l’ancienne copie rouge (`proc_fcb281563349`, exit 1) reste historique. Aucun résultat n’a été reconstruit.

Un seul paquet T03 courant, les anciens retirés hors dépôt sous `C:/Users/Ced/AppData/Local/hermes/cache/scratch/a30-t03-20261127/`. A30 a son unique paquet final et son PRET, déclaré avant son premier sceau ; ses 25 tests par console, 122 contrôles natifs par contexte, sept contrôles purs, six lint et PSR-12 strict verts sont relus par son lecteur sans argument. Le second lot exclu éventuel reste celui réellement annoncé, sans intégration forcée. A22 n’est pas clos par cet auteur. Aucun GO réel, archive Imagine, site/compte, Git, diagnostic A29 ou modification de l’autre voie. Verrou rafraîchi, non libéré.
