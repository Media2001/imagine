# Relecture B-10 — points de vente (Claude, relecteur indépendant)

Lot : B-10. Brief : `briefs/B-10-points-de-vente.md`. CDC : §3.14, §4.4.
Code lu : `wp/plugins/imagine-site/PointsVente.php`, `.../PointsVenteRegles.php`,
`.../tests/PointsVenteReglesTest.php`, section README B-10 ; production `production/B-10/`.
Je n'ai pas ouvert `codex.md`. Je ne fais pas la fusion.

## 1. Conformité

Le lot fait ce que le brief demande, sans ajout notable. Correspondance point par point.

- **Standard d'abord** : type natif `imagine_vente` + option non autoloadée `imagine_vente_actifs`, aucune table, aucune bibliothèque. Cinq lignes dans `NOTE.md`, sources officielles citées. Conforme à la doctrine §4.
- **Page liste + recherche** (`PointsVente.php:130` `afficher`) : formulaire, liste (nom, adresse, code postal, localité), recherche par localité ou code postal. Sans recherche, liste entière triée par localité puis nom (`PointsVenteRegles.php:30`). Conforme §3.14. La liste montre le code postal en plus des trois champs demandés : plus complet, pas un écart.
- **Chargement CSV + correspondance en config** (`PointsVente.php:191`, `importer` ligne 80) : remplace la liste, annonce pris/refusés, motif + numéro de ligne physique sans recopier la donnée (`PointsVenteRegles.php:106`). Se rejoue sans doublon à deux niveaux : doublon exact refusé dans un import (`:102`) et rejeu identique qui garde les IDs (`PointsVente.php:93`). Conforme au brief et à la doctrine (idempotence).
- **Carte** : réglage fermé `carte=0|1`, défaut `0`, valeur inconnue ramenée à `0` (`PointsVente.php:42`). À `1`, simple bloc texte « Carte non raccordée » (`:153`), aucun script/image/iframe/fournisseur. Rien d'appelé. Conforme §4.4 (pas de fond de carte par défaut, pas de tiers sans consentement). Trois lignes « carte ultérieure » présentes dans `NOTE.md`.
- **Aucun géocodage, aucun appel sortant** : aucune fonction HTTP dans le code B-10. Vérifié par lecture.
- **Personne / téléphone** : non affichés sans ligne explicite dans la correspondance (`afficher` `:143` teste la présence de la clé dans le mapping courant ; `charger` ne projette que les champs mappés). Retrait du mapping = masquage immédiat même sans réimport. Conforme à la règle « un point de vente est un commerce, pas une personne » ; pas de raccord C-21.
- **Fichier d'essai** : `commerces-fictifs.csv`, 30 lignes de données manifestement fictives (`PERSONNE_NON_MAPPEE_*`, adresses « impasse inventée »). Conforme.
- **Aucun style inventé** : aucun CSS ajouté, HTML sémantique minimal ; repose sur le squelette B-01. (Le rendu visuel reste du ressort de Ced.)

**Interprétations signalées** (bon point) : `NOTE.md` déclare les choix faits à défaut (recherche exacte sans préfixe/rayon, plafonds techniques, clés de mapping fermées). Rien n'est comblé en silence.

Un seul point d'interprétation à confirmer : le réglage import+carte est posé sur un écran dédié **Réglages → Points de vente** (`PointsVente.php:28`), et non sur l'écran C-10 clos. Hermès le signale lui-même (`A-VOIR.md`, « à confirmer en relecture »). Voir « Décisions techniques ».

## 2. Exactitude métier (déroulé à la main)

