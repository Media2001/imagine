# Imagine Connecteur — cœur PHP pur C-04

Bibliothèque PHP **8.2+**, sans chargement de WordPress, WooCommerce, Odoo ou n8n.
Aucun appel réseau, aucun paiement. Données de démonstration entièrement fictives.
Ce n’est pas encore une extension activable ni un connecteur comptable de production.

## Exécuter les tests sans installation hôte

Depuis la racine du dépôt, avec le Python et le Docker de l’outil déjà présents :

```sh
python wp/tests/connecteur-runner/run.py prepare
python wp/tests/connecteur-runner/run.py run --name final
python wp/tests/connecteur-runner/verify.py
python wp/tests/connecteur-runner/run.py close
```

Le lanceur réutilise **sans le modifier** celui de C-01, avec ses propres chemins,
état, étiquette et preuves. Le conteneur jetable n’a ni montage, port, base ni service
WordPress ; seule la préparation Composer a le réseau. `composer test`, `composer lint`,
la syntaxe PHP et `composer validate --strict --no-check-publish` sont réellement lancés.
`verify.py` rejoue C-01 dans le même conteneur isolé, sans changer ses fichiers, et
exécute `examples/export.php` pour produire un vrai CSV fictif et son SHA-256.
Les preuves sont sous `production/C-04/tests/`. Toujours appeler `close`, même en échec.

Dans un autre environnement PHP jetable autorisé : `composer install`, `composer test`,
`composer lint`. Ne rien installer sur Windows. Aucune dépendance d’exécution autre
que PHP ; PHPUnit et PHPCS ne servent qu’au développement. `composer.lock` est fourni.

## API et données

- `Event` et `Entry` immuables ; `EventType` et `State` sont des enums.
- `Event::key()` = SHA-256 du tuple JSON `[type, sourceId]`. Ni contenu, ni heure de
  réception, ni numéro d’essai ne modifient la clé. Le premier dépôt gagne.
- Pour un renouvellement, `sourceId` est **la commande de renouvellement**, non le
  seul abonnement ; pour un remboursement, c’est l’objet remboursement. Fournir
  `subscriptionId` pour tous les événements associés au même abonnement, y compris
  une commande ou un remboursement, sinon cet ordre ne peut pas être assuré.
- `occurredAt` est un `DateTimeImmutable`, normalisé en `Europe/Brussels`.
- Contenu provisoire autorisé : `identity` (`name`, `email` facultatif), `address`
  (`street`, `postal_code`, `city`, `country`), `lines` (liste de `product`, `amount_minor`),
  `total_minor`, `currency`, `payment_method`, `enterprise_number`, `payment_reference`.
  Tout autre champ, y compris imbriqué, est refusé avant dépôt ; pas de persona,
  préférence ni réponse de formulaire. Aucun tableau libre de métadonnées.
- Montants **entiers en unité mineure**, devise à trois lettres majuscules, somme
  exacte des lignes = total, débordement refusé. Aucun calcul de TVA, signe de
  remboursement, tarif ou échéance comptable n’est décidé ici.

`Validator::billing($knownPayments, $enterpriseValidator)` fournit les règles nommées
`identity`, `address`, `amounts`, `payment_method`, `enterprise_number`. Les modes de
paiement viennent explicitement de l’adaptateur, sans liste métier inventée. Le contrôle
C-02 peut être injecté comme callable `string -> bool` ; **en son absence, un numéro
présent est bloqué**, jamais accepté sans contrôle. `Validator::with(Rule)` ajoute une
règle sans modifier le moteur. Les messages des règles doivent être en français et
ne jamais inclure de données personnelles ; aucune fonction de traduction WordPress
n’est appelée dans ce cœur indépendant.

## File et reprise

Les interfaces sont `QueueStorage`, `Destination`, `Clock`, `Alerts` et `Rule`.
`InMemoryQueue`, `FrozenClock`, `InMemoryAlerts`, `FakeDestination` servent au banc.
La destination fictive accepte un script `ok`, `down`, `slow`, `late_ack`, `refuse` ;
`slow` et `late_ack` simulent un dépassement sans attendre réellement.

