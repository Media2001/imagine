# A-32 — Réception locale du 27 novembre 2026

**Fait :** tournée de quinze inventaires, garde initiale A-05 recopiée, matrice locale complète réellement verte.
**Prêt à relire :** code, matrice locale complète et gates parent vertes ; PRET est conditionné à la réception indépendante post-sceau consignée hors paquet.
**À arbitrer par Ced :** aucune règle métier nouvelle ; un outil seul reste sa décision.
**Bloqué :** blocage initial A31_PARTIAL_EVIDENCE levé par la préparation conjointe du parent, sans changement de lecteur ; les deux collecteurs de gates ont rendu exit 0, sources stables.
**Ensuite :** scellement par seal.py puis réception indépendante avec A-31/A-32 effectivement vérifiés, sans exclusion ; PRET seulement après. Rapport de réception hors paquet dans files/rapports/ ; A-33 garde ses prérequis.

## Standard et périmètre

A-08 enchaîne déjà audit, photographies, mise à jour et nettoyage et s'arrête au premier refus. A-32 n'en exécute aucune étape : uniquement les commandes d'inventaire closes, en lecture seule, avec poursuite après refus/échec. Aucun nouveau compte métier, aucun outil clos, import, gardien ou lanceur commun modifié ; aucun Git, site réel, compte ou archive utilisé. Les 239 fichiers protégés suivis sont restés identiques.

Chemin réel imposé par le brief et conservé : `wp/outils/bascule/tournee/`, pas un nouveau dossier `a32/`. Inclus, une ligne chacun et dans cet ordre : A-10, A-11, A-12, A-15, A-16, A-17, A-18, A-19, A-20, A-21, A-23, A-24, A-25, **A-26, A-27**. Commandes exactes des README vérifiées, seuls les chemins opérateur changent. Hors tournée : A-13/A-14/A-30 (fichiers Imagine), A-29/A-31 (non clos), A-02 (audit préalable), A-03 (non-régression), A-04/A-05/A-08 (mutation), A-09 (plan opérateur), A-22 (gardien), A-28 (import gelé).

## Garde et mode d'emploi

La lecture de `.imagine-staging-verified.json` reprend exactement les trois prédicats d'A-05 (`clean.py:210–211`, lecteur A-04 borné et sans lien) : `status=verified`, `offline_verified is True`, `runtime_probe_passed is True`. Règle recopiée dans la seule tournée, sans importer l'outil de mutation, sans champ obligatoire ou format nouveau. La déclaration littérale unique `WP_ENVIRONMENT_TYPE=staging` est lue sans PHP ; production, déclaration opaque/absente ou environnement hérité production sont refusés avant tout outil. Un seul refus `A32_NOT_VERIFIED`, stdout vide, aucune sortie créée et aucune option de contournement.

Mode d'emploi courant dans `tournee/README.md` : copie vérifiée seulement, outil seul décision de Ced. **Décision technique à défaut :** le périmètre strict ne permet pas de réécrire le README commun ; ses trois lignes A-32 contractuelles sont préservées et contrôlées ligne par ligne, sans empreinte globale. Son ancienne phrase excluant A-26/A-27 reste historiquement obsolète ; la liste courante est explicitement celle du mode d'emploi local. Aucun fichier commun restructuré.

## Exécutions réelles

`C:/Python314/python.exe -B wp/tests/a32/matrix.py --output=.../a32-active-20261127/matrix-final-v2` : **exit 0**. Windows Python **3.14.6**, deux consoles mesurées UTF-8/cp1252, TMPDIR retiré à tous les fils, TEMP/TMP dans le scratch. **10 tests Python verts par console** ; **48 contrôles natifs + 6 contrôles runner par console, 108/108 PASS au total**. Classique et HPOS réellement exécutés dans chaque console, PHP exclusivement dans les conteneurs jetables déconnectés, sans montage ni port ; suppression des seuls runners possédés et absence relue.

Sur chaque magasin/console : commande du mode d'emploi copiée avec ses seuls arguments, quinze outils réels réussis avec marqueur valide ; refus globaux absent/invalide/champs invalides/production, zéro sous-processus mesuré par l'audit Python du véritable exécuteur par défaut, base et fichiers complets identiques ; doubles nommés A-10 refus/A-11 exit 255, les treize autres outils réels poursuivent ; sept canaux MU réels couverts (stdout, stderr, arrêts anticipés muet/bavard, shutdown des deux flux, fichier de rapport altéré), aucun canari publié. Un refus/échec laisse le bilan `partielle` et le protocole `A32_PARTIAL`, jamais une fausse tournée complète. Les nouveaux codes fermés A-26/A-27 restent classés « refusé ».

`wp/tests/a32/verify.py --evidence=.../matrix-final-v2` : **exit 0, A32_LOCAL_MATRIX PASS**, sans prétention de réception finale. Qualification sur copies des vraies preuves : **9/9 PASS**, dont huit falsifications refusées (preuve Python seule, cas négatif manquant, processus lancé, base modifiée, A-27 absent, faux OK re-haché, source changée, clé JSON dupliquée).

## Gates initiales et sceau final

`wp/tests/a32/gates.py --output=.../a32-active-20261127/gates-current` : **exit 1, refus conservé**. Préparation d'image exit 0 après ajout des tests ; chacun des deux rejeux exécute réellement **1 204 tests / 36 667 assertions**, zéro échec/erreur/ignoré, et **22 outils / 791 contrôles** verts. Les vérificateurs A-20/A-21/A-22/A-28 sortent 0. Mais PAQUETS nomme **A-31 `A31_PARTIAL_EVIDENCE`** (manifeste absent), A-32 étant honnêtement hors rejeu pour journaux finaux de gates absents. Le `pass=true` de la suite ne transforme pas ce rouge de paquet en vert : la gate A-32 reste FAIL.

Un seul paquet neuf dans preuves/final/, ancien et essais hors dépôt. Les refus précédents sont historiques et conservés sous qualification/gates-blocked. Le parent a suivi FINALISATION.md : candidat A-31 sorti sans perte, gates neuves A-31 et A-32 réellement vertes dans le scratch a31-a32-joint-final, aucun lecteur assoupli. Installation par les commandes propres, jamais par remplacement manuel de hash. seal.py joint les seules gates valides et calcule complete=true. Cette préparation exclut honnêtement les paquets non encore installés ; elle ne remplace pas leur réception. Un rejeu indépendant où A-31/A-32 sont effectivement vérifiés, non exclus, est exigé avant PRET ; son reçu est conservé hors des paquets scellés dans files/rapports/.

