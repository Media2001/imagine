# Relecture indépendante Codex — A-13

Date : 26 novembre 2026. Références lues : `relecteurs/AGENTS.md`, doctrine, grille, brief A-13, cahier des charges §2.3, §3.13 et §4.3, décisions, production A-13, outil, correspondance, documentation, fixtures et tests associés. Le rapport de Claude n'a pas été consulté. Aucun code corrigé.

## 1. Conformité

Le périmètre est respecté : outil Python autonome, correspondance externe, aucun import, compte, accès réseau ou écriture dans un site. Les livrables et `PRET` sont présents. Les diagnostics ne reprennent pas les valeurs des contacts ; l'email absent est compté séparément. Les 16 empreintes du manifeste correspondent aux fichiers livrés.

**R1 — Important — `wp/outils/bascule/controler-export:231` : le prénom restreint le contrôle des doublons demandé.** Le brief demande « même nom et même adresse postale ». La clé ajoute systématiquement `prenom`, même facultatif. Reproduction en mémoire à partir des deux premières lignes de la fixture propre : rendre identiques le nom et les quatre champs postaux, garder les emails distincts, vider seulement le prénom de la deuxième ligne. Résultat : aucun rejet ni doublon. En renseignant le même prénom, les deux lignes sont signalées. Un contact dont le prénom manque dans une occurrence échappe donc au rapprochement prescrit. L'interprétation « nom complet » est bien signalée dans la livraison, mais réduit la règle du brief sans option dédiée. **Correction proposée :** comparer par défaut le champ `nom` et l'adresse normalisés ; réserver une éventuelle exigence de prénom identique à une option explicite, désactivée par défaut. Ajouter le cas du prénom absent et celui de prénoms différents aux tests.

## 2. Exactitude métier

Cas déroulés manuellement puis comparés aux fonctions exécutées en mémoire :

- **Abonné sans email, §4.3 et §3.13 :** retirer l'email d'une ligne autrement valide donne zéro rejet et un abonné sans email. Aucune adresse n'est générée. Conforme au périmètre de contrôle préalable.
- **Échéance, §4.3 :** au 25 novembre 2026, une échéance au même jour et zéro numéro dû sont acceptés. Au 1er janvier 2027, une échéance au 31 décembre 2026 produit « Date d’échéance passée ». Le 29 février 2028 est lisible ; le 29 février 2027 produit « Date d’échéance illisible ». Le code signale le défaut sans décider d'un import ni transmettre à Odoo (§2.3).
- **Doublons :** la fixture retrouve les six lignes attendues, mais le cas du prénom absent échoue au contrat décrit en R1.

**R2 — Mineur — `wp/outils/bascule/controler-export:100` : une configuration peut activer un filtre impossible à appliquer.** Avec `colonnes.type_abonnement = null`, `type_abonnement` retiré des champs obligatoires et `types_abonnement_autorises = ["numerique"]`, `lire_config` accepte la correspondance. L'analyse de la fixture propre renvoie zéro rejet, alors que le même filtre avec la colonne mappée rejette ses trente types `papier`. Le filtre déclaré actif est silencieusement inopérant. **Correction proposée :** refuser une liste de types non vide lorsque sa colonne n'est pas mappée, avec un message français ; tester cette combinaison. Le filtre vide doit continuer à permettre un champ facultatif non mappé.

## 3. Tests

Commande lancée, sans option d'écriture des preuves et avec les caches Python désactivés :

```text
python -B wp/tests/a13/verifier_livraison.py
```

**Résultat local : code 1 ; 35 tests tentés, 70 erreurs de permissions.** Chaque test échoue lors de la préparation des fichiers temporaires, puis lors de leur nettoyage, sous `C:\Users\Ced\AppData\Local\Temp\a13-test-*` (`PermissionError`, accès refusé). Les trois appels CLI supplémentaires du vérificateur ne sont donc pas atteints. Cette limitation de l'environnement ne démontre pas un défaut du lot ; je ne revendique pas un passage local de la suite. Aucun déplacement des sorties dans le dépôt ni modification du dispositif de tests pour contourner cette limite.

Les deux journaux livrés indiquent 35 tests réussis sous Python 3.11.15 ; leurs empreintes sont conformes au manifeste. Ce sont des preuves de production, distinctes de cette tentative indépendante.