Construire `Worker(stockage, destination, horloge, alertes, validateur, politique, délai)`.
`run()` tente les entrées éligibles ; `replay(clé)` refuse notamment les déjà envoyées.
`RetryPolicy(maxAttempts, initialSeconds, factor, maximumSeconds)` impose une attente
croissante plafonnée, en secondes écoulées, calculée **après** l’échec. Aucun paramètre
métier n’est fixé implicitement. Une destination doit respecter le délai et lever
`TemporaryFailure` pour une panne/ambiguïté, `PermanentFailure` pour un refus de donnée.
Un autre incident est conservé comme échec temporaire, sans recopier son texte brut.

Un essai est une prise atomique de l’entrée, suivie de son contrôle et éventuel envoi.
Un bail `leaseUntil` permet de récupérer un processus interrompu après son délai,
puis d’attendre le prochain rejeu. Les CAS de stockage empêchent les prises périmées.
À la limite d’essais : alerte unique, entrée conservée en échec temporaire sans boucle
infinie. Un opérateur pourra fournir une politique à limite augmentée pour reprendre ;
pas de suppression automatique ni de remise à zéro du compteur. La quarantaine est
terminale dans ce lot : aucune correction comptable automatique ni nouvel identifiant
fabriqué pour contourner la déduplication. La future reprise administrative devra
être auditée et arbitrée avant branchement.

**Condition non négociable de la destination réelle :** stocker la même clé avec une
contrainte d’unicité atomique et l’effet comptable, puis retourner le même accusé de
réception au rejeu. La file seule ne peut garantir « exactement une fois » après une
réponse perdue ; n8n ne supprime pas cette exigence. Voir `production/C-04/notes.md`.

## Export quotidien

`DailyCsvDestination($privateDirectory, $clock)` implémente `Destination` : `send()`
accuse la prise en charge **durable dans son journal**, pas la création d’une facture.
Le dossier passé doit exister, être privé et sauvegardé. Toutes les écritures, y compris
le verrou et les fichiers temporaires, restent dedans. Aucun répertoire système n’est
utilisé. Liens symboliques et cibles non régulières sont refusés. Répertoire de confiance :
ne pas le partager avec un processus hostile ou un répertoire de médias public.

`exportPreviousDay($now)` publie `AAAA-MM-JJ.csv` pour la veille civile à Bruxelles,
y compris une journée vide, et rattrape les anciens lots du journal non encore publiés.
UTF-8, séparateur virgule, guillemets CSV, LF, en-tête fixe `DailyCsvDestination::COLUMNS`.
Une ligne par clé ; `lines_json` contient la liste ordonnée des produits/montants dans
une colonne stable et `batch_day` explicite le lot technique. Importer les colonnes texte
**comme du texte**, pas comme des formules dans un tableur. Le schéma reste provisoire
à valider par Step ; il ne représente pas les champs définitifs d’Odoo.

Les fichiers publiés sont **scellés** : une relance ne change aucun octet. Un événement
arrivé après publication de sa journée rejoint un prochain lot ouvert (jour de prise
en charge selon l’horloge injectée), sans changer sa véritable date `occurred_at`.
Ce rattrapage technique évite à la fois l’omission, le doublon inter-journées et la
modification d’un fichier déjà remis. Un numéro de lot n’est pas une date comptable.
La journalisation de la clé et du lot, sous verrou, survit au redémarrage ; publication
par fichier temporaire synchronisé et renommage atomique. Journal corrompu ou CSV
scellé divergent : arrêt explicite, pas de fichier incomplet silencieux. Ne supprimer
ni journal ni CSV scellés tant que la déduplication/les relances en dépendent.

Le futur ordonnanceur doit appeler l’export après minuit et signaler ses erreurs ;
aucun cron hôte ou WordPress n’est installé ici. Le passage à l’heure d’été et d’hiver
n’utilise jamais « maintenant moins 86 400 secondes ».
