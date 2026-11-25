# Relecture indépendante — Lot C-13 (L'écran de la liste d'envoi)

Relecteur : Claude. Date : 25 novembre 2026. Brief : `briefs/C-13-ecran-liste-envoi.md`. Cahier des charges : §3.13.
Je n'ai pas ouvert `relectures/C-13/codex.md`. Pas de fusion à ce stade.

## Rejeu de la suite PHP (commande autorisée, sans argument)

Commande exécutée depuis la racine :

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1
```

Conteneur jetable, sans réseau, dépôt monté en lecture seule. Dernière ligne :

```
REJEU : 927 tests, 33680 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

**Portée réelle de ce rejeu, à ne pas confondre avec « C-13 testé ».** `rejouer.ps1` ne joue que les paquets ayant un `phpunit.xml` (`discovery.php`). Ces 927 tests sont ceux de `imagine-pilotage` (bibliothèque pure C-01/C-07/C-10) et `imagine-connecteur` (C-04). Le code C-13 vit dans le greffon `imagine-site`, qui n'a **pas** de `phpunit.xml` : **aucune ligne de `EnvoiNatif.php` ni de `ListeEnvoiAdmin.php` n'est exercée par la commande autorisée.** Les tests propres à C-13 (`wp/tests/demo/c13-runtime.php`, `wp/tests/demo/c13-http.py`) sont joués par l'outil `wp/outils/demo/c13.py` contre un WordPress de démonstration vivant (`http://192.168.129.32:8085`). Je ne les ai pas lancés : ce n'est pas la commande autorisée et la doctrine m'interdit l'accès à un site. Les chiffres « 47 assertions », « 2 destinataires », « 12/12 sans paiement » reposent donc sur le rejeu d'Hermès, que je n'ai **pas** pu vérifier de façon indépendante ; je ne juge le raccord C-13 que par lecture du code.

## 1. Conformité

- **Écran, menu, droits** — Conforme au brief. Page « Liste d'envoi » sous un parent « Imagine », capacité `imagine_exporter_liste_envoi` ou `manage_options` (`ListeEnvoiAdmin::autorise`, ligne 14). Référent et admin seulement.
- **Aperçu** — Conforme : nombre de destinataires, répartition Belgique/étranger, table des exclus avec motif (`page()`, lignes 100-123). Les motifs renvoient au vocabulaire §3.13 (suspendu, virement non validé, expiré…).
- **Export CSV à la demande, nonce, capacité, pas de fichier public** — Conforme (`exporter()`, lignes 196-221 ; `admin_post`). Format lu dans le réglage C-10 (`AdministrationFormatExport`). Protection anti-formule déléguée à C-04 (`CsvProtection`).
- **Journal** — Conforme : qui, quand (UTC), numéro, lignes, état ; une option par export, pas de purge (`preparer()`, lignes 185-192).
- **Bloquant — la livraison centrale de §3.13 n'est pas démontrée.** §3.13 et le brief exigent « l'export des adresses des abonnés qui y ont droit, **bénéficiaires des abonnements offerts et groupés compris**, figé à la clôture ». Or, d'après la production elle-même : **0 destinataire issu des profils réels C-09** (12/12 sans paiement validé), **aucun support des bénéficiaires offerts/groupés**, et les 2 seuls destinataires affichés sont des **témoins C-13 synthétiques** (`c13-postal-be`, `c13-postal-fr`). Le livrable « contenu de la liste pour les profils de C-09 » du brief n'est donc pas atteint. Hermès le reconnaît et laisse volontairement la porte stricte en échec (`--require-complete` → code 2, `recette_complete=false`).
- **Important — le numéro de démonstration a une clôture future** (DEMO-2027-T1, clôture 5 janvier 2027). L'écran affiche une « projection provisoire », pas une liste **figée à la clôture**. Le gel réel n'est prouvé que par un test synthétique à dates passées (`calculer()`), jamais par l'écran sur un numéro réellement clos.
- **Interprétation signalée (correcte).** §3.13 « Encodage sans email » dit que le compte sans email est « exclu de tous les envois », mais le brief tranche l'inverse pour la liste postale (« les abonnés sans email y figurent : ils reçoivent le magazine »). Le code suit le brief : aucun filtre sur `imagine_sans_email`, et le témoin BE sans email est bien inclus. Contradiction interne cahier/brief à reporter dans `docs/ecarts.md` (résolue par le brief, mais à tracer — doctrine §7).

## 2. Exactitude métier (déroulé à la main)

J'ai déroulé le code pur et le raccord ; je n'ai pas pu dérouler sur données réelles (site hors de portée).

