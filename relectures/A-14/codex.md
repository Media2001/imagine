# Relecture indépendante Codex — A-14

Date : 26 novembre 2026. Références : `relecteurs/AGENTS.md`, doctrine, grille, brief A-14, décisions et cahier des charges §3.10 et §4.3 ; §3.13 consulté pour les comptes sans email. Rapport Claude non consulté.

## 1. Conformité

Le périmètre fonctionnel demandé est présent : rapprochement par email seulement, correspondance configurable, lecture CSV réemployée d’A-13, lecture du site par A-11, protection des sorties par A-12, rapports séparés, tests et mode d’emploi. Aucun appel à Brevo ni mécanisme de réinscription. Un seul paquet de preuves est livré.

Les restrictions et interprétations sont explicites dans le mode d’emploi : conversion du tableur en CSV, abonnement actif limité à l’état natif `active`, statut non reconnu conservé comme `inconnu`, plusieurs comptes au même email traités comme une ambiguïté, doublons comptés par lignes concernées. Les colonnes coopérateur et tarif restent vides. Ces choix ne créent aucun droit ni consentement.

## 2. Exactitude métier

Déroulement manuel du code et comparaison avec les sorties fictives classic et HPOS :

| Cas | Résultat attendu et constaté |
|---|---|
| Lignes 2 et 3 : même email après suppression des espaces et changement de casse, seconde ligne désinscrite | Deux lignes rapprochées et signalées comme doublons ; abonnement actif sur les deux ; la ligne 3 reste `desinscrit`. |
| Ligne 4 : contact bloqué, abonnement annulé | Ligne rapprochée, abonnement `non`, statut `bloque` conservé. |
| Ligne 6 : compte marqué sans email | Aucun rapprochement ni adresse technique dans les sorties ; le compte est exclu des comptes sans contact. |
| Ligne 11 : deux comptes au même email normalisé | Une anomalie d’ambiguïté, aucun compte choisi et aucun statut d’abonnement attribué. |

Les lignes 7 et 8 sont correctement invalides. Les variantes avec suffixe `+tag` ou point ne sont pas assimilées à une autre adresse. Le total se décompose en 4 lignes rapprochées, 23 sans compte, 2 invalides et 1 ambiguë, soit 30. Les 7 comptes sans contact sont cohérents avec l’exclusion des comptes techniques, invalides et des comptes du groupe ambigu présent.

Le rejeu identique est couvert dans les preuves. Les dates de clôture et changements d’année ne pilotent pas ce lot : il photographie un état d’abonnement, sans calcul d’échéance.

## 3. Tests

- **Exécuté** : `python -B wp/tests/a14/verify.py production/A-14/preuves/final` — code 0, **13 contrôles sur 13 réussis**.
- **Exécuté en lecture seule** : lecture de la fixture avec le véritable `read_contacts` — 30 lignes, numéros physiques 2 à 31, désinscription et blocage conservés. Vérification des empreintes du manifeste de livraison : **62 fichiers conformes**.
- **Tenté** : `python -B wp/tests/a14/test_input.py`, avec `TMPDIR` dirigé vers le répertoire temporaire Windows. Le test statique du transport UTF-8 passe ; les deux méthodes utilisant des fichiers temporaires échouent avec `PermissionError` dans le bac à sable, avant de vérifier leurs assertions métier. Ce résultat ne démontre pas une régression du lecteur.
- **Tenté** : lancement de `wp/tests/a14/run.py --output <répertoire temporaire>/preuves`. Refus d’écriture lors de la création du dossier de preuves, avant tout démarrage Docker. **Les tests PHP et natifs classic/HPOS n’ont donc pas été rejoués par cette relecture.** Aucun contournement du bac à sable effectué.

Le paquet vérifié contient les résultats verts de 8 contrôles PHP, 3 méthodes Python, 55 contrôles de la suite native, 8 gardes du runner, ainsi que PHPCS sans erreur ni avertissement et la matrice Windows UTF-8/cp1252. Les empreintes avant/après des 55 tables sont identiques pour chaque stockage ; les preuves contrôlent aussi les fichiers, les gardes SQL/mail/HTTP/cron et le rejeu. Il s’agit des exécutions livrées, pas de nouvelles exécutions natives indépendantes.

Comparaison complémentaire des 27 dépendances enregistrées : seul `wp/outils/bascule/a12/README.md` diffère ; aucune différence constatée dans les dépendances exécutables enregistrées. La couverture est pertinente, mais ne prouve pas toutes les branches documentées : notamment le domaine technique réservé sans marqueur, `pending-cancel` et plusieurs abonnements sur un même compte.

## 4. Sécurité et données

Aucune donnée réelle ni secret constaté dans les fichiers examinés. Les fixtures sont manifestement fictives. Les sorties sont construites à partir de nombres, motifs fixes et statuts normalisés : aucune adresse ni valeur brute n’est recopiée. Les sorties neuves sont disjointes du site et du dépôt ; le code prévoit les permissions 0700/0600 et refuse l’écrasement.

Le chemin A-11 installe la transaction en lecture seule et les gardes avant le chargement WordPress ; les erreurs de lecture SQL sont remontées. Les requêtes variables utilisent le préfixe du contexte WordPress et une préparation pour l’identifiant utilisateur. Aucun écran web ajouté : nonces et paywall sans objet pour ce lot. Aucun accès à un site, une base ou un compte réel pendant cette relecture.

## 5. Doctrine

La séparation entre rapprochement PHP pur et collecte WordPress est respectée. Les PHP du lot déclarent le typage strict ; les classes métier utilisent l’espace de noms `Imagine`. Le réemploi d’A-11/A-12/A-13 évite un nouveau bootstrap et un nouveau parseur.

**M1 — Mineur — `wp/outils/bascule/a14/command.php:79`.** Le résumé Markdown destiné à l’opérateur affiche directement les clés anglaises (`contacts_with_account`, `accounts_unmatchable`, etc.). Il ne respecte donc pas la règle des textes d’interface en français de la doctrine §5. **Correction proposée :** conserver les clés techniques JSON et utiliser des libellés français dans le Markdown, avec le mécanisme de traduction adapté à cette commande autonome.

**M2 — Mineur — `wp/outils/bascule/a14/Accounts.php:22`.** La collecte reconstruit l’accès aux abonnements actifs par SQL distinct pour classic et HPOS, sans référence documentaire officielle ni justification du choix par rapport aux API natives dans la livraison A-14. L’oracle `wcs_user_has_subscription` valide les cas testés, mais ne remplace pas la justification « standard d’abord » demandée par la doctrine §4. **Correction proposée :** documenter brièvement l’API native examinée et la raison du SQL dans ce contexte de lecture seule, avec les références officielles pertinentes ; ne pas changer la stratégie de collecte sans nécessité démontrée.

## 6. Études (lots sans code)

Sans objet : lot de code. Les références externes n’ont pas été ouvertes, conformément à l’interdiction d’accéder à un site pendant cette relecture. La lacune documentaire précise est portée par M2.

## Verdict

**À corriger.** Aucun défaut fonctionnel bloquant établi par l’examen ; deux écarts mineurs à corriger.

- **Bloquant :** aucun constaté.
- **Important :** aucun constaté.
- **Mineur :** M1 — libellés anglais du résumé opérateur ; M2 — justification documentaire de la collecte SQL manquante.

La vérification du paquet est verte ; le rejeu indépendant complet reste non réalisé en raison des refus d’écriture temporaires décrits ci-dessus. Aucune question ouverte nécessitant un arbitrage de Ced ou d’Imagine. **Ce verdict n’est pas un GO.**
