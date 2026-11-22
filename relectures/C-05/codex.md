# Relecture indépendante Codex — C-05

Date : 22 novembre 2026. Périmètre : brief C-05, production courante du 22/11, code `Echeancier`, dépendance C-01 et banc `echeancier-runner`. Le rapport de l'autre relecteur n'a pas été consulté. Aucune correction de code effectuée.

## 1. Conformité

La référence applicable est le cahier des charges §§3.4–3.5, précisé par `docs/decisions.md` et `docs/arbitrages-2026-11-22.md`. L'Option A remplace expressément le comptage anniversaire du brief : quatre échéances par bloc de quatre numéros ; cinq dates dans une fenêtre anniversaire sont admises. Ce changement est correctement signalé dans la proposition. Les trois réglages suivent également l'arbitrage : marge obligatoire sans défaut, créances maintenues après rejet et tarif figé par défaut.

Les livrables sont présents : moteur PHP pur déléguant les numéros et les dates à C-01, comparaison de deux voies Subscriptions, recommandation motivée, adaptation manuelle et preuves archivées sur deux blocs. La comparaison aborde compte abonné, échec, reconduction, engagement et Odoo. L'absence de raccord automatique de production est explicite et compatible avec la nature de proposition/prototype du lot.

R-02, R-16 et R-17 ne sont pas intégralement validés par ce banc : mandat, emails, opposition à reconduction, passerelle et transmission Odoo ne sont pas exercés. Les preuves concernent la planification et les commandes manuelles locales, conformément au périmètre technique demandé ; elles ne valent pas réception de ces parcours complets.

## 2. Exactitude métier

Déroulés manuels confrontés aux branches du code, sans prétendre à une exécution PHP indépendante :

| Cas | Résultat attendu et obtenu par lecture du code |
|---|---|
| Exemple du §3.5 : commande du 08/10/2026, après la sortie du n°170 ; calendrier fictif C-01, marge 7 jours | C-01 sélectionne 171–174. C-05 donne l'initial au 08/10/2026, puis les 13/03, 13/06 et 13/09/2027. La commune du premier numéro n'est pas ajoutée à l'initial. |
| Reconduction de cet exemple en octobre 2027 | C-01 sélectionne 175–178. C-05 conserve les quatre communes : 13/12/2027, 13/03, 13/06 et 13/09/2028. Aucun nouveau versement initial à l'anniversaire. |
| Fixture C-05 : commande du 09/04/2027 à midi, marge 7 | Avril 2027 à janvier 2028 ; versements les 09/04, 03/07, 03/10 et 03/01. Reconduction dès le 03/04/2028 : cinq dates dans la fenêtre anniversaire, autorisées par l'Option A. |
| Même fixture : commande du 10/04/2027 à minuit ou le 11/04 | La clôture est incluse selon C-01 : premier numéro juillet 2027, puis octobre, janvier et avril. Initial à la commande ; trois communes suivantes. |

Les calendriers incomplets sont refusés ; le 29 février, les fuseaux et le passage d'année sont couverts par les tests fournis. Une anomalie subsiste à la jonction des blocs.

**C05-01 — important — `wp/plugins/imagine-pilotage/src/Echeancier/Planificateur.php:36`.** Le contrôle des dates strictement croissantes repart de `null` à chaque appel, y compris pour une reconduction. Il ne compare donc jamais la première échéance reconduite à la dernière du bloc précédent.

Contre-exemple précis, déduit statiquement : prendre `c05Calendrier()`, conserver les sorties et donner à `REG-2028-04` la même clôture qu'à `REG-2028-01`, soit le 10/01/2028. C-01 accepte ce calendrier : il refuse les clôtures inversées, mais autorise l'égalité. Pour une commande du 20/02/2027 avec marge 7, le quatrième versement initial et le premier versement reconduit tombent tous deux le **03/01/2028 à 00:00 Bruxelles**. Chaque bloc est strictement croissant pris isolément ; les deux appels réussissent. La garantie de refus des dates non croissantes devient ainsi dépendante de la position de l'anomalie dans le bloc, et le raccord reçoit deux positions successives au même instant.

Correction proposée : contrôler aussi la frontière avec le dernier versement du bloc précédent, en utilisant les données de C-01 et le contexte du plan précédent, sans déplacer les communes ni rétablir une borne anniversaire. Ajouter un test de clôtures identiques entre rang 4 et rang 1 reconduit, attendu en refus explicite avant utilisation du plan. Le cas valide du 09/04 doit continuer à passer. Ce contre-exemple n'a pas pu être exécuté dans cette session, pour les raisons ci-dessous.

## 3. Tests

Deux tentatives locales de lancement de la suite autonome ont été faites :

- `php wp/plugins/imagine-pilotage/tests/Echeancier/run.php` : impossible, commande `php` introuvable.
- `wsl.exe -d Ubuntu -- php /mnt/c/Users/Ced/imagine/wp/plugins/imagine-pilotage/tests/Echeancier/run.php` : refus du service WSL, `Wsl/Service/E_ACCESSDENIED`.

