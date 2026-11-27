# A30 — réception parent

**Périmètre écrit : uniquement `wp/outils/bascule/a30/`, `wp/tests/a30/`, `production/A-30/`. Aucun commun modifié, A13 réemployé sans mutation, A22 intact. Pas de PRET.**

## Résultat et preuves réellement exécutées

- Outil complet de simulation préparé : adaptateur A13 strict sans ses écritures, configuration fictive types→produits, PHP pur de classement, lecteur natif classique/HPOS, frontière A22, fichiers à côté de l'entrée hors dépôt, résumé K5 par issue/produit/paiement et numéros de lignes sans cellule.
- **Python réel Windows `C:/Python314/python.exe`, 3.14.6 : 22 tests réussis en UTF-8 et 22 en cp1252**, `PYTHONUTF8=0` pour cp1252 ; stdout/stderr/locale/préférence réellement mesurés. Résultats et empreintes de sources : paquet unique `production/A-30/preuves/final/`.
- RED observés avant implémentation : adaptateur A13 absent ; configuration/rapports absents ; validation/sorties privées absentes ; lanceur absent ; vérificateur absent ; digest final absent ; contrat des deux lignes absent. GREEN finaux conservés dans le paquet, pas de sortie RED fabriquée.
- Le gardien A22 a réellement supervisé des processus **Python** avec les cinq canaux stdout/stderr/affichage/shutdown-stdout/shutdown-stderr et dépassement de taille. Les tests réels des fichiers couvrent JSON valide modifié, schéma inattendu, fichier supplémentaire et digest final incohérent. **Ce ne sont pas des preuves d'exécution PHP/WordPress.**
- Le vérificateur **sans argument** a réellement renvoyé **1**, `native_proven=false`, `readiness_claimed=false` : natif absent et deux lignes communes non encore intégrées. C'est le refus attendu, pas une acceptation masquée.
- Tous les fichiers Python ont été compilés par `compile()` sans écrire de pyc. **Aucun PHP, Docker, WSL, site, compte, archive réelle ni Git n'a été exécuté/consulté.** Le verrou et les autres lots ne sont pas touchés.

## Livrables

- `wp/outils/bascule/a30/` : `confine.py`, `core.py`, `Analysis.php`, `Inventory.php`, `observer.php`, `types.exemple.json`, `README.md`.
- `wp/tests/a30/` : tests Python, `unit.php` (sept contrôles de PHP pur), `seed.php`, `neutralise.php`, `cases.py`, `inside.py`, `run.py`, `matrix.py`, `verify.py`.
- `production/A-30/README-AJOUT-2-LIGNES.txt` : **exactement deux lignes**, à ajouter **par le parent seulement** dans `wp/outils/bascule/README.md`. Le vérificateur contrôle leur présence unique, sans empreinte de l'ensemble du fichier commun.
- Le banc préparé importe les trois fichiers fictifs A13 **exacts** et étend la fixture propre dans `/scratch`, pas dans le dépôt. Ses 25 lignes d'essai couvrent cinq issues, cinq lignes chacune : créer 2–6, existant 7–11, sans email 12–16, type à décider 17–21, refus A13 22–26. Le banc vérifie aussi les 25 rejets exacts de la fixture A13 sale, l'IBAN et l'encodage refusés identiquement, le replay et la commande complète du README.

## À lancer par le parent, seulement après gel de l'import A28

Depuis `C:/Users/Ced/imagine`, dans le shell habituel. **Ces commandes natives n'ont pas été lancées par ce worker.**

```sh
# 1. Intégrer les deux lignes fournies, une fois chacune, dans le README commun.
# 2. Remplacer seulement le candidat Python incomplet et exécuter les deux matrices complètes.
C:/Python314/python.exe -B wp/tests/a30/matrix.py --refresh-python --with-native
# 3. Vérifier le paquet courant, sans argument.
C:/Python314/python.exe -B wp/tests/a30/verify.py
# 4. Préparation et replay communs du parent, avant tout PRET.
powershell.exe -NoProfile -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -File wp/tests/rejouer.ps1
```