Contrôles complémentaires exécutés sans fichier ajouté : chargement du module par `runpy`, lecture des fixtures fictives et appels des fonctions. Résultats retrouvés : propre = 30 lignes, zéro rejet ; défauts = 25 lignes rejetées, 25 motifs, six lignes en doublon, une sans email ; IBAN = refus de la colonne 14. Les cas de dates et d'email ci-dessus sont également vérifiés. Pour R3, `controler` a été exécuté avec lecture fictive et écriture remplacées en mémoire : cela vérifie le chemin de décision, pas l'écriture réelle des rapports.

La suite existante vérifie utilement les motifs et lignes physiques exacts, les champs multilignes, les encodages, les ambiguïtés de séparateur et plusieurs protections des sorties. Elle ne couvre pas les contre-exemples R1, R2 et R3 ; les ajouter aux tests de régression, puis rejouer la suite dans un environnement autorisant son répertoire temporaire hors dépôt.

## 4. Sécurité et données

**R3 — Important — `wp/outils/bascule/controler-export:15` : des contenus ressemblant à un IBAN passent le précontrôle.** Le motif ne tolère entre caractères que des espaces reconnus par `\s` et des tirets. Dans une colonne non mappée `Note`, la valeur fictive `ZZ00 0000 0000 0000 0000` est refusée ; la même séquence présentée comme `ZZ00.0000.0000.0000.0000`, ou séparée par des caractères invisibles U+200B, traverse `controler` avec le résultat `(0, "Contrôle terminé : 1 lignes, 0 rejet(s).")`. Le balayage du texte brut utilise le même motif et ne rattrape pas ces formes. Le brief exige un arrêt sur une ressemblance, pas seulement sur une présentation bancaire canonique. **Correction proposée :** examiner également une représentation normalisée des candidats au sein de chaque cellule, couvrant ces séparateurs et caractères de format, sans concaténer les colonnes et sans restituer de valeur. Tester le refus, la bonne colonne et l'absence de sorties pour ces variantes. La reproduction ne constate pas de fuite de valeur, mais un défaut du refus obligatoire.

Les fixtures examinées sont manifestement fictives. Les sorties ordinaires ne contiennent que des compteurs, numéros de ligne et motifs fixes. La lecture du code confirme le refus des sorties dans le dépôt et des cibles déjà présentes. Aucun accès au réel effectué. Droits WordPress, nonces, SQL et paywall : sans objet pour cet outil autonome.

## 5. Doctrine

Le choix de Python pur est expressément permis par le brief ; les conventions PHP ne s'appliquent pas. Le contrôle préalable sans WordPress correspond au besoin et ne réimplémente pas un importeur. Mode d'emploi en français, dépendances limitées à la bibliothèque standard, aucune décision de produit, d'éligibilité ou de comptabilité ajoutée.

### Décisions techniques, défaut proposé

Pour R2, refuser une configuration contradictoire plutôt que laisser un filtre déclaré actif sans effet. Pour R3, conserver un refus prudent sur les représentations normalisées suspectes et n'afficher que la position de colonne. Ces corrections techniques ne nécessitent aucun accès au réel.

### Pour Imagine

R1 relève du métier : défaut proposé conforme au brief, rapprochement sur nom et adresse même si le prénom manque ou diffère. Si Imagine souhaite réduire ces alertes, en faire un réglage explicite exigeant le prénom identique ; ne pas attendre cet arbitrage pour appliquer le défaut.

## 6. Études (lots sans code)

Sans objet : lot de code. Aucune affirmation nouvelle sur une extension externe n'est nécessaire à cette relecture.

## Verdict

**À corriger.** Ce verdict n'est pas un GO.

- **Bloquant :** aucun constat classé à ce niveau.
- **Important :** R1, doublons manqués lorsque le prénom diffère ou manque ; R3, précontrôle IBAN incomplet sur les variantes reproduites.
- **Mineur :** R2, filtre de types actif accepté sans colonne exploitable.

La suite CLI reste à rejouer dans un environnement permettant les fichiers temporaires hors dépôt ; les résultats historiques et les vérifications en mémoire ne remplacent pas ce rejeu.