**Aucun test PHP ni scénario Subscriptions n'a donc été rejoué avec succès par ce relecteur.** Le banc Docker dépend de WSL. Ses commandes écrivent aussi des reçus dans `production/C-05/preuves/` et son vérificateur réécrit `verification.json` : ils n'ont pas été lancés, afin de respecter l'écriture exclusive du présent rapport. Aucun site ni aucune base n'a été ouvert.

Contrôles locaux en lecture seule effectivement réalisés : comparaison SHA-256 des **16 fichiers** de chacun des manifests `reprise-final-unit.json` et `reprise-final-e2e.json` avec les fichiers actuels, et du lanceur avec son empreinte. **Aucun écart.** Lecture et recomptage des résultats archivés :

- Suite pure : 380 résultats, tous vrais ; 2 289 assertions annoncées, zéro échec.
- Intégration : 350 contrôles vrais par stockage, classique et HPOS ; quatre scénarios et 32 commandes par stockage, soit huit abonnements et 64 commandes au total.
- Versions enregistrées : PHP 8.2.36, WordPress 7.0.9, WooCommerce 11.1.1 et Subscriptions 9.4.1.

Les tests comportent des attentes littérales utiles, notamment les dates et numéros initiaux ; ils ne se limitent pas tous à rappeler le moteur. Le balayage des 365 jours compare cependant largement le résultat à C-01 et conserve un calendrier régulier unique. Son assertion de chronologie entre blocs ne couvre pas le calendrier anormal de C05-01. Le test des clôtures identiques actuel ne place l'égalité qu'à l'intérieur d'un bloc.

Le rejeu démontré par le scénario concerne deux positionnements identiques avant traitement d'une action. Il ne prouve pas l'idempotence d'une confirmation rejouée ou concurrente ; cette limite est correctement déclarée. Les commandes futures sont exécutées en accéléré et leurs validations portent l'heure réelle du banc, distinction également documentée.

## 4. Sécurité et données

Aucun secret ni donnée d'abonné réel repéré dans les surfaces examinées. La fixture utilise des identités fictives et `@example.org`. Le raccord exige cumulativement le marqueur C-05, le renouvellement manuel et une passerelle vide. Il n'enregistre aucun hook au chargement.

L'administration s'appuie sur la Settings API, un nonce standard, la capacité `manage_woocommerce`, l'échappement des sorties et une option non exposée en REST. Les entrées invalides conservent l'option précédente. Le test vérifie notamment le refus du formulaire à un utilisateur anonyme ; il ne teste pas une sauvegarde HTTP, limite annoncée.

Le code du banc et les manifests décrivent un conteneur sans réseau, montage ni port, avec HTTP et emails bloqués. Le nettoyage reste une preuve archivée, non revérifiée via Docker pendant cette relecture. Aucun nouveau chemin de diffusion de contenu réservé identifié ; le paywall n'est pas modifié par ce lot.

## 5. Doctrine

Standard examiné avant le sur-mesure ; API Subscriptions utilisée sans modification d'une extension tierce. Séparation entre PHP pur et adaptation WordPress respectée. Les classes du lot déclarent les types stricts et utilisent l'espace de noms attendu. Préfixes d'options/hooks, traduction des libellés et documentation dédiée sont présents.

Les réglages ouverts sont isolés et testés dans leurs différentes positions. Le maintien de la dette et le tarif figé ne constituent pas des arbitrages inventés : ils viennent du 22/11. Aucun besoin d'une nouvelle décision de Ced identifié pour corriger C05-01. L'absence de branchement partagé, d'encaissement et d'émission Odoo est explicite.

## 6. Études

La proposition comporte huit références officielles, accompagnées d'extraits et de traces de consultation conservés dans le dépôt. Aucune page externe n'a été consultée par ce relecteur, conformément aux restrictions du rôle. Les extraits historiques documentent notamment l'alignement natif, le renouvellement manuel, les actions hors calendrier et les prérequis des reprises automatiques.

**C05-02 — mineur — `production/C-05/proposition.md:47`.** L'affirmation selon laquelle la documentation signale un traitement particulier des renouvellements anticipés sur `woocommerce_subscription_payment_complete` renvoie à [4], mais aucun extrait conservé pour cette source ne porte sur ce hook ou sur cette réserve : l'extrait historique traite du déclenchement hors calendrier et celui du 22/11 de `woocommerce_scheduled_subscription_payment`. **Doute documentaire** sur cette réserve précise, pas constat qu'elle serait fausse.

Correction proposée : rattacher à cette phrase un court extrait officiel pertinent, avec URL et nom du hook, ou la présenter explicitement comme un point à vérifier. Une empreinte de page et un extrait relatif à un autre hook ne permettent pas à eux seuls de contrôler cette affirmation selon la grille.

## Verdict

**À corriger.** Ce verdict n'est pas un GO.

- **Bloquant :** aucun point classé bloquant ; le rejeu indépendant reste indisponible dans cet environnement.
- **Important : C05-01** — contrôler et tester la chronologie à la jonction des blocs.
- **Mineur : C05-02** — compléter la citation concernant les renouvellements anticipés.

Les preuves archivées correspondent au code relu et rapportent des tests au vert. Après correction, un rejeu de la suite pure comprenant le contre-exemple et des scénarios Subscriptions reste nécessaire dans l'environnement de test autorisé.