Le runner réemploie en lecture seule le transport A02 et son image déjà épinglée, sans pull, réseau, montage ou port, avec destruction du seul conteneur qu'il possède. Il copie uniquement le code autorisé et les paquets commerciaux locaux du banc A02 déjà prévus par ce banc ; pas de site/archive de production entrant. Son import du module `run.py` n'exécute **aucun** transport : le natif n'est appelé que dans son `main()` explicite. Une exécution de PHP pur seule, facultative, est disponible pour diagnostic parent :

```sh
C:/Python314/python.exe -B wp/tests/a30/run.py --unit-only --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a30-unit-parent
```

Cette sortie doit être neuve et ne vaut pas acceptation. Pour le paquet final, conserver uniquement `preuves/final/` issu du rejeu complet. Après ce rejeu, `--refresh-python` refusera de supprimer un paquet déclaré natif ; ne pas multiplier les preuves dans le dépôt. Toute correction de code exige un paquet neuf et de nouvelles empreintes. Le parent prend ses gates et son éventuel scellement/PRET ; le worker n'en revendique aucun.

Le banc natif préparé exige, **dans les deux stockages** : sept assertions pures ; vrais comptes fictifs correspondants ; cinq canaris d'interdiction SQL/fichiers/mail/HTTP/scheduler ; canaux affichage, flux directs, sortie précoce, silencieuse ou forgée, shutdown sur les deux flux, affichage tardif, UTF-8 invalide, dépassement, **JSON valide altéré après succès**, clé libre, fichier supplémentaire et résultat supprimé ; empreintes de toutes les tables et des fichiers avant/après identiques ; neutralisation/anonymisation par le moteur d'import réellement gelé puis rapprochement inconnu et nouvelle immutabilité. Aucun reçu de ces opérations n'a été synthétisé.

## Défauts prudents et limites de contrat

1. Priorité : rejet A13 → sans email → type sans produit natif → rapprochement de compte. Le produit doit être un abonnement simple ou une variation concrète ; aucun choix d'un parent variable, titre ou prix.
2. Les comptes après neutralisation sont **inconnaissables**, pas absents. Les deux comptes/listes valent `inconnu après neutralisation`. Les numéros restants sont une métadonnée `rapprochement_inconnu`, avec issue privée null : **aucune sixième décision métier**, aucune fausse attribution « à créer ». Le README expose explicitement cette limite nécessaire au brief : une répartition exclusive en cinq issues n'est prouvable que lorsque le rapprochement est observable. À conserver dans la relecture plutôt que de transformer l'inconnu en zéro.
3. Options métier `importer_echus`, `resoudre_doublons`, `calculer_prochaine_echeance` toutes false ; true est refusé, pas interprété. Aucune règle d'import échu, de fusion ou de prochaine date n'est implémentée. L'option déjà close d'A13 sur le prénom est lue telle quelle. Un email correspondant à deux comptes du site refuse le passage ; aucun compte arbitraire choisi.
4. Les nombres désignent les **lignes du fichier**, y compris rejets, et non des créations réalisées. Les groupes <5 sont fondus sans libellé ; le fichier privé des numéros de lignes n'est pas un rapport public K5.
5. La documentation officielle standard a été consultée : import CSV natif Woo = produits ; ajout manuel Subscriptions et importeur CSV bêta séparé = écritures, pas cette simulation. Cinq lignes et sources actuelles dans le README. Aucun importeur, mot de passe, activation, invitation ou envoi Odoo n'est appelé.

Lectures effectuées : brief A30 intégral ; doctrine et consigne permanente intégrales ; décisions ; file voie 1 ; cahier §§2.3, 3.7, 3.13, 4.3 et composants utiles de §4.1. Rien de la voie 2 n'a été ouvert ni modifié. Limite restante : **syntaxe/exécution PHP, banc classique/HPOS, image et gates communs à prouver par le parent**. Aucun blocage métier n'a été maquillé en réussite.