- **Cas « figé à la clôture » (§3.13).** `calculer()` ignore tout relevé `observe_utc ≥ clôture` (ligne 134) ; `ListeEnvoi::etablir` ne garde que les situations `effet < clôture && enregistre < clôture` (ligne 51). Une modification d'adresse ou de statut **après** la clôture ne change pas la ligne. **Conforme.** C'est exactement ce que couvre le témoin `gel_cloture_C07_adresse_statut`.
- **Cas limite « existait avant la clôture, mais aucun relevé antérieur ».** `reason` par défaut = `historique_indisponible`, `$blocked = true` → `historique_incomplet` → export **entièrement fermé**, bouton désactivé (`page()`, ligne 136). Conforme à la prudence doctrinale (« dans le doute, fermé »). **Conforme.**
- **Cas limite « date de fin = clôture ».** `ListeEnvoi::etablir` ligne 57 : `fin <= cloture` ⇒ exclu (motif `expire`). Clôture strictement exclusive. Cohérent.
- **Exclus et motifs.** Les motifs calculés (`suspendu`, `virement_non_valide` = statut `pending`, `paiement_non_valide`, `expire`, `numero_non_du`) couvrent les cas du brief. **Mineur** : la branche `default => 'non_eligible'` (ligne 168) n'a pas d'entrée dans `motif()` (ligne 156) → libellé brut « non_eligible » affiché si jamais un abonnement éligible sans destinataire remonte comme exclu. Cas rare, affichage seulement.
- **Répartition BE/étranger.** `belgique` compté sur `pays === 'BE'`, étranger = reste (lignes 177-181). Correct, repose sur le pays de livraison.

## 3. Tests

- **Bibliothèque pure (C-07/C-10/C-04)** : bien couverte et verte dans le rejeu autorisé. L'injection de formules est testée sur cellules `= + @ - `, tabulation, retour chariot, caractères de contrôle, et round-trip CSV (`ExportCsvTest`). La déduplication, les adresses incomplètes, le pays manquant, le format C-10 sont testés (`ListeEnvoiTest`, `FormatExportTest`, `AdministrationFormatExportTest`).
- **Bloquant — le raccord C-13 n'a aucun test dans la commande autorisée.** Les règles propres à C-13 (gel natif, motifs C-09, journal, droits HTTP des 4 profils, panne de journal) ne vivent que dans `wp/tests/demo/`, hors suite PHPUnit, et ne tournent que contre un site vivant. Résultat : la commande autorisée **ne prouve rien sur C-13**. C'est aussi une entorse à la doctrine §4 (« la logique métier hors de WordPress, testable sans base ni WordPress ») : `EnvoiNatif::calculer` concentre une logique métier substantielle (gel, grâce, calcul des motifs) dans la couche couplée WordPress, au lieu de rester un raccord fin sur la bibliothèque pure — d'où l'impossibilité de la tester dans le rejeu.
- Les tests C-13 « répètent-ils la règle » ? `c13-runtime.php` vérifie surtout des présences/égalités de surface ; le vrai gel est éprouvé par `calculer()` à dates fabriquées, ce qui est honnête, mais non rejoué ici.

## 4. Sécurité et données

- **Capacité indépendante du nonce** : `verifier()` appelé avant tout, puis `check_admin_referer` (lignes 198-208). Ordre correct. **Conforme.**
- **Méthode** : export en POST uniquement (405 sinon), nonce lié au numéro (`ACTION . ':' . $code`). Bon.
- **`admin_post_nopriv_` enregistré** (ligne 36) : volontaire, pour renvoyer 403 à l'anonyme via `verifier()` plutôt qu'une redirection login. Acceptable, mais à garder à l'œil (toute régression de `autorise()` ouvrirait la route). **Mineur/technique.**
- **CSV jamais déposé dans un répertoire public** : généré en mémoire, `Content-Disposition: attachment`, `Cache-Control: private, no-store`, `X-Content-Type-Options: nosniff`. **Conforme.**
- **Injection de formule** : `CsvProtection::cellule` préfixe `'` sur `[=+@-]` après caractères de contrôle/espaces. **Conforme** (règle C-04 existante, non modifiée).
- **Aucune donnée réelle, aucun secret** : identifiants de démo hors dépôt ; adresses `@example.org` ; aucun paiement inventé. **Conforme.**
- **Mineur/technique — écriture sur lecture.** `apercu()` (lignes 94-110) appelle `relever()` sur **chaque** abonnement à **chaque** affichage de la page (GET), ce qui écrit des options `imagine_envoi_releve_*`. Idempotent (écrit seulement si les données ont changé) et protégé par la capacité, donc pas d'abus CSRF ; mais un GET qui mute la base et balaie tous les abonnements est un choix à surveiller en volume réel.

