# A-31 — Réception exclusive

> **Reprise du 27/11, fusion de 08 h 58 : réception historique ci-dessous, pas une preuve des corrections courantes.** Ancien PRET et ancien paquet archivés hors dépôt dans `C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-fusion-1250/previous-delivery/`. Le worker a été interrompu par HTTP 401 (jeton fournisseur expiré) ; le parent reprend. Défauts proposés appliqués : quatre scalaires de liens cassés distincts exacts ; remboursement total exact, années rares cachées ; K5 maintenu sur les ventilations. Ajouts : corbeille, frontière UTC, métriques 0/1/4/5 seules et mêlées, sonde Windows sans TMPDIR. Le premier natif a trouvé une requête du banc `SELECT meta_id` incompatible HPOS ; corrigée en `SELECT 1` sans toucher au sujet commun. RED conservé dans `a31-parent-recovery-1310`. Matrice finale : `C:/Python314/python.exe -B wp/tests/a31/matrix.py --include-native --parent-serialized --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-parent-final-1320`. Résultats finaux et blocages dans le rapport de réveil ; aucun nouveau PRET avant tous les verts. Aucun import, gardien ou lanceur gelé modifié.

## Relecture indépendante sans mutation

Depuis `C:/Users/Ced/imagine`, **la seule commande de relecture A-31** :

```sh
C:/Python314/python.exe -B production/A-31/verify.py
```

Aucun argument, Docker, réseau, écriture de rapport ou reseal. Le lecteur exige le manifeste exact, les sources/dépendances courantes, les sept gates et la matrice native complète. Succès : contrôle `A31_PACKAGE_PASS`, exit 0 ; seuls les refus ont une clé `code`, conformément au parseur T-03 inchangé. Ce n'est aucune clôture indépendante ni aucun GO réel ; A-22 reste non clos par cet auteur.

## Un seul paquet, sources gelées

`production/A-31/preuves/final/` est le seul paquet natif. Essais, diagnostics, anciennes réceptions et reçu Python seul sont hors dépôt dans `C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-qualification-20261127-0604/`. La déclaration `rejeu.json`, présente avant les gates, est conservée octet pour octet : 28 journaux, sept contrôles. Les deux lignes de `readme-ajout.txt` sont présentes exactement une fois dans le README d'audit ; le contrat porte sur elles, jamais sur l'empreinte du fichier partagé entier.

Commandes de qualification finale sérielles, à la racine du dépôt :

```sh
C:/Python314/python.exe -B wp/tests/a31/matrix.py --include-native --parent-serialized --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-qualification-20261127-0604/matrix-final-02
C:/Python314/python.exe -B wp/tests/a31/verify.py --evidence=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-qualification-20261127-0604/matrix-final-02
C:/Python314/python.exe -B wp/tests/a31/gates.py --parent-serialized --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-qualification-20261127-0604/gates-final-02
C:/Python314/python.exe -B wp/tests/a31/reseal.py --parent-serialized --evidence=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-qualification-20261127-0604/matrix-final-02 --gates=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-qualification-20261127-0604/gates-final-02
C:/Python314/python.exe -B production/A-31/verify.py
```

Le reseal publie ; il n'est **pas** une vérification read-only et refuse un final/manifeste existant sans écrasement. Les runners matrice/gates écrivent aussi des preuves : ne pas les confondre avec la relecture sans argument. Toute nouvelle qualification utilise des sorties scratch neuves.

Le contrôle canonique T-03 est lancé après sceau par `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1`, avec reçus post-sceau séparés en scratch et résultat réel dans PRET/rapport de réveil. Les gates pré-sceau annoncent légitimement A-31 « journaux absents » ; la réception post-sceau doit le trouver dans `T01_RESULT.packets.lots` sans échec. Aucun manifeste/rapport historique de T-03 n'est réécrit pour son compteur dynamique.

## Contrôles natifs et limites

- Python Windows `C:/Python314/python.exe` 3.14.6 : suites complètes UTF-8/cp1252 et sondes des deux flux, locale et mode UTF-8. Quatre cellules indivisibles classique/HPOS × deux consoles, PHP exclusivement en conteneurs jetables déconnectés.
- PHP pur, doubles, inspection/empreintes du Woo/WCS réellement installé avant le sujet ; dix puis cinquante commandes, toutes natures, état inconnu, liens cassés, refund et oldest/K5. Par magasin : commande littérale documentée, 17 refus de canaux, 11 témoins observés puis détruits, JSON/Markdown encore valides mais altérés au shutdown refusés par SHA-256.
- SQL wpdb/mysqli, fichier du site, HTTP, mail, WP-Cron et quatre planifications AS refusés. Empreintes de toutes les tables, actions/logs compris, et de tous les fichiers stables après chaque inventaire nominal, clone neutralisé et K5. Vrai `Engine::neutraliser()` puis `anonymiser()` de l'import gelé sur clone fictif ; aucune simulation de cette preuve.
- Conteneurs sans réseau/montage/port, cap-drop ALL, no-new-privileges ; MariaDB par socket sans écoute TCP. Chaque absence de conteneur possédé est relue après cleanup exact. Ni PHP Windows, site réel, archive Imagine, compte externe, Git, ni voie 2.
- Les lecteurs sans argument A-20 à A-28 et A-30, avec inventaire/octets des anciens paquets et de T-03, ont leur reçu `readonly-old-packets/` en scratch. Import et gardien sont lus/empreintés seulement, aucun ancien lot resealé.

## Corrections bornées, pas de contournement

Le standard installé utilise les enums `OrderInternalStatus`/`OrderStatus` : inspection des sources et valeurs exactes, pas une ancienne chaîne littérale. Le seed WCS impose un client fictif existant et une reconduction explicitement manuelle sans passerelle. Le getter WCS journalise ses recherches inexistantes : A-31 résout le recensement natif une fois, corbeille incluse pour l'existence, puis compte les références absentes sans appeler ce chemin d'écriture ; RED observé avant correction, GREEN ensuite. La preuve de neutralisation distingue deux références numériques de trois lignes de métadonnées, dont une opaque ; les deux nombres et l'opacité conservée sont exigés. Le rendu du verdict est passé RED/GREEN contre le vrai parseur T-03 sans modifier ce dernier, le collecteur ni la déclaration.

PSR-12 strict exige zéro erreur/avertissement. Exceptions ciblées uniquement aux noms API natifs des doubles et au mélange symbole/exécution des deux scripts de fixture ; aucune exclusion dans le sujet. Les mutations RED restent scratch/conteneur.

Après neutralisation, **seul `natures` vaut « inconnu après neutralisation »**, jamais zéro : une relation d'extension sensible a réellement disparu. Années/états, orphelins sur références WCS numériques, parents des actifs, comptes manquants, remboursements/année et oldest restent lisibles sous K5, conservation structurelle mesurée. Vivant = exactement `active`, règle A-19. Oldest rare = `fusionne`, jamais la prochaine année visible. L'outil ne répare, ne rattache et ne supprime aucune commande ; aucune décision métier ni autorisation réelle.