- **Localité, accents + casse (§3.14)** : requête `ETOILE-FICTIVE` → `cle()` abaisse et retire les accents → `etoile-fictive` ; égale `cle("Étoile-Fictive")`. Retourne les 5 commerces de cette localité. La forme décomposée (NFD : `e`+accent combinant) passe aussi : `strtr` laisse le `e`, puis `\p{M}` retire l'accent. Conforme. **Vérifié.**
- **Code postal exact** : `00001` → 5 commerces ; `000` (préfixe) → 0 résultat. Conforme au brief (pas de préfixe). **Vérifié.**
- **Rejeu sans doublon (IDs conservés)** : deuxième import du même CSV+mapping → `charger` rend les mêmes lignes dans le même ordre → `self::lignes() === $result['lignes']` vrai (`:93`) → retour anticipé, aucun réinsert, IDs inchangés. **Vérifié** (lecture ; le readback réel est dans les logs d'Hermès, voir §3).
- **Ligne mal formée nommée** : ligne 32 du fixture (`REFUS_DONNEE…;incomplet`, 2 colonnes contre 6) → `nombre_colonnes`, numéro 32, donnée non recopiée. **Vérifié** (numérotation physique correcte, y compris champs multi-lignes entre guillemets, cf. test `testColonnesOptionnellesEtCsvStandard`).
- **Toutes lignes refusées → liste conservée** : `importer` retourne `pris=0` sans toucher `ACTIFS` (`:83`). Ancienne liste intacte. **Vérifié.**
- **En-tête inconnu → refus, liste conservée** : `charger` lève `entete_invalide` avant toute écriture et avant la pose du verrou (`:86`) ; `ACTIFS` intact. **Vérifié.**
- **Carte OFF/ON** : OFF n'ajoute rien ; ON ajoute un bloc texte, zéro tiers. **Vérifié** par lecture.

## 3. Tests

- **Suite autorisée rejouée** (conteneur jetable, hors réseau, dépôt en lecture seule) :
  `REJEU : 1176 tests, 36417 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`
- B-10 : `PointsVenteReglesTest` = **6 tests, 27 assertions, vert**. Couvre des cas limites réels (numéros de lignes refusées, BOM + CRLF + champ cité multi-ligne, doublon + champ requis + syntaxe, fichiers/mappings invalides, recherche exacte + tri, projection du mapping + non-fuite de donnée refusée). Les tests vérifient la règle, pas le code.
- **Portée de mon rejeu** : la commande autorisée n'exécute que les règles PHP pures (`PointsVenteRegles`) et les contrôles d'outils. La **couche WordPress** (idempotence des IDs, masquage personne/téléphone, nonce, rendu carte, zéro requête tierce observée) est prouvée par les recettes d'Hermès (`recette-reception.json`, `regression-reception.log`), que j'ai lues mais **ne peux pas rejouer** sans accès au site. Ma vérification de cette couche est par lecture de code + logs, pas par ré-exécution. C'est proportionné au brief ; je le dis explicitement.
- **Écart de preuve (mineur)** : `A-VOIR.md`/README citent *1 175 tests / 36 407 assertions* ; mon rejeu frais donne *1 176 / 36 417*. Écart très vraisemblablement dû au chantier **B-11** en cours dans l'arbre (fichiers B-11 non suivis, `b11-observer.php` modifié). Les 6 tests B-10 sont inchangés. À aligner quand B-11 sera stable.
- Le bilan relève **A-32 / A32_PARTIAL_EVIDENCE**, hors B-10 (aucun fichier de ce lot touché). Signalé, pas imputable à B-10.

## 4. Sécurité et données

- Échappement systématique en sortie : `esc_html`, `esc_attr`, `esc_textarea` sur toutes les valeurs ; requête `localite` dé-slashée, tronquée, échappée (`PointsVente.php:35`, `:133`). Pas de XSS vu.
- Droits et nonce : `current_user_can('manage_options')` + `wp_verify_nonce` sur chaque POST (`:162`, `:169`). CPT **privé**, `show_in_rest=false`, exclu de la recherche ; la métadonnée `imagine_vente_ligne` n'est pas enregistrée pour REST → personne/téléphone ne fuient par aucune voie d'API.
- CSV : `is_uploaded_file`, plafond 2 Mio, UTF-8 vérifié, octets nuls refusés, fichier non ajouté aux médias ni exécuté ni conservé.
- Données : jeu entièrement fictif ; aucun secret ; aucune donnée réelle. Message d'erreur générique « aucune donnée du fichier n'est reproduite » (`:212`).
- Paywall : sans objet (données publiques).

## 5. Doctrine

- **Standard d'abord** respecté : natif WordPress, pas de réécriture de l'existant, pas de bibliothèque.
- **Logique hors WordPress** : `PointsVenteRegles` est du PHP pur testable sans base ; la couche WP est fine. Conforme §4.
- **Conventions §5** : `declare(strict_types=1)`, espace de noms `Imagine\`, préfixe `imagine_`, textes passés par les fonctions de traduction, section README présente. Conforme. Rejeu passé avec `--fail-on-warning --fail-on-deprecation` → pas de déprécié (notamment `fgetcsv` échappement vide, `escape=''`).

## Verdict

**Conforme.** Aucun point bloquant. Le lot fait ce que le brief demande, tests au vert, interprétations déclarées. Rappel : ce verdict n'est pas un GO (doctrine §6).

Points classés (tous **mineurs**) :

1. **Récupération d'une liste corrompue** — `PointsVente.php:93`. Le contrôle d'idempotence appelle `self::lignes()`, qui **lève** `RuntimeException` si un seul post actif est cassé (méta absente, type changé). Dans ce cas l'import censé *remplacer* la liste corrompue est avorté : on ne peut plus réparer par un nouveau chargement. Trigger étroit (corruption hors du flux normal), d'où « mineur ». *Correction proposée* : encadrer la comparaison `self::lignes() === …` d'un `try/catch` qui, en cas d'échec de lecture de l'ancienne liste, poursuit vers le remplacement complet au lieu d'abandonner.
2. **Ligatures/diacritiques hors table** — `PointsVenteRegles.php:18`. La table de pliage couvre les accents français usuels mais pas `œ`/`æ` ni certains diacritiques ; la recherche exacte ne les replie pas (`cœur` ≠ `coeur`). Données de démo non concernées. *Correction proposée* : au choix, compléter la table (œ→oe, æ→ae) ou laisser tel quel et noter la limite dans `NOTE.md`.
3. **Idempotence liée à l'ordre des clés du mapping** — `PointsVente.php:93`. Le `===` est sensible à l'ordre des clés : réordonner le JSON de correspondance (mêmes clés) sur un CSV identique provoque un réinsert complet (nouveaux IDs) au lieu du no-op. Bénin. *Correction proposée* : comparer après normalisation (ex. `ksort`) si l'on veut l'ordre indifférent ; sinon documenter.
4. **Posts orphelins après bascule** — `PointsVente.php:114`. Si le nettoyage de l'ancienne liste échoue après la bascule (`nettoyage_refuse`), des posts privés orphelins subsistent (non affichés, non comptés). Invisible pour le lecteur. *Correction proposée* : tolérer/journaliser l'échec de suppression plutôt que lever, ou prévoir un balayage.
5. **Micro-perf d'affichage** — `PointsVente.php:143`. `self::configuration()` (donc `get_option`) est rappelée pour chaque ligne et chaque clé facultative dans la boucle. *Correction proposée* : lire la configuration une fois hors boucle.
6. **Preuve chiffrée à aligner** — voir §3 (écart 1 175/1 176 dû à B-11).

Point prospectif (hors périmètre démo, pour mémoire) : la liaison page↔extension (`imagine_b10_page`) vit dans le seed de démo (`wp/outils/demo/b10-seed.php`). Pour la vraie mise en ligne, la création/association de la page « Points de vente » devra être un script de bascule versionné (doctrine « rejouable »). Non exigé par ce lot de démo.

## Décisions techniques, défaut proposé (Hermès applique, Claude arbitre après)

- **Écran des réglages import+carte** : garder l'écran dédié **Réglages → Points de vente**, sans toucher l'écran C-10 clos. *Défaut proposé* : rester sur l'écran dédié. Déplacer ce réglage dans C-10 n'apporte rien et rouvrirait un écran clos.
- **Point n°1 (récupération liste corrompue)** : *défaut proposé* : appliquer la correction (try/catch autour du contrôle d'idempotence) ; faible coût, améliore la robustesse de l'outil d'administration.

## Pour Imagine (question métier)

- **Étendue de la recherche** : localité/code postal **exacts** uniquement, ou faut-il un préfixe de code postal / un rayon ? *Défaut prudent proposé* : recherche exacte (le comportement actuel), insensible aux accents et à la casse. Ne pas inventer de rayon sans demande.

## Pour Ced (visuel / réel)

- Validation visuelle du rendu public (squelette B-01, capture `production/B-10/page-mobile.png`) et de l'écran d'administration. Le code n'ajoute aucun style ; l'aspect dépend du thème.
- Données et adresses entièrement fictives laissées en place sur la démo pour inspection, déclarées fictives dans `A-VOIR.md`. Rien de réel.

---

*Note de déroulé : `codex.md` existe déjà dans `relectures/B-10/` mais je ne l'ai pas ouvert, conformément à la consigne. La fusion (`corrections/B-10.md`) n'est pas faite — à réaliser dans un second temps.*