## 5. Doctrine

- **Standard d'abord** : `add_submenu_page`, `admin_post`, `check_admin_referer`, CRUD Subscriptions, Settings API — réutilisés, sources officielles citées (`references.md`). **Conforme.** Hermès signale lui-même que la consultation des docs a été tardive sur le premier tracer (procédure, pas blocage).
- **Pas de modification des bibliothèques closes** ni des adaptateurs C-10 : respecté.
- **Marqueur `PRET` contradictoire.** Le fichier `production/C-13/PRET` est présent, mais `RAPPORT.md` (ligne 2) dit « PRET retiré par le parent », tandis que `A-VOIR.md` dit « PRET redéposé ». Le lot se déclare lui-même `BLOQUE_ACCEPTATION_C09` avec `recette_complete=false`. Documentation incohérente : à clarifier. Un lot dont la recette propre sort en code 2 n'est pas « prêt » au sens d'une clôture.
- **Menu** : `menu()` remplace le parent « Imagine » pour les non-admins et retire le sous-menu d'origine. Interaction possible avec le menu de C-10 sous le même parent `imagine` — à vérifier visuellement (ressort de Ced).

## 6. Études

Sans objet (lot avec code).

## Verdict

**À corriger.**

- **Bloquant** — La livraison centrale de §3.13 n'est pas démontrée : 0 destinataire réel C-09, bénéficiaires offerts/groupés absents, et démonstration sur un numéro à clôture future (projection, pas liste figée). Le brief exige le contenu de la liste pour les profils C-09.
- **Bloquant** — Le raccord C-13 n'a aucune couverture dans la commande autorisée ; ses tests exigent un site vivant. Logique métier concentrée dans la couche WordPress au lieu de la bibliothèque pure (doctrine §4).
- **Important** — `PRET` présent alors que le lot se déclare bloqué (`recette_complete=false`, code 2) ; documentation `RAPPORT.md`/`A-VOIR.md` contradictoire sur le marqueur.
- **Important** — Le gel « à la clôture » n'est prouvé que par un test synthétique, jamais par l'écran sur un numéro réellement clos.
- **Mineur** — `motif()` sans cas `non_eligible` (libellé brut possible). Écriture de relevés sur affichage GET. `admin_post_nopriv` à surveiller.

Ce qui est positif : le code de l'écran, des droits, du nonce, de la protection CSV et du journal est propre et cohérent ; la bibliothèque pure C-07/C-10/C-04 est bien testée et verte. Le blocage est de **périmètre/données** (C-09 sans paiement validé, offerts/groupés hors scope déclaré) plus que de codage — Hermès refuse à juste titre d'inventer un paiement (doctrine §3).

Ce verdict n'est pas un GO.

### Décisions techniques, défaut proposé

1. **Tester C-13 dans la commande autorisée.** Extraire la logique de `EnvoiNatif::calculer` vers la bibliothèque pure (ou ajouter un `phpunit.xml` à `imagine-site`) pour que `rejouer.ps1` exerce le raccord sans site vivant. *Défaut proposé (à appliquer sans attendre) : le code pur reste la seule source de règles ; C-13 ne doit être qu'un adaptateur fin.*
2. **Clarifier le marqueur `PRET`** et aligner `RAPPORT.md`, `A-VOIR.md`, `resultats.json` sur un seul état. *Défaut : tant que `recette_complete=false`, pas de `PRET` affiché comme prêt à clôture.*
3. **Libellé `non_eligible`** : ajouter l'entrée dans `motif()` ou garantir que ce cas ne remonte jamais en exclusion. *Défaut : ajouter le libellé traduit.*

### Pour Imagine (métier)

- Les profils C-09 n'ont aucun paiement validé ni lien bénéficiaire offert/groupé natif. Sans l'un ou l'autre, la liste réelle reste vide et les offerts/groupés de §3.13 ne sont pas couverts. *Défaut prudent : gates fermées, aucun paiement ni rattachement inventé (doctrine §3).* Question posée par Hermès : **autoriser un complément postal C-13 explicitement fictif rattaché aux profils C-09 (validation administrative + bloc C-01 documentés), sans paiement et sans changer leurs états natifs, oui ou non ?** C'est une décision de périmètre entre C-09 et C-13 ; à reporter aussi dans `docs/ecarts.md`.

### Écarts à tracer (`docs/ecarts.md`)

- Contradiction §3.13 (« sans email exclu de tous les envois ») vs brief C-13 (« les abonnés sans email figurent dans la liste »), résolue par le brief.
- Bénéficiaires offerts/groupés de §3.13 non livrés par C-13 (dépend de C-09).
