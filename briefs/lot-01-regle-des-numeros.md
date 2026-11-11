# Lot 01 — Moteur de la règle des numéros

**Nature** : code PHP pur et tests. Aucune dépendance à WordPress ni à WooCommerce.
**Emplacement** : `wp/plugins/imagine-pilotage/src/Numeros/` et `wp/plugins/imagine-pilotage/tests/Numeros/`.
**Livrables** : le code, ses tests, `production/lot-01/notes.md`, puis `production/lot-01/PRET`.

## Pourquoi

Un abonnement papier se compte en numéros, pas en jours (§3.5). La liste d'envoi, les échéances de prélèvement et l'étalement comptable en découlent. C'est la règle la plus spécifique du projet : elle doit exister seule, testée, avant d'être branchée sur WooCommerce.

## Les règles à implémenter (cahier des charges §3.5, §3.4, §3.6)

1. **Calendrier de parution.** Une liste de numéros : identifiant (ex. 171), type (régulier ou hors-série), date de sortie, date de clôture de la liste d'envoi.
2. **Premier numéro papier.** Le prochain numéro régulier dont la liste d'envoi n'est pas clôturée à la date de la commande.
3. **Dernier numéro.** Un abonnement donne droit à quatre numéros réguliers consécutifs.
4. **Hors-série.** Un par année d'abonnement.
5. **Accès numérique.** De date à date, ouvert dès le paiement ou l'acceptation du mandat.
6. **Renouvellement.** L'année suivante commence au numéro qui suit le dernier numéro de l'année précédente.
7. **Paiement en quatre fois.** Une échéance par numéro. Chaque prélèvement est lancé avant la clôture de la liste d'envoi du numéro qu'il paie, avec une marge en jours **paramétrable** (elle sera fixée avec l'administration).
8. **Numéros restant à recevoir**, à une date donnée (affiché dans le compte, §3.7).
9. **Ayants droit d'un numéro** : un abonnement y a-t-il droit ? (base de la liste d'envoi, §3.13).

## Cas du cahier des charges, à reproduire tel quel en test

- Commande le 8 octobre 2026, après la sortie du n° 170 : numéros papier 171, 172, 173 et 174, et le hors-série de l'été 2027.
- Renouvellement en octobre 2027 : numéros 175 à 178 et le hors-série de l'été 2028.

Les dates de sortie et de clôture réelles ne sont pas connues : construire un calendrier fictif plausible (trimestriel, hors-série en été) dans `tests/Numeros/fixtures/`.

## Cas limites à tester

- Commande le jour même de la clôture ; la veille ; le lendemain.
- Commande entre la clôture et la sortie d'un numéro.
- Passage d'année.
- Calendrier qui ne contient pas encore les quatre numéros à venir.
- Abonnement suspendu pour impayé puis réactivé : les numéros déjà clôturés ne sont pas rattrapés.

## Ce que tu ne décides pas

Ces points ne sont pas tranchés par le cahier des charges. Implémente l'interprétation indiquée, isole-la derrière un réglage ou une méthode unique, et liste-la dans `notes.md` sous « À arbitrer par Ced » :

- **Quel hors-série ?** Interprétation : le premier hors-série dont la liste d'envoi n'est pas clôturée à la date de début de l'année d'abonnement.
- **Clôture le jour de la commande.** Interprétation : la liste est considérée comme clôturée à partir de la date de clôture incluse.
- **Calendrier incomplet.** Interprétation : l'abonnement garde un nombre de numéros dus ; le premier et le dernier numéro sont résolus quand le calendrier est complété. Ne jamais inventer un numéro.
- **Fin de l'accès numérique.** Interprétation : un an jour pour jour après son ouverture.

## Exigences

- PHP 8.2, `declare(strict_types=1)`, PSR-12, espace de noms `Imagine\Pilotage\Numeros`.
- Objets immuables, dates en `DateTimeImmutable`, fuseau `Europe/Brussels`. Aucune lecture de l'horloge dans le moteur : la date du jour est toujours passée en argument.
- PHPUnit, lancé par `composer test`. **Tout s'exécute dans Docker**, jamais sur la machine : `docker compose run --rm -w /app/imagine-pilotage php composer install`, puis `docker compose run --rm -w /app/imagine-pilotage php composer test` (voir `docker-compose.yml`).
- `README.md` de l'extension : comment installer les dépendances et lancer les tests (commandes Docker).
- Si Docker n'est pas disponible ou si l'image ne se construit pas : ne rien installer sur la machine, le signaler dans le rapport.